from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt
import math

class WriteTagsTab(QWidget):
    TAG_CAPACITY = 144  # bytes for MIFARE Ultralight C

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.progress_bars = []

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("Write NFC Tags")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Connect your NFC reader and write the configuration to MIFARE Ultralight tags.")
        layout.addWidget(subtitle)

        # NFC Reader Status Section
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setFrameShadow(QFrame.Shadow.Raised)

        status_label = QLabel("NFC Reader Status")
        status_layout.addWidget(status_label)

        supported = QLabel("Supported readers: ACR122U (USB-A), ACR1252U-M1 (USB-C)")
        status_layout.addWidget(supported)

        self.connection_label = QLabel("Reader Connection: Not Connected")
        self.connection_label.setStyleSheet(
            "background-color: #FF4C4C; border-radius: 4px; padding: 5px; color: white;"
        )
        status_layout.addWidget(self.connection_label)

        note = QLabel("Make sure your NFC reader is properly connected via USB before proceeding.")
        status_layout.addWidget(note)

        layout.addWidget(status_frame)

        # Configuration Data Section
        config_frame = QFrame()
        config_layout = QVBoxLayout(config_frame)
        config_frame.setFrameShape(QFrame.Shape.StyledPanel)
        config_frame.setFrameShadow(QFrame.Shadow.Raised)

        data_label = QLabel("Configuration Data")
        config_layout.addWidget(data_label)

        self.data_size_label = QLabel("Data Size: 0 Bytes")
        self.tags_required_label = QLabel("Tags Required: 0")
        config_layout.addWidget(self.data_size_label)
        config_layout.addWidget(self.tags_required_label)

        self.note2 = QLabel("")
        config_layout.addWidget(self.note2)

        layout.addWidget(config_frame)

        # Progress Bars Section
        self.progress_section = QVBoxLayout()
        layout.addLayout(self.progress_section)

        # Navigation buttons
        back_button = QPushButton("Back to Summary")
        back_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(5))
        layout.addWidget(back_button)

        start_button = QPushButton("Start Writing")
        start_button.clicked.connect(self.parent.write_nfc_config)
        layout.addWidget(start_button)

        self.setLayout(layout)

        # Try auto-connect reader
        self.auto_connect_reader()

    def auto_connect_reader(self):
        """Automatically try to connect to NFC reader."""
        try:
            if self.parent.nfc.connect():
                self.connection_label.setText("Reader Connection: Connected")
                self.connection_label.setStyleSheet(
                    "background-color: #4CAF50; border-radius: 4px; padding: 5px; color: white;"
                )
                self.parent.is_connected = True
            else:
                self.connection_label.setText("Reader Connection: Not Connected")
        except Exception as e:
            self.connection_label.setText(f"Reader Connection: Failed ({e})")

    def update_config_data(self, data_size):
        """Update UI with calculated tags and progress bars."""
        self.data_size_label.setText(f"Data Size: {data_size} Bytes")

        tags_required = math.ceil(data_size / self.TAG_CAPACITY)
        self.tags_required_label.setText(f"Tags Required: {tags_required} Tag(s)")
        self.note2.setText(
            f"Your configuration requires {tags_required} NFC tag(s). "
            "Data will be split across multiple tags using continuation flags."
        )

        # Clear old progress bars
        for bar in self.progress_bars:
            self.progress_section.removeWidget(bar)
            bar.deleteLater()
        self.progress_bars.clear()

        # Add progress bars
        for tag_index in range(tags_required):
            bar = QProgressBar()
            if tag_index < tags_required - 1:
                bar.setValue(100)
                bar.setFormat(f"Tag {tag_index+1} Memory Usage: {self.TAG_CAPACITY} / {self.TAG_CAPACITY} Bytes")
            else:
                last_tag_bytes = data_size % self.TAG_CAPACITY or self.TAG_CAPACITY
                percent_fill = int((last_tag_bytes / self.TAG_CAPACITY) * 100)
                bar.setValue(percent_fill)
                bar.setFormat(f"Tag {tag_index+1} Memory Usage: {last_tag_bytes} / {self.TAG_CAPACITY} Bytes")
            self.progress_section.addWidget(bar)
            self.progress_bars.append(bar)
