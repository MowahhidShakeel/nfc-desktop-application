# src/gui/central_data.py
from dataclasses import dataclass

@dataclass
class FormData:
    # WiFi
    wifi_ssid: str = ""
    wifi_security: str = ""
    wifi_password: str = ""

    # MQTT
    mqtt_host: str = ""
    mqtt_host_type: str = ""
    mqtt_username: str = ""
    mqtt_password: str = ""

    # IP
    ip_dhcp_enabled: bool = False
    ip_address: str = ""
    ip_netmask: str = ""
    ip_gateway: str = ""
    ip_dns1: str = ""

    # SNTP
    sntp_primary_server: str = ""
    sntp_secondary_server: str = ""
    sntp_tertiary_server: str = ""

    def reset(self):
        """Clear all fields for a new session."""
        for field in self.__dataclass_fields__:
            value_type = type(getattr(self, field))
            setattr(self, field, value_type())
