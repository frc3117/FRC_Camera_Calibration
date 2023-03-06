import cv2 as cv
import numpy as np

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer


class OpencvImageWidget(QLabel):
    def __init__(self,
                 resolution: tuple[int, int] = None,
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

        if self.resolution is not None:
            self.set_image(np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8))

    def set_image(self, img):
        if self.resolution is None:
            ratio = img.shape[0] / img.shape[1]

            old_height = img.shape[0]
            old_width = img.shape[1]
        else:
            ratio = img.shape[0] / img.shape[1]

            old_height = self.resolution[1]
            old_width = self.resolution[0]

        ratio = old_height / old_width
        new_height = max(min(old_height, self.max_height), self.min_height)
        new_width = max(min(old_width, self.max_width), self.min_width)

        frame = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        frame = cv.resize(frame, (new_width, new_height))

        self.resize(new_width, new_height)

        image = QImage(frame, new_width, new_height,
                       frame.strides[0], QImage.Format_RGB888)

        self.setPixmap(QPixmap.fromImage(image))


class OpencvVideoWidget(OpencvImageWidget):
    def __init__(self,
                 cap,
                 resolution: tuple[int, int] = None,
                 min_height: int = 640,
                 max_height: int = 2040,
                 min_width: int = 640,
                 max_width: int = 2048,
                 keep_ratio: bool = True
                 ):
        super().__init__(resolution, min_height, max_height, min_width, max_width, keep_ratio)

        self.cap = cap

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(60)

        self.last_frame = None

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()
            self.set_image(frame)
