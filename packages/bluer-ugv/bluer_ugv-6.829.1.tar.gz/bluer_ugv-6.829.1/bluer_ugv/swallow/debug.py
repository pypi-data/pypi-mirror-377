from blueness import module
import numpy as np
import cv2

from bluer_options.terminal import hr
from bluer_algo.socket.classes import SocketComm
from bluer_algo.tracker.classes.target import Target

from bluer_ugv import NAME
from bluer_ugv.logger import logger


NAME = module.name(__file__, NAME)


def debug() -> bool:
    logger.info(f"{NAME}.debug ...")

    socket = SocketComm.listen_on()

    title = "debug..."

    cv2.namedWindow(title)
    logger.info("Ctrl+C to exit...")

    image = np.zeros((480, 640, 3), np.uint8)

    try:
        while True:
            cv2.imshow(title, image)
            cv2.waitKey(1)

            success, image = socket.receive_data(np.ndarray)
            if not success:
                break
    except KeyboardInterrupt:
        logger.info("Ctrl+C, stopping.")

    cv2.destroyWindow(title)

    return True
