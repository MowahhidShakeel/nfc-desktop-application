from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

class SummaryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Title 
        title_label = QLabel("Configuration Summary")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Review your network configuration before writing to NFC tags.")
        subtitle_label.setStyleSheet("color: grey;")
        main_layout.addWidget(subtitle_label)

        # Grid layout for 2x2 blocks
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(10)

        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        # 1.1 WiFi Settings Box
        wifi_box = QGroupBox()
        wifi_layout = QVBoxLayout()
        wifi_box.setLayout(wifi_layout)

        wifi_heading_layout = QHBoxLayout()
        wifi_icon = QLabel()
        wifi_icon.setPixmap(QIcon("src/gui/assets/wifi_icon.png").pixmap(16, 16))
        wifi_heading_layout.addWidget(wifi_icon)
        wifi_sub_heading = QLabel("WiFi Settings")
        wifi_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        wifi_heading_layout.addWidget(wifi_sub_heading)
        wifi_heading_layout.addStretch()
        wifi_layout.addLayout(wifi_heading_layout)

        wifi_desc = QLabel("Contains info about SSID, Security, Password")
        wifi_desc.setStyleSheet("color: #999999; font-size: 12px;")
        wifi_layout.addWidget(wifi_desc)

        self.wifi_ssid = QLabel("SSID: Not set")
        self.wifi_security = QLabel("Security: Not set")
        self.wifi_password = QLabel("Password: Not set")
        self.wifi_authentication = QLabel("Authentication Mode: Not set")
        self.wifi_identity = QLabel("Identity: Not set")
        self.wifi_username = QLabel("Username: Not set")
        wifi_layout.addWidget(self.wifi_ssid)
        wifi_layout.addWidget(self.wifi_security)
        wifi_layout.addWidget(self.wifi_password)
        wifi_layout.addWidget(self.wifi_authentication)
        wifi_layout.addWidget(self.wifi_identity)
        wifi_layout.addWidget(self.wifi_username)
        
        wifi_layout.addStretch(1) 
        left_column.addWidget(wifi_box)

        # 1.2 MQTT Settings Box
        mqtt_box = QGroupBox()
        mqtt_layout = QVBoxLayout()
        mqtt_box.setLayout(mqtt_layout)

        mqtt_heading_layout = QHBoxLayout()
        mqtt_icon = QLabel()
        mqtt_icon.setPixmap(QIcon("src/gui/assets/broker_icon.png").pixmap(16, 16))
        mqtt_heading_layout.addWidget(mqtt_icon)
        mqtt_sub_heading = QLabel("MQTT Settings")
        mqtt_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        mqtt_heading_layout.addWidget(mqtt_sub_heading)
        mqtt_heading_layout.addStretch()
        mqtt_layout.addLayout(mqtt_heading_layout)

        mqtt_desc = QLabel("Host, Username, Password")
        mqtt_desc.setStyleSheet("color: #999999; font-size: 12px;")
        mqtt_layout.addWidget(mqtt_desc)

        self.mqtt_host = QLabel("Host: Not set")
        self.mqtt_username = QLabel("Username: Not set")
        self.mqtt_password = QLabel("Password: Not set")
        mqtt_layout.addWidget(self.mqtt_host)
        mqtt_layout.addWidget(self.mqtt_username)
        mqtt_layout.addWidget(self.mqtt_password)
        mqtt_layout.addStretch(1)

        left_column.addWidget(mqtt_box)

        grid_layout.addLayout(left_column)

        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(10)

        # 2.1 IP Settings Box
        ip_box = QGroupBox()
        ip_layout = QVBoxLayout()
        ip_box.setLayout(ip_layout)

        ip_heading_layout = QHBoxLayout()
        ip_icon = QLabel()
        ip_icon.setPixmap(QIcon("src/gui/assets/ip_icon.png").pixmap(16, 16))  # Replace with actual icon path
        ip_heading_layout.addWidget(ip_icon)
        ip_sub_heading = QLabel("IP Settings")
        ip_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        ip_heading_layout.addWidget(ip_sub_heading)
        ip_heading_layout.addStretch()
        
        ip_layout.addLayout(ip_heading_layout)

        ip_desc = QLabel("DHCP, IP Address, Netmask/CIDR, Gateway, Primary DNS")
        ip_desc.setStyleSheet("color: #999999; font-size: 12px;")
        ip_layout.addWidget(ip_desc)

        self.ip_dhcp = QLabel("DHCP: Not set")
        self.ip_address = QLabel("IP Address: Not set")
        self.ip_netmask = QLabel("Netmask/CIDR: Not set")
        self.ip_gateway = QLabel("Gateway: Not set")
        self.ip_dns = QLabel("Primary DNS: Not set")
        ip_layout.addWidget(self.ip_dhcp)
        ip_layout.addWidget(self.ip_address)
        ip_layout.addWidget(self.ip_netmask)
        ip_layout.addWidget(self.ip_gateway)
        ip_layout.addWidget(self.ip_dns)

        ip_layout.addStretch(1)
        right_column.addWidget(ip_box)

        # 2.2 SNTP Settings Box
        sntp_box = QGroupBox()
        sntp_layout = QVBoxLayout()
        sntp_box.setLayout(sntp_layout)

        sntp_heading_layout = QHBoxLayout()
        sntp_icon = QLabel()
        sntp_icon.setPixmap(QIcon("src/gui/assets/time_icon.png").pixmap(16, 16)) 
        sntp_heading_layout.addWidget(sntp_icon)
        sntp_sub_heading = QLabel("SNTP Settings")
        sntp_sub_heading.setStyleSheet("font-size: 16px; font-weight: bold; color: #000000;")
        sntp_heading_layout.addWidget(sntp_sub_heading)
        sntp_heading_layout.addStretch()
        sntp_layout.addLayout(sntp_heading_layout)

        sntp_desc = QLabel("Primary Server, Secondary Server, Tertiary Server")
        sntp_desc.setStyleSheet("color: #999999; font-size: 12px;")
        sntp_layout.addWidget(sntp_desc)

        self.sntp_server1 = QLabel("Primary Server: Not set")
        self.sntp_server2 = QLabel("Secondary Server: Not set")
        self.sntp_server3 = QLabel("Tertiary Server: Not set")
        sntp_layout.addWidget(self.sntp_server1)
        sntp_layout.addWidget(self.sntp_server2)
        sntp_layout.addWidget(self.sntp_server3)

        right_column.addWidget(sntp_box)

        grid_layout.addLayout(right_column)
        sntp_layout.addStretch(1) 

        main_layout.addLayout(grid_layout)

        # Export JSON
        self.json_group = self.create_group_box(
            "Configuration Settings",
            "Save your configuration as a JSON file for future use.",
            "src/gui/assets/broker_icon.png"
        )

        json_layout = self.json_group.layout()
        
        # Add Export as JSON button
        export_button = QPushButton("Export as JSON")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                padding: 4px 8px;  /* smaller padding for smaller size */
                border: 1px solid black;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: grey;
            }
        """)

        # Connect to export function (to be implemented by parent)
        export_button.clicked.connect(lambda: parent.export_json())
        json_layout.addWidget(export_button)
        
        main_layout.addWidget(self.json_group)

        # Navigation buttons
        button_layout = QHBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: 1px solid #CCCCCC;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(4))

        next_button = QPushButton("Next")
        next_button.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)

        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(6))

        button_layout.addWidget(prev_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(next_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addStretch(1) 
        main_layout.addLayout(button_layout)
 
        self.setLayout(main_layout)


        # === Helper UI Methods ===
    def create_group_box(self, title, subtitle, icon_path):
        group_box = QGroupBox()
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        header_layout = QHBoxLayout()
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setFixedSize(16, 16)

        header_label = QLabel(title)
        header_label.setStyleSheet("font-weight: bold; font-size: 15px; margin: 0;")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: grey; font-size: 12px; margin: 0;")
        layout.addWidget(subtitle_label)

        group_box.setLayout(layout)
        return group_box
