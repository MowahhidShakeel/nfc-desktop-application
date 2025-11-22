from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLabel, QTabWidget, QFileDialog, QTextEdit, QSplitter
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
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
from src.version import APP_NAME, APP_VERSION
import sys, os
import json
from datetime import datetime

def resource_path(relative_path):
    """ Get absolute path to resource (for PyInstaller and dev). """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class NFCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setWindowIcon(QIcon(resource_path("resources/elixion_medical.ico")))
        
        # Screen-aware sizing
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen.width() * 0.7), int(screen.height() * 0.7))
        self.setMinimumSize(400, 900)

        self.setStyleSheet(STYLESHEET)
        
        # Initialize logger and NFC handler
        self.logger = setup_logger()
        self.nfc = NFCHandler()
        self.is_connected = False

        # Create main layout
        main_layout = QVBoxLayout()

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

        self.write_tags_tab = WriteTagsTab(self, self.nfc)
        self.tabs.addTab(self.write_tags_tab, "Write Tags")

        self.read_tags_tab = ReadTagsTab(self, self.nfc)
        self.tabs.addTab(self.read_tags_tab, "Read Tags")

        self.tabs.currentChanged.connect(lambda idx: 
            self.update_summary() if self.tabs.widget(idx) == self.summary_tab else None
        )
        
        self.tabs.currentChanged.connect(lambda idx:
            self.write_tags_tab.tab_shown() if self.tabs.widget(idx) == self.write_tags_tab else None
        )
        
        self.tabs.currentChanged.connect(lambda idx:
            self.read_tags_tab.tab_shown() if self.tabs.widget(idx) == self.read_tags_tab else None
        )
         
            
        # Log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.log_area)
        self.splitter.setSizes([600, 400])  # initial ratio
        main_layout.addWidget(self.splitter)

        # Set up central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initial check for reader
        if self.nfc.reader is None:
            self.log("No NFC reader detected or Smart Card service not running", level="ERROR")

    def switch_to_home_tab(self):
        """Switch back to the Summary tab after writing tags."""
        try:
            # Switch to Summary tab (index may vary depending on your tab order)
            self.tabs.setCurrentWidget(self.import_tab)
            self.log("Returned to Summary tab.", level="INFO")
        except Exception as e:
            self.log(f"Failed to switch to home tab: {e}", level="ERROR")

    def log(self, message, level="INFO"):
        """Append message to the log area and file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"{timestamp} - [{level}] - {message}"

        # Show in UI
        self.log_area.append(formatted)
        QApplication.processEvents()
    
        # Write to file via Python logging
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        elif level == "WARNING":
            self.logger.warning(message)

    def connect_reader(self):
        """Connect to the NFC reader."""
        try:
            self.nfc.connect()
            self.is_connected = True
            self.status_label.setText("Connected to reader")
            self.log("Connected to reader")
            self.write_tags_tab.update_connection_status()  
            self.read_tags_tab.update_connection_status()   
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
                
                self.tabs.setTabEnabled(1, True)
                self.tabs.setCurrentWidget(self.wifi_tab)
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
            self.wifi_tab.enterprise_mode.setCurrentIndex(0)
            self.wifi_tab.security_mode.setCurrentIndex(0)
            self.wifi_tab.enterprise_identity.clear()
            self.wifi_tab.enterprise_username.clear()
            self.mqtt_tab.host.clear()
            self.mqtt_tab.username.clear()
            self.mqtt_tab.password.clear()
            self.ip_tab.dhcp_toggle.setChecked(True)
            self.ip_tab.static_ip.clear()
            self.ip_tab.netmask.clear()
            self.ip_tab.gateway.clear()
            self.ip_tab.dns1.clear()
            self.ip_tab.dns2.clear()
            self.ip_tab.dns3.clear()
            self.sntp_tab.primary_server.clear()
            self.sntp_tab.secondary_server.clear()
            self.sntp_tab.tertiary_server.clear()

            self.tabs.setTabEnabled(1, True)
            self.tabs.setCurrentWidget(self.wifi_tab)
            self.log("New configuration created", level="INFO")
            self.update_summary()
        except Exception as e:
            self.log(f"New config error: {e}", level="ERROR")

    def read_nfc_config(self):
        """Read network configuration from NFC tag."""
        try:
            if not self.is_connected:
                self.log("NFC reader not connected", level="ERROR")
                return
            config = self.nfc.read_config()
            self.set_config(config)
            self.log("Read configuration from NFC tag", level="INFO")
            self.tabs.setCurrentWidget(self.summary_tab)
        except Exception as e:
            self.log(f"Read NFC error: {e}", level="ERROR")

    def write_nfc_config(self):
        """Write current configuration to NFC tag."""
        try:
            if not self.is_connected:
                self.log("NFC reader not connected", level="ERROR")
                return
            config = self.get_config()
            self.nfc.write_full_config(config)
            self.log("Successfully wrote configuration to NFC tag", level="INFO")
        except Exception as e:
            self.log(f"Write NFC error: {e}", level="ERROR")

    def get_config(self):
        """Get configuration from GUI fields."""
        config = {
            "wifi": {
                "ssid": self.wifi_tab.ssid.text(),
                "password": self.wifi_tab.password.text(),
                "enterpriseMode": self.wifi_tab.enterprise_mode.currentText(),
                "enterpriseIdentity": self.wifi_tab.enterprise_identity.text(),
                "enterpriseUsername": self.wifi_tab.enterprise_username.text(),
                "securityMode": self.wifi_tab.security_mode.currentText(),
            },
            "mqtt": {
                "host": self.mqtt_tab.host.text(),
                "username": self.mqtt_tab.username.text(),
                "password": self.mqtt_tab.password.text()
            },
            "ip": {
                "dhcpEnabled": self.ip_tab.dhcp_toggle.isChecked(),
                "ipAddress": self.ip_tab.static_ip.text(),
                "netmask": self.ip_tab.netmask.text(),
                "gateway": self.ip_tab.gateway.text(),
                "dns1": self.ip_tab.dns1.text(),
                "dns2": self.ip_tab.dns2.text(),
                "dns3": self.ip_tab.dns3.text()
            },
            "sntp": {
                "server1": {"value": self.sntp_tab.primary_server.text()},
                "server2": {"value": self.sntp_tab.secondary_server.text()},
                "server3": {"value": self.sntp_tab.tertiary_server.text()}
            }
        }
        return config

    def set_config(self, config):
        """Set configuration to GUI fields from a dict."""
        # ==== WIFI ====
        self.wifi_tab.ssid.setText(config["wifi"].get("ssid", ""))
        self.wifi_tab.password.setText(config["wifi"].get("password", ""))

        # If enterpriseMode is stored as index:
        if isinstance(config["wifi"].get("enterpriseMode"), int):
            self.wifi_tab.enterprise_mode.setCurrentIndex(config["wifi"]["enterpriseMode"])
        else:  # If stored as text
            self.wifi_tab.enterprise_mode.setCurrentText(config["wifi"].get("enterpriseMode", ""))

        self.wifi_tab.security_mode.setCurrentText(config["wifi"].get("securityMode", ""))
        self.wifi_tab.enterprise_identity.setText(config["wifi"].get("enterpriseIdentity", ""))
        self.wifi_tab.enterprise_username.setText(config["wifi"].get("enterpriseUsername", ""))

        # ==== MQTT ====
        self.mqtt_tab.host.setText(config["mqtt"].get("host", ""))
        self.mqtt_tab.username.setText(config["mqtt"].get("username", ""))
        self.mqtt_tab.password.setText(config["mqtt"].get("password", ""))

        # ==== IP ====
        self.ip_tab.dhcp_toggle.setChecked(config["ip"].get("dhcpEnabled", True))
        self.ip_tab.static_ip.setText(config["ip"].get("ipAddress", ""))
        self.ip_tab.netmask.setText(str(config["ip"].get("netmask", "")))
        self.ip_tab.gateway.setText(config["ip"].get("gateway", ""))
        self.ip_tab.dns1.setText(config["ip"].get("dns1", ""))
        if hasattr(self.ip_tab, "dns2"):
            self.ip_tab.dns2.setText(config["ip"].get("dns2", ""))
        if hasattr(self.ip_tab, "dns3"):
            self.ip_tab.dns3.setText(config["ip"].get("dns3", ""))

        # ==== SNTP ====
        self.sntp_tab.primary_server.setText(config["sntp"]["server1"].get("value", ""))
        self.sntp_tab.secondary_server.setText(config["sntp"]["server2"].get("value", ""))
        self.sntp_tab.tertiary_server.setText(config["sntp"]["server3"].get("value", ""))

    def update_summary(self):
        """Update the Summary tab labels from the current configuration."""
        # --- WiFi ---
        self.summary_tab.wifi_ssid.setText(f"SSID: {self.wifi_tab.ssid.text() or 'Not set'}")
        self.summary_tab.wifi_security.setText(f"Security: {self.wifi_tab.security_type.currentText() or 'Not set'}")
        self.summary_tab.wifi_password.setText(f"Password: {self.wifi_tab.password.text() or 'Not set'}")
        if (self.wifi_tab.security_type.currentText() == "WPA2 Enterprise"):
            self.summary_tab.wifi_identity.setText(f"Identity: {self.wifi_tab.enterprise_identity.text() or 'Not set'}")
            self.summary_tab.wifi_username.setText(f"Username: {self.wifi_tab.enterprise_username.text() or 'Not set'}")
            self.summary_tab.wifi_authentication.setText(f"Authentication Mode: {self.wifi_tab.enterprise_mode.currentText() or 'Not set'}")
            self.summary_tab.wifi_security_mode.setText(f"Security Mode:  {self.wifi_tab.security_mode.currentText() or 'Not set'}")

        # --- MQTT ---
        self.summary_tab.mqtt_host.setText(f"Host: {self.mqtt_tab.host.text() or 'Not set'}")
        self.summary_tab.mqtt_username.setText(f"Username: {self.mqtt_tab.username.text() or 'Not set'}")
        self.summary_tab.mqtt_password.setText(f"Password: {self.mqtt_tab.password.text() or 'Not set'}")

        # --- IP ---
        self.summary_tab.ip_dhcp.setText(
            f"DHCP: {'Enabled' if self.ip_tab.dhcp_toggle.isChecked() else 'Disabled'}"
        )
        self.summary_tab.ip_address.setText(f"IP Address: {self.ip_tab.static_ip.text() or 'Not set'}")
        self.summary_tab.ip_netmask.setText(f"Netmask/CIDR: {self.ip_tab.netmask.text() or 'Not set'}")
        self.summary_tab.ip_gateway.setText(f"Gateway: {self.ip_tab.gateway.text() or 'Not set'}")
        self.summary_tab.ip_dns.setText(f"Primary DNS: {self.ip_tab.dns1.text() or 'Not set'}")

        # --- SNTP ---
        self.summary_tab.sntp_server1.setText(f"Primary Server: {self.sntp_tab.primary_server.text() or 'Not set'}")
        self.summary_tab.sntp_server2.setText(f"Secondary Server: {self.sntp_tab.secondary_server.text() or 'Not set'}")
        self.summary_tab.sntp_server3.setText(f"Tertiary Server: {self.sntp_tab.tertiary_server.text() or 'Not set'}")

    def closeEvent(self, event):
        """Handle window close event to disconnect reader."""
        if self.is_connected:
            self.nfc.connection.disconnect()
            self.log("Disconnected from reader", level="ERROR")
        event.accept()
        
    def is_entire_config_valid(self):
        """Checks if the data in all configuration tabs is valid."""
        return (
            self.wifi_tab.is_valid() and
            self.mqtt_tab.is_valid() and
            self.ip_tab.is_valid() and
            self.sntp_tab.is_valid()
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NFCWindow()
    window.show()
    sys.exit(app.exec())