import sys

from PySide6 import QtWidgets, QtCore
import qdarktheme

from rw_ui import Ui_MainWindow


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
        self.splitter_state = None
        self.splitter_2_state = None

        while True:
            self.window = MainWindow()
            self.splitter = self.window.ui.sidebar_splitter
            self.splitter_2 = self.window.ui.preview_splitter
            self.preview_stack = self.window.ui.preview_stack
            self.preview_page = self.window.ui.preview_page
            self.crop_page = self.window.ui.crop_page
            self.trim_page = self.window.ui.trim_page
            self.benchmark_page = self.window.ui.benchmark_page
            self.preview_toolbutton = self.window.ui.preview_toolbutton
            self.preview_toolbutton.clicked.connect(self.on_preview_toolbutton_clicked)
            self.trim_toolbutton = self.window.ui.trim_toolbutton
            self.trim_toolbutton.clicked.connect(self.on_trim_toolbutton_clicked)
            self.crop_toolbutton = self.window.ui.crop_toolbutton
            self.crop_toolbutton.clicked.connect(self.on_crop_toolbutton_clicked)
            self.benchmark_toolbutton = self.window.ui.benchmark_toolbutton
            self.benchmark_toolbutton.clicked.connect(self.on_benchmark_toolbutton_clicked)
            self.window.show()

            if self.window and self.window_state and self.window_geometry and self.splitter_state and self.splitter_2_state:
                self.window.restoreState(self.window_state)
                self.window.restoreGeometry(self.window_geometry)
                self.splitter.restoreState(self.splitter_state)
                self.splitter_2.restoreState(self.splitter_2_state)

            app.setStyleSheet(qdarktheme.load_stylesheet(border='sharp'))
            app.exec()

        sys.exit(0)

    def on_window_state_changed(self):
        self.window_state = self.window.saveState()
        self.window_geometry = self.window.saveGeometry()
        self.splitter_state = self.splitter.saveState()
        self.splitter_2_state = self.splitter_2.saveState()
        print('save state')

    def on_preview_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.preview_page)

    def on_trim_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.trim_page)

    def on_crop_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.crop_page)

    def on_benchmark_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.benchmark_page)


if __name__ == '__main__':
    app_loop = AppLoop()
