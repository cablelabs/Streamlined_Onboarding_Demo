import os
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from slined_onboarding import SoSwitch

class SwitchWorker(QObject):
    device_state = pyqtSignal(tuple)
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.switch = SoSwitch(os.environ.get('WPA_CTRL_IFACE'), self._state_update)

    def run(self):
        self.logger.debug('Thread run called')
        self.switch.main_event_loop()

    def _state_update(self, discovered, state, error_state, error_message):
        self.logger.debug('State update called...')
        self.logger.debug('Current state: discovered {}, state {} error_state {} error_message {}'.format(discovered, state, error_state, error_message))
        self.device_state.emit((discovered, state, error_state, error_message))

