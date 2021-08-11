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
        self.event_thread_lock.acquire()
        self.logger.debug('Invoking main IoTivity-Lite event loop')
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
        if selection == 1:
            self.discover_light()
        if selection == 2:
            self.toggle_light()
        if selection == 9:
            self.logger.debug('Exit called')
            self.quit_event.set()

    def _user_prompt(self):
        self.event_thread_lock.acquire()
        self._display_menu()
        selection = click.prompt('Choose an option', type=int)
        self._process_selection(selection)
        self.event_thread_lock.release()

    def discover_light(self):
        pass

    def toggle_light(self):
        if not self.light_discovered:
            self.logger.error('Light not yet discovered')
            return

    def run_cli(self):
        self.event_thread.start()
        while not self.quit_event.is_set():
            self._user_prompt()
        self.soswitch.handle_signal(1)
        self.event_thread.join()
