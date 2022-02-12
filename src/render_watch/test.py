import sys

from PyQt5 import QtCore, QtWidgets, QtGui, uic

from render_watch import get_rw_ui, rw_ui
# from rw_ui import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        ui = rw_ui.Ui_MainWindow()
        ui.setupUi(self)


def main():
    app = QtWidgets.QApplication([])
    #app.setStyle('Windows')

    window = MainWindow()
    window.show()

    print(get_rw_ui())

    sys.exit(app.exec_())
