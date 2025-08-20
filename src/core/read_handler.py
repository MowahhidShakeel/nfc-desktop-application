import ipaddress

class MultiCardReadHandler:
    def __init__(self, nfc_handler):
        """Initializes the handler for a multi-card read operation."""
        self.nfc_handler = nfc_handler
        self.all_records = []
        self.is_finished = False

    def process_next_card(self):
        """
        Reads the next card and returns status. Should be called by the GUI's 'Proceed' button.
        """
        if self.is_finished:
            return {"status": "finished", "message": "Already finished reading."}

        try:
            # Read the entire user data from the card
            data = self.nfc_handler.read_write_nfc(action="read", start_page=4, end_page=39)
        except Exception as e:
            return {"status": "error", "message": f"Failed to read card: {e}"}

        # parsing logic 
        i = 0
        while i < len(data) and i < 144:
            key = data[i]
            i += 1
            if key == 0x00: # End of record list for this card
                self.all_records.append((0x00, b''))
                break
            if key == 0x81: # Tag Flags
                i += 1
                continue
            # ... (the rest of your value parsing logic for string, IPv4, byte) ...
            value = b""
            if (key & 0xC0) == 0x00 and (key & 0x3F) != 0:  # String
                while i < len(data) and data[i] != 0x00:
                    value += bytes([data[i]])
                    i += 1
                i += 1  # Skip NUL
                value = value.decode('ascii', errors='ignore')
            elif (key & 0xC0) == 0x40:  # IPv4
                if i + 3 < len(data):
                    value = bytes(data[i:i+4])
                    i += 4
                    value = str(ipaddress.IPv4Address(value))
                else:
                    break
            elif (key & 0xC0) == 0x80:  # Byte
                if i < len(data):
                    value = data[i]
                    i += 1
                    value = int(value)
                else:
                    break

            self.all_records.append((key, value))

        # Check for the 'more_tags' flag
        more_tags = False
        i = 0
        while i < len(data) and i < 144:
            key = data[i]
            if key == 0x81:
                flags = data[i+1]
                more_tags = (flags & 0x01) != 0
                break
            if key == 0x00:
                break
            i+=1

        if not more_tags:
            self.is_finished = True
            final_config = self._build_final_config()
            return {
                "status": "finished",
                "message": "Successfully read all cards!",
                "config": final_config
            }
        else:
            return {
                "status": "in_progress",
                "message": "Card read successfully. Please insert the next card."
            }

    def _build_final_config(self):
        """Builds the final config dictionary from all accumulated records."""
        config = {"wifi": {}, "mqtt": {}, "ip": {}, "sntp": {}}
        ip_values = {}
        has_ip_data = False
        
        # Mapping logic
        for key, value in self.all_records:
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