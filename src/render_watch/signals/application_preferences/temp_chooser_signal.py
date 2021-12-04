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


import logging

from render_watch.helpers import directory_helper
from render_watch.startup import Gtk


class TempChooserSignal:
    """
    Handles the signal emitted when the Temporary Directory Chooser is changed in the preferences dialog.
    """

    def __init__(self, prefs_handlers, main_window_handlers, application_preferences, original_temp_directory):
        self.prefs_handlers = prefs_handlers
        self.main_window_handlers = main_window_handlers
        self.application_preferences = application_preferences
        self.original_temp_directory = original_temp_directory

    def on_temporary_files_chooserbutton_file_set(self, temporary_files_chooserbutton):
        """
        Applies the Temporary Directory in the application's preferences.

        :param temporary_files_chooserbutton: File Chooser that emitted the signal.
        """
        temp_directory = temporary_files_chooserbutton.get_filename()

        try:
            self._test_temp_directory_accessible(temporary_files_chooserbutton, temp_directory)
            self._test_temp_directory_empty(temporary_files_chooserbutton, temp_directory)
        except ImportError:
            logging.warning('--- CAN\'T SET TEMP FOLDER DIRECTORY: ' + temp_directory + ' ---')
        else:
            self.application_preferences.set_temp_directory(temp_directory)

            self.prefs_handlers.update_temp_restart_state(temp_directory)

    def _test_temp_directory_accessible(self, temp_file_chooser, temp_directory):
        if directory_helper.is_directory_accessible(temp_directory):
            return

        temp_file_chooser.set_filename(self.original_temp_directory)
        self._show_directory_not_accessible_dialog(temp_directory)

        raise ImportError

    def _show_directory_not_accessible_dialog(self, temp_directory):
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           'Directory \"' + temp_directory + '\" is not accessible')
        message_dialog.format_secondary_text('Check permissions or select a different directory.')
        message_dialog.run()
        message_dialog.destroy()

    def _test_temp_directory_empty(self, temp_file_chooser, temp_directory):
        if directory_helper.is_directory_empty(temp_directory):
            return

        message_response = self._show_directory_not_empty_message_dialog(temp_directory)
        if message_response == Gtk.ResponseType.NO:
            temp_file_chooser.set_filename(self.original_temp_directory)

            raise ImportError

    def _show_directory_not_empty_message_dialog(self, temp_directory):
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.YES_NO,
                                           'Directory \"' + temp_directory + '\" is not empty')
        message_dialog.format_secondary_text('This can lead to potential data loss.'
                                             '\n\nUse chosen directory?')
        response = message_dialog.run()
        message_dialog.destroy()

        return response
