from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class ReadTagsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("Read Tags")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Read the configuration from an NFC tag.")
        layout.addWidget(subtitle)

        # Buttons
        self.read_button = QPushButton("Read Config from NFC")
        self.read_button.clicked.connect(self.parent.read_nfc_config)
        layout.addWidget(self.read_button)

        # Previous Button
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(6))
        layout.addWidget(prev_button)

        self.setLayout(layout)