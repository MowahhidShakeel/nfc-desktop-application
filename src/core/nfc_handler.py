import sys
from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES3
import ipaddress

class NFCHandler:
    def __init__(self):
        self.connection = None
        self.reader = None

    def connect(self, reader_index: int = 0):
        r = readers()
        if not r:
            raise RuntimeError("No PC/SC readers found")
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()
    
    def disconnect(self):
        self.connection.disconnect()
        return

    def tx_direct_transmit(self, payload_bytes):
        apdu = [0xFF, 0x00, 0x00, 0x00, len(payload_bytes)] + payload_bytes
        data, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Reader error SW={sw1:02X}{sw2:02X}")
        if len(data) < 3 or data[0:3] != [0xD5, 0x41, 0x00]:
            raise RuntimeError(f"PN532 error: {toHexString(data)}")
        return data[3:]

    def pn532_exchange(self, native_cmd):
        return self.tx_direct_transmit([0xD4, 0x40, 0x01] + native_cmd)

    def ulc_read_pages(self, start_page, end_page):
        if not (0 <= start_page <= end_page <= 47):
            raise ValueError("Pages must be between 0 and 47, with start_page <= end_page")
        result = b""
        for page in range(start_page, end_page + 1):
            resp = self.pn532_exchange([0x30, page & 0xFF])
            if len(resp) < 4:
                raise RuntimeError(f"Failed to read page {page}")
            result += bytes(resp[:4])
        return result

    def ulc_write_page(self, page, four_bytes):
        if len(four_bytes) != 4:
            raise ValueError("Data must be exactly 4 bytes")
        self.pn532_exchange([0xA2, page & 0xFF] + list(four_bytes))

    def ulc_authenticate_3des(self, key16):
        part1 = self.pn532_exchange([0x1A, 0x00])
        if len(part1) < 9 or part1[0] != 0xAF:
            raise RuntimeError(f"Auth part1 unexpected: {toHexString(list(part1))}")
        return True

    def read_write_nfc(self, action: str, start_page: int, end_page: int = None, data: bytes = None, key16: bytes = None):
        try:
            self.connect()
            action = action.lower()
            if action not in ['read', 'write']:
                raise ValueError("Action must be 'read' or 'write'")

            if action == 'read':
                if end_page is None:
                    end_page = start_page
                data = self.ulc_read_pages(start_page, end_page)
                return data
            else:
                if end_page is not None:
                    raise ValueError("end_page not required for write")
                if not 0 <= start_page <= 47:
                    raise ValueError("Page must be between 0 and 47")
                if data is None or len(data) != 4:
                    raise ValueError("Data must be exactly 4 bytes")
                if key16:
                    self.ulc_authenticate_3des(key16)
                self.ulc_write_page(start_page, data)
                return None

        except Exception as e:
            raise RuntimeError(f"Operation failed: {e}")
        finally:
            if self.connection:
                self.connection.disconnect()

    def get_uid(self):
        data, sw1, sw2 = self.connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError("Failed to get UID")
        return data
