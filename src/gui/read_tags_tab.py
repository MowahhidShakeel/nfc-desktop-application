from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtCore import Qt

class ReadTagsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("Read NFC Tags")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Connect your NFC reader and read the configuration from MIFARE Ultralight tags.")
        layout.addWidget(subtitle)

        # NFC Reader Status
        status_label = QLabel("NFC Reader Status")
        layout.addWidget(status_label)

        # Supported readers
        supported = QLabel("Supported readers: ACR122U (USB-A), ACR1252U-M1 (USB-C)")
        layout.addWidget(supported)

        # Reader Connection
        self.connection_label = QLabel("Reader Connection")
        self.connection_label.setStyleSheet("background-color: #00FF00; border-radius: 4px; padding: 5px; color: #333333;")
        self.connection_label.setText("Connected")
        layout.addWidget(self.connection_label)

        # Note
        note = QLabel("Make sure your NFC reader is properly connected via USB before proceeding.")
        layout.addWidget(note)

        # Configuration Data (placeholder for read, can be similar to write)
        data_label = QLabel("Configuration Data")
        layout.addWidget(data_label)

        # Data Size and Tags Required
        data_size = QLabel("Data Size: 420 Bytes")
        tags_required = QLabel("Tags Required: 3 Tags")
        layout.addWidget(data_size)
        layout.addWidget(tags_required)

        # Note
        note2 = QLabel("The configuration is stored across 3 NFC tags with continuation flags.")
        layout.addWidget(note2)

        # Memory Usage Bars (placeholder, update with read data)
        tag1_bar = QProgressBar()
        tag1_bar.setValue(100)
        tag1_bar.setFormat("Tag 1 Memory Usage: 144 / 144 Bytes")
        layout.addWidget(tag1_bar)

        tag2_bar = QProgressBar()
        tag2_bar.setValue(100)
        tag2_bar.setFormat("Tag 2 Memory Usage: 144 / 144 Bytes")
        layout.addWidget(tag2_bar)

        tag3_bar = QProgressBar()
        tag3_bar.setValue(90)
        tag3_bar.setFormat("Tag 3 Memory Usage: 132 / 144 Bytes")
        layout.addWidget(tag3_bar)

        # Note
        note3 = QLabel("Data is distributed across 3 tags. Tag 1 and 2 are filled completely. Tag 3 contains the remaining 132 bytes.")
        layout.addWidget(note3)

        # Back and Start Reading buttons
        button_layout = QVBoxLayout()
        back_button = QPushButton("Back to Summary")
        back_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(5))
        button_layout.addWidget(back_button)

        start_button = QPushButton("Start Reading")
        start_button.clicked.connect(self.parent.read_nfc_config)
        button_layout.addWidget(start_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)