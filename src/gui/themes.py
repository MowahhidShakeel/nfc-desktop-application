STYLESHEET = """
QMainWindow {
    background-color: #FFFFFF;
}

QLabel {
    color: #333333;
    font-size: 14px;
}

QLineEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 4px;
    background-color: #F8F8F8;
    margin-top: 2px;
    color: #000000;
}

QSpinBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 4px;
    background-color: #F8F8F8;
    margin-top: 2px;
    color: #000000;
}

QComboBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 4px;
    background-color: #F8F8F8;
    margin-top: 2px;
    color: #000000;
}

QComboBox::drop-down {
    border-left: 1px solid #CCCCCC;
    background-color: #E0E0E0;
    width: 20px;
    color: black;
}

QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background-color: #FFFFFF;
    color: #000000; 
    selection-background-color: #0056b3;
    selection-color: #FFFFFF;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #F0F0F0;
    color: #000000;
}

QCheckBox {
    color: #333333;
    margin-top: 2px;
    spacing: 5px;
}
    
QPushButton {
    background-color: #007BFF;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 6px;
    font-size: 14px;
    margin-top: 2px;
}

QPushButton:hover {
    background-color: #0056b3;
}

QTabWidget::pane {
    border: none;
}

QTabBar::tab {
    background-color: #000000;
    color: #FFFFFF;
    padding: 8px;
    margin-right: 2px;
}

QTabBar::tab:hover {
    background-color: #FFFFFF;
    color: #000000;
}

QTabBar::tab:selected {
    background-color: #0056b3;
    color: #FFFFFF;
}

QTextEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    background-color: #F8F8F8;
    margin-top: 2px;
    color: #000000;
}

QTextBrowser {
    border: none;
    background-color: #F8F8F8;
    margin-top: 2px;
    color: #000000;
}

QGroupBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    background-color: #F8F8F8;
    margin-top: 10px;
    padding: 10px;
}
"""
