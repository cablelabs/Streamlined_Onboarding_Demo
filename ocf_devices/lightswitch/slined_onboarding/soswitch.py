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
        self.soswitch.so_switch_init.argtypes = [ctypes.c_char_p]

    def main_event_loop(self):
        self.lock.acquire()
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.soswitch.so_switch_init(b'./lightswitch_creds')
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
        pass

    def toggle_light(self):
        if not self.light_discovered:
            self.logger.error('Light not yet discovered')
            return
