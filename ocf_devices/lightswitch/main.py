import logging
import sys
from slined_onboarding import gui_main

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)
    sys.exit(gui_main())
