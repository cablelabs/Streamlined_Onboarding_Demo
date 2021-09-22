import qrcode
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from slined_onboarding import get_dpp_uri
from .so_img import SoImgLabel
from .switch_worker import SwitchWorker

class SoPiUi(QtWidgets.QMainWindow):
    def __init__(self, iface_name):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.iface_name = iface_name
        self.output_text = list()
        self._set_qr_code()
        self._setupUi()
        self._off_img = QtGui.QPixmap('./off.png')
        self._on_img = QtGui.QPixmap('./on.png')

        self.event_worker = SwitchWorker()
        self.event_thread = QtCore.QThread()
        self.event_worker.moveToThread(self.event_thread)
        self.event_thread.started.connect(self.event_worker.run)

        self.event_worker.device_state.connect(self._state_update)

    def toggle_qr_code(self):
        if self.qr_img is None:
            self.logger.error('QR image not generated.')
            self.append_output_text('No DPP QR code generated!')
            return

        if self.qr_code_shown:
            self.img_label.set_img(self._on_img if self.event_worker.switch.light_state else self._off_img)
        else:
            self.img_label.set_img(QtGui.QPixmap.fromImage(self.qr_img))
            self.append_output_text('Scan the QR code!')
        self.qr_code_shown = not self.qr_code_shown

    def toggle_switch(self):
        self.logger.debug('Toggle button pressed')
        if self.qr_code_shown:
            self.toggle_qr_code()

        if not self.event_worker.switch.light_discovered:
            self.logger.error('Light not discovered!')
            self.append_output_text('Light not discovered')
        else:
            self.logger.debug('Toggling light')
            self.event_worker.switch.toggle_light()

        self.toggle_button.setEnabled(False)

    def append_output_text(self, new_text):
        self.output_text.append(new_text)
        self.output_txt_label.setText('\n'.join(self.output_text))

    def showEvent(self, event):
        self.logger.debug('Starting main switch event loop...')
        self.event_thread.start()
        self.logger.debug('Done starting event loop?')
        event.accept()

    def closeEvent(self, event):
        self.logger.debug('Close event received; cleaning up')
        self.event_worker.switch.stop_main_loop()
        self.logger.debug('Stopped main loop')
        event.accept()

    def _set_qr_code(self):
        self.qr_img = None
        self.qr_code_shown = False
        try:
            dpp_uri = get_dpp_uri(self.iface_name)
            self.qr_img = ImageQt(qrcode.make(dpp_uri))
        except:
            self.logger.error('Failed to fetch/generate DPP URI')

    def _setupUi(self):
        self.setObjectName("MainWindow")
        self.setMinimumSize(QtCore.QSize(320, 240))
        self.resize(320, 240)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self._set_main_widget()
        self._set_labels()
        self._set_buttons()
        self.setCentralWidget(self.centralwidget)

        self._retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def _set_main_widget(self):
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setCursor(QtCore.Qt.BlankCursor)
        self.main_hz_layout = QtWidgets.QHBoxLayout(self.centralwidget)

    def _set_labels(self):
        self.label_layout = QtWidgets.QVBoxLayout()

        self.img_label = SoImgLabel()
        self.img_label.setGeometry(QtCore.QRect(5, 5, 210, 210))
        self.img_label.setObjectName("img_label")

        self.output_txt_label = QtWidgets.QLabel()
        self.output_txt_label.setStyleSheet('border: 1px solid gray')
        self.output_txt_label.setWordWrap(True)
        self.output_txt_label.setMaximumHeight(40)
        self.output_txt_label.setText('Streamlined Onboarding OCF Pi Switch')

        self.label_layout.addWidget(self.img_label, 4)
        self.label_layout.addWidget(self.output_txt_label, 1)

        self.main_hz_layout.addLayout(self.label_layout, 3)

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
        self.toggle_button.clicked.connect(self.toggle_switch)
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

    def _state_update(self, device_state):
        (discovered, state, error_state, error_message) = device_state
        self.logger.debug('State update called...')
        self.logger.debug('Current state: discovered {}, state {} error_state {} error_message {}'.format(discovered, state, error_state, error_message))
        if error_state:
            self.logger.error('Error flag set')
            error_text = '<font color="red">{}</font>\n'.format(error_message.decode('ascii'))
            self.append_output_text(error_text)
        if not discovered:
            return
        self.toggle_button.setEnabled(True)
        self.img_label.set_img(self._on_img if state else self._off_img)
