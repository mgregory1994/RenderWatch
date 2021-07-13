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


from render_watch.startup.preferences import Preferences
from render_watch.signals.prefs.prefs_clear_signal import PrefsClearSignal
from render_watch.signals.prefs.prefs_concurrent_signal import PrefsConcurrentSignal
from render_watch.signals.prefs.prefs_dark_theme_signal import PrefsDarkThemeSignal
from render_watch.signals.prefs.prefs_move_to_done_signal import PrefsMoveToDoneSignal
from render_watch.signals.prefs.prefs_overwrite_outputs_signal import PrefsOverwriteOutputsSignal
from render_watch.signals.prefs.prefs_temp_chooser_signal import PrefsTempChooserSignal
from render_watch.signals.prefs.prefs_wait_for_tasks_signal import PrefsWaitForTasksSignal


class PrefsHandlers:
    """Handles all widget changes for the preferences dialog."""

    def __init__(self, gtk_builder, gtk_settings, main_window_handlers, preferences):
        self.original_temp_directory = preferences.temp_directory
        self.original_parallel_tasks_index = Preferences.parallel_tasks_values_list.index(
            preferences.parallel_tasks_as_string)
        self.prefs_clear_signal = PrefsClearSignal(self,
                                                   main_window_handlers,
                                                   preferences,
                                                   self.original_temp_directory)
        self.prefs_concurrent_signal = PrefsConcurrentSignal(self, preferences)
        self.prefs_dark_theme_signal = PrefsDarkThemeSignal(gtk_settings, preferences)
        self.prefs_move_to_done_signal = PrefsMoveToDoneSignal(preferences)
        self.prefs_overwrite_outputs_signal = PrefsOverwriteOutputsSignal(preferences)
        self.prefs_temp_chooser_signal = PrefsTempChooserSignal(self,
                                                                main_window_handlers,
                                                                preferences,
                                                                self.original_temp_directory)
        self.prefs_wait_for_tasks_signal = PrefsWaitForTasksSignal(preferences)
        self.signals_list = (
            self.prefs_clear_signal, self.prefs_concurrent_signal, self.prefs_dark_theme_signal,
            self.prefs_move_to_done_signal, self.prefs_overwrite_outputs_signal,
            self.prefs_temp_chooser_signal, self.prefs_wait_for_tasks_signal
        )
        self.prefs_dialog = gtk_builder.get_object("prefs_dialog")
        self.prefs_concurrent_combobox = gtk_builder.get_object('prefs_concurrent_combobox')
        self.prefs_concurrent_message_stack = gtk_builder.get_object('prefs_concurrent_message_stack')
        self.prefs_concurrent_message_8 = gtk_builder.get_object('prefs_concurrent_message_8')
        self.prefs_concurrent_message_12 = gtk_builder.get_object('prefs_concurrent_message_12')
        self.prefs_concurrent_message_24 = gtk_builder.get_object('prefs_concurrent_message_24')
        self.prefs_concurrent_message_32 = gtk_builder.get_object('prefs_concurrent_message_32')
        self.prefs_concurrent_message_final = gtk_builder.get_object('prefs_concurrent_message_final')
        self.prefs_concurrent_restart_stack = gtk_builder.get_object('prefs_concurrent_restart_stack')
        self.prefs_concurrent_restart_image = gtk_builder.get_object('prefs_concurrent_restart_image')
        self.prefs_concurrent_empty_label = gtk_builder.get_object('prefs_concurrent_empty_label')
        self.prefs_nvenc_concurrent_warning_stack = gtk_builder.get_object('prefs_nvenc_concurrent_warning_stack')
        self.prefs_nvenc_concurrent_empty_label = gtk_builder.get_object('prefs_nvenc_concurrent_empty_label')
        self.prefs_nvenc_concurrent_warning_image = gtk_builder.get_object('prefs_nvenc_concurrent_warning_image')
        self.prefs_temp_restart_stack = gtk_builder.get_object('prefs_temp_restart_stack')
        self.prefs_temp_restart_image = gtk_builder.get_object('prefs_temp_restart_image')
        self.prefs_temp_empty_label = gtk_builder.get_object('prefs_temp_empty_label')
        self.prefs_dark_theme_checkbox = gtk_builder.get_object("prefs_dark_theme_checkbox")
        self.prefs_temp_chooserbutton = gtk_builder.get_object('prefs_temp_chooserbutton')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def update_concurrent_restart_state(self):
        """Shows the restart required image when the concurrent settings are changed."""
        if self.prefs_concurrent_combobox.get_active() == self.original_parallel_tasks_index:
            self.prefs_concurrent_restart_stack.set_visible_child(self.prefs_concurrent_empty_label)
        else:
            self.prefs_concurrent_restart_stack.set_visible_child(self.prefs_concurrent_restart_image)

    def update_concurrent_message(self, parallel_tasks_value):
        """Shows a message about your current concurrency setting."""
        if parallel_tasks_value == '2':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_8)
        elif parallel_tasks_value == '3':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_12)
        elif parallel_tasks_value == '4':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_24)
        elif parallel_tasks_value == '6':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_32)
        else:
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_final)

    def update_nvenc_concurrent_restart_state(self, concurrent_nvenc_text):
        """Shows the restart required image when the NVENC concurrent settings are changed."""
        if concurrent_nvenc_text != 'auto':
            self.prefs_nvenc_concurrent_warning_stack.set_visible_child(self.prefs_nvenc_concurrent_warning_image)
        else:
            self.prefs_nvenc_concurrent_warning_stack.set_visible_child(self.prefs_nvenc_concurrent_empty_label)

    def update_temp_restart_state(self, temp_file_path):
        """Shows the restart required image when the temp directory is changed."""
        if temp_file_path == self.original_temp_directory:
            self.prefs_temp_restart_stack.set_visible_child(self.prefs_temp_empty_label)
        else:
            self.prefs_temp_restart_stack.set_visible_child(self.prefs_temp_restart_image)
