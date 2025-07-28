from smartcard.System import readers
from smartcard.util import toHexString

PAGE_BYTES = 4
USER_PAGE_START = 4
USER_PAGE_END = 39

class NFCHandler:
    def __init__(self):
        self.reader = readers()[0] if readers() else None
        self.connection = None

    def connect(self):
        """Connect to the ACR1252U reader."""
        if not self.reader:
            raise Exception('No NFC reader detected')
        self.connection = self.reader.createConnection()
        self.connection.connect()
        return True

    def write_page(self, page, data):
        """Write 4 bytes to a MIFARE Ultralight page (4-39 for user data)."""
        if not USER_PAGE_START <= page <= USER_PAGE_END:
            raise ValueError('Page must be between ', USER_PAGE_START, ' and ', USER_PAGE_END)
        if len(data) != PAGE_BYTES:
            raise ValueError('Data must be exactly ' + PAGE_BYTES)
        command = [0xFF, 0xD6, 0x00, page, 4] + list(data) # MIFARE Ultralight APDU command to write
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            return True
        raise Exception(f'Write failed: SW1={sw1}, SW2={sw2}')

    def read_page(self, page):
        """Read 4 bytes from a MIFARE Ultralight page (4-39 for user data)."""
        if not USER_PAGE_START <= page <= USER_PAGE_END:
            raise ValueError("Page must be between ", USER_PAGE_START, " and ", USER_PAGE_END)
        command = [0xFF, 0xB0, 0x00, page, 4] # MIFARE Ultralight APDU command to read
        data, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00: # Success codes
            return data
        raise Exception(f'Read failed: SW1={sw1}, SW2={sw2}')

    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None