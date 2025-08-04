from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from src.core.nfc_handler import NFCHandler
from src.core.logging_config import setup_logger
import sys

class NFCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC Desktop Application")
        self.setGeometry(100, 100, 400, 300)

        # Initialize logger and NFC handler
        self.logger = setup_logger()
        self.nfc = NFCHandler()
        self.is_connected = False

        # Create layout and widgets
        layout = QVBoxLayout()
        self.status_label = QLabel("No reader detected")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.connect_button = QPushButton("Connect to Reader")
        self.write_button = QPushButton("Write to NFC Card")
        self.read_button = QPushButton("Read from NFC Card")
        self.write_button.setEnabled(False)
        self.read_button.setEnabled(False)

        # Add widgets to layout
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_area)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.write_button)
        layout.addWidget(self.read_button)

        # Set up the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect button signals
        self.connect_button.clicked.connect(self.connect_reader)
        self.write_button.clicked.connect(self.write_block)
        self.read_button.clicked.connect(self.read_block)

        # Initial check for reader
        if self.nfc.reader is None:
            self.log("No NFC reader detected or Smart Card service not running")

    def log(self, message, level='INFO'):
        """Append message to the log area and file."""
        self.log_area.append(message)
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'ERROR':
            self.logger.error(message)

    def connect_reader(self):
        """Connect to the NFC reader."""
        try:
            if self.nfc.connect():
                self.is_connected = True
                self.status_label.setText("Connected to reader")
                self.log("Connected to reader")
                self.connect_button.setEnabled(False)
                self.write_button.setEnabled(True)
                self.read_button.setEnabled(True)
        except Exception as e:
            self.status_label.setText("Connection failed")
            self.log(f"Error: {e}", level='ERROR')

    def write_block(self):
        """Write test data to block 4."""
        try:
            test_data = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                         0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10]
            self.nfc.write_block(4, test_data)
            self.log(f"Wrote to block 4: {test_data}")
        except Exception as e:
            self.log(f"Write error: {e}", level='ERROR')

    def read_block(self):
        """Read data from block 4."""
        try:
            data = self.nfc.read_block(4)
            self.log(f"Read from block 4: {data}")
        except Exception as e:
            self.log(f"Read error: {e}", level='ERROR')

    def closeEvent(self, event):
        """Handle window close event to disconnect reader."""
        if self.is_connected:
            self.nfc.disconnect()
            self.log("Disconnected from reader")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFCWindow()
    window.show()
    sys.exit(app.exec())