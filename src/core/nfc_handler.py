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
    
    def disconnect(self):
        self.connection.disconnect()
        return

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
                    records.append((0x02, wifi["ssid"].encode('ascii') + b'\x00'))
                if wifi.get("enterpriseIdentity"):
                    records.append((0x03, wifi["enterpriseIdentity"].encode('ascii') + b'\x00'))
                if wifi.get("enterpriseUsername"):
                    records.append((0x04, wifi["enterpriseUsername"].encode('ascii') + b'\x00'))
                if wifi.get("password"):
                    records.append((0x05, wifi["password"].encode('ascii') + b'\x00'))
                if wifi.get("enterpriseMode"):
                    mode_map = {"": 0xFF, "EAP-TLS": 0x00, "EAP-PEAP": 0x01, "EAP-TTLS": 0x02}
                    mode = mode_map.get(wifi["enterpriseMode"], 0xFF)
                    records.append((0x86, bytes([mode])))

            # MQTT records
            if config.get("mqtt"):
                mqtt = config["mqtt"]
                if mqtt.get("host"):
                    records.append((0x10, mqtt["host"].encode('ascii') + b'\x00'))
                if mqtt.get("username"):
                    records.append((0x11, mqtt["username"].encode('ascii') + b'\x00'))
                if mqtt.get("password"):
                    records.append((0x12, mqtt["password"].encode('ascii') + b'\x00'))

            # IP records
            if config.get("ip"):
                ip_config = config["ip"]
                if ip_config.get("ipAddress"):
                    ip = ipaddress.ip_address(ip_config["ipAddress"])
                    records.append((0x60, ip.packed))
                if ip_config.get("netmask"):
                    records.append((0xA1, bytes([int(ip_config["netmask"])])))
                if ip_config.get("gateway"):
                    ip = ipaddress.ip_address(ip_config["gateway"])
                    records.append((0x62, ip.packed))
                if ip_config.get("dns1"):
                    ip = ipaddress.ip_address(ip_config["dns1"])
                    records.append((0x63, ip.packed))
                if ip_config.get("dns2"):
                    ip = ipaddress.ip_address(ip_config["dns2"])
                    records.append((0x64, ip.packed))
                if ip_config.get("dns3"):
                    ip = ipaddress.ip_address(ip_config["dns3"])
                    records.append((0x65, ip.packed))

            # SNTP records
            if config.get("sntp"):
                sntp = config["sntp"]
                if sntp.get("server1", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server1"]["value"])
                        records.append((0x70, ip.packed))
                    except ValueError:
                        records.append((0x30, sntp["server1"]["value"].encode('ascii') + b'\x00'))
                if sntp.get("server2", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server2"]["value"])
                        records.append((0x71, ip.packed))
                    except ValueError:
                        records.append((0x31, sntp["server2"]["value"].encode('ascii') + b'\x00'))
                if sntp.get("server3", {}).get("value"):
                    try:
                        ip = ipaddress.ip_address(sntp["server3"]["value"])
                        records.append((0x72, ip.packed))
                    except ValueError:
                        records.append((0x32, sntp["server3"]["value"].encode('ascii') + b'\x00'))

            # Add end of record list
            records.append((0x00, b''))

            # Convert records to bytes
            data = b''.join([bytes([key]) + value for key, value in records])
            max_card_size = 144
            num_cards = (len(data) + max_card_size - 1) // max_card_size

            # Write to multiple cards with record boundary awareness
            remaining_data = data
            for card in range(num_cards):
                input(f"Insert card {card + 1} and press Enter to continue...")
                chunk = b""
                if card == 0:
                    # First card, no Tag Flags unless more data
                    if num_cards > 1:
                        chunk += bytes([0x81, 0x01])  # More tags, clear data
                elif card < num_cards - 1:
                    chunk += bytes([0x81, 0x03])  # More tags, keep data
                else:
                    if num_cards > 1:
                        chunk += bytes([0x81, 0x02])  # Last card, keep data

                # Fill chunk with complete records
                while len(chunk) < max_card_size and remaining_data:
                    if not remaining_data:
                        break
                    key = remaining_data[0]
                    if key == 0x00:  # End of record list
                        chunk += remaining_data[:1]
                        remaining_data = remaining_data[1:]
                        break
                    value_len = 1  # Minimum for key
                    if key & 0xC0 == 0x00 and (key & 0x3F) != 0:  # String
                        value_len += remaining_data[1:].index(b'\x00') + 1 if b'\x00' in remaining_data[1:] else len(remaining_data[1:])
                    elif key & 0xC0 == 0x40:  # IPv4
                        value_len += 4
                    elif key & 0xC0 == 0x80:  # Byte
                        value_len += 1
                    if len(chunk) + value_len <= max_card_size:
                        chunk += remaining_data[:value_len]
                        remaining_data = remaining_data[value_len:]
                    else:
                        break

                # Pad and write
                while len(chunk) < max_card_size:
                    chunk += b'\x00'
                for i in range(0, max_card_size, 4):
                    page_data = chunk[i:i+4]
                    self.read_write_nfc(action="write", start_page=4 + (i // 4), data=page_data, key16=key16)

        except Exception as e:
            raise RuntimeError(f"Configuration write failed: {e}")
        finally:
            if self.connection:
                self.connection.disconnect()

    def read_config(self, key16=None):

        try:
            self.connect()
            config = {"wifi": {}, "mqtt": {}, "ip": {}, "sntp": {}}
            all_records = []

            while True:
                input("Insert a card and press Enter to continue...")
                data = self.read_write_nfc(action="read", start_page=4, end_page=39)
                
                # Parse records from this card
                i = 0

                while i < len(data):
                    
                    if i >= 144:
                        break

                    key = data[i]
                    i += 1

                    if key == 0x00:  # End of record list
                        all_records.append((0x00, b''))
                        break
                    if key == 0x81:  # Tag Flags
                        i += 1
                        continue

                    value = b""
                    if key & 0xC0 == 0x00 and (key & 0x3F) != 0:  # String
                        while i < len(data) and data[i] != 0x00:
                            value += bytes([data[i]])
                            i += 1
                        i += 1  # Skip NUL
                        value = value.decode('ascii', errors='ignore')
                    elif key & 0xC0 == 0x40:  # IPv4
                        if i + 3 < len(data):
                            value = bytes(data[i:i+4])
                            i += 4
                            value = str(ipaddress.IPv4Address(value))
                        else:
                            break
                    elif key & 0xC0 == 0x80:  # Byte
                        if i < len(data):
                            value = data[i]
                            i += 1
                            value = int(value)
                        else:
                            break

                    all_records.append((key, value))

                # Check for more tags
                more_tags = False
                i = 0
                while i < len(data):
                    if i >= 144:
                        break
                    key = data[i]
                    i += 1
                    if key == 0x81:
                        flags = data[i]
                        i += 1
                        more_tags = (flags & 0x01) != 0  # Bit 0 indicates more tags
                        break
                    if key == 0x00:
                        break
                if not more_tags:
                    break

            # Combine all records into config with IP aggregation
            ip_values = {}
            has_ip_data = False
            for key, value in all_records:
                key_id = key & 0x3F
                if key_id == 0x02: config["wifi"]["ssid"] = value
                elif key_id == 0x03: config["wifi"]["enterpriseIdentity"] = value
                elif key_id == 0x04: config["wifi"]["enterpriseUsername"] = value
                elif key_id == 0x05: config["wifi"]["password"] = value
                elif key_id == 0x06: config["wifi"]["enterpriseMode"] = {0x00: "EAP-TLS", 0x01: "EAP-PEAP", 0x02: "EAP-TTLS", 0xFF: ""}.get(value, "")
                elif key_id == 0x10 or key_id == 0x50: config["mqtt"]["host"] = value
                elif key_id == 0x11: config["mqtt"]["username"] = value
                elif key_id == 0x12: config["mqtt"]["password"] = value
                elif key_id == 0x20: # Correct ID for IPv4 address is 0x20
                    ip_values["ipAddress"] = value
                    has_ip_data = True
                elif key_id == 0x21: # Correct ID for Netmask is 0x21
                    ip_values["netmask"] = str(value)
                    has_ip_data = True # Also set flag here
                elif key_id == 0x22: # Correct ID for Gateway is 0x22
                    ip_values["gateway"] = value
                    has_ip_data = True # Also set flag here
                elif key_id == 0x23: # Correct ID for DNS1 is 0x23
                    ip_values["dns1"] = value
                    has_ip_data = True # Also set flag here
                elif key_id == 0x24: # Correct ID for DNS2 is 0x24
                    ip_values["dns2"] = value
                    has_ip_data = True # Also set flag here
                elif key_id == 0x25: # Correct ID for DNS3 is 0x25
                    ip_values["dns3"] = value
                    has_ip_data = True # Also set flag here
                elif key_id == 0x30 or key_id == 0x70: config["sntp"]["server1"] = {"value": value}
                elif key_id == 0x31 or key_id == 0x71: config["sntp"]["server2"] = {"value": value}
                elif key_id == 0x32 or key_id == 0x72: config["sntp"]["server3"] = {"value": value}

            # Update config["ip"] if IP data exists
            if has_ip_data:
                config["ip"] = {"dhcpEnabled": False}
                config["ip"].update(ip_values)

            return config

        except Exception as e:
            raise RuntimeError(f"Configuration read failed: {e}")

        finally:
            if self.connection:
                self.connection.disconnect() 

if __name__ == "__main__":
    handler = NFCHandler()
    try:
        # Sample test data exceeding 144 bytes
        test_config = {
            "wifi": {
                "ssid": "VeryLongSSIDThatExceedsNormalLimits1234567890",
                "enterpriseIdentity": "user@longdomain.com1234567890",
                "enterpriseUsername": "user1234567890",
                "password": "VerySecurePassword1234567890abcde",
                "enterpriseMode": "EAP-TTLS"
            },
            "mqtt": {
                "host": "mqttserver.very.long.domain.name1234567890",
                "username": "mqttuser1234567890",
                "password": "mqttpass1234567890"
            },
            "ip": {
                "dhcpEnabled": False,
                "ipAddress": "192.168.1.100",
                "netmask": "24",
                "gateway": "192.168.1.1",
                "dns1": "8.8.8.8",
                "dns2": "8.8.4.4",
                "dns3": "1.1.1.1"
            },
            "sntp": {
                "server1": {"value": "time1.very.long.domain.name123"},
                "server2": {"value": "time2.very.long.domain.name123"},
                "server3": {"value": "time3.very.long.domain.name123"}
            }
        }
        # handler.write_full_config(test_config)
        read_config = handler.read_config()
        print("Read configuration:", read_config)
    except Exception as e:
        print(f"Error: {e}")