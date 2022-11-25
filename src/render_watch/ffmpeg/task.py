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


from __future__ import annotations


import copy
import threading


from render_watch.ffmpeg import media_file, stream, video_codec, audio_codec, filter
from render_watch.helpers import directory_helper
from render_watch import app_preferences


class GeneralSettings:
    """Class that configures all general settings available for Render Watch."""

    FRAME_RATE = ('23.98', '24', '25', '29.97', '30', '50', '59.94', '60')
    FRAME_RATE_LENGTH = len(FRAME_RATE)

    def __init__(self):
        """Initializes the GeneralSettings class with all necessary variables the general options."""
        self.ffmpeg_args = {}

    @property
    def frame_rate(self) -> int | None:
        """
        Returns the frame rate option's index.

        Returns:
            Frame rate option as an index using the FRAME_RATE variable.
        """
        if '-r' in self.ffmpeg_args:
            frame_rate_arg = self.ffmpeg_args['-r']

            return GeneralSettings.FRAME_RATE.index(frame_rate_arg)
        return None

    @frame_rate.setter
    def frame_rate(self, frame_rate_index: int | None):
        """
        Sets the frame rate option.

        Parameters:
            frame_rate_index: Index from the FRAME_RATE variable.

        Returns:
            None
        """
        if frame_rate_index is not None and 0 <= frame_rate_index < GeneralSettings.FRAME_RATE_LENGTH:
            self.ffmpeg_args['-r'] = GeneralSettings.FRAME_RATE[frame_rate_index]
        else:
            self.ffmpeg_args.pop('-r', 0)

    @property
    def fast_start(self) -> bool:
        """
        Returns what the fast start option is set to.

        Returns:
            Fast start option as a boolean.
        """
        if '-movflags' in self.ffmpeg_args:
            return self.ffmpeg_args['-movflags'] == 'faststart'
        return False

    @fast_start.setter
    def fast_start(self, is_fast_start_enabled: bool):
        """
        Sets the fast start option.

        Parameters:
            is_fast_start_enabled: Boolean value to set the fast start option to.

        Returns:
            None
        """
        if is_fast_start_enabled:
            self.ffmpeg_args['-movflags'] = 'faststart'
        else:
            self.ffmpeg_args.pop('-movflags', 0)


class TrimSettings:
    """Class that configures all trim settings available for Render Watch."""

    MIN_TRIM_DURATION_IN_SECONDS = 0.5

    def __init__(self):
        """Initializes the TrimSettings class with all necessary variables for the trim options."""
        self.ffmpeg_args = {}

    @property
    def start_time(self) -> float | None:
        """
        Returns the trim start time.

        Returns:
            Trim start time as a float in seconds.
        """
        if '-ss' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-ss'])
        return None

    @start_time.setter
    def start_time(self, start_time_in_seconds: float | None):
        """
        Sets the trim start time.

        Parameters:
            start_time_in_seconds: Trim segment start time in seconds.

        Returns:
            None
        """
        if start_time_in_seconds:
            self.ffmpeg_args['-ss'] = str(round(start_time_in_seconds, 1))
        else:
            self.ffmpeg_args.pop('-ss', 0)

    @property
    def trim_duration(self) -> float | None:
        """
        Returns the trim duration.

        Returns:
            Trim duration as a float in seconds.
        """
        if '-to' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-to'])
        return None

    @trim_duration.setter
    def trim_duration(self, trim_duration_in_seconds: float | None):
        """
        Sets the trim duration.

        Parameters:
            trim_duration_in_seconds: Duration of the trim segment in seconds.

        Returns:
            None
        """
        if trim_duration_in_seconds is None:
            self.ffmpeg_args.pop('-to', 0)
        else:
            self.ffmpeg_args['-to'] = str(round(trim_duration_in_seconds, 1))


class Encode:
    VIDEO_STREAM_INDEX = 0
    VIDEO_CODEC_INDEX = 1

    def __init__(self, input_file: media_file.InputFile, app_settings: app_preferences.Settings):
        self._input_file = input_file
        self.app_settings = app_settings
        self._output_file = media_file.OutputFile(self._input_file, app_settings)
        self._temp_file = media_file.TempFile(self._input_file, app_settings.temp_directory)
        self._general_settings = GeneralSettings()
        self._trim_settings = None
        self._filters = filter.Filters(self._input_file)
        self._video_stream = [None, None]
        self._audio_streams = {}
        self._task_preview_file = None
        self._is_using_temp_file = False
        self._is_no_video = False
        self._is_no_audio = False
        self._has_started = False
        self._is_paused = False
        self._is_idle = False
        self._is_stopped = False
        self._is_done = False
        self._has_failed = False
        self.paused_threading_event = threading.Event()
        self._task_lock = threading.Lock()
        self._bitrate = None
        self._file_size = None
        self._speed = None
        self._time_left = None
        self._current_time_position = None
        self._progress = None
        self._task_duration = 0
        self._bitrate_lock = threading.Lock()
        self._file_size_lock = threading.Lock()
        self._speed_lock = threading.Lock()
        self._time_left_lock = threading.Lock()
        self._current_position_lock = threading.Lock()
        self._progress_lock = threading.Lock()

        self._setup_initial_streams()

    def _setup_initial_streams(self):
        self.set_video_stream(self.input_file.get_initial_video_stream())
        self.set_video_codec(video_codec.X264())

        initial_audio_stream = self.input_file.get_initial_audio_stream()

        if initial_audio_stream:
            self.add_audio_stream(initial_audio_stream)

            initial_audio_stream_codec = audio_codec.Aac(self.get_audio_stream_index(initial_audio_stream))
            self.set_audio_stream_codec(initial_audio_stream, initial_audio_stream_codec)

    @property
    def input_file(self) -> media_file.InputFile:
        with self._task_lock:
            return self._input_file

    @property
    def output_file(self) -> media_file.OutputFile:
        with self._task_lock:
            return self._output_file

    @output_file.setter
    def output_file(self, new_output_file: media_file.OutputFile):
        with self._task_lock:
            self._output_file = new_output_file

    @property
    def temp_file(self) -> media_file.TempFile:
        with self._task_lock:
            return self._temp_file

    @temp_file.setter
    def temp_file(self, new_temp_file: media_file.TempFile):
        with self._task_lock:
            self._temp_file = new_temp_file

    @property
    def general_settings(self) -> GeneralSettings:
        with self._task_lock:
            return self._general_settings

    @general_settings.setter
    def general_settings(self, new_general_settings: GeneralSettings):
        with self._task_lock:
            self._general_settings = new_general_settings

    @property
    def trim_settings(self) -> TrimSettings:
        with self._task_lock:
            return self._trim_settings

    @trim_settings.setter
    def trim_settings(self, new_trim_settings: TrimSettings):
        with self._task_lock:
            self._trim_settings = new_trim_settings

    @property
    def filters(self) -> filter.Filters:
        with self._task_lock:
            return self._filters

    @property
    def video_stream(self) -> list:
        with self._task_lock:
            return self._video_stream

    @property
    def audio_streams(self) -> dict:
        with self._task_lock:
            return self._audio_streams

    @audio_streams.setter
    def audio_streams(self, new_audio_streams: dict):
        with self._task_lock:
            self._audio_streams = new_audio_streams

    @property
    def task_preview_file(self) -> str:
        with self._task_lock:
            return self._task_preview_file

    @task_preview_file.setter
    def task_preview_file(self, new_preview_file: str):
        with self._task_lock:
            self._task_preview_file = new_preview_file

    @property
    def is_using_temp_file(self) -> bool:
        with self._task_lock:
            return self._is_using_temp_file

    @is_using_temp_file.setter
    def is_using_temp_file(self, is_enabled: bool):
        with self._task_lock:
            self._is_using_temp_file = is_enabled

    @property
    def is_no_video(self) -> bool:
        with self._task_lock:
            return self._is_no_video

    @is_no_video.setter
    def is_no_video(self, is_enabled: bool):
        with self._task_lock:
            self._is_no_video = is_enabled

    @property
    def is_no_audio(self) -> bool:
        with self._task_lock:
            return self._is_no_audio

    @is_no_audio.setter
    def is_no_audio(self, is_enabled: bool):
        with self._task_lock:
            self._is_no_audio = is_enabled

    @property
    def has_started(self) -> bool:
        with self._task_lock:
            return self._has_started

    @has_started.setter
    def has_started(self, is_enabled: bool):
        with self._task_lock:
            self._has_started = is_enabled

    @property
    def is_paused(self) -> bool:
        with self._task_lock:
            return self._is_paused

    @is_paused.setter
    def is_paused(self, is_enabled: bool):
        with self._task_lock:
            self._is_paused = is_enabled

    @property
    def is_idle(self) -> bool:
        with self._task_lock:
            return self._is_idle

    @is_idle.setter
    def is_idle(self, is_enabled: bool):
        with self._task_lock:
            self._is_idle = is_enabled

    @property
    def is_stopped(self) -> bool:
        with self._task_lock:
            return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, is_enabled: bool):
        with self._task_lock:
            self._is_stopped = is_enabled

    @property
    def is_done(self) -> bool:
        with self._task_lock:
            return self._is_done

    @is_done.setter
    def is_done(self, is_enabled: bool):
        with self._task_lock:
            self._is_done = is_enabled

    @property
    def has_failed(self) -> bool:
        with self._task_lock:
            return self._has_failed

    @has_failed.setter
    def has_failed(self, is_enabled: bool):
        with self._task_lock:
            self._has_failed = is_enabled

    @property
    def bitrate(self) -> float:
        with self._bitrate_lock:
            return self._bitrate

    @bitrate.setter
    def bitrate(self, new_bitrate: float):
        with self._bitrate_lock:
            self._bitrate = new_bitrate

    @property
    def file_size(self) -> int:
        with self._file_size_lock:
            return self._file_size

    @file_size.setter
    def file_size(self, new_file_size: int):
        with self._file_size_lock:
            self._file_size = new_file_size

    @property
    def speed(self) -> float:
        with self._speed_lock:
            return self._speed

    @speed.setter
    def speed(self, new_speed: float):
        with self._speed_lock:
            self._speed = new_speed

    @property
    def time_left(self) -> int:
        with self._time_left_lock:
            return self._time_left

    @time_left.setter
    def time_left(self, new_time_left: int):
        with self._time_left_lock:
            self._time_left = new_time_left

    @property
    def current_time_position(self) -> int:
        with self._current_position_lock:
            return self._current_time_position

    @current_time_position.setter
    def current_time_position(self, new_time_position: int):
        with self._current_position_lock:
            self._current_time_position = new_time_position

    @property
    def progress(self) -> float:
        with self._progress_lock:
            return self._progress

    @progress.setter
    def progress(self, new_progress: float):
        with self._progress_lock:
            self._progress = new_progress

    @property
    def task_duration(self) -> int:
        with self._task_lock:
            return self._task_duration

    def increment_task_duration(self):
        with self._task_lock:
            self._task_duration += 1

    def set_video_stream(self, new_video_stream: video_stream):
        self.video_stream[self.VIDEO_STREAM_INDEX] = new_video_stream

    def set_video_codec(self, new_video_codec):
        self.video_stream[self.VIDEO_CODEC_INDEX] = new_video_codec

    def get_video_stream(self) -> stream.VideoStream:
        return self.video_stream[self.VIDEO_STREAM_INDEX]

    def get_video_codec(self):
        return self.video_stream[self.VIDEO_CODEC_INDEX]

    def add_audio_stream(self, audio_stream: stream.AudioStream):
        """
        Adds the audio stream to the task's dictionary of audio streams and sets its codec to None.

        Parameters:
            audio_stream: Audio stream to add.

        Returns:
            None
        """
        self.audio_streams[audio_stream] = None

    def remove_audio_stream(self, audio_stream: stream.AudioStream):
        """
        Removes the given audio stream from the task's dictionary of audio streams.

        Parameters:
            audio_stream: Audio stream to remove.

        Returns:
            None
        """
        self.audio_streams.pop(audio_stream, 0)

    def set_audio_stream_codec(self, audio_stream: stream.AudioStream, audio_stream_codec):
        """
        Sets the given audio codec for the given audio stream. If the audio stream has been added to the task's
        dictionary of audio streams, then the given audio codec is set as its codec.

        Parameters:
            audio_stream: Audio stream that will have its audio codec changed.
            audio_stream_codec: Audio codec to use for the given audio stream.

        Returns:
            None
        """
        if audio_stream in self.audio_streams:
            self.audio_streams[audio_stream] = audio_stream_codec

    def get_audio_stream_codec(self, audio_stream: stream.AudioStream):
        """
        Returns the audio codec that's set for the given audio stream. Returns None if the given audio stream is not
        present in the task's dictionary of audio streams.

        Parameters:
            audio_stream: Audio stream to get the audio codec from.

        Returns:
            Audio codec for the given audio stream.
        """
        if audio_stream in self.audio_streams:
            return self.audio_streams[audio_stream]
        return None

    def get_audio_stream_index(self, audio_stream: stream.AudioStream) -> int | None:
        """
        Returns the index of what position the given audio stream is in the task's audio streams dictionary.

        Returns:
            Index that represents the given audio stream's position in the task's audio streams dictionary.
        """
        if audio_stream in self.audio_streams:
            audio_streams_list = list(self.audio_streams)

            return audio_streams_list.index(audio_stream)
        return None
    
    def get_copy(self) -> Encode:
        encode_task_copy = Encode(self.input_file, self.app_settings)
        encode_task_copy.output_file = copy.deepcopy(self.output_file)
        encode_task_copy.temp_file = copy.deepcopy(self.temp_file)
        encode_task_copy.general_settings = copy.deepcopy(self.general_settings)
        encode_task_copy.trim_settings = copy.deepcopy(self.trim_settings)
        encode_task_copy.filters.crop = copy.deepcopy(self.filters.crop)
        encode_task_copy.filters.scale = copy.deepcopy(self.filters.scale)
        encode_task_copy.filters.subtitles = copy.deepcopy(self.filters.subtitles)
        encode_task_copy.filters.deinterlace = copy.deepcopy(self.filters.deinterlace)
        encode_task_copy.set_video_stream(self.get_video_stream())
        encode_task_copy.set_video_codec(self.get_video_codec())
        encode_task_copy.audio_streams = copy.deepcopy(self.audio_streams)
        encode_task_copy.task_preview_file = self.task_preview_file
        encode_task_copy.is_using_temp_file = self.is_using_temp_file
        encode_task_copy.is_no_video = self.is_no_video
        encode_task_copy.is_no_audio = self.is_no_audio
        encode_task_copy.has_started = self.has_started
        encode_task_copy.is_paused = self.is_paused
        encode_task_copy.is_idle = self.is_idle
        encode_task_copy.is_stopped = self.is_stopped
        encode_task_copy.is_done = self.is_done
        encode_task_copy.has_failed = self.has_failed
        encode_task_copy.bitrate = self.bitrate
        encode_task_copy.file_size = self.file_size
        encode_task_copy.speed = self.speed
        encode_task_copy.time_left = self.time_left
        encode_task_copy.current_time_position = self.current_time_position
        encode_task_copy.progress = self.progress

        return encode_task_copy


class Folder(Encode):
    def __init__(self, input_file: media_file.InputFile, app_settings: app_preferences.Settings):
        super().__init__(input_file, app_settings)

        self._is_recursive = False
        self._files_in_folder = []
        self._next_encode_task = None
        self._task_thread_lock = threading.Lock()

    @property
    def is_stopped(self) -> bool:
        return super().is_stopped

    @is_stopped.setter
    def is_stopped(self, is_enabled: bool):
        super().is_stopped = is_enabled

        if self.next_encode_task:
            self.next_encode_task.is_stopped = is_enabled

    @property
    def is_recursive(self) -> bool:
        with self._task_thread_lock:
            return self._is_recursive

    @is_recursive.setter
    def is_recursive(self, is_recursively_searching: bool):
        with self._task_thread_lock:
            self._is_recursive = is_recursively_searching

    @property
    def files_in_folder(self) -> list[str]:
        while self._task_thread_lock:
            return self._files_in_folder

    @property
    def next_encode_task(self) -> Encode | None:
        with self._task_thread_lock:
            return self._next_encode_task

    @next_encode_task.setter
    def next_encode_task(self, new_encode_task: Encode):
        with self._task_thread_lock:
            self._next_encode_task = new_encode_task

    def populate_files_in_folder(self):
        for file_path in directory_helper.get_files_in_directory(self.input_file.dir, self.is_recursive):
            self.files_in_folder.append(file_path)

        self.process_next_encode_task()

    def process_next_encode_task(self):
        for file_path in self.files_in_folder:
            child_encode_task = copy.deepcopy(super())
            child_encode_task._input_file = media_file.InputFile(file_path)
            child_encode_task._output_file = media_file.OutputFile(child_encode_task.input_file, self.app_settings)
            child_encode_task.output_file.name = directory_helper.get_unique_file_name(
                child_encode_task.output_file.file_path,
                child_encode_task.output_file.name
            )
            child_encode_task.filters.crop = filter.Crop(child_encode_task, self.app_settings)

            if child_encode_task.input_file.is_valid():
                self.next_encode_task = child_encode_task

                yield
            else:
                continue

        self._files_in_folder.clear()
        self.next_encode_task = None


class WatchFolder(Encode):
    def __init__(self, input_file: media_file.InputFile, app_settings: app_preferences.Settings):
        super().__init__(input_file, app_settings)

        self._next_encode_task = None
        self._task_thread_lock = threading.Lock()

    @property
    def is_stopped(self) -> bool:
        return super().is_stopped

    @is_stopped.setter
    def is_stopped(self, is_enabled: bool):
        super().is_stopped = is_enabled

        if self.next_encode_task:
            self.next_encode_task.is_stopped = is_enabled

    @property
    def next_encode_task(self) -> Encode:
        with self._task_thread_lock:
            return self._next_encode_task

    @next_encode_task.setter
    def next_encode_task(self, new_encode_task: Encode):
        with self._task_thread_lock:
            self._next_encode_task = new_encode_task

    def process_next_encode_task(self, new_input_file_path: str):
        child_encode_task = copy.deepcopy(super())
        child_encode_task._input_file = media_file.InputFile(new_input_file_path)
        child_encode_task._output_file = media_file.OutputFile(child_encode_task.input_file, self.app_settings)
        child_encode_task.output_file.name = directory_helper.get_unique_file_name(
            child_encode_task.output_file.file_path,
            child_encode_task.output_file.name
        )
        child_encode_task.filters.crop = filter.Crop(child_encode_task, self.app_settings)

        if child_encode_task.input_file.is_valid():
            self.next_encode_task = child_encode_task
        else:
            self.next_encode_task = None


class VideoChunk:
    def __init__(self, encode_task: Encode, total_number_of_chunks: int, chunk_index: int):
        self._encode_task = copy.deepcopy(encode_task)
        self._parent_encode_task = encode_task
        self._total_number_of_chunks = total_number_of_chunks
        self._chunk_index = chunk_index
        self._task_lock = threading.Lock()

        self._setup_video_chunk_settings()

    def _setup_video_chunk_settings(self):
        self.encode_task.is_no_audio = True
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, str(self.chunk_index)])

        self._setup_2_pass_settings()
        self._setup_trim_settings()
        self._setup_extension()

    def _setup_2_pass_settings(self):
        if video_codec.is_codec_2_pass(self.encode_task.get_video_codec()):
            self.encode_task.get_video_codec().stats = ''.join([self.encode_task.temp_file.dir,
                                                                '/',
                                                                self.encode_task.temp_file.name,
                                                                '.log'])

    def _setup_trim_settings(self):
        trim_settings = TrimSettings()

        if self.encode_task.trim_settings:
            trim_duration = self.encode_task.trim_settings.trim_duration
            trim_start_time = self.encode_task.trim_settings.start_time
            chunk_duration = (trim_duration / self.total_number_of_chunks)
            chunk_start_time = trim_start_time + (chunk_duration * (self.chunk_index - 1))

            if self.chunk_index == 1:
                trim_settings.start_time = trim_start_time
                trim_settings.trim_duration = chunk_duration
            elif self.chunk_index == self.total_number_of_chunks:
                chunk_duration_offset = (trim_duration + trim_start_time) - chunk_start_time
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration_offset
            else:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration
        else:
            input_duration = self.encode_task.input_file.duration
            chunk_duration = (input_duration / self.total_number_of_chunks)
            chunk_start_time = chunk_duration * (self.chunk_index - 1)

            if self.chunk_index == 1:
                trim_settings.start_time = 0
                trim_settings.trim_duration = chunk_duration
            elif self.chunk_index == self.total_number_of_chunks:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = input_duration - chunk_start_time
            else:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration

        return trim_settings

    def _setup_extension(self):
        if video_codec.is_codec_vp9(self.encode_task.get_video_codec()):
            self.encode_task.temp_file.extension = '.webm'
        else:
            self.encode_task.temp_file.extension = '.mp4'

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def total_number_of_chunks(self) -> int:
        return self._total_number_of_chunks

    @property
    def chunk_index(self) -> int:
        return self._chunk_index


class AudioChunk:
    def __init__(self, encode_task: Encode):
        self._encode_task = copy.deepcopy(encode_task)
        self._parent_encode_task = encode_task

        self._setup_audio_chunk_settings()

    def _setup_audio_chunk_settings(self):
        self.encode_task.is_no_video = True
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, 'audio'])
        self.encode_task.temp_file.extension = '.mkv'

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task


class TrimPreview:
    def __init__(self, encode_task: Encode, time_position=None):
        self._encode_task = encode_task.get_copy()
        self._parent_encode_task = encode_task
        self.preview_threading_event = threading.Event()
        self._preview_file_path = None
        self._preview_thread_lock = threading.Lock()

        if time_position:
            self._time_position = time_position
        else:
            self._time_position = 0

        self._setup_trim_preview_settings()

    def _setup_trim_preview_settings(self):
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, 'trim_preview'])
        self.encode_task.temp_file.extension = '.png'
        self.encode_task.is_using_temp_file = True

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def time_position(self) -> int:
        return self._time_position

    @property
    def preview_file_path(self) -> str:
        with self._preview_thread_lock:
            return self._preview_file_path

    @preview_file_path.setter
    def preview_file_path(self, new_file_path: str):
        with self._preview_thread_lock:
            self._preview_file_path = new_file_path

    def update_encode_task(self):
        self._encode_task = self._parent_encode_task.get_copy()
        self._setup_trim_preview_settings()

    def apply_trim_preview_file_path(self):
        self.preview_file_path = self.encode_task.temp_file.file_path


class CropPreview:
    def __init__(self, encode_task: Encode, time_position=None):
        self._encode_task = encode_task.get_copy()
        self._parent_encode_task = encode_task
        self.preview_threading_event = threading.Event()
        self._preview_file_path = None
        self._preview_thread_lock = threading.Lock()

        if time_position:
            self._time_position = time_position
        else:
            self._time_position = round(self.encode_task.input_file.duration / 2, 2)

        self._setup_crop_preview_settings()

    def _setup_crop_preview_settings(self):
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, 'crop_preview'])
        self.encode_task.temp_file.extension = '.png'
        self.encode_task.is_using_temp_file = True

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def time_position(self) -> int:
        return self._time_position

    @property
    def preview_file_path(self) -> str:
        with self._preview_thread_lock:
            return self._preview_file_path

    @preview_file_path.setter
    def preview_file_path(self, new_file_path: str):
        with self._preview_thread_lock:
            self._preview_file_path = new_file_path

    def update_encode_task(self):
        self._encode_task = self._parent_encode_task.get_copy()
        self._setup_crop_preview_settings()

    def apply_trim_preview_file_path(self):
        self.preview_file_path = self.encode_task.temp_file.file_path
        self.parent_encode_task.task_preview_file = self.encode_task.temp_file.file_path


class SettingsPreview:

    ENCODE_DURATION = 1

    def __init__(self, encode_task: Encode, time_position=None):
        self._encode_task = encode_task.get_copy()
        self._parent_encode_task = encode_task
        self.preview_threading_event = threading.Event()
        self._preview_file_path = None
        self._preview_thread_lock = threading.Lock()

        self._setup_time_position(time_position)
        self._setup_settings_preview_settings()

    def _setup_time_position(self, time_position: int | None):
        if time_position:
            self._time_position = time_position
        else:
            self._time_position = round(self.encode_task.input_file.duration / 2, 2)

        if self._time_position > (self.encode_task.input_file.duration - 1):
            self._time_position -= 1

    def _setup_settings_preview_settings(self):
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, 'preview'])
        self.encode_task.is_using_temp_file = True

        self._setup_trim_settings()

    def _setup_trim_settings(self):
        trim_settings = TrimSettings()
        trim_settings.start_time = self.time_position
        trim_settings.trim_duration = self.ENCODE_DURATION
        self.encode_task.trim_settings = trim_settings

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def time_position(self) -> int:
        return self._time_position

    @property
    def preview_file_path(self) -> str:
        with self._preview_thread_lock:
            return self._preview_file_path

    @preview_file_path.setter
    def preview_file_path(self, new_file_path: str):
        with self._preview_thread_lock:
            self._preview_file_path = new_file_path

    def apply_settings_preview_file_path(self):
        self.preview_file_path = self.encode_task.temp_file.file_path


class VideoPreview:
    def __init__(self, encode_task: Encode, video_preview_duration: int, time_position=None):
        self._encode_task = encode_task.get_copy()
        self._parent_encode_task = encode_task
        self._preview_duration = video_preview_duration
        self._is_preview_stopped = False
        self._is_preview_done = False
        self.preview_threading_event = threading.Event()
        self._progress = 0.0
        self._current_time_position = 0.0
        self._current_time_position_lock = threading.Lock()
        self._progress_lock = threading.Lock()
        self._preview_thread_lock = threading.Lock()
        self._preview_file_path = None

        self._setup_time_position(time_position)
        self._setup_video_preview_settings()

    def _setup_time_position(self, time_position: float | None):
        if time_position:
            self._time_position = time_position
        else:
            self._time_position = round(self.encode_task.input_file.duration / 2, 2)

        if self._time_position > (self.encode_task.input_file.duration - self.preview_duration):
            self._time_position -= self.preview_duration

    def _setup_video_preview_settings(self):
        self.encode_task.temp_file.name = '_'.join([self.encode_task.temp_file.name, 'preview'])
        self.encode_task.is_using_temp_file = True

        self._setup_trim_settings()

    def _setup_trim_settings(self):
        trim_settings = TrimSettings()
        trim_settings.start_time = self.time_position
        trim_settings.trim_duration = self.preview_duration
        self.encode_task.trim_settings = trim_settings

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def preview_duration(self) -> int:
        return self._preview_duration

    @property
    def time_position(self) -> float:
        return self._time_position

    @property
    def is_preview_stopped(self) -> bool:
        with self._preview_thread_lock:
            return self._is_preview_stopped

    @is_preview_stopped.setter
    def is_preview_stopped(self, is_stopped: bool):
        with self._preview_thread_lock:
            self._is_preview_stopped = is_stopped

    @property
    def is_preview_done(self) -> bool:
        with self._preview_thread_lock:
            return self._is_preview_done

    @is_preview_done.setter
    def is_preview_done(self, is_done: bool):
        with self._preview_thread_lock:
            self._is_preview_done = is_done

    @property
    def progress(self) -> float:
        with self._progress_lock:
            return self._progress

    @progress.setter
    def progress(self, preview_progress: float):
        with self._progress_lock:
            self._progress = preview_progress

    @property
    def current_time_position(self) -> float:
        with self._current_time_position_lock:
            return self._current_time_position

    @current_time_position.setter
    def current_time_position(self, new_time_position: float):
        with self._current_time_position_lock:
            self._current_time_position = new_time_position

    @property
    def preview_file_path(self) -> str:
        with self._preview_thread_lock:
            return self._preview_file_path

    @preview_file_path.setter
    def preview_file_path(self, new_file_path: str):
        with self._preview_thread_lock:
            self._preview_file_path = new_file_path

    def apply_video_preview_file_path(self):
        self.preview_file_path = self.encode_task.temp_file.file_path

    def reset(self):
        self.is_preview_done = False
        self.is_preview_stopped = False
        self.current_time_position = 0.0
        self.progress = 0.0


class Benchmark:
    SHORT_BENCHMARK_DURATION = 15
    LONG_BENCHMARK_DURATION = 30

    def __init__(self, encode_task: Encode, long_benchmark=False):
        self._encode_task = encode_task.get_copy()
        self._parent_encode_task = encode_task
        self._has_started = False
        self._has_failed = False
        self._is_stopped = False
        self._is_done = False
        self._progress = 0.0
        self._bitrate = None
        self._speed = None
        self._file_size = None
        self._encode_time_estimate = None
        self._current_time_position = None
        self._progress_lock = threading.Lock()
        self._bitrate_lock = threading.Lock()
        self._speed_lock = threading.Lock()
        self._file_size_lock = threading.Lock()
        self._encode_time_estimate_lock = threading.Lock()
        self._current_time_position_lock = threading.Lock()
        self._preview_thread_lock = threading.Lock()

        self._setup_benchmark_duration(long_benchmark)
        self._setup_time_position()
        self._setup_benchmark_settings()

    def _setup_benchmark_duration(self, is_long_benchmark_enabled: bool):
        if is_long_benchmark_enabled:
            self._preview_duration = self.LONG_BENCHMARK_DURATION
        else:
            self._preview_duration = self.SHORT_BENCHMARK_DURATION

    def _setup_time_position(self):
        if (self.encode_task.input_file.duration / self.preview_duration) >= 2:
            self._time_position = self.encode_task.input_file.duration / 2
        else:
            self._time_position = 0.0

    def _setup_benchmark_settings(self):
        self.encode_task.temp_file.name = 'benchmark'
        self.encode_task.is_using_temp_file = True

        self._setup_trim_settings()

    def _setup_trim_settings(self):
        trim_settings = TrimSettings()
        trim_settings.start_time = self.time_position
        trim_settings.trim_duration = self.preview_duration
        self.encode_task.trim_settings = trim_settings

    def reset(self):
        self.has_started = False
        self.has_failed = False
        self.is_stopped = False
        self.is_done = False
        self.progress = 0.0
        self.bitrate = None
        self.speed = None
        self.file_size = None
        self.encode_time_estimate = None
        self.current_time_position = None

    @property
    def encode_task(self) -> Encode:
        return self._encode_task

    @property
    def parent_encode_task(self) -> Encode:
        return self._parent_encode_task

    @property
    def preview_duration(self) -> int:
        with self._preview_thread_lock:
            return self._preview_duration

    @property
    def time_position(self) -> float:
        with self._preview_thread_lock:
            return self._time_position

    @property
    def has_started(self) -> bool:
        with self._preview_thread_lock:
            return self._has_started

    @has_started.setter
    def has_started(self, has_benchmark_started: bool):
        with self._preview_thread_lock:
            self._has_started = has_benchmark_started

    @property
    def has_failed(self) -> bool:
        with self._preview_thread_lock:
            return self._has_failed

    @has_failed.setter
    def has_failed(self, has_benchmark_failed: bool):
        with self._preview_thread_lock:
            self._has_failed = has_benchmark_failed

    @property
    def is_stopped(self) -> bool:
        with self._preview_thread_lock:
            return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, is_benchmark_stopped: bool):
        with self._preview_thread_lock:
            self._is_stopped = is_benchmark_stopped

    @property
    def is_done(self) -> bool:
        with self._preview_thread_lock:
            return self._is_done

    @is_done.setter
    def is_done(self, is_benchmark_done: bool):
        with self._preview_thread_lock:
            self._is_done = is_benchmark_done

    @property
    def progress(self) -> float:
        with self._progress_lock:
            return self._progress

    @progress.setter
    def progress(self, new_progress: float):
        with self._progress_lock:
            self._progress = new_progress

    @property
    def bitrate(self) -> float:
        with self._bitrate_lock:
            return self._bitrate

    @bitrate.setter
    def bitrate(self, new_bitrate: float):
        with self._bitrate_lock:
            self._bitrate = new_bitrate

    @property
    def speed(self) -> float:
        with self._speed_lock:
            return self._speed

    @speed.setter
    def speed(self, new_speed: float):
        with self._speed_lock:
            self._speed = new_speed

    @property
    def file_size(self) -> int:
        with self._file_size_lock:
            return self._file_size

    @file_size.setter
    def file_size(self, new_file_size: int):
        with self._file_size_lock:
            self._file_size = new_file_size

    @property
    def encode_time_estimate(self) -> float:
        with self._encode_time_estimate_lock:
            return self._encode_time_estimate

    @encode_time_estimate.setter
    def encode_time_estimate(self, new_encode_time_estimate: float):
        with self._encode_time_estimate_lock:
            self._encode_time_estimate = new_encode_time_estimate

    @property
    def current_time_position(self) -> float:
        with self._current_time_position_lock:
            return self._current_time_position

    @current_time_position.setter
    def current_time_position(self, new_time_position: float):
        with self._current_time_position_lock:
            self._current_time_position = new_time_position
