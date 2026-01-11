import sys
from smartcard.System import readers
from smartcard.util import toHexString


class NFCHandler:
    def __init__(self):
        self.connection = None
        self.reader = None
        self.reader_type = None  # "ACR122" or "ACR1252U"

    def connect(self, reader_index: int = 0):
        r = readers()
        if not r:
            raise RuntimeError("No PC/SC readers found")
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()

        # Detect type by name
        name = self.reader.name.lower()
        if "acr122" in name:
            self.reader_type = "ACR122"
        elif "acr125" in name:
            self.reader_type = "ACR1252U"
        else:
            raise RuntimeError(f"Unsupported reader: {self.reader.name}")

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    # ------------------------------------------------------------------
    # Low-level helpers for ACR122 (PN532 passthrough)
    # ------------------------------------------------------------------
    def _pn532_transmit(self, payload_bytes):
        apdu = [0xFF, 0x00, 0x00, 0x00, len(payload_bytes)] + payload_bytes
        data, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Reader error SW={sw1:02X}{sw2:02X}")
        if len(data) < 3 or data[:3] != [0xD5, 0x41, 0x00]:
            raise RuntimeError(f"PN532 error: {toHexString(data)}")
        return data[3:]


    def _acr122_read_page(self, page):
        resp = self._pn532_transmit([0xD4, 0x40, 0x01, 0x30, page & 0xFF])
        if len(resp) < 4:
            raise RuntimeError(f"Failed to read page {page}")
        return bytes(resp[:4])

    def _acr122_write_page(self, page, data4):
        if len(data4) != 4:
            raise ValueError("Data must be exactly 4 bytes")
        self._pn532_transmit([0xD4, 0x40, 0x01, 0xA2, page & 0xFF] + list(data4))

    # ------------------------------------------------------------------
    # Low-level helpers for ACR1252U (PC/SC APDUs)
    # ------------------------------------------------------------------
    def _acr1252_read_page(self, page):
        apdu = [0xFF, 0xB0, 0x00, page, 0x04]  # Read 4 bytes from page
        data, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Read failed SW={sw1:02X}{sw2:02X}")
        #print(data)
        hex_list = [hex(x) for x in data]
        print(hex_list) 
        return bytes(data)

    def _acr1252_write_page(self, page, data4):
        if len(data4) != 4:
            raise ValueError("Data must be exactly 4 bytes")
        apdu = [0xFF, 0xD6, 0x00, page, 0x04] + list(data4)
        _, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Write failed SW={sw1:02X}{sw2:02X}")

    # ------------------------------------------------------------------
    # Unified API
    # ------------------------------------------------------------------
    def ulc_read_pages(self, start_page, end_page):
        if not (0 <= start_page <= end_page <= 47):
            raise ValueError("Pages must be between 0 and 47, with start_page <= end_page")
        result = b""
        for page in range(start_page, end_page + 1):
            if self.reader_type == "ACR122":
                result += self._acr122_read_page(page)
            else:
                result += self._acr1252_read_page(page)
        return result

    def ulc_write_page(self, page, data4):
        if self.reader_type == "ACR122":
            self._acr122_write_page(page, data4)
        else:
            self._acr1252_write_page(page, data4)

    def read_write_nfc(self, action: str, start_page: int, end_page: int = None,
                       data: bytes = None, key16: bytes = None):
        try:
            self.connect()
            action = action.lower()
            if action not in ['read', 'write']:
                raise ValueError("Action must be 'read' or 'write'")

            if action == 'read':
                if end_page is None:
                    end_page = start_page
                return self.ulc_read_pages(start_page, end_page)

            else:  # write
                if end_page is not None:
                    raise ValueError("end_page not required for write")
                if not 0 <= start_page <= 47:
                    raise ValueError("Page must be between 0 and 47")
                if data is None or len(data) != 4:
                    raise ValueError("Data must be exactly 4 bytes")
                self.ulc_write_page(start_page, data)
                return None

        except Exception as e:
            raise RuntimeError(f"Operation failed: {e}")
        finally:
            if self.connection:
                self.disconnect()

    def get_uid(self):
        # Same for both readers
        data, sw1, sw2 = self.connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError("Failed to get UID")
        return bytes(data)
