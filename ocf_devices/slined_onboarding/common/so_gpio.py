import logging

from gpiozero import Button, PWMLED

logger = logging.getLogger(__name__)
button_map = dict()

def gpio_setup():
    # Backlight PWM
    backlight = PWMLED(18)

def set_button(pin, button_callback):
    logger.debug('Setting up button callback on pin {}'.format(pin))
    button_map.setdefault(pin, Button(pin, bounce_time=0.03)).when_pressed = button_callback
