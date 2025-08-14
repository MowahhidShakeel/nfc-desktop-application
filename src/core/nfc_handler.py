from smartcard.System import readers
from smartcard.pcsc.PCSCExceptions import EstablishContextException
from src.core.logging_config import setup_logger
from src.core.config_handler import ConfigHandler

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

        self.config_handler = ConfigHandler()

    def connect(self):
        """Connect to the ACR1252U reader and load default key."""
        if not self.reader:
            self.logger.error("Cannot connect: No NFC reader detected")
            raise Exception("No NFC reader detected")
        self.connection = self.reader.createConnection()
        self.connection.connect()
        # Load default Key A (0xFF FF FF FF FF FF) into key slot 0
        command = [0xFF, 0x82, 0x00, 0x00, 0x06, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        response, sw1, sw2 = self.connection.transmit(command)
        if sw1 != 0x90 or sw2 != 0x00:
            self.logger.error(f"Failed to load authentication keys: SW1={sw1:02X}, SW2={sw2:02X}")
            raise Exception(f"Failed to load authentication keys: SW1={sw1:02X}, SW2={sw2:02X}")
        self.logger.info("Connected to reader and loaded authentication keys")
        return True

    def authenticate_block(self, block):
        """Authenticate the sector containing the block using Key A."""
        if not self.connection:
            self.logger.error("Cannot authenticate: Not connected to reader")
            raise Exception("Not connected to reader")
        sector = block // 4
        if self.authenticated_sector != sector:
            command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
            response, sw1, sw2 = self.connection.transmit(command)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Authentication failed for sector {sector} (block {block}): SW1={sw1:02X}, SW2={sw2:02X}")
                raise Exception(f"Authentication failed for sector {sector}: SW1={sw1:02X}, SW2={sw2:02X}")
            self.authenticated_sector = sector
            self.logger.info(f"Authenticated sector {sector} for block {block}")

    def write_config(self, data):
        """Write configuration data across multiple blocks (4-6, 8-10, ..., 60-62)."""
        if not self.connection:
            self.logger.error("Cannot write: Not connected to reader")
            raise Exception("Not connected to reader")
        if len(data) > 832:  # 52 blocks * 16 bytes (sectors 1-15)
            self.logger.error(f"Data too large: {len(data)} bytes, max 832")
            raise ValueError("Data exceeds 832 bytes")
        
        # List of usable blocks, excluding sector trailers, starting from sector 1
        usable_blocks = []
        for sector in range(1, 16):  # Sectors 1-15
            for block_offset in range(3):  # Blocks 0, 1, 2 in each sector
                block = sector * 4 + block_offset
                usable_blocks.append(block)
        
        if len(data) > len(usable_blocks) * 16:
            self.logger.error(f"Data too large: {len(data)} bytes, max {len(usable_blocks) * 16}")
            raise ValueError("Data exceeds available block capacity")
        
        for i in range(0, len(data), 16):
            block_index = i // 16
            if block_index >= len(usable_blocks):
                self.logger.error(f"Insufficient blocks for data: {len(data)} bytes")
                raise ValueError("Insufficient blocks for data")
            block = usable_blocks[block_index]
            self.authenticate_block(block)
            block_data = data[i:i+16]
            if len(block_data) < 16:
                block_data += b"\x00" * (16 - len(block_data))
            command = [0xFF, 0xD6, 0x00, block, 0x10] + list(block_data)
            response, sw1, sw2 = self.connection.transmit(command)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Write failed for block {block}: SW1={sw1:02X}, SW2={sw2:02X}")
                raise Exception(f"Write failed for block {block}: SW1={sw1:02X}, SW2={sw2:02X}")
            self.logger.info(f"Wrote to block {block}: {block_data}")
        self.logger.info(f"Configuration written to blocks {usable_blocks[0]}-{usable_blocks[block_index]}")

    def read_config(self):
        """Read configuration data from blocks (4-6, 8-10, ..., 60-62)."""
        if not self.connection:
            self.logger.error("Cannot read: Not connected to reader")
            raise Exception("Not connected to reader")
        data = b""
        for sector in range(1, 16):  # Sectors 1-15
            for block_offset in range(3):  # Blocks 0, 1, 2 in each sector
                block = sector * 4 + block_offset
                self.authenticate_block(block)
                command = [0xFF, 0xB0, 0x00, block, 0x10]
                block_data, sw1, sw2 = self.connection.transmit(command)
                if sw1 != 0x90 or sw2 != 0x00:
                    self.logger.error(f"Read failed for block {block}: SW1={sw1:02X}, SW2={sw2:02X}")
                    raise Exception(f"Read failed for block {block}: SW1={sw1:02X}, SW2={sw2:02X}")
                data += bytes(block_data)
                self.logger.info(f"Read from block {block}: {block_data}")
        return data.rstrip(b"\x00")  # Remove padding

    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
            self.authenticated_sector = None
            self.logger.info("Disconnected from reader")