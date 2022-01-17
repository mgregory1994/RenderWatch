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


import os
import threading

from render_watch.app_handlers.subtitle_stream_row import StreamRow
from render_watch.signals.subtitles.subtitle_streams_signal import AddSubtitleStreamSignal
from render_watch.startup import Gtk, GLib


class SubtitlesHandlers:
    """
    Handles all widget changes for the subtitles options.
    """

    def __init__(self, gtk_builder, inputs_page_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.is_restricted_mode_enabled = False

        self._setup_signals()
        self._setup_widgets(gtk_builder)

    def _setup_signals(self):
        self.add_subtitle_streams_signal = AddSubtitleStreamSignal(self)

        self.signals_list = [
            self.add_subtitle_streams_signal
        ]

    def _setup_widgets(self, gtk_builder):
        this_modules_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_modules_file_path, '../render_watch_data/rows_ui.glade')

        self.options_rows_gtk_builder = Gtk.Builder()
        self.options_rows_gtk_builder.add_from_file(rows_ui_file_path)

        self.subtitle_settings_stack = gtk_builder.get_object('subtitle_settings_stack')
        self.subtitle_settings_box = gtk_builder.get_object('subtitle_settings_box')
        self.subtitle_settings_not_available_label = gtk_builder.get_object('subtitle_settings_not_available_label')
        self.subtitle_streams_list = gtk_builder.get_object('subtitle_streams_list')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def set_settings(self):
        self._reset_list()
        threading.Thread(target=GLib.idle_add, args=(self._populate_list,)).start()

    def _reset_list(self):
        for row in self.subtitle_streams_list.get_children():
            self.subtitle_streams_list.remove(row)

    def _populate_list(self):
        ffmpeg = self.inputs_page_handlers.get_selected_row().ffmpeg

        if ffmpeg.subtitles_settings.subtitle_streams:
            self.set_settings_available_state()
        else:
            self.set_settings_not_available_state()

        for key, stream_in_use in ffmpeg.subtitles_settings.streams_in_use.items():
            stream_row = StreamRow(self, self.inputs_page_handlers, starting_stream=stream_in_use)
            self.subtitle_streams_list.add(stream_row)

            if key == ffmpeg.subtitles_settings.burn_in_stream_index:
                stream_row.set_burn_in_method()
        self.subtitle_streams_list.show_all()

    def set_settings_not_available_state(self):
        self.subtitle_settings_stack.set_visible_child(self.subtitle_settings_not_available_label)

    def set_settings_available_state(self):
        self.subtitle_settings_stack.set_visible_child(self.subtitle_settings_box)

    def set_restricted_state(self):
        if len(self.subtitle_streams_list.get_children()) > 1:
            for subtitle_stream_row in self.subtitle_streams_list.get_children()[1:]:
                self.remove_stream(subtitle_stream_row)

        self.subtitle_streams_list.get_children()[0].set_burn_in_method()
        self.subtitle_streams_list.get_children()[0].is_restricted_mode_enabled = True
        self.is_restricted_mode_enabled = True

    def set_unrestricted_state(self):
        if self.subtitle_streams_list.get_children():
            self.subtitle_streams_list.get_children()[0].is_restricted_mode_enabled = False

        self.is_restricted_mode_enabled = False

    def reset_settings(self):
        for subtitle_stream_row in self.subtitle_streams_list.get_children():
            self.remove_stream(subtitle_stream_row)

    def add_available_stream(self):
        if self.is_restricted_mode_enabled and self.subtitle_streams_list.get_children():
            return

        stream_row = StreamRow(self, self.inputs_page_handlers)

        if stream_row.get_selected_stream():
            ffmpeg = self.inputs_page_handlers.get_selected_row().ffmpeg
            ffmpeg.subtitles_settings.use_stream(stream_row.get_selected_stream())

            self.subtitle_streams_list.add(stream_row)
            self.update_streams()
            self.subtitle_streams_list.show_all()

    def remove_stream(self, subtitle_stream_row):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        ffmpeg.subtitles_settings.remove_stream(subtitle_stream_row.get_selected_stream())

        if subtitle_stream_row.is_burn_in_method_enabled():
            self.remove_burn_in_method()

            self.inputs_page_handlers.update_preview_page()

        self.subtitle_streams_list.remove(subtitle_stream_row)
        self.update_streams()
        self.subtitle_streams_list.show_all()

    def change_stream(self, subtitle_stream_row):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        ffmpeg.subtitles_settings.remove_stream(subtitle_stream_row.previously_selected_stream)
        ffmpeg.subtitles_settings.use_stream(subtitle_stream_row.get_selected_stream())

        if subtitle_stream_row.is_burn_in_method_enabled():
            ffmpeg.subtitles_settings.set_stream_method_burn_in(subtitle_stream_row.get_selected_stream())

            self.inputs_page_handlers.update_preview_page()

        self.update_streams()
        self.subtitle_streams_list.show_all()

    def set_burn_in_for_stream(self, subtitle_stream_row):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        if ffmpeg.video_settings:
            ffmpeg.subtitles_settings.set_stream_method_burn_in(subtitle_stream_row.get_selected_stream())
        else:
            subtitle_stream_row.remove_burn_in_method()
            return

        self.inputs_page_handlers.update_preview_page()

        threading.Thread(target=self._remove_burn_in_for_other_streams, args=(subtitle_stream_row,)).start()

    def _remove_burn_in_for_other_streams(self, selected_subtitle_stream_row):
        for subtitle_stream_row in self.subtitle_streams_list:
            if subtitle_stream_row is not selected_subtitle_stream_row:
                GLib.idle_add(subtitle_stream_row.remove_burn_in_method)

    def remove_burn_in_method(self):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        ffmpeg.subtitles_settings.burn_in_stream_index = None

        self.inputs_page_handlers.update_preview_page()

    def remove_burn_in_for_all_streams(self):
        for subtitle_stream_row in self.subtitle_streams_list.get_children():
            subtitle_stream_row.remove_burn_in_method()

        self.remove_burn_in_method()

    def update_streams(self):
        for stream_row in self.subtitle_streams_list.get_children():
            stream_row.update_available_streams()
