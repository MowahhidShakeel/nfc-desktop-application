import ipaddress

class MultiCardWriteHandler:
    def __init__(self, nfc_writer, config):
        """
        Initialize the NFC multi-card write handler.

        Args:
            nfc_writer: An object that exposes 'read_write_nfc' for NFC operations.
            config (dict): Configuration dictionary with wifi, mqtt, ip, and sntp data.
        """
        self.nfc_writer = nfc_writer
        self.config = config
        self.tags_data = []
        self.num_cards = 0
        self.current_card = 0

        self._prepare_data()

    def _records_to_bytes(self, records):
        """
        Convert (key, value) records into raw bytes.

        Args:
            records (list[tuple[int, bytes]]): Key-value record list.

        Returns:
            bytes: Concatenated byte stream of all records.
        """
        out = b""
        for key, value in records:
            out += bytes([key]) + value
        return out

    def _map_enterprise_mode(self, val):
        """
        Map enterprise mode string or int to a single byte.

        Args:
            val (str|int|None): Enterprise mode value.

        Returns:
            int: Encoded enterprise mode byte.
        """
        mode_map = {
            "EAP-TLS": 0x00,
            "EAP-PEAP": 0x01,
            "EAP-TTLS": 0x02,
            "": 0xFF,
            None: 0xFF,
        }
        if isinstance(val, int):
            return val
        return mode_map.get(val, 0xFF)

    def _build_records_single(self):
        """
        Build records for the single-card case:
        WiFi → MQTT → IP → SNTP.

        Returns:
            list: Records for the single-card payload.
        """
        records = []

        wifi = self.config.get("wifi", {})
        if wifi.get("ssid"):
            records.append((0x02, wifi["ssid"].encode("ascii") + b"\x00"))
        if wifi.get("enterpriseIdentity"):
            records.append((0x03, wifi["enterpriseIdentity"].encode("ascii") + b"\x00"))
        if wifi.get("enterpriseUsername"):
            records.append((0x04, wifi["enterpriseUsername"].encode("ascii") + b"\x00"))
        if wifi.get("password"):
            records.append((0x05, wifi["password"].encode("ascii") + b"\x00"))
        if wifi.get("enterpriseMode") is not None:
            mode = self._map_enterprise_mode(wifi["enterpriseMode"])
            records.append((0x86, bytes([mode])))

        mqtt = self.config.get("mqtt", {})
        if mqtt.get("host"):
            records.append((0x10, mqtt["host"].encode("ascii") + b"\x00"))
        if mqtt.get("username"):
            records.append((0x11, mqtt["username"].encode("ascii") + b"\x00"))
        if mqtt.get("password"):
            records.append((0x12, mqtt["password"].encode("ascii") + b"\x00"))

        ip_config = self.config.get("ip", {})
        if ip_config.get("dhcpEnabled", True):
            records.append((0x80, b"\x01"))
        if ip_config.get("ipAddress"):
            records.append((0x60, ipaddress.ip_address(ip_config["ipAddress"]).packed))
        if ip_config.get("netmask"):
            records.append((0xA1, bytes([int(ip_config["netmask"])])))
        if ip_config.get("gateway"):
            records.append((0x62, ipaddress.ip_address(ip_config["gateway"]).packed))
        if ip_config.get("dns1"):
            records.append((0x63, ipaddress.ip_address(ip_config["dns1"]).packed))
        if ip_config.get("dns2"):
            records.append((0x64, ipaddress.ip_address(ip_config["dns2"]).packed))
        if ip_config.get("dns3"):
            records.append((0x65, ipaddress.ip_address(ip_config["dns3"]).packed))

        sntp = self.config.get("sntp", {})
        for idx, key_id in enumerate([0x30, 0x31, 0x32], start=1):
            server = sntp.get(f"server{idx}", {}).get("value")
            if server:
                try:
                    ip = ipaddress.ip_address(server)
                    records.append((0x70 + (idx - 1), ip.packed))
                except ValueError:
                    records.append((key_id, server.encode("ascii") + b"\x00"))

        return records

    def _build_records_multi(self):
        """
        Build records for the multi-card case:
        Tag 1: Device-specific → Tag 2: Common network → Tag 3: SNTP.

        Returns:
            tuple: (device_records, common_records, global_records)
        """
        device_records, common_records, global_records = [], [], []

        wifi = self.config.get("wifi", {})
        if wifi.get("enterpriseIdentity"):
            device_records.append((0x03, wifi["enterpriseIdentity"].encode("ascii") + b"\x00"))
        if wifi.get("enterpriseUsername"):
            device_records.append((0x04, wifi["enterpriseUsername"].encode("ascii") + b"\x00"))
        if wifi.get("password"):
            device_records.append((0x05, wifi["password"].encode("ascii") + b"\x00"))
        if wifi.get("ssid"):
            common_records.append((0x02, wifi["ssid"].encode("ascii") + b"\x00"))
        if wifi.get("enterpriseMode") is not None:
            mode = self._map_enterprise_mode(wifi["enterpriseMode"])
            common_records.append((0x86, bytes([mode])))

        mqtt = self.config.get("mqtt", {})
        if mqtt.get("host"):
            common_records.append((0x10, mqtt["host"].encode("ascii") + b"\x00"))
        if mqtt.get("username"):
            common_records.append((0x11, mqtt["username"].encode("ascii") + b"\x00"))
        if mqtt.get("password"):
            common_records.append((0x12, mqtt["password"].encode("ascii") + b"\x00"))

        ip_config = self.config.get("ip", {})
        if ip_config.get("ipAddress"):
            device_records.append((0x60, ipaddress.ip_address(ip_config["ipAddress"]).packed))
        if ip_config.get("netmask"):
            common_records.append((0xA1, bytes([int(ip_config["netmask"])])))
        if ip_config.get("gateway"):
            common_records.append((0x62, ipaddress.ip_address(ip_config["gateway"]).packed))
        if ip_config.get("dns1"):
            common_records.append((0x63, ipaddress.ip_address(ip_config["dns1"]).packed))
        if ip_config.get("dns2"):
            common_records.append((0x64, ipaddress.ip_address(ip_config["dns2"]).packed))
        if ip_config.get("dns3"):
            common_records.append((0x65, ipaddress.ip_address(ip_config["dns3"]).packed))

        sntp = self.config.get("sntp", {})
        for idx, key_id in enumerate([0x30, 0x31, 0x32], start=1):
            server = sntp.get(f"server{idx}", {}).get("value")
            if server:
                try:
                    ip = ipaddress.ip_address(server)
                    global_records.append((0x70 + (idx - 1), ip.packed))
                except ValueError:
                    global_records.append((key_id, server.encode("ascii") + b"\x00"))

        common_records = sorted(common_records, key=lambda r: r[0])
        return device_records, common_records, global_records

    def _prepare_data(self):
        """
        Build final tag payloads.
        Single-card: JSON order, no flags.
        Multi-card: Split into device, common, global with flags.
        """
        single_records = self._build_records_single()
        single_payload = self._records_to_bytes(single_records) + b"\x00"

        if len(single_payload) <= 144:
            tag_bytes = single_payload.ljust(144, b"\x00")
            self.tags_data = [tag_bytes]
        else:
            device, common, global_r = self._build_records_multi()
            groups = [device, common, global_r]
            tag_list = []

            for idx, group in enumerate(groups):
                if idx == 0:
                    tag_bytes = bytes([0x81, 0x01])
                elif idx == len(groups) - 1:
                    tag_bytes = bytes([0x81, 0x02])
                else:
                    tag_bytes = bytes([0x81, 0x03])

                tag_bytes += self._records_to_bytes(group)
                tag_bytes += b"\x00"
                tag_bytes = tag_bytes.ljust(144, b"\x00")
                tag_list.append(tag_bytes)

            self.tags_data = tag_list

        self.num_cards = len(self.tags_data)

    def process_next_card(self):
        """
        Write data to the next NFC card.

        Returns:
            dict: Status and message for UI handling.
        """
        if self.current_card >= self.num_cards:
            return {"status": "finished", "message": "All data written successfully!"}

        tag_data = self.tags_data[self.current_card]
        self.current_card += 1

        try:
            self.nfc_writer.connect()
            for i in range(0, 144, 4):
                page_data = tag_data[i:i+4]
                self.nfc_writer.read_write_nfc(
                    action="write", start_page=4 + (i // 4), data=page_data
                )
        except Exception as e:
            return {"status": "error", "message": f"Error writing card {self.current_card}: {e}"}
        finally:
            self.nfc_writer.disconnect()

        if self.current_card >= self.num_cards:
            return {"status": "finished", "message": "All data written successfully!"}
        else:
            return {
                "status": "in_progress",
                "message": f"Card {self.current_card} of {self.num_cards} written. "
                           f"Please insert card {self.current_card + 1}."
            }
