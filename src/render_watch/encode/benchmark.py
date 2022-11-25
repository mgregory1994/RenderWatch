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

from render_watch.ffmpeg import task, video_codec
from render_watch.helpers import ffmpeg_helper, format_converter
from render_watch import app_preferences, logger


class BenchmarkGenerator:
    """Class that queues encoding tasks and runs a benchmark for them."""

    def __init__(self, app_settings: app_preferences.Settings):
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
                benchmark_task = self._benchmark_tasks_queue.get()

                if not benchmark_task:
                    logger.log_stopping_benchmark_queue_loop()

                    break

                try:
                    benchmark_task.reset()
                    self._process_benchmark_task(benchmark_task)
                except:
                    benchmark_task.has_failed = True

                    logger.log_benchmark_task_failed(benchmark_task.encode_task.input_file.file_path)
                finally:
                    benchmark_task.is_done = True
        except:
            logging.exception('--- BENCHMARK QUEUE LOOP FAILED ---')

    def _process_benchmark_task(self, benchmark_task: task.Benchmark):
        # Gets the ffmpeg args for the benchmark task and sends them to the benchmark subprocess.
        benchmark_subprocess_args = ffmpeg_helper.Args.get_args(benchmark_task.encode_task)

        benchmark_task.has_started = True

        if self._run_benchmark_subprocess(benchmark_task, benchmark_subprocess_args):
            if not benchmark_task.is_stopped:
                raise Exception

    def _run_benchmark_subprocess(self, benchmark_task: task.Benchmark, benchmark_subprocess_args: list) -> int:
        # Runs the benchmark subprocess for the benchmark task.
        for encode_pass, ffmpeg_args in enumerate(benchmark_subprocess_args):
            with subprocess.Popen(ffmpeg_args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as benchmark_process:
                while True:
                    if benchmark_task.is_stopped and benchmark_process.poll() is None:
                        os.kill(benchmark_process.pid, signal.SIGKILL)

                        break

                    stdout = benchmark_process.stdout.readline().strip()
                    if stdout == '' and benchmark_process.poll() is not None:
                        break

                    stdout_last_line = stdout

                    self._update_task_status(benchmark_task, stdout, encode_pass)

        self._update_task_total_file_size(benchmark_task)
        self._update_task_encode_time_estimate(benchmark_task, len(benchmark_subprocess_args))
        self._log_benchmark_process_state(benchmark_process, benchmark_task, stdout_last_line)

        benchmark_task.progress = 1.0

        return benchmark_process.wait()

    def _update_task_status(self, benchmark_task: task.Benchmark, stdout: str, encode_pass: int):
        # Updates the benchmark status variables of the encoding task.
        self._update_task_bitrate(benchmark_task, stdout)
        self._update_task_file_size(benchmark_task, stdout)
        self._update_task_speed(benchmark_task, stdout)
        self._update_task_current_time_position(benchmark_task, stdout)
        self._update_task_progress(benchmark_task, encode_pass)

    @staticmethod
    def _update_task_bitrate(benchmark_task: task.Benchmark, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's bitrate status.
        try:
            bitrate = re.search(r'bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', stdout).group().split('=')[1]
            benchmark_task.bitrate = float(bitrate)
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_file_size(benchmark_task: task.Benchmark, stdout: str):
        # Uses the ffmpeg subprocess' stdout to update the encoding task's file size status.
        try:
            file_size_in_kilobytes = re.search(r'size=\d+|size=\s+\d+', stdout).group().split('=')[1]
            file_size_in_bytes = format_converter.get_bytes_from_kilobytes(int(file_size_in_kilobytes))
            benchmark_task.file_size = file_size_in_bytes
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_speed(benchmark_task: task.Benchmark, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's speed status.
        try:
            speed = re.search(r'speed=\d+\.\d+|speed=\s+\d+\.\d+', stdout).group().split('=')[1]
            benchmark_task.speed = float(speed)
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_current_time_position(benchmark_task: task.Benchmark, stdout: str):
        # Uses the benchmark subprocess' stdout to update the benchmark task's current position status.
        try:
            current_position_timecode = re.search(r'time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                                  stdout).group().split('=')[1]
            current_position_in_seconds = format_converter.get_seconds_from_timecode(current_position_timecode)
            benchmark_task.current_time_position = current_position_in_seconds
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_task_progress(benchmark_task: task.Benchmark, encode_pass: int):
        # Updates the benchmark task's progress status.
        try:
            current_time_position = benchmark_task.current_time_position

            if video_codec.is_codec_2_pass(benchmark_task.encode_task):
                encode_passes = 2
            else:
                encode_passes = 1

            if encode_pass == 0:
                progress = (current_time_position / benchmark_task.preview_duration) / encode_passes
            else:
                progress = 0.5 + ((current_time_position / benchmark_task.preview_duration) / encode_passes)

            benchmark_task.progress = round(progress, 4)
        except (AttributeError, TypeError, ZeroDivisionError):
            pass

    @staticmethod
    def _update_task_total_file_size(benchmark_task: task.Benchmark):
        # Updates the benchmark task's file size status.
        ratio = benchmark_task.encode_task.input_file.duration / benchmark_task.preview_duration
        benchmark_task.file_size = benchmark_task.file_size * ratio

    @staticmethod
    def _update_task_encode_time_estimate(benchmark_task: task.Benchmark, encode_passes: int):
        # Updates the benchmark task's time estimate.
        time_estimate = round((benchmark_task.encode_task.input_file.duration * encode_passes) / benchmark_task.speed)
        benchmark_task.encode_time_estimate = time_estimate

    @staticmethod
    def _log_benchmark_process_state(benchmark_process: subprocess.Popen,
                                     benchmark_task: task.Benchmark,
                                     stdout_last_line: str):
        # Logs whether the benchmark task has been stopped or if the benchmark task failed.
        if benchmark_task.is_stopped:
            logger.log_benchmark_process_stopped(benchmark_task.encode_task.input_file.file_path)
        elif benchmark_process.wait():
            logger.log_benchmark_process_failed(benchmark_task.encode_task.input_file.file_path, stdout_last_line)

    def add_benchmark_task(self, benchmark_task: task.Benchmark):
        """
        Adds the given encoding task to the benchmark tasks queue.

        Parameters:
            benchmark_task: benchmark task to add to the benchmark tasks queue.

        Returns:
            None
        """
        self._benchmark_tasks_queue.put(benchmark_task)

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
