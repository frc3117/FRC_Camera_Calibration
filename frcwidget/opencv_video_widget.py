import cv2 as cv
import numpy as np
import ctypes

from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QLabel
from PySide2.QtCore import QTimer, Qt


class OpencvImageWidget(QLabel):
    def __init__(self,
                 resolution = None,
                 min_height: int = 640,
                 max_height: int = 2040,
                 min_width: int = 640,
                 max_width: int = 2048,
                 keep_ratio: bool = True):
        super().__init__()

        self.resolution = resolution

        self.min_height = min_height
        self.min_width = min_width

        self.max_height = max_height
        self.max_width = max_width

        self.keep_ratio = True

        self.qpix = None

        if self.resolution is not None:
            self.set_image(np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8))

    def set_image(self, img):
        ch = ctypes.c_char.from_buffer(img.data, 0)
        rcount = ctypes.c_long.from_address(id(ch)).value

        image = QImage(ch, img.shape[1], img.shape[0],
                       img.strides[0], QImage.Format_RGB888)
        image = image.scaled(self.resolution[0], self.resolution[1])

        ctypes.c_long.from_address(id(ch)).value = rcount

        if self.qpix is None:
            self.qpix = QPixmap.fromImage(image)
        else:
            self.qpix.convertFromImage(image)

        self.setPixmap(self.qpix)


class OpencvVideoWidget(OpencvImageWidget):
    def __init__(self,
                 cap,
                 resolution = None,
                 min_height: int = 640,
                 max_height: int = 2040,
                 min_width: int = 640,
                 max_width: int = 2048,
                 keep_ratio: bool = True,
                 mtx = None,
                 dist = None):
        super().__init__(resolution, min_height, max_height, min_width, max_width, keep_ratio)

        self.cap = cap

        self.set_calibration(mtx, dist)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(60)

        self.last_frame = None    

    def set_calibration(self, mtx, dist):
        self.mtx = mtx
        self.dist = dist

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            if (self.mtx is not None and self.dist is not None):
                self.last_frame = cv.undistort(frame, self.mtx, self.dist, None, None)
            else:
                self.last_frame = frame.copy()

            self.set_image(self.last_frame)
