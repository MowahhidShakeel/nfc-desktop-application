import ipaddress

class MultiCardWriteHandler:
    def __init__(self, nfc_writer, config):
        """
        Initializes the handler but does not start the writing process yet.
        """
        self.nfc_writer = nfc_writer
        self.config = config
        self.all_data = b''
        self.num_cards = 0
        self.current_card = 0
        
        # This prepares the data ahead of time, before any cards are written.
        self._prepare_data()

    def _prepare_data(self):
        """Prepares the entire byte stream from the config dictionary."""
        records = []
        
        # WiFi records
        if self.config.get("wifi"):
            wifi = self.config["wifi"]
            if wifi.get("ssid"): records.append((0x02, wifi["ssid"].encode('ascii') + b'\x00'))
            if wifi.get("enterpriseIdentity"): records.append((0x03, wifi["enterpriseIdentity"].encode('ascii') + b'\x00'))
            if wifi.get("enterpriseUsername"): records.append((0x04, wifi["enterpriseUsername"].encode('ascii') + b'\x00'))
            
            # FIX: Use .get() to prevent KeyError if password key is entirely missing
            records.append((0x05, wifi.get("password", "").encode('ascii') + b'\x00')) 
            
            # FIX: Use 'in' to ensure empty strings are processed instead of evaluating to False
            if "enterpriseMode" in wifi:
                mode_map = {"": 0xFF, "EAP-TLS": 0x00, "EAP-PEAP": 0x01, "EAP-TTLS": 0x02}
                mode = mode_map.get(wifi["enterpriseMode"], 0xFF)
                records.append((0x86, bytes([mode])))
            if "securityMode" in wifi:
                sec_map = {
                    "": 0x00,
                    "Don't use certificates": 0x00,
                    "Send client certificate": 0x01,
                    "Verify server certificate": 0x02,
                    "Send client certificate + verify server certificate": 0x03,
                }
                sec = sec_map.get(wifi["securityMode"], 0x00)
                records.append((0x87, bytes([sec])))
        
        # MQTT records
        if self.config.get("mqtt"):
            mqtt = self.config["mqtt"]
            if mqtt.get("host"):
                records.append((0x10, mqtt["host"].encode('ascii') + b'\x00'))
            if mqtt.get("username"):
                records.append((0x11, mqtt["username"].encode('ascii') + b'\x00'))
            if mqtt.get("password"):
                records.append((0x12, mqtt["password"].encode('ascii') + b'\x00'))

        # IP records
        if self.config.get("ip"):
            ip_config = self.config["ip"]
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
        if self.config.get("sntp"):
            sntp = self.config["sntp"]
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

        records.append((0x00, b'')) # Add end of record list

        self.all_data = b''.join([bytes([key]) + value for key, value in records])
        max_card_size = 144
        self.num_cards = (len(self.all_data) + max_card_size - 1) // max_card_size
        self.remaining_data = self.all_data

    def process_next_card(self):
        """
        Processes and writes the data for the next card in the sequence.
        Called by the GUI's 'Proceed' button.
        """
        if self.current_card >= self.num_cards:
            return {"status": "finished", "message": "All data written successfully!"}

        self.current_card += 1
        card_index = self.current_card - 1
        max_card_size = 144
        chunk = b""
        
        # Chunking logic, determine Tag Flags
        if card_index == 0:
            if self.num_cards > 1: chunk += bytes([0x81, 0x01]) # More tags, clear data
        elif card_index < self.num_cards - 1:
            chunk += bytes([0x81, 0x03]) # More tags, keep data
        else:
            if self.num_cards > 1: chunk += bytes([0x81, 0x02]) # Last card, keep data

        # Fill chunk with complete records
        while len(chunk) < max_card_size and self.remaining_data:
            if not self.remaining_data:
                break
            key = self.remaining_data[0]
            if key == 0x00:
                value_len = 1
            elif (key & 0xC0) == 0x00: # String
                value_len = self.remaining_data.find(b'\x00') + 1 if b'\x00' in self.remaining_data else len(self.remaining_data)
            elif (key & 0xC0) == 0x40: # IPv4
                value_len = 5
            elif (key & 0xC0) == 0x80: # Byte
                value_len = 2
            
            if len(chunk) + value_len <= max_card_size:
                 record_data = self.remaining_data[:value_len]
                 chunk += record_data
                 self.remaining_data = self.remaining_data[value_len:]
            else:
                 break
        
        # Pad and write
        chunk = chunk.ljust(max_card_size, b'\x00')
        
        try:
            # Call the actual NFC writing method
            self.nfc_writer.connect()
            for i in range(0, max_card_size, 4):
                page_data = chunk[i:i+4]
                self.nfc_writer.read_write_nfc(action="write", start_page=4 + (i // 4), data=page_data)
        except Exception as e:
            return {"status": "error", "message": f"Error writing card {self.current_card}: {e}"}
        finally:
            self.nfc_writer.disconnect()

        # Return status to the GUI
        if self.current_card >= self.num_cards:
             return {"status": "finished", "message": "All data written successfully!"}
        else:
            return {
                "status": "in_progress",
                "message": f"Card {self.current_card} of {self.num_cards} written. Please insert card {self.current_card + 1}."
            }