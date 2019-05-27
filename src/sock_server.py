#!/usr/bin/env python3

import logging
import coloredlogs
import sys
import time
import socket
from io import BytesIO
import numpy as np

from radar_display import TCP_PORT, IMAGE_DIMENSIONS


def main():
    coloredlogs.install(level="DEBUG")

    data = np.zeros((IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), dtype="f")

    # x = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", TCP_PORT))
    logging.info("Waiting for connection")
    sock.listen(1)
    conn, address = sock.accept()
    with conn:
        logging.info(f"Connected to {address}")
        while True:
            # for d in np.nditer(data, op_flags=["readwrite"]):
            #     d[...] = d + x
            #     x += 0.1
            # logging.info(f"Sending new image of length {len(data.tobytes())}")
            # for i in range(0, IMAGE_DIMENSIONS[0]):
            # for j in range(0, IMAGE_DIMENSIONS[1]):
            # sock.sendto(bytes([127]), address)
            # f = BytesIO()
            # np.savez_compressed(f, frame=data)
            # f.seek(0)
            # f_data = f.read()
            # logging.debug(f"{len(f_data)}")
            try:
                conn.sendall(data.tobytes())
                # time.sleep(2.0)
            except BrokenPipeError:
                logging.warning("Client disconnected")
                sys.exit(0)
            # logging.info("Waiting")
            # time.sleep(0.01)


if __name__ == "__main__":
    main()
