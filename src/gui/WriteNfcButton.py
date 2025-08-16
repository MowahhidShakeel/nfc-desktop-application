from PyQt6.QtWidgets import QPushButton, QMessageBox
from smartcard.Exceptions import NoCardException
from src.core.nfc_handler import NFCHandler


class WriteNfcButton(QPushButton):
    def __init__(self, parent, nfc_handler: NFCHandler, config_provider):
        super().__init__("Write Config to NFC", parent)
        self.nfc = nfc_handler
        self.config_provider = config_provider
        self.clicked.connect(self.write_cards)

    def encode_config(self, config: dict) -> bytes:
        data = bytearray()

        # Example: WiFi SSID
        ssid = config["wifi"]["ssid"].encode("utf-8") + b"\x00"
        data.append(0x02)  # WiFi SSID key
        data.extend(ssid)

        # WiFi password
        pwd = config["wifi"]["password"].encode("utf-8") + b"\x00"
        data.append(0x05)
        data.extend(pwd)

        # End of record list
        data.append(0x00)
        return bytes(data)

    def split_across_cards(self, data: bytes) -> list[bytes]:
        chunks = []
        max_size = 144

        for i in range(0, len(data), max_size):
            chunk = bytearray()
            if i == 0:
                chunk += b"\x81\x01"  # first card
            elif i + max_size >= len(data):
                chunk += b"\x82\x01"  # last card
            else:
                chunk += b"\x83\x01"  # middle card

            chunk.extend(data[i:i + max_size - 2])
            chunk.append(0x00)
            chunks.append(bytes(chunk))
        return chunks

    def write_to_card(self, chunk: bytes):
        # Attempt to connect until card is present
        while True:
            try:
                self.nfc.connect()
                break
            except NoCardException:
                QMessageBox.information(self, "Insert Card", "Please insert the next NFC card...")

        # Write user data pages (4–39)
        for page in range(4, 4 + (len(chunk) + 3) // 4):
            slice4 = chunk[(page - 4) * 4:(page - 3) * 4]
            if len(slice4) < 4:
                slice4 = slice4.ljust(4, b"\x00")
            self.nfc.ulc_write_page(page, slice4)

    def write_cards(self):
        try:
            config = self.config_provider()
            raw = self.encode_config(config)
            chunks = self.split_across_cards(raw)

            for i, chunk in enumerate(chunks):
                QMessageBox.information(
                    self, "Write NFC", f"Ready to write card {i+1}/{len(chunks)}.\nInsert card."
                )
                self.write_to_card(chunk)

            QMessageBox.information(self, "Done", "All cards written successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
