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


import threading

from app_formatting import format_converter
from startup import Gtk, GLib


class ChunkRow(Gtk.ListBoxRow):
    def __init__(self, ffmpeg_chunk, chunk_number, active_row):
        Gtk.ListBoxRow.__init__(self)

        self.ffmpeg = ffmpeg_chunk
        self.chunk_number = chunk_number
        self.active_row = active_row
        self.finished = False
        self.task_information = {
            'progress': 0.0,
            'speed': 0.0,
            'bitrate': 0.0,
            'filesize': 0.0,
            'time': 0,
            'current_time': 0,
        }
        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file('../data/chunk_ui.glade')
        self.__chunk_row_container = gtk_builder.get_object('chunk_row_container')
        self.chunk_identifier_label = gtk_builder.get_object('chunk_identifier_label')
        self.chunk_timespan_label = gtk_builder.get_object('chunk_timespan_label')
        self.chunk_progress_bar = gtk_builder.get_object('chunk_progress_bar')

        self.__setup_chunk_row()
        self.add(self.__chunk_row_container)

    def __setup_chunk_row(self):
        start_time, trim_duration = self.__get_ffmpeg_trim_start_time_and_duration()
        end_time = start_time + trim_duration
        start_timecode = format_converter.get_timecode_from_seconds(start_time)
        end_timecode = format_converter.get_timecode_from_seconds(end_time)

        self.__setup_chunk_identifier_label()
        self.chunk_timespan_label.set_text('(' + start_timecode + ' - ' + end_timecode + ')')

    def __get_ffmpeg_trim_start_time_and_duration(self):
        if self.ffmpeg.trim_settings is None:
            start_time = 0
            trim_duration = self.ffmpeg.duration_origin
        else:
            start_time = self.ffmpeg.trim_settings.start_time
            trim_duration = self.ffmpeg.trim_settings.trim_duration

        return start_time, trim_duration

    def __setup_chunk_identifier_label(self):
        if self.ffmpeg.no_video:
            self.chunk_identifier_label.set_text('Audio:')
        else:
            self.chunk_identifier_label.set_text('Chunk ' + str(self.chunk_number) + ':')

    def set_start_state(self):
        self.active_row.chunk_set_start_state()

    def set_finished_state(self):
        self.finished = True

        threading.Thread(target=self.active_row.chunk_set_finished_state, args=()).start()

    def update_thumbnail(self):
        self.active_row.update_thumbnail()

    def update_labels(self):  # Needs this name for active row / chunk row interoperability
        self.chunk_progress_bar.set_fraction(self.progress)

    @property
    def paused(self):
        return self.active_row.paused

    @property
    def stopped(self):
        return self.active_row.stopped

    @stopped.setter
    def stopped(self, is_stopped):
        self.active_row.stopped = is_stopped

    @property
    def progress(self):
        return self.task_information['progress']

    @progress.setter
    def progress(self, progress_value):
        if progress_value is None:
            return

        self.task_information['progress'] = progress_value

    @property
    def speed(self):
        return self.task_information['speed']

    @speed.setter
    def speed(self, speed_value):
        if speed_value == 0:
            return

        self.task_information['speed'] = speed_value

    @property
    def bitrate(self):
        return self.task_information['bitrate']

    @bitrate.setter
    def bitrate(self, bitrate_value):
        if bitrate_value == 0:
            return

        self.task_information['bitrate'] = bitrate_value

    @property
    def file_size(self):
        return self.task_information['filesize']

    @file_size.setter
    def file_size(self, file_size_value):
        if file_size_value == 0:
            return

        self.task_information['filesize'] = file_size_value

    @property
    def time(self):
        return self.task_information['time']

    @time.setter
    def time(self, time_value):
        if time_value == 0:
            return

        self.task_information['time'] = time_value

    @property
    def current_time(self):
        return self.task_information['current_time']

    @current_time.setter
    def current_time(self, current_time_in_seconds):
        if current_time_in_seconds == 0:
            return

        self.task_information['current_time'] = current_time_in_seconds

    @property
    def task_threading_event(self):
        return self.active_row.task_threading_event
