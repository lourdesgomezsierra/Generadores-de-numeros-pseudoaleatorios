ESTILO_APLICACION = """
QMainWindow, QWidget {
    background: #f5f7f8;
    color: #1f2933;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 10pt;
}

QLabel#titulo {
    font-size: 24pt;
    font-weight: 800;
    color: #172026;
}

QLabel#subtitulo {
    font-size: 11pt;
    color: #5b6770;
}

QLabel#seccion {
    font-size: 13pt;
    font-weight: 700;
    color: #25313a;
}

QLabel#ayuda {
    color: #6b7680;
    line-height: 140%;
}

QFrame#tarjeta, QFrame#panel {
    background: #ffffff;
    border: 1px solid #dde4e8;
    border-radius: 12px;
}

QPushButton {
    background: #2f7d7e;
    border: 0;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 700;
    padding: 9px 15px;
}

QPushButton:hover {
    background: #286d6f;
}

QPushButton:pressed {
    background: #205b5c;
}

QPushButton#secundario {
    background: #e8eef1;
    color: #25313a;
}

QPushButton#secundario:hover {
    background: #d9e3e8;
}

QPushButton#peligro {
    background: #d96c5f;
}

QLineEdit, QComboBox {
    background: #ffffff;
    border: 1px solid #cfd8dd;
    border-radius: 8px;
    min-height: 28px;
    padding: 6px 9px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2f7d7e;
}

QTableWidget {
    background: #ffffff;
    border: 1px solid #dde4e8;
    border-radius: 8px;
    gridline-color: #edf1f3;
    selection-background-color: #d9eeee;
    selection-color: #172026;
}

QHeaderView::section {
    background: #eef3f5;
    border: 0;
    border-right: 1px solid #dde4e8;
    border-bottom: 1px solid #dde4e8;
    color: #25313a;
    font-weight: 700;
    padding: 7px;
}

QScrollBar:vertical {
    background: #f5f7f8;
    width: 11px;
}

QScrollBar::handle:vertical {
    background: #b9c6cc;
    border-radius: 5px;
}
"""
