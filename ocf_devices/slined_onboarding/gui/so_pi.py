import qrcode
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from slined_onboarding import get_dpp_uri
from .so_img import SoImgLabel

logger = logging.getLogger(__name__)

class SoPiUi(QtWidgets.QMainWindow):
    def __init__(self, iface_name):
        super().__init__()
        self.iface_name = iface_name
        self._set_qr_code()
        self._setupUi()

    def toggle_qr_code(self):
        if self.qr_img is None:
            logger.error('QR image not generated.')
            return

        if self.qr_code_shown:
            self.img_label.set_img(None)
        else:
            self.img_label.set_img(QtGui.QPixmap.fromImage(self.qr_img))
        self.qr_code_shown = not self.qr_code_shown

    def _set_qr_code(self):
        self.qr_code_shown = False
        try:
            dpp_uri = get_dpp_uri(self.iface_name)
            self.qr_img = ImageQt(qrcode.make(dpp_uri))
        except:
            logger.error('Failed to fetch/generate DPP URI')

    def _setupUi(self):
        self.setObjectName("MainWindow")
        self.setMinimumSize(QtCore.QSize(320, 240))
        self.resize(320, 240)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self._set_main_widget()
        self._set_img_label()
        self._set_buttons()
        self.setCentralWidget(self.centralwidget)

        self._retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def _set_main_widget(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setCursor(QtCore.Qt.BlankCursor)
        self.main_hz_layout = QtWidgets.QHBoxLayout(self.centralwidget)

    def _set_img_label(self):
        self.img_label = SoImgLabel(None)
        self.img_label.setGeometry(QtCore.QRect(5, 5, 210, 210))
        self.img_label.setObjectName("img_label")
        self.main_hz_layout.addWidget(self.img_label, 3)

    def _set_buttons(self):
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.qr_button = QtWidgets.QPushButton()
        self.qr_button.setObjectName("qr_button")
        self.button_layout.addWidget(self.qr_button)
        self.reset_button = QtWidgets.QPushButton()
        self.reset_button.setObjectName("reset_button")
        self.button_layout.addWidget(self.reset_button)
        self.toggle_button = QtWidgets.QPushButton()
        self.toggle_button.setObjectName("toggle_button")
        self.button_layout.addWidget(self.toggle_button)
        self.reboot_button = QtWidgets.QPushButton()
        self.reboot_button.setObjectName("reboot_button")
        self.button_layout.addWidget(self.reboot_button)

        self.qr_button.clicked.connect(self.toggle_qr_code)
        self.reboot_button.clicked.connect(self.close)

        self.toggle_button.setEnabled(False)
        self.reset_button.setEnabled(False)

        self.main_hz_layout.addLayout(self.button_layout, 1)

    def _retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.qr_button.setText(_translate("MainWindow", "QR Code"))
        self.reset_button.setText(_translate("MainWindow", "RESET"))
        self.toggle_button.setText(_translate("MainWindow", "Toggle"))
        self.reboot_button.setText(_translate("MainWindow", "Reboot"))
