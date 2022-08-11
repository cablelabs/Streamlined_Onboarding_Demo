import logging
import os
from slined_onboarding.common import SoPiUi
from PyQt5.QtCore import QCoreApplication, QObject, pyqtSignal
from slined_onboarding.lightswitch import SoSwitch

class SwitchUi(SoPiUi):
    def __init__(self, iface_name):
        super().__init__(SwitchWorker(), iface_name)

    def discover_light(self):
        self.logger.debug('Discover light called')
        if self.event_worker.ocf_device.light_discovered:
            return
        self.event_worker.ocf_device.discover_light()

    def toggle_switch(self):
        self.logger.debug('Toggle button pressed')
        if self.qr_code_shown:
            self.toggle_qr_code()

        if not self.event_worker.ocf_device.light_discovered:
            self.logger.error('Light not discovered!')
            self.append_output_text('Light not discovered')
        else:
            self.logger.debug('Toggling light')
            self.event_worker.ocf_device.toggle_light()

        self.toggle_button.setEnabled(False)

    def _state_update_ui(self, device_state):
        (discovered, state, error_state, error_message) = device_state
        self.logger.debug('State update called...')
        self.logger.debug('Current state: discovered {}, state {} error_state {} error_message {}'.format(discovered, state, error_state, error_message))
        if error_state:
            self.logger.error('Error flag set')
            error_text = '<font color="red">{}</font>'.format(error_message.decode('ascii'))
            self.append_output_text(error_text)
        if not discovered:
            return
        self.toggle_button.setEnabled(True)
        self.img_label.set_img(self._on_img if state else self._off_img)

    def _set_buttons(self):
        super()._set_buttons()
        self.discover_button.clicked.connect(self.discover_light)
        self.toggle_button.clicked.connect(self.toggle_switch)
        self.toggle_button.setEnabled(False)

    def _retranslateUi(self):
        super()._retranslateUi()
        _translate = QCoreApplication.translate
        self.discover_button.setText(_translate("MainWindow", "Discover Light"))
        self.toggle_button.setText(_translate("MainWindow", "Toggle"))

class SwitchWorker(QObject):
    device_state = pyqtSignal(tuple)
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ocf_device = SoSwitch(os.environ.get('WPA_CTRL_IFACE'), os.environ.get('SO_LIGHTSWITCH_CREDS'), self._state_update, os.environ.get('SO_PERSIST_CREDS'))

    def run(self):
        self.logger.debug('Thread run called')
        self.ocf_device.main_event_loop()

    def stop(self):
        self.logger.debug('Stopping switch worker')
        self.ocf_device.stop_main_loop()

    def _state_update(self, discovered, state, error_state, error_message):
        self.logger.debug('State update called...')
        self.logger.debug('Current state: discovered {}, state {} error_state {} error_message {}'.format(discovered, state, error_state, error_message))
        self.device_state.emit((discovered, state, error_state, error_message))
