import os
import sys
import logging
import click
import threading
from dotenv import load_dotenv
from slined_onboarding import SoSwitch

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
    _display_menu()
    selection = click.prompt('Choose an option', type=int)
    _process_selection(selection)

def run_cli():
    switch.start_main_loop()
    while not quit_event.is_set():
        _user_prompt()
    switch.stop_main_loop()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    load_dotenv()
    if os.environ.get('SO_CONFIG_PATH') is None:
        logger.error('SO_CONFIG_PATH variable not set!')
        sys.exit(-1)
    switch = SoSwitch('./libsoswitch.so', os.environ.get('SO_CONFIG_PATH'))
    quit_event = threading.Event()
    run_cli()
