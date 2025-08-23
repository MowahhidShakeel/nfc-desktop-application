from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPixmap, QColor, QPainter
import re


# ==== Custom Smooth Toggle Switch ====
class ToggleSwitch(QWidget):
    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self._checked = checked
        self._offset = 1 if checked else 0
        self.setFixedSize(50, 25)

        self.animation = QPropertyAnimation(self, b"offset")
        self.animation.setDuration(200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_color = QColor(128, 128, 128) if not self._checked else QColor(0, 0, 0)
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 12.5, 12.5)

        # Handle
        handle_diameter = self.height() - 4
        x_pos = self._offset * (self.width() - handle_diameter - 4) + 2
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(QRectF(x_pos, 2, handle_diameter, handle_diameter))

    def mousePressEvent(self, event):
        self.setChecked(not self._checked, animate=True)
        self.parentWidget().parentWidget().toggle_dhcp()

    def getOffset(self):
        return self._offset

    def setOffset(self, value):
        self._offset = value
        self.update()

    offset = pyqtProperty(float, getOffset, setOffset)

    def isChecked(self):
        return self._checked

    def setChecked(self, state, animate=False):
        self._checked = state
        if animate:
            self.animation.stop()
            self.animation.setStartValue(self._offset)
            self.animation.setEndValue(1 if state else 0)
            self.animation.start()
        else:
            self._offset = 1 if state else 0
            self.update()


# ==== IP Tab ====
class IpTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # === Title ===
        title_label = QLabel("IP Configuration")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 0;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("Configure network IP settings including DHCP, static IP, and DNS servers.")
        subtitle_label.setStyleSheet("color: grey; margin: 0;")
        main_layout.addWidget(subtitle_label)

        # === IP Settings Group ===
        self.ip_group = self.create_group_box(
            "IP Settings",
            "Configure how the device obtains its IP address.",
            "src/gui/assets/ip_icon.png"
        )
        ip_layout = self.ip_group.layout()

        # DHCP Toggle (Custom Switch)
        toggle_row = QHBoxLayout()
        toggle_row.addWidget(QLabel("Enable DHCP"))
        toggle_row.addStretch()

        self.dhcp_toggle = ToggleSwitch(checked=True)
        toggle_row.addWidget(self.dhcp_toggle)

        ip_layout.addLayout(toggle_row)

        # Static IP Fields
        self.static_ip_label = QLabel("IPv4 Address *")
        self.static_ip = QLineEdit()
        self.static_ip.setPlaceholderText("e.g. 192.168.1.100")
        self.set_field_style(self.static_ip)

        self.netmask_label = QLabel("Netmask/CIDR")
        self.netmask = QLineEdit()
        self.netmask.setPlaceholderText("e.g. 24")
        self.set_field_style(self.netmask)

        ip_layout.addWidget(self.static_ip_label)
        ip_layout.addWidget(self.static_ip)
        ip_layout.addWidget(self.netmask_label)
        ip_layout.addWidget(self.netmask)

        self.static_ip_label.hide()
        self.static_ip.hide()
        self.netmask_label.hide()
        self.netmask.hide()

        main_layout.addWidget(self.ip_group)

        # === Gateway Settings Group ===
        self.gateway_group = self.create_group_box(
            "Gateway Settings",
            "Set the default gateway for the device.",
            "src/gui/assets/gateway_icon.png"
        )
        gateway_layout = self.gateway_group.layout()
        gateway_layout.addWidget(QLabel("Default Gateway"))
        self.gateway = QLineEdit()
        self.gateway.setPlaceholderText("e.g. 192.168.1.1")
        self.set_field_style(self.gateway)
        gateway_layout.addWidget(self.gateway)
        self.gateway_group.hide()
        main_layout.addWidget(self.gateway_group)

        # === DNS Servers Group ===
        self.dns_group = self.create_group_box(
            "DNS Servers",
            "Configure the DNS servers for domain name resolution.",
            "src/gui/assets/dns_icon.png"
        )
        dns_layout = self.dns_group.layout()

        dns_layout.addWidget(QLabel("Primary DNS Server"))
        self.dns1 = QLineEdit()
        self.dns1.setPlaceholderText("e.g. 8.8.8.8")
        self.set_field_style(self.dns1)
        dns_layout.addWidget(self.dns1)

        dns_layout.addWidget(QLabel("Secondary DNS Server"))
        self.dns2 = QLineEdit()
        self.dns2.setPlaceholderText("Optional")
        self.set_field_style(self.dns2)
        dns_layout.addWidget(self.dns2)

        dns_layout.addWidget(QLabel("Tertiary DNS Server"))
        self.dns3 = QLineEdit()
        self.dns3.setPlaceholderText("Optional")
        self.set_field_style(self.dns3)
        dns_layout.addWidget(self.dns3)

        self.dns_group.hide()
        main_layout.addWidget(self.dns_group)

        # === Navigation Buttons ===
        button_layout = QHBoxLayout()

        prev_button = QPushButton("Previous")
        prev_button.setStyleSheet(self.nav_button_style(light=True))
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(2))

        next_button = QPushButton("Next")
        next_button.setStyleSheet(self.nav_button_style(light=False))
        next_button.clicked.connect(self.next_clicked)

        button_layout.addWidget(prev_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addStretch()
        button_layout.addWidget(next_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Ensure layout matches toggle when changing tabs
        self.parent.tabs.currentChanged.connect(self.sync_dhcp_layout)

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

    def set_field_style(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #555555;
            }
        """)

    def nav_button_style(self, light=True):
        if light:
            return """
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
            """
        else:
            return """
                QPushButton {
                    background-color: black;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
            """

    def toggle_dhcp(self):
        enabled = self.dhcp_toggle.isChecked()
        self.static_ip_label.setVisible(not enabled)
        self.static_ip.setVisible(not enabled)
        self.netmask_label.setVisible(not enabled)
        self.netmask.setVisible(not enabled)
        self.gateway_group.setVisible(not enabled)
        self.dns_group.setVisible(not enabled)

    def sync_dhcp_layout(self, index):
        if self.parent.tabs.currentWidget() == self:
            self.toggle_dhcp()

    def is_valid(self):
        errors = []
        self.clear_error_styles()

        if not self.dhcp_toggle.isChecked():
            if not self.is_valid_ip(self.static_ip.text()):
                errors.append(("IPv4 Address *", self.static_ip))
            if not self.netmask.text().strip().isdigit() or not (0 <= int(self.netmask.text()) <= 32):
                errors.append(("Netmask/CIDR *", self.netmask))
            if not self.is_valid_ip(self.gateway.text()):
                errors.append(("Default Gateway *", self.gateway))
            if not self.is_valid_ip(self.dns1.text()):
                errors.append(("Primary DNS Server *", self.dns1))

            for dns_field in [self.dns2, self.dns3]:
                if dns_field.text().strip() and not self.is_valid_ip(dns_field.text()):
                    errors.append(("DNS Server", dns_field))

        if errors:
            for field_name, widget in errors:
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid red;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
                
                self.parent.log(f"IP Tab Validation Error: {field_name} is invalid or missing", level="ERROR")

            return False

        return True
    
    def next_clicked(self):
        """Check valid inputs and navigate to next tab if valid"""
        if (self.is_valid()):
            self.parent.tabs.setCurrentIndex(4)

    def clear_error_styles(self):
        for field in [self.static_ip, self.netmask, self.gateway, self.dns1, self.dns2, self.dns3]:
            self.set_field_style(field)

    def is_valid_ip(self, ip):
        pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
        if not re.match(pattern, ip.strip()):
            return False
        return all(0 <= int(octet) <= 255 for octet in ip.strip().split("."))
