import ctypes
from slined_onboarding.common import SoDevice

class SoLamp(SoDevice):
    def __init__(self, wpa_ctrl_iface, creds_dir='./lamp_creds', state_update_cb=None, persist_creds=True):
        super().__init__(wpa_ctrl_iface, creds_dir, state_update_cb, persist_creds)

    def _configure_lib(self):
        super()._configure_lib()
        self.device.so_lamp_init.argtypes = [ctypes.c_char_p, ctypes.c_char_p, self._state_cb_type]

    def main_event_loop(self):
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.device.so_lamp_init(self._creds_dir.encode('utf8'), self._wpa_ctrl_iface.encode('utf8'), self._state_cb)
        self.device.so_main_loop()
        self.logger.debug('Main event loop finished')

    def toggle_lamp(self):
        self.light_state = !self.light_state
        self.device.set_state(self.light_state)
