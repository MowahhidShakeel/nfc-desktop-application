import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton, QMessageBox, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Make sure your handler classes are available for import
from ..core.read_handler import MultiCardReadHandler

class ReadTagsTab(QWidget):
    def __init__(self, parent, nfc_handler):
        super().__init__()
        self.parent = parent
        self.nfc_handler = nfc_handler
        self.read_handler = None  # To hold the instance of the read process manager

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # --- Title and NFC Reader Status (Largely Unchanged) ---
        title_label = QLabel("Read NFC Tags")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        subtitle_label = QLabel("Connect your NFC reader to read configuration from Mifare Ultralight tags.")
        subtitle_label.setStyleSheet("color: grey;")
        main_layout.addWidget(subtitle_label)
        
        self.reader_box = self._create_reader_status_box()
        main_layout.addWidget(self.reader_box)

        # --- NEW: Reading Process Box (Initially Hidden) ---
        self.reading_box = self._create_reading_process_box()
        self.reading_box.setVisible(False)
        main_layout.addWidget(self.reading_box)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        self.action_button = QPushButton("Start Reading")
        self.action_button.setStyleSheet("font-size: 14px; padding: 5px 15px;")
        self.action_button.clicked.connect(self.handle_read_action)

        self.read_another_button = QPushButton("Read Another Set")
        self.read_another_button.setStyleSheet("font-size: 14px; padding: 5px 15px;")
        self.read_another_button.clicked.connect(self.reset_for_new_read)
        self.read_another_button.setVisible(False)

        button_layout.addStretch()
        button_layout.addWidget(self.action_button)
        button_layout.addWidget(self.read_another_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        main_layout.addStretch(1)
        self.update_connection_status()

    # --- UI Creation Helper Methods ---
    def _create_reader_status_box(self):
        # This method is refactored from your original __init__
        group_box = self._create_group_box_template("NFC Reader Status", "Supported readers: ACR122U, ACR1252U-M1.", "src/gui/assets/nfc_icon.png")
        layout = group_box.layout()
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Reader Connection"))
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: #ff6666; border: 1px solid #ff6666; border-radius: 10px; padding: 2px 8px;")
        status_layout.addStretch()
        status_layout.addWidget(self.connection_status)
        layout.addLayout(status_layout)
        self.reader_detected = QLabel("No reader detected")
        self.reader_detected.setStyleSheet("font-size: 12px; color: #999999;")
        layout.addWidget(self.reader_detected)
        layout.addStretch(1)
        return group_box

    def _create_reading_process_box(self):
        group_box = QGroupBox("Reading Tag")
        layout = QVBoxLayout(group_box)
        self.read_status_label = QLabel("Waiting to start...")
        self.read_status_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(self.read_status_label)
        return group_box

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

    # --- Core Logic Methods ---
    def handle_read_action(self):
        """Central function for the main action button, handling the read process."""
        # --- This is the "Start Reading" click ---
        if not self.read_handler:
            self.read_handler = MultiCardReadHandler(self.nfc_handler)
            self.reading_box.setVisible(True)
            self.action_button.setText("Scan Card & Proceed")
            self.read_another_button.setVisible(False)
            self.read_status_label.setText("Please insert the first card and press 'Scan'.")
            return

        # --- This is a "Scan Card & Proceed" click ---
        self.action_button.setEnabled(False)
        self.read_status_label.setText("Reading card... Please wait.")
        
        # Call the handler to process one card
        result = self.read_handler.process_next_card()
        
        if result["status"] == "error":
            QMessageBox.critical(self, "Read Error", result["message"])
            self.reset_for_new_read()
            return

        if result["status"] == "in_progress":
            self.read_status_label.setText(result["message"])
            self.action_button.setEnabled(True)

        elif result["status"] == "finished":
            self.read_status_label.setText(result["message"])
            final_config = result["config"]
            
            # Use the parent methods to update the rest of the GUI
            try:
                self.parent.set_config(final_config)
                self.parent.update_summary()
                QMessageBox.information(self, "Read Complete", "Configuration read successfully. Showing summary.")
                self.parent.tabs.setCurrentWidget(self.parent.summary_tab)
                # Reset this tab for the next use
                self.reset_for_new_read(show_another_button=True)
            except Exception as e:
                QMessageBox.critical(self, "UI Error", f"Failed to display configuration: {e}")
                self.reset_for_new_read()

    def reset_for_new_read(self, show_another_button=False):
        """Resets the UI to its initial state to start another read process."""
        self.read_handler = None
        self.reading_box.setVisible(False)
        self.action_button.setText("Start Reading")
        self.action_button.setEnabled(True)
        self.read_another_button.setVisible(show_another_button)

    def update_connection_status(self):
        """Updates the reader connection status indicator."""
        try:
            # A simple connect/disconnect to check status without holding the connection
            self.nfc_handler.connect()
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: #66cc66; border: 1px solid #66cc66; border-radius: 10px; padding: 2px 8px;")
            self.reader_detected.setText(f"{str(self.nfc_handler.reader)} detected")
            if self.nfc_handler.connection:
                self.nfc_handler.connection.disconnect()
        except Exception:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: #ff6666; border: 1px solid #ff6666; border-radius: 10px; padding: 2px 8px;")
            self.reader_detected.setText("No reader detected")

    def tab_shown(self):
        """Public method to be called by the parent when this tab becomes visible."""
        self.update_connection_status()
        self.reset_for_new_read()