from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QTextEdit, QLabel, QFormLayout, QLineEdit, QCheckBox, QSpinBox,
    QFileDialog, QTabWidget, QTextBrowser
)
from src.core.nfc_handler import NFCHandler
from src.core.config_handler import ConfigHandler
from src.core.logging_config import setup_logger
import sys
import json

class NFCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC Desktop Application")
        self.setGeometry(100, 100, 600, 900)

        # Initialize logger, NFC handler, and config handler
        self.logger = setup_logger()
        self.nfc = NFCHandler()
        self.config_handler = ConfigHandler()
        self.is_connected = False

        # Create main layout
        main_layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("No reader detected")
        main_layout.addWidget(self.status_label)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Import tab
        import_widget = QWidget()
        import_layout = QVBoxLayout()
        self.import_button = QPushButton("Import JSON Config")
        self.export_button = QPushButton("Export JSON Config")
        self.new_config_button = QPushButton("New Configuration")
        self.import_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.new_config_button.setEnabled(True)
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.export_button)
        import_layout.addWidget(self.new_config_button)
        import_layout.addStretch()
        import_widget.setLayout(import_layout)
        self.tabs.addTab(import_widget, "Import")

        # WiFi tab
        wifi_widget = QWidget()
        wifi_layout = QFormLayout()
        self.wifi_ssid = QLineEdit()
        self.wifi_ssid.setMaxLength(32)
        self.wifi_password = QLineEdit()
        self.wifi_password.setMaxLength(64)
        self.wifi_enterprise_mode = QSpinBox()
        self.wifi_enterprise_mode.setRange(0, 255)
        self.wifi_enterprise_identity = QLineEdit()
        self.wifi_enterprise_identity.setMaxLength(64)
        self.wifi_enterprise_username = QLineEdit()
        self.wifi_enterprise_username.setMaxLength(64)
        wifi_layout.addRow("Wi-Fi SSID:", self.wifi_ssid)
        wifi_layout.addRow("Wi-Fi Password:", self.wifi_password)
        wifi_layout.addRow("Wi-Fi Enterprise Mode:", self.wifi_enterprise_mode)
        wifi_layout.addRow("Wi-Fi Enterprise Identity:", self.wifi_enterprise_identity)
        wifi_layout.addRow("Wi-Fi Enterprise Username:", self.wifi_enterprise_username)
        wifi_widget.setLayout(wifi_layout)
        self.tabs.addTab(wifi_widget, "WiFi")

        # MQTT tab
        mqtt_widget = QWidget()
        mqtt_layout = QFormLayout()
        self.mqtt_host = QLineEdit()
        self.mqtt_host.setMaxLength(64)
        self.mqtt_host_type = QLineEdit()
        self.mqtt_host_type.setMaxLength(16)
        self.mqtt_port = QSpinBox()
        self.mqtt_port.setRange(0, 65535)
        self.mqtt_username = QLineEdit()
        self.mqtt_username.setMaxLength(32)
        self.mqtt_password = QLineEdit()
        self.mqtt_password.setMaxLength(32)
        mqtt_layout.addRow("MQTT Host:", self.mqtt_host)
        mqtt_layout.addRow("MQTT Host Type:", self.mqtt_host_type)
        mqtt_layout.addRow("MQTT Port:", self.mqtt_port)
        mqtt_layout.addRow("MQTT Username:", self.mqtt_username)
        mqtt_layout.addRow("MQTT Password:", self.mqtt_password)
        mqtt_widget.setLayout(mqtt_layout)
        self.tabs.addTab(mqtt_widget, "MQTT")

        # IP tab
        ip_widget = QWidget()
        ip_layout = QFormLayout()
        self.ip_dhcp_enabled = QCheckBox()
        self.ip_address = QLineEdit()
        self.ip_address.setMaxLength(15)
        self.ip_netmask = QSpinBox()
        self.ip_netmask.setRange(0, 32)
        self.ip_gateway = QLineEdit()
        self.ip_gateway.setMaxLength(15)
        self.ip_dns1 = QLineEdit()
        self.ip_dns1.setMaxLength(15)
        self.ip_dns2 = QLineEdit()
        self.ip_dns2.setMaxLength(15)
        self.ip_dns3 = QLineEdit()
        self.ip_dns3.setMaxLength(15)
        ip_layout.addRow("IP DHCP Enabled:", self.ip_dhcp_enabled)
        ip_layout.addRow("IP Address:", self.ip_address)
        ip_layout.addRow("IP Netmask:", self.ip_netmask)
        ip_layout.addRow("IP Gateway:", self.ip_gateway)
        ip_layout.addRow("IP DNS 1:", self.ip_dns1)
        ip_layout.addRow("IP DNS 2:", self.ip_dns2)
        ip_layout.addRow("IP DNS 3:", self.ip_dns3)
        ip_widget.setLayout(ip_layout)
        self.tabs.addTab(ip_widget, "IP")

        # SNTP tab
        sntp_widget = QWidget()
        sntp_layout = QFormLayout()
        self.sntp_server1_value = QLineEdit()
        self.sntp_server1_value.setMaxLength(32)
        self.sntp_server1_type = QLineEdit()
        self.sntp_server1_type.setMaxLength(16)
        self.sntp_server2_value = QLineEdit()
        self.sntp_server2_value.setMaxLength(32)
        self.sntp_server2_type = QLineEdit()
        self.sntp_server2_type.setMaxLength(16)
        self.sntp_server3_value = QLineEdit()
        self.sntp_server3_value.setMaxLength(32)
        self.sntp_server3_type = QLineEdit()
        self.sntp_server3_type.setMaxLength(16)
        sntp_layout.addRow("SNTP Server 1 Value:", self.sntp_server1_value)
        sntp_layout.addRow("SNTP Server 1 Type:", self.sntp_server1_type)
        sntp_layout.addRow("SNTP Server 2 Value:", self.sntp_server2_value)
        sntp_layout.addRow("SNTP Server 2 Type:", self.sntp_server2_type)
        sntp_layout.addRow("SNTP Server 3 Value:", self.sntp_server3_value)
        sntp_layout.addRow("SNTP Server 3 Type:", self.sntp_server3_type)
        sntp_widget.setLayout(sntp_layout)
        self.tabs.addTab(sntp_widget, "SNTP")

        # Summary tab
        summary_widget = QWidget()
        summary_layout = QVBoxLayout()
        self.summary_display = QTextBrowser()
        self.summary_display.setReadOnly(True)
        self.update_summary()  # Initial empty summary
        summary_layout.addWidget(self.summary_display)
        summary_widget.setLayout(summary_layout)
        self.tabs.addTab(summary_widget, "Summary")

        # Write Tags tab
        write_tags_widget = QWidget()
        write_tags_layout = QVBoxLayout()
        self.connect_button = QPushButton("Connect to Reader")
        self.read_nfc_button = QPushButton("Read Config from NFC")
        self.write_nfc_button = QPushButton("Write Config to NFC")
        self.read_nfc_button.setEnabled(False)
        self.write_nfc_button.setEnabled(False)
        write_tags_layout.addWidget(self.connect_button)
        write_tags_layout.addWidget(self.read_nfc_button)
        write_tags_layout.addWidget(self.write_nfc_button)
        write_tags_layout.addStretch()
        write_tags_widget.setLayout(write_tags_layout)
        self.tabs.addTab(write_tags_widget, "Write Tags")

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect button signals
        self.connect_button.clicked.connect(self.connect_reader)
        self.import_button.clicked.connect(self.import_json)
        self.export_button.clicked.connect(self.export_json)
        self.new_config_button.clicked.connect(self.new_configuration)
        self.read_nfc_button.clicked.connect(self.read_nfc_config)
        self.write_nfc_button.clicked.connect(self.write_nfc_config)

        # Connect field changes to update summary
        self.wifi_ssid.textChanged.connect(self.update_summary)
        self.wifi_password.textChanged.connect(self.update_summary)
        self.wifi_enterprise_mode.valueChanged.connect(self.update_summary)
        self.wifi_enterprise_identity.textChanged.connect(self.update_summary)
        self.wifi_enterprise_username.textChanged.connect(self.update_summary)
        self.mqtt_host.textChanged.connect(self.update_summary)
        self.mqtt_host_type.textChanged.connect(self.update_summary)
        self.mqtt_port.valueChanged.connect(self.update_summary)
        self.mqtt_username.textChanged.connect(self.update_summary)
        self.mqtt_password.textChanged.connect(self.update_summary)
        self.ip_dhcp_enabled.stateChanged.connect(self.update_summary)
        self.ip_address.textChanged.connect(self.update_summary)
        self.ip_netmask.valueChanged.connect(self.update_summary)
        self.ip_gateway.textChanged.connect(self.update_summary)
        self.ip_dns1.textChanged.connect(self.update_summary)
        self.ip_dns2.textChanged.connect(self.update_summary)
        self.ip_dns3.textChanged.connect(self.update_summary)
        self.sntp_server1_value.textChanged.connect(self.update_summary)
        self.sntp_server1_type.textChanged.connect(self.update_summary)
        self.sntp_server2_value.textChanged.connect(self.update_summary)
        self.sntp_server2_type.textChanged.connect(self.update_summary)
        self.sntp_server3_value.textChanged.connect(self.update_summary)
        self.sntp_server3_type.textChanged.connect(self.update_summary)

        # Initial check for reader
        if self.nfc.reader is None:
            self.log("No NFC reader detected or Smart Card service not running", level="ERROR")

    def log(self, message, level="INFO"):
        """Append message to the log area and file."""
        self.log_area.append(message)
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)

    def update_summary(self):
        """Update the Summary tab with current configuration."""
        summary_text = (
            "Wi-Fi Configuration:\n"
            f"  SSID: {self.wifi_ssid.text()}\n"
            f"  Password: {self.wifi_password.text()}\n"
            f"  Enterprise Mode: {self.wifi_enterprise_mode.value()}\n"
            f"  Enterprise Identity: {self.wifi_enterprise_identity.text()}\n"
            f"  Enterprise Username: {self.wifi_enterprise_username.text()}\n\n"
            "MQTT Configuration:\n"
            f"  Host: {self.mqtt_host.text()}\n"
            f"  Host Type: {self.mqtt_host_type.text()}\n"
            f"  Port: {self.mqtt_port.value()}\n"
            f"  Username: {self.mqtt_username.text()}\n"
            f"  Password: {self.mqtt_password.text()}\n\n"
            "IP Configuration:\n"
            f"  DHCP Enabled: {self.ip_dhcp_enabled.isChecked()}\n"
            f"  IP Address: {self.ip_address.text()}\n"
            f"  Netmask: {self.ip_netmask.value()}\n"
            f"  Gateway: {self.ip_gateway.text()}\n"
            f"  DNS 1: {self.ip_dns1.text()}\n"
            f"  DNS 2: {self.ip_dns2.text()}\n"
            f"  DNS 3: {self.ip_dns3.text()}\n\n"
            "SNTP Configuration:\n"
            f"  Server 1 Value: {self.sntp_server1_value.text()}\n"
            f"  Server 1 Type: {self.sntp_server1_type.text()}\n"
            f"  Server 2 Value: {self.sntp_server2_value.text()}\n"
            f"  Server 2 Type: {self.sntp_server2_type.text()}\n"
            f"  Server 3 Value: {self.sntp_server3_value.text()}\n"
            f"  Server 3 Type: {self.sntp_server3_type.text()}"
        )
        self.summary_display.setPlainText(summary_text)

    def get_config(self):
        """Get configuration from GUI fields."""
        config = {
            "wifi": {
                "ssid": self.wifi_ssid.text(),
                "password": self.wifi_password.text(),
                "enterpriseMode": self.wifi_enterprise_mode.value(),
                "enterpriseIdentity": self.wifi_enterprise_identity.text(),
                "enterpriseUsername": self.wifi_enterprise_username.text()
            },
            "mqtt": {
                "host": self.mqtt_host.text(),
                "hostType": self.mqtt_host_type.text(),
                "port": self.mqtt_port.value(),
                "username": self.mqtt_username.text(),
                "password": self.mqtt_password.text()
            },
            "ip": {
                "dhcpEnabled": self.ip_dhcp_enabled.isChecked(),
                "ipAddress": self.ip_address.text(),
                "netmask": self.ip_netmask.value(),
                "gateway": self.ip_gateway.text(),
                "dns1": self.ip_dns1.text(),
                "dns2": self.ip_dns2.text(),
                "dns3": self.ip_dns3.text()
            },
            "sntp": {
                "server1": {"value": self.sntp_server1_value.text(), "type": self.sntp_server1_type.text()},
                "server2": {"value": self.sntp_server2_value.text(), "type": self.sntp_server2_type.text()},
                "server3": {"value": self.sntp_server3_value.text(), "type": self.sntp_server3_type.text()}
            }
        }
        return config

    def set_config(self, config):
        """Set GUI fields from configuration."""
        try:
            self.config_handler.validate_config(config)
            self.wifi_ssid.setText(config["wifi"]["ssid"])
            self.wifi_password.setText(config["wifi"]["password"])
            self.wifi_enterprise_mode.setValue(config["wifi"]["enterpriseMode"])
            self.wifi_enterprise_identity.setText(config["wifi"]["enterpriseIdentity"])
            self.wifi_enterprise_username.setText(config["wifi"]["enterpriseUsername"])
            self.mqtt_host.setText(config["mqtt"]["host"])
            self.mqtt_host_type.setText(config["mqtt"]["hostType"])
            self.mqtt_port.setValue(config["mqtt"]["port"])
            self.mqtt_username.setText(config["mqtt"]["username"])
            self.mqtt_password.setText(config["mqtt"]["password"])
            self.ip_dhcp_enabled.setChecked(config["ip"]["dhcpEnabled"])
            self.ip_address.setText(config["ip"]["ipAddress"])
            self.ip_netmask.setValue(config["ip"]["netmask"])
            self.ip_gateway.setText(config["ip"]["gateway"])
            self.ip_dns1.setText(config["ip"]["dns1"])
            self.ip_dns2.setText(config["ip"]["dns2"])
            self.ip_dns3.setText(config["ip"]["dns3"])
            self.sntp_server1_value.setText(config["sntp"]["server1"]["value"])
            self.sntp_server1_type.setText(config["sntp"]["server1"]["type"])
            self.sntp_server2_value.setText(config["sntp"]["server2"]["value"])
            self.sntp_server2_type.setText(config["sntp"]["server2"]["type"])
            self.sntp_server3_value.setText(config["sntp"]["server3"]["value"])
            self.sntp_server3_type.setText(config["sntp"]["server3"]["type"])
            self.update_summary()
        except Exception as e:
            self.log(f"Error setting config: {e}", level="ERROR")
            raise

    def connect_reader(self):
        """Connect to the NFC reader."""
        try:
            if self.nfc.connect():
                self.is_connected = True
                self.status_label.setText("Connected to reader")
                self.log("Connected to reader")
                self.connect_button.setEnabled(False)
                self.import_button.setEnabled(True)
                self.export_button.setEnabled(True)
                self.read_nfc_button.setEnabled(True)
                self.write_nfc_button.setEnabled(True)
        except Exception as e:
            self.status_label.setText("Connection failed")
            self.log(f"Error: {e}", level="ERROR")

    def import_json(self):
        """Import network configuration from a JSON file."""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Import JSON Config", "", "JSON Files (*.json)"
            )
            if file_name:
                with open(file_name, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.set_config(config)
                self.log(f"Imported JSON from {file_name}")
        except Exception as e:
            self.log(f"Import error: {e}", level="ERROR")

    def export_json(self):
        """Export current configuration to a JSON file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export JSON Config", "", "JSON Files (*.json)"
            )
            if file_name:
                config = self.get_config()
                self.config_handler.validate_config(config)
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                self.log(f"Exported JSON to {file_name}")
        except Exception as e:
            self.log(f"Export error: {e}", level="ERROR")

    def new_configuration(self):
        """Clear form for a new configuration."""
        try:
            self.wifi_ssid.clear()
            self.wifi_password.clear()
            self.wifi_enterprise_mode.setValue(255)
            self.wifi_enterprise_identity.clear()
            self.wifi_enterprise_username.clear()
            self.mqtt_host.clear()
            self.mqtt_host_type.setText("hostname")
            self.mqtt_port.setValue(1883)
            self.mqtt_username.clear()
            self.mqtt_password.clear()
            self.ip_dhcp_enabled.setChecked(True)
            self.ip_address.clear()
            self.ip_netmask.setValue(24)
            self.ip_gateway.clear()
            self.ip_dns1.clear()
            self.ip_dns2.clear()
            self.ip_dns3.clear()
            self.sntp_server1_value.setText("0.pool.ntp.org")
            self.sntp_server1_type.setText("hostname")
            self.sntp_server2_value.setText("1.pool.ntp.org")
            self.sntp_server2_type.setText("hostname")
            self.sntp_server3_value.setText("2.pool.ntp.org")
            self.sntp_server3_type.setText("hostname")
            self.log("New configuration created")
            self.update_summary()
        except Exception as e:
            self.log(f"New config error: {e}", level="ERROR")

    def read_nfc_config(self):
        """Read network configuration from NFC tag."""
        try:
            data = self.nfc.read_config()
            config = self.config_handler.deserialize_config(data)
            self.set_config(config)
            self.log("Read configuration from NFC tag")
        except Exception as e:
            self.log(f"Read NFC error: {e}", level="ERROR")

    def write_nfc_config(self):
        """Write current configuration to NFC tag."""
        try:
            config = self.get_config()
            data = self.config_handler.serialize_config(config)
            self.nfc.write_config(data)
            self.log("Wrote configuration to NFC tag")
        except Exception as e:
            self.log(f"Write NFC error: {e}", level="ERROR")

    def closeEvent(self, event):
        """Handle window close event to disconnect reader."""
        if self.is_connected:
            self.nfc.disconnect()
            self.log("Disconnected from reader")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFCWindow()
    window.show()
    sys.exit(app.exec())