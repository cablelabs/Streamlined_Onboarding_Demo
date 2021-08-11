import logging
import time
from slined_onboarding import SoSwitch

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Creating Streamlined Onboarding Switch')
    switch = SoSwitch('./libsoswitch.so')
    switch.start_main_event_loop()
    logger.info('This is in the main thread')
    switch.run()
    switch.stop_main_event_loop()
    logger.info('Done')
