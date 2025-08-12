from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt

class ImportTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # Reference to NFCWindow for backend calls
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title
        title = QLabel("Import Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Import a network configuration from a JSON file or start with a new one.")
        layout.addWidget(subtitle)

        # Upload JSON section
        upload_label = QLabel("Upload JSON Configuration File")
        layout.addWidget(upload_label)

        # Drag and drop area
        self.drop_area = QLabel("Drag and drop your JSON")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("border: 2px dashed #CCCCCC; border-radius: 4px; padding: 20px; background-color: #F8F8F8;")
        self.drop_area.setAcceptDrops(True)
        layout.addWidget(self.drop_area)

        # Choose File button
        choose_button = QPushButton("Choose File")
        choose_button.clicked.connect(self.parent.import_json)
        layout.addWidget(choose_button)

        # Start New Configuration button
        new_button = QPushButton("Start New Configuration")
        new_button.clicked.connect(self.parent.new_configuration)
        layout.addWidget(new_button)

        # Configuration File Format code block
        format_label = QLabel("Configuration File Format")
        layout.addWidget(format_label)

        format_code = QTextEdit()
        format_code.setReadOnly(True)
        format_code.setPlainText(
            "{\n"
            "  \"wifi\": {\n"
            "    \"ssid\": \"NetworkName\",\n"
            "    \"password\": \"password123\",\n"
            "    \"enterpriseMode\": 255,\n"
            "    \"enterpriseIdentity\": \"\",\n"
            "    \"enterpriseUsername\": \"\"\n"
            "  },\n"
            "  \"mqtt\": {\n"
            "    \"host\": \"mqtt.example.com\",\n"
            "    \"hostType\": \"hostname\",\n"
            "    \"port\": 1883,\n"
            "    \"username\": \"mqttuser\",\n"
            "    \"password\": \"mqttpass\"\n"
            "  },\n"
            "  \"ip\": {\n"
            "    \"dhcpEnabled\": true,\n"
            "    \"ipAddress\": \"\",\n"
            "    \"netmask\": 24,\n"
            "    \"gateway\": \"\",\n"
            "    \"dns1\": \"\",\n"
            "    \"dns2\": \"\",\n"
            "    \"dns3\": \"\"\n"
            "  },\n"
            "  \"sntp\": {\n"
            "    \"server1\": { \"value\": \"0.pool.ntp.org\", \"type\": \"hostname\" },\n"
            "    \"server2\": { \"value\": \"1.pool.ntp.org\", \"type\": \"hostname\" },\n"
            "    \"server3\": { \"value\": \"2.pool.ntp.org\", \"type\": \"hostname\" }\n"
            "  }\n}"
        )
        format_code.setStyleSheet("background-color: #F0F0F0; font-family: monospace; font-size: 12px;")
        layout.addWidget(format_code)

        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].endswith('.json'):
            # Call parent import_json with the dropped file
            self.parent.import_json(files[0])
        else:
            self.parent.log("Invalid file dropped. Please drop a JSON file.", level="ERROR")