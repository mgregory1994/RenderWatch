import sys

import qdarktheme
from PySide6 import QtWidgets, QtCore

from untitled import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class AppLoop:
    def __init__(self):
        app = QtWidgets.QApplication([])
        app.aboutToQuit.connect(self.on_window_state_changed)
        self.window_state = None
        self.window_geometry = None
        self.window = None

        while True:
            self.window = MainWindow()
            self.button = self.window.ui.pushButton_2
            self.window.show()

            if self.window and self.window_state and self.window_geometry:
                self.window.restoreState(self.window_state)
                self.window.restoreGeometry(self.window_geometry)

            # self.button.clicked.connect(self.on_window_state_changed)
            app.setStyleSheet(qdarktheme.load_stylesheet(border='sharp'))
            app.exec()

        sys.exit(0)

    def on_window_state_changed(self):
        self.window_state = self.window.saveState()
        self.window_geometry = self.window.saveGeometry()
        print('save state')


if __name__ == '__main__':
    app_loop = AppLoop()

