# Copyright 2022 Michael Gregory
#
# This file is part of Render Watch.
#
# Render Watch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Render Watch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.


from PySide6 import QtWidgets
import qdarktheme

from render_watch.ui.rw_ui import Ui_MainWindow
from render_watch.ui import main_window
from render_watch import app_preferences


class MainWindowOLD(QtWidgets.QMainWindow):
    def __init__(self, app_settings: app_preferences.Settings):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.splitter = self.ui.sidebar_splitter
        self.splitter_2 = self.ui.preview_splitter
        self.preview_stack = self.ui.preview_stack
        self.preview_page = self.ui.preview_page
        self.crop_page = self.ui.crop_page
        self.trim_page = self.ui.trim_page
        self.benchmark_page = self.ui.benchmark_page
        self.preview_toolbutton = self.ui.preview_toolbutton
        self.preview_toolbutton.clicked.connect(self.on_preview_toolbutton_clicked)
        self.trim_toolbutton = self.ui.trim_toolbutton
        self.trim_toolbutton.clicked.connect(self.on_trim_toolbutton_clicked)
        self.crop_toolbutton = self.ui.crop_toolbutton
        self.crop_toolbutton.clicked.connect(self.on_crop_toolbutton_clicked)
        self.benchmark_toolbutton = self.ui.benchmark_toolbutton
        self.benchmark_toolbutton.clicked.connect(self.on_benchmark_toolbutton_clicked)

        self.splitter.restoreState(app_settings.sidebar_splitter_state)
        self.splitter_2.restoreState(app_settings.preview_splitter_state)

    def on_preview_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.preview_page)

    def on_trim_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.trim_page)

    def on_crop_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.crop_page)

    def on_benchmark_toolbutton_clicked(self):
        self.preview_stack.setCurrentWidget(self.benchmark_page)


class Application:
    def __init__(self, app_settings: app_preferences.Settings):
        self.app_settings = app_settings
        self.app = QtWidgets.QApplication([])
        self.window = main_window.MainWindow(app_settings)

    def start_application(self):
        self.window.show()
        self.window.restoreState(self.app_settings.app_window_state)
        self.window.restoreGeometry(self.app_settings.app_window_geometry)

        self.app.aboutToQuit.connect(self.on_application_closing)
        self.app.setStyleSheet(qdarktheme.load_stylesheet(border='sharp'))

        return self.app.exec()

    def on_application_closing(self):
        self.app_settings.app_window_state = self.window.saveState()
        self.app_settings.app_window_geometry = self.window.saveGeometry()
        self.app_settings.sidebar_splitter_state = self.window.side_bar_splitter.saveState()
        self.app_settings.preview_splitter_state = self.window.preview_splitter.saveState()
        self.app_settings.is_encoding_parallel_tasks = self.window.parallel_tasks_action.isChecked()
        self.app_settings.is_auto_cropping_inputs = self.window.auto_crop_inputs_action.isChecked()

        self.app_settings.save()
