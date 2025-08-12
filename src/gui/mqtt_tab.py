from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton
from PyQt6.QtCore import Qt

class MqttTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("MQTT Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Configure your MQTT settings.")
        layout.addWidget(subtitle)

        # Input Fields
        layout.addWidget(QLabel("Host:"))
        self.host = QLineEdit()
        self.host.setMaxLength(64)
        layout.addWidget(self.host)

        layout.addWidget(QLabel("Host Type:"))
        self.host_type = QLineEdit()
        self.host_type.setMaxLength(16)
        layout.addWidget(self.host_type)

        layout.addWidget(QLabel("Port:"))
        self.port = QSpinBox()
        self.port.setRange(0, 65535)
        layout.addWidget(self.port)

        layout.addWidget(QLabel("Username:"))
        self.username = QLineEdit()
        self.username.setMaxLength(32)
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password:"))
        self.password = QLineEdit()
        self.password.setMaxLength(32)
        layout.addWidget(self.password)

        # Previous/Next Buttons
        button_layout = QVBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(1))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(3))
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)