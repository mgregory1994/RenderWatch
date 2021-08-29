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
import time
import logging

from render_watch.encoding import preview
from render_watch.helpers import encoder_helper
from render_watch.app_formatting import format_converter
from render_watch.signals.active_row.pause_signal import PauseSignal
from render_watch.signals.active_row.start_signal import StartSignal
from render_watch.signals.active_row.stop_signal import StopSignal
from render_watch.startup import Gtk, GLib


class ActiveRow(Gtk.ListBoxRow):
    """Handles all functionality for each Gtk.ListboxRow active row on the active page."""

    def __init__(self,
                 ffmpeg,
                 input_information_popover,
                 gtk_builder,
                 preview_thumbnail_file_path,
                 active_page_handlers,
                 preferences,
                 live_thumbnail_enabled=True):
        Gtk.ListBoxRow.__init__(self)
        self._ffmpeg = ffmpeg
        self._folder_path = None
        self.preferences = preferences
        self.chunk_row_list = []
        self.audio_chunk_row = None
        self.watch_folder = None
        self.input_information_popover = input_information_popover
        self.preview_thumbnail_file_path = preview_thumbnail_file_path
        self.active_page_handlers = active_page_handlers
        self.paused = False
        self.stopped = False
        self.started = False
        self.failed = False
        self.idle = False
        self.finished = False
        self.video_chunks_done = False
        self.audio_chunk_done = False
        self.live_thumbnail = live_thumbnail_enabled
        self.task_information = {
            'progress': 0.0,
            'speed': 0.0,
            'bitrate': 0.0,
            'filesize': 0.0,
            'time': 0,
            'current_time': 0,
            'total_time': 0
        }
        self.proc_timer_thread = threading.Thread(target=self._start_proc_timer, args=(), daemon=True)
        self.name_changer_timer_thread = threading.Thread(target=self._start_name_changer_timer, args=(), daemon=True)
        self.task_threading_event = threading.Event()
        self._thread_lock = threading.Lock()
        self.pause_signal = PauseSignal(self)
        self.start_signal = StartSignal(self)
        self.stop_signal = StopSignal(self)
        self.gtk_builder = gtk_builder
        self.listbox_row_widget_container = gtk_builder.get_object('active_row_container')
        self.active_row_filename_stack = gtk_builder.get_object('active_row_filename_stack')
        self.active_row_folder_filename_label = gtk_builder.get_object('active_row_folder_filename_label')
        self.filename_label = gtk_builder.get_object('active_row_filename_label')
        self.bitrate_label = gtk_builder.get_object('active_row_bitrate_label')
        self.speed_label = gtk_builder.get_object('active_row_speed_label')
        self.filesize_label = gtk_builder.get_object('active_row_filesize_label')
        self.time_label = gtk_builder.get_object('active_row_time_label')
        self.progress_bar = gtk_builder.get_object('active_row_progress_bar')
        self.preview_thumbnail = gtk_builder.get_object('active_row_preview')
        self.info_button = gtk_builder.get_object('active_row_info_button')
        self.pause_button = gtk_builder.get_object('active_row_pause_button')
        self.start_button = gtk_builder.get_object('active_row_play_button')
        self.control_stack = gtk_builder.get_object('active_row_control_stack')
        self.stop_button = gtk_builder.get_object('active_row_stop_button')
        self.active_row_chunks_revealer = gtk_builder.get_object('active_row_chunks_revealer')
        self.active_row_chunks_listbox = gtk_builder.get_object('active_row_chunks_listbox')
        self.chunks_popover = gtk_builder.get_object('chunks_popover')

        self._setup_listbox_row()
        self.add(self.listbox_row_widget_container)
        self.pause_button.connect('clicked', self.pause_signal.on_pause_button_clicked)
        self.start_button.connect('clicked', self.start_signal.on_start_button_clicked)
        self.stop_button.connect('clicked', self.stop_signal.on_stop_button_clicked)

    def _setup_listbox_row(self):
        # Configure widgets and setup task state
        self.filename_label.set_text(self.ffmpeg.filename)
        self.info_button.set_popover(self.input_information_popover)
        if not self.ffmpeg.folder_state:
            self.thumbnail.set_from_file(self.preview_thumbnail_file_path)
        else:
            self._folder_path = self.ffmpeg.input_file
            self.thumbnail.set_from_icon_name('folder-symbolic', 96)
        self._update_labels()
        self.task_threading_event.set()

    def _update_labels(self):
        # Updates labels while encode process is running.
        with self._thread_lock:
            GLib.idle_add(self._update_progress)
            GLib.idle_add(self._update_speed_value_text)
            GLib.idle_add(self._update_bitrate_value_text)
            GLib.idle_add(self._update_filesize_value_text)
            GLib.idle_add(self._update_time_value_text)

    def _update_progress(self):
        progress = self.task_information['progress']
        self.progress_bar.set_fraction(progress)

    def _update_speed_value_text(self):
        speed = self.task_information['speed']
        self.speed_label.set_text(str(speed) + 'x')

    def _update_bitrate_value_text(self):
        bitrate = self.task_information['bitrate']
        self.bitrate_label.set_text(str(bitrate) + 'kbps')

    def _update_filesize_value_text(self):
        filesize = self.task_information['filesize']
        self.filesize_label.set_text(format_converter.get_file_size_from_bytes(filesize))

    def _update_time_value_text(self):
        time_value = self.task_information['time']
        self.time_label.set_text(format_converter.get_timecode_from_seconds(time_value))

    def update_thumbnail(self):
        # Shows preview thumbnail of current encode task.
        with self._thread_lock:
            if self.live_thumbnail:
                current_time = self._get_current_time_from_active_row()
                self._generate_new_thumbnail(current_time)

    def _get_current_time_from_active_row(self):
        if self.ffmpeg.is_video_settings_2_pass():
            return self.current_time / 2
        return self.current_time

    def _generate_new_thumbnail(self, current_time):
        # Creates and shows a preview image of the current encode task.
        if self.ffmpeg.trim_settings:
            current_time = current_time + self.ffmpeg.trim_settings.start_time
        try:
            preview_thumbnail_file = preview.generate_crop_preview_file(self.ffmpeg,
                                                                        self.preferences,
                                                                        96,
                                                                        start_time_param=current_time)
            GLib.idle_add(self.preview_thumbnail.set_from_file, preview_thumbnail_file)
        except:
            logging.warning('--- FAILED TO SET ACTIVE_ROW PREVIEW THUMBNAIL ---')
            GLib.idle_add(self.preview_thumbnail.set_from_icon_name, 'applications-multimedia-symbolic', 96)
        finally:
            if self.idle:
                GLib.idle_add(self.preview_thumbnail.set_from_icon_name, 'folder-symbolic', 96)

    def add_chunk_row(self, chunk_row):
        """Adds a Gtk.ListboxRow for a chunk of the current encode task."""
        self.chunk_row_list.append(chunk_row)
        self.active_row_chunks_listbox.add(chunk_row)
        self.active_row_chunks_listbox.show_all()
        self.active_row_chunks_revealer.set_reveal_child(True)

    def add_audio_chunk_row(self, audio_chunk_row):
        """Adds a Gtk.ListboxRow for an audio chunk of the current encode task."""
        self.audio_chunk_row = audio_chunk_row
        self.active_row_chunks_listbox.add(audio_chunk_row)
        self.active_row_chunks_listbox.show_all()

    def set_start_state(self):
        """Sets this Gtk.ListboxRow's widgets to the encode start state."""
        self.idle = False
        self.started = True
        self.progress_bar.set_sensitive(True)
        self.control_stack.set_sensitive(True)
        self._setup_proc_timer_thread()
        self._setup_name_changer_timer_thread()

    def _setup_proc_timer_thread(self):
        # Starts a timer to keep track of how long the encode task takes.
        if not self.proc_timer_thread.is_alive():
            self.proc_timer_thread = threading.Thread(target=self._start_proc_timer, args=(), daemon=True)
            self.proc_timer_thread.start()

    def _setup_name_changer_timer_thread(self):
        # Starts a thread for the timer that changes the title of this Gtk.ListboxRow.
        if (self.ffmpeg.folder_state or self.watch_folder is not None) \
                and not self.name_changer_timer_thread.is_alive():
            self.name_changer_timer_thread = threading.Thread(target=self._start_name_changer_timer,
                                                              args=(),
                                                              daemon=True)
            self.name_changer_timer_thread.start()

    def _start_name_changer_timer(self):
        # Changes the title of this Gtk.ListboxRow to switch between the folder name
        # and the name of the file being currently worked on.
        while not self.finished and not self.stopped and not self.idle:
            GLib.idle_add(self.active_row_filename_stack.set_visible_child, self.active_row_folder_filename_label)
            time.sleep(5)
            GLib.idle_add(self.active_row_filename_stack.set_visible_child, self.filename_label)
            time.sleep(5)

    def set_idle_state(self):
        """Sets this Gtk.ListboxRow's widgets to the encode idle state."""
        self.idle = True
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_sensitive(False)
        self.preview_thumbnail.set_from_icon_name('folder-symbolic', 96)

    def set_finished_state(self):
        """Sets this Gtk.ListboxRow's widgets to the encode finished state."""
        threading.Thread(target=self._finish_and_remove_active_listbox_row, args=()).start()

    def _finish_and_remove_active_listbox_row(self):
        # Sets the widgets to a finished state and removes this Gtk.ListboxRow from it's parent Gtk.Listbox.
        self.finished = True
        GLib.idle_add(self._popdown_popovers)

        self._wait_for_info_threads()

        if not self.stopped:  # Needed because stop button already removes this from active page listbox
            GLib.idle_add(self.active_page_handlers.remove_row, self)

    def _popdown_popovers(self):
        # Closes the input info.'s and chunk's popover menus.
        self.input_information_popover.popdown()
        self.chunks_popover.popdown()

    def _wait_for_info_threads(self):
        # Wait for the task timer and the name changer timer threads.
        if self.proc_timer_thread is not None and self.proc_timer_thread.is_alive():
            self.proc_timer_thread.join()
        if self.name_changer_timer_thread is not None and self.name_changer_timer_thread.is_alive():
            self.name_changer_timer_thread.join()

    def chunk_set_start_state(self):
        """If this chunk Gtk.ListboxRow's widgets to a encoder start state."""
        with self._thread_lock:
            if not self.started:
                GLib.idle_add(self.set_start_state)

    def chunk_set_finished_state(self):
        """If this chunk Gtk.ListboxRow's widgets to a encoder finished state."""
        with self._thread_lock:
            for chunk_row in self.chunk_row_list:
                if not chunk_row.finished or self.stopped:
                    return
            if not self.video_chunks_done:
                encoder_helper.concatenate_video_chunks(self.chunk_row_list, self.ffmpeg, self.preferences)
                self.video_chunks_done = True

            if not self.audio_chunk_row.finished or self.stopped:
                return
            if not self.audio_chunk_done:
                encoder_helper.mux_chunks(self.audio_chunk_row, self.ffmpeg, self.preferences)
                self.audio_chunk_done = True

            GLib.idle_add(self.set_finished_state)

    def _chunk_update_progress(self):
        with self._thread_lock:
            total_progress = 0.0
            for chunk_row in self.chunk_row_list:
                total_progress += chunk_row.progress
            total_progress /= len(self.chunk_row_list)
            self.progress = total_progress

    def _chunk_update_speed(self):
        with self._thread_lock:
            total_speed = 0.0
            for chunk_row in self.chunk_row_list:
                total_speed += chunk_row.speed
            self.speed = round(total_speed, 2)

    def _chunk_update_bitrate(self):
        with self._thread_lock:
            total_bitrate = 0.0
            for chunk_row in self.chunk_row_list:
                total_bitrate += chunk_row.bitrate
            total_bitrate /= len(self.chunk_row_list)
            self.bitrate = round(total_bitrate, 1)

    def _chunk_update_file_size(self):
        with self._thread_lock:
            total_file_size = 0.0
            for chunk_row in self.chunk_row_list:
                total_file_size += chunk_row.file_size
            self.file_size = total_file_size

    def _chunk_update_time(self):
        with self._thread_lock:
            longest_time_estimate = 0
            number_of_chunks_idle = 0
            for chunk_row in self.chunk_row_list:
                if chunk_row.time == 0:
                    number_of_chunks_idle += 1
                elif chunk_row.time > longest_time_estimate:
                    longest_time_estimate = chunk_row.time
            time_estimate = longest_time_estimate * (number_of_chunks_idle + 1)
            self.time = time_estimate

    def _chunk_update_current_time(self):
        with self._thread_lock:
            total_time = 0
            for chunk_row in self.chunk_row_list:
                if chunk_row.finished and not chunk_row.stopped:
                    total_time += chunk_row.ffmpeg.trim_settings.trim_duration
                else:
                    total_time += chunk_row.current_time
            self.current_time = total_time

    def _chunk_update_labels(self):
        for chunk_row in self.chunk_row_list:
            GLib.idle_add(chunk_row.update_labels)
        if self.audio_chunk_row is not None:
            GLib.idle_add(self.audio_chunk_row.update_labels)
        self._chunk_update_bitrate()
        self._chunk_update_speed()
        self._chunk_update_file_size()
        self._chunk_update_time()
        self._chunk_update_current_time()
        self._chunk_update_progress()
        self._update_labels()

    def _start_proc_timer(self):
        # Starts the task's timers for update all info. and runs until the task is done.
        update_row_thumbnail_thread = threading.Thread(target=self.update_thumbnail, args=(), daemon=True)
        update_row_thumbnail_thread.start()
        self._update_thumbnail_and_labels_until_finished(update_row_thumbnail_thread)
        self._update_active_row_labels()
        self._wait_for_update_row_thumbnail_thread(update_row_thumbnail_thread)

    def _update_thumbnail_and_labels_until_finished(self, update_row_thumbnail_thread):
        while not self.finished and not self.stopped and not self.idle:
            if self.paused:
                self.task_threading_event.wait()

            self._update_active_row_labels()
            self._re_run_update_row_thumbnail_thread(update_row_thumbnail_thread)

            time.sleep(1)
            self.proc_time += 1

    def _update_active_row_labels(self):
        if self.chunk_row_list:
            self._chunk_update_labels()
        else:
            self._update_labels()

    def _re_run_update_row_thumbnail_thread(self, update_row_thumbnail_thread):
        if not update_row_thumbnail_thread.is_alive():
            update_row_thumbnail_thread = threading.Thread(target=self.update_thumbnail, args=(), daemon=True)
            update_row_thumbnail_thread.start()

    def set_encoding_state(self):
        """Sets this Gtk.ListboxRow's widgets to the encoding state."""
        self.control_stack.set_visible_child(self.pause_button)
        self.stop_button.set_sensitive(True)

    def set_paused_state(self):
        """Sets this Gtk.ListboxRow's widgets to the encoding paused state."""
        self.control_stack.set_visible_child(self.start_button)
        self.stop_button.set_sensitive(False)

    def stop_and_remove_row(self):
        """Stops the running task and removes this Gtk.ListboxRow from it's parent Gtk.Listbox."""
        self.stopped = True
        if self.watch_folder is not None:
            self.watch_folder.stop_and_remove_instance(self._folder_path)

        GLib.idle_add(self.start_signal.on_start_button_clicked, None)
        GLib.idle_add(self._popdown_popovers)

        self._wait_for_info_threads()

        GLib.idle_add(self.active_page_handlers.remove_row, self)

    @staticmethod
    def _wait_for_update_row_thumbnail_thread(update_row_thumbnail_thread):
        if update_row_thumbnail_thread.is_alive():
            update_row_thumbnail_thread.join()

    @property
    def ffmpeg(self):
        return self._ffmpeg

    @ffmpeg.setter
    def ffmpeg(self, ffmpeg):
        self._ffmpeg = ffmpeg
        GLib.idle_add(self.active_row_folder_filename_label.set_text, ffmpeg.filename)

    @property
    def thumbnail(self):
        return self.preview_thumbnail

    @property
    def current_time(self):
        return self.task_information['current_time']

    @current_time.setter
    def current_time(self, current_time_in_seconds):
        if current_time_in_seconds == 0:
            return
        self.task_information['current_time'] = current_time_in_seconds

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
    def proc_time(self):
        return self.task_information['total_time']

    @proc_time.setter
    def proc_time(self, proc_time_value):
        self.task_information['total_time'] = proc_time_value

    @property
    def file_name(self):
        return self.filename_label.get_text()
