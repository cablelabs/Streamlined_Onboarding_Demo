import logging

from gpiozero import Button, PWMLED

class SoGpioContext:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._gpio_setup()
        self.button_map = dict()

    def _gpio_setup(self):
        # Backlight PWM
        self.backlight = PWMLED(18)
        self.backlightOn = True
        self.backlight.value = 1

    def set_button(self, pin, button_callback):
        self.logger.debug('Setting up button callback on pin {}'.format(pin))
        self.button_map.setdefault(pin, Button(pin, bounce_time=0.03)).when_pressed = button_callback
