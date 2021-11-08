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
    '3: Display DPP URI\n'
    '9: Exit\n')
    print(menu_str)

def state_update_print(discovered, state, error_state, error_message):
    cli_cv.acquire()
    if error_state is True:
        print('IoTivity-Lite Error: {}'.format(error_message.decode('ascii')))
    state_str = '\nLight discovered: {}\nLight state: {}'.format(discovered, 'N/A' if not discovered else state)
    print('\nCurrent light state:{}'.format(state_str))
    cli_cv.notify()
    cli_cv.release()

def _process_selection(selection):
    if selection == 1:
        switch.discover_light()
    if selection == 2:
        switch.toggle_light()
    if selection == 9:
        logger.debug('Exit called')
        quit_event.set()

def _user_prompt():
    cli_cv.acquire()
    if not cli_cv.wait(timeout=1.0):
        logger.debug('Wait for state update timed out')
    _display_menu()
    selection = click.prompt('Choose an option', type=int)
    _process_selection(selection)
    cli_cv.release()

def run_cli():
    while not quit_event.is_set():
        _user_prompt()
    switch.stop_main_loop()
    event_thread.join()

if __name__ == '__main__':
    # logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
    logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)
    load_dotenv()
    cli_cv = threading.Condition()
    wpa_ctrl_iface = os.environ.get('WPA_CTRL_IFACE')
    if wpa_ctrl_iface is None:
        logger.error('WPA_CTRL_IFACE variable not set!')
        sys.exit(-1)
    switch = SoSwitch(wpa_ctrl_iface, creds_dir=os.environ.get('SO_LIGHTSWITCH_CREDS'), state_update_cb=state_update_print)
    quit_event = threading.Event()
    event_thread = threading.Thread(target=switch.main_event_loop)
    event_thread.start()
    run_cli()
