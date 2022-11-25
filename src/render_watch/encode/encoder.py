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


import os
import re
import signal
import subprocess

from render_watch.ffmpeg import task, video_codec
from render_watch.helpers import ffmpeg_helper, format_converter
from render_watch import logger


def run_encode_subprocess(encode_task: task.Encode) -> int:
    """
    Runs ffmpeg via a subprocess using ffmpeg args from the given encoding task. Updates the
    encoding task's status while the process runs.

    Parameters:
        encode_task: Encoding task to use for the ffmpeg subprocess.

    Returns:
        Process return code as an integer.
    """
    for encode_pass, ffmpeg_args in enumerate(ffmpeg_helper.Args.get_args(encode_task)):
        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as ffmpeg_process:
            while True:
                if encode_task.is_stopped and ffmpeg_process.poll() is None:
                    os.kill(ffmpeg_process.pid, signal.SIGKILL)

                    break
                elif encode_task.is_paused and ffmpeg_process.poll() is None:
                    _pause_ffmpeg_process(encode_task, ffmpeg_process)

                stdout = ffmpeg_process.stdout.readline().strip()
                if stdout == '' and ffmpeg_process.poll() is not None:
                    break

                stdout_last_line = stdout

                _update_task_status(encode_task, stdout, encode_pass)

    _log_ffmpeg_process_state(encode_task, ffmpeg_process, stdout_last_line)

    encode_task.progress = 1.0

    return ffmpeg_process.wait()


def _pause_ffmpeg_process(encode_task: task.Encode, ffmpeg_process: subprocess.Popen):
    # Pauses the subprocess and waits until the encoding task signals the paused threading event to resume.
    os.kill(ffmpeg_process.pid, signal.SIGSTOP)
    encode_task.paused_threading_event.wait()
    os.kill(ffmpeg_process.pid, signal.SIGCONT)


def _update_task_status(encode_task: task.Encode, stdout: str, encode_pass: int):
    # Updates the encoding task using the stdout of the ffmpeg subprocess.
    _update_task_bitrate_status(encode_task, stdout)
    _update_task_file_size_status(encode_task, stdout)
    _update_task_speed_status(encode_task, stdout)
    _update_task_current_position_status(encode_task, stdout)
    _update_task_progress_status(encode_task, encode_pass)
    _update_task_time_left_status(encode_task, encode_pass)


def _update_task_bitrate_status(encode_task: task.Encode, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's bitrate status.
    try:
        bitrate = re.search(r'bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', stdout).group().split('=')[1]
        encode_task.bitrate = float(bitrate)
    except (AttributeError, TypeError):
        pass


def _update_task_file_size_status(encode_task: task.Encode, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's file size status.
    try:
        file_size_in_kilobytes = re.search(r'size=\d+|size=\s+\d+', stdout).group().split('=')[1]
        file_size_in_bytes = format_converter.get_bytes_from_kilobytes(int(file_size_in_kilobytes))
        encode_task.file_size = file_size_in_bytes
    except (AttributeError, TypeError):
        pass


def _update_task_speed_status(encode_task: task.Encode, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's speed status.
    try:
        speed = re.search(r'speed=\d+\.\d+|speed=\s+\d+\.\d+', stdout).group().split('=')[1]
        encode_task.speed = float(speed)
    except (AttributeError, TypeError):
        pass


def _update_task_current_position_status(encode_task: task.Encode, stdout: str):
    # Uses the ffmpeg subprocess' stdout to update the encoding task's current position status.
    try:
        current_position_timecode = re.search(r'time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                              stdout).group().split('=')[1]
        current_position_in_seconds = format_converter.get_seconds_from_timecode(current_position_timecode)
        encode_task.current_position = current_position_in_seconds
    except (AttributeError, TypeError):
        pass


def _update_task_progress_status(encode_task: task.Encode, encode_pass: int):
    # Updates the encoding task's progress status.
    try:
        if video_codec.is_codec_2_pass(encode_task.get_video_codec()):
            encode_passes = 2
        else:
            encode_passes = 1

        if encode_pass == 0:
            progress = (encode_task.current_time_position / encode_task.input_file.duration) / encode_passes
        else:
            progress = 0.5 + ((encode_task.current_time_position / encode_task.input_file.duration) / encode_passes)

        encode_task.progress = round(progress, 4)
    except (AttributeError, TypeError, ZeroDivisionError):
        pass


def _update_task_time_left_status(encode_task: task.Encode, encode_pass: int):
    # Updates the encoding task's time left status.
    try:
        if not encode_task.speed > 0.0:
            return

        if video_codec.is_codec_2_pass(encode_task.get_video_codec()) and encode_pass == 0:
            duration_in_seconds = encode_task.input_file.duration * 2
        else:
            duration_in_seconds = encode_task.input_file.duration

        if encode_task.current_time_position >= duration_in_seconds:
            time_left = 0
        else:
            time_left = (duration_in_seconds - encode_task.current_time_position) / encode_task.speed

        encode_task.time_left_in_seconds = round(time_left)
    except (AttributeError, TypeError, ZeroDivisionError):
        pass


def _log_ffmpeg_process_state(encode_task: task.Encode, ffmpeg_process: subprocess.Popen, stdout_last_line: str):
    # Logs the status of the ffmpeg subprocess if it was stopped or has failed.
    if encode_task.is_stopped:
        logger.log_encode_process_stopped(encode_task.output_file.file_path)
    elif ffmpeg_process.wait():
        logger.log_encode_process_failed(encode_task.output_file.file_path, stdout_last_line)
