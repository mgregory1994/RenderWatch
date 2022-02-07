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
import queue

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.startup import GLib


class PerCodecParallelEncodeTask:
    """
    Queues parallel encode tasks on a per codec basis and runs them through the encoder.
    """

    def __init__(self, encoder_queue, application_preferences):
        self.encoder_queue = encoder_queue
        self.application_preferences = application_preferences
        self.per_codec_tasks_list = []
        self._per_codec_task_list_lock = threading.Lock()

        self._setup_codec_queues(application_preferences)

    def _setup_codec_queues(self, application_preferences):
        threading.Thread(target=self._setup_x264_codec_queue, args=(application_preferences,), daemon=True).start()
        threading.Thread(target=self._setup_x265_codec_queue, args=(application_preferences,), daemon=True).start()
        threading.Thread(target=self._setup_vp9_codec_queue, args=(application_preferences,), daemon=True).start()
        threading.Thread(target=self._setup_copy_codec_queue, args=(), daemon=True).start()

        if NvidiaHelper.is_nvenc_supported():
            threading.Thread(target=self._setup_nvenc_codec_queue, args=(), daemon=True).start()
        else:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def _setup_x264_codec_queue(self, application_preferences):
        self.x264_codec_queue = queue.Queue()
        self.number_of_x264_tasks = application_preferences.per_codec_parallel_tasks['x264']

        with ThreadPoolExecutor(max_workers=self.number_of_x264_tasks) as future_executor:
            future_executor.map(self._parse_per_codec_queue,
                                range(self.number_of_x264_tasks),
                                repeat(self.x264_codec_queue))

    def _setup_x265_codec_queue(self, application_preferences):
        self.x265_codec_queue = queue.Queue()
        self.number_of_x265_tasks = application_preferences.per_codec_parallel_tasks['x265']

        with ThreadPoolExecutor(max_workers=self.number_of_x265_tasks) as future_executor:
            future_executor.map(self._parse_per_codec_queue,
                                range(self.number_of_x265_tasks),
                                repeat(self.x265_codec_queue))

    def _setup_nvenc_codec_queue(self):
        try:
            self.nvenc_codec_queue = queue.Queue()
            self.number_of_nvenc_tasks = NvidiaHelper.nvenc_max_workers

            with ThreadPoolExecutor(max_workers=self.number_of_nvenc_tasks) as future_executor:
                future_executor.map(self._parse_per_codec_queue,
                                    range(self.number_of_nvenc_tasks),
                                    repeat(self.nvenc_codec_queue))
        except ValueError:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def _setup_vp9_codec_queue(self, application_preferences):
        self.vp9_codec_queue = queue.Queue()
        self.number_of_vp9_tasks = application_preferences.per_codec_parallel_tasks['vp9']

        with ThreadPoolExecutor(max_workers=self.number_of_vp9_tasks) as future_executor:
            future_executor.map(self._parse_per_codec_queue,
                                range(self.number_of_vp9_tasks),
                                repeat(self.vp9_codec_queue))

    def _setup_copy_codec_queue(self):
        self.copy_codec_queue = queue.Queue()
        self.number_of_copy_codec_tasks = 1

        with ThreadPoolExecutor(max_workers=self.number_of_copy_codec_tasks) as future_executor:
            future_executor.map(self._parse_per_codec_queue,
                                range(self.number_of_copy_codec_tasks),
                                repeat(self.copy_codec_queue))

    def _parse_per_codec_queue(self, worker_id, codec_queue):  # Unused parameter required for this function
        try:
            while True:
                if codec_queue.empty():
                    self._remove_codec_queue_from_per_codec_tasks_list(codec_queue)

                active_row = codec_queue.get()
                if not active_row:
                    break

                nvenc_skip = active_row.ffmpeg.is_video_settings_nvenc() \
                             and active_row.ffmpeg.folder_state \
                             and not active_row.ffmpeg.watch_folder

                try:
                    self.encoder_queue.wait_for_standard_tasks()
                    self._wait_for_current_codec_queue(codec_queue)

                    self.encoder_queue.add_to_running_tasks(active_row)
                    self._run_per_codec_encode_task(active_row, codec_queue)
                except:
                    logging.exception('--- FAILED TO RUN PER CODEC PARALLEL TASK PROCESS ---')
                finally:
                    if not nvenc_skip:
                        if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                            GLib.idle_add(active_row.set_finished_state)
                        if not active_row.ffmpeg.watch_folder:
                            self.encoder_queue.remove_from_running_tasks(active_row)

                    codec_queue.task_done()
        except:
            logging.exception('--- PER CODEC PARALLEL TASKS THREAD FAILED ---')

    def _wait_for_current_codec_queue(self, codec_queue):
        with self._per_codec_task_list_lock:
            current_codec_queue = self.per_codec_tasks_list[0]

            if codec_queue == current_codec_queue:
                return

        while not current_codec_queue.empty():
            current_codec_queue.join()
        current_codec_queue.join()

        self._wait_for_current_codec_queue(codec_queue)

    def _run_per_codec_encode_task(self, active_row, codec_queue):
        if active_row.stopped:
            return

        with ThreadPoolExecutor(max_workers=2) as future_executor:
            if active_row.ffmpeg.is_video_settings_nvenc():
                if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                    future_executor.submit(self.encoder_queue.start_parallel_nvenc_task, active_row)
                else:
                    self.encoder_queue.start_parallel_nvenc_task(active_row, wait=False)
                    return
            else:
                if active_row.ffmpeg.folder_state:
                    future_executor.submit(self.encoder_queue.start_folder_task, active_row)
                else:
                    future_executor.submit(self.encoder_queue.run_encode_task, active_row)

                future_executor.submit(active_row.set_start_state)

    def add_task(self, active_row):
        """
        Adds a Gtk.ListboxRow to the proper codec queue as a new task.
        """
        if active_row.ffmpeg.is_video_settings_x264():
            self.x264_codec_queue.put(active_row)
            self._add_codec_queue_to_per_codec_tasks_list(self.x264_codec_queue)
        elif active_row.ffmpeg.is_video_settings_x265():
            self.x265_codec_queue.put(active_row)
            self._add_codec_queue_to_per_codec_tasks_list(self.x265_codec_queue)
        elif active_row.ffmpeg.is_video_settings_nvenc():
            self.nvenc_codec_queue.put(active_row)
            self._add_codec_queue_to_per_codec_tasks_list(self.nvenc_codec_queue)
        elif active_row.ffmpeg.is_video_settings_vp9():
            self.vp9_codec_queue.put(active_row)
            self._add_codec_queue_to_per_codec_tasks_list(self.vp9_codec_queue)
        else:
            self.copy_codec_queue.put(active_row)
            self._add_codec_queue_to_per_codec_tasks_list(self.copy_codec_queue)

    def _add_codec_queue_to_per_codec_tasks_list(self, codec_queue):
        with self._per_codec_task_list_lock:
            if codec_queue not in self.per_codec_tasks_list:
                self.per_codec_tasks_list.append(codec_queue)

    def _remove_codec_queue_from_per_codec_tasks_list(self, codec_queue):
        with self._per_codec_task_list_lock:
            if codec_queue in self.per_codec_tasks_list:
                self.per_codec_tasks_list.remove(codec_queue)

    def set_stop_state(self):
        """
        Sends a stop task to all codec queues.
        """
        self._set_codec_queue_stop_state(self.x264_codec_queue, self.number_of_x264_tasks)
        self._set_codec_queue_stop_state(self.x265_codec_queue, self.number_of_x265_tasks)
        self._set_codec_queue_stop_state(self.vp9_codec_queue, self.number_of_vp9_tasks)
        self._set_codec_queue_stop_state(self.copy_codec_queue, self.number_of_copy_codec_tasks)

        if NvidiaHelper.is_nvenc_supported():
            self._set_codec_queue_stop_state(self.nvenc_codec_queue, self.number_of_nvenc_tasks)

    @staticmethod
    def _set_codec_queue_stop_state(codec_queue, number_of_tasks):
        for index in range(number_of_tasks):
            codec_queue.put(False)

    def is_queue_empty(self):
        return self.x264_codec_queue.empty() \
               and self.x265_codec_queue.empty() \
               and self.nvenc_codec_queue.empty() \
               and self.vp9_codec_queue.empty() \
               and self.copy_codec_queue.empty()

    def join_queue(self):
        self.x264_codec_queue.join()
        self.x265_codec_queue.join()
        self.nvenc_codec_queue.join()
        self.vp9_codec_queue.join()
        self.copy_codec_queue.join()

    def empty_queue(self):
        self._empty_codec_queue(self.x264_codec_queue)
        self._empty_codec_queue(self.x265_codec_queue)
        self._empty_codec_queue(self.vp9_codec_queue)
        self._empty_codec_queue(self.copy_codec_queue)

        if NvidiaHelper.is_nvenc_supported():
            self._empty_codec_queue(self.nvenc_codec_queue)

    @staticmethod
    def _empty_codec_queue(codec_queue):
        while not codec_queue.empty():
            codec_queue.get()
