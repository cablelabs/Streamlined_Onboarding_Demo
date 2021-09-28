import logging
import os
import sys
from dotenv import load_dotenv
from PyQt5 import QtWidgets

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)

from slined_onboarding import gui

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.debug('Loading environment vars from .env')
    load_dotenv()
    logger.debug('Starting the GUI')
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    window = gui.SoPiUi(sys.argv[1])
    gpio_context = gui.SoGpioContext()
    gpio_context.set_button(17, lambda x: window.toggle_qr_code())
    gpio_context.set_button(22, lambda x: window.discover_light())
    gpio_context.set_button(23, lambda x: window.toggle_light())
    if os.environ.get('ENV') == 'debug':
        gpio_context.set_button(27, lambda x: window.close())
    else:
        gpio_context.set_button(27, lambda x: os.system('sudo reboot'))
    window.show()
    # window.showFullScreen()
    sys.exit(app.exec_())
