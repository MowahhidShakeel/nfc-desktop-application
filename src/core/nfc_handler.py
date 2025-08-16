# pip install pyscard pycryptodome
from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes

# -------------------- PC/SC + ACR122U helpers --------------------
def tx_direct_transmit(conn, payload_bytes):
    # ACS Direct Transmit: FF 00 00 00 Lc | <PN532 payload>
    apdu = [0xFF, 0x00, 0x00, 0x00, len(payload_bytes)] + payload_bytes
    data, sw1, sw2 = conn.transmit(apdu)
    if (sw1, sw2) != (0x90, 0x00):
        raise RuntimeError(f"Reader error SW={sw1:02X}{sw2:02X}; APDU was {toHexString(apdu)}")
    # Expect PN532 response: D5 41 00 ... (InDataExchange OK)
    if len(data) < 3 or data[0:3] != [0xD5, 0x41, 0x00]:
        raise RuntimeError(f"PN532 error/NAK: {toHexString(data)}")
    return data[3:]  # strip D5 41 00

def pn532_exchange(conn, native_cmd):
    # Wrap native Ultralight command with PN532 InDataExchange (D4 40 01)
    return tx_direct_transmit(conn, [0xD4, 0x40, 0x01] + native_cmd)

def get_uid(conn):
    # ACR122U GET DATA (UID)
    data, sw1, sw2 = conn.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
    if (sw1, sw2) != (0x90, 0x00):
        raise RuntimeError("Failed to get UID")
    return bytes(data)

# -------------------- Ultralight C native ops --------------------
def ulc_read_16bytes(conn, start_page):
    # READ (0x30) returns 4 pages (16 bytes) starting at start_page
    resp = pn532_exchange(conn, [0x30, start_page & 0xFF])
    return bytes(resp[:16])

def ulc_write_page(conn, page, four_bytes):
    assert len(four_bytes) == 4
    # WRITE (0xA2) writes one page (4 bytes)
    pn532_exchange(conn, [0xA2, page & 0xFF] + list(four_bytes))

# -------------------- 3DES Authentication (Ultralight C) --------------------
def _des3_ecb_encrypt(key16, block8):
    # MF0ICU2 uses 16-byte (2-key) 3DES; Double-length key K1||K2, EDE
    k = DES3.adjust_key_parity(key16 + key16[:8])  # 16->24 for PyCryptodome (K1,K2,K1)
    cipher = DES3.new(k, DES3.MODE_ECB)
    return cipher.encrypt(block8)

def _des3_ecb_decrypt(key16, block8):
    k = DES3.adjust_key_parity(key16 + key16[:8])
    cipher = DES3.new(k, DES3.MODE_ECB)
    return cipher.decrypt(block8)

def rotate_left8(b8):
    return b8[1:] + b8[:1]

def ulc_authenticate_3des(conn, key16):
    # STEP 1: PCD -> PICC : 1A 00
    part1 = pn532_exchange(conn, [0x1A, 0x00])
    if len(part1) < 9 or part1[0] != 0xAF:
        raise RuntimeError(f"Auth part1 unexpected: {toHexString(list(part1))}")
    ek_rndB = bytes(part1[1:9])
    rndB = _des3_ecb_decrypt(key16, ek_rndB)

    # STEP 2: build RndA, RndB' and send AF + ENC(RndA||RndB')
    rndA = get_random_bytes(8)
    payload = rndA + rotate_left8(rndB)
    ek_payload = b''.join(_des3_ecb_encrypt(key16, payload[i:i+8]) for i in range(0, 16, 8))
    part2 = pn532_exchange(conn, [0xAF] + list(ek_payload))

    # STEP 3: expect 00 + ek(RndA')
    if len(part2) < 9 or part2[0] != 0x00:
        raise RuntimeError(f"Auth part2 failed: {toHexString(list(part2))}")
    ek_rndA_prim = bytes(part2[1:9])
    rndA_prim = _des3_ecb_decrypt(key16, ek_rndA_prim)
    if rndA_prim != rotate_left8(rndA):
        raise RuntimeError("Auth verify failed (RndA' mismatch)")
    return True  # authenticated

# -------------------- Demo flow --------------------
def main():
    r = readers()
    if not r:
        raise RuntimeError("No PC/SC readers found")
    conn = r[0].createConnection()
    conn.connect()  # tap the card now

    print("Reader:", r[0])
    print("UID:", get_uid(conn).hex())

    # Example: read pages 4..7 (16 bytes)
    print("P4..7:", ulc_read_16bytes(conn, 0x04).hex())

    # If tag is in delivery state (AUTH0=0x30), you can write without auth:
    ulc_write_page(conn, 0x04, b"TEST")  # writes bytes 'T','E','S','T' to page 4
    print("Wrote page 0x04")

    # If you've configured auth, do this first with your 16-byte key:
    # key16 = bytes.fromhex("49454D4B41455242214E4143554F5946")  # Example from NXP datasheet
    # ulc_authenticate_3des(conn, key16)
    # ulc_write_page(conn, 0x10, b"\x01\x02\x03\x04")

if __name__ == "__main__":
    main()
