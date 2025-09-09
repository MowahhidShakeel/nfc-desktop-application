from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QGroupBox, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class MqttTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # === Scrollable container ===
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(10)

        #  Title 
        title_label = QLabel("MQTT Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Configure MQTT broker settings for device communication.")
        subtitle_label.setStyleSheet("color: grey;")
        main_layout.addWidget(subtitle_label)

        #  Broker Settings Group 
        self.broker_group = self.create_group_box(
            "Broker Settings",
            "Enter the MQTT broker hostname or IP address.",
            "src/gui/assets/broker_icon.png"
        )
        broker_layout = self.broker_group.layout()

        # Host
        broker_layout.addWidget(QLabel("Host"))
        self.host = QLineEdit()
        self.host.setMaxLength(64)
        self.host.setPlaceholderText("mqtt.example.com or 192.168.1.100")
        self.set_field_style(self.host)
        broker_layout.addWidget(self.host)

        mqtt_label = QLabel("Enter hostname or IPv4 address of the MQTT broker.")
        mqtt_label.setStyleSheet("color: grey;")
        broker_layout.addWidget(mqtt_label)

        main_layout.addWidget(self.broker_group)

        # Authentication Group 
        self.auth_group = self.create_group_box(
            "Authentication",
            "Enter authentication details for the MQTT broker.",
            "src/gui/assets/authentication_icon.png"
        )
        auth_layout = self.auth_group.layout()

        # Username
        auth_layout.addWidget(QLabel("Username"))
        self.username = QLineEdit()
        self.username.setMaxLength(32)
        self.username.setPlaceholderText("Enter MQTT username")
        self.set_field_style(self.username)
        auth_layout.addWidget(self.username)

        # Password
        auth_layout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setMaxLength(32)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter MQTT password")
        self.set_field_style(self.password)
        auth_layout.addWidget(self.password)

        main_layout.addWidget(self.auth_group)

        # Navigation Buttons 
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
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(1))

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

        main_layout.addStretch(1)  # keeps buttons pinned to bottom
        main_layout.addLayout(button_layout)

        # === Scroll Area ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # Tab layout
        tab_layout = QVBoxLayout(self)
        tab_layout.addWidget(scroll_area)
        self.setLayout(tab_layout)

    # Helper UI Methods
    def create_group_box(self, title, subtitle, icon_path):
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

    def set_spinbox_style(self, widget):
        widget.setStyleSheet("""
            QSpinBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QSpinBox:focus {
                border: 1px solid #555555;
            }
        """)

    # Validation 
    def is_valid(self):
        errors = []
        self.clear_error_styles()

        # Add error checks here 

        if errors:
            for _, widget in errors:
                widget.setStyleSheet("""
                    QLineEdit, QSpinBox {
                        border: 1px solid red;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
            self.parent.log("Add MQTT error message here")
            return False
        return True

    def next_clicked(self):
        """Check valid inputs and navigate to next tab if valid"""
        if (self.is_valid()):
            self.parent.tabs.setCurrentIndex(3)
            
    def clear_error_styles(self):
        self.set_field_style(self.host)
        self.set_field_style(self.username)
        self.set_field_style(self.password)

    def show_error_message(self, text):
        msg = QMessageBox(self)
        msg.setWindowTitle("Validation Error")
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Warning)

        # Adaptive theme-safe colors
        palette = self.palette()
        bg_color = palette.window().color().name()
        fg_color = palette.windowText().color().name()
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {bg_color};
                color: {fg_color};
            }}
            QLabel {{
                color: {fg_color};
            }}
        """)
        msg.exec()
