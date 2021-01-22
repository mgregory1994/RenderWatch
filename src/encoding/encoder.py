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

import queue
import threading
import subprocess
import time
import os
import shutil
import signal
import logging

from concurrent.futures import ThreadPoolExecutor
from app_formatting import format_converter
from app_formatting.alias import AliasGenerator
from startup.app_requirements import AppRequirements
from encoding import directory_helper
from encoding import encoder_helper
from encoding.watch_folder import WatchFolder
from encoding import preview
from startup import GLib


class Encoder:
    def __init__(self, preferences):
        self.preferences = preferences
        self.nvenc_max_workers = AppRequirements.nvenc_max_workers
        self.watch_folder = WatchFolder()
        self.parallel_tasks_queue = queue.Queue()
        self.parallel_nvenc_tasks_queue = queue.Queue()
        self.standard_tasks_queue = queue.Queue()
        self.watch_folder_tasks_queue = queue.Queue()
        self.standard_tasks_startup_thread = threading.Thread(target=self.__start_standard_tasks_thread, args=(),
                                                              daemon=True)
        self.watch_folder_tasks_startup_thread = threading.Thread(target=self.__start_watch_folder_tasks_thread, args=(),
                                                                  daemon=True)
        self.parallel_tasks_startup_thread = threading.Thread(target=self.__start_parallel_tasks_thread, args=(),
                                                              daemon=True)
        self.parallel_nvenc_tasks_startup_thread = threading.Thread(
            target=self.__start_parallel_nvenc_tasks_thread, args=(), daemon=True)
        self.__watch_folder_thread_lock = threading.Lock()
        self.number_of_workers = preferences.parallel_tasks
        self.parallel_tasks_enabled = False
        self.rows_tasked_currently = []
        self.__rows_tasked_currently_lock = threading.Lock()

        self.standard_tasks_startup_thread.start()
        self.watch_folder_tasks_startup_thread.start()
        self.parallel_tasks_startup_thread.start()

        if AppRequirements.is_nvenc_supported():
            self.parallel_nvenc_tasks_startup_thread.start()
        else:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def __start_standard_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=1) as future_executor:
            future_executor.submit(self.__start_standard_tasks)

    def __start_watch_folder_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=1) as future_executor:
            future_executor.submit(self.__start_watch_folder_tasks)

    def __start_parallel_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=self.number_of_workers) as future_executor:
            future_executor.map(self.__start_parallel_tasks, range(self.number_of_workers))

    def __start_parallel_nvenc_tasks_thread(self):
        try:
            with ThreadPoolExecutor(max_workers=self.nvenc_max_workers) as future_executor:
                future_executor.map(self.__start_parallel_nvenc_tasks, range(self.nvenc_max_workers))
        except ValueError:
            logging.info('--- NVENC ENCODING THREAD DISABLED ---')

    def __start_standard_tasks(self):
        while True:
            active_row = self.standard_tasks_queue.get()

            if not active_row:
                break

            self.__add_to_currently_tasked_rows(active_row)
            self.__start_standard_task_process(active_row)

            if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                GLib.idle_add(active_row.set_finished_state)

            if not active_row.ffmpeg.watch_folder:
                self.__remove_from_currently_tasked_rows(active_row)

            self.standard_tasks_queue.task_done()

    def __start_standard_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:

                if active_row.ffmpeg.folder_state:
                    future_executor.submit(self.__start_ffmpeg_folder_task, active_row)
                else:
                    future_executor.submit(self.__start_ffmpeg_task, active_row)

                future_executor.submit(active_row.set_start_state)

    def __start_watch_folder_tasks(self):
        while True:
            active_row = self.watch_folder_tasks_queue.get()

            if not active_row:
                break

            if self.preferences.watch_folder_wait_for_other_tasks:
                self.__wait_for_all_tasks()

            self.__add_to_currently_tasked_rows(active_row)
            self.__start_watch_folder_task_process(active_row)
            self.watch_folder_tasks_queue.task_done()

    def __start_watch_folder_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=1) as future_executor:
                future_executor.submit(self.__start_ffmpeg_folder_task, active_row)

    def __start_parallel_tasks(self, worker_id):
        try:
            while True:
                active_row = self.parallel_tasks_queue.get()

                if not active_row:
                    break

                self.__wait_for_standard_tasks()
                self.__add_to_currently_tasked_rows(active_row)

                try:
                    self.__start_parallel_task_process(active_row)
                except:
                    logging.exception('--- FAILED TO RUN PARALLEL TASK PROCESS ---')

                    continue

                if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                    GLib.idle_add(active_row.set_finished_state)

                if not active_row.ffmpeg.watch_folder:
                    self.__remove_from_currently_tasked_rows(active_row)

                self.parallel_tasks_queue.task_done()
        except:
            logging.exception('--- PARALLEL TASKS THREAD FAILED ---')

    def __start_parallel_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:

                if active_row.ffmpeg.is_video_settings_nvenc():
                    self.__remove_from_currently_tasked_rows(active_row)
                    self.parallel_nvenc_tasks_queue.put(active_row)
                    self.parallel_nvenc_tasks_queue.join()
                    self.parallel_tasks_queue.task_done()

                    return
                elif active_row.ffmpeg.folder_state:
                    future_executor.submit(self.__start_ffmpeg_folder_task, active_row)
                else:
                    future_executor.submit(self.__start_ffmpeg_task, active_row)

                future_executor.submit(active_row.set_start_state)

    def __start_parallel_nvenc_tasks(self, worker_id):
        while True:
            active_row = self.parallel_nvenc_tasks_queue.get()

            if not active_row:
                break

            self.__wait_until_nvenc_available(active_row)
            self.__wait_for_standard_tasks()
            self.__add_to_currently_tasked_rows(active_row)
            self.__start_parallel_nvenc_task_process(active_row)

            if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                GLib.idle_add(active_row.set_finished_state)

            if not active_row.ffmpeg.watch_folder:
                self.__remove_from_currently_tasked_rows(active_row)

            self.parallel_nvenc_tasks_queue.task_done()

    @staticmethod
    def __wait_until_nvenc_available(active_row):
        while not AppRequirements.is_nvenc_available() and not active_row.stopped:
            time.sleep(5)

    def __start_parallel_nvenc_task_process(self, active_row):
        if not active_row.stopped:
            with ThreadPoolExecutor(max_workers=2) as future_executor:

                if active_row.ffmpeg.folder_state:
                    future_executor.submit(self.__start_ffmpeg_folder_task, active_row)
                else:
                    future_executor.submit(self.__start_ffmpeg_task, active_row)

                future_executor.submit(active_row.set_start_state)

    def __start_ffmpeg_task(self, active_row):
        if active_row.stopped:
            return

        ffmpeg = active_row.ffmpeg
        duration_in_seconds = self.__get_ffmpeg_duration_in_seconds(ffmpeg)
        ffmpeg_args = self.__get_ffmpeg_args(ffmpeg)
        number_of_encode_passes = len(ffmpeg_args)

        self.__start_encode_process(active_row, ffmpeg_args, duration_in_seconds, number_of_encode_passes, False)

    @staticmethod
    def __get_ffmpeg_duration_in_seconds(ffmpeg):
        if ffmpeg.trim_settings is not None:
            duration_in_seconds = ffmpeg.trim_settings.trim_duration
        else:
            duration_in_seconds = ffmpeg.duration_origin

        return duration_in_seconds

    @staticmethod
    def __get_ffmpeg_args(ffmpeg):
        ffmpeg_args = [ffmpeg.get_args()]

        if '&&' in ffmpeg_args[0]:
            first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
            second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
            ffmpeg_args = first_pass_args, second_pass_args

        return ffmpeg_args

    def __start_ffmpeg_folder_task(self, active_row):
        if active_row.stopped:
            return

        if active_row.ffmpeg.watch_folder:
            threading.Thread(target=self.__start_watch_folder_task, args=(active_row,), daemon=True).start()
        else:
            self.__start_standard_folder_task(active_row)

    def __start_standard_folder_task(self, active_row):
        parent_ffmpeg = active_row.ffmpeg

        for file_path in directory_helper.get_files_in_directory(parent_ffmpeg.input_file, parent_ffmpeg.recursive_folder):
            if active_row.stopped:
                break

            child_ffmpeg = self.__generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path)

            if self.__is_folder_task_ffmpeg_not_valid(child_ffmpeg):
                continue

            directory_helper.fix_same_name_occurences(child_ffmpeg, self.preferences)

            if parent_ffmpeg.folder_auto_crop:
                preview.process_auto_crop(child_ffmpeg)

            self.__setup_and_start_standard_folder_task_encode_process(active_row, child_ffmpeg)

        active_row.ffmpeg = parent_ffmpeg

    @staticmethod
    def __generate_child_ffmpeg_from_standard_folder_task(parent_ffmpeg, file_path):
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)

        return child_ffmpeg

    @staticmethod
    def __is_folder_task_ffmpeg_not_valid(ffmpeg):
        return not encoder_helper.is_input_valid(ffmpeg.input_file) or not preview.set_info(ffmpeg)

    def __setup_and_start_standard_folder_task_encode_process(self, active_row, child_ffmpeg):
        active_row.ffmpeg = child_ffmpeg
        duration_in_seconds = self.__get_ffmpeg_duration_in_seconds(child_ffmpeg)
        ffmpeg_args = self.__get_ffmpeg_args(child_ffmpeg)
        number_of_encode_passes = len(ffmpeg_args)

        self.__start_encode_process(active_row, ffmpeg_args, duration_in_seconds, number_of_encode_passes, True)

    def __start_watch_folder_task(self, active_row):
        try:
            parent_ffmpeg = active_row.ffmpeg
            folder_path = parent_ffmpeg.input_file

            self.watch_folder.add_folder_path(folder_path)

            active_row.watch_folder = self.watch_folder

            self.__process_watch_folder_task(active_row, parent_ffmpeg, folder_path)
        except:
            logging.exception('--- FAILED TO RUN WATCH FOLDER TASK: ' + active_row.ffmpeg.input_file + ' ---')
        else:
            active_row.ffmpeg = parent_ffmpeg
        finally:
            self.__remove_from_currently_tasked_rows(active_row)

    def __process_watch_folder_task(self, active_row, parent_ffmpeg, folder_path):
        while not active_row.stopped:
            if self.watch_folder.is_instance_empty(folder_path):
                GLib.idle_add(active_row.set_idle_state)

            active_row.started = False
            file_path = self.watch_folder.get_instance(folder_path)

            if not file_path:
                break

            if self.preferences.watch_folder_wait_for_other_tasks:
                self.__wait_for_all_tasks()

            if not self.preferences.concurrent_watch_folder:
                self.__wait_for_watch_folder_tasks()

            child_ffmpeg = self.__generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path)

            if self.__is_folder_task_ffmpeg_not_valid(child_ffmpeg):
                continue

            directory_helper.fix_same_name_occurences(child_ffmpeg, self.preferences)

            if parent_ffmpeg.folder_auto_crop:
                preview.process_auto_crop(child_ffmpeg)

            self.__setup_and_start_watch_folder_task_encode_process(active_row, child_ffmpeg)

            if self.preferences.watch_folder_move_finished_to_done:
                self.__move_watch_input_to_done_folder(child_ffmpeg.input_file)

    @staticmethod
    def __generate_child_ffmpeg_from_watch_folder_task(parent_ffmpeg, file_path):
        child_ffmpeg = parent_ffmpeg.get_copy()
        child_ffmpeg.input_file = file_path
        child_ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(child_ffmpeg.filename)

        return child_ffmpeg

    def __setup_and_start_watch_folder_task_encode_process(self, active_row, child_ffmpeg):
        active_row.ffmpeg = child_ffmpeg
        duration_in_seconds = self.__get_ffmpeg_duration_in_seconds(child_ffmpeg)
        ffmpeg_args = self.__get_ffmpeg_args(child_ffmpeg)
        number_of_encode_passes = len(ffmpeg_args)

        active_row.set_start_state()
        self.__start_encode_process(active_row, ffmpeg_args, duration_in_seconds, number_of_encode_passes, True)

    @staticmethod
    def __move_watch_input_to_done_folder(input_file):
        file_name = os.path.basename(input_file)
        input_file_path = os.path.dirname(input_file)
        done_file_path = os.path.join(input_file_path, 'done')
        done_file = os.path.join(done_file_path, file_name)

        if not os.path.exists(done_file_path):
            os.mkdir(done_file_path)

        shutil.move(input_file, done_file)

    def __wait_for_distributed_tasks(self):
        if not self.parallel_tasks_enabled and not self.parallel_tasks_queue.empty():
            self.parallel_tasks_queue.join()

    def __wait_for_standard_tasks(self):
        if self.parallel_tasks_enabled and not self.standard_tasks_queue.empty():
            self.standard_tasks_queue.join()

    def __wait_for_all_tasks(self):
        while not self.standard_tasks_queue.empty() or not self.parallel_tasks_queue.empty() or \
                not self.parallel_nvenc_tasks_queue.empty():
            self.standard_tasks_queue.join()
            self.parallel_tasks_queue.join()
            self.parallel_nvenc_tasks_queue.join()

        self.standard_tasks_queue.join()
        self.parallel_tasks_queue.join()
        self.parallel_nvenc_tasks_queue.join()

    def __wait_for_watch_folder_tasks(self):
        while self.__check_watch_folder_task_running():
            time.sleep(5)

    def __check_watch_folder_task_running(self):
        with self.__watch_folder_thread_lock:
            for active_row in self.rows_tasked_currently:
                if active_row.watch_folder is not None and not active_row.idle and active_row.started:
                    return True

            return False

    def __add_to_currently_tasked_rows(self, active_row):
        with self.__rows_tasked_currently_lock:
            self.rows_tasked_currently.append(active_row)

    def __remove_from_currently_tasked_rows(self, active_row):
        with self.__rows_tasked_currently_lock:
            self.rows_tasked_currently.remove(active_row)

    def add_active_listbox_row(self, active_listbox_row):
        if active_listbox_row.ffmpeg.watch_folder:
            self.watch_folder_tasks_queue.put(active_listbox_row)
        elif not self.parallel_tasks_enabled:
            self.standard_tasks_queue.put(active_listbox_row)
        else:
            self.__add_active_listbox_row_to_parallel_tasks(active_listbox_row)

    def __add_active_listbox_row_to_parallel_tasks(self, active_listbox_row):
        if active_listbox_row.ffmpeg.is_video_settings_nvenc() and self.preferences.concurrent_nvenc:
            self.parallel_nvenc_tasks_queue.put(active_listbox_row)
        else:
            self.parallel_tasks_queue.put(active_listbox_row)

    def kill(self):
        self.__empty_queues()
        self.__setup_queues_stop_state()
        self.__stop_rows_tasked_currently()

    def __empty_queues(self):
        self.__empty_standard_tasks_queue()
        self.__empty_distributed_tasks_queue()
        self.__empty_distributed_nvenc_tasks_queue()
        self.__empty_watch_folder_tasks_queue()

    def __empty_standard_tasks_queue(self):
        while not self.standard_tasks_queue.empty():
            self.standard_tasks_queue.get()

    def __empty_distributed_tasks_queue(self):
        while not self.parallel_tasks_queue.empty():
            self.parallel_tasks_queue.get()

    def __empty_distributed_nvenc_tasks_queue(self):
        while not self.parallel_nvenc_tasks_queue.empty():
            self.parallel_nvenc_tasks_queue.get()

    def __empty_watch_folder_tasks_queue(self):
        while not self.watch_folder_tasks_queue.empty():
            self.watch_folder_tasks_queue.get()

    def __setup_queues_stop_state(self):
        self.standard_tasks_queue.put(False)
        self.watch_folder_tasks_queue.put(False)
        self.__setup_distributed_tasks_queue_stop_state()
        self.__setup_distributed_nvenc_tasks_queue_stop_state()

    def __setup_distributed_tasks_queue_stop_state(self):
        for i in range(self.number_of_workers):
            self.parallel_tasks_queue.put(False)

    def __setup_distributed_nvenc_tasks_queue_stop_state(self):
        for i in range(self.nvenc_max_workers):
            self.parallel_nvenc_tasks_queue.put(False)

    def __stop_rows_tasked_currently(self):
        for active_row in self.rows_tasked_currently:
            active_row.task_threading_event.set()
            active_row.stopped = True

    def __start_encode_process(self, active_row, ffmpeg_args, duration_in_seconds, number_of_encode_passes, folder_state):
        for encode_pass, args in enumerate(ffmpeg_args):
            with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                                  bufsize=1) as ffmpeg_process:
                while True:
                    if active_row.stopped and ffmpeg_process.poll() is None:
                        ffmpeg_process.terminate()

                        break
                    elif active_row.paused and ffmpeg_process.poll() is None:
                        self.__pause_ffmpeg_task(ffmpeg_process, active_row)

                    ffmpeg_process_stdout = ffmpeg_process.stdout.readline().strip().split('=')

                    if ffmpeg_process_stdout == [''] and ffmpeg_process.poll() is not None:
                        break

                    last_line = ffmpeg_process_stdout

                    try:
                        self.__evaluate_encode_process_state(active_row, ffmpeg_process_stdout, encode_pass,
                                                             number_of_encode_passes, duration_in_seconds)
                    except:
                        continue

        self.__evaluate_encode_process_finished(active_row, ffmpeg_process, last_line)
        self.__set_encode_process_finished(active_row, folder_state)

    def __evaluate_encode_process_state(self, active_row, ffmpeg_process_stdout, encode_pass, number_of_encode_passes,
                                        duration_in_seconds):
        bitrate = self.__get_bitrate_as_float(ffmpeg_process_stdout)
        file_size_in_kilobytes = self.__get_file_size_in_kilobytes(ffmpeg_process_stdout)
        current_time_in_seconds = self.__get_current_time_in_seconds(ffmpeg_process_stdout)
        speed_as_float = self.__get_speed_as_float(ffmpeg_process_stdout)

        if encode_pass == 0:
            progress = (current_time_in_seconds / duration_in_seconds) / number_of_encode_passes
        else:
            progress = .5 + ((current_time_in_seconds / duration_in_seconds) / number_of_encode_passes)

        if speed_as_float is not None:
            active_row.time = self.__get_time_estimate(current_time_in_seconds, duration_in_seconds,
                                                       speed_as_float, encode_pass,
                                                       number_of_encode_passes)

        if file_size_in_kilobytes is not None:
            active_row.file_size = self.__convert_file_size_in_kilobytes_to_bytes(file_size_in_kilobytes)

        active_row.bitrate = bitrate
        active_row.speed = speed_as_float
        active_row.progress = progress
        active_row.current_time = current_time_in_seconds

    @staticmethod
    def __evaluate_encode_process_finished(active_row, ffmpeg_process, last_line):
        ffmpeg_process_return_code = ffmpeg_process.wait()

        if not active_row.stopped and ffmpeg_process_return_code != 0:
            active_row.failed = True

            logging.error('--- ENCODE FAILED: ' + active_row.ffmpeg.input_file + ' ---\n'
                          + last_line)
        elif active_row.stopped:
            logging.info('--- ENCODE STOPPED: ' + active_row.ffmpeg.input_file + ' ---')

    @staticmethod
    def __set_encode_process_finished(active_row, folder_state):
        active_row.progress = 1.0

        if not folder_state:
            GLib.idle_add(active_row.set_finished_state)

    @staticmethod
    def __pause_ffmpeg_task(ffmpeg_process, active_row):
        os.kill(ffmpeg_process.pid, signal.SIGSTOP)
        active_row.task_threading_event.wait()
        os.kill(ffmpeg_process.pid, signal.SIGCONT)

    @staticmethod
    def __get_bitrate_as_float(ffmpeg_process_stdout):
        try:
            bitrate_identifier = 'kbits/s'
            bitrate_index = None

            for index, stdout_chunk in enumerate(ffmpeg_process_stdout):
                if bitrate_identifier in stdout_chunk:
                    bitrate_index = index

            if bitrate_index is not None:
                bitrate = ffmpeg_process_stdout[bitrate_index].split(' ')

                while '' in bitrate:
                    bitrate.remove('')

                return float(bitrate[0].split('k')[0])
            else:
                return 0.0
        except:
            return 0.0

    @staticmethod
    def __get_speed_as_float(ffmpeg_process_stdout):
        try:
            speed_identifier = 'x'
            speed_index = None

            for index, stdout_chunk in enumerate(ffmpeg_process_stdout):
                if speed_identifier in stdout_chunk:
                    speed_index = index

            if speed_index is not None:
                speed = ffmpeg_process_stdout[speed_index]

                return float(speed.split('x')[0])
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_file_size_in_kilobytes(ffmpeg_process_stdout):
        try:
            file_size_identifier = 'kB'
            file_size_index = None

            for index, stdout_chunk in enumerate(ffmpeg_process_stdout):
                if file_size_identifier in stdout_chunk:
                    file_size_index = index

            if file_size_index is not None:
                file_size_line = ffmpeg_process_stdout[file_size_index].split(' ')
                file_size = file_size_line[-2].split('k')[0]

                return int(file_size)
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_current_time_in_seconds(ffmpeg_process_stdout):
        try:
            current_time_identifier = 'bitrate'
            current_time_index = None

            for index, stdout_chunk in enumerate(ffmpeg_process_stdout):
                if current_time_identifier in stdout_chunk:
                    current_time_index = index

            if current_time_index is not None:
                current_time = ffmpeg_process_stdout[current_time_index].split(' ')

                return format_converter.get_seconds_from_timecode(current_time[0])
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_time_estimate(current_time_in_seconds, duration_in_seconds, speed_as_float, encode_pass,
                            number_of_encode_passes):
        try:
            if encode_pass == 0:
                duration_in_seconds *= number_of_encode_passes

            if current_time_in_seconds >= duration_in_seconds:
                time_estimate = 0
            else:
                time_estimate = (duration_in_seconds - current_time_in_seconds) / speed_as_float

            return time_estimate
        except:
            return 0

    @staticmethod
    def __convert_file_size_in_kilobytes_to_bytes(file_size_in_kilobytes):
        total_bytes = file_size_in_kilobytes * 1000

        return total_bytes
