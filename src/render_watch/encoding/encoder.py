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


import subprocess
import os
import signal
import logging
import re

from render_watch.app_formatting import format_converter
from render_watch.startup import GLib


class Encoder:
    """Allows for running a process to encode a given task."""

    @staticmethod
    def start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, folder_state=False):
        """Run a process using ffmpeg arguments to encode a single task.

        Each processing task updates it's respective active_row on the encoding state.

        :param active_row:
            Gtk.ListboxRow from the active page.
        :param ffmpeg_args:
            ffmpeg settings arguments list.
        :param duration_in_seconds:
            Total duration of the task.
        :param encode_passes:
            Number of encode passes.
        :param folder_state:
            (Default False) Processes the task with a folder as it's ffmpeg input.
        """
        for encode_pass, args in enumerate(ffmpeg_args):
            with subprocess.Popen(args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as encode_process:
                while True:
                    if active_row.stopped and encode_process.poll() is None:
                        encode_process.terminate()
                        break
                    elif active_row.paused and encode_process.poll() is None:
                        Encoder._pause_ffmpeg_task(encode_process, active_row)

                    process_stdout = encode_process.stdout.readline().strip()
                    if process_stdout == '' and encode_process.poll() is not None:
                        break
                    last_line = process_stdout

                    try:
                        Encoder._evaluate_encode_process(active_row,
                                                         process_stdout,
                                                         encode_pass,
                                                         encode_passes,
                                                         duration_in_seconds)
                    except Exception as e:
                        print(e)
                        continue

        Encoder._check_encode_process_finished_state(active_row, encode_process, last_line)
        Encoder._set_encode_process_finished(active_row, folder_state)

    @staticmethod
    def _evaluate_encode_process(active_row, process_stdout, encode_pass, encode_passes, duration_in_seconds):
        # Uses the encoder's process' stdout to evaluate the encoder's state.
        bitrate = Encoder._get_bitrate_as_float(process_stdout)
        file_size_in_kilobytes = Encoder._get_file_size_in_kilobytes(process_stdout)
        current_time_in_seconds = Encoder._get_current_time_in_seconds(process_stdout)
        speed_as_float = Encoder._get_speed_as_float(process_stdout)
        if encode_pass == 0:
            progress = (current_time_in_seconds / duration_in_seconds) / encode_passes
        else:
            progress = .5 + ((current_time_in_seconds / duration_in_seconds) / encode_passes)

        if speed_as_float is not None:
            active_row.time = Encoder._get_time_estimate(
                current_time_in_seconds, duration_in_seconds,
                speed_as_float, encode_pass, encode_passes)
        if file_size_in_kilobytes is not None:
            active_row.file_size = Encoder._convert_kilobytes_to_bytes(file_size_in_kilobytes)
        active_row.bitrate = bitrate
        active_row.speed = speed_as_float
        active_row.progress = progress
        active_row.current_time = current_time_in_seconds

    @staticmethod
    def _check_encode_process_finished_state(active_row, encode_process, last_line):
        # Checks if the encode process finished successfully.
        process_return_code = encode_process.wait()
        if not active_row.stopped and process_return_code != 0:
            active_row.failed = True
            logging.error('--- ENCODE FAILED: '
                          + active_row.ffmpeg.input_file
                          + ' ---\n'
                          + last_line)
        elif active_row.stopped:
            logging.info('--- ENCODE STOPPED: ' + active_row.ffmpeg.input_file + ' ---')

    @staticmethod
    def _set_encode_process_finished(active_row, folder_state):
        # Sets the finished state for the task's active row.
        active_row.progress = 1.0
        if not folder_state:
            GLib.idle_add(active_row.set_finished_state)

    @staticmethod
    def _pause_ffmpeg_task(encode_process, active_row):
        # Pauses the encoder's process by using OS signals.
        os.kill(encode_process.pid, signal.SIGSTOP)
        active_row.task_threading_event.wait()
        os.kill(encode_process.pid, signal.SIGCONT)

    @staticmethod
    def _get_bitrate_as_float(process_stdout):
        try:
            bitrate = re.search('bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', process_stdout).group().split('=')[1]
            return float(bitrate)
        except:
            return 0.0

    @staticmethod
    def _get_speed_as_float(process_stdout):
        try:
            speed = re.search('speed=\d+\.\d+|speed=\s+\d+\.\d+', process_stdout).group().split('=')[1]
            return float(speed)
        except:
            return 0

    @staticmethod
    def _get_file_size_in_kilobytes(process_stdout):
        try:
            file_size = re.search('size=\d+|size=\s+\d+', process_stdout).group().split('=')[1]
            return int(file_size)
        except:
            return 0

    @staticmethod
    def _get_current_time_in_seconds(process_stdout):
        try:
            current_time = re.search('time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                    process_stdout).group().split('=')[1]
            return format_converter.get_seconds_from_timecode(current_time)
        except:
            return 0

    @staticmethod
    def _get_time_estimate(current_time_in_seconds, duration_in_seconds, speed_as_float, encode_pass, encode_passes):
        # Determines how much longer the encode process will take to complete.
        try:
            if encode_pass == 0:
                duration_in_seconds *= encode_passes

            if current_time_in_seconds >= duration_in_seconds:
                time_estimate = 0
            else:
                time_estimate = (duration_in_seconds - current_time_in_seconds) / speed_as_float
            return time_estimate
        except:
            return 0

    @staticmethod
    def _convert_kilobytes_to_bytes(file_size_in_kilobytes):
        return file_size_in_kilobytes * format_converter.KILOBYTE_IN_BYTES
