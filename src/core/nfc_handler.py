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
        self.authenticated_sector = None

    def connect(self):
        """Connect to the ACR1252U reader and load default key."""
        if not self.reader:
            raise Exception('No NFC reader detected')
        self.connection = self.reader.createConnection()
        self.connection.connect()
        # Load default Key A (0xFF FF FF FF FF FF) into key slot 0
        command = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 != 0x90 or sw2 != 0x00:
            raise Exception(f'Failed to load authentication keys: SW1={sw1}, SW2={sw2}')
        return True

    def authenticate_block(self, block):
        """Authenticate the sector containing the block using Key A."""
        if not self.connection:
            raise Exception('Not connected to reader')
        sector = block // 4  # MIFARE Classic 1K: 4 blocks per sector
        if self.authenticated_sector != sector:
            # Authenticate sector with Key A (key slot 0)
            command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            response, sw1, sw2 = self.connection.transmit(command)
            if sw1 != 0x90 or sw2 != 0x00:
                raise Exception(f'Authentication failed for sector {sector}: SW1={sw1}, SW2={sw2}')
            self.authenticated_sector = sector

    def write_block(self, block, data):
        """Write 16 bytes to a MIFARE Classic 1K block (4-63, avoiding sector trailers)."""
        if not self.connection:
            raise Exception('Not connected to reader')
        if not 4 <= block <= 63 or (block % 4) == 3:
            raise ValueError('Block must be between 4 and 63, excluding sector trailers')
        if len(data) != 16:
            raise ValueError('Data must be exactly 16 bytes')
        self.authenticate_block(block)
        command = [0xFF, 0xD6, 0x00, block, 0x10] + list(data)
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            return True
        raise Exception(f'Write failed: SW1={sw1}, SW2={sw2}')

    def read_block(self, block):
        """Read 16 bytes from a MIFARE Classic 1K block (4-63, avoiding sector trailers)."""
        if not self.connection:
            raise Exception('Not connected to reader')
        if not 4 <= block <= 63 or (block % 4) == 3:
            raise ValueError('Block must be between 4 and 63, excluding sector trailers')
        self.authenticate_block(block)
        command = [0xFF, 0xB0, 0x00, block, 0x10]
        data, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            return data
        raise Exception(f'Read failed: SW1={sw1}, SW2={sw2}')

    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            self.authenticated_sector = None