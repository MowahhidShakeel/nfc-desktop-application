from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import re

class SntpTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # === Title ===
        title_label = QLabel("SNTP Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 0;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Configure Simple Network Time Protocol (SNTP) servers for time synchronization.")
        subtitle_label.setStyleSheet("color: grey; margin: 0;")
        main_layout.addWidget(subtitle_label)

        # === Time Servers Group ===
        self.time_servers_group = self.create_group_box(
            "Time Servers",
            "Configure up to three SNTP servers for reliable time synchronization.",
            "src/gui/assets/time_icon.png"
        )

        group_layout = self.time_servers_group.layout()

        # Primary SNTP Server (Required)
        group_layout.addWidget(QLabel("Primary SNTP Server *"))
        self.primary_server = QLineEdit()
        self.set_field_style(self.primary_server)
        self.primary_server.setText("0.pool.ntp.org")
        self.primary_server.setPlaceholderText("Enter hostname (e.g., pool.ntp.org) or IPv4 address")
        group_layout.addWidget(self.primary_server)

        # Secondary SNTP Server (Optional, default)
        group_layout.addWidget(QLabel("Secondary SNTP Server"))
        self.secondary_server = QLineEdit()
        self.set_field_style(self.secondary_server)
        self.secondary_server.setText("1.pool.ntp.org")
        self.secondary_server.setPlaceholderText("Optional: Backup time server")
        group_layout.addWidget(self.secondary_server)

        # Tertiary SNTP Server (Optional, default)
        group_layout.addWidget(QLabel("Tertiary SNTP Server"))
        self.tertiary_server = QLineEdit()
        self.set_field_style(self.tertiary_server)
        self.tertiary_server.setText("2.pool.ntp.org")
        self.tertiary_server.setPlaceholderText("Optional: Third backup time server")
        group_layout.addWidget(self.tertiary_server)

        main_layout.addWidget(self.time_servers_group)

        # === Navigation Buttons ===
        button_layout = QHBoxLayout()

        prev_button = QPushButton("Previous")
        prev_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(3))

        next_button = QPushButton("Next")
        next_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        next_button.clicked.connect(self.next_clicked)

        button_layout.addWidget(prev_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(next_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def create_group_box(self, title, subtitle, icon_path):
        """Creates a styled QGroupBox with title, subtitle, and optional icon."""
        group_box = QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        header_layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setFixedSize(16, 16)
        header_label = QLabel(title)
        header_label.setStyleSheet("font-weight: bold; font-size: 15px; margin: 0;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: grey; font-size: 12px; margin: 0;")
        layout.addWidget(subtitle_label)

        group_box.setLayout(layout)
        return group_box

    def set_field_style(self, widget):
        """Adds focus highlighting style to QLineEdit."""
        widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #555555;
            }
        """)

    def is_valid(self):
        """Validates required fields and logs errors."""
        errors = []
        self.clear_error_styles()

        if not self.primary_server.text().strip():
            errors.append(("Primary SNTP Server *", self.primary_server))
        elif not self.is_valid_hostname_or_ip(self.primary_server.text().strip()):
            errors.append(("Primary SNTP Server * (invalid format)", self.primary_server))

        # Secondary/Tertiary are optional but validate if not empty
        if self.secondary_server.text().strip() and not self.is_valid_hostname_or_ip(self.secondary_server.text().strip()):
            errors.append(("Secondary SNTP Server (invalid format)", self.secondary_server))

        if self.tertiary_server.text().strip() and not self.is_valid_hostname_or_ip(self.tertiary_server.text().strip()):
            errors.append(("Tertiary SNTP Server (invalid format)", self.tertiary_server))

        if errors:
            for field_name, widget in errors:
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid red;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
            self.parent.log("Add SNTP error message here")
            for field_name, _ in errors:
                self.parent.log(f"Validation error: {field_name}", level="ERROR")
            return False

        self.parent.log("SNTP settings validated successfully.")
        return True

    def next_clicked(self):
        """Check valid inputs and navigate to next tab if valid"""
        if (self.is_valid()):
            self.parent.tabs.setCurrentIndex(5)
            
    def is_valid_hostname_or_ip(self, value):
        """Basic hostname or IPv4 validation."""
        ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        hostname_pattern = r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(?:\.[A-Za-z]{2,})+$"
        return re.match(ip_pattern, value) or re.match(hostname_pattern, value)


    def clear_error_styles(self):
        """Reset all field styles."""
        self.set_field_style(self.primary_server)
        self.set_field_style(self.secondary_server)
        self.set_field_style(self.tertiary_server)
