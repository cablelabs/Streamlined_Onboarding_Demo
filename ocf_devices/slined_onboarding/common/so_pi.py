# Copyright (c) 2023 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed in accordance of the accompanied LICENSE.txt or LICENSE.md
# file in the base directory for this project. If none is supplied contact
# CableLabs for licensing terms of this software.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import qrcode
import logging
import pkg_resources
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL.ImageQt import ImageQt
from .wpa_dpp_qr import get_dpp_uri, start_dpp_listen
from .so_img import SoImgLabel

class SoPiUi(QtWidgets.QMainWindow):
    def __init__(self, event_worker, iface_name):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.iface_name = iface_name
        self._off_img = QtGui.QPixmap(pkg_resources.resource_filename(__name__, 'images/off.png'))
        self._on_img = QtGui.QPixmap(pkg_resources.resource_filename(__name__, 'images/on.png'))
        self._set_qr_code()
        self._setupUi()

        self.event_worker = event_worker
        self.event_thread = QtCore.QThread()
        self.event_worker.moveToThread(self.event_thread)
        self.event_thread.started.connect(self.event_worker.run)

        self.event_worker.device_state.connect(self._state_update_ui)

    def toggle_qr_code(self):
        if self.qr_img is None:
            self.logger.error('QR image not generated.')
            self.append_output_text('No DPP QR code generated!')
            return

        if self.qr_code_shown:
            self.img_label.set_img(self._on_img if self.event_worker.ocf_device.light_state else self._off_img)
        else:
            self.img_label.set_img(QtGui.QPixmap.fromImage(self.qr_img))
            self.append_output_text('Scan the QR code!')
        self.qr_code_shown = not self.qr_code_shown

    def append_output_text(self, new_text):
        self.output_txt_label.setText(new_text)

    def showEvent(self, event):
        self.logger.debug('Starting main event loop...')
        self.event_thread.start()
        self.logger.debug('Done starting event loop?')
        event.accept()

    def closeEvent(self, event):
        self.logger.debug('Close event received; cleaning up')
        self.event_worker.stop()
        self.logger.debug('Stopped main loop')
        event.accept()

    def _set_qr_code(self):
        self.qr_img = None
        self.qr_code_shown = False
        try:
            dpp_uri = get_dpp_uri(self.iface_name)
            self.qr_img = ImageQt(qrcode.make(dpp_uri))
            listen_output = start_dpp_listen(self.iface_name)
            self.logger.debug('DPP listen init output: {}'.format(listen_output))
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
        if os.environ.get('ENV') != 'dev':
            self.centralwidget.setCursor(QtCore.Qt.BlankCursor)
        self.main_hz_layout = QtWidgets.QHBoxLayout(self.centralwidget)

    def _set_labels(self):
        self.label_layout = QtWidgets.QVBoxLayout()

        self.img_label = SoImgLabel(self._off_img)
        self.img_label.setGeometry(QtCore.QRect(5, 5, 210, 210))
        self.img_label.setObjectName("img_label")

        self.output_txt_label = QtWidgets.QLabel()
        self.output_txt_label.setStyleSheet('border: 1px solid gray')
        self.output_txt_label.setWordWrap(True)
        self.output_txt_label.setMaximumHeight(40)
        self.output_txt_label.setText('Streamlined Onboarding OCF Pi')

        self.label_layout.addWidget(self.img_label, 4)
        self.label_layout.addWidget(self.output_txt_label, 1)

        self.main_hz_layout.addLayout(self.label_layout, 3)

    def _set_buttons(self):
        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.qr_button = QtWidgets.QPushButton()
        self.qr_button.setObjectName("qr_button")
        self.button_layout.addWidget(self.qr_button)
        self.discover_button = QtWidgets.QPushButton()
        self.discover_button.setObjectName("discover_button")
        self.button_layout.addWidget(self.discover_button)
        self.toggle_button = QtWidgets.QPushButton()
        self.toggle_button.setObjectName("toggle_button")
        self.button_layout.addWidget(self.toggle_button)
        self.reboot_button = QtWidgets.QPushButton()
        self.reboot_button.setObjectName("reboot_button")
        self.button_layout.addWidget(self.reboot_button)
        self.main_hz_layout.addLayout(self.button_layout, 1)

        self.qr_button.clicked.connect(self.toggle_qr_code)
        if os.environ.get('ENV') == 'dev':
            self.reboot_button.clicked.connect(self.close)
        else:
            self.reboot_button.clicked.connect(lambda x: os.system('sudo reboot'))

    def _retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.qr_button.setText(_translate("MainWindow", "QR Code"))
        self.reboot_button.setText(_translate("MainWindow", "Reboot"))

    # Should be overridden by inheriting classes
    def _state_update_ui(self, device_state):
        print('Super class state update')
        pass
