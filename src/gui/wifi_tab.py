from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QComboBox, QCheckBox
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

class WifiTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.valid = True
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # === Title ===
        title_label = QLabel("WiFi Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 0;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Configure wireless network settings and authentication.")
        subtitle_label.setStyleSheet("color: grey;")
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
        group_layout.addWidget(self.security_type)

        # SSID
        group_layout.addWidget(QLabel("SSID (Network Name) *"))
        self.ssid = QLineEdit()
        self.ssid.setMaxLength(32)
        self.ssid.setPlaceholderText("Enter WiFi network name")
        self.set_field_style(self.ssid)
        group_layout.addWidget(self.ssid)

        # Password
        group_layout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setMaxLength(64)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter Wi-Fi password")

        main_layout.addWidget(self.network_group)

        # Checkbox to toggle show/hide
        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)


        # Add stretch to push button to the right
        group_layout.addStretch()
        group_layout.addWidget(self.password)
        group_layout.addWidget(self.show_password_checkbox)

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
        self.enterprise_mode.addItems(["","EAP-TLS", "EAP-PEAP", "EAP-TTLS"])
        enterprise_layout.addWidget(self.enterprise_mode)

        # Identity
        enterprise_layout.addWidget(QLabel("Identity"))
        self.enterprise_identity = QLineEdit()
        self.set_field_style(self.enterprise_identity)
        self.enterprise_identity.setPlaceholderText("user@domain.com")
        enterprise_layout.addWidget(self.enterprise_identity)

        # Username
        enterprise_layout.addWidget(QLabel("Username"))
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

    def toggle_enterprise_section(self, value):
        """Show or hide enterprise section based on security type."""
        self.enterprise_group.setVisible(value == "WPA2 Enterprise")

    def toggle_password_visibility(self, state):
        """Show/hide the password based on checkbox value """
        if state == Qt.CheckState.Checked.value:
            self.password.setEchoMode(QLineEdit.EchoMode.Normal)  
        else:
            self.password.setEchoMode(QLineEdit.EchoMode.Password)  
        
    def next_clicked(self):
        """Check valid inputs and navigate to next tab if valid"""
        if (self.is_valid()):
            self.parent.tabs.setCurrentIndex(2)
         
    def is_valid(self):
        """Validates required fields."""
        errors = []
        self.clear_error_styles()

        # SSID always required
        if not self.ssid.text().strip():
            errors.append(("SSID (Network Name) *", self.ssid))

        if errors:
            for field_name, widget in errors:
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid red;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
            
            self.parent.log("Add Wifi error message here")

            return False
        
        # If everything is valid, go to next tab
        return True

    def clear_error_styles(self):
        """Reset all field styles."""
        self.set_field_style(self.ssid)
