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
import numpy as np
from io import BytesIO

STYLESHEET_NAME = "stylesheet.qss"
IMAGE_DIMENSIONS = [1024, 256]
TCP_IP = "127.0.0.1"
TCP_PORT = 54321
UDP_PING_MESSAGE = b"ready"
SOCKET_TIMEOUT = 3.0

# f = BytesIO()
# np.savez_compressed(
#     f, frame=np.zeros((IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), dtype="f")
# )
# f.seek(0)
DATA_LEN = IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1] * 4


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

    def get_data(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < DATA_LEN:
            chunk = self.sock.recv(min(DATA_LEN - bytes_recd, 2048))
            if chunk == b"":
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b"".join(chunks)

    def run(self):
        while not self.stopping:
            data = self.get_data()
            # for i in range(0, IMAGE_DIMENSIONS[0]):
            #     for j in range(0, IMAGE_DIMENSIONS[1]):
            #         self.data[i * IMAGE_DIMENSIONS[0] + j] = i + j
            # logging.debug(f"{DATA_LEN}")
            final_data = np.frombuffer(data, dtype="f")
            final_data = np.int8(final_data)  # TODO colorramp with slider as max
            # logging.debug(f"emitting new data to {self.data}")
            if not self.stopping:
                # logging.info(f"Received new image")
                self.new_data.emit(
                    QImage(
                        final_data,
                        IMAGE_DIMENSIONS[0],
                        IMAGE_DIMENSIONS[1],
                        QImage.Format_Grayscale8,
                    )
                )
            # time.sleep(1.0)


def main():
    coloredlogs.install(level="DEBUG")

    # bind UDP socket
    with socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    ) as sock:  # internt IP with UDP
        sock.connect((TCP_IP, TCP_PORT))
        logging.info(f"Connected to IP {TCP_IP} with port {TCP_PORT}")

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
        data_thread.wait()
        sys.exit(qt_exit_code)


if __name__ == "__main__":
    main()
