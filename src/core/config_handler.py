import json
from src.core.logging_config import setup_logger

class ConfigHandler:
    def __init__(self):
        self.logger = setup_logger()
        self.config_schema = {
            "wifi": {
                "ssid": str,
                "password": str,
                "enterpriseMode": int,
                "enterpriseIdentity": str,
                "enterpriseUsername": str
            },
            "mqtt": {
                "host": str,
                "hostType": str,
                "port": int,
                "username": str,
                "password": str
            },
            "ip": {
                "dhcpEnabled": bool,
                "ipAddress": str,
                "netmask": int,
                "gateway": str,
                "dns1": str,
                "dns2": str,
                "dns3": str
            },
            "sntp": {
                "server1": {"value": str, "type": str},
                "server2": {"value": str, "type": str},
                "server3": {"value": str, "type": str}
            }
        }
        self.max_lengths = {
            "wifi": {
                "ssid": 32,
                "password": 64,
                "enterpriseIdentity": 64,
                "enterpriseUsername": 64
            },
            "mqtt": {
                "host": 64,
                "hostType": 16,
                "username": 32,
                "password": 32
            },
            "ip": {
                "ipAddress": 15,
                "gateway": 15,
                "dns1": 15,
                "dns2": 15,
                "dns3": 15
            },
            "sntp": {
                "server1": {"value": 32, "type": 16},
                "server2": {"value": 32, "type": 16},
                "server3": {"value": 32, "type": 16}
            }
        }

    def validate_config(self, config):
        """Validate configuration against the schema and length limits."""
        try:
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")
            for section, fields in self.config_schema.items():
                if section not in config:
                    raise ValueError(f"Missing section: {section}")
                for field, field_type in fields.items():
                    if field not in config[section]:
                        raise ValueError(f"Missing field: {section}.{field}")
                    if isinstance(field_type, dict):
                        if not isinstance(config[section][field], dict):
                            raise ValueError(f"Invalid type for {section}.{field}: expected dict")
                        for subfield, subfield_type in field_type.items():
                            if subfield not in config[section][field]:
                                raise ValueError(f"Missing subfield: {section}.{field}.{subfield}")
                            if not isinstance(config[section][field][subfield], subfield_type):
                                raise ValueError(f"Invalid type for {section}.{field}.{subfield}")
                            if section in self.max_lengths and field in self.max_lengths[section] and subfield in self.max_lengths[section][field]:
                                max_len = self.max_lengths[section][field][subfield]
                                if len(config[section][field][subfield]) > max_len:
                                    raise ValueError(f"{section}.{field}.{subfield} exceeds {max_len} characters")
                    else:
                        if not isinstance(config[section][field], field_type):
                            raise ValueError(f"Invalid type for {section}.{field}")
                        if section in self.max_lengths and field in self.max_lengths[section]:
                            max_len = self.max_lengths[section][field]
                            if isinstance(config[section][field], str) and len(config[section][field]) > max_len:
                                raise ValueError(f"{section}.{field} exceeds {max_len} characters")
                        if field == "enterpriseMode" and not (0 <= config[section][field] <= 255):
                            raise ValueError("enterpriseMode must be 0-255")
                        if field == "port" and not (0 <= config[section][field] <= 65535):
                            raise ValueError("port must be 0-65535")
                        if field == "netmask" and not (0 <= config[section][field] <= 32):
                            raise ValueError("netmask must be 0-32")
            return True
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            raise

    def serialize_config(self, config):
        """Serialize configuration to JSON bytes with a format identifier."""
        try:
            self.validate_config(config)
            json_str = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
            data = b"NFCCFG" + json_str.encode("utf-8")
            self.logger.info(f"Serialized config size before padding: {len(data)} bytes")
            if len(data) > 896:  # Max 56 blocks (4-63) = 896 bytes
                raise ValueError("Configuration too large for NFC storage")
            # Pad to multiple of 16 bytes
            data += b"\x00" * (16 - (len(data) % 16)) if len(data) % 16 != 0 else b""
            self.logger.info(f"Serialized config size after padding: {len(data)} bytes")
            return data
        except Exception as e:
            self.logger.error(f"Serialization failed: {e}")
            raise

    def deserialize_config(self, data):
        """Deserialize JSON bytes to configuration, checking format identifier."""
        try:
            if not data.startswith(b"NFCCFG"):
                raise ValueError("Invalid format identifier")
            json_str = data[6:].decode("utf-8").rstrip("\x00")
            config = json.loads(json_str)
            self.validate_config(config)
            self.logger.info("Deserialized config successfully")
            return config
        except Exception as e:
            self.logger.error(f"Deserialization failed: {e}")
            raise