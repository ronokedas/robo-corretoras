from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .main_window import EvePulseWindow
from .theme import STYLESHEET


def main() -> int:
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setApplicationName("EvePulse Trader")
    app.setOrganizationName("EvePulse")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = EvePulseWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
