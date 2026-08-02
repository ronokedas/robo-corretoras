STYLESHEET = r"""
* { font-family: "Segoe UI"; font-size: 13px; color: #E8F0F0; }
QMainWindow, QWidget#root { background: #071113; }
QFrame#sidebar { background: #091719; border-right: 1px solid #183034; }
QLabel#brand { font-size: 20px; font-weight: 700; color: #F4FFFF; }
QLabel#brandSub { color: #6D8F91; font-size: 10px; letter-spacing: 2px; }
QPushButton#nav { text-align: left; padding: 12px 16px; border: 0; border-radius: 9px; color: #789496; background: transparent; }
QPushButton#nav:hover { background: #102426; color: #DDF6F4; }
QPushButton#nav[active="true"] { background: #123336; color: #48E0CD; border-left: 3px solid #48E0CD; }
QLabel#pageTitle { font-size: 25px; font-weight: 650; color: #F3FAFA; }
QLabel#muted { color: #789496; }
QFrame#card { background: #0B1A1D; border: 1px solid #183336; border-radius: 14px; }
QLabel#metric { font-size: 27px; font-weight: 700; color: #F4FFFF; }
QLabel#metricGreen { font-size: 27px; font-weight: 700; color: #48E0CD; }
QLabel#eyebrow { color: #789496; font-size: 11px; font-weight: 600; }
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background: #091618; border: 1px solid #244044; border-radius: 9px; padding: 9px; min-height: 18px; }
QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: #42CEBD; }
QPushButton#primary { background: #38CBB8; color: #03201D; border: 0; border-radius: 9px; padding: 11px 18px; font-weight: 700; }
QPushButton#primary:hover { background: #55E3D0; }
QPushButton#primary:disabled { background: #204A49; color: #6B9390; }
QPushButton#danger { background: #321B20; color: #FF8797; border: 1px solid #64313A; border-radius: 9px; padding: 10px 17px; font-weight: 600; }
QPushButton#secondary { background: #102528; color: #C9E7E5; border: 1px solid #244548; border-radius: 9px; padding: 10px 17px; font-weight: 600; }
QCheckBox { spacing: 8px; color: #B4CAC9; }
QCheckBox::indicator { width: 18px; height: 18px; }
QTableWidget { background: #0B1A1D; alternate-background-color: #0D2022; border: 1px solid #183336; border-radius: 12px; gridline-color: transparent; selection-background-color: #123A3C; }
QHeaderView::section { background: #0E2023; color: #789496; border: 0; border-bottom: 1px solid #1A373A; padding: 10px; font-size: 11px; font-weight: 600; }
QTableWidget::item { padding: 8px; border-bottom: 1px solid #12282B; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 2px; }
QScrollBar::handle:vertical { background: #29494C; border-radius: 4px; min-height: 30px; }
QTextEdit { background: #071416; border: 1px solid #183336; border-radius: 10px; color: #99B6B5; padding: 8px; }
QLabel#badgeGreen { color: #4AE0CD; background: #10332F; border: 1px solid #245A53; border-radius: 9px; padding: 4px 9px; font-weight: 600; }
QLabel#badgeAmber { color: #FFC96B; background: #302715; border: 1px solid #57451F; border-radius: 9px; padding: 4px 9px; font-weight: 600; }
QDialog { background: #081416; }
"""
