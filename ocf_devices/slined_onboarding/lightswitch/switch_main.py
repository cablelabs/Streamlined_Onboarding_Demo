import logging
import os
import sys
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from slined_onboarding.lightswitch import switch_gui

def switch_main():
    logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.debug('Current directory is {}'.format(os.getcwd()))
    logger.debug('Loading environment vars from .env')
    load_dotenv()
    iface_name = os.environ.get('SO_IFACE')
    if iface_name is None:
        logger.error('Environment variable SO_IFACE not set - check configuration file.')
        sys.exit(1)
    logger.debug('Starting the GUI')
    app = QtWidgets.QApplication(sys.argv)
    window = gui.SoPiUi(iface_name)
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
