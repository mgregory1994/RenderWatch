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


from render_watch.helpers import directory_helper
from render_watch.startup import Gtk


class OutputChooserSignal:
    def __init__(self, main_window_handlers, inputs_page_handlers, preferences):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences

    def on_output_chooserbutton_file_set(self, file_chooser_button):
        folder_path = file_chooser_button.get_filename()

        if not directory_helper.is_directory_accessible(folder_path):
            message_dialog = Gtk.MessageDialog(
                self.main_window_handlers.main_window,
                Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                'Directory \"' + folder_path + '\" is not accessable'
            )

            message_dialog.format_secondary_text('Check permissions or select a different directory.')
            message_dialog.run()
            message_dialog.destroy()
            file_chooser_button.set_filename(self.preferences.output_directory)

            return

        self.__setup_new_output_directory(folder_path)

    def __setup_new_output_directory(self, folder_path):
        self.preferences.output_directory = folder_path
        output_dir = folder_path + '/'

        for row in self.inputs_page_handlers.get_rows():
            row.ffmpeg.output_directory = output_dir

            row.setup_labels()
