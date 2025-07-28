from smartcard.System import readers
from smartcard.pcsc.PCSCExceptions import EstablishContextException
from smartcard.util import toHexString

class NFCHandler:
    def __init__(self):
        try:
            self.reader = readers()[0] if readers() else None
        except EstablishContextException:
            self.reader = None
        self.connection = None

    def connect(self):
        """Connect to the ACR1252U reader."""
        if not self.reader:
            raise Exception('No NFC reader detected')
        self.connection = self.reader.createConnection()
        self.connection.connect()
        return True

    def write_page(self, page, data):
        """Write 4 bytes to a MIFARE Ultralight page (4-39)."""
        if not self.connection:
            raise Exception('Not connected to reader')
        if not 4 <= page <= 39:
            raise ValueError('Page must be between 4 and 39')
        if len(data) != 4:
            raise ValueError('Data must be exactly 4 bytes')
        command = [0xFF, 0xD6, 0x00, page, 4] + list(data)
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            return True
        raise Exception(f'Write failed: SW1={sw1}, SW2={sw2}')

    def read_page(self, page):
        """Read 4 bytes from a MIFARE Ultralight page (4-39)."""
        if not self.connection:
            raise Exception('Not connected to reader')
        if not 4 <= page <= 39:
            raise ValueError('Page must be between 4 and 39')
        command = [0xFF, 0xB0, 0x00, page, 4]
        data, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            return data
        raise Exception(f'Read failed: SW1={sw1}, SW2={sw2}')

    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None