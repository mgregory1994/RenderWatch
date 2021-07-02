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


import threading

from render_watch.encoding import preview
from render_watch.app_formatting import format_converter
from render_watch.signals.completed_row.remove_signal import RemoveSignal
from render_watch.startup import Gtk, GLib


class CompletedRow(Gtk.ListBoxRow):
    """Handles all functionality for each Gtk.ListboxRow completed row on the completed page."""

    def __init__(self, active_listbox_row, completed_page_handlers, preferences):
        Gtk.ListBoxRow.__init__(self)
        self.input_information_popover = active_listbox_row.input_information_popover
        self.active_listbox_row = active_listbox_row
        self.preferences = preferences
        gtk_builder = active_listbox_row.gtk_builder
        self.remove_signal = RemoveSignal(self, completed_page_handlers)
        self.listbox_row_widget_container = gtk_builder.get_object('completed_row_container')
        self.filename_label = gtk_builder.get_object('completed_row_filename_label')
        self.info_button = gtk_builder.get_object('completed_row_info_button')
        self.preview_thumbnail = gtk_builder.get_object('completed_row_preview')
        self.remove_button = gtk_builder.get_object('completed_row_remove_button')
        self.file_path_link = gtk_builder.get_object('completed_row_filepath_link')
        self.bitrate_label = gtk_builder.get_object('completed_row_bitrate_label')
        self.speed_label = gtk_builder.get_object('completed_row_speed_label')
        self.filesize_label = gtk_builder.get_object('completed_row_filesize_label')
        self.time_label = gtk_builder.get_object('completed_row_time_label')

        self._setup_listbox_row()
        self.add(self.listbox_row_widget_container)
        self.remove_button.connect('clicked', self.remove_signal.on_remove_button_clicked)

    def _setup_listbox_row(self):
        # Performs initial widget setup for the completed row.
        ffmpeg = self.active_listbox_row.ffmpeg
        output_file_path = self._get_output_file_path(ffmpeg)
        total_task_duration = format_converter.get_timecode_from_seconds(self.active_listbox_row.proc_time)
        self._setup_thumbnail(ffmpeg)
        self._setup_labels(output_file_path, total_task_duration)
        self.info_button.set_popover(self.input_information_popover)

    @staticmethod
    def _get_output_file_path(ffmpeg):
        # Returns the output path of the ffmpeg settings object's output.
        if ffmpeg.folder_state:
            return ffmpeg.output_directory
        return ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container

    def _setup_thumbnail(self, ffmpeg):
        # Sets the thumbnail of the completed row.
        if ffmpeg.folder_state:
            self.preview_thumbnail.set_from_icon_name('folder-symbolic', 96)
        else:
            threading.Thread(target=self._start_update_thumbnail_thread, args=(ffmpeg,)).start()

    def _setup_labels(self, output_file_path, total_task_duration):
        # Sets the labels for the completed row.
        self.filename_label.set_text(self.active_listbox_row.file_name)
        self.file_path_link.set_label(output_file_path)
        self.file_path_link.set_uri('file://' + output_file_path)
        self.bitrate_label.set_text(self.active_listbox_row.bitrate_label.get_text())
        self.speed_label.set_text(self.active_listbox_row.speed_label.get_text())
        self.filesize_label.set_text(self.active_listbox_row.filesize_label.get_text())
        self.time_label.set_text(total_task_duration)

    def _start_update_thumbnail_thread(self, ffmpeg):
        # Gets a preview thumbnail of the ffmpeg setting's input file.
        thumbnail_file_path = preview.generate_crop_preview_file(ffmpeg, self.preferences, 96)
        GLib.idle_add(self.preview_thumbnail.set_from_file, thumbnail_file_path)
