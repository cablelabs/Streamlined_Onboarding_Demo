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

from gpiozero import Button, PWMLED, LED

logger = logging.getLogger(__name__)
button_map = dict()
led_map = dict()

def gpio_setup():
    # Backlight PWM
    backlight = PWMLED(18)
    led_map[4] = LED(4)

def set_button(pin, button_callback):
    logger.debug('Setting up button callback on pin {}'.format(pin))
    button_map.setdefault(pin, Button(pin, bounce_time=0.03)).when_pressed = button_callback

def set_pin_value(pin, value):
    toggle_pin = led_map.get(pin)
    if toggle_pin:
        logger.debug('Setting pin {} to value {}'.format(pin, 'on' if value else 'off'))
        toggle_pin.on() if value else toggle_pin.off()
