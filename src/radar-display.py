#!/usr/bin/env python3

from PySide2.QtCore import Qt, Signal, QObject, Slot
from PySide2 import QtCore, QtWidgets, QtGui
import sys
import logging
import coloredlogs

STYLESHEET_NAME = "stylesheet.qss"

def main():
    coloredlogs.install(level='DEBUG')

    app = QtWidgets.QApplication(sys.argv)
    try:
        with open(STYLESHEET_NAME, "r") as stylesheet:
            app.setStyleSheet(stylesheet.read())
    except FileNotFoundError:
        logging.warning(f"Could not find stylesheet {STYLESHEET_NAME}")

    window = QtWidgets.QWidget()
    window_layout = QtWidgets.QVBoxLayout()
    window.setLayout(window_layout)

    test_label = QtWidgets.QLabel("Testing")
    test_label.setAlignment(Qt.AlignLeft)
    window_layout.addWidget(test_label)

    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
