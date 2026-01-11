# Elixion Niviu Network Configuration Tool

This project is a Python-based desktop application for configuring and writing network settings (WiFi, MQTT, IP, SNTP) to **MIFARE Ultralight C** NFC tags using the **ACR1252U/ACR1255U USB NFC Reader III** on Windows. It features a PyQt6 GUI with tabbed configuration interfaces, multi-tag support for larger configurations, data validation, and logging. The application reads/writes data in a custom binary format optimized for the tag's **144-byte user memory**, with support for chaining multiple tags when needed.

The data encoding follows a size-optimized binary record format where each record starts with a **key byte** (type + ID bits) followed by variable-length data. Records are padded with `0x00`, and **tag flags (0x81)** indicate multi-tag chaining.

---

## Version History

| Version | Date            | Description |
|---------|-----------------|-------------|
| 0.1     | 2025-08-04      | Initial prototype: Basic PyQt6 GUI (ENNC-13, ENNC-19), pyscard integration for NFC read/write on MIFARE Classic 1K (ENNC-15, ENNC-12), logging setup (ENNC-17). Temporary tag support; reader connection via ACR1252U (ENNC-2). Focus: Core NFC handler and debug output. |
| 0.2     | 2025-08-08      | GUI expansion: Tabs for Import (JSON, ENNC-9/ENNC-10), WiFi, MQTT, IP, SNTP, Summary (ENNC-13). Dynamic controls (e.g., DHCP toggle, ENNC-11). Alignment: Tag specification compliance and reader support. |
| 0.3     | 2025-08-15      | Input validation basics (ENNC-11, ENNC-16, ENNC-18). Window resizing (ENNC-21). Alignment: User interface per requirements, with input highlighting. |
| 0.4     | 2025-08-25    | Application setup and installer development. Added support for MIFARE Ultralight C |
| 0.5     | 2025-09-09      | Multi-tag support: Chunking for >144 bytes, flags (0x81) for chaining (ENNC-12). Write/read handlers with progressive prompts (ENNC-13). GUI updates for tabs (ENNC-14). Alignment: Full operating sequence for multi-card operations. |
| 0.5.1   | 2025-09-23      | Bug fixes: Improved error handling in NFC operations, fixed IP/netmask validation, ensured padding and end-of-records (`0x00`) in serialization. |
| 0.5.2   | 2025-09-30      | Logging enhancements: Moved logs to `%APPDATA%` for non-admin access. Added debug levels and UTF-8 encoding. GUI asset path fixes for PyInstaller bundling. |
| 0.5.3   | 2025-11-17  | Final Release: Screen-aware resizing, theme stylesheet, close event disconnect. Updated documentation, troubleshooting, and sources. Project testing and completion with full multi-tag read/write support per **20250724_NFC-Tag-Specfication.pdf**. |
| 0.5.4   | 2025-12-22  | Default password value set in the memory for empty string. "Identity" parameter is now compulsory in WPA2 Enterprise Mode in the Wi-Fi section. |
---

## Features

- **Tabbed PyQt6 GUI** for configuring network settings:
  - **Import/Export JSON**
  - **WiFi** (SSID, password, enterprise modes)
  - **MQTT** (host, credentials)
  - **IP** (DHCP/static with address/netmask/gateway/DNS)
  - **SNTP** (up to 3 servers)
- **NFC read/write** using `pyscard`:
  - Supports **MIFARE Ultralight C** tags (pages 4–39, 144 bytes user data)
  - Unified handling for **ACR122U** and **ACR1252U** readers
- **Multi-tag support**: Automatically chunks large configs across tags with flags (`more_tags`, `keep_data`). Progressive GUI prompts for inserting next tag during write/read.
- **Data validation**: Schema checks, length limits (e.g., SSID ≤32 chars), type enforcement (e.g., IPv4 addresses).
- **Binary encoding/decoding**: Custom record format (key byte + data) for:
  - Strings (NUL-terminated)
  - IPv4 (4 bytes)
  - Bytes (1 byte)
  - Padded with `0x00`
- **Logging**: Debug/info/error to GUI and file (`%APPDATA%\ElixionNiviu\logs\nfc_app.log`) with rotation (1MB, 3 backups).
- **Error handling**: Reader detection, connection issues, invalid configs, tag authentication (factory defaults assumed).
- **Resource bundling**: Icons and assets via `resource_path` for PyInstaller compatibility.

---

## Requirements

### Hardware
- **ACR1252U USB NFC Reader III** (USB-A or USB-C variant)
- **MIFARE Ultralight C** tag (physical or emulated; factory default with 144 readable/writable user bytes)

### Software
- **Windows 10 or 11** (executable in VM on macOS via Parallels)
- **Python 3.8+** (for development)
- **ACS Unified Driver** for ACR1252U (download from [acs.com.hk](https://www.acs.com.hk), also included in setup installer)

### Dependencies (`docs/requirements.txt`)
- PyQt6==6.9.1
- pyscard==2.2.2
- pytest==7.4.0
- pycryptodome==3.23.0


Install the ACS Unified Driver from [acs.com.hk](https://www.acs.com.hk). Verify the reader in Device Manager and start the Smart Card service.

Packaged installer: Run `elixion-niviu-setup.exe` to install with prerequisites.

---

## Usage

Run the application:
python src/main.py


Or use the installed executable.

- **Import Tab**: Load JSON config
- **WiFi Tab**: Enter SSID, security, password, enterprise details
- **MQTT Tab**: Host, username, password
- **IP Tab**: Toggle DHCP; enter static details if disabled
- **SNTP Tab**: Up to 3 servers
- **Summary Tab**: Review settings
- **Write Tags Tab**: Write config to tag(s); follow prompts for multi-tag
- **Read Tags Tab**: Read and display config from tag(s)
- Export JSON from any tab
- Logs in GUI and `%APPDATA%\ElixionNiviu\logs\nfc_app.log`

NFC: Place tag 1–5 cm from reader. Use factory-default tags.

---

## NFC Tag Specification (Summary)

### Hardware
MIFARE Ultralight C, as physical tag or emulated

### Memory Map
The tag has 48 pages. Each page has 4 bytes. Pages 0 and 1 contain the serial number. Page 2 contains the last byte of the serial number, internal data, and two lock bytes. Page 3 contains one-time programmable data. Pages 4 to 39 contain user data, in total 144 bytes. Page 40 contains more lock bytes. Page 41 contains a counter. Pages 42 and 43 contain authentication configuration. Pages 44 to 47 contain the authentication key.

### Data Protection
Tags are left at their factory default value, with all 144 user data bytes readable and writable.

### Data Encoding
Data is stored in the user data pages, as a list of records, padded by `0x00` bytes.

### Record Format
Due to the very limited amount of memory on the tag, records are stored in a size-optimized binary format. Each record starts with a key byte, followed by binary data. The key byte is composed of type bits identifying the type of the binary data, and ID bits identifying the information in the binary data.

The ID portion of the key byte must be unique, even if the type bits change.

The binary can contain different data types, they are encoded by the most significant bits in the key byte:

| Bit 7 | Bit 6 | Values       | Data Format                          | Data Size, in bytes |
|-------|-------|--------------|--------------------------------------|---------------------|
| 0     | 0     | `0x00`       | If all other Bits are 0, final record. No data. | 0 |
| 0     | 0     | `0x01` to `0x3F` | If at least one other Bit is 1, a NUL-terminated string, as in C. | At least 1, for the trailing NUL byte |
| 0     | 1     | `0x40` to `0x7F` | Binary IPv4 address, first byte of dotted decimal notation first. | 4 |
| 1     | 0     | `0x80` to `0xBF` | A single byte, used for booleans (0 = false, 1 = true), for flag bits, and for small numbers. | 1 |
| 1     | 1     | `0xC0` to `0xFF` | Reserved for future use — will be defined later. | — |

---

## Key References

| Document | Link |
|--------|------|
| **MIFARE Ultralight C Datasheet** | [nxp.com/docs/en/data-sheet/MF0ICU2.pdf](https://www.nxp.com/docs/en/data-sheet/MF0ICU2.pdf) |
| **ACR1252U API Reference** | [acs.com.hk/en/download-manual/317/RD_ACR1252U-API.pdf](https://www.acs.com.hk/en/download-manual/317/RD_ACR1252U-API.pdf) |
| **Python Logging** | [docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html) |
| **PyQt6 Documentation** | [riverbankcomputing.com/static/Docs/PyQt6/](https://www.riverbankcomputing.com/static/Docs/PyQt6/) |
| **pyscard Documentation** | [pyscard.sourceforge.io](https://pyscard.sourceforge.io/) |

---

## Troubleshooting

| Issue | Solution |
|------|----------|
| **Reader not detected** | Check driver, USB, Smart Card service |
| **Write/Read failed** | Use factory-default Ultralight C tag, 1–5 cm distance, pages 4–39 writable |
| **Invalid config** | Check lengths/types in GUI (e.g., SSID ≤32), required fields |
| **Multi-tag issues** | Re-insert tags as prompted; verify `0x81` flags |
| **Permission errors** | Logs now in `%APPDATA%` — no admin needed |
| **GUI assets missing** | `resource_path` ensures PyInstaller compatibility |
| **Module errors** | Run in activated venv |

---
