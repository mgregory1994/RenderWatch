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
    """
    Handles the functionality for an individual completed task on the completed page.
    """

    def __init__(self, active_listbox_row, completed_page_handlers, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self.input_information_popover = active_listbox_row.input_information_popover
        self.active_listbox_row = active_listbox_row
        self.application_preferences = application_preferences

        self._setup_signals(completed_page_handlers)
        self._setup_widgets(active_listbox_row)

    def _setup_signals(self, completed_page_handlers):
        self.remove_signal = RemoveSignal(self, completed_page_handlers)

    def _setup_widgets(self, active_listbox_row):
        gtk_builder = active_listbox_row.gtk_builder

        self.completed_listbox_row_box = gtk_builder.get_object('completed_listbox_row_box')
        self.completed_listbox_row_file_name_label = gtk_builder.get_object('completed_listbox_row_file_name_label')
        self.completed_listbox_row_task_info_menubutton = gtk_builder.get_object('completed_listbox_row_task_info_menubutton')
        self.completed_listbox_row_preview_icon = gtk_builder.get_object('completed_listbox_row_preview_icon')
        self.completed_listbox_row_remove_button = gtk_builder.get_object('completed_listbox_row_remove_button')
        self.completed_listbox_row_file_path_link = gtk_builder.get_object('completed_listbox_row_file_path_link')
        self.completed_listbox_row_bitrate_value_label = gtk_builder.get_object('completed_listbox_row_bitrate_value_label')
        self.completed_listbox_row_speed_value_label = gtk_builder.get_object('completed_listbox_row_speed_value_label')
        self.completed_listbox_row_file_size_value_label = gtk_builder.get_object('completed_listbox_row_file_size_value_label')
        self.completed_listbox_row_encode_time_value_label = gtk_builder.get_object('completed_listbox_row_encode_time_value_label')

        self._setup_listbox_row()
        self.add(self.completed_listbox_row_box)

        self.completed_listbox_row_remove_button.connect('clicked', self.remove_signal.on_remove_button_clicked)

    def _setup_listbox_row(self):
        ffmpeg = self.active_listbox_row.ffmpeg
        output_file_path = self._get_output_file_path(ffmpeg)
        total_task_duration = format_converter.get_timecode_from_seconds(self.active_listbox_row.proc_time)

        self._setup_thumbnail(ffmpeg)
        self._setup_labels(output_file_path, total_task_duration)
        self.completed_listbox_row_task_info_menubutton.set_popover(self.input_information_popover)

    @staticmethod
    def _get_output_file_path(ffmpeg):
        if ffmpeg.folder_state:
            return ffmpeg.output_directory
        return ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container

    def _setup_thumbnail(self, ffmpeg):
        if ffmpeg.folder_state:
            self.completed_listbox_row_preview_icon.set_from_icon_name('folder-symbolic', 96)
        else:
            threading.Thread(target=self._start_update_thumbnail_thread, args=(ffmpeg,)).start()

    def _setup_labels(self, output_file_path, total_task_duration):
        self.completed_listbox_row_file_name_label.set_text(self.active_listbox_row.file_name)
        self.completed_listbox_row_file_path_link.set_label(output_file_path)
        self.completed_listbox_row_file_path_link.set_uri('file://' + output_file_path)
        self.completed_listbox_row_bitrate_value_label.set_text(self.active_listbox_row.completed_listbox_row_bitrate_value_label.get_text())
        self.completed_listbox_row_speed_value_label.set_text(self.active_listbox_row.completed_listbox_row_speed_value_label.get_text())
        self.completed_listbox_row_file_size_value_label.set_text(self.active_listbox_row.completed_listbox_row_file_size_value_label.get_text())
        self.completed_listbox_row_encode_time_value_label.set_text(total_task_duration)

    def _start_update_thumbnail_thread(self, ffmpeg):
        thumbnail_file_path = preview.generate_crop_preview_file(ffmpeg, self.application_preferences, 96)
        GLib.idle_add(self.completed_listbox_row_preview_icon.set_from_file, thumbnail_file_path)

    def signal_remove_button(self):
        self.remove_signal.on_remove_button_clicked(self.completed_listbox_row_remove_button)
