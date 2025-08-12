from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QPushButton, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt

class SummaryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title = QLabel("Summary")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        subtitle = QLabel("Review your network configuration.")
        layout.addWidget(subtitle)

        # Frame around summary
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)
        frame_layout = QVBoxLayout()
        self.summary_display = QTextBrowser()
        self.summary_display.setReadOnly(True)
        frame_layout.addWidget(self.summary_display)
        frame.setLayout(frame_layout)
        layout.addWidget(frame)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(4))
        nav_layout.addWidget(prev_button)

        next_button = QPushButton("Next")
        next_button.clicked.connect(lambda: self.parent.tabs.setCurrentIndex(6))
        nav_layout.addWidget(next_button)

        layout.addLayout(nav_layout)
        self.setLayout(layout)
