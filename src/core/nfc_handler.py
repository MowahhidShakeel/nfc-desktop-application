import sys
from smartcard.System import readers
from smartcard.util import toHexString
from Crypto.Cipher import DES3
import ipaddress

class NFCHandler:
    def __init__(self):
        self.connection = None
        self.reader = None

    def connect(self, reader_index: int = 0):
        r = readers()
        if not r:
            raise RuntimeError("No PC/SC readers found")
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()

    def tx_direct_transmit(self, payload_bytes):
        apdu = [0xFF, 0x00, 0x00, 0x00, len(payload_bytes)] + payload_bytes
        data, sw1, sw2 = self.connection.transmit(apdu)
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(f"Reader error SW={sw1:02X}{sw2:02X}")
        if len(data) < 3 or data[0:3] != [0xD5, 0x41, 0x00]:
            raise RuntimeError(f"PN532 error: {toHexString(data)}")
        return data[3:]

    def pn532_exchange(self, native_cmd):
        return self.tx_direct_transmit([0xD4, 0x40, 0x01] + native_cmd)

    def ulc_read_pages(self, start_page, end_page):
        if not (0 <= start_page <= end_page <= 47):
            raise ValueError("Pages must be between 0 and 47, with start_page <= end_page")
        result = b""
        for page in range(start_page, end_page + 1):
            resp = self.pn532_exchange([0x30, page & 0xFF])
            if len(resp) < 4:
                raise RuntimeError(f"Failed to read page {page}")
            result += bytes(resp[:4])
        return result

    def ulc_write_page(self, page, four_bytes):
        if len(four_bytes) != 4:
            raise ValueError("Data must be exactly 4 bytes")
        self.pn532_exchange([0xA2, page & 0xFF] + list(four_bytes))

    def ulc_authenticate_3des(self, key16):
        part1 = self.pn532_exchange([0x1A, 0x00])
        if len(part1) < 9 or part1[0] != 0xAF:
            raise RuntimeError(f"Auth part1 unexpected: {toHexString(list(part1))}")
        return True

    def read_write_nfc(self, action: str, start_page: int, end_page: int = None, data: bytes = None, key16: bytes = None):
        try:
            self.connect()
            action = action.lower()
            if action not in ['read', 'write']:
                raise ValueError("Action must be 'read' or 'write'")

            if action == 'read':
                if end_page is None:
                    end_page = start_page
                data = self.ulc_read_pages(start_page, end_page)
                return data
            else:
                if end_page is not None:
                    raise ValueError("end_page not required for write")
                if not 0 <= start_page <= 47:
                    raise ValueError("Page must be between 0 and 47")
                if data is None or len(data) != 4:
                    raise ValueError("Data must be exactly 4 bytes")
                if key16:
                    self.ulc_authenticate_3des(key16)
                self.ulc_write_page(start_page, data)
                return None

        except Exception as e:
            raise RuntimeError(f"Operation failed: {e}")
        finally:
            if self.connection:
                self.connection.disconnect()

    def get_uid(self):
        data, sw1, sw2 = self.connection.transmit([0xFF, 0xCA, 0x00, 0x00, 0x00])
        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError("Failed to get UID")
        return data

    def write_full_config(self, config, key16=None):
        try:
            self.connect()
            records = []

            # WiFi records
            if config.get("wifi"):
                wifi = config["wifi"]
                if wifi.get("ssid"):
                    records.append((0x02, wifi["ssid"].encode('ascii') + b'\x00'))  # String
                if wifi.get("enterpriseIdentity"):
                    records.append((0x03, wifi["enterpriseIdentity"].encode('ascii') + b'\x00'))  # String
                if wifi.get("enterpriseUsername"):
                    records.append((0x04, wifi["enterpriseUsername"].encode('ascii') + b'\x00'))  # String
                if wifi.get("password"):
                    records.append((0x05, wifi["password"].encode('ascii') + b'\x00'))  # String
                if wifi.get("enterpriseMode"):
                    mode_map = {"": 0xFF, "EAP-TLS": 0x00, "EAP-PEAP": 0x01, "EAP-TTLS": 0x02}
                    mode = mode_map.get(wifi["enterpriseMode"], 0xFF)
                    records.append((0x86, bytes([mode])))  # Byte

            # MQTT records
            if config.get("mqtt"):
                mqtt = config["mqtt"]
                if mqtt.get("host"):
                    try:
                        ip = ipaddress.ip_address(mqtt["host"])
                        records.append((0x50, ip.packed))  # IPv4
                    except ValueError:
                        records.append((0x10, mqtt["host"].encode('ascii') + b'\x00'))  # String
                if mqtt.get("port"):
                    records.append((0x80, bytes([mqtt["port"] >> 8, mqtt["port"] & 0xFF])))  # Approx as 2 bytes
                if mqtt.get("username"):
                    records.append((0x11, mqtt["username"].encode('ascii') + b'\x00'))  # String
                if mqtt.get("password"):
                    records.append((0x12, mqtt["password"].encode('ascii') + b'\x00'))  # String

            # IP records
            if config.get("ip"):
                ip_config = config["ip"]
                if ip_config.get("dhcpEnabled") is not None:
                    records.append((0x80, bytes([0 if ip_config["dhcpEnabled"] else 1])))  # Boolean
                if not ip_config.get("dhcpEnabled") and ip_config.get("ipAddress"):
                    ip = ipaddress.ip_address(ip_config["ipAddress"])
                    records.append((0x60, ip.packed))  # IPv4
                if not ip_config.get("dhcpEnabled") and ip_config.get("netmask"):
                    records.append((0xA1, bytes([int(ip_config["netmask"])])))  # Byte
                if not ip_config.get("dhcpEnabled") and ip_config.get("gateway"):
                    ip = ipaddress.ip_address(ip_config["gateway"])
                    records.append((0x62, ip.packed))  # IPv4
                if not ip_config.get("dhcpEnabled") and ip_config.get("dns1"):
                    ip = ipaddress.ip_address(ip_config["dns1"])
                    records.append((0x63, ip.packed))  # IPv4

            # SNTP records
            if config.get("sntp"):
                sntp = config["sntp"]
                if sntp.get("server1", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server1"]["value"])
                        records.append((0x70, ip.packed))  # IPv4
                    except ValueError:
                        records.append((0x30, sntp["server1"]["value"].encode('ascii') + b'\x00'))  # String
                if sntp.get("server2", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server2"]["value"])
                        records.append((0x71, ip.packed))  # IPv4
                    except ValueError:
                        records.append((0x31, sntp["server2"]["value"].encode('ascii') + b'\x00'))  # String
                if sntp.get("server3", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server3"]["value"])
                        records.append((0x72, ip.packed))  # IPv4
                    except ValueError:
                        records.append((0x32, sntp["server3"]["value"].encode('ascii') + b'\x00'))  # String

            # Add end of record list
            records.append((0x00, b''))

            # Write records to pages
            data = b''.join([bytes([key]) + value for key, value in records])
            if len(data) > 144:
                raise ValueError("Configuration exceeds 144 bytes")
            for i in range(0, len(data), 4):
                chunk = data[i:i+4].ljust(4, b'\x00')
                self.read_write_nfc(action="write", start_page=4 + (i // 4), data=chunk, key16=key16)

        except Exception as e:
            raise RuntimeError(f"Configuration write failed: {e}")
        finally:
            if self.connection:
                self.connection.disconnect()

    def read_config(self, key16=None):
        try:
            self.connect()
            data = self.read_write_nfc(action="read", start_page=4, end_page=39)
            config = {"wifi": {}, "mqtt": {}, "ip": {}, "sntp": {}}

            i = 0
            while i < len(data):
                if i >= 144:  # Safety limit
                    break
                key = data[i]
                i += 1

                if key == 0x00:  # End of record list
                    break

                # Determine data type and length based on key MSBs
                if key & 0xC0 == 0x00 and (key & 0x3F) != 0:  # String (0x01-0x3F with other bits)
                    value = b""
                    while i < len(data) and data[i] != 0x00:
                        value += bytes([data[i]])
                        i += 1
                    i += 1  # Skip NUL
                    value = value.decode('ascii', errors='ignore')
                elif key & 0xC0 == 0x40:  # IPv4 (0x40-0x7F)
                    if i + 3 < len(data):
                        value = bytes(data[i:i+4])
                        i += 4
                        value = str(ipaddress.IPv4Address(value))
                    else:
                        break
                elif key & 0xC0 == 0x80:  # Byte (0x80-0xBF)
                    if i < len(data):
                        value = data[i]
                        i += 1
                        value = int(value)
                    else:
                        break
                else:  # Skip reserved or invalid
                    break

                # Assign to config based on key LSBs
                key_id = key & 0x3F
                if key_id == 0x02: config["wifi"]["ssid"] = value
                elif key_id == 0x03: config["wifi"]["enterpriseIdentity"] = value
                elif key_id == 0x04: config["wifi"]["enterpriseUsername"] = value
                elif key_id == 0x05: config["wifi"]["password"] = value
                elif key_id == 0x06: config["wifi"]["enterpriseMode"] = {0x00: "EAP-TLS", 0x01: "EAP-PEAP", 0x02: "EAP-TTLS", 0xFF: ""}.get(value, "")
                elif key_id == 0x10 or key_id == 0x50: config["mqtt"]["host"] = value
                elif key_id == 0x11: config["mqtt"]["username"] = value
                elif key_id == 0x12: config["mqtt"]["password"] = value
                elif key_id == 0x80:  # Approx port or DHCP
                    if "port" not in config["mqtt"]:
                        config["mqtt"]["port"] = (value << 8) if i < len(data) else value  # Reconstruct 2-byte port if possible
                    else:
                        config["ip"]["dhcpEnabled"] = (value == 0)
                elif key_id == 0x20 or key_id == 0x60: config["ip"]["ipAddress"] = value
                elif key_id == 0x21 or key_id == 0xA1: config["ip"]["netmask"] = str(value)
                elif key_id == 0x22 or key_id == 0x62: config["ip"]["gateway"] = value
                elif key_id == 0x23 or key_id == 0x63: config["ip"]["dns1"] = value
                elif key_id == 0x30 or key_id == 0x70: config["sntp"]["server1"] = {"value": value}
                elif key_id == 0x31 or key_id == 0x71: config["sntp"]["server2"] = {"value": value}
                elif key_id == 0x32 or key_id == 0x72: config["sntp"]["server3"] = {"value": value}

            return config

        except Exception as e:
            raise RuntimeError(f"Configuration read failed: {e}")
        finally:
            if self.connection:
                self.connection.disconnect()

if __name__ == "__main__":
    handler = NFCHandler()
    # Example usage
    sample_config = {
        "wifi": {"ssid": "1212", "password": "1212", "enterpriseMode": "EAP-TLS", "enterpriseIdentity": "", "enterpriseUsername": ""},
        "mqtt": {"host": "192.168.1.1", "port": 1883, "username": "1212", "password": "1212"},
        "ip": {"dhcpEnabled": False, "ipAddress": "192.168.1.100", "netmask": "21", "gateway": "192.168.1.1", "dns1": "8.8.8.8"},
        "sntp": {"server1": {"value": "192.168.1.100"}, "server2": {"value": "1.pool.ntp.org"}, "server3": {"value": "2.pool.ntp.org"}}
    }
    try:
        handler.write_full_config(sample_config)
        print("Configuration written successfully")
        read_config = handler.read_config()
        print("Read configuration:", read_config)
    except Exception as e:
        print(f"Error: {e}")