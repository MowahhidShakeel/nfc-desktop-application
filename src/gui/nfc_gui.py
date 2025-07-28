from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel
from src.core.nfc_handler import NFCHandler
import sys

class NFCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC Desktop Application")
        self.setGeometry(100, 100, 400, 300)

        # Initialize NFC handler
        self.nfc = NFCHandler()
        self.is_connected = False

        # Create layout and widgets
        layout = QVBoxLayout()
        self.status_label = QLabel("No reader detected")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.connect_button = QPushButton("Connect to Reader")
        self.write_button = QPushButton("Write to Page 4")
        self.read_button = QPushButton("Read from Page 4")
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
        self.write_button.clicked.connect(self.write_page)
        self.read_button.clicked.connect(self.read_page)

        # Initial check for reader
        if self.nfc.reader is None:
            self.log("No NFC reader detected or Smart Card service not running")

    def log(self, message):
        """Append message to the log area."""
        self.log_area.append(message)

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
            self.log(f"Error: {e}")

    def write_page(self):
        """Write test data to page 4."""
        try:
            test_data = [0x01, 0x02, 0x03, 0x04]
            self.nfc.write_page(4, test_data)
            self.log(f"Wrote to page 4: {test_data}")
        except Exception as e:
            self.log(f"Write error: {e}")

    def read_page(self):
        """Read data from page 4."""
        try:
            data = self.nfc.read_page(4)
            self.log(f"Read from page 4: {data}")
        except Exception as e:
            self.log(f"Read error: {e}")

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