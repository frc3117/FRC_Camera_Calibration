import json
import cv2 as cv
import pyperclip
import argparse

from calibration import CameraCalibration
from frcwidget import OpencvImageWidget, OpencvVideoWidget

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QMessageBox


class JsonModal(QDialog):
    def __init__(self, json_str: str):
        super().__init__()

        self.json_str = json_str

        self.setWindowTitle('Calibration Results')

        self.json_text = QLabel(json_str)
        self.json_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.copy_to_clipboard_button = QPushButton('Save to clipboard')
        self.copy_to_clipboard_button.pressed.connect(self.copy_to_clipboard)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.json_text)
        self.main_layout.addWidget(self.copy_to_clipboard_button)
        self.setLayout(self.main_layout)

    def copy_to_clipboard(self):
        pyperclip.copy(self.json_str)

        dialog = QDialog()
        text = QLabel('Successfuly copied to clipboard!')
        ok_button = QPushButton('ok')
        ok_button.pressed.connect(dialog.close)

        layout = QVBoxLayout()
        layout.addWidget(text)
        layout.addWidget(ok_button)
        dialog.setLayout(layout)

        dialog.exec_()
        self.close()


class CalibrationWidget(QWidget):
    def __init__(self, src):
        super().__init__()

        self.preview_layout = QHBoxLayout()
        self.main_layout = QVBoxLayout()

        cap = cv.VideoCapture(src)
        self.camera_preview = OpencvVideoWidget(cap, resolution=(640, 640))
        self.detection_preview = OpencvImageWidget(resolution=(640, 640))

        self.preview_layout.addWidget(self.camera_preview)
        self.preview_layout.addWidget(self.detection_preview)

        self.sample_count = 0
        self.sample_count_text = QLabel('0 Samples')
        self.sample_count_text.setAlignment(Qt.AlignCenter)

        self.detection_button = QPushButton('Add to calibration')
        self.detection_button.pressed.connect(self.add_to_calibration)

        self.get_results_button = QPushButton('Get results')
        self.get_results_button.pressed.connect(self.get_results)

        self.main_layout.addLayout(self.preview_layout)
        self.main_layout.addWidget(self.sample_count_text)
        self.main_layout.addWidget(self.detection_button)
        self.main_layout.addWidget(self.get_results_button)
        self.setLayout(self.main_layout)

        self.calibration = CameraCalibration((7, 9))

    def add_to_calibration(self):
        last_frame = self.camera_preview.last_frame.copy()

        ret, corners, img = self.calibration.find_corners(last_frame)
        if ret:
            self.sample_count += 1

            self.sample_count_text.setText(f'{self.sample_count} Samples')
            self.detection_preview.set_image(self.calibration.draw_corners(corners, img))
        else:
            self.detection_preview.set_image(last_frame)

    def get_results(self):
        ret, mtx, dist, *_ = self.calibration.calibrate()

        self.camera_preview.set_calibration(mtx, dist)

        results_json = {
            'matrix': {
                'fx': mtx[0, 0],
                'fy': mtx[1, 1],
                'cx': mtx[0, 2],
                'cy': mtx[1, 2]
            },
            'distortionCoef': {
                'k1': dist[0, 0],
                'k2': dist[0, 1],
                'p1': dist[0, 2],
                'p2': dist[0, 3],
                'k3': dist[0, 4]
            }
        }

        str_json = json.dumps(results_json, indent=4)

        modal = JsonModal(str_json)
        modal.exec_()


class MainWindow(QMainWindow):
    def __init__(self, src):
        super().__init__()

        self.setWindowTitle('Camera Calibration')

        self.calibration_widget = CalibrationWidget(src)
        self.setCentralWidget(self.calibration_widget)


def main(src=0):
    app = QApplication([])

    window = MainWindow(src)
    window.show()

    # Start the event loop.
    app.exec_()

    snap = tracemalloc.take_snapshot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Camera Calibration Tool',
    )

    parser.add_argument('-s', '--src', action='store', default=0, metavar='camera source')
    args = parser.parse_args()

    main(args.src)
