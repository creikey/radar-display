#!/usr/bin/env python3

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Qt, Signal, QObject, Slot
from PySide2.QtGui import QImage, QPixmap
import sys
import logging
import coloredlogs

STYLESHEET_NAME = "stylesheet.qss"
IMAGE_DIMENSIONS = [16, 16]

radar_qimage = None


class RadarImage(QtWidgets.QLabel):
    def __init__(self, *args):
        """Creates the QImage if not created yet, then scales with aspect ratio"""
        global radar_qimage  # updates from another thread
        super().__init__(*args)
        if radar_qimage == None:
            radar_qimage = QImage(
                IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1], QImage.Format_Grayscale8
            )
        label_width = self.width()
        label_height = self.height()
        self.setPixmap(
            QPixmap.fromImage(radar_qimage).scaled(
                label_width, label_height, Qt.KeepAspectRatio
            )
        )
        self.setScaledContents(False)
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
