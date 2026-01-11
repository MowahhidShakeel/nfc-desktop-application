from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QMessageBox, QFrame, QProgressBar, QScrollArea
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer

from ..core.write_handler import MultiCardWriteHandler


class WriteTagsTab(QWidget):
    def __init__(self, parent, nfc_handler):
        super().__init__()
        self.parent = parent
        self.nfc_handler = nfc_handler
        self.write_handler = None

        # --- Scrollable container ---
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(10)

        # --- Title and NFC Reader Status ---
        title_label = QLabel("Write NFC Tags")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        subtitle_label = QLabel(
            "Connect your NFC reader and write the configuration to Mifare Ultralight tags."
        )
        subtitle_label.setStyleSheet("color: grey;")
        main_layout.addWidget(subtitle_label)

        self.reader_box = self._create_reader_status_box()
        main_layout.addWidget(self.reader_box)

        # --- Configuration Data Box ---
        self.config_box = self._create_config_data_box()
        main_layout.addWidget(self.config_box)

        # --- Writing Process Box (always visible, initially disabled) ---
        self.writing_box = self._create_writing_process_box()
        self.writing_box.setEnabled(False)
        main_layout.addWidget(self.writing_box)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        self.action_button = QPushButton("Start Writing")
        self.action_button.setStyleSheet("font-size: 14px; padding: 5px 15px;")
        self.action_button.clicked.connect(self.handle_write_action)

        self.write_another_button = QPushButton("Write Another Set")
        self.write_another_button.setStyleSheet("font-size: 14px; padding: 5px 15px;")
        self.write_another_button.clicked.connect(self.reset_for_new_write)
        self.write_another_button.setVisible(False)

        button_layout.addStretch()
        button_layout.addWidget(self.action_button)
        button_layout.addWidget(self.write_another_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        main_layout.addStretch(1)

        # --- Wrap in scroll area ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Initialize connection status
        self.update_connection_status()

        # --- Timer for live connection updates ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_connection_status)
        self.timer.start(1000)  # every 1 second

    # --- UI Creation Helper Methods ---
    def _create_reader_status_box(self):
        group_box = self._create_group_box_template(
            "NFC Reader Status",
            "Supported readers: ACR122U, ACR1252U-M1.",
            "src/gui/assets/nfc_icon.png",
        )
        layout = group_box.layout()
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Reader Connection"))
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet(
            "color: #ff6666; border: 1px solid #ff6666; "
            "border-radius: 10px; padding: 2px 8px;"
        )
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status)
        layout.addLayout(status_layout)

        self.reader_detected = QLabel("No reader detected")
        self.reader_detected.setStyleSheet("font-size: 12px; color: #999999;")
        layout.addWidget(self.reader_detected)
        layout.addStretch(1)
        return group_box

    def _create_config_data_box(self):
        group_box = self._create_group_box_template(
            "Configuration Data",
            "The network configuration to be written to the tags.",
            "src/gui/assets/config_icon.png",
        )
        layout = group_box.layout()
        self.config_details_label = QLabel("Configuration not loaded.")
        self.config_details_label.setStyleSheet("font-size: 12px; color: #999999;")
        layout.addWidget(self.config_details_label)

        # Layout to hold usage bars
        self.usage_bars_layout = QVBoxLayout()
        layout.addLayout(self.usage_bars_layout)
        layout.addStretch(1)
        return group_box

    def _create_writing_process_box(self):
        group_box = QGroupBox("Writing Tag")
        layout = QVBoxLayout(group_box)

        self.write_process_title = QLabel("Write Process - Tag 1")
        self.write_process_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.write_process_subtitle = QLabel("Writing configuration data to tag 1 of 1.")
        self.write_process_subtitle.setStyleSheet("color: grey;")

        self.write_progress_bar = QProgressBar()
        self.write_progress_bar.setRange(0, 100)
        self.write_progress_bar.setTextVisible(False)

        layout.addWidget(self.write_process_title)
        layout.addWidget(self.write_process_subtitle)
        layout.addWidget(self.write_progress_bar)

        # Checklist items
        self.checklist_labels = {
            "validate": self._create_checklist_item("Validate tag compatibility"),
            "encode": self._create_checklist_item("Encode configuration data"),
            "write": self._create_checklist_item("Write to NFC tag"),
            "verify": self._create_checklist_item("Verify written data"),
        }
        for label in self.checklist_labels.values():
            layout.addWidget(label)

        return group_box

    def _create_checklist_item(self, text):
        label = QLabel(f"⚪ {text}")
        label.setStyleSheet("font-size: 12px;")
        return label

    def _create_group_box_template(self, title, description, icon_path):
        group_box = QGroupBox()
        layout = QVBoxLayout(group_box)
        heading_layout = QHBoxLayout()

        icon = QLabel()
        icon.setPixmap(QIcon(icon_path).pixmap(16, 16))
        heading_layout.addWidget(icon)

        sub_heading = QLabel(title)
        sub_heading.setStyleSheet("font-size: 16px; font-weight: bold;")
        heading_layout.addWidget(sub_heading)
        heading_layout.addStretch()
        layout.addLayout(heading_layout)

        desc = QLabel(description)
        desc.setStyleSheet("color: #999999; font-size: 12px;")
        layout.addWidget(desc)
        return group_box

    # --- Core Logic ---
    def load_config_data(self):
        try:
            is_valid = self.parent.is_entire_config_valid()
            self.action_button.setEnabled(is_valid)
            self.action_button.setToolTip(
                "" if is_valid else
                "Button is disabled because some configuration fields are incomplete or invalid."
            )

            config = self.parent.get_config()
            temp_handler = MultiCardWriteHandler(self.nfc_handler, config)
            data_len = len(temp_handler.all_data)
            num_tags = temp_handler.num_cards

            self.config_details_label.setText(
                f"<b>Total Data Size:</b> {data_len} bytes | <b>Tags Required:</b> {num_tags}"
            )
            self._generate_usage_bars(temp_handler)

            self.parent.log(
                f"Loaded configuration: {data_len} bytes, requires {num_tags} tags.",
                level="INFO",
            )

        except Exception as e:
            self.config_details_label.setText(f"Error loading configuration: {e}")
            self.action_button.setEnabled(False)
            self.parent.log(f"Error loading configuration: {e}", level="ERROR")

    def _generate_usage_bars(self, handler):
        while self.usage_bars_layout.count():
            child = self.usage_bars_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if handler.num_cards == 0:
            return

        remaining_data = handler.all_data
        for i in range(handler.num_cards):
            space = 142 if handler.num_cards > 1 else 144
            chunk_len = min(len(remaining_data) + (2 if handler.num_cards > 1 else 0), space)
            remaining_data = remaining_data[max(0, space - 2):]

            bar_label = QLabel(f"Tag {i+1} Usage: {chunk_len} / 144 bytes")
            bar_container = QFrame()
            bar_container.setFixedHeight(10)
            bar_container.setStyleSheet("background-color: #e0e0e0; border-radius: 5px;")

            bar_fill = QFrame(bar_container)
            percentage = (chunk_len / 144) * 100
            bar_fill.setFixedHeight(10)
            bar_fill.setFixedWidth(int(144 * (percentage / 100)))
            bar_fill.setStyleSheet("background-color: #333333; border-radius: 5px;")

            self.usage_bars_layout.addWidget(bar_label)
            self.usage_bars_layout.addWidget(bar_container)

    def handle_write_action(self):
        if not self.write_handler:
            try:
                config = self.parent.get_config()
                print(config)
                self.write_handler = MultiCardWriteHandler(self.nfc_handler, config)
                self.writing_box.setEnabled(True)
                self.process_single_tag()
            except Exception as e:
                self.parent.log(f"Failed to start writing process: {e}", level="ERROR")
                QMessageBox.critical(self, "Error", str(e))
        else:
            if self.write_handler.current_card >= self.write_handler.num_cards:
                self.parent.switch_to_home_tab()
            else:
                self.parent.log("Proceeding to next NFC tag.", level="INFO")
                self.process_single_tag()

    def process_single_tag(self):
        if not self.write_handler:
            return

        current = self.write_handler.current_card + 1
        total = self.write_handler.num_cards

        self.write_process_title.setText(f"Write Process - Tag {current}")
        self.write_process_subtitle.setText(f"Writing configuration data to tag {current} of {total}.")
        self.action_button.setEnabled(False)

        self._update_checklist("validate", "done")
        self.write_progress_bar.setValue(25)
        self._update_checklist("encode", "done")
        self.write_progress_bar.setValue(50)

        result = self.write_handler.process_next_card()

        if result["status"] == "error":
            self._update_checklist("write", "error")
            self.parent.log(f"Write error on Tag {current}: {result['message']}", level="ERROR")
            QMessageBox.critical(self, "Write Error", result["message"])
            self.reset_for_new_write()
            return

        self.parent.log(f"Write successful for Tag {current}", level="INFO")
        self._update_checklist("write", "done")
        self.write_progress_bar.setValue(75)
        self._update_checklist("verify", "done")
        self.write_progress_bar.setValue(100)

        if result["status"] == "finished":
            self.parent.log("All NFC tags written successfully.", level="INFO")
            self.action_button.setText("Return to Home")
            self.write_another_button.setVisible(True)
        else:
            next_card = self.write_handler.current_card + 1
            self.action_button.setText(f"Write Tag {next_card}")

        self.action_button.setEnabled(True)

    def reset_for_new_write(self):
        self.parent.log("Resetting write process for new session.", level="INFO")
        self.write_handler = None
        self.writing_box.setEnabled(False)
        self.write_another_button.setVisible(False)
        self.action_button.setText("Start Writing")
        self.write_progress_bar.setValue(0)
        for step in self.checklist_labels:
            self._update_checklist(step, "pending")
        self.load_config_data()

    def _update_checklist(self, step, status):
        if step not in self.checklist_labels:
            return
        text = self.checklist_labels[step].text()[2:]
        if status == "pending":
            self.checklist_labels[step].setText(f"⚪ {text}")
        elif status == "done":
            self.checklist_labels[step].setText(f"✅ {text}")
        elif status == "error":
            self.checklist_labels[step].setText(f"❌ {text}")

    def update_connection_status(self):
        """Checks reader connection continuously via QTimer."""
        try:
            self.nfc_handler.connect()
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet(
                "color: #66cc66; border: 1px solid #66cc66; "
                "border-radius: 10px; padding: 2px 8px;"
            )
            self.reader_detected.setText(f"{str(self.nfc_handler.reader)} detected")
        except Exception:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet(
                "color: #ff6666; border: 1px solid #ff6666; "
                "border-radius: 10px; padding: 2px 8px;"
            )
            self.reader_detected.setText("No reader detected")

    def tab_shown(self):
        self.update_connection_status()
        self.load_config_data()