# Copyright 2021 Michael Gregory
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


from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.signals.prefs.clear_temp_files_signal import ClearTempFilesSignal
from render_watch.signals.prefs.concurrent_tasks_signal import ConcurrentTasksSignal
from render_watch.signals.prefs.dark_mode_signal import DarkModeSignal
from render_watch.signals.prefs.move_watch_folder_tasks_to_done_signal import MoveWatchFolderTasksToDoneSignal
from render_watch.signals.prefs.overwrite_outputs_signal import OverwriteOutputsSignal
from render_watch.signals.prefs.temp_chooser_signal import TempChooserSignal
from render_watch.signals.prefs.watch_folder_wait_for_tasks_signal import WatchFolderWaitForTasksSignal


class ApplicationPreferencesHandlers:
    """
    Handles all widget changes for the preferences dialog.
    """

    def __init__(self, gtk_builder, gtk_settings, main_window_handlers, application_preferences):
        self.original_temp_directory = application_preferences.temp_directory
        self.original_concurrent_tasks_index = ApplicationPreferences.PARALLEL_TASKS_VALUES.index(
            str(application_preferences.parallel_tasks))

        self._setup_signals(gtk_settings, main_window_handlers, application_preferences)
        self._setup_widgets(gtk_builder)

    def _setup_signals(self, gtk_settings, main_window_handlers, application_preferences):
        self.clear_temp_files_signal = ClearTempFilesSignal(self,
                                                            main_window_handlers,
                                                            application_preferences,
                                                            self.original_temp_directory)
        self.concurrent_tasks_signal = ConcurrentTasksSignal(self, application_preferences)
        self.dark_mode_signal = DarkModeSignal(gtk_settings, application_preferences)
        self.move_watch_folder_tasks_to_done_signal = MoveWatchFolderTasksToDoneSignal(application_preferences)
        self.overwrite_outputs_signal = OverwriteOutputsSignal(application_preferences)
        self.temp_chooser_signal = TempChooserSignal(self,
                                                     main_window_handlers,
                                                     application_preferences,
                                                     self.original_temp_directory)
        self.watch_folder_wait_for_tasks_signal = WatchFolderWaitForTasksSignal(application_preferences)
        self.signals_list = (
            self.clear_temp_files_signal, self.concurrent_tasks_signal, self.dark_mode_signal,
            self.move_watch_folder_tasks_to_done_signal, self.overwrite_outputs_signal,
            self.temp_chooser_signal, self.watch_folder_wait_for_tasks_signal
        )

    def _setup_widgets(self, gtk_builder):
        self.application_preferences_dialog = gtk_builder.get_object("application_preferences_dialog")
        self.concurrent_tasks_combobox = gtk_builder.get_object('concurrent_tasks_combobox')
        self.concurrent_tasks_message_stack = gtk_builder.get_object('concurrent_tasks_message_stack')
        self.concurrent_tasks_message_8 = gtk_builder.get_object('concurrent_tasks_message_8')
        self.concurrent_tasks_message_12 = gtk_builder.get_object('concurrent_tasks_message_12')
        self.concurrent_tasks_message_24 = gtk_builder.get_object('concurrent_tasks_message_24')
        self.concurrent_tasks_message_32 = gtk_builder.get_object('concurrent_tasks_message_32')
        self.concurrent_tasks_message_max = gtk_builder.get_object('concurrent_tasks_message_max')
        self.concurrent_tasks_restart_stack = gtk_builder.get_object('concurrent_tasks_restart_stack')
        self.concurrent_tasks_restart_icon = gtk_builder.get_object('concurrent_tasks_restart_icon')
        self.concurrent_tasks_restart_blank_label = gtk_builder.get_object('concurrent_tasks_restart_blank_label')
        self.concurrent_nvenc_tasks_warning_stack = gtk_builder.get_object('concurrent_nvenc_tasks_warning_stack')
        self.concurrent_nvenc_tasks_warning_blank_label = gtk_builder.get_object('concurrent_nvenc_tasks_warning_blank_label')
        self.concurrent_nvenc_tasks_warning_icon = gtk_builder.get_object('concurrent_nvenc_tasks_warning_icon')
        self.temporary_files_restart_stack = gtk_builder.get_object('temporary_files_restart_stack')
        self.temporary_files_restart_icon = gtk_builder.get_object('temporary_files_restart_icon')
        self.temporary_files_restart_blank_label = gtk_builder.get_object('temporary_files_restart_blank_label')
        self.dark_mode_switch = gtk_builder.get_object("dark_mode_switch")
        self.temporary_files_chooserbutton = gtk_builder.get_object('temporary_files_chooserbutton')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def update_concurrent_tasks_restart_state(self):
        """
        Shows the "restart required" icon when the concurrent tasks settings are changed.
        """
        if self.concurrent_tasks_combobox.get_active() == self.original_concurrent_tasks_index:
            self.concurrent_tasks_restart_stack.set_visible_child(self.concurrent_tasks_restart_blank_label)
        else:
            self.concurrent_tasks_restart_stack.set_visible_child(self.concurrent_tasks_restart_icon)

    def update_concurrent_message(self, concurrent_tasks_value):
        """
        Shows the recommended amount of cores for the selected amount of concurrent tasks.
        """
        if concurrent_tasks_value == '2':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_8)
        elif concurrent_tasks_value == '3':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_12)
        elif concurrent_tasks_value == '4':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_24)
        elif concurrent_tasks_value == '6':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_32)
        else:
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_max)

    def update_nvenc_concurrent_tasks_restart_state(self, concurrent_nvenc_tasks_text):
        """
        Shows the restart required image when the NVENC concurrent settings are changed.
        """
        if concurrent_nvenc_tasks_text != 'auto':
            self.concurrent_nvenc_tasks_warning_stack.set_visible_child(self.concurrent_nvenc_tasks_warning_icon)
        else:
            self.concurrent_nvenc_tasks_warning_stack.set_visible_child(self.concurrent_nvenc_tasks_warning_blank_label)

    def update_temp_restart_state(self, temp_files_directory):
        """
        Shows the "restart required" icon when the temp directory is changed.
        """
        if temp_files_directory == self.original_temp_directory:
            self.temporary_files_restart_stack.set_visible_child(self.temporary_files_restart_blank_label)
        else:
            self.temporary_files_restart_stack.set_visible_child(self.temporary_files_restart_icon)
