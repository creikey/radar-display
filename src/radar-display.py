#!/usr/bin/env python3

from PySide2 import QtCore, QtWidgets, QtGui  # core of the QT library
from PySide2.QtCore import (
    Qt,
    Signal,
    QObject,
    Slot,
    QThread,
    QByteArray,
)  # basic QObject utilities
from PySide2.QtGui import QImage, QPixmap  # radar image
import sys  # arguments for QT
import logging  # python logging library
import coloredlogs  # pretty logs
import socket  # receiving data from radar server
import time  # make data thread wait when testing TODO remove once socket server is working

STYLESHEET_NAME = "stylesheet.qss"
IMAGE_DIMENSIONS = [128, 128]
UDP_IP = "127.0.0.1"
UDP_PORT = 54321


class RadarImage(QtWidgets.QLabel):
    def __init__(self, *args):
        """Scales created image by aspect ratio"""
        super().__init__(*args)
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

    @Slot(QImage)
    def update(self, radar_qimage):  # received from thread when new data is ready
        label_width = self.width()
        label_height = self.height()
        self.setPixmap(
            QPixmap.fromImage(radar_qimage).scaled(
                label_width, label_height, Qt.KeepAspectRatio
            )
        )


class DataThread(QThread):
    new_data = Signal(QImage)

    def __init__(self, sock, radar_image: RadarImage):
        super(
            DataThread, self
        ).__init__()  # not sure why syntax has to be this way, errors if not
        self.sock = sock
        self.stopping = False
        # self.data = bytearray(IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1])
        self.radar_image = radar_image

    def __del__(self):
        pass  # TODO make deconstructor shutdown instead of in main

    def run(self):
        while not self.stopping:
            data, addr = self.sock.recvfrom(
                IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1]
            )  # receive whole image in buffer
            # for i in range(0, IMAGE_DIMENSIONS[0]):
            #     for j in range(0, IMAGE_DIMENSIONS[1]):
            #         self.data[i * IMAGE_DIMENSIONS[0] + j] = i + j

            # logging.debug(f"emitting new data to {self.data}")
            if data != None:
                self.new_data.emit(
                    QImage(
                        data,
                        IMAGE_DIMENSIONS[0],
                        IMAGE_DIMENSIONS[1],
                        QImage.Format_Grayscale8,
                    )
                )
            # time.sleep(1.0)


def main():
    coloredlogs.install(level="DEBUG")

    # bind UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internt IP with UDP
    sock.connect((UDP_IP, UDP_PORT))
    logging.info(f"Connected to IP {UDP_IP} with port {UDP_PORT}")

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

    data_thread = DataThread(sock, radar_image)
    data_thread.new_data.connect(radar_image.update)
    data_thread.start()

    window.show()
    qt_exit_code = app.exec_()
    logging.debug("Stopping thread...")
    data_thread.stopping = True
    logging.debug("Shutting down socket")
    data_thread.sock.shutdown(socket.SHUT_RD)
    data_thread.wait()
    sys.exit(qt_exit_code)


if __name__ == "__main__":
    main()
