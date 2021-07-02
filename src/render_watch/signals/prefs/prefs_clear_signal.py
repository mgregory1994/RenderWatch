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


from render_watch.startup import Gtk


class PrefsClearSignal:
    """Handles the signal emitted when the Clear Temporary Files option is changed in the preferences dialog."""

    def __init__(self, prefs_handlers, main_window_handlers, preferences, original_temp_directory):
        self.prefs_handlers = prefs_handlers
        self.main_window_handlers = main_window_handlers
        self.preferences = preferences
        self.original_temp_directory = original_temp_directory

    def on_prefs_clear_checkbox_toggled(self, clear_temp_directory_checkbox):
        """Applies the Clear Temporary Files option in the application's preferences.

        :param clear_temp_directory_checkbox:
            Checkbox that emitted the signal.
        """
        clear_temp_directory_enabled = clear_temp_directory_checkbox.get_active()
        if clear_temp_directory_enabled:
            self._show_clear_temp_warning_dialog()
        self.preferences.clear_temp_directory_on_exit = clear_temp_directory_enabled

    def _show_clear_temp_warning_dialog(self):
        # Warns the user that the Clear Temporary Files option can be dangerous.
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           'Warning')
        message_dialog.format_secondary_text('This option deletes the chosen temp directory when closing '
                                             'Render Watch.\nThis can lead to possible data loss.')
        message_dialog.run()
        message_dialog.destroy()
