import logging
import os
import sys
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from slined_onboarding import gui

def gui_main():
    logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.debug('Current directory is {}'.format(os.getcwd()))
    logger.debug('Loading environment vars from .env')
    load_dotenv('./.env')
    logger.debug('Starting the GUI')
    app = QtWidgets.QApplication(sys.argv)
    window = gui.SoPiUi(sys.argv[1])
    gpio_context = gui.SoGpioContext()
    gpio_context.set_button(17, lambda x: window.toggle_qr_code())
    gpio_context.set_button(22, lambda x: window.discover_light())
    gpio_context.set_button(23, lambda x: window.toggle_switch())
    if os.environ.get('ENV') == 'dev':
        gpio_context.set_button(27, lambda x: window.close())
        window.show()
    else:
        gpio_context.set_button(27, lambda x: os.system('sudo reboot'))
        window.showFullScreen()
    sys.exit(app.exec_())
