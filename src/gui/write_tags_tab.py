from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class WriteTagsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("Write Tags")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Write the configuration to an NFC tag.")
        layout.addWidget(subtitle)

        # Buttons
        self.connect_button = QPushButton("Connect to Reader")
        self.connect_button.clicked.connect(self.parent.connect_reader)
        layout.addWidget(self.connect_button)

        self.write_button = QPushButton("Write Config to NFC")
        self.write_button.clicked.connect(self.parent.write_nfc_config)
        layout.addWidget(self.write_button)

        # Previous Button
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(5))
        layout.addWidget(prev_button)

        self.setLayout(layout)