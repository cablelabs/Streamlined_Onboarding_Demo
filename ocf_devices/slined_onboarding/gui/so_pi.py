import qrcode
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from slined_onboarding import get_dpp_uri

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except:
    logger.warn('Failed to import RPi GPIO, falling back to mock GPIO')
    import Mock.GPIO as GPIO

class Ui_MainWindow():
    def __init__(self, MainWindow, iface_name):
        self.iface_name = iface_name
        self.qr_img = None
        # self.qr_img = ImageQt(qrcode.make(raw_uri))
        self._setupUi(MainWindow)

    def _set_widgets(self):
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setCursor(QtCore.Qt.BlankCursor)

        self.qr_widget = QtWidgets.QWidget(self.centralwidget)
        self.qr_widget.setGeometry(QtCore.QRect(5, 5, 210, 210))
        self.qr_widget.setObjectName("qr_widget")

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(220, 10, 95, 221))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

    def _set_buttons(self):
        self.button_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setObjectName("button_layout")
        self.qr_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.qr_button.setObjectName("qr_button")
        self.button_layout.addWidget(self.qr_button)
        self.reset_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.reset_button.setObjectName("reset_button")
        self.button_layout.addWidget(self.reset_button)
        self.toggle_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.toggle_button.setObjectName("toggle_button")
        self.button_layout.addWidget(self.toggle_button)
        self.reboot_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.reboot_button.setObjectName("reboot_button")
        self.button_layout.addWidget(self.reboot_button)
        self.qr_button.clicked.connect(self._toggle_qr_code)

    def _setup_qr_code(self):
        self.qr_code = QtWidgets.QLabel(self.qr_widget)
        self.qr_code.setGeometry(QtCore.QRect(5, 5, 210, 210))
        self.qr_code.setText("")
        # self.qr_code.setPixmap(QtGui.QPixmap.fromImage(self.qr_img))
        self.qr_code.setScaledContents(True)
        self.qr_code.setObjectName("qr_code")
        self.qr_code.hide()

    def _toggle_qr_code(self):
        if self.qr_img is None:
            try:
                dpp_uri = get_dpp_uri(self.iface_name)
                self.qr_img = ImageQt(qrcode.make(dpp_uri))
            except:
                logger.error('Failed to fetch/generate DPP URI')
                return
            self.qr_code.setPixmap(QtGui.QPixmap.fromImage(self.qr_img))


        if self.qr_code_shown:
            self.qr_code.hide()
        else:
            self.qr_code.show()

        self.qr_code_shown = not self.qr_code_shown

    def _setupUi(self, MainWindow):
        self.qr_code_shown = False
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(320, 240)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self._set_widgets()
        self._set_buttons()
        self._setup_qr_code()
        MainWindow.setCentralWidget(self.centralwidget)

        self._retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.qr_button.setText(_translate("MainWindow", "QR Code"))
        self.reset_button.setText(_translate("MainWindow", "RESET"))
        self.toggle_button.setText(_translate("MainWindow", "Toggle"))
        self.reboot_button.setText(_translate("MainWindow", "Reboot"))
