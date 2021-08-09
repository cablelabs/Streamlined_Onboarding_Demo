import logging

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except:
    logger.warn('Failed to import RPi GPIO, falling back to mock GPIO')
    import Mock.GPIO as GPIO

class SoGpioContext:
    def __init__(self):
        self._gpio_setup()

    def _gpio_setup(self):
        GPIO.setmode(GPIO.BCM)

        # Backlight PWM
        GPIO.setup(18, GPIO.OUT)
        self.backlightOn = True
        self.backlight = GPIO.PWM(18, 1000)
        self.backlight.start(100)

    def set_button(self, pin, button_callback):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.RISING, button_callback, 300)

    def gpio_cleanup(self):
        logger.info('Cleaning up GPIO context')
        GPIO.cleanup()
