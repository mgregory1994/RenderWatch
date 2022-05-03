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


from PySide6 import QtWidgets, QtGui

from render_watch.ui.rw_ui import Ui_MainWindow
from render_watch.ui.rw_settings_dialog import Ui_SettingsDialog
from render_watch.ui.rw_about_dialog import Ui_AboutDialog

from render_watch import app_preferences


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_settings: app_preferences.Settings):
        super(MainWindow, self).__init__()

        self.app_settings = app_settings
        self.main_window_ui = Ui_MainWindow()
        self.main_window_ui.setupUi(self)

        self._setup_widgets()
        self._setup_signals()

    def _setup_widgets(self):
        self._setup_splitters()
        self._setup_actions()
        self._setup_preferences_dialog()
        self._setup_about_dialog()
        # Other ui classes go here

    def _setup_splitters(self):
        self.side_bar_splitter = self.main_window_ui.sidebar_splitter
        self.preview_splitter = self.main_window_ui.preview_splitter

        self.side_bar_splitter.restoreState(self.app_settings.sidebar_splitter_state)
        self.preview_splitter.restoreState(self.app_settings.preview_splitter_state)

    def _setup_actions(self):
        self.standard_tasks_action = self.main_window_ui.standard_tasks_action
        self.parallel_tasks_action = self.main_window_ui.parallel_tasks_action
        self.auto_crop_inputs_action = self.main_window_ui.auto_crop_inputs_action
        self.preferences_action = self.main_window_ui.preferences_action
        self.about_render_watch_action = self.main_window_ui.about_render_watch_action

        self.encoder_action_group = QtGui.QActionGroup(self)
        self.encoder_action_group.addAction(self.main_window_ui.standard_tasks_action)
        self.encoder_action_group.addAction(self.main_window_ui.parallel_tasks_action)
        self.encoder_action_group.setExclusive(True)

        self.auto_crop_inputs_action.setChecked(self.app_settings.is_auto_cropping_inputs)

        if self.app_settings.is_encoding_parallel_tasks:
            self.parallel_tasks_action.setChecked(True)
        else:
            self.standard_tasks_action.setChecked(True)

    def _setup_preferences_dialog(self):
        self.preferences_dialog = PreferencesDialog(self.app_settings)

    def _setup_about_dialog(self):
        self.about_dialog = AboutDialog()

    def _setup_signals(self):
        self.preferences_action.triggered.connect(self.on_preferences_dialog_action_triggered)
        self.about_render_watch_action.triggered.connect(self.on_about_render_watch_action_triggered)

    def on_about_render_watch_action_triggered(self):
        self.about_dialog.show()

    def on_preferences_dialog_action_triggered(self):
        self.preferences_dialog.show()


class AboutDialog(QtWidgets.QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        self.about_dialog_ui = Ui_AboutDialog()
        self.about_dialog_ui.setupUi(self)


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, app_settings: app_preferences.Settings):
        super(PreferencesDialog, self).__init__()

        self.app_settings = app_settings
        self.settings_dialog_ui = Ui_SettingsDialog()
        self.settings_dialog_ui.setupUi(self)

        self._setup_widgets()
        self._setup_signals()

    def _setup_widgets(self):
        pass

    def _setup_signals(self):
        pass
