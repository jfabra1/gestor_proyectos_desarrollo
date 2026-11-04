TEMA_CLARO = """
QMainWindow, QWidget {
    background-color: #f5f5f5;
    color: #2c3e50;
}

QMenuBar {
    background-color: #ffffff;
    color: #2c3e50;
    border-bottom: 1px solid #dcdde1;
}

QMenuBar::item:selected {
    background-color: #3498db;
    color: white;
}

QMenu {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #21618c;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #7f8c8d;
}

QPushButton#boton_peligro {
    background-color: #e74c3c;
}

QPushButton#boton_peligro:hover {
    background-color: #c0392b;
}

QPushButton#boton_exito {
    background-color: #2ecc71;
}

QPushButton#boton_exito:hover {
    background-color: #27ae60;
}

QPushButton#boton_advertencia {
    background-color: #f39c12;
}

QPushButton#boton_advertencia:hover {
    background-color: #e67e22;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #3498db;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #3498db;
}

QListWidget {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 4px;
}

QListWidget::item:selected {
    background-color: #3498db;
    color: white;
}

QListWidget::item:hover {
    background-color: #ecf0f1;
}

QTreeWidget, QTreeView {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    outline: none;
}

QTreeWidget::item, QTreeView::item {
    padding: 6px;
    border-radius: 4px;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #3498db;
    color: white;
}

QTabWidget::pane {
    border: 1px solid #dcdde1;
    border-radius: 6px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #ecf0f1;
    color: #2c3e50;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #3498db;
    color: white;
}

QTabBar::tab:hover {
    background-color: #d5dbdb;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #95a5a6;
}

QLabel {
    color: #2c3e50;
}

QLabel#titulo {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
}

QLabel#subtitulo {
    font-size: 14px;
    color: #7f8c8d;
}

QGroupBox {
    border: 1px solid #dcdde1;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #2c3e50;
}

QComboBox {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
    border-radius: 6px;
    padding: 6px 12px;
}

QComboBox:hover {
    border: 1px solid #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #dcdde1;
    selection-background-color: #3498db;
}

QProgressBar {
    border: 1px solid #dcdde1;
    border-radius: 6px;
    text-align: center;
    background-color: #ecf0f1;
    height: 12px;
}

QProgressBar::chunk {
    border-radius: 5px;
    background-color: #3498db;
}

QSplitter::handle {
    background-color: #dcdde1;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QToolTip {
    background-color: #2c3e50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
}

QStatusBar {
    background-color: #ffffff;
    color: #7f8c8d;
    border-top: 1px solid #dcdde1;
}

QFrame#tarjeta_servicio {
    background-color: #ffffff;
    border: 1px solid #dcdde1;
    border-radius: 8px;
}

QLabel#nombre_servicio {
    font-weight: bold;
    font-size: 14px;
    color: #2c3e50;
}

QLabel#comando_servicio {
    font-size: 11px;
    color: #7f8c8d;
}

QLabel#detalle_servicio {
    font-size: 11px;
    color: #95a5a6;
}

QCheckBox {
    spacing: 8px;
    color: #2c3e50;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #bdc3c7;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #bdc3c7;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #3498db;
    border-color: #3498db;
}
"""

TEMA_OSCURO = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}

QMenuBar::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QMenu {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
}

QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #74c7ec;
}

QPushButton:pressed {
    background-color: #89dceb;
}

QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#boton_peligro {
    background-color: #f38ba8;
}

QPushButton#boton_peligro:hover {
    background-color: #eba0ac;
}

QPushButton#boton_exito {
    background-color: #a6e3a1;
}

QPushButton#boton_exito:hover {
    background-color: #94e2d5;
}

QPushButton#boton_advertencia {
    background-color: #fab387;
}

QPushButton#boton_advertencia:hover {
    background-color: #f9e2af;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #89b4fa;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #89b4fa;
}

QListWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
}

QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 4px;
}

QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QListWidget::item:hover {
    background-color: #313244;
}

QTreeWidget, QTreeView {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 6px;
    outline: none;
}

QTreeWidget::item, QTreeView::item {
    padding: 6px;
    border-radius: 4px;
}

QTreeWidget::item:selected, QTreeView::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}

QTabBar::tab:hover {
    background-color: #45475a;
}

QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QLabel {
    color: #cdd6f4;
}

QLabel#titulo {
    font-size: 18px;
    font-weight: bold;
    color: #cdd6f4;
}

QLabel#subtitulo {
    font-size: 14px;
    color: #a6adc8;
}

QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #cdd6f4;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
}

QComboBox:hover {
    border: 1px solid #89b4fa;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    selection-background-color: #89b4fa;
}

QProgressBar {
    border: 1px solid #313244;
    border-radius: 6px;
    text-align: center;
    background-color: #313244;
    height: 12px;
}

QProgressBar::chunk {
    border-radius: 5px;
    background-color: #89b4fa;
}

QSplitter::handle {
    background-color: #313244;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}

QFrame#tarjeta_servicio {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 8px;
}

QLabel#nombre_servicio {
    font-weight: bold;
    font-size: 14px;
    color: #cdd6f4;
}

QLabel#comando_servicio {
    font-size: 11px;
    color: #a6adc8;
}

QLabel#detalle_servicio {
    font-size: 11px;
    color: #7f849c;
}

QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid #45475a;
    background-color: #313244;
}

QRadioButton::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}
"""
