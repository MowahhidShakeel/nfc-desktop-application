from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLabel, QTabWidget, QFileDialog, QTextEdit
from PyQt6.QtGui import QIcon
from src.gui.import_tab import ImportTab
from src.gui.wifi_tab import WifiTab
from src.gui.mqtt_tab import MqttTab
from src.gui.ip_tab import IpTab
from src.gui.sntp_tab import SntpTab
from src.gui.summary_tab import SummaryTab
from src.gui.write_tags_tab import WriteTagsTab
from src.gui.read_tags_tab import ReadTagsTab
from src.core.nfc_handler import NFCHandler
from src.core.logging_config import setup_logger
from src.gui.themes import STYLESHEET
import sys
import json

class NFCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NFC Desktop Application")
        self.setGeometry(100, 100, 600, 900)
        self.setStyleSheet(STYLESHEET)

        # Initialize logger and NFC handler
        self.logger = setup_logger()
        self.nfc = NFCHandler()
        self.is_connected = False

        # Create main layout
        main_layout = QVBoxLayout()

        # Status label
        self.status_label = QLabel("No reader detected")
        main_layout.addWidget(self.status_label)

        # Tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # All tabs
        self.import_tab = ImportTab(self)
        self.tabs.addTab(self.import_tab, "Import")

        self.wifi_tab = WifiTab(self)
        self.tabs.addTab(self.wifi_tab, "WiFi")

        self.mqtt_tab = MqttTab(self)
        self.tabs.addTab(self.mqtt_tab, "MQTT")

        self.ip_tab = IpTab(self)
        self.tabs.addTab(self.ip_tab, "IP")

        self.sntp_tab = SntpTab(self)
        self.tabs.addTab(self.sntp_tab, "SNTP")

        self.summary_tab = SummaryTab(self)
        self.tabs.addTab(self.summary_tab, "Summary")

        self.write_tags_tab = WriteTagsTab(self)
        self.tabs.addTab(self.write_tags_tab, "Write Tags")

        self.read_tags_tab = ReadTagsTab(self)
        self.tabs.addTab(self.read_tags_tab, "Read Tags")

        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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

    def connect_reader(self):
        """Connect to the NFC reader."""
        try:
            if self.nfc.connect():
                self.is_connected = True
                self.status_label.setText("Connected to reader")
                self.log("Connected to reader")
                self.write_tags_tab.connect_button.setEnabled(False)
        except Exception as e:
            self.status_label.setText("Connection failed")
            self.log(f"Error: {e}", level="ERROR")

    def import_json(self, file_name=None):
        """Import network configuration from a JSON file."""
        try:
            if not file_name:
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
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                self.log(f"Exported JSON to {file_name}")
        except Exception as e:
            self.log(f"Export error: {e}", level="ERROR")

    def new_configuration(self):
        """Clear form for a new configuration."""
        try:
            self.wifi_tab.ssid.clear()
            self.wifi_tab.password.clear()
            self.wifi_tab.enterprise_mode.setValue(255)
            self.wifi_tab.enterprise_identity.clear()
            self.wifi_tab.enterprise_username.clear()
            self.mqtt_tab.host.clear()
            self.mqtt_tab.host_type.setText("hostname")
            self.mqtt_tab.port.setValue(1883)
            self.mqtt_tab.username.clear()
            self.mqtt_tab.password.clear()
            self.ip_tab.dhcp_enabled.setChecked(True)
            self.ip_tab.ip_address.clear()
            self.ip_tab.netmask.setValue(24)
            self.ip_tab.gateway.clear()
            self.ip_tab.dns1.clear()
            self.ip_tab.dns2.clear()
            self.ip_tab.dns3.clear()
            self.sntp_tab.server1_value.setText("0.pool.ntp.org")
            self.sntp_tab.server1_type.setText("hostname")
            self.sntp_tab.server2_value.setText("1.pool.ntp.org")
            self.sntp_tab.server2_type.setText("hostname")
            self.sntp_tab.server3_value.setText("2.pool.ntp.org")
            self.sntp_tab.server3_type.setText("hostname")
            self.log("New configuration created")
            self.update_summary()
        except Exception as e:
            self.log(f"New config error: {e}", level="ERROR")

    def read_nfc_config(self):
        """Read network configuration from NFC tag."""
        try:
            data = self.nfc.read_config()
            config = self.nfc.config_handler.deserialize_config(data)
            self.set_config(config)
            self.log("Read configuration from NFC tag")
        except Exception as e:
            self.log(f"Read NFC error: {e}", level="ERROR")

    def write_nfc_config(self):
        """Write current configuration to NFC tag."""
        try:
            config = self.get_config()
            data = self.nfc.config_handler.serialize_config(config)
            self.nfc.write_config(data)
            self.log("Wrote configuration to NFC tag")
        except Exception as e:
            self.log(f"Write NFC error: {e}", level="ERROR")

    def get_config(self):
        """Get configuration from GUI fields."""
        config = {
            "wifi": {
                "ssid": self.wifi_tab.ssid.text(),
                "password": self.wifi_tab.password.text(),
                "enterpriseMode": self.wifi_tab.enterprise_mode.value(),
                "enterpriseIdentity": self.wifi_tab.enterprise_identity.text(),
                "enterpriseUsername": self.wifi_tab.enterprise_username.text()
            },
            "mqtt": {
                "host": self.mqtt_tab.host.text(),
                "hostType": self.mqtt_tab.host_type.text(),
                "port": self.mqtt_tab.port.value(),
                "username": self.mqtt_tab.username.text(),
                "password": self.mqtt_tab.password.text()
            },
            "ip": {
                "dhcpEnabled": self.ip_tab.dhcp_enabled.isChecked(),
                "ipAddress": self.ip_tab.ip_address.text(),
                "netmask": self.ip_tab.netmask.value(),
                "gateway": self.ip_tab.gateway.text(),
                "dns1": self.ip_tab.dns1.text(),
                "dns2": self.ip_tab.dns2.text(),
                "dns3": self.ip_tab.dns3.text()
            },
            "sntp": {
                "server1": {"value": self.sntp_tab.server1_value.text(), "type": self.sntp_tab.server1_type.text()},
                "server2": {"value": self.sntp_tab.server2_value.text(), "type": self.sntp_tab.server2_type.text()},
                "server3": {"value": self.sntp_tab.server3_value.text(), "type": self.sntp_tab.server3_type.text()}
            }
        }
        return config

    def set_config(self, config):
        """Set GUI fields from configuration."""
        try:
            self.wifi_tab.ssid.setText(config.get("wifi", {}).get("ssid", ""))
            self.wifi_tab.password.setText(config.get("wifi", {}).get("password", ""))
            self.wifi_tab.enterprise_mode.setValue(config.get("wifi", {}).get("enterpriseMode", 255))
            self.wifi_tab.enterprise_identity.setText(config.get("wifi", {}).get("enterpriseIdentity", ""))
            self.wifi_tab.enterprise_username.setText(config.get("wifi", {}).get("enterpriseUsername", ""))
            self.mqtt_tab.host.setText(config.get("mqtt", {}).get("host", ""))
            self.mqtt_tab.host_type.setText(config.get("mqtt", {}).get("hostType", "hostname"))
            self.mqtt_tab.port.setValue(config.get("mqtt", {}).get("port", 1883))
            self.mqtt_tab.username.setText(config.get("mqtt", {}).get("username", ""))
            self.mqtt_tab.password.setText(config.get("mqtt", {}).get("password", ""))
            self.ip_tab.dhcp_enabled.setChecked(config.get("ip", {}).get("dhcpEnabled", True))
            self.ip_tab.ip_address.setText(config.get("ip", {}).get("ipAddress", ""))
            self.ip_tab.netmask.setValue(config.get("ip", {}).get("netmask", 24))
            self.ip_tab.gateway.setText(config.get("ip", {}).get("gateway", ""))
            self.ip_tab.dns1.setText(config.get("ip", {}).get("dns1", ""))
            self.ip_tab.dns2.setText(config.get("ip", {}).get("dns2", ""))
            self.ip_tab.dns3.setText(config.get("ip", {}).get("dns3", ""))
            self.sntp_tab.server1_value.setText(config.get("sntp", {}).get("server1", {}).get("value", "0.pool.ntp.org"))
            self.sntp_tab.server1_type.setText(config.get("sntp", {}).get("server1", {}).get("type", "hostname"))
            self.sntp_tab.server2_value.setText(config.get("sntp", {}).get("server2", {}).get("value", "1.pool.ntp.org"))
            self.sntp_tab.server2_type.setText(config.get("sntp", {}).get("server2", {}).get("type", "hostname"))
            self.sntp_tab.server3_value.setText(config.get("sntp", {}).get("server3", {}).get("value", "2.pool.ntp.org"))
            self.sntp_tab.server3_type.setText(config.get("sntp", {}).get("server3", {}).get("type", "hostname"))
            self.update_summary()
        except Exception as e:
            self.log(f"Error setting config: {e}", level="ERROR")

    def update_summary(self):
        """Update the Summary tab with current configuration."""
        summary_text = (
            "WiFi Configuration:\n"
            f"  SSID: {self.wifi_tab.ssid.text()}\n"
            f"  Password: {self.wifi_tab.password.text()}\n"
            f"  Enterprise Mode: {self.wifi_tab.enterprise_mode.value()}\n"
            f"  Enterprise Identity: {self.wifi_tab.enterprise_identity.text()}\n"
            f"  Enterprise Username: {self.wifi_tab.enterprise_username.text()}\n\n"
            "MQTT Configuration:\n"
            f"  Host: {self.mqtt_tab.host.text()}\n"
            f"  Host Type: {self.mqtt_tab.host_type.text()}\n"
            f"  Port: {self.mqtt_tab.port.value()}\n"
            f"  Username: {self.mqtt_tab.username.text()}\n"
            f"  Password: {self.mqtt_tab.password.text()}\n\n"
            "IP Configuration:\n"
            f"  DHCP Enabled: {self.ip_tab.dhcp_enabled.isChecked()}\n"
            f"  IP Address: {self.ip_tab.ip_address.text()}\n"
            f"  Netmask: {self.ip_tab.netmask.value()}\n"
            f"  Gateway: {self.ip_tab.gateway.text()}\n"
            f"  DNS 1: {self.ip_tab.dns1.text()}\n"
            f"  DNS 2: {self.ip_tab.dns2.text()}\n"
            f"  DNS 3: {self.ip_tab.dns3.text()}\n\n"
            "SNTP Configuration:\n"
            f"  Server 1 Value: {self.sntp_tab.server1_value.text()}\n"
            f"  Server 1 Type: {self.sntp_tab.server1_type.text()}\n"
            f"  Server 2 Value: {self.sntp_tab.server2_value.text()}\n"
            f"  Server 2 Type: {self.sntp_tab.server2_type.text()}\n"
            f"  Server 3 Value: {self.sntp_tab.server3_value.text()}\n"
            f"  Server 3 Type: {self.sntp_tab.server3_type.text()}"
        )
        self.summary_tab.summary_display.setPlainText(summary_text)

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