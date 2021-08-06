import sys
from PyQt5 import QtWidgets
from slined_onboarding.gui import Ui_MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    # MainWindow.showFullScreen()
    MainWindow.show()
    sys.exit(app.exec_())

