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
import os
import shutil
import threading
import time
import queue

from concurrent.futures import ThreadPoolExecutor

from render_watch.app_formatting.alias import AliasGenerator
from render_watch.helpers import encoder_helper, directory_helper
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.encoding.encoder import Encoder
from render_watch.encoding import preview
from render_watch.encoding.watch_folder import WatchFolder
from render_watch.startup import GLib


class EncoderQueue:
    """Queues Gtk.ListboxRow widgets from the active page to send to the encoder."""

    def __init__(self, preferences):
        self.preferences = preferences
        self.parallel_tasks_queue = queue.Queue()
        self.parallel_nvenc_tasks_queue = queue.Queue()
        self.standard_tasks_queue = queue.Queue()
        self.watch_folder_tasks_queue = queue.Queue()
        self.number_of_workers = preferences.parallel_tasks
        self.nvenc_max_workers = NvidiaHelper.nvenc_max_workers
        self.watch_folder = WatchFolder()
        self.__watch_folder_thread_lock = threading.Lock()
        self.parallel_tasks_enabled = False
        self.running_tasks = []
        self.__running_tasks_lock = threading.Lock()
        self.standard_tasks_startup_thread = threading.Thread(target=self._start_standard_tasks_thread,
                                                              args=(),
                                                              daemon=True)
        self.watch_folder_tasks_startup_thread = threading.Thread(target=self._start_watch_folder_tasks_thread,
                                                                  args=(),
                                                                  daemon=True)
        self.parallel_tasks_startup_thread = threading.Thread(target=self._start_parallel_tasks_thread,
                                                              args=(),
                                                              daemon=True)
        self.parallel_nvenc_tasks_startup_thread = threading.Thread(target=self._start_parallel_nvenc_tasks_thread,
                                                                    args=(),
                                                                    daemon=True)

        self.standard_tasks_startup_thread.start()
        self.watch_folder_tasks_startup_thread.start()
        self.parallel_tasks_startup_thread.start()
        if NvidiaHelper.is_nvenc_supported():
            self.parallel_nvenc_tasks_startup_thread.start()
        else:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def _start_standard_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=1) as future_executor:
            future_executor.submit(self._handle_standard_tasks)

    def _start_watch_folder_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=1) as future_executor:
            future_executor.submit(self._handle_watch_folder_tasks)

    def _start_parallel_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=self.number_of_workers) as future_executor:
            future_executor.map(self._handle_parallel_tasks, range(self.number_of_workers))

    def _start_parallel_nvenc_tasks_thread(self):
        try:
            with ThreadPoolExecutor(max_workers=self.nvenc_max_workers) as future_executor:
                future_executor.map(self._handle_parallel_nvenc_tasks, range(self.nvenc_max_workers))
        except ValueError:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def _handle_standard_tasks(self):
        # Waits for an available standard task and sends it to the encoder.
        while True:
            active_row = self.standard_tasks_queue.get()

            if not active_row:
                break

            self._add_to_running_tasks(active_row)
            self._run_standard_task_process(active_row)

            if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                GLib.idle_add(active_row.set_finished_state)
            if not active_row.ffmpeg.watch_folder:
                self._remove_from_running_tasks(active_row)
            self.standard_tasks_queue.task_done()

    def _run_standard_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:
                if active_row.ffmpeg.folder_state:
                    future_executor.submit(self._start_folder_task, active_row)
                else:
                    future_executor.submit(self._run_task, active_row)
                future_executor.submit(active_row.set_start_state)

    def _handle_watch_folder_tasks(self):
        # Waits for an available folder task and sends it to the encoder.
        while True:
            active_row = self.watch_folder_tasks_queue.get()

            if not active_row:
                break

            if self.preferences.watch_folder_wait_for_other_tasks:
                self._wait_for_all_tasks()

            self._add_to_running_tasks(active_row)
            self._run_watch_folder_task_process(active_row)
            self.watch_folder_tasks_queue.task_done()

    def _run_watch_folder_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=1) as future_executor:
                future_executor.submit(self._start_folder_task, active_row)

    def _handle_parallel_tasks(self, worker_id):  # Unused parameter required for this function
        # Waits for an available parallel task and sends it to the encoder.
        try:
            while True:
                active_row = self.parallel_tasks_queue.get()

                if not active_row:
                    break

                self._wait_for_standard_tasks()

                self._add_to_running_tasks(active_row)
                try:
                    self._run_parallel_task_process(active_row)
                except:
                    logging.exception('--- FAILED TO RUN PARALLEL TASK PROCESS ---')
                    continue

                if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                    GLib.idle_add(active_row.set_finished_state)
                if not active_row.ffmpeg.watch_folder:
                    self._remove_from_running_tasks(active_row)
                self.parallel_tasks_queue.task_done()
        except:
            logging.exception('--- PARALLEL TASKS THREAD FAILED ---')

    def _run_parallel_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:
                if active_row.ffmpeg.is_video_settings_nvenc():
                    self._remove_from_running_tasks(active_row)
                    self.parallel_nvenc_tasks_queue.put(active_row)
                    self.parallel_nvenc_tasks_queue.join()
                    self.parallel_tasks_queue.task_done()
                    return
                elif active_row.ffmpeg.folder_state:
                    future_executor.submit(self._start_folder_task, active_row)
                else:
                    future_executor.submit(self._run_task, active_row)
                future_executor.submit(active_row.set_start_state)

    def _handle_parallel_nvenc_tasks(self, worker_id):  # Unused parameter required for this function
        # Waits for an available NVENC task and sends it to the encoder.
        while True:
            active_row = self.parallel_nvenc_tasks_queue.get()

            if not active_row:
                break

            self._wait_until_nvenc_available(active_row)
            self._wait_for_standard_tasks()

            self._add_to_running_tasks(active_row)
            self._run_parallel_nvenc_task_process(active_row)

            if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                GLib.idle_add(active_row.set_finished_state)
            if not active_row.ffmpeg.watch_folder:
                self._remove_from_running_tasks(active_row)
            self.parallel_nvenc_tasks_queue.task_done()

    @staticmethod
    def _wait_until_nvenc_available(active_row):
        # Checks if we can start a new ffmpeg process using NVENC.
        # The system's driver may be blocking the creation of a new process.
        while not NvidiaHelper.is_nvenc_available() and not active_row.stopped:
            time.sleep(5)

    def _run_parallel_nvenc_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:
                if active_row.ffmpeg.folder_state:
                    future_executor.submit(self._start_folder_task, active_row)
                else:
                    future_executor.submit(self._run_task, active_row)
                future_executor.submit(active_row.set_start_state)

    def _run_task(self, active_row):
        # Sends a task to the encoder.
        if active_row.stopped:
            return

        ffmpeg = active_row.ffmpeg
        duration_in_seconds = self._get_ffmpeg_duration_in_seconds(ffmpeg)
        ffmpeg_args = self._get_ffmpeg_args(ffmpeg)
        encode_passes = len(ffmpeg_args)
        Encoder.start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, False)

    @staticmethod
    def _get_ffmpeg_duration_in_seconds(ffmpeg):
        if ffmpeg.trim_settings is None:
            return ffmpeg.duration_origin
        return ffmpeg.trim_settings.trim_duration

    @staticmethod
    def _get_ffmpeg_args(ffmpeg):
        ffmpeg_args = [ffmpeg.get_args()]

        if '&&' in ffmpeg_args[0]:
            first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
            second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
            ffmpeg_args = first_pass_args, second_pass_args

        return ffmpeg_args

    def _start_folder_task(self, active_row):
        if active_row.stopped:
            return

        if active_row.ffmpeg.watch_folder:
            threading.Thread(target=self._run_watch_folder_task, args=(active_row,), daemon=True).start()
        else:
            self._run_standard_folder_task(active_row)

    def _run_standard_folder_task(self, active_row):
        parent_ffmpeg = active_row.ffmpeg

        for file_path in directory_helper.get_files_in_directory(parent_ffmpeg.input_file,
                                                                 parent_ffmpeg.recursive_folder):
            if active_row.stopped:
                break

            child_ffmpeg = self._generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path)

            if not self._is_folder_task_valid(child_ffmpeg):
                continue
            directory_helper.fix_same_name_occurences(child_ffmpeg, self.preferences)
            if parent_ffmpeg.folder_auto_crop:
                preview.process_auto_crop(child_ffmpeg)

            self._run_standard_folder_task_encode_process(active_row, child_ffmpeg)

        active_row.ffmpeg = parent_ffmpeg

    @staticmethod
    def _generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path):
        # Creates a ffmpeg settings object for a file from a folder.
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)
        return child_ffmpeg

    @staticmethod
    def _is_folder_task_valid(ffmpeg):
        # Make sure the file from the folder is valid to encode.
        return encoder_helper.is_extension_valid(ffmpeg.input_file) and preview.set_info(ffmpeg)

    def _run_standard_folder_task_encode_process(self, active_row, child_ffmpeg):
        # Sends a standard folder task to the encoder.
        active_row.ffmpeg = child_ffmpeg
        duration_in_seconds = self._get_ffmpeg_duration_in_seconds(child_ffmpeg)
        ffmpeg_args = self._get_ffmpeg_args(child_ffmpeg)
        encode_passes = len(ffmpeg_args)
        Encoder.start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, True)

    def _run_watch_folder_task(self, active_row):
        try:
            parent_ffmpeg = active_row.ffmpeg
            folder_path = parent_ffmpeg.input_file
            self.watch_folder.add_folder_path(folder_path)
            active_row.watch_folder = self.watch_folder
            self._process_watch_folder_task(active_row, parent_ffmpeg, folder_path)
        except:
            logging.exception('--- FAILED TO RUN WATCH FOLDER TASK: ' + active_row.ffmpeg.input_file + ' ---')
        else:
            active_row.ffmpeg = parent_ffmpeg
        finally:
            self._remove_from_running_tasks(active_row)

    def _process_watch_folder_task(self, active_row, parent_ffmpeg, folder_path):
        while not active_row.stopped:
            if self.watch_folder.is_instance_empty(folder_path):
                GLib.idle_add(active_row.set_idle_state)
            active_row.started = False

            file_path = self.watch_folder.get_instance(folder_path)

            if not file_path:
                break

            if self.preferences.watch_folder_wait_for_other_tasks:
                self._wait_for_all_tasks()
            if not self.preferences.concurrent_watch_folder:
                self._wait_for_watch_folder_tasks()

            child_ffmpeg = self._generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path)

            if self._is_folder_task_valid(child_ffmpeg):
                continue
            directory_helper.fix_same_name_occurences(child_ffmpeg, self.preferences)
            if parent_ffmpeg.folder_auto_crop:
                preview.process_auto_crop(child_ffmpeg)

            self._run_watch_folder_task_encode_process(active_row, child_ffmpeg)

            if self.preferences.watch_folder_move_finished_to_done:
                self._move_to_done_folder(child_ffmpeg.input_file)

    @staticmethod
    def _generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path):
        # Creates a ffmpeg settings object for a file from the watch folder.
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)
        return child_ffmpeg

    def _run_watch_folder_task_encode_process(self, active_row, child_ffmpeg):
        # Sends the watch folder task to the encoder.
        active_row.ffmpeg = child_ffmpeg
        duration_in_seconds = self._get_ffmpeg_duration_in_seconds(child_ffmpeg)
        ffmpeg_args = self._get_ffmpeg_args(child_ffmpeg)
        encode_passes = len(ffmpeg_args)
        active_row.set_start_state()
        Encoder.start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, True)

    @staticmethod
    def _move_to_done_folder(input_file):
        # Moves a finished input file into a done folder.
        file_name = os.path.basename(input_file)
        input_file_path = os.path.dirname(input_file)
        done_file_path = os.path.join(input_file_path, 'done')
        done_file = os.path.join(done_file_path, file_name)

        if not os.path.exists(done_file_path):
            os.mkdir(done_file_path)
        shutil.move(input_file, done_file)

    def _wait_for_distributed_tasks(self):
        if not self.parallel_tasks_enabled and not self.parallel_tasks_queue.empty():
            self.parallel_tasks_queue.join()

    def _wait_for_standard_tasks(self):
        if self.parallel_tasks_enabled and not self.standard_tasks_queue.empty():
            self.standard_tasks_queue.join()

    def _wait_for_all_tasks(self):
        while not self.standard_tasks_queue.empty() or not self.parallel_tasks_queue.empty() or \
                not self.parallel_nvenc_tasks_queue.empty():
            self.standard_tasks_queue.join()
            self.parallel_tasks_queue.join()
            self.parallel_nvenc_tasks_queue.join()
        self.standard_tasks_queue.join()
        self.parallel_tasks_queue.join()
        self.parallel_nvenc_tasks_queue.join()

    def _wait_for_watch_folder_tasks(self):
        while self._check_watch_folder_task_running():
            time.sleep(5)

    def _check_watch_folder_task_running(self):
        with self.__watch_folder_thread_lock:
            for active_row in self.running_tasks:
                if active_row.watch_folder is not None and not active_row.idle and active_row.started:
                    return True
            return False

    def _add_to_running_tasks(self, active_row):
        with self.__running_tasks_lock:
            self.running_tasks.append(active_row)

    def _remove_from_running_tasks(self, active_row):
        with self.__running_tasks_lock:
            self.running_tasks.remove(active_row)

    def add_active_row(self, active_row):
        """Adds a Gtk.ListboxRow from the active page into the encoder queue.

        :param active_row:
            Gtk.ListboxRow from the active page's Gtk.Listbox.
        """
        if active_row.ffmpeg.watch_folder:
            self.watch_folder_tasks_queue.put(active_row)
        elif not self.parallel_tasks_enabled:
            self.standard_tasks_queue.put(active_row)
        else:
            self._add_active_row_to_parallel_tasks(active_row)

    def _add_active_row_to_parallel_tasks(self, active_row):
        if active_row.ffmpeg.is_video_settings_nvenc() and self.preferences.concurrent_nvenc:
            self.parallel_nvenc_tasks_queue.put(active_row)
        else:
            self.parallel_tasks_queue.put(active_row)

    def kill(self):
        """Stops all running tasks and empties all queues."""
        self._empty_queues()
        self._set_queues_stop_state()
        self._stop_running_tasks()

    def _empty_queues(self):
        self._empty_standard_tasks_queue()
        self._empty_distributed_tasks_queue()
        self._empty_distributed_nvenc_tasks_queue()
        self._empty_watch_folder_tasks_queue()

    def _empty_standard_tasks_queue(self):
        while not self.standard_tasks_queue.empty():
            self.standard_tasks_queue.get()

    def _empty_distributed_tasks_queue(self):
        while not self.parallel_tasks_queue.empty():
            self.parallel_tasks_queue.get()

    def _empty_distributed_nvenc_tasks_queue(self):
        while not self.parallel_nvenc_tasks_queue.empty():
            self.parallel_nvenc_tasks_queue.get()

    def _empty_watch_folder_tasks_queue(self):
        while not self.watch_folder_tasks_queue.empty():
            self.watch_folder_tasks_queue.get()

    def _set_queues_stop_state(self):
        self.standard_tasks_queue.put(False)
        self.watch_folder_tasks_queue.put(False)
        self._set_parallel_tasks_queue_stop_state()
        self._set_parallel_nvenc_tasks_queue_stop_state()

    def _set_parallel_tasks_queue_stop_state(self):
        for i in range(self.number_of_workers):
            self.parallel_tasks_queue.put(False)

    def _set_parallel_nvenc_tasks_queue_stop_state(self):
        for i in range(self.nvenc_max_workers):
            self.parallel_nvenc_tasks_queue.put(False)

    def _stop_running_tasks(self):
        for active_row in self.running_tasks:
            active_row.task_threading_event.set()
            active_row.stopped = True
