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
from PIL import Image, ImageQt
import matplotlib as mpl
import matplotlib.cm as cm

STYLESHEET_NAME = "stylesheet.qss"
IMAGE_DIMENSIONS = [1024, 256]
TCP_IP = "127.0.0.1"
TCP_PORT = 54321
UDP_PING_MESSAGE = b"ready"
SOCKET_TIMEOUT = 3.0
DEFAULT_VMAX = 255.0
DEFAULT_LOG_CONSTANT = 20.0

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

    @Slot(QPixmap)
    def update(self, radar_pixmap):  # received from thread when new data is ready
        label_width = self.width()
        label_height = self.height()
        self.setPixmap(
            radar_pixmap.scaled(
                label_width, label_height, Qt.KeepAspectRatio
            )
        )


class DataThread(QThread):
    new_data = Signal(QPixmap)

    def __init__(self, sock, radar_image: RadarImage):
        super(
            DataThread, self
        ).__init__()  # not sure why syntax has to be this way, errors if not
        self.sock = sock
        self.vmax = DEFAULT_VMAX
        self.log_constant = DEFAULT_LOG_CONSTANT
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
            norm = mpl.colors.Normalize(vmin=0.0, vmax=self.vmax)
            cmap = cm.hot
            m = cm.ScalarMappable(norm=norm, cmap=cmap)
            final_data = np.frombuffer(data, dtype="f")
            final_data.shape = (IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1])
            log_function = lambda x: np.log(x) * self.log_constant
            final_data = log_function(final_data)
            # logging.debug(f"{m.to_rgba(127.0)}")
            ultra_final_data = m.to_rgba(final_data, bytes=True)
            # logging.debug(f"{ultra_final_data[0]}")
            im = Image.frombytes(
                "RGBA", (IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), ultra_final_data
            )
            # logging.debug(f"emitting new data to {self.data}")
            imqt = ImageQt.ImageQt(im)
            pix = QPixmap.fromImage(imqt)
            if not self.stopping:
                # logging.info(f"Received new image")
                self.new_data.emit(pix)
            # time.sleep(1.0)

    @Slot(str)
    def new_vmax(self, new_vmax):
        if new_vmax == "":
            self.vmax = DEFAULT_VMAX
        else:
            self.vmax = float(new_vmax)

    @Slot(str)
    def new_log_constant(self, new_log_constant):
        if new_log_constant == "":
            self.log_constant = DEFAULT_LOG_CONSTANT
        else:
            self.log_constant = float(new_log_constant)


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

        properties = QtWidgets.QWidget()
        properties_layout = QtWidgets.QGridLayout()
        properties.setLayout(properties_layout)
        window_layout.addWidget(properties)

        data_thread = DataThread(sock, radar_image)
        data_thread.new_data.connect(radar_image.update)
        data_thread.start()

        vmax_lineedit = QtWidgets.QLineEdit()
        vmax_lineedit.text = str(DEFAULT_VMAX)
        vmax_lineedit.setValidator(QtGui.QDoubleValidator())
        vmax_lineedit.textChanged.connect(data_thread.new_vmax)
        properties_layout.addWidget(QtWidgets.QLabel("Colorramp VMax: "), 0, 0, 1, 1)
        properties_layout.addWidget(vmax_lineedit, 0, 1, 1, 1)

        log_constant_lineedit = QtWidgets.QLineEdit()
        log_constant_lineedit.text = str(DEFAULT_LOG_CONSTANT)
        log_constant_lineedit.setValidator(QtGui.QDoubleValidator())
        log_constant_lineedit.textChanged.connect(data_thread.new_log_constant)
        properties_layout.addWidget(QtWidgets.QLabel("Log Constant: "), 1, 0, 1, 1)
        properties_layout.addWidget(log_constant_lineedit, 1, 1, 1, 1)

        window.show()
        qt_exit_code = app.exec_()
        logging.debug("Stopping thread...")
        data_thread.stopping = True
        logging.debug("Shutting down socket")
        data_thread.wait()
        sys.exit(qt_exit_code)


if __name__ == "__main__":
    main()
