# Copyright 2022 Michael Gregory
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
import queue
import signal
import subprocess
import threading
import re

from render_watch.ffmpeg import encoding, trim
from render_watch.helpers import format_converter
from render_watch import app_preferences


SHORT_BENCHMARK_DURATION = 15
LONG_BENCHMARK_DURATION = 30


class BenchmarkGenerator:
    """Class that queues encoding tasks and runs a benchmark for them."""

    def __int__(self, app_settings: app_preferences.Settings):
        """
        Initializes the BenchmarkGenerator class with the necessary variables for queueing encoding tasks and
        sending them to the benchmark queue.

        Parameters:
            app_settings: Application settings.
        """
        self.app_settings = app_settings
        self._benchmark_tasks_queue = queue.Queue()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Loop that runs a benchmark for each queued encoding task.
        try:
            while True:
                encoding_task, is_long_benchmark = self._benchmark_tasks_queue.get()

                if encoding_task:
                    encoding_task_copy = encoding_task.get_copy()
                    benchmark_length = self._get_benchmark_length(is_long_benchmark)
                    time_position = self._get_time_position(encoding_task_copy, benchmark_length)
                else:
                    logging.info('--- STOPPING BENCHMARK QUEUE LOOP ---')

                    break

                try:
                    self._setup_encoding_task(encoding_task_copy, time_position, benchmark_length)
                    self._process_benchmark_task(encoding_task, encoding_task_copy, benchmark_length)
                except:
                    logging.exception(''.join(['--- BENCHMARK TASK FAILED ---\n', encoding_task.input_file.file_path]))
                finally:
                    encoding_task.has_benchmark_started = False
                    encoding_task.is_benchmark_stopped = False
        except:
            logging.exception('--- BENCHMARK QUEUE LOOP FAILED ---')

    @staticmethod
    def _get_benchmark_length(is_long_benchmark: bool):
        # Returns the benchmark length to use depending on whether the user has selected the longer benchmark option.
        if is_long_benchmark:
            return LONG_BENCHMARK_DURATION
        return SHORT_BENCHMARK_DURATION

    @staticmethod
    def _get_time_position(encoding_task: encoding.Task, benchmark_length: int):
        # Returns the time position to use for the benchmark.
        if (encoding_task.input_file.duration / benchmark_length) >= 2:
            return encoding_task.input_file.duration / 2
        return 0

    def _setup_encoding_task(self, encoding_task: encoding.Task, time_position: int | float, benchmark_length: int):
        # Changes the encoding task's settings for running a benchmark.
        encoding_task.temp_output_file.name = 'benchmark'
        encoding_task.temp_output_file.extension = encoding_task.output_file.extension
        encoding_task.is_using_temp_output_file = True
        self._setup_encoding_task_trim_settings(encoding_task, time_position, benchmark_length)

    @staticmethod
    def _setup_encoding_task_trim_settings(encoding_task: encoding.Task,
                                           time_position: int | float,
                                           benchmark_length: int):
        # Sets the encoding task's trim settings for running a benchmark.
        trim_settings = trim.TrimSettings()
        trim_settings.start_time = time_position
        trim_settings.trim_duration = benchmark_length
        encoding_task.trim = trim_settings

    def _process_benchmark_task(self, encoding_task: encoding.Task,
                                encoding_task_copy: encoding.Task,
                                benchmark_length: int):
        # Gets the ffmpeg args for the benchmark task and sends them to the benchmark subprocess.
        benchmark_subprocess_args = encoding.FFmpegArgs.get_args(encoding_task_copy)

        encoding_task.has_benchmark_started = True

        if self._run_benchmark_subprocess(encoding_task, benchmark_subprocess_args, benchmark_length):
            raise Exception

    def _run_benchmark_subprocess(self,
                                  encoding_task: encoding.Task,
                                  benchmark_subprocess_args: list,
                                  benchmark_length: int) -> int:
        # Runs the benchmark subprocess for the benchmark task.
        for encode_pass, ffmpeg_args in enumerate(benchmark_subprocess_args):
            with subprocess.Popen(ffmpeg_args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as benchmark_process:
                while True:
                    if encoding_task.is_benchmark_stopped and benchmark_process.poll() is None:
                        os.kill(benchmark_process.pid, signal.SIGKILL)

                        break

                    stdout = benchmark_process.stdout.readline().strip()
                    if stdout == '' and benchmark_process.poll() is not None:
                        break

                    stdout_last_line = stdout

                    self._update_task_status(encoding_task, stdout, encode_pass)

        self._update_task_total_file_size_status(encoding_task, benchmark_length)
        self._update_task_time_estimate(encoding_task, len(benchmark_subprocess_args))
        self._log_benchmark_process_state(benchmark_process, encoding_task, stdout_last_line)

        encoding_task.benchmark_progress = 1.0

        return benchmark_process.wait()

    def _update_task_status(self, encoding_task: encoding.Task, stdout: str, encode_pass: int):
        # Updates the benchmark status variables of the encoding task.
        self._update_task_bitrate_status(encoding_task, stdout)
        self._update_task_file_size_status(encoding_task, stdout)
        self._update_task_speed_status(encoding_task, stdout)
        self._update_task_current_position_status(encoding_task, stdout)
        self._update_task_progress_status(encoding_task, encode_pass)

    @staticmethod
    def _update_task_bitrate_status(encoding_task: encoding.Task, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's bitrate status.
        try:
            bitrate = re.search(r'bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', stdout).group().split('=')[1]
            encoding_task.benchmark_bitrate = float(bitrate)
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_file_size_status(encoding_task: encoding.Task, stdout: str):
        # Uses the ffmpeg subprocess' stdout to update the encoding task's file size status.
        try:
            file_size_in_kilobytes = re.search(r'size=\d+|size=\s+\d+', stdout).group().split('=')[1]
            file_size_in_bytes = format_converter.get_bytes_from_kilobytes(int(file_size_in_kilobytes))
            encoding_task.benchmark_file_size = file_size_in_bytes
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_speed_status(encoding_task: encoding.Task, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's speed status.
        try:
            speed = re.search(r'speed=\d+\.\d+|speed=\s+\d+\.\d+', stdout).group().split('=')[1]
            encoding_task.benchmark_speed = float(speed)
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_current_position_status(encoding_task: encoding.Task, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's current position status.
        try:
            current_position_timecode = re.search(r'time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                                  stdout).group().split('=')[1]
            current_position_in_seconds = format_converter.get_seconds_from_timecode(current_position_timecode)
            encoding_task.benchmark_current_position = current_position_in_seconds
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_progress_status(encoding_task: encoding.Task, encode_pass: int):
        # Updates the benchmark task's progress status.
        try:
            current_time_position = encoding_task.benchmark_current_position
            input_file_duration = encoding_task.input_file.duration

            if encoding_task.is_video_2_pass():
                encode_passes = 2
            else:
                encode_passes = 1

            if encode_pass == 0:
                progress = (current_time_position / input_file_duration) / encode_passes
            else:
                progress = 0.5 + ((current_time_position / input_file_duration) / encode_passes)

            encoding_task.benchmark_progress = round(progress, 4)
        except (AttributeError, TypeError, ZeroDivisionError):
            pass

    @staticmethod
    def _update_task_total_file_size_status(encoding_task: encoding.Task, benchmark_duration: int):
        # Updates the benchmark task's file size status.
        ratio = encoding_task.input_file.duration / benchmark_duration
        encoding_task.benchmark_file_size = encoding_task.benchmark_file_size * ratio * format_converter.KILOBYTE_IN_BYTES

    @staticmethod
    def _update_task_time_estimate(encoding_task: encoding.Task, encode_passes: int):
        # Updates the benchmark task's time estimate.
        time_estimate = round((encoding_task.input_file.duration * encode_passes) / encoding_task.benchmark_speed)
        encoding_task.benchmark_time_estimate = time_estimate

    @staticmethod
    def _log_benchmark_process_state(benchmark_process: subprocess.Popen,
                                     encoding_task: encoding.Task,
                                     stdout_last_line: str):
        # Logs whether the benchmark task has been stopped or if the benchmark task failed.
        if encoding_task.is_benchmark_stopped:
            logging.info(''.join(['--- BENCHMARK PROCESS STOPPED: ', encoding_task.input_file.file_path, ' ---']))
        elif benchmark_process.wait():
            logging.error(''.join(['--- BENCHMARK PROCESS FAILED: ',
                                   encoding_task.input_file.file_path,
                                   ' ---\n',
                                   stdout_last_line]))

    def add_benchmark_task(self, encoding_task: encoding.Task, long_benchmark=False):
        """
        Adds the given encoding task to the benchmark tasks queue.

        Parameters:
            encoding_task: Encoding task to add to the benchmark tasks queue.
            long_benchmark: Boolean that represents whether to run a longer benchmark.

        Returns:
            None
        """
        self._benchmark_tasks_queue.put((encoding_task, long_benchmark))

    def kill(self):
        """
        Empties the benchmark queue and then adds a stop task to the benchmark queue.

        Returns:
            None
        """
        self._empty_queue()
        self._add_stop_task()

    def _empty_queue(self):
        # Empties the benchmark queue.
        while not self._benchmark_tasks_queue.empty():
            self._benchmark_tasks_queue.get()

    def _add_stop_task(self):
        # Adds a False boolean that represents the stop task for the benchmark queue loop.
        self._benchmark_tasks_queue.put(False)
