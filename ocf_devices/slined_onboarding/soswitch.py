import logging
import ctypes
import pkg_resources
import os

class SWITCHSTATE(ctypes.Structure):
    _fields_ = [('state', ctypes.c_bool), ('discovered', ctypes.c_bool),
            ('error_state', ctypes.c_bool), ('error_message', ctypes.c_char_p)]

class SoSwitch:
    def __init__(self, wpa_ctrl_iface, creds_dir='./lightswitch_creds', state_update_cb=None, persist_creds=True):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing ctypes library for soswitch.')
        lib_path = pkg_resources.resource_filename(__name__, 'resources/libsoswitch.so')
        self.logger.debug('So Switch library path: {}'.format(lib_path))
        self.soswitch = ctypes.CDLL(lib_path)
        self._configure_lib()

        self.light_state = False
        self.light_discovered = False

        self._wpa_ctrl_iface = wpa_ctrl_iface
        self._creds_dir = creds_dir
        self._state_update_cb = state_update_cb
        self._persist_creds = persist_creds

    def _configure_lib(self):
        self._state_cb_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(SWITCHSTATE))
        self._state_cb = self._state_cb_type(self._update_state)
        self.soswitch.so_switch_init.argtypes = [ctypes.c_char_p, ctypes.c_char_p, self._state_cb_type]

    def _update_state(self, switch_state):
        self.logger.debug('Discovered: {}'.format(switch_state.contents.discovered))
        self.logger.debug('State: {}'.format(switch_state.contents.state))

        self.light_state = switch_state.contents.state
        self.light_discovered = switch_state.contents.discovered
        if self._state_update_cb is not None:
            self._state_update_cb(self.light_discovered, self.light_state, switch_state.contents.error_state, switch_state.contents.error_message)

    def main_event_loop(self):
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.soswitch.so_switch_init(self._creds_dir.encode('utf8'), self._wpa_ctrl_iface.encode('utf8'), self._state_cb)
        self.soswitch.so_switch_main_loop()
        self.logger.debug('Main event loop finished')

    def stop_main_loop(self):
        self.logger.debug('Signaling main event loop to exit')
        self.soswitch.handle_signal(1)
        if not self._persist_creds:
            self.logger.debug('Removing credential files')
            for f in os.listdir(self._creds_dir):
                os.remove(os.path.join(self._creds_dir, f))

    def discover_light(self):
        self.soswitch.discover_light()

    def toggle_light(self):
        self.logger.debug('Attempting to toggle light resource.')
        if not self.light_discovered:
            self.logger.error('Light not yet discovered')
        else:
            self.soswitch.toggle_light()
            self.logger.debug('Done calling toggle_light')
