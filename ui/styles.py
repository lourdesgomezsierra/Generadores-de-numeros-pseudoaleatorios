ESTILO_APLICACION = """
QMainWindow, QWidget {
    background: #fff7fb;
    color: #211827;
    font-family: "Arial Black";
    font-size: 10pt;
}

QLabel#titulo {
    font-family: "Arial Black";
    font-size: 30pt;
    font-weight: 900;
    color: #111111;
    letter-spacing: 2px;
    padding-bottom: 10px;
}

QLabel#subtitulo {
    font-size: 11pt;
    color: #7b5f78;
    font-family: "Segoe UI";
    font-weight: 500;
}

QLabel#seccion {
    font-size: 15pt;
    font-weight: 900;
    color: #211827;
    font-family: "Arial Black";
}

QLabel#ayuda {
    color: #6f5d78;
    background: #fff0f8;
    border: 2px solid #211827;
    border-radius: 10px;
    padding: 8px;
    font-family: "Segoe UI";
}

QFrame#tarjeta, QFrame#panel {
    background: #ffffff;
    border: 3px solid #211827;
    border-radius: 22px;
}

QFrame#panelSecundario {
    background: #fffaff;
    border: 2px solid #d8b7ec;
    border-radius: 16px;
}

QPushButton {
    background: #d88cf5;
    border: 3px solid #211827;
    border-radius: 14px;
    color: #ffffff;
    font-family: "Arial Black";
    font-size: 10pt;
    font-weight: 900;
    padding: 10px 18px;
    min-height: 18px;
}

QPushButton:hover {
    background: #e6a7ff;
}

QPushButton:pressed {
    background: #b66ce3;
}

QPushButton#secundario {
    background: #ffd0e6;
    color: #211827;
}

QPushButton#secundario:hover {
    background: #ffbddb;
}

QPushButton#peligro {
    background: #ff7ea5;
    color: #ffffff;
}

QPushButton#peligro:hover {
    background: #ff6795;
}

QLineEdit, QComboBox {
    background: #ffffff;
    border: 2px solid #d8b7ec;
    border-radius: 14px;
    min-height: 32px;
    padding: 8px 12px;
    color: #211827;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QLineEdit:focus, QComboBox:focus {
    border: 3px solid #c06eff;
    background: #fffaff;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QTabWidget::pane {
    border: 2px solid #d8b7ec;
    border-radius: 14px;
    background: #ffffff;
}

QTabBar::tab {
    background: #ffd0e6;
    color: #211827;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 10px 18px;
    margin-right: 5px;
    font-family: "Arial Black";
    font-weight: 900;
}

QTabBar::tab:selected {
    background: #d88cf5;
    color: #ffffff;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #fff0f8;
    border: 3px solid #211827;
    border-radius: 16px;
    gridline-color: #f0d9f7;
    selection-background-color: #f7c9ff;
    selection-color: #211827;
    font-family: "Segoe UI";
}

QHeaderView::section {
    background: #ffd0e6;
    border: 0;
    border-right: 1px solid #e3b4f5;
    border-bottom: 2px solid #211827;
    color: #211827;
    font-family: "Arial Black";
    font-size: 9pt;
    font-weight: 900;
    padding: 10px;
}

QScrollBar:vertical {
    background: #fff0f8;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #c87cf0;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #de9cff;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QToolTip {
    background: #211827;
    color: #ffffff;
    border: 2px solid #d88cf5;
    padding: 6px;
    border-radius: 8px;
}
"""