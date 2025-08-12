from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton
from PyQt6.QtCore import Qt

class WifiTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("WiFi Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Configure your WiFi settings.")
        layout.addWidget(subtitle)

        # Input Fields
        layout.addWidget(QLabel("SSID:"))
        self.ssid = QLineEdit()
        self.ssid.setMaxLength(32)
        layout.addWidget(self.ssid)

        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setMaxLength(64)
        layout.addWidget(self.password)

        layout.addWidget(QLabel("Enterprise Mode:"))
        self.enterprise_mode = QSpinBox()
        self.enterprise_mode.setRange(0, 255)
        layout.addWidget(self.enterprise_mode)

        layout.addWidget(QLabel("Enterprise Identity:"))
        self.enterprise_identity = QLineEdit()
        self.enterprise_identity.setMaxLength(64)
        layout.addWidget(self.enterprise_identity)

        layout.addWidget(QLabel("Enterprise Username:"))
        self.enterprise_username = QLineEdit()
        self.enterprise_username.setMaxLength(64)
        layout.addWidget(self.enterprise_username)

        # Previous/Next Buttons
        button_layout = QVBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(0))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(2))
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)