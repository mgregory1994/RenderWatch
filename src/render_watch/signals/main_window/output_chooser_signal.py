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


from render_watch.helpers import directory_helper
from render_watch.startup import Gtk


class OutputChooserSignal:
    """
    Handles the signal emitted when the user selected the output file chooser.
    """

    def __init__(self, main_window_handlers, inputs_page_handlers, application_preferences):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.application_preferences = application_preferences

    def on_output_chooserbutton_file_set(self, file_chooser_button):
        """
        Applies the selected output directory to all inputs.
        If the file path isn't accessible, then the user is notified and the old path is used instead.

        :param file_chooser_button: File chooser button that emitted the signal.
        """
        output_directory = file_chooser_button.get_filename()

        if directory_helper.is_directory_accessible(output_directory):
            self._apply_new_output_directory(output_directory)
        else:
            self._show_directory_not_accessible_dialog(output_directory, file_chooser_button)

    def _show_directory_not_accessible_dialog(self, output_directory, file_chooser_button):
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           'Directory \"' + output_directory + '\" is not accessable')
        message_dialog.format_secondary_text('Check permissions or select a different directory.')
        message_dialog.run()
        message_dialog.destroy()

        file_chooser_button.set_filename(self.application_preferences.output_directory)

    def _apply_new_output_directory(self, output_directory):
        self.application_preferences.output_directory = output_directory

        row_output_directory = output_directory + '/'
        for row in self.inputs_page_handlers.get_rows():
            row.ffmpeg.output_directory = row_output_directory
            row.setup_labels()
