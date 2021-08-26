import logging
import ctypes
import threading

class SWITCHSTATE(ctypes.Structure):
    _fields_ = [('state', ctypes.c_bool), ('discovered', ctypes.c_bool),
            ('error_state', ctypes.c_bool), ('error_message', ctypes.c_char_p)]

class SoSwitch:
    def __init__(self, soswitch_lib_path, so_config_path, state_update_cb=None):
        self.logger = logging.getLogger(__name__)
        self.soswitch = ctypes.CDLL(soswitch_lib_path)
        self._configure_lib()

        self.light_state = False
        self.light_discovered = False

        self.event_thread = threading.Thread(target=self.main_event_loop)
        self.lock = threading.Lock()

        self._so_config_path = so_config_path
        self._state_update_cb = state_update_cb

    def _configure_lib(self):
        self._state_cb_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(SWITCHSTATE))
        self._state_cb = self._state_cb_type(self._update_state)
        self.soswitch.so_switch_init.argtypes = [ctypes.c_char_p, ctypes.c_char_p, self._state_cb_type]

    def _update_state(self, switch_state):
        self.lock.acquire()
        self.logger.debug('Update state called')
        self.logger.debug('Switch State is {}'.format(switch_state.contents))
        self.logger.debug('Discovered: {}'.format(switch_state.contents.discovered))
        self.logger.debug('State: {}'.format(switch_state.contents.state))

        self.light_state = switch_state.contents.state
        self.light_discovered = switch_state.contents.discovered
        if self._state_update_cb is not None:
            self._state_update_cb(self.light_discovered, self.light_state, switch_state.contents.error_state, switch_state.contents.error_message)
        self.lock.release()

    def main_event_loop(self):
        self.lock.acquire()
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.soswitch.so_switch_init(b'./lightswitch_creds', self._so_config_path.encode('utf8'), self._state_cb)
        self.lock.release()
        self.soswitch.so_switch_main_loop()
        self.logger.debug('Main event loop finished')

    def start_main_loop(self):
        self.event_thread.start()

    def stop_main_loop(self):
        self.lock.acquire()
        self.logger.debug('Signaling main event loop to exit')
        self.soswitch.handle_signal(1)
        self.event_thread.join()
        self.lock.release()

    def discover_light(self):
        self.lock.acquire()
        self.soswitch.discover_light()
        self.lock.release()

    def toggle_light(self):
        self.lock.acquire()
        self.logger.debug('Lock acquired, attempting to toggle light resource.')
        if not self.light_discovered:
            self.logger.error('Light not yet discovered')
        self.soswitch.toggle_light()
        self.logger.debug('Done calling toggle_light')
        self.lock.release()
