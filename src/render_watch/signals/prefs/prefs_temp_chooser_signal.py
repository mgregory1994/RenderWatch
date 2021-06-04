"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""


import logging

from render_watch.helpers import directory_helper
from render_watch.startup import Gtk


class PrefsTempChooserSignal:
    def __init__(self, prefs_handlers, main_window_handlers, preferences, original_temp_directory):
        self.prefs_handlers = prefs_handlers
        self.main_window_handlers = main_window_handlers
        self.preferences = preferences
        self.original_temp_directory = original_temp_directory

    def on_prefs_temp_chooserbutton_file_set(self, temp_file_chooser):
        temp_file_path = temp_file_chooser.get_filename()

        try:
            self.__check_temp_directory_accessible(temp_file_chooser, temp_file_path)
            self.__check_temp_directory_empty(temp_file_chooser, temp_file_path)
        except ImportError:
            logging.warning('--- NOT SETTING TEMP FOLDER DIRECTORY: ' + temp_file_path + ' ---')
        else:
            self.prefs_handlers.update_temp_restart_state(temp_file_path)

            self.preferences.temp_directory = temp_file_path

    def __check_temp_directory_accessible(self, temp_file_chooser, temp_file_path):
        if not directory_helper.is_directory_accessible(temp_file_path):
            self.__show_directory_not_accessible_dialog(temp_file_path)
            temp_file_chooser.set_filename(self.original_temp_directory)

            raise ImportError

    def __show_directory_not_accessible_dialog(self, directory):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Directory \"' + directory + '\" is not accessible'
        )

        message_dialog.format_secondary_text('Check permissions or select a different directory.')
        message_dialog.run()
        message_dialog.destroy()

    def __check_temp_directory_empty(self, temp_file_chooser, temp_file_path):
        if not directory_helper.is_directory_empty(temp_file_path):
            message_response = self.__show_directory_not_empty_message_dialog(temp_file_path)

            if message_response == Gtk.ResponseType.NO:
                temp_file_chooser.set_filename(self.original_temp_directory)

                raise ImportError

    def __show_directory_not_empty_message_dialog(self, directory):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            'Directory \"' + directory + '\" is not empty'
        )

        message_dialog.format_secondary_text('It is highly recommended that you choose an empty directory due to '
                                             'potential DATA LOSS.\n\n'
                                             'This is especially dangerous when using the \"Clear Temp Folder'
                                             ' on Exit\" option.\n\n'
                                             'Are you sure you want to use this directory?')

        response = message_dialog.run()

        message_dialog.destroy()

        return response
