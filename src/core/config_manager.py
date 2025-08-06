import json
from src.core.logging_config import setup_logger

class ConfigManager:
    def __init__(self):
        self.logger = setup_logger()

    def get_default_config(self):
        """Return default network configuration."""
        return {
            "wifi": {
                "ssid": "",
                "password": "",
                "enterpriseMode": 255,
                "enterpriseIdentity": "",
                "enterpriseUsername": ""
            },
            "mqtt": {
                "host": "",
                "hostType": "hostname",
                "port": 1883,
                "username": "",
                "password": ""
            },
            "ip": {
                "dhcpEnabled": True,
                "ipAddress": "",
                "netmask": 24,
                "gateway": "",
                "dns1": "",
                "dns2": "",
                "dns3": ""
            },
            "sntp": {
                "server1": {"value": "0.pool.ntp.org", "type": "hostname"},
                "server2": {"value": "1.pool.ntp.org", "type": "hostname"},
                "server3": {"value": "2.pool.ntp.org", "type": "hostname"}
            }
        }

    def load_config(self, file_path):
        """Load configuration from JSON file."""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            if not all(key in config for key in ["wifi", "mqtt", "ip", "sntp"]):
                self.logger.error("Invalid JSON configuration format")
                raise Exception("Invalid JSON configuration format")
            self.logger.info(f"Loaded configuration from {file_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def save_config(self, config, file_path):
        """Save configuration to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Saved configuration to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise