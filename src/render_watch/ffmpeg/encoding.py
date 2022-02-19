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


import threading

from render_watch.ffmpeg import input, output


# FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-loglevel', 'quiet', '-stats', "-y"]
FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-stats', "-y"]
FFMPEG_INIT_AUTO_CROP_ARGS = ['ffmpeg', '-hide_banner', '-y']
FFMPEG_CONCATENATION_INIT_ARGS = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i']

VIDEO_COPY_ARGS = ('-c:v', 'copy')
AUDIO_COPY_ARGS = ('-c:a', 'copy')

AUDIO_NONE_ARG = '-an'
VIDEO_NONE_ARG = '-vn'

RAW_VIDEO_ARGS = ('-f', 'rawvideo')

VSYNC_ARGS = ('-vsync', '0')

NVDEC_ARGS = ('-hwaccel', 'nvdec')
NVDEC_OUT_FORMAT_ARGS = ('-hwaccel_output_format', 'cuda')


class Task:
    def __init__(self, input_file_path: str):
        self.input_file = input.InputFile(input_file_path)
        self.output_file = output.OutputFile(self.input_file, 'get_default_output_dir_from_preferences')
        self.temp_output_file = output.TempOutputFile(self.input_file, 'get_default_temp_dir_from_preferences')
        self.video_codec = None
        self.audio_codec = None
        self.filters = None
        self.subtitles = None
        self._bitrate = None
        self._file_size = None
        self._speed = None
        self._time_left = None
        self._bitrate_lock = threading.Lock()
        self._file_size_lock = threading.Lock()
        self._speed_lock = threading.Lock()
        self._time_left_lock = threading.Lock()
        self._task_thread_lock = threading.Lock()
        self._has_started = False
        self._is_paused = False
        self._is_stopped = False
        self._is_done = False
        self.has_failed = False
        self.duration = 0

    @property
    def bitrate(self) -> float:
        with self._bitrate_lock:
            return self._bitrate

    @bitrate.setter
    def bitrate(self, bitrate_value: float):
        with self._bitrate_lock:
            self._bitrate = bitrate_value

    @property
    def file_size(self) -> str:
        with self._file_size_lock:
            return self._file_size

    @file_size.setter
    def file_size(self, file_size_value: str):
        with self._file_size_lock:
            self._file_size = file_size_value

    @property
    def speed(self) -> float:
        with self._speed_lock:
            return self._speed

    @speed.setter
    def speed(self, speed_value: float):
        with self._speed_lock:
            self._speed = speed_value

    @property
    def time_left_in_seconds(self) -> int:
        with self._time_left_lock:
            return self._time_left

    @time_left_in_seconds.setter
    def time_left_in_seconds(self, encoder_time_left: int):
        with self._time_left_lock:
            self._time_left = encoder_time_left

    @property
    def has_started(self) -> bool:
        with self._task_thread_lock:
            return self._has_started

    @has_started.setter
    def has_started(self, has_encoder_started: bool):
        with self._task_thread_lock:
            self._has_started = has_encoder_started

    @property
    def is_paused(self) -> bool:
        with self._task_thread_lock:
            return self._is_paused

    @is_paused.setter
    def is_paused(self, is_encoder_paused: bool):
        with self._task_thread_lock:
            self._is_paused = is_encoder_paused

    @property
    def is_stopped(self) -> bool:
        with self._task_thread_lock:
            return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, is_encoder_stopped: bool):
        with self._task_thread_lock:
            self._is_stopped = is_encoder_stopped

    @property
    def is_done(self) -> bool:
        with self._task_thread_lock:
            return self._is_done

    @is_done.setter
    def is_done(self, is_encoder_done: bool):
        with self._task_thread_lock:
            self._is_done = is_encoder_done


class FFmpegArgs:

    @staticmethod
    def get_args(encoding_task: Task):
        pass