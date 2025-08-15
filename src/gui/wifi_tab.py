from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QGroupBox, QComboBox, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class WifiTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.data = parent.data

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # === Title ===
        title_label = QLabel("WiFi Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 0;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Configure wireless network settings and authentication.")
        subtitle_label.setStyleSheet("color: grey; margin: 0;")
        main_layout.addWidget(subtitle_label)

        # === Network Settings Group ===
        self.network_group = self.create_group_box(
            "Network Settings",
            "Enter the WiFi network name and authentication details.",
            "src/gui/assets/wifi_icon.png"
        )

        group_layout = self.network_group.layout()

        # Security Type
        group_layout.addWidget(QLabel("Security Type"))
        self.security_type = QComboBox()
        self.security_type.addItems(["WPA2 Personal", "WPA2 Enterprise"])
        self.security_type.currentTextChanged.connect(self.toggle_enterprise_section)
        self.security_type.currentTextChanged.connect(self.on_security_changed)
        group_layout.addWidget(self.security_type)

        # SSID
        group_layout.addWidget(QLabel("SSID (Network Name) *"))
        self.ssid = QLineEdit()
        self.ssid.setMaxLength(32)
        self.ssid.setPlaceholderText("Enter WiFi network name")
        self.set_field_style(self.ssid)
        group_layout.addWidget(self.ssid)

        # Password
        group_layout.addWidget(QLabel("Password *"))
        self.password = QLineEdit()
        self.password.setMaxLength(64)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter WiFi password")
        self.set_field_style(self.password)
        group_layout.addWidget(self.password)

        self.ssid.textChanged.connect(lambda t: setattr(self.data, "wifi_ssid", t))
        self.password.textChanged.connect(lambda t: setattr(self.data, "wifi_password", t))
        
        main_layout.addWidget(self.network_group)

        # === Enterprise Settings Group (Hidden initially) ===
        self.enterprise_group = self.create_group_box(
            "Enterprise Settings",
            "Additional settings for WPA2 Enterprise networks.",
            "src/gui/assets/enterprise_icon.png"
        )

        enterprise_layout = self.enterprise_group.layout()

        # Enterprise Mode
        enterprise_layout.addWidget(QLabel("Authentication Mode:"))
        self.enterprise_mode = QComboBox()
        self.enterprise_mode.addItems(["EAP-TLS", "EAP-PEAP", "EAP-TTLS"])
        enterprise_layout.addWidget(self.enterprise_mode)

        # Identity
        enterprise_layout.addWidget(QLabel("Identity"))
        self.enterprise_identity = QLineEdit()
        self.set_field_style(self.enterprise_identity)
        self.enterprise_identity.setPlaceholderText("user@domain.com")
        enterprise_layout.addWidget(self.enterprise_identity)

        # Username
        enterprise_layout.addWidget(QLabel("Username *"))
        self.enterprise_username = QLineEdit()
        self.set_field_style(self.enterprise_username)
        self.enterprise_username.setPlaceholderText("Enter username")
        enterprise_layout.addWidget(self.enterprise_username)

        self.enterprise_group.setVisible(False)
        main_layout.addWidget(self.enterprise_group)

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
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(0))

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
        next_button.clicked.connect(self.validate_inputs)

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

    def on_security_changed(self, value):
        self.data.wifi_security = value
        self.toggle_enterprise_section(value)

    def toggle_enterprise_section(self, value):
        """Show or hide enterprise section based on security type."""
        self.enterprise_group.setVisible(value == "WPA2 Enterprise")

    def validate_inputs(self):
        """Validates required fields and shows error messages."""
        errors = []
        self.clear_error_styles()

        # SSID & Password always required
        if not self.ssid.text().strip():
            errors.append(("SSID (Network Name) *", self.ssid))
        if not self.password.text().strip():
            errors.append(("Password *", self.password))

        # Enterprise-specific validation
        if self.security_type.currentText() == "WPA2 Enterprise":
            if not self.enterprise_identity.text().strip():
                errors.append(("Identity *", self.enterprise_identity))
            if not self.enterprise_username.text().strip():
                errors.append(("Username *", self.enterprise_username))

        if errors:
            for field_name, widget in errors:
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid red;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)

            msg = QMessageBox(self)
            msg.setWindowTitle("Validation Error")
            msg.setText("Please fix all errors before proceeding to the next step.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            msg.exec()
            return

        # Save final validated values
        self.data.wifi_ssid = self.ssid.text().strip()
        self.data.wifi_password = self.password.text().strip()
        self.data.wifi_security = self.security_type.currentText()

        # If everything is valid, go to next tab
        self.parent.tabs.setCurrentIndex(2)

    def clear_error_styles(self):
        """Reset all field styles."""
        self.set_field_style(self.ssid)
        self.set_field_style(self.password)
        self.set_field_style(self.enterprise_identity)
        self.set_field_style(self.enterprise_username)
