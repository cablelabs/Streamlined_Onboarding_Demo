# Copyright (c) 2023 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed in accordance of the accompanied LICENSE.txt or LICENSE.md
# file in the base directory for this project. If none is supplied contact
# CableLabs for licensing terms of this software.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import os
import sys
from dotenv import load_dotenv
from PyQt5 import QtWidgets
from slined_onboarding.common import so_gpio
from slined_onboarding.lamp import LampUi

def lamp_main():
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
    window = LampUi(iface_name)
    so_gpio.gpio_setup()
    so_gpio.set_button(17, lambda x: window.toggle_qr_code())
    so_gpio.set_button(23, lambda x: window.toggle_lamp())
    if os.environ.get('ENV') == 'dev':
        so_gpio.set_button(27, lambda x: window.close())
        window.show()
    else:
        so_gpio.set_button(27, lambda x: os.system('sudo reboot'))
        window.showFullScreen()
    sys.exit(app.exec_())
