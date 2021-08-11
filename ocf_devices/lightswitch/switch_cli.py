import ctypes
import threading
import logging
import time

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)

def configure_lib(lib):
    lib.so_switch_init.argtypes = [ctypes.c_char_p]

def thread_function(lib):
    logger = logging.getLogger(__name__)
    ret = lib.so_switch_init(b'./lightswitch_creds')
    if ret == 0:
        lib.so_switch_main_loop()
    logger.info('Thread function exiting')

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    lib = ctypes.CDLL('./libsoswitch.so')
    configure_lib(lib)
    x = threading.Thread(target=thread_function, args=(lib,))
    logger.info('Going to star the thread now')
    x.start()
    logger.info('This is in the main thread')
    x.join()
    logger.info('Done')
