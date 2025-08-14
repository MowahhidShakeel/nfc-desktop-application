from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog, QHBoxLayout, QGroupBox
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtCore import Qt

class ImportTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Title
        title = QLabel("Import Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Import a network configuration from a JSON file or start with a new one.")
        main_layout.addWidget(subtitle)

        # JSON Configuration File Box
        json_box = QGroupBox()
        json_layout = QVBoxLayout()
        json_box.setLayout(json_layout)

        # Sub-heading with icon
        heading_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("src/gui/assets/json_icon.png").pixmap(16, 16))  # Replace with actual icon path
        heading_layout.addWidget(icon_label)

        sub_heading = QLabel("JSON Configuration File")
        sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        heading_layout.addWidget(sub_heading)
        heading_layout.addStretch()
        json_layout.addLayout(heading_layout)

        # Faded/grey text below sub-heading
        description = QLabel("Select a previously exported configuration file to import settings.")
        description.setStyleSheet("color: #999999; font-size: 12px;")
        json_layout.addWidget(description)

        # Drag and drop area
        self.drop_area = QLabel("Drag and drop your JSON")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("border: 2px dashed #CCCCCC; border-radius: 4px; padding: 10px; background-color: #F8F8F8;")
        self.drop_area.setAcceptDrops(True)
        json_layout.addWidget(self.drop_area)

        # Import & Continue button
        import_button = QPushButton("Import && Continue")
        import_button.clicked.connect(self.parent.import_json)
        json_layout.addWidget(import_button)

        # Start New Configuration button
        new_button = QPushButton("Start New Configuration")
        new_button.clicked.connect(self.parent.new_configuration)
<<<<<<< HEAD
        json_layout.addWidget(new_button)

        main_layout.addWidget(json_box)

        # Configuration File Format Box
        format_box = QGroupBox()
        format_layout = QVBoxLayout()
        format_box.setLayout(format_layout)

        # Sub-heading with icon
        format_heading_layout = QHBoxLayout()
        format_sub_heading = QLabel("Configuration File Format")
        format_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        format_heading_layout.addWidget(format_sub_heading)
        format_heading_layout.addStretch()
        format_layout.addLayout(format_heading_layout)

        # Faded/grey text below sub-heading
        format_description = QLabel("Expected JSON structure for import files")
        format_description.setStyleSheet("color: #999999; font-size: 12px;")
        format_layout.addWidget(format_description)
=======
        new_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(1))  # Navigate to WiFi tab
        layout.addWidget(new_button)
>>>>>>> b2accabdeb47cf6901afea5642eb77ee27705df6

        format_label = QLabel("Configuration File Format")
        format_layout.addWidget(format_label)

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
        format_layout.addWidget(format_code)

        main_layout.addWidget(format_box)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file in files:
            if file.endswith('.json'):
                self.parent.import_json(file)
                return
        self.parent.log("Invalid file dropped. Please drop a JSON file.", level="ERROR")