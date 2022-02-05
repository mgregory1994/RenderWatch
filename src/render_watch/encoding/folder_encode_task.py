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
import queue

from concurrent.futures import ThreadPoolExecutor

from render_watch.app_formatting.alias import AliasGenerator
from render_watch.helpers import encoder_helper, directory_helper, auto_crop_helper
from render_watch.ffmpeg.input_information import InputInformation
from render_watch.encoding.watch_folder import WatchFolder
from render_watch.startup import GLib


class FolderEncodeTask:
    """
    Queues watch folder encode tasks and runs them through the encoder.
    """

    def __init__(self, encoder_queue, application_preferences):
        self.encoder_queue = encoder_queue
        self.application_preferences = application_preferences
        self.folder_tasks_queue = queue.Queue()
        self.watch_folder = WatchFolder()
        self._folder_tasks_thread_lock = threading.Lock()

        self.folder_tasks_startup_thread = threading.Thread(target=self._start_folder_tasks_thread,
                                                            args=(),
                                                            daemon=True)
        self.folder_tasks_startup_thread.start()

    def _start_folder_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=1) as future_executor:
            future_executor.submit(self._parse_folder_tasks_queue)

    def _parse_folder_tasks_queue(self):
        while True:
            active_row = self.folder_tasks_queue.get()
            if not active_row:
                break

            if self.application_preferences.is_watch_folder_wait_for_tasks_enabled:
                self.encoder_queue.wait_for_all_tasks()

            self.encoder_queue.add_to_running_tasks(active_row)
            self._run_folder_encode_task(active_row)

            self.folder_tasks_queue.task_done()

    def _run_folder_encode_task(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=1) as future_executor:
                future_executor.submit(self.start_folder_task, active_row)

    def start_folder_task(self, active_row):
        if active_row.stopped:
            return

        if active_row.ffmpeg.watch_folder:
            threading.Thread(target=self._parse_watch_folder_task, args=(active_row,), daemon=True).start()
        else:
            self._run_standard_folder_encode_task(active_row)

    def _parse_watch_folder_task(self, active_row):
        parent_ffmpeg = active_row.ffmpeg

        try:
            folder_path = parent_ffmpeg.input_file
            self.watch_folder.add_folder_path(folder_path)
            active_row.watch_folder = self.watch_folder
            self._run_watch_folder_encode_task(active_row, parent_ffmpeg, folder_path)
        except:
            logging.exception('--- FAILED TO RUN WATCH FOLDER TASK: ' + active_row.ffmpeg.input_file + ' ---')
        finally:
            active_row.ffmpeg = parent_ffmpeg

            self.encoder_queue.remove_from_running_tasks(active_row)

    def _run_watch_folder_encode_task(self, active_row, parent_ffmpeg, folder_path):
        while True:
            if active_row.stopped:
                break

            if self.watch_folder.is_instance_empty(folder_path):
                GLib.idle_add(active_row.set_idle_state)
            active_row.started = False

            file_path = self.watch_folder.get_instance(folder_path)
            if not file_path:
                break

            if self.application_preferences.is_watch_folder_wait_for_tasks_enabled:
                self.encoder_queue.wait_for_all_tasks()
            if not self.application_preferences.is_concurrent_watch_folder_enabled:
                self.encoder_queue.wait_for_watch_folder_tasks()

            child_ffmpeg = self._generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path)
            if self._is_folder_task_valid(child_ffmpeg):
                directory_helper.fix_same_name_occurences(child_ffmpeg, self.application_preferences)

                if parent_ffmpeg.folder_auto_crop:
                    auto_crop_helper.process_auto_crop(child_ffmpeg)

                self.encoder_queue.run_folder_encode_task(active_row, child_ffmpeg, watch_folder=True)

                if self.application_preferences.is_watch_folder_move_tasks_to_done_enabled:
                    self._move_input_file_to_done_folder(child_ffmpeg.input_file)

    @staticmethod
    def _generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path):
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)
        return child_ffmpeg

    @staticmethod
    def _is_folder_task_valid(child_ffmpeg):
        return encoder_helper.is_file_extension_valid(child_ffmpeg.input_file) \
               and InputInformation.generate_input_information(child_ffmpeg)

    @staticmethod
    def _move_input_file_to_done_folder(input_file_path):
        file_name = os.path.basename(input_file_path)
        input_file_path = os.path.dirname(input_file_path)
        done_file_path = os.path.join(input_file_path, 'done')
        done_file = os.path.join(done_file_path, file_name)

        if not os.path.exists(done_file_path):
            os.mkdir(done_file_path)

        shutil.move(input_file_path, done_file)

    def _run_standard_folder_encode_task(self, active_row):
        parent_ffmpeg = active_row.ffmpeg

        for file_path in directory_helper.get_files_in_directory(parent_ffmpeg.input_file,
                                                                 parent_ffmpeg.recursive_folder):
            if active_row.stopped:
                break

            child_ffmpeg = self._generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path)
            if self._is_folder_task_valid(child_ffmpeg):
                directory_helper.fix_same_name_occurences(child_ffmpeg, self.application_preferences)

                if parent_ffmpeg.folder_auto_crop:
                    auto_crop_helper.process_auto_crop(child_ffmpeg)

                self.encoder_queue.run_folder_encode_task(active_row, child_ffmpeg)

        active_row.ffmpeg = parent_ffmpeg

    @staticmethod
    def _generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path):
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)
        return child_ffmpeg

    def add_task(self, active_row):
        """
        Adds a Gtk.ListboxRow to the encoder queue as a new task.
        """
        self.folder_tasks_queue.put(active_row)

    def set_stop_state(self):
        """
        Sends a stop task to the encoder queue.
        """
        self.folder_tasks_queue.put(False)

    def get_thread_lock(self):
        return self._folder_tasks_thread_lock

    def is_queue_empty(self):
        return self.folder_tasks_queue.empty()

    def join_queue(self):
        self.folder_tasks_queue.join()

    def empty_queue(self):
        while not self.is_queue_empty():
            self.folder_tasks_queue.get()
