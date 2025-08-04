# NFC Desktop Application

This project is a Python-based desktop application for reading and writing data to NFC tags using the ACR1252U USB NFC Reader III on Windows. It features a simple PyQt6 GUI and a logging system for debugging. Version 1 (Milestone 1) supports MIFARE Classic 1K tags, with plans to switch to MIFARE Ultralight tags in future updates.

## Version History

| Version | Date       | Description |
|---------|------------|-------------|
| 0.1     | 2025-08-04 | Milestone 1 completed: PyQt6 GUI, pyscard for NFC communication, and logging system. Supports reading/writing 16-byte blocks to MIFARE Classic 1K tags (block 4, sector 1) using the ACR1252U reader. Key features: <br>- Connect to reader <br>- Write/read data to block 4 <br>- GUI with status and log display <br>- File-based logging with rotation <br>- Temporary MIFARE Classic 1K support (pending Ultralight tag) |

## Features
- Simple GUI with buttons to connect to the reader, write to block 4, and read from block 4 of a MIFARE Classic 1K tag
- NFC operations using pyscard to communicate with the ACR1252U, including authentication for MIFARE Classic 1K
- Logging to both GUI and a file (logs/nfc_app.log) with rotation for debugging
- Error handling for reader detection, Smart Card service issues, and authentication failures

## Requirements
Hardware:
- ACR1252U USB NFC Reader III (USB-A or USB-C)
- MIFARE Classic 1K tag (temporary; MIFARE Ultralight planned)

Software:
- Windows 10 or 11
- Python 3.8 or higher
- ACS Unified Driver for ACR1252U (available at acs.com.hk website)

Dependencies (listed in docs/requirements.txt):
- PyQt6 version 6.5.2 for the GUI
- pyscard version 2.0.7 for NFC communication
- pytest-qt version 4.2.0 for optional GUI testing

## Installation

1. Clone the repository:  
   ```bash
   git clone [repository-url]  
   cd nfc-desktop-application
   ```

2. Set up a virtual environment:  
   ```bash
   python -m venv venv    
   source venv/Scripts/activate
   ```

3. Install dependencies:  
   ```bash
   pip install -r docs/requirements.txt
   ```

4. Install the ACS Unified Driver:  
   - Download from acs.com.hk (driver section for ACR1252U)
   - Install and connect the ACR1252U via USB
   - Verify in Device Manager under Smart Card Readers as ACS ACR1252 0
   - Ensure the Smart Card service is running:
     sc query SCardSvr
     sc start SCardSvr

## Usage

1. Run the application:  
   ```bash
   source venv/Scripts/activate  
   python -m src.main
   ```

2. Using the GUI:
   - Click Connect to Reader to initialize the ACR1252U
   - Click Write to Block 4 to write 16 bytes (e.g., 1, 2, ..., 16) to block 4
   - Click Read from Block 4 to read 16 bytes from block 4
   - View logs in the GUI or check logs/nfc_app.log for details

3. Requirements:
   - Place a MIFARE Classic 1K tag within 1 to 5 cm of the reader
   - Ensure the tag uses default Key A (six bytes: FF FF FF FF FF FF)

## File Structure

- docs/requirements.txt: Lists project dependencies
- logs/nfc_app.log: Log file with rotation
- src/core/logging_config.py: Logging setup
- src/core/nfc_handler.py: NFC reader communication
- src/gui/nfc_gui.py: PyQt6 GUI
- src/main.py: Application entry point
- README.md: This documentation


## Troubleshooting
- Reader not detected: Verify ACS Unified Driver and Smart Card service (sc start SCardSvr)
- Authentication failed: Use a MIFARE Classic 1K tag with default keys or obtain a new tag
- Module import errors: Ensure correct sys.path in src/main.py and run with python -m src.main

## Sources
- MIFARE Classic 1K Datasheet: `nxp.com/docs/en/data-sheet/MF1S50YYX_V1.pdf`
- ACS ACR1252U API Reference: `acs.com.hk/en/download-manual/317/RD_ACR1252U-API.pdf`
- Python Logging Documentation: `docs.python.org/3/library/logging.html`
- PyQt6 Documentation: `riverbankcomputing.com/static/Docs/PyQt6/`
- pyscard Documentation: `pyscard.sourceforge.io/`