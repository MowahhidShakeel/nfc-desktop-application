# pip install pyscard pycryptodome
from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes


class NFCHandler:
    def __init__(self):
        self.connection = None
        self.reader = None

    # -------------------- Setup --------------------
    def connect(self, reader_index: int = 0):
        r = readers()
        if not r:
            raise RuntimeError("No PC/SC readers found")
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()
        print(f"Connected to reader: {self.reader}")

    # -------------------- PC/SC + ACR122U helpers --------------------
    def tx_direct_transmit(self, payload_bytes):
        apdu = [0xFF, 0x00, 0x00, 0x00, len(payload_bytes)] + payload_bytes
        data, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(
                f"Reader error SW={sw1:02X}{sw2:02X}; APDU was {toHexString(apdu)}"
            )
        if len(data) < 3 or data[0:3] != [0xD5, 0x41, 0x00]:
            raise RuntimeError(f"PN532 error/NAK: {toHexString(data)}")
        return data[3:]

    def pn532_exchange(self, native_cmd):
        return self.tx_direct_transmit([0xD4, 0x40, 0x01] + native_cmd)

    def get_uid(self):
        data, sw1, sw2 = self.connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError("Failed to get UID")
        return bytes(data)

    # -------------------- Ultralight C native ops --------------------
    def ulc_read_16bytes(self, start_page):
        resp = self.pn532_exchange([0x30, start_page & 0xFF])
        return bytes(resp[:16])

    def ulc_write_page(self, page, four_bytes):
        assert len(four_bytes) == 4, "Page write requires exactly 4 bytes"
        self.pn532_exchange([0xA2, page & 0xFF] + list(four_bytes))

    # -------------------- 3DES Authentication (Ultralight C) --------------------
    @staticmethod
    def _des3_ecb_encrypt(key16, block8):
        k = DES3.adjust_key_parity(key16 + key16[:8])  # expand to 24 bytes
        cipher = DES3.new(k, DES3.MODE_ECB)
        return cipher.encrypt(block8)

    @staticmethod
    def _des3_ecb_decrypt(key16, block8):
        k = DES3.adjust_key_parity(key16 + key16[:8])
        cipher = DES3.new(k, DES3.MODE_ECB)
        return cipher.decrypt(block8)

    @staticmethod
    def _rotate_left8(b8):
        return b8[1:] + b8[:1]

    def ulc_authenticate_3des(self, key16):
        # STEP 1
        part1 = self.pn532_exchange([0x1A, 0x00])
        if len(part1) < 9 or part1[0] != 0xAF:
            raise RuntimeError(f"Auth part1 unexpected: {toHexString(list(part1))}")
        ek_rndB = bytes(part1[1:9])
        rndB = self._des3_ecb_decrypt(key16, ek_rndB)

        # STEP 2
        rndA = get_random_bytes(8)
        payload = rndA + self._rotate_left8(rndB)
        ek_payload = b''.join(
            self._des3_ecb_encrypt(key16, payload[i:i+8]) for i in range(0, 16, 8)
        )
        part2 = self.pn532_exchange([0xAF] + list(ek_payload))

        # STEP 3
        if len(part2) < 9 or part2[0] != 0x00:
            raise RuntimeError(f"Auth part2 failed: {toHexString(list(part2))}")
        ek_rndA_prim = bytes(part2[1:9])
        rndA_prim = self._des3_ecb_decrypt(key16, ek_rndA_prim)
        if rndA_prim != self._rotate_left8(rndA):
            raise RuntimeError("Auth verify failed (RndA' mismatch)")
        return True


# -------------------- Demo flow --------------------
if __name__ == "__main__":
    handler = NFCHandler()
    handler.connect()

    print("UID:", handler.get_uid().hex())

    # Example: read pages 4..7 (16 bytes)
    print("P4..7:", handler.ulc_read_16bytes(0x04).hex())

    # Write test
    handler.ulc_write_page(0x04, b"TEST")
    print("Wrote page 0x04")

    # Authenticate (if needed)
    # key16 = bytes.fromhex("49454D4B41455242214E4143554F5946")
    # handler.ulc_authenticate_3des(key16)
    # handler.ulc_write_page(0x10, b"\x01\x02\x03\x04")
