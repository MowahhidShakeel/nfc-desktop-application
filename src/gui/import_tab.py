from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit,
    QFileDialog, QHBoxLayout, QGroupBox, QScrollArea
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PyQt6.QtCore import Qt


class ImportTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # === Scrollable container ===
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
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
        json_layout = QVBoxLayout(json_box)

        # Sub-heading with icon
        heading_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("src/gui/assets/json_icon.png").pixmap(16, 16))
        heading_layout.addWidget(icon_label)

        sub_heading = QLabel("JSON Configuration File")
        sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        heading_layout.addWidget(sub_heading)
        heading_layout.addStretch()
        json_layout.addLayout(heading_layout)

        # Grey description text
        description = QLabel("Select a previously exported configuration file to import settings.")
        description.setStyleSheet("color: #999999; font-size: 12px;")
        json_layout.addWidget(description)

        # Buttons
        import_button = QPushButton("Import && Continue")
        import_button.clicked.connect(self.parent.import_json)
        json_layout.addWidget(import_button)

        new_button = QPushButton("Start New Configuration")
        new_button.clicked.connect(self.parent.new_configuration)
        json_layout.addWidget(new_button)

        main_layout.addWidget(json_box)

        # Configuration File Format Box
        format_box = QGroupBox()
        format_layout = QVBoxLayout(format_box)

        # Sub-heading
        format_heading_layout = QHBoxLayout()
        format_sub_heading = QLabel("Configuration File Format")
        format_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        format_heading_layout.addWidget(format_sub_heading)
        format_heading_layout.addStretch()
        format_layout.addLayout(format_heading_layout)

        # Grey description
        format_description = QLabel("Expected JSON structure for import files")
        format_description.setStyleSheet("color: #999999; font-size: 12px;")
        format_layout.addWidget(format_description)

        # Example code
        format_code = QTextEdit()
        format_code.setReadOnly(True)
        format_code.setPlainText(
            "{\n"
            "  \"wifi\": {\n"
            "    \"ssid\": \"NetworkName\",\n"
            "    \"password\": \"password123\",\n"
            "    \"enterpriseMode\": \"EAP-TTLS\",\n"
            "    \"securityMode\": \"Verify server certificate\",\n"
            "    \"enterpriseIdentity\": \"\",\n"
            "    \"enterpriseUsername\": \"\"\n"
            "  },\n"
            "  \"mqtt\": {\n"
            "    \"host\": \"mqtt.example.com\",\n"
            "    \"hostType\": \"hostname\",\n"
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
            "    \"server1\": { \"value\": \"0.pool.ntp.org\" },\n"
            "    \"server2\": { \"value\": \"1.pool.ntp.org\" },\n"
            "    \"server3\": { \"value\": \"2.pool.ntp.org\" }\n"
            "  }\n"
            "}"
        )
        format_code.setStyleSheet("background-color: #F0F0F0; font-family: monospace; font-size: 12px;")
        format_layout.addWidget(format_code)

        main_layout.addWidget(format_box)
        main_layout.addStretch(1)

        # Wrap with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].endswith('.json'):
            self.parent.import_json(files[0])
        else:
            self.parent.log("Invalid file dropped. Please drop a JSON file.", level="ERROR")
