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
import logging
import threading
import time

from render_watch.encoding.encoder import Encoder
from render_watch.encoding.standard_encode_task import StandardEncodeTask
from render_watch.encoding.parallel_encode_task import ParallelEncodeTask
from render_watch.encoding.per_codec_parallel_encode_task import PerCodecParallelEncodeTask
from render_watch.encoding.parallel_nvenc_encode_task import ParallelNvencEncodeTask
from render_watch.encoding.folder_encode_task import FolderEncodeTask
from render_watch.helpers import ffmpeg_helper


class EncoderQueue:
    """
    Queues Gtk.ListboxRow widgets from the active page to sends them to the encoder.
    """

    def __init__(self, application_preferences):
        self.application_preferences = application_preferences
        self.is_parallel_tasks_enabled = False
        self.is_per_codec_parallel_tasks_enabled = application_preferences.is_per_codec_parallel_tasks_enabled
        self.running_tasks = []
        self._running_tasks_lock = threading.Lock()
        self.standard_encode_task = StandardEncodeTask(self)
        self.parallel_encode_task = ParallelEncodeTask(self, application_preferences)
        self.per_codec_parallel_encode_task = PerCodecParallelEncodeTask(self, application_preferences)
        self.parallel_nvenc_encode_task = ParallelNvencEncodeTask(self)
        self.folder_encode_task = FolderEncodeTask(self, application_preferences)

    def add_active_row(self, active_row):
        """
        Adds a Gtk.ListboxRow from the active page into the appropriate encode task queue.

        :param active_row: Gtk.ListboxRow from the active page's Gtk.Listbox.
        """
        if active_row.ffmpeg.watch_folder:
            self.folder_encode_task.add_task(active_row)
        elif self._is_per_codec_parallel_tasks_valid():
            self.per_codec_parallel_encode_task.add_task(active_row)
        elif self.is_parallel_tasks_enabled:
            self._add_active_row_to_parallel_tasks(active_row)
        else:
            self.standard_encode_task.add_task(active_row)

    def _is_per_codec_parallel_tasks_valid(self):
        return self.is_per_codec_parallel_tasks_enabled and self.is_parallel_tasks_enabled

    def _add_active_row_to_parallel_tasks(self, active_row):
        if active_row.ffmpeg.is_video_settings_nvenc() and self.application_preferences.is_concurrent_nvenc_enabled:
            self.parallel_nvenc_encode_task.add_task(active_row)
        else:
            self.parallel_encode_task.add_task(active_row)

    def add_to_running_tasks(self, active_row):
        with self._running_tasks_lock:
            self.running_tasks.append(active_row)

    def remove_from_running_tasks(self, active_row):
        try:
            with self._running_tasks_lock:
                self.running_tasks.remove(active_row)
        except ValueError:
            logging.exception('--- TASK NOT IN RUNNING TASKS LIST ---')

    def start_folder_task(self, active_row):
        self.folder_encode_task.start_folder_task(active_row)

    def start_parallel_nvenc_task(self, active_row, wait=True):
        self.parallel_nvenc_encode_task.add_task(active_row)

        if wait:
            self.parallel_nvenc_encode_task.join_queue()

    def wait_for_standard_tasks(self):
        if self.is_parallel_tasks_enabled or self.is_per_codec_parallel_tasks_enabled:
            self.standard_encode_task.join_queue()

    def wait_for_parallel_tasks(self):
        self._wait_for_per_codec_tasks_queue()
        self._wait_for_parallel_tasks_queue()

    def _wait_for_per_codec_tasks_queue(self):
        if not self.is_per_codec_parallel_tasks_enabled:
            self.per_codec_parallel_encode_task.join_queue()

    def _wait_for_parallel_tasks_queue(self):
        if not self.is_parallel_tasks_enabled:
            self.parallel_encode_task.join_queue()

    def wait_for_watch_folder_tasks(self):
        while self._check_watch_folder_task_running():
            time.sleep(5)

    def _check_watch_folder_task_running(self):
        with self.folder_encode_task.get_thread_lock():
            for active_row in self.running_tasks:
                if active_row.watch_folder and not active_row.idle and active_row.started:
                    return True
            return False

    def wait_for_all_tasks(self):
        while not self.standard_encode_task.is_queue_empty() \
                or not self.per_codec_parallel_encode_task.is_queue_empty() \
                or not self.parallel_encode_task.is_queue_empty() \
                or not self.parallel_nvenc_encode_task.is_queue_empty():
            self._join_on_all_encode_queues()
        self._join_on_all_encode_queues()

    def _join_on_all_encode_queues(self):
        self.standard_encode_task.join_queue()
        self.per_codec_parallel_encode_task.join_queue()
        self.parallel_encode_task.join_queue()
        self.parallel_nvenc_encode_task.join_queue()

    @staticmethod
    def run_encode_task(active_row):
        if active_row.stopped:
            return

        ffmpeg = active_row.ffmpeg

        duration_in_seconds = ffmpeg_helper.get_duration_in_seconds(ffmpeg)
        ffmpeg_args = ffmpeg_helper.get_parsed_ffmpeg_args(ffmpeg)
        encode_passes = len(ffmpeg_args)
        Encoder.start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes)

    @staticmethod
    def run_folder_encode_task(active_row, child_ffmpeg, watch_folder=False):
        active_row.ffmpeg = child_ffmpeg
        if watch_folder:
            active_row.set_start_state()

        duration_in_seconds = ffmpeg_helper.get_duration_in_seconds(child_ffmpeg)
        ffmpeg_args = ffmpeg_helper.get_parsed_ffmpeg_args(child_ffmpeg)
        encode_passes = len(ffmpeg_args)
        Encoder.start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, folder_state=True)

    def kill(self):
        """
        Stops all running encode tasks and empties all encode queues.
        """
        self._empty_encode_queues()
        self._set_encode_queues_stop_state()
        self._stop_running_tasks()

    def _empty_encode_queues(self):
        self.standard_encode_task.empty_queue()
        self.per_codec_parallel_encode_task.empty_queue()
        self.parallel_encode_task.empty_queue()
        self.parallel_nvenc_encode_task.empty_queue()
        self.folder_encode_task.empty_queue()

    def _set_encode_queues_stop_state(self):
        self.standard_encode_task.set_stop_state()
        self.per_codec_parallel_encode_task.set_stop_state()
        self.parallel_encode_task.set_stop_state()
        self.parallel_nvenc_encode_task.set_stop_state()
        self.folder_encode_task.set_stop_state()

    def _stop_running_tasks(self):
        for active_row in self.running_tasks:
            active_row.task_threading_event.set()
            active_row.stopped = True
