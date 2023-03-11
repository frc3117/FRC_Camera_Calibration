import cv2 as cv
import numpy as np


class CameraCalibration:
    def __init__(self, square_count, size: int = 1):
        self.__square_count__ = (square_count[0] - 1, square_count[1] - 1)
        self.__size__ = size

        self.__criteria__ = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        ny, nx = self.__square_count__
        self.__3D_points__ = np.zeros((ny * nx, 3), np.float32)
        self.__3D_points__[:, :2] = np.mgrid[0:ny, 0:nx].T.reshape(-1, 2)
        self.__3D_points__ = self.__3D_points__ * size

        self.__3D_detected_points__ = []
        self.__2D_detected_points__ = []
        self.__resolution__ = (0, 0)

    def find_corners(self, img: np.ndarray):
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        success, corners = cv.findChessboardCorners(gray, self.__square_count__, None)
        if success:
            corners_sub = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.__criteria__)
            self.__2D_detected_points__.append(corners_sub)
            self.__3D_detected_points__.append(self.__3D_points__)
            self.__resolution__ = gray.shape[::-1]

            return True, corners_sub, img

        return False, None, None

    def draw_corners(self, corners, img) -> np.ndarray:
        img_copy = img.copy()
        cv.drawChessboardCorners(img_copy, self.__square_count__, corners, True)

        return img_copy

    def calibrate(self):
        return cv.calibrateCamera(self.__3D_detected_points__,
                                  self.__2D_detected_points__,
                                  self.__resolution__,
                                  None,
                                  None)
