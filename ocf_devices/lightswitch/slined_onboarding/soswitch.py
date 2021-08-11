import click
import ctypes
import logging
import threading

class SoSwitch:
    def __init__(self, soswitch_lib_path):
        self.logger = logging.getLogger(__name__)
        self.soswitch = ctypes.CDLL(soswitch_lib_path)
        self._configure_lib()
        self.light_state = None
        self.light_discovered = False

        self.event_thread = threading.Thread(target=self._main_event_loop)
        self.event_thread_lock = threading.Lock()
        self.quit_event = threading.Event()

    def _configure_lib(self):
        self.soswitch.so_switch_init.argtypes = [ctypes.c_char_p]

    def _main_event_loop(self):
        self.logger.debug('Invoking main IoTivity-Lite event loop')
        self.event_thread_lock.acquire()
        self.soswitch.so_switch_init(b'./lightswitch_creds')
        self.event_thread_lock.release()
        self.soswitch.so_switch_main_loop()
        self.logger.debug('Thread function exiting')

    def _display_menu(self):
        menu_str = ('\n1: Discover Light\n'
        '2: Toggle Light State\n'
        '9: Exit\n')
        print(menu_str)

    def _process_selection(self, selection):
        if selection == 9:
            self.logger.debug('Exit called')
            self.quit_event.set()

    def _user_prompt(self):
        self.event_thread_lock.acquire()
        self._display_menu()
        selection = click.prompt('Choose an option', type=int)
        self._process_selection(selection)
        self.event_thread_lock.release()

    def start_main_event_loop(self):
        self.event_thread.start()

    def stop_main_event_loop(self):
        self.soswitch.handle_signal(1)
        self.event_thread.join()

    def run(self):
        while not self.quit_event.is_set():
            self._user_prompt()
