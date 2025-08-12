from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QCheckBox, QPushButton
from PyQt6.QtCore import Qt

class IpTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("IP Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Configure your IP settings.")
        layout.addWidget(subtitle)

        # Input Fields
        self.dhcp_enabled = QCheckBox("DHCP Enabled")
        layout.addWidget(self.dhcp_enabled)

        layout.addWidget(QLabel("IP Address:"))
        self.ip_address = QLineEdit()
        self.ip_address.setMaxLength(15)
        layout.addWidget(self.ip_address)

        layout.addWidget(QLabel("Netmask:"))
        self.netmask = QSpinBox()
        self.netmask.setRange(0, 32)
        layout.addWidget(self.netmask)

        layout.addWidget(QLabel("Gateway:"))
        self.gateway = QLineEdit()
        self.gateway.setMaxLength(15)
        layout.addWidget(self.gateway)

        layout.addWidget(QLabel("DNS 1:"))
        self.dns1 = QLineEdit()
        self.dns1.setMaxLength(15)
        layout.addWidget(self.dns1)

        layout.addWidget(QLabel("DNS 2:"))
        self.dns2 = QLineEdit()
        self.dns2.setMaxLength(15)
        layout.addWidget(self.dns2)

        layout.addWidget(QLabel("DNS 3:"))
        self.dns3 = QLineEdit()
        self.dns3.setMaxLength(15)
        layout.addWidget(self.dns3)

        # Previous/Next Buttons
        button_layout = QVBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(2))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(4))
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)