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


from render_watch.signals.application_preferences.temp_chooser_signal import TempChooserSignal
from render_watch.startup import Gtk


class TemporaryFilesRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the temporary files option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, main_window_handlers, application_preferences_handlers, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self.original_temp_directory = application_preferences.temp_directory

        self._setup_signals(main_window_handlers, application_preferences_handlers, application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, main_window_handlers, application_preferences_handlers, application_preferences):
        self.temp_chooser_signal = TempChooserSignal(application_preferences_handlers,
                                                     main_window_handlers,
                                                     application_preferences,
                                                     self.original_temp_directory)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.temproray_files_row_box = gtk_builder.get_object('temproray_files_row_box')
        self.temporary_files_chooserbutton = gtk_builder.get_object('temporary_files_chooserbutton')
        self.temporary_files_chooserbutton.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        self.temporary_files_chooserbutton.set_current_folder(application_preferences.temp_directory)

        self.add(self.temproray_files_row_box)

        self.temporary_files_chooserbutton.connect('file-set',
                                                   self.temp_chooser_signal.on_temporary_files_chooserbutton_file_set)
