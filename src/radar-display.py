#!/usr/bin/env python3

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt, Signal, QObject, Slot
from PySide2.QtGui import QImage, QPixmap
import sys
import logging
import coloredlogs

STYLESHEET_NAME = "stylesheet.qss"
IMAGE_DIMENSIONS = [16, 16]


class RadarImage(QtWidgets.QLabel):
    def __init__(self, *args):
        super().__init__(*args)
        image = QImage(3, 3, QImage.Format_Grayscale8)
        self.setPixmap(QPixmap.fromImage(image))
        self.show()


def main():
    coloredlogs.install(level="DEBUG")

    app = QtWidgets.QApplication(sys.argv)
    try:
        with open(STYLESHEET_NAME, "r") as stylesheet:
            app.setStyleSheet(stylesheet.read())
    except FileNotFoundError:
        logging.warning(f"Could not find stylesheet {STYLESHEET_NAME}")

    window = QtWidgets.QWidget()
    window_layout = QtWidgets.QVBoxLayout()
    window.setLayout(window_layout)

    radar_label = QtWidgets.QLabel("Radar Data")
    radar_label.setAlignment(Qt.AlignCenter)
    window_layout.addWidget(radar_label)

    radar_image = RadarImage()
    radar_image.setAlignment(Qt.AlignCenter)
    window_layout.addWidget(radar_image)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
