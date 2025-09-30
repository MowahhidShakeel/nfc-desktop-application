STYLESHEET = """
/* ======================
   Main Window
   ====================== */
QMainWindow {
    background-color: #FFFFFF;
}

/* ======================
   Text Elements
   ====================== */
QLabel {
    color: #222222;
    font-size: 14px;
}

QCheckBox {
    color: #222222;
    margin-top: 2px;
    spacing: 5px;
    font-size: 13px;
}

/* ======================
   Input Fields
   ====================== */
QLineEdit, 
QSpinBox, 
QComboBox, 
QTextEdit {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    padding: 4px;
    background-color: #FFFFFF;
    color: #000000;
    font-size: 13px;
}

QLineEdit:focus, 
QSpinBox:focus, 
QComboBox:focus, 
QTextEdit:focus {
    border: 1px solid #007BFF;
    outline: none;
}

/* ======================
   ComboBox
   ====================== */
QComboBox::drop-down {
    border-left: 1px solid #CCCCCC;
    background-color: #E9F2FF;
    width: 20px;
}

QComboBox QAbstractItemView {
    border: 1px solid #CCCCCC;
    background-color: #FFFFFF;
    color: #000000;
    selection-background-color: #007BFF;
    selection-color: #FFFFFF;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #E9F2FF;
    color: #000000;
}

/* ======================
   Buttons
   ====================== */
QPushButton {
    background-color: #007BFF;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #0056b3;
}

QPushButton:pressed {
    background-color: #004080;
}

/* ======================
   Tabs
   ====================== */
QTabWidget::pane {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    margin-top: -1px;
}

QTabBar::tab {
    background-color: #F1F1F1;
    color: #000000;
    padding: 8px 14px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:hover {
    background-color: #E9F2FF;
    color: #000000;
}

QTabBar::tab:selected {
    background-color: #007BFF;
    color: #FFFFFF;
}

/* ======================
   Scroll Areas
   ====================== */
QScrollArea {
    background-color: #FFFFFF;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: #FFFFFF;
}


/* ======================
   Text Display
   ====================== */
QTextBrowser {
    border: none;
    background-color: #F8F8F8;
    color: #000000;
    padding: 4px;
}

/* ======================
   Message Boxes
   ====================== */
QMessageBox {
    background-color: #FFFFFF;
    color: #000000;
}

QMessageBox QLabel {
    color: #000000;
}

/* ======================
   Group Boxes
   ====================== */
QGroupBox {
    border: 1px solid #CCCCCC;
    border-radius: 4px;
    background-color: #FAFAFA;
    margin-top: 10px;
    padding: 10px;
}
"""
