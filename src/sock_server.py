#!/usr/bin/env python3

import logging
import coloredlogs
import sys
import time
import socket

from radar_display import TCP_PORT, IMAGE_DIMENSIONS


def main():
    coloredlogs.install(level="DEBUG")

    data = bytearray([127] * (IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1]))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", TCP_PORT))
    logging.info("Waiting for connection")
    sock.listen(1)
    conn, address = sock.accept()
    with conn:
        logging.info(f"Connected to {address}")
        while True:
            logging.info("Sending new image")
            # for i in range(0, IMAGE_DIMENSIONS[0]):
            # for j in range(0, IMAGE_DIMENSIONS[1]):
            # sock.sendto(bytes([127]), address)
            try:
                conn.sendall(data)
            except BrokenPipeError:
                logging.warning("Client disconnected")
                sys.exit(0)
            logging.info("Waiting")
            time.sleep(1)


if __name__ == "__main__":
    main()
