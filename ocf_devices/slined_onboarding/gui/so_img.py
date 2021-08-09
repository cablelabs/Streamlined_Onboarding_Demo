import logging
from PyQt5 import QtWidgets, QtCore

logger = logging.getLogger(__name__)

class SoImgLabel(QtWidgets.QLabel):
    def __init__(self, img):
        super().__init__()
        self.img = img

    def set_img(self, img):
        self.img = img
        self._scale_img()

    def resizeEvent(self, event):
        self._scale_img()

    def _scale_img(self):
        if self.img is None:
            return
        self.setPixmap(self.img.scaled(self.size(), QtCore.Qt.KeepAspectRatio))
