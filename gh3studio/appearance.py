"""Shared visual language for the desktop studio; no gameplay behavior."""
from PySide6.QtGui import QFont

STYLE='''
QWidget { background: #101722; color: #e6edf6; font-family: "Segoe UI", "DejaVu Sans"; font-size: 12px; }
QMainWindow, QDialog { background: #101722; }
QLabel { background: transparent; }
QLabel#brand { font-size: 20px; font-weight: 700; letter-spacing: 1px; }
QLabel#eyebrow { color: #77dec5; font-weight: 700; font-size: 11px; letter-spacing: 2px; }
QLabel#hero { font-size: 30px; font-weight: 700; }
QLabel#muted, QLabel#versionBadge { color: #a6b6c9; }
QLabel#nextStep { background: #1b3440; border-left: 3px solid #61dfb1; border-radius: 5px; padding: 9px; color: #dffbf2; }
QFrame#card { background: #192536; border: 1px solid #30445a; border-radius: 14px; }
QFrame#card QLabel { background: transparent; }
QLabel#cardTitle { font-size: 21px; font-weight: 600; }
QLabel#cardBody { color: #b8c6d7; font-size: 13px; }
QLabel#cardNumber { font-size: 27px; color: #70e2b8; font-weight: 700; }
QTabWidget::pane { border: 1px solid #29394d; border-radius: 8px; top: -1px; }
QTabBar::tab { background: #131e2c; color: #a9b9cc; padding: 10px 18px; border-bottom: 3px solid transparent; }
QTabBar::tab:selected { background: #1b2a3b; color: #f3fbff; border-bottom: 3px solid #62dab1; }
QTabBar::tab:hover { background: #213349; }
QPushButton { background: #25364b; border: 1px solid #3b506b; border-radius: 6px; padding: 7px 11px; font-weight: 600; }
QPushButton:hover { background: #31465f; border-color: #6da2c9; }
QPushButton:pressed { background: #172b3c; }
QPushButton:focus { border: 2px solid #79cfff; }
QPushButton:disabled { background: #182331; color: #6f8195; border-color: #29394d; }
QPushButton#primaryAction { background: #63ddb1; color: #09251f; border-color: #63ddb1; }
QPushButton#primaryAction:hover { background: #8beac8; }
QPushButton#primaryAction:disabled { background: #274d47; color: #8aaba3; border-color: #31594f; }
QPushButton#quietAction { background: transparent; border-color: #33445a; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: #0d1520; border: 1px solid #3a4d65; border-radius: 5px; padding: 5px; selection-background-color: #386a81; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #70d7bc; }
QComboBox QAbstractItemView { background: #1a293b; color: #eef6ff; selection-background-color: #305c6b; }
QTextEdit, QTextBrowser, QTableView { background: #0d1520; border: 1px solid #314259; border-radius: 6px; selection-background-color: #315f74; alternate-background-color: #172537; }
QHeaderView::section { background: #23364b; color: #cfdbeb; border: none; border-bottom: 1px solid #3c526d; padding: 6px; }
QGroupBox { border: 1px solid #33465c; border-radius: 8px; margin-top: 13px; padding-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; color: #b9d9e8; }
QProgressBar { background: #182638; border: none; border-radius: 4px; min-height: 7px; max-height: 16px; color: #e6edf6; text-align: center; }
QProgressBar::chunk { background: #64dcb4; border-radius: 4px; }
QSlider::groove:horizontal { height: 5px; background: #31445b; border-radius: 2px; }
QSlider::handle:horizontal { background: #7be3bf; width: 13px; margin: -5px 0; border-radius: 6px; }
QCheckBox { spacing: 7px; }
QCheckBox::indicator { width: 15px; height: 15px; border: 1px solid #56708b; background: #101d2b; border-radius: 3px; }
QCheckBox::indicator:checked { background: #64dcb4; border: 2px solid #c3ffeb; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #101b29; width: 11px; }
QScrollBar::handle:vertical { background: #3e5773; border-radius: 5px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QToolTip { background: #23354a; color: #f2f7ff; border: 1px solid #6084a2; padding: 5px; }
'''


def apply_style(window):
    window.setStyleSheet(STYLE)


def primary(widget):
    widget.setObjectName('primaryAction')
    widget.style().unpolish(widget);widget.style().polish(widget);widget.update()

# Focused workshop surfaces. All decoration is native Qt; no downloaded assets.
STYLE += '''
QWidget { font-size: 13px; }
QLabel#brand { font-size: 18px; letter-spacing: 1px; }
QLabel#versionBadge { color: #86b6b7; font-size: 11px; }
QLabel#hero { font-size: 32px; }
QLabel#pageTitle { font-size: 24px; font-weight: 700; color: #f1f6fc; }
QLabel#songTitle { font-size: 16px; font-weight: 600; }
QLabel#step { background: #172636; color: #94a8bf; padding: 9px 12px; border: 1px solid #283b50; border-radius: 7px; }
QLabel#step[active="true"] { background: #1b3c3c; border-color: #63ddb1; color: #bff6df; font-weight: 600; }
QLabel#step[complete="true"] { color: #9ee6c9; border-color: #35594f; }
QLabel#nextStep { background: #172e39; border-left: 3px solid #68d7b5; border-radius: 7px; padding: 7px 9px; }
QFrame#card { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #203344,stop:1 #182331); border: 1px solid #3e556b; border-radius: 14px; }
QTableView { alternate-background-color: #142130; gridline-color: transparent; }
QTableView::item { padding: 5px; }
QTableView::item:selected { background: #244c5c; color: #f3fcff; }
QTabBar::tab { padding: 9px 16px; }
QMenu { background: #1b2939; border: 1px solid #486079; padding: 6px; }
QMenu::item { padding: 9px 18px; }
QMenu::item:selected { background: #31566a; border-radius: 4px; }
QSplitter::handle { background: #24374a; }
'''
