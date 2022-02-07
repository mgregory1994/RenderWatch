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


import os
import signal
import subprocess
import logging
import re

from render_watch.app_formatting import format_converter
from render_watch.helpers import ffmpeg_helper
from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.startup import GLib


SHORT_BENCHMARK_DURATION = 15
LONG_BENCHMARK_DURATION = 30


def start_benchmark(ffmpeg, settings_sidebar_handlers, application_preferences):
    """
    Runs a benchmark using ffmpeg settings.

    :param ffmpeg: ffmpeg settings.
    :param settings_sidebar_handlers: Settings sidebar handlers.
    :param application_preferences: Application preferences.
    """
    ffmpeg_copy = ffmpeg.get_copy()
    origin_duration = ffmpeg_copy.duration_origin
    start_time, duration = _get_benchmark_position_and_duration(settings_sidebar_handlers, origin_duration)
    _setup_benchmark_ffmpeg_settings(ffmpeg_copy, start_time, duration, application_preferences)

    _set_benchmark_widgets_start_state(settings_sidebar_handlers)
    _run_benchmark_process(ffmpeg_copy, settings_sidebar_handlers, duration, origin_duration)


def _get_benchmark_position_and_duration(settings_sidebar_handlers, origin_duration):
    if settings_sidebar_handlers.is_benchmark_short_radiobutton_active():
        return _get_short_position_and_duration(origin_duration)
    else:
        return _get_long_position_and_duration(origin_duration)


def _get_short_position_and_duration(origin_duration):
    if (origin_duration / 15) >= 2:
        return (origin_duration / 2), SHORT_BENCHMARK_DURATION
    elif (origin_duration / 15) >= 1:
        return 0, SHORT_BENCHMARK_DURATION
    else:
        return 0, origin_duration


def _get_long_position_and_duration(origin_duration):
    if (origin_duration / 30) >= 2:
        return (origin_duration / 2), LONG_BENCHMARK_DURATION
    elif (origin_duration / 30) >= 1:
        return 0, LONG_BENCHMARK_DURATION
    else:
        return 0, origin_duration


def _setup_benchmark_ffmpeg_settings(ffmpeg, start_time, duration, application_preferences):
    ffmpeg.trim_settings = _get_benchmark_trim_settings(start_time, duration)
    ffmpeg.filename = 'benchmark'
    ffmpeg.output_directory = application_preferences.temp_directory + '/'


def _get_benchmark_trim_settings(start_time, duration):
    trim_settings = TrimSettings()
    trim_settings.start_time = start_time
    trim_settings.trim_duration = duration
    return trim_settings


def _set_benchmark_widgets_start_state(settings_sidebar_handlers):
    GLib.idle_add(settings_sidebar_handlers.set_benchmark_start_state)


def _run_benchmark_process(ffmpeg, settings_sidebar_handlers, duration, origin_duration):
    ffmpeg_args = ffmpeg_helper.get_parsed_ffmpeg_args(ffmpeg)
    speed_value = 0
    file_size_value = None

    for encode_pass, args in enumerate(ffmpeg_args):
        with subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1) as benchmark_process:
            while True:
                with settings_sidebar_handlers.benchmark_thread_lock:
                    if settings_sidebar_handlers.is_benchmark_thread_stopping:
                        os.kill(benchmark_process.pid, signal.SIGKILL)
                        break

                stdout = benchmark_process.stdout.readline().strip()
                if not stdout:
                    break

                try:
                    bitrate_value = _get_bitrate(stdout)
                    file_size_value = _get_current_file_size(stdout)
                    speed_value = _get_speed(stdout)
                    current_time = _get_current_time(stdout)

                    if encode_pass == 0:
                        progress = (current_time / duration) / len(ffmpeg_args)
                    else:
                        progress = .5 + ((current_time / duration) / len(ffmpeg_args))

                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_progress_bar_fraction, progress)
                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_bitrate_label_text,
                                  str(bitrate_value) + 'kbits/s')
                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_speed_label_text, str(speed_value) + 'x')
                except:
                    continue

        benchmark_process.wait()

    try:
        if speed_value is not None:
            time_estimate = (origin_duration * len(ffmpeg_args)) / speed_value
            timecode = format_converter.get_timecode_from_seconds(time_estimate)
            GLib.idle_add(settings_sidebar_handlers.set_benchmark_process_time_label_text, timecode)
    except ZeroDivisionError:
        logging.error('--- BENCHMARK SPEED LABEL CAN\'T BE SET ---')

    if file_size_value is not None:
        total_file_size = _get_final_file_size(file_size_value, origin_duration, duration)
        GLib.idle_add(settings_sidebar_handlers.set_benchmark_file_size_label_text, total_file_size)

    process_return_code = benchmark_process.poll()

    GLib.idle_add(settings_sidebar_handlers.set_benchmark_done_state)

    if process_return_code != 0:
        with settings_sidebar_handlers.benchmark_thread_lock:
            if settings_sidebar_handlers.is_benchmark_thread_stopping:
                GLib.idle_add(settings_sidebar_handlers.set_benchmark_ready_state)
            else:
                logging.error('--- BENCHMARK PROCESS FAILED ---\n' + str(ffmpeg.get_args()))
    return process_return_code == 0


def _get_bitrate(stdout):
    bitrate = re.search('bitrate=\d+\.\d+|bitrate=\s+\d+\.\d+', stdout).group().split('=')[1]
    return float(bitrate)


def _get_current_file_size(stdout):
    file_size = re.search('size=\d+|size=\s+\d+', stdout).group().split('=')[1]
    return int(file_size)


def _get_speed(stdout):
    speed = re.search('speed=\d+\.\d+|speed=\s+\d+\.\d+', stdout).group().split('=')[1]
    return float(speed)


def _get_current_time(stdout):
    current_time = re.search('time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                             stdout).group().split('=')[1]
    return format_converter.get_seconds_from_timecode(current_time)


def _get_final_file_size(file_size_value, origin_duration, duration):
    ratio = origin_duration / duration
    total = file_size_value * ratio * format_converter.KILOBYTE_IN_BYTES
    return format_converter.get_file_size_from_bytes(total)
