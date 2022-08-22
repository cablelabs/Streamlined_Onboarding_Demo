import logging
import ctypes
import pkg_resources
import os

class SWITCHSTATE(ctypes.Structure):
    _fields_ = [('state', ctypes.c_bool), ('discovered', ctypes.c_bool),
            ('error_state', ctypes.c_bool), ('error_message', ctypes.c_char_p)]

class SoDevice:
    def __init__(self, wpa_ctrl_iface, creds_dir='./sodevice_creds', state_update_cb=None, persist_creds=True):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing ctypes library for SO Device.')
        lib_path = pkg_resources.resource_filename('slined_onboarding', 'resources/libso.so')
        self.logger.debug('SO Device library path: {}'.format(lib_path))
        self.device = ctypes.CDLL(lib_path)
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

    def _update_state(self, switch_state):
        self.logger.debug('Discovered: {}'.format(switch_state.contents.discovered))
        self.logger.debug('State: {}'.format(switch_state.contents.state))

        self.light_state = switch_state.contents.state
        self.light_discovered = switch_state.contents.discovered
        if self._state_update_cb is not None:
            self._state_update_cb(self.light_discovered, self.light_state, switch_state.contents.error_state, switch_state.contents.error_message)

    def stop_main_loop(self):
        self.logger.debug('Signaling main event loop to exit')
        self.device.handle_signal(1)
        if not self._persist_creds:
            self.logger.debug('Removing credential files')
            for f in os.listdir(self._creds_dir):
                os.remove(os.path.join(self._creds_dir, f))
