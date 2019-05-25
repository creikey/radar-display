#!/usr/bin/env python3

import logging
import coloredlogs
import sys
import time
import socket

from radar_display import UDP_PORT, IMAGE_DIMENSIONS, UDP_PING_MESSAGE


def main():
    coloredlogs.install(level="DEBUG")

    data = bytearray([127] * (IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1]))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", UDP_PORT))
    logging.info(f"Listening for message {UDP_PING_MESSAGE}")
    message, address = sock.recvfrom(len(UDP_PING_MESSAGE))
    logging.info(f"Got response: {message}")
    if message != UDP_PING_MESSAGE:
        logging.error(f"Did not get back {UDP_PING_MESSAGE}")
        sys.exit(1)
    logging.info(f"Accepted new client from {address}!")
    logging.info(f"Sending back {UDP_PING_MESSAGE}")
    sock.sendto(UDP_PING_MESSAGE, address)
    while True:
        logging.info("Sending new image")
        # for i in range(0, IMAGE_DIMENSIONS[0]):
        # for j in range(0, IMAGE_DIMENSIONS[1]):
        # sock.sendto(bytes([127]), address)
        sock.sendto(data, address)
        logging.info("Waiting")
        time.sleep(1)


if __name__ == "__main__":
    main()
