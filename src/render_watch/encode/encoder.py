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
import re
import signal
import subprocess

from render_watch.ffmpeg import encoding
from render_watch.helpers import format_converter


def run_encode_subprocess(encoding_task: encoding.Task) -> int:
    """
    Runs ffmpeg via a subprocess using ffmpeg args from the given encoding task. Updates the
    encoding task's status while the process runs.

    Parameters:
        encoding_task: Encoding task to use for the ffmpeg subprocess.

    Returns:
        Process return code as an integer.
    """
    for encode_pass, ffmpeg_args in enumerate(encoding.FFmpegArgs.get_args(encoding_task)):
        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as ffmpeg_process:
            encoding_task.has_started = True

            while True:
                if encoding_task.is_stopped and ffmpeg_process.poll() is None:
                    os.kill(ffmpeg_process.pid, signal.SIGKILL)

                    break
                elif encoding_task.is_paused and ffmpeg_process.poll() is None:
                    _pause_ffmpeg_process(ffmpeg_process, encoding_task)

                stdout = ffmpeg_process.stdout.readline().strip()
                if stdout == '' and ffmpeg_process.poll() is not None:
                    break

                stdout_last_line = stdout

                _update_task_status(encoding_task, stdout, encode_pass)

    _log_ffmpeg_process_state(ffmpeg_process, encoding_task, stdout_last_line)

    encoding_task.progress = 1.0
    encoding_task.is_done = True

    return ffmpeg_process.wait()


def _pause_ffmpeg_process(ffmpeg_process: subprocess.Popen, encoding_task: encoding.Task):
    # Pauses the subprocess and waits until the encoding task signals the paused threading event to resume.
    os.kill(ffmpeg_process.pid, signal.SIGSTOP)
    encoding_task.paused_threading_event.wait()
    os.kill(ffmpeg_process.pid, signal.SIGCONT)


def _update_task_status(encoding_task: encoding.Task, stdout: str, encode_pass: int):
    # Updates the encoding task using the stdout of the ffmpeg subprocess.
    _update_task_bitrate_status(encoding_task, stdout)
    _update_task_file_size_status(encoding_task, stdout)
    _update_task_speed_status(encoding_task, stdout)
    _update_task_current_position_status(encoding_task, stdout)
    _update_task_progress_status(encoding_task, encode_pass)
    _update_task_time_left_status(encoding_task, encode_pass)


def _update_task_bitrate_status(encoding_task: encoding.Task, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's bitrate status.
    try:
        bitrate = re.search(r'bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', stdout).group().split('=')[1]
        encoding_task.bitrate = float(bitrate)
    except (AttributeError, TypeError):
        pass


def _update_task_file_size_status(encoding_task: encoding.Task, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's file size status.
    try:
        file_size_in_kilobytes = re.search(r'size=\d+|size=\s+\d+', stdout).group().split('=')[1]
        file_size_in_bytes = format_converter.get_bytes_from_kilobytes(int(file_size_in_kilobytes))
        encoding_task.file_size = file_size_in_bytes
    except (AttributeError, TypeError):
        pass


def _update_task_speed_status(encoding_task: encoding.Task, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's speed status.
    try:
        speed = re.search(r'speed=\d+\.\d+|speed=\s+\d+\.\d+', stdout).group().split('=')[1]
        encoding_task.speed = float(speed)
    except (AttributeError, TypeError):
        pass


def _update_task_current_position_status(encoding_task: encoding.Task, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's current position status.
    try:
        current_position_timecode = re.search(r'time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                              stdout).group().split('=')[1]
        current_position_in_seconds = format_converter.get_seconds_from_timecode(current_position_timecode)
        encoding_task.current_position = current_position_in_seconds
    except (AttributeError, TypeError):
        pass


def _update_task_progress_status(encoding_task: encoding.Task, encode_pass: int):
    # Updates the encoding task's progress status.
    try:
        if encoding_task.is_video_2_pass():
            encode_passes = 2
        else:
            encode_passes = 1

        if encode_pass == 0:
            progress = (encoding_task.current_position / encoding_task.input_file.duration) / encode_passes
        else:
            progress = 0.5 + ((encoding_task.current_position / encoding_task.input_file.duration) / encode_passes)

        encoding_task.progress = round(progress, 4)
    except (AttributeError, TypeError, ZeroDivisionError):
        pass


def _update_task_time_left_status(encoding_task: encoding.Task, encode_pass: int):
    # Updates the encoding task's time left status.
    try:
        if not encoding_task.speed > 0.0:
            return

        if encoding_task.is_video_2_pass() and encode_pass == 0:
            duration_in_seconds = encoding_task.input_file.duration * 2
        else:
            duration_in_seconds = encoding_task.input_file.duration

        if encoding_task.current_position >= duration_in_seconds:
            time_left = 0
        else:
            time_left = (duration_in_seconds - encoding_task.current_position) / encoding_task.speed

        encoding_task.time_left_in_seconds = round(time_left)
    except (AttributeError, TypeError, ZeroDivisionError):
        pass


def _log_ffmpeg_process_state(ffmpeg_process: subprocess.Popen, encoding_task: encoding.Task, stdout_last_line: str):
    # Logs the status of the ffmpeg subprocess if it was stopped or has failed.
    if encoding_task.is_stopped:
        logging.info(''.join(['--- ENCODE PROCESS STOPPED: ', encoding_task.output_file.file_path, ' ---']))
    elif ffmpeg_process.wait():
        encoding_task.has_failed = True
        logging.error(''.join(['--- ENCODE PROCESS FAILED: ',
                               encoding_task.output_file.file_path,
                               ' ---\n',
                               stdout_last_line]))
