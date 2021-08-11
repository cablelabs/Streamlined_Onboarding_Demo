import logging
import click
import threading
from slined_onboarding import SoSwitch

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

switch = SoSwitch('./libsoswitch.so')
quit_event = threading.Event()

def _display_menu():
    menu_str = ('\n1: Discover Light\n'
    '2: Toggle Light State\n'
    '9: Exit\n')
    print(menu_str)

def _process_selection(selection):
    if selection == 1:
        switch.discover_light()
    if selection == 2:
        switch.toggle_light()
    if selection == 9:
        logger.debug('Exit called')
        quit_event.set()

def _user_prompt():
    switch.lock.acquire()
    _display_menu()
    selection = click.prompt('Choose an option', type=int)
    _process_selection(selection)
    switch.lock.release()

def run_cli():
    switch.start_main_loop()
    while not quit_event.is_set():
        _user_prompt()
    switch.stop_main_loop()

if __name__ == '__main__':
    run_cli()
