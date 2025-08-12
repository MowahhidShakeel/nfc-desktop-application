from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

class SntpTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("SNTP Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Configure your SNTP servers.")
        layout.addWidget(subtitle)

        # Input Fields
        layout.addWidget(QLabel("Server 1 Value:"))
        self.server1_value = QLineEdit()
        self.server1_value.setMaxLength(32)
        layout.addWidget(self.server1_value)

        layout.addWidget(QLabel("Server 1 Type:"))
        self.server1_type = QLineEdit()
        self.server1_type.setMaxLength(16)
        layout.addWidget(self.server1_type)

        layout.addWidget(QLabel("Server 2 Value:"))
        self.server2_value = QLineEdit()
        self.server2_value.setMaxLength(32)
        layout.addWidget(self.server2_value)

        layout.addWidget(QLabel("Server 2 Type:"))
        self.server2_type = QLineEdit()
        self.server2_type.setMaxLength(16)
        layout.addWidget(self.server2_type)

        layout.addWidget(QLabel("Server 3 Value:"))
        self.server3_value = QLineEdit()
        self.server3_value.setMaxLength(32)
        layout.addWidget(self.server3_value)

        layout.addWidget(QLabel("Server 3 Type:"))
        self.server3_type = QLineEdit()
        self.server3_type.setMaxLength(16)
        layout.addWidget(self.server3_type)

        # Previous/Next Buttons
        button_layout = QVBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(3))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(5))
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)