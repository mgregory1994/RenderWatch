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


import subprocess
import os
import signal
import logging

from render_watch.app_formatting import format_converter
from render_watch.startup import GLib


class Encoder:
    @staticmethod
    def start_encode_process(active_row, ffmpeg_args, duration_in_seconds, encode_passes, folder_state=False):
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
                        Encoder.__pause_ffmpeg_task(encode_process, active_row)

                    process_stdout = encode_process.stdout.readline().strip().split('=')

                    if process_stdout == [''] and encode_process.poll() is not None:
                        break

                    last_line = process_stdout

                    try:
                        Encoder.__evaluate_encode_process(active_row,
                                                          process_stdout,
                                                          encode_pass,
                                                          encode_passes,
                                                          duration_in_seconds)
                    except:
                        continue

        Encoder.__check_encode_process_state(active_row, encode_process, last_line)
        Encoder.__set_encode_process_finished(active_row, folder_state)

    @staticmethod
    def __evaluate_encode_process(active_row, process_stdout, encode_pass, encode_passes, duration_in_seconds):
        bitrate = Encoder.__get_bitrate_as_float(process_stdout)
        file_size_in_kilobytes = Encoder.__get_file_size_in_kilobytes(process_stdout)
        current_time_in_seconds = Encoder.__get_current_time_in_seconds(process_stdout)
        speed_as_float = Encoder.__get_speed_as_float(process_stdout)

        if encode_pass == 0:
            progress = (current_time_in_seconds / duration_in_seconds) / encode_passes
        else:
            progress = .5 + ((current_time_in_seconds / duration_in_seconds) / encode_passes)

        if speed_as_float is not None:
            active_row.time = Encoder.__get_time_estimate(current_time_in_seconds,
                                                          duration_in_seconds,
                                                          speed_as_float,
                                                          encode_pass,
                                                          encode_passes)

        if file_size_in_kilobytes is not None:
            active_row.file_size = Encoder.__convert_kilobytes_to_bytes(file_size_in_kilobytes)

        active_row.bitrate = bitrate
        active_row.speed = speed_as_float
        active_row.progress = progress
        active_row.current_time = current_time_in_seconds

    @staticmethod
    def __check_encode_process_state(active_row, encode_process, last_line):
        process_return_code = encode_process.wait()

        if not active_row.stopped and process_return_code != 0:
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
    def __pause_ffmpeg_task(encode_process, active_row):
        os.kill(encode_process.pid, signal.SIGSTOP)
        active_row.task_threading_event.wait()
        os.kill(encode_process.pid, signal.SIGCONT)

    @staticmethod
    def __get_bitrate_as_float(process_stdout):
        try:
            bitrate_identifier = 'kbits/s'
            bitrate_index = None

            for index, stdout_chunk in enumerate(process_stdout):
                if bitrate_identifier in stdout_chunk:
                    bitrate_index = index

            if bitrate_index is not None:
                bitrate = process_stdout[bitrate_index].split(' ')

                while '' in bitrate:
                    bitrate.remove('')

                return float(bitrate[0].split('k')[0])
            else:
                return 0.0
        except:
            return 0.0

    @staticmethod
    def __get_speed_as_float(process_stdout):
        try:
            speed_identifier = 'x'
            speed_index = None

            for index, stdout_chunk in enumerate(process_stdout):
                if speed_identifier in stdout_chunk:
                    speed_index = index

            if speed_index is not None:
                speed = process_stdout[speed_index]

                return float(speed.split('x')[0])
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_file_size_in_kilobytes(process_stdout):
        try:
            file_size_identifier = 'kB'
            file_size_index = None

            for index, stdout_chunk in enumerate(process_stdout):
                if file_size_identifier in stdout_chunk:
                    file_size_index = index

            if file_size_index is not None:
                file_size_line = process_stdout[file_size_index].split(' ')
                file_size = file_size_line[-2].split('k')[0]

                return int(file_size)
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_current_time_in_seconds(process_stdout):
        try:
            current_time_identifier = 'bitrate'
            current_time_index = None

            for index, stdout_chunk in enumerate(process_stdout):
                if current_time_identifier in stdout_chunk:
                    current_time_index = index

            if current_time_index is not None:
                current_time = process_stdout[current_time_index].split(' ')

                return format_converter.get_seconds_from_timecode(current_time[0])
            else:
                return 0
        except:
            return 0

    @staticmethod
    def __get_time_estimate(current_time_in_seconds, duration_in_seconds, speed_as_float, encode_pass, encode_passes):
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
    def __convert_kilobytes_to_bytes(file_size_in_kilobytes):
        total_bytes = file_size_in_kilobytes * format_converter.KILOBYTE_IN_BYTES

        return total_bytes
