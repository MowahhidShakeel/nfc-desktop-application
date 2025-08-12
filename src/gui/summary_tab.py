from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt

class SummaryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Title and Subtitle
        title = QLabel("Summary")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Review your network configuration.")
        layout.addWidget(subtitle)

        # Summary Display
        self.summary_display = QTextBrowser()
        self.summary_display.setReadOnly(True)
        layout.addWidget(self.summary_display)

        # Previous/Next Buttons
        button_layout = QVBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(4))
        button_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(6))
        button_layout.addWidget(next_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)