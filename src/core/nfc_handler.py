from smartcard.System import readers
from smartcard.pcsc.PCSCExceptions import EstablishContextException
from src.core.logging_config import setup_logger

class NFCHandler:
    def __init__(self):
        self.logger = setup_logger()
        try:
            self.reader = readers()[0] if readers() else None
            if self.reader:
                self.logger.info(f"Reader detected: {str(self.reader)}")
            else:
                self.logger.error("No NFC reader detected")
        except EstablishContextException as e:
            self.reader = None
            self.logger.error(f"Failed to establish context: {e}")
        self.connection = None
        self.authenticated_sector = None

    def connect(self):
        """Connect to the ACR1252U reader and load default key."""
        if not self.reader:
            self.logger.error("Cannot connect: No NFC reader detected")
            raise Exception('No NFC reader detected')
        self.connection = self.reader.createConnection()
        self.connection.connect()
        # Load default Key A (0xFF FF FF FF FF FF) into key slot 0
        command = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 != 0x90 or sw2 != 0x00:
            self.logger.error(f"Failed to load authentication keys: SW1={sw1}, SW2={sw2}")
            raise Exception(f'Failed to load authentication keys: SW1={sw1}, SW2={sw2}')
        self.logger.info("Connected to reader and loaded authentication keys")
        return True

    def authenticate_block(self, block):
        """Authenticate the sector containing the block using Key A."""
        if not self.connection:
            self.logger.error("Cannot authenticate: Not connected to reader")
            raise Exception('Not connected to reader')
        sector = block // 4  # MIFARE Classic 1K: 4 blocks per sector
        if self.authenticated_sector != sector:
            # Authenticate sector with Key A (key slot 0)
            command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            response, sw1, sw2 = self.connection.transmit(command)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Authentication failed for sector {sector}: SW1={sw1}, SW2={sw2}")
                raise Exception(f'Authentication failed for sector {sector}: SW1={sw1}, SW2={sw2}')
            self.authenticated_sector = sector
            self.logger.info(f"Authenticated sector {sector} for block {block}")

    def write_block(self, block, data):
        """Write 16 bytes to a MIFARE Classic 1K block (4-63, avoiding sector trailers)."""
        if not self.connection:
            self.logger.error("Cannot write: Not connected to reader")
            raise Exception('Not connected to reader')
        if not 4 <= block <= 63 or (block % 4) == 3:
            self.logger.error(f"Invalid block {block}: Must be 4-63, excluding sector trailers")
            raise ValueError('Block must be between 4 and 63, excluding sector trailers')
        if len(data) != 16:
            self.logger.error(f"Invalid data length: {len(data)} bytes, expected 16")
            raise ValueError('Data must be exactly 16 bytes')
        self.authenticate_block(block)
        command = [0xFF, 0xD6, 0x00, block, 0x10] + list(data)
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            self.logger.info(f"Wrote to block {block}: {data}")
            return True
        self.logger.error(f"Write failed for block {block}: SW1={sw1}, SW2={sw2}")
        raise Exception(f'Write failed: SW1={sw1}, SW2={sw2}')

    def read_block(self, block):
        """Read 16 bytes from a MIFARE Classic 1K block (4-63, avoiding sector trailers)."""
        if not self.connection:
            self.logger.error("Cannot read: Not connected to reader")
            raise Exception('Not connected to reader')
        if not 4 <= block <= 63 or (block % 4) == 3:
            self.logger.error(f"Invalid block {block}: Must be 4-63, excluding sector trailers")
            raise ValueError('Block must be between 4 and 63, excluding sector trailers')
        self.authenticate_block(block)
        command = [0xFF, 0xB0, 0x00, block, 0x10]
        data, sw1, sw2 = self.connection.transmit(command)
        if sw1 == 0x90 and sw2 == 0x00:
            self.logger.info(f"Read from block {block}: {data}")
            return data
        self.logger.error(f"Read failed for block {block}: SW1={sw1}, SW2={sw2}")
        raise Exception(f'Read failed: SW1={sw1}, SW2={sw2}')

    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            self.authenticated_sector = None
            self.logger.info("Disconnected from reader")