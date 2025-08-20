from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from smartcard.scard import *
from smartcard.Exceptions import CardServiceException

class ReadTagsTab(QWidget):
    def __init__(self, parent, nfc_handler):
        super().__init__()
        self.parent = parent
        self.nfc_handler = nfc_handler
        self.is_connected = False
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Title
        title_label = QLabel("Read NFC Tags")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Connect your NFC reader to read configuration from Mifare Ultralight tags.")
        subtitle_label.setStyleSheet("color: grey;")
        main_layout.addWidget(subtitle_label)

        # NFC Reader Status Box
        self.reader_box = self.create_group_box(
            "NFC Reader Status",
            "Supported readers: ACR122U (USB-A), ACR1252U-M1 (USB-C).",
            "src/gui/assets/nfc_icon.png"
        )
        reader_layout = self.reader_box.layout()

        # Reader Connection Status
        status_layout = QHBoxLayout()
        status_label = QLabel("Reader Connection")
        status_label.setStyleSheet("font-size: 14px; color: #000000;")
        status_layout.addWidget(status_label)

        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ff6666;
                border: 1px solid #ff6666;
                border-radius: 10px;
                padding: 2px 8px;
            }
        """)
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status, alignment=Qt.AlignmentFlag.AlignRight)

        reader_layout.addLayout(status_layout)

        # Reader Detection Status
        self.reader_detected = QLabel("No reader detected")
        self.reader_detected.setStyleSheet("font-size: 12px; color: #999999;")
        reader_layout.addWidget(self.reader_detected)
        reader_layout.addStretch(1)

        main_layout.addWidget(self.reader_box)

        # Configuration Data Box
        self.config_box = self.create_group_box(
            "Configuration Data",
            "View the network configuration read from the NFC tag.",
            "src/gui/assets/config_icon.png"
        )
        config_layout = self.config_box.layout()

        self.config_status = QLabel("Configuration not loaded")
        self.config_status.setStyleSheet("font-size: 12px; color: #999999;")
        config_layout.addWidget(self.config_status)
        config_layout.addStretch(1)

        main_layout.addWidget(self.config_box)

        # Read Button
        read_button = QPushButton("Read from NFC Card")
        read_button.setStyleSheet("font-size: 14px; padding: 5px 15px;")
        read_button.clicked.connect(self.read_from_card)
        main_layout.addWidget(read_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

        # Attempt to connect to NFC reader
        self.update_connection_status()

    def create_group_box(self, title, description, icon_path):
        group_box = QGroupBox()
        layout = QVBoxLayout()
        group_box.setLayout(layout)

        heading_layout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QIcon(icon_path).pixmap(16, 16))
        heading_layout.addWidget(icon)
        sub_heading = QLabel(title)
        sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        heading_layout.addWidget(sub_heading)
        heading_layout.addStretch()
        layout.addLayout(heading_layout)

        desc = QLabel(description)
        desc.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(desc)

        return group_box

    def update_connection_status(self):
        try:
            self.nfc_handler.connect()
            self.is_connected = True
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #66cc66;
                    border: 1px solid #66cc66;
                    border-radius: 10px;
                    padding: 2px 8px;
                }
            """)
            self.reader_detected.setText(f"{str(self.nfc_handler.reader)} detected")
        except (CardServiceException, Exception) as e:
            self.is_connected = False
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #ff6666;
                    border: 1px solid #ff6666;
                    border-radius: 10px;
                    padding: 2px 8px;
                }
            """)
            self.reader_detected.setText("No reader detected")

    def read_from_card(self):
        if not self.is_connected:
            QMessageBox.warning(self, "Connection Error", "Please connect to an NFC reader first.")
            return

        try:
            card_count = 1
            all_configs = []
            while True:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Insert Card")
                msg_box.setText(f"Please insert card {card_count} and click OK to continue, or Cancel to stop.")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
                ret = msg_box.exec()

                if ret == QMessageBox.StandardButton.Cancel:
                    break

                config = self.nfc_handler.read_config()
                all_configs.append(config)
                self.parent.set_config(config)  # Update GUI with the last read config
                self.config_status.setText(f"Configuration read from card {card_count}")
                card_count += 1

            if all_configs:
                final_config = all_configs[-1]  # Use the last config for now
                self.parent.set_config(final_config)
                QMessageBox.information(self, "Read Success", "Configuration read from NFC card(s) successfully.")
                self.parent.tabs.setCurrentWidget(self.parent.summary_tab)
            else:
                QMessageBox.warning(self, "Read Warning", "No configuration data was read.")
        except Exception as e:
            QMessageBox.critical(self, "Read Error", f"Failed to read from NFC card: {str(e)}")