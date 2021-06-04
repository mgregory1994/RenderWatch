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


from render_watch.startup import Gtk


class PrefsClearSignal:
    def __init__(self, prefs_handlers, main_window_handlers, preferences, original_temp_directory):
        self.prefs_handlers = prefs_handlers
        self.main_window_handlers = main_window_handlers
        self.preferences = preferences
        self.original_temp_directory = original_temp_directory

    def on_prefs_clear_checkbox_toggled(self, clear_temp_directory_checkbox):
        clear_temp_directory_enabled = clear_temp_directory_checkbox.get_active()

        if clear_temp_directory_enabled:
            self.__show_clear_temp_warning_dialog()

        self.preferences.clear_temp_directory_on_exit = clear_temp_directory_enabled

    def __show_clear_temp_warning_dialog(self):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Possible data loss'
        )

        message_dialog.format_secondary_text('This option deletes the chosen temp directory when closing '
                                             'Render Watch.\n\nThis can lead to possible DATA LOSS.\n\n'
                                             'USE WITH CAUTION!')
        message_dialog.run()
        message_dialog.destroy()
