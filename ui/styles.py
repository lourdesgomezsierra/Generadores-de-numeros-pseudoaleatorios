ESTILO_APLICACION = """
QMainWindow, QWidget {
    background: #fff7fb;
    color: #211827;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 10pt;
}

QLabel#titulo {
    font-size: 25pt;
    font-weight: 900;
    color: #1f1726;
}

QLabel#subtitulo {
    font-size: 11pt;
    color: #6f5d78;
}

QLabel#seccion {
    font-size: 14pt;
    font-weight: 800;
    color: #2a1b32;
}

QLabel#ayuda {
    color: #7b6b84;
    background: #fff0f8;
    border-radius: 8px;
    padding: 7px;
}

QFrame#tarjeta, QFrame#panel {
    background: #ffffff;
    border: 2px solid #2a1b32;
    border-radius: 18px;
}

QFrame#panelSecundario {
    background: #fffaff;
    border: 1px solid #d8b7ec;
    border-radius: 14px;
}

QPushButton {
    background: #a876e8;
    border: 2px solid #2a1b32;
    border-radius: 12px;
    color: #ffffff;
    font-weight: 800;
    padding: 10px 16px;
}

QPushButton:hover {
    background: #bf8cff;
}

QPushButton:pressed {
    background: #8659c9;
}

QPushButton#secundario {
    background: #f5d1e6;
    color: #2a1b32;
}

QPushButton#secundario:hover {
    background: #efb7d8;
}

QPushButton#peligro {
    background: #f07f9f;
    color: #ffffff;
}

QPushButton#peligro:hover {
    background: #e86a8d;
}

QLineEdit, QComboBox {
    background: #ffffff;
    border: 2px solid #d8b7ec;
    border-radius: 12px;
    min-height: 30px;
    padding: 7px 10px;
    color: #211827;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #a876e8;
    background: #fffaff;
}

QTabWidget::pane {
    border: 2px solid #d8b7ec;
    border-radius: 12px;
    background: #ffffff;
}

QTabBar::tab {
    background: #f5d1e6;
    color: #2a1b32;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    padding: 9px 15px;
    margin-right: 4px;
    font-weight: 700;
}

QTabBar::tab:selected {
    background: #a876e8;
    color: #ffffff;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #fff0f8;
    border: 2px solid #d8b7ec;
    border-radius: 12px;
    gridline-color: #f0d9f7;
    selection-background-color: #e8d4ff;
    selection-color: #211827;
}

QHeaderView::section {
    background: #f5d1e6;
    border: 0;
    border-right: 1px solid #d8b7ec;
    border-bottom: 1px solid #d8b7ec;
    color: #2a1b32;
    font-weight: 800;
    padding: 8px;
}

QScrollBar:vertical {
    background: #fff0f8;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #a876e8;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #bf8cff;
}
"""