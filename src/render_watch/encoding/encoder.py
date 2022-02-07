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
    """
    Runs a process to encode tasks.
    """

    @staticmethod
    def start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, folder_state=False):
        """
        Runs a process using ffmpeg arguments to encode a single task.

        :param active_row: Gtk.ListboxRow from the active page.
        :param ffmpeg_args: ffmpeg settings arguments.
        :param duration_in_seconds: Task's input file duration.
        :param encode_passes: Number of encode passes.
        :param folder_state:(Default False) Processes the task as a folder for it's input.
        """
        for encode_pass, args in enumerate(ffmpeg_args):
            with subprocess.Popen(args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as encode_process:
                while True:
                    if active_row.stopped and encode_process.poll() is None:
                        os.kill(encode_process.pid, signal.SIGKILL)
                        break
                    elif active_row.paused and encode_process.poll() is None:
                        Encoder._pause_encode_process(encode_process, active_row)

                    process_stdout = encode_process.stdout.readline().strip()
                    if process_stdout == '' and encode_process.poll() is not None:
                        break
                    stdout_last_line = process_stdout

                    try:
                        Encoder._update_active_row_encode_status(active_row,
                                                                 process_stdout,
                                                                 encode_pass,
                                                                 encode_passes,
                                                                 duration_in_seconds)
                    except Exception as exception:
                        logging.exception(exception)
                        continue

        Encoder._update_active_row_finished_state(active_row, encode_process, stdout_last_line)
        Encoder._set_active_row_finished_state(active_row, folder_state)

    @staticmethod
    def _pause_encode_process(encode_process, active_row):
        os.kill(encode_process.pid, signal.SIGSTOP)
        active_row.task_threading_event.wait()
        os.kill(encode_process.pid, signal.SIGCONT)

    @staticmethod
    def _update_active_row_encode_status(active_row,
                                         process_stdout,
                                         current_encode_pass,
                                         encode_passes,
                                         duration_in_seconds):
        Encoder._update_bitrate_value(active_row, process_stdout)
        Encoder._update_file_size_value(active_row, process_stdout)

        speed_as_a_float = Encoder._update_encode_speed_value(active_row, process_stdout)
        current_time_in_seconds = Encoder._update_current_encode_time_position(active_row, process_stdout)

        Encoder._update_encode_progress(active_row,
                                        current_encode_pass,
                                        encode_passes,
                                        duration_in_seconds,
                                        current_time_in_seconds)
        Encoder._update_encode_time_left(active_row,
                                         speed_as_a_float,
                                         current_encode_pass,
                                         encode_passes,
                                         current_time_in_seconds,
                                         duration_in_seconds)

    @staticmethod
    def _update_bitrate_value(active_row, process_stdout):
        try:
            bitrate = re.search('bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', process_stdout).group().split('=')[1]
            active_row.bitrate = float(bitrate)
        except:
            pass

    @staticmethod
    def _update_file_size_value(active_row, process_stdout):
        try:
            file_size_in_kilobytes = re.search('size=\d+|size=\s+\d+', process_stdout).group().split('=')[1]
            file_size_in_bytes = format_converter.convert_kilobytes_to_bytes(int(file_size_in_kilobytes))
            active_row.file_size = file_size_in_bytes
        except:
            pass

    @staticmethod
    def _update_current_encode_time_position(active_row, process_stdout):
        try:
            current_time = re.search('time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                     process_stdout).group().split('=')[1]
            current_time_in_seconds = format_converter.get_seconds_from_timecode(current_time)
            active_row.current_time = current_time_in_seconds
        except:
            pass
        else:
            return current_time_in_seconds

    @staticmethod
    def _update_encode_speed_value(active_row, process_stdout):
        try:
            speed = re.search('speed=\d+\.\d+|speed=\s+\d+\.\d+', process_stdout).group().split('=')[1]
            active_row.speed = float(speed)
        except:
            pass
        else:
            return float(speed)

    @staticmethod
    def _update_encode_progress(active_row,
                                current_encode_pass,
                                encode_passes,
                                duration_in_seconds,
                                current_time_in_seconds):
        try:
            if current_encode_pass == 0:
                progress = (current_time_in_seconds / duration_in_seconds) / encode_passes
            else:
                progress = .5 + ((current_time_in_seconds / duration_in_seconds) / encode_passes)

            active_row.progress = progress
        except:
            pass

    @staticmethod
    def _update_encode_time_left(active_row,
                                 speed_as_a_float,
                                 current_encode_pass,
                                 encode_passes,
                                 current_time_in_seconds,
                                 duration_in_seconds):
        try:
            if speed_as_a_float > 0.0:
                if current_encode_pass == 0:
                    duration_in_seconds *= encode_passes

                if current_time_in_seconds >= duration_in_seconds:
                    time_left = 0
                else:
                    time_left = (duration_in_seconds - current_time_in_seconds) / speed_as_a_float

                active_row.time = time_left
        except:
            pass

    @staticmethod
    def _update_active_row_finished_state(active_row, encode_process, stdout_last_line):
        process_return_code = encode_process.wait()

        if active_row.stopped:
            logging.info('--- ENCODE STOPPED: ' + active_row.ffmpeg.input_file + ' ---')
        elif process_return_code:
            active_row.failed = True
            logging.error('--- ENCODE FAILED: '
                          + active_row.ffmpeg.input_file
                          + ' ---\n'
                          + stdout_last_line)

    @staticmethod
    def _set_active_row_finished_state(active_row, folder_state):
        active_row.progress = 1.0

        if not folder_state:
            GLib.idle_add(active_row.set_finished_state)
