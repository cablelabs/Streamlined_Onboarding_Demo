import logging
import ctypes
import threading

class SoSwitch:
    def __init__(self, soswitch_lib_path):
        self.logger = logging.getLogger(__name__)
        self.soswitch = ctypes.CDLL(soswitch_lib_path)
        self._configure_lib()
        self.light_state = None
        self.light_discovered = False

        self.event_thread = threading.Thread(target=self.main_event_loop)
        self.lock = threading.Lock()

    def _configure_lib(self):
        self._state_cb_type = ctypes.CFUNCTYPE(None)
        self._state_cb = self._state_cb_type(self._update_state)
        self.soswitch.so_switch_init.argtypes = [ctypes.c_char_p, self._state_cb_type]

    def _update_state(self):
        self.lock.acquire()
        self.logger.debug('Update state called')
        self.lock.release()

    def main_event_loop(self):
        self.lock.acquire()
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.soswitch.so_switch_init(b'./lightswitch_creds', self._state_cb)
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
        if not self.light_discovered:
            self.logger.error('Light not yet discovered')
            return
        self.lock.release()
