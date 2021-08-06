import logging
import sys
from PyQt5 import QtWidgets

logging.basicConfig(format='%(levelname)s [%(name)s]: %(message)s', level=logging.DEBUG)

from slined_onboarding.gui import Ui_MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow, sys.argv[1])
    # MainWindow.showFullScreen()
    MainWindow.show()
    sys.exit(app.exec_())
