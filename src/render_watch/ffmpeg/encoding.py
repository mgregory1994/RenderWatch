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
import subprocess
import threading
import copy

from render_watch.ffmpeg import input, output
from render_watch.ffmpeg import trim
from render_watch.ffmpeg import filters
from render_watch.ffmpeg import general_settings, h264_nvenc, hevc_nvenc, x264, x265, vp9, aac, opus
from render_watch.helpers import ffmpeg_helper, nvidia_helper
from render_watch import app_preferences


class Task:
    """
    Class that configures the encoding task with all necessary variables to store settings about the task's
    input file, output file, video codec, audio codec, filters, general settings, task type as well as information
    about the task's encoding status.
    """

    VIDEO_CODECS_MP4_UI = ['copy', 'H264', 'H265']
    VIDEO_CODECS_MKV_UI = ['copy', 'H264', 'H265', 'VP9']
    VIDEO_CODECS_TS_UI = ['copy', 'H264']
    VIDEO_CODECS_WEBM_UI = ('copy', 'VP9')

    AUDIO_CODECS_MP4_UI = ('copy', 'aac')
    AUDIO_CODECS_MP4 = ('copy', 'aac')
    AUDIO_CODECS_MKV_UI = ('copy', 'aac', 'opus')
    AUDIO_CODECS_MKV = ('copy', 'aac', 'libopus')
    AUDIO_CODECS_TS_UI = ('copy', 'aac')
    AUDIO_CODECS_TS = ('copy', 'aac')
    AUDIO_CODECS_WEBM_UI = ('copy', 'opus')
    AUDIO_CODECS_WEBM = ('copy', 'libopus')

    def __init__(self, input_file_path: str, app_settings: app_preferences.Settings, video_chunk=False):
        """Initializes the Task class with all necessary variables for storing its setting and encode status."""
        self.app_settings = app_settings
        self.input_file = input.InputFile(input_file_path)
        self.output_file = output.OutputFile(self.input_file, self.app_settings)
        self.temp_output_file = output.TempOutputFile(self.input_file, self.app_settings.temp_directory)
        self.is_using_temp_output_file = False
        self.general_settings = general_settings.GeneralSettings()
        self.video_stream = None
        self.video_codec = x264.X264()
        self.audio_streams = {}
        self.trim = None
        self.filter = filters.Filter(self.input_file)
        self._bitrate = None
        self._file_size = None
        self._speed = None
        self._time_left = None
        self._current_position = None
        self._progress = None
        self._video_preview_progress = None
        self._video_preview_current_position = None
        self.video_preview_duration = None
        self._benchmark_bitrate = None
        self._benchmark_speed = None
        self._benchmark_current_position = None
        self._benchmark_progress = None
        self._benchmark_file_size = None
        self._benchmark_time_estimate = None
        self._bitrate_lock = threading.Lock()
        self._file_size_lock = threading.Lock()
        self._speed_lock = threading.Lock()
        self._time_left_lock = threading.Lock()
        self._current_position_lock = threading.Lock()
        self._progress_lock = threading.Lock()
        self._video_preview_current_position_lock = threading.Lock()
        self._video_preview_progress_lock = threading.Lock()
        self._benchmark_bitrate_lock = threading.Lock()
        self._benchmark_speed_lock = threading.Lock()
        self._benchmark_current_position_lock = threading.Lock()
        self._benchmark_progress_lock = threading.Lock()
        self._benchmark_file_size_lock = threading.Lock()
        self._benchmark_time_estimate_lock = threading.Lock()
        self._task_thread_lock = threading.Lock()
        self.is_video_chunk = video_chunk
        self._is_watch_folder = False
        self.is_no_video = False
        self.is_no_audio = False
        self._has_started = False
        self._is_paused = False
        self._is_idle = False
        self._is_stopped = False
        self._is_done = False
        self._has_failed = False
        self._has_benchmark_started = False
        self._is_benchmark_stopped = False
        self._is_video_preview_stopped = False
        self._is_video_preview_done = False
        self.paused_threading_event = threading.Event()
        self.video_preview_threading_event = threading.Event()
        self.duration = 0
        self.child_encoding_task = None

        self._set_default_streams()

    def _set_default_streams(self):
        # Set up the initial default streams for video and audio streams.
        if self.input_file.is_folder:
            return

        if self.input_file.is_video:
            self.video_stream = self.input_file.video_streams[0]

        if self.input_file.is_audio:
            self.add_audio_stream(self.input_file.audio_streams[0])
            default_audio_codec = aac.Aac(self.get_audio_stream_index(self.input_file.audio_streams[0]))
            self.set_audio_stream_codec(self.input_file.audio_streams[0], default_audio_codec)

    @property
    def bitrate(self) -> float:
        """
        Returns the encoding status for the bitrate of the task. This property is thread safe.

        Returns:
            Bitrate of the encoding task as an integer.
        """
        with self._bitrate_lock:
            return self._bitrate

    @bitrate.setter
    def bitrate(self, bitrate_value: float):
        """
        Sets the bitrate status of the encoding task. This property is thread safe.

        Parameters:
            bitrate_value: Bitrate value for the encoding task's bitrate status.

        Returns:
            None
        """
        with self._bitrate_lock:
            self._bitrate = bitrate_value

    @property
    def file_size(self) -> int:
        """
        Returns the encoding status for the file size of the task. This property is thread safe.

        Returns:
            File size of the encoding task as an integer representing the file size in bytes.
        """
        with self._file_size_lock:
            return self._file_size

    @file_size.setter
    def file_size(self, file_size_value: int):
        """
        Sets the file size status of the encoding task. This property is thread safe.

        Parameters:
            file_size_value: File size value in bytes for the encoding task's file size status.

        Returns:
            None
        """
        with self._file_size_lock:
            self._file_size = file_size_value

    @property
    def speed(self) -> float:
        """
        Returns the encoding status for the speed of the task. This property is thread safe.

        Returns:
            Speed ratio of the encoding task as a float.
        """
        with self._speed_lock:
            return self._speed

    @speed.setter
    def speed(self, speed_value: float):
        """
        Sets the speed status of the encoding task. This property is thread safe.

        Parameters:
            speed_value: Speed ratio value for the encoding task's speed status.

        Returns:
            None
        """
        with self._speed_lock:
            self._speed = speed_value

    @property
    def time_left_in_seconds(self) -> int:
        """
        Returns the encoding status for the time left of the task. This property is thread safe.

        Returns:
            Time left of the encoding task as an integer in seconds.
        """
        with self._time_left_lock:
            return self._time_left

    @time_left_in_seconds.setter
    def time_left_in_seconds(self, encoder_time_left: int):
        """
        Sets the time left status of the encoding task. This property is thread safe.

        Parameters:
            encoder_time_left: Time left value in seconds for the encoding task's time left status.

        Returns:
            None
        """
        with self._time_left_lock:
            self._time_left = encoder_time_left

    @property
    def current_position(self) -> int:
        """
        Returns the encoding task's current position. This property is thread safe.

        Returns:
            Encoding task's current position in seconds.
        """
        with self._current_position_lock:
            return self._current_position

    @current_position.setter
    def current_position(self, current_position_value: int):
        """
        Sets the encoding task's current position. This property is thread safe.

        Parameters:
            current_position_value: Encoding task's current position in seconds.

        Returns:
            None
        """
        with self._current_position_lock:
            self._current_position = current_position_value

    @property
    def progress(self) -> float:
        """
        Returns the encoding progress from 0.0 - 1.0. This property is thread safe.

        Returns:
            Progress of the encoding task as a float from 0.0 - 1.0.
        """
        with self._progress_lock:
            return self._progress

    @progress.setter
    def progress(self, task_progress: float):
        """
        Sets the encoding task progress to the specified value. This property is thread safe.

        Parameters:
            task_progress: Encoding task progress as a float from 0.0 - 1.0.

        Returns:
            None
        """
        with self._progress_lock:
            self._progress = task_progress

    @property
    def video_preview_current_position(self) -> int:
        """
        Returns the preview task's current position. This property is thread safe.

        Returns:
            Integer that represents the preview task's current position in seconds.
        """
        with self._video_preview_current_position_lock:
            return self._video_preview_current_position

    @video_preview_current_position.setter
    def video_preview_current_position(self, current_position_value: int):
        """
        Sets the video preview task's current position. This property is thread safe.

        Parameters:
            current_position_value: Video preview task's current position in seconds.
        """
        with self._video_preview_current_position_lock:
            self._video_preview_current_position = current_position_value

    @property
    def video_preview_progress(self) -> float:
        """
        Returns the video preview's progress from 0.0 - 1.0. This property is thread safe.

        Returns:
            Progress of the video preview as a float from 0.0 - 1.0.
        """
        with self._video_preview_progress_lock:
            return self._video_preview_progress

    @video_preview_progress.setter
    def video_preview_progress(self, preview_progress: float):
        """
        Sets the video preview's progress to the specified value. This property is thread safe.

        Parameters:
            preview_progress: Video preview's progress as a float from 0.0 - 1.0.

        Returns:
            None
        """
        with self._video_preview_progress_lock:
            self._video_preview_progress = preview_progress

    @property
    def benchmark_bitrate(self) -> float:
        """
        Returns the benchmark task's bitrate. This property is thread safe.

        Returns:
            Benchmark task's bitrate as an integer.
        """
        with self._benchmark_bitrate_lock:
            return self._benchmark_bitrate

    @benchmark_bitrate.setter
    def benchmark_bitrate(self, bitrate: float):
        """
        Sets the benchmark task's bitrate to the specified value. This property is thread safe.

        Parameters:
            bitrate: Benchmark task's bitrate as an integer.

        Returns:
            None
        """
        with self._benchmark_bitrate_lock:
            self._benchmark_bitrate = bitrate

    @property
    def benchmark_speed(self) -> float:
        """
        Returns the benchmark task's encoding speed ratio. This property is thread safe.

        Returns:
            Benchmark task's encoding speed ratio as a float.
        """
        with self._benchmark_speed_lock:
            return self._benchmark_speed

    @benchmark_speed.setter
    def benchmark_speed(self, speed: float):
        """
        Sets the benchmark task's encoding speed ratio to the specified value. This property is thread safe.

        Parameters:
            speed: Benchmark task's speed ratio as a float.

        Returns:
            None
        """
        with self._benchmark_speed_lock:
            self._benchmark_speed = speed

    @property
    def benchmark_current_position(self) -> int:
        """
        Returns the benchmark task's current time position. This property is thread safe.

        Returns:
            Benchmark task's current time position as an integer that represents the current time position in seconds.
        """
        with self._benchmark_current_position_lock:
            return self._benchmark_current_position

    @benchmark_current_position.setter
    def benchmark_current_position(self, current_position: int):
        """
        Sets the benchmark task's current time position. This property is thread safe.

        Parameters:
            current_position: Benchmark task's current time position as an integer that represents the
            current time position in seconds.
        """
        with self._benchmark_current_position_lock:
            self._benchmark_current_position = current_position

    @property
    def benchmark_progress(self) -> float:
        """
        Returns the benchmark task's progress from 0.0 - 1.0. This property is thread safe.

        Returns:
            Progress of the benchmark task as a float from 0.0 - 1.0.
        """
        with self._benchmark_progress_lock:
            return self._benchmark_progress

    @benchmark_progress.setter
    def benchmark_progress(self, progress: float):
        """
        Sets the benchmark task's progress to the specified value. This property is thread safe.

        Parameters:
            progress: Benchmark task's progress as a float from 0.0 - 1.0.

        Returns:
            None
        """
        with self._benchmark_progress_lock:
            self._benchmark_progress = progress

    @property
    def benchmark_file_size(self) -> int:
        """
        Returns the benchmark task's file size in bytes. This property is thread safe.

        Returns:
            File size of the benchmark task as an int that represents file size in bytes.
        """
        with self._benchmark_file_size_lock:
            return self._benchmark_file_size

    @benchmark_file_size.setter
    def benchmark_file_size(self, file_size: int):
        """
        Sets the benchmark task's file size to the specified value. This property is thread safe.

        Parameters:
            file_size: Benchmark task's file size as an int that represents the file size in bytes.

        Returns:
            None
        """
        with self._benchmark_file_size_lock:
            self._benchmark_file_size = file_size

    @property
    def benchmark_time_estimate(self) -> int:
        """
        Returns the benchmark task's encoding time estimate. This property is thread safe.

        Returns:
            Benchmark task's encoding time estimate as an int that represents the number of seconds.
        """
        with self._benchmark_time_estimate_lock:
            return self._benchmark_time_estimate

    @benchmark_time_estimate.setter
    def benchmark_time_estimate(self, time_estimate: int):
        """
        Sets the benchmark task's encoding time estimate. This property is thread safe.

        Parameters:
            time_estimate: Benchmark task's time estimate as an int that represents the number of seconds.

        Returns:
            None
        """
        with self._benchmark_time_estimate_lock:
            self._benchmark_time_estimate = time_estimate

    @property
    def has_started(self) -> bool:
        """
        Returns whether the task has started encoding. This property is thread safe.

        Returns:
            Boolean that represents whether the task has started encoding.
        """
        with self._task_thread_lock:
            return self._has_started

    @has_started.setter
    def has_started(self, has_encoder_started: bool):
        """
        Sets whether the task has started encoding. This property is thread safe.

        Parameters:
            has_encoder_started: Boolean that represents whether the task has started encoding.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._has_started = has_encoder_started

    @property
    def is_paused(self) -> bool:
        """
        Returns whether the task has been paused while encoding. This property is thread safe.

        Returns:
            Boolean that represents whether the task has been paused while encoding.
        """
        with self._task_thread_lock:
            return self._is_paused

    @is_paused.setter
    def is_paused(self, is_encoder_paused: bool):
        """
        Sets whether the task has been paused while encoding. This property is thread safe.

        Parameters:
            is_encoder_paused: Boolean that represents whether the task has been paused while encoding.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._is_paused = is_encoder_paused

            if self.child_encoding_task:
                self.child_encoding_task.is_paused = is_encoder_paused

    @property
    def is_idle(self) -> bool:
        """
        Returns whether the task is idling while encoding. This applies to watch folder encoding tasks only.
        This property is thread safe.

        Returns:
            Boolean that represents whether the task is idling while encoding.
        """
        with self._task_thread_lock:
            return self._is_idle

    @is_idle.setter
    def is_idle(self, is_encoder_idle: bool):
        """
        Sets whether the task is idling while encoding. This applies to watch folder encoding tasks only.
        This property is thread safe.

        Parameters:
            is_encoder_idle: Boolean that represents whether the task is idling while encoding.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._is_idle = is_encoder_idle

    @property
    def is_stopped(self) -> bool:
        """
        Returns whether the task has been stopped while encoding. This property is thread safe.

        Returns:
            Boolean that represents whether the task has been stopped while encoding.
        """
        with self._task_thread_lock:
            return self._is_stopped

    @is_stopped.setter
    def is_stopped(self, is_encoder_stopped: bool):
        """
        Sets whether the task has been stopped while encoding. This property is thread safe.

        Parameters:
            is_encoder_stopped: Boolean that represents whether the task has been stopped while encoding.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._is_stopped = is_encoder_stopped

            if self.child_encoding_task:
                self.child_encoding_task.is_stopped = is_encoder_stopped

    @property
    def is_done(self) -> bool:
        """
        Returns whether the task has finished encoding. This property is thread safe.

        Returns:
            Boolean that represents whether the task has finished encoding.
        """
        with self._task_thread_lock:
            return self._is_done

    @is_done.setter
    def is_done(self, is_encoder_done: bool):
        """
        Sets whether the task has finished encoding. This property is thread safe.

        Parameters:
            is_encoder_done: Boolean that represents whether the task has finished encoding.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._is_done = is_encoder_done

    @property
    def has_failed(self) -> bool:
        """
        Returns whether the task has failed while encoding. This property is thread safe.

        Returns:
            Boolean that represents whether the task has failed while encoding.
        """
        with self._task_thread_lock:
            return self._has_failed

    @has_failed.setter
    def has_failed(self, has_encoder_failed: bool):
        """
        Sets whether the task has failed while encoding. This property is thread safe.

        Parameters:
            has_encoder_failed: Boolean that represents whether the task has failed while encoding.

        Returns:
            None
        """
        if self.has_failed:
            return

        with self._task_thread_lock:
            self._has_failed = has_encoder_failed

    @property
    def has_benchmark_started(self) -> bool:
        """
        Returns whether the benchmark task has started. This property is thread safe.

        Returns:
            Boolean that represents whether the benchmark task has started.
        """
        with self._task_thread_lock:
            return self._has_benchmark_started

    @has_benchmark_started.setter
    def has_benchmark_started(self, has_started: bool):
        """
        Sets whether the benchmark task has started. This property is thread safe.

        Parameters:
            has_started: Boolean that represents whether the benchmark task has started.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._has_benchmark_started = has_started

    @property
    def is_benchmark_stopped(self) -> bool:
        """
        Returns whether the benchmark task has stopped. This property is thread safe.

        Returns:
            Boolean that represents whether the benchmark task has stopped.
        """
        with self._task_thread_lock:
            return self._is_benchmark_stopped

    @is_benchmark_stopped.setter
    def is_benchmark_stopped(self, is_stopped: bool):
        """
        Sets whether the benchmark task has stopped. This property is thread safe.

        Parameters:
            is_stopped: Boolean that represents whether the benchmark task has stopped.

        Returns:
            None
        """
        with self._task_thread_lock:
            self._is_benchmark_stopped = is_stopped

    @property
    def is_video_preview_done(self) -> bool:
        """
        Returns whether the video preview task has finished. This property is thread safe.

        Returns:
            Boolean that represents whether the video preview task has finished.
        """
        with self._task_thread_lock:
            return self._is_video_preview_done

    @is_video_preview_done.setter
    def is_video_preview_done(self, is_done: bool):
        """
        Sets whether the video preview task has finished. This property is thread safe.

        Parameters:
            is_done: Boolean that represents whether the video preview task has finished.
        """
        with self._task_thread_lock:
            self._is_video_preview_done = is_done

    @property
    def is_video_preview_stopped(self) -> bool:
        """
        Returns whether the video preview task has stopped. This property is thread safe.

        Returns:
            Boolean that represents whether the video preview task has stopped.
        """
        with self._task_thread_lock:
            return self._is_video_preview_stopped

    @is_video_preview_stopped.setter
    def is_video_preview_stopped(self, is_stopped: bool):
        """
        Sets whether the video preview task has stopped. This property is thread safe.

        Parameters:
            is_stopped: Boolean that represents whether the video preview task has stopped.
        """
        with self._task_thread_lock:
            self._is_video_preview_stopped = is_stopped

    @property
    def is_watch_folder(self) -> bool:
        """
        Returns whether this task is a watch folder task.

        Returns:
            Boolean that represents whether this task is a watch folder task.
        """
        if self.input_file.is_folder:
            return self._is_watch_folder
        return False

    @is_watch_folder.setter
    def is_watch_folder(self, is_encoding_task_watch_folder: bool):
        """
        Sets whether this task is a watch folder task.

        Parameters:
            is_encoding_task_watch_folder: Boolean that represents whether this task is a watch folder task.

        Returns:
            None
        """
        self._is_watch_folder = is_encoding_task_watch_folder

    def add_audio_stream(self, audio_stream: input.AudioStream):
        """
        Adds the audio stream to the task's dictionary of audio streams and sets its codec to None.

        Parameters:
            audio_stream: Audio stream to add.

        Returns:
            None
        """
        self.audio_streams[audio_stream] = None

    def remove_audio_stream(self, audio_stream: input.AudioStream):
        """
        Removes the given audio stream from the task's dictionary of audio streams.

        Parameters:
            audio_stream: Audio stream to remove.

        Returns:
            None
        """
        self.audio_streams.pop(audio_stream, 0)

    def set_audio_stream_codec(self, audio_stream: input.AudioStream, audio_codec):
        """
        Sets the given audio codec for the given audio stream. If the audio stream has been added to the task's
        dictionary of audio streams, then the given audio codec is set as its codec.

        Parameters:
            audio_stream: Audio stream that will have its audio codec changed.
            audio_codec: Audio codec to use for the given audio stream.

        Returns:
            None
        """
        if audio_stream in self.audio_streams:
            self.audio_streams[audio_stream] = audio_codec

    def get_audio_stream_codec(self, audio_stream: input.AudioStream):
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

    def get_audio_stream_index(self, audio_stream: input.AudioStream) -> int | None:
        """
        Returns the index of what position the given audio stream is in the task's audio streams dictionary.

        Returns:
            Index that represents the given audio stream's position in the task's audio streams dictionary.
        """
        if audio_stream in self.audio_streams:
            audio_streams_list = list(self.audio_streams)

            return audio_streams_list.index(audio_stream)
        return None

    def is_video_copy(self) -> bool:
        """
        Returns whether the task's video codec is set to the copy codec.

        Returns:
            Boolean that represents whether the task's video codec is set to the copy codec.
        """
        return self.video_codec is None

    def is_audio_copy(self) -> bool:
        """
        Returns whether an audio stream in the task's audio streams dictionary contains a copy codec.

        Returns:
            Boolean that represents whether there's an audio stream in the task's audio streams dictionary that
            contains a copy codec.
        """
        for audio_stream, audio_codec in self.audio_streams.items():
            if audio_codec is None:
                return True
        return False

    def is_video_h264_nvenc(self) -> bool:
        """
        Returns whether the task's video codec is the h264_nvenc video codec.

        Returns:
            Boolean that represents whether the task's video codec is the h264_nvenc video codec.
        """
        return isinstance(self.video_codec, h264_nvenc.H264Nvenc)

    def is_video_hevc_nvenc(self) -> bool:
        """
        Returns whether the task's video codec is the hevc_nvenc video codec.

        Returns:
            Boolean that represents whether the task's video codec is the hevc_nvenc video codec.
        """
        return isinstance(self.video_codec, hevc_nvenc.HevcNvenc)

    def is_video_nvenc(self) -> bool:
        """
        Returns whether the task's video codec is a type of nvenc codec.

        Returns:
            Boolean that represents whether the task's video codec is a type of nvenc codec.
        """
        return self.is_video_hevc_nvenc() or self.is_video_h264_nvenc()

    def is_video_x264(self) -> bool:
        """
        Returns whether the task's video codec is the x264 video codec.

        Returns:
            Boolean that represents whether the task's video codec is the x264 video codec.
        """
        return isinstance(self.video_codec, x264.X264)

    def is_video_x265(self) -> bool:
        """
        Returns whether the task's video codec is the x265 video codec.

        Returns:
            Boolean that represents whether the task's video codec is the x265 video codec.
        """
        return isinstance(self.video_codec, x265.X265)

    def is_video_vp9(self) -> bool:
        """
        Returns whether the task's video codec is the vp9 video codec.

        Returns:
            Boolean that represents whether the task's video codec is the vp9 video codec.
        """
        return isinstance(self.video_codec, vp9.VP9)

    def is_video_2_pass(self):
        """
        Returns whether the task's video codec has the encode pass setting set.

        Returns:
            Boolean that represents whether the task's video codec has the encode pass setting set.
        """
        if self.video_codec:
            return self.video_codec.encode_pass == 1 or self.video_codec.encode_pass == 2
        return False

    def is_audio_stream_codec_copy(self, audio_stream: input.AudioStream):
        """
        Returns whether the audio stream's codec is set to be the copy codec.

        Returns:
            Boolean that represents whether the audio stream's codec is set to be the copy codec.
        """
        return self.get_audio_stream_codec(audio_stream) is None

    def is_audio_stream_codec_aac(self, audio_stream: input.AudioStream):
        """
        Returns whether the audio stream's codec is the AAC codec.

        Returns:
            Boolean that represents whether the audio stream's codec is the AAC codec.
        """
        return isinstance(self.get_audio_stream_codec(audio_stream), aac.Aac)

    def is_audio_stream_codec_opus(self, audio_stream: input.AudioStream):
        """
        Returns whether the audios stream's codec is the Opus codec.

        Returns:
            Boolean that represents whether the audio stream's codec is the Opus codec.
        """
        return isinstance(self.get_audio_stream_codec(audio_stream), opus.Opus)

    def is_nvenc_codec_settings_valid(self) -> bool:
        """
        Returns whether the task's nvenc video codec has valid settings by running a quick test of the current video
        codec's settings using a null input and output. If the test passes, then the settings will work on the
        user's machine.

        Returns:
            Boolean that represents whether the current nvenc video codec settings will work on their machine.
        """
        if not self.is_video_nvenc():
            return False

        test_process_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        test_process_args.append('-f')
        test_process_args.append('lavfi')
        test_process_args.append('-i')
        test_process_args.append('nullsrc=s=256x256:d=5')
        test_process_args.extend(FFmpegArgs.get_args_from_dict(self.video_codec.ffmpeg_args))
        test_process_args.extend(FFmpegArgs.get_args_from_dict(self.video_codec.get_ffmpeg_advanced_args()))
        test_process_args.append('-f')
        test_process_args.append('null')
        test_process_args.append('-')

        return nvidia_helper.Compatibility.run_test_process(test_process_args)

    def get_copy(self):
        """
        Returns an exact copy of this task.

        Returns:
            An encoding task that's an exact copy of this task.
        """
        task_copy = Task(self.input_file.file_path, self.app_settings, self.is_video_chunk)

        try:
            task_copy.video_stream = self.video_stream
            task_copy.audio_streams = self.audio_streams
            task_copy.is_no_video = self.is_no_video
            task_copy.is_no_audio = self.is_no_audio
            task_copy.filter = copy.deepcopy(self.filter)
            task_copy.audio_streams = copy.deepcopy(self.audio_streams)
            task_copy.video_preview_duration = self.video_preview_duration

            if self.general_settings:
                task_copy.general_settings = copy.deepcopy(self.general_settings)

            if self.video_codec:
                task_copy.video_codec = copy.deepcopy(self.video_codec)

            if self.trim:
                task_copy.trim = copy.deepcopy(self.trim)
        except:
            logging.exception('---FAILED TO CREATE TASK COPY---')
        finally:
            return task_copy

    def get_info(self) -> list:
        return FFmpegArgs.get_args(self, cli_args=True)


class Parallel:
    """Class that contains functions for setting up an encoding task for parallel encoding."""

    MIN_CHUNK_LENGTH_SECONDS = 10

    @staticmethod
    def get_task_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> tuple | None:
        """
        Returns a tuple containing encoding tasks that are chunks of the given encoding task. Returns None if
        chunking is not possible for the given encoding task.

        Returns:
            Tuple containing encoding tasks that are chunks of the given encoding task. Or None if
            chunking is not possible.
        """
        number_of_chunks = Parallel._get_number_of_chunks(encoding_task, app_settings)

        if Parallel._is_task_chunkable(encoding_task, number_of_chunks):
            return Parallel._get_task_chunks_tuple(encoding_task, number_of_chunks)
        return None

    @staticmethod
    def _get_number_of_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> int:
        # Returns the number of encoding task chunks to generate from the given encoding task.
        if encoding_task.is_video_nvenc():
            return nvidia_helper.Parallel.nvenc_max_workers
        return Parallel._get_per_codec_number_of_chunks(encoding_task, app_settings)

    @staticmethod
    def _get_per_codec_number_of_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> int:
        # Returns the number of encoding task chunks to generate depending on which video codec the task is using.
        if encoding_task.is_video_x264():
            return app_settings.per_codec_x264

        if encoding_task.is_video_x265():
            return app_settings.per_codec_x265

        if encoding_task.is_video_vp9():
            return app_settings.per_codec_vp9
        return 1

    @staticmethod
    def _is_task_chunkable(encoding_task: Task, number_of_chunks: int) -> bool:
        # Returns a boolean representing whether it's possible to generate chunks from the given encoding task.
        if encoding_task.is_video_copy() or encoding_task.is_no_video:
            return False

        if encoding_task.trim and not encoding_task.is_audio_copy():
            if (encoding_task.trim.trim_duration / number_of_chunks) >= Parallel.MIN_CHUNK_LENGTH_SECONDS:
                return True
        elif (encoding_task.input_file.duration / number_of_chunks) >= Parallel.MIN_CHUNK_LENGTH_SECONDS:
            return True
        return False

    @staticmethod
    def _get_task_chunks_tuple(encoding_task: Task, number_of_chunks: int) -> tuple:
        # Generates the given number of encoding task chunks from the given encoding task.
        task_chunks = []

        for index in range(1, (number_of_chunks + 1)):
            task_chunks.append(Parallel._get_video_task_chunk(encoding_task, number_of_chunks, index))
        task_chunks.append(Parallel._get_audio_task_chunk(encoding_task))

        return tuple(task_chunks)

    @staticmethod
    def _get_video_task_chunk(encoding_task: Task, number_of_chunks: int, index: int) -> Task:
        # Returns an encoding task chunk at the given index using the given encoding task.
        video_task_chunk = encoding_task.get_copy()
        video_task_chunk.trim = Parallel._get_video_task_trim_settings(encoding_task, number_of_chunks, index)

        if video_task_chunk.is_video_2_pass():
            video_task_chunk.video_codec.stats = ''.join([video_task_chunk.temp_output_file.dir,
                                                          '/',
                                                          video_task_chunk.temp_output_file.name,
                                                          '.log'])

        video_task_chunk.is_no_audio = True
        video_task_chunk.is_video_chunk = True
        video_task_chunk.temp_output_file.name = ''.join([video_task_chunk.temp_output_file.name, '_', str(index)])

        if video_task_chunk.is_video_vp9():
            video_task_chunk.temp_output_file.extension = '.webm'
        else:
            video_task_chunk.temp_output_file.extension = '.mp4'

        return video_task_chunk

    @staticmethod
    def _get_video_task_trim_settings(encoding_task: Task, number_of_chunks: int, index: int) -> trim.TrimSettings:
        # Returns trim settings to use for an encoding task chunk at the given index.
        trim_settings = trim.TrimSettings()

        if encoding_task.trim:
            trim_duration = encoding_task.trim.trim_duration
            trim_start_time = encoding_task.trim.start_time
            chunk_duration = (trim_duration / number_of_chunks)
            chunk_start_time = trim_start_time + (chunk_duration * (index - 1))

            if index == 1:
                trim_settings.start_time = trim_start_time
                trim_settings.trim_duration = chunk_duration
            elif index == number_of_chunks:
                chunk_duration_offset = (trim_duration + trim_start_time) - chunk_start_time
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration_offset
            else:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration
        else:
            input_duration = encoding_task.input_file.duration
            chunk_duration = (input_duration / number_of_chunks)
            chunk_start_time = chunk_duration * (index - 1)

            if index == 1:
                trim_settings.start_time = 0
                trim_settings.trim_duration = chunk_duration
            elif index == number_of_chunks:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = input_duration - chunk_start_time
            else:
                trim_settings.start_time = chunk_start_time
                trim_settings.trim_duration = chunk_duration

        return trim_settings

    @staticmethod
    def _get_audio_task_chunk(encoding_task: Task):
        # Returns an encoding task chunk for the audio of the given encoding task.
        audio_task_chunk = encoding_task.get_copy()
        audio_task_chunk.is_no_video = True
        audio_task_chunk.temp_output_file.extension = '.mkv'
        audio_task_chunk.temp_output_file.name = audio_task_chunk.temp_output_file.name + '_audio'

        return audio_task_chunk

    @staticmethod
    def concatenate_video_task_chunks(task_chunks: tuple, encoding_task: Task):
        """
        Takes the given tuple of encoding task chunks and runs a subprocess to concatenate them into
        a single video file that has the same settings as the given encoding task.

        Parameters:
            task_chunks: Tuple that contains the encoding task chunks.
            encoding_task: Original encoding task that the task chunks are based off of.

        Returns:
            None
        """
        chunk_list_file_path = ''.join([encoding_task.temp_output_file.dir,
                                        '/',
                                        encoding_task.temp_output_file.name,
                                        '_concat'])
        concatenation_args = Parallel._get_video_concatenation_args(task_chunks)

        if Parallel._write_concatenation_args(encoding_task, chunk_list_file_path, concatenation_args):
            concatenation_process_args = Parallel._get_concatenation_process_args(encoding_task, chunk_list_file_path)
            Parallel._run_process_args(encoding_task, concatenation_process_args)

    @staticmethod
    def _get_video_concatenation_args(task_chunks: tuple) -> list:
        # Returns a list of strings that represent the concatenation args that ffmpeg will use.
        concatenation_args = []

        for video_task_chunk in task_chunks:
            if video_task_chunk.is_no_video():
                continue

            concatenation_args.append(''.join(['file \'',
                                               video_task_chunk.temp_output_file.name,
                                               video_task_chunk.temp_output_file.extension,
                                               '\'\n']))

        return concatenation_args

    @staticmethod
    def _write_concatenation_args(encoding_task: Task, chunk_list_file_path: str, concatenation_args: list) -> bool:
        # Writes the given concatenation args to a file at the given chunk list file path.
        try:
            with open(chunk_list_file_path, 'w') as concatenation_file:
                concatenation_file.writelines(concatenation_args)

            return True
        except OSError:
            logging.error(''.join(['--- FAILED TO CONCAT VIDEO CHUNKS: ', encoding_task.input_file.name, ' ---']))

            return False

    @staticmethod
    def _get_concatenation_process_args(encoding_task: Task, chunk_list_file_path: str) -> list:
        # Returns a list of ffmpeg arguments that will concatenate the encoding task chunks.
        process_args = ffmpeg_helper.FFMPEG_CONCATENATION_INIT_ARGS.copy()
        process_args.append(chunk_list_file_path)
        process_args.append('-c')
        process_args.append('copy')
        process_args.append(''.join([encoding_task.temp_output_file.dir,
                                     '/',
                                     encoding_task.output_file.name,
                                     encoding_task.output_file.extension]))

        return process_args

    @staticmethod
    def _run_process_args(encoding_task: Task, process_args: list):
        # Runs a subprocess for the given encoding task using the given process args.
        with subprocess.Popen(process_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as process:
            stdout_log = ''

            while True:
                stdout = process.stdout.readline().strip()

                if stdout == '' and process.poll() is not None:
                    break

                stdout_log = ''.join([stdout_log, stdout, '\n'])

            concatenation_process_return_code = process.wait()

            if concatenation_process_return_code:
                logging.error(''.join(['--- FAILED TO RUN PROCESS: ',
                                       encoding_task.input_file.name,
                                       ' ---\n',
                                       str(process_args),
                                       '\n',
                                       stdout_log]))

    @staticmethod
    def mux_chunks(task_chunks: tuple, encoding_task: Task, app_settings: app_preferences.Settings):
        """
        Runs a subprocess that uses ffmpeg to mux the concatenated encoding task chunks and the
        encoding task audio chunk into a single video file.

        Parameters:
            task_chunks: Tuple containing the encoding task chunks.
            encoding_task: Original encoding task that the encoding task chunks are based off of.
            app_settings: Application settings.

        Returns:
            None
        """
        mux_chunks_process_args = Parallel._get_mux_chunks_process_args(task_chunks, encoding_task, app_settings)
        Parallel._run_process_args(encoding_task, mux_chunks_process_args)

    @staticmethod
    def _get_mux_chunks_process_args(task_chunks: tuple,
                                     encoding_task: Task,
                                     app_settings: app_preferences.Settings) -> list:
        # Returns a list of subprocess arguments to mux the chunked files using ffmpeg.
        audio_task_chunk = task_chunks[-1]

        mux_chunks_process_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        mux_chunks_process_args.append('-i')
        mux_chunks_process_args.append(''.join([app_settings.temp_directory,
                                                '/',
                                                encoding_task.output_file.name,
                                                encoding_task.output_file.extension]))
        mux_chunks_process_args.append('-i')
        mux_chunks_process_args.append(''.join([app_settings.temp_directory,
                                                '/',
                                                audio_task_chunk.output_file.name,
                                                audio_task_chunk.output_file.extension]))
        mux_chunks_process_args.append('-c')
        mux_chunks_process_args.append('copy')
        mux_chunks_process_args.append(encoding_task.output_file.file_path)

        return mux_chunks_process_args


class FFmpegArgs:
    """Class that contains functions to get a list of ffmpeg subprocess args for the given encoding task."""

    @staticmethod
    def get_args(encoding_task: Task, cli_args=False) -> list:
        """
        Returns a list of ffmpeg subprocess args for the given encoding task.

        Parameters:
            encoding_task: Encoding task to generate args from.
            cli_args: Boolean that represents whether to return arguments for the use of copy/paste into a terminal.

        Returns:
            A list of ffmpeg subprocess args using the given encoding task.
        """
        ffmpeg_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        FFmpegArgs._add_trim_start_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_nvdec_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_input_file_args(encoding_task, ffmpeg_args, cli_args)
        FFmpegArgs._add_stream_map_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_video_codec_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_audio_codec_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_filter_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_general_settings_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_trim_duration_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_vsync_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_output_file_args(encoding_task, ffmpeg_args, cli_args)

        return FFmpegArgs._add_2_pass_args(encoding_task, ffmpeg_args)

    @staticmethod
    def _add_trim_start_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the trim setting's args to the list of ffmpeg args.
        if encoding_task.trim:
            ffmpeg_args.append('-ss')
            ffmpeg_args.append(encoding_task.trim.ffmpeg_args['-ss'])

    @staticmethod
    def _add_nvdec_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the nvdec args to the list of ffmpeg args.
        if encoding_task.is_video_nvenc() and nvidia_helper.Compatibility.is_nvdec_supported():
            ffmpeg_args.extend(nvidia_helper.NVDEC_ARGS)
            ffmpeg_args.extend(nvidia_helper.NVDEC_OUT_FORMAT_ARGS)

    @staticmethod
    def _add_input_file_args(encoding_task: Task, ffmpeg_args: list, is_cli_args_enabled: bool):
        # Uses the given encoding task to add the input file args to the list of ffmpeg args.
        ffmpeg_args.append('-i')

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"', encoding_task.input_file.file_path, '\"']))
        else:
            ffmpeg_args.append(encoding_task.input_file.file_path)

    @staticmethod
    def _add_stream_map_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the stream mapping args to the list of ffmpeg args.
        FFmpegArgs._add_video_stream_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_audio_stream_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_subtitle_stream_args(encoding_task, ffmpeg_args)

    @staticmethod
    def _add_video_stream_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the video stream mapping args to the list of ffmpeg args.
        if encoding_task.video_stream is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(encoding_task.video_stream.index)]))

    @staticmethod
    def _add_audio_stream_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the audio stream mapping args to the list of ffmpeg args.
        for audio_stream, audio_codec in encoding_task.audio_streams.items():
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(audio_stream.index)]))

    @staticmethod
    def _add_subtitle_stream_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the subtitle stream mapping args to the list of ffmpeg args.
        for stream in encoding_task.filter.ffmpeg_args['-map']:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(stream)

    @staticmethod
    def _add_video_codec_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the video codec settings args to the list of ffmpeg args.
        if encoding_task.is_no_video:
            ffmpeg_args.append(ffmpeg_helper.VIDEO_NONE_ARG)
        elif encoding_task.video_codec:
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.video_codec.ffmpeg_args))
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.video_codec.get_ffmpeg_advanced_args()))
        else:
            ffmpeg_args.extend(ffmpeg_helper.VIDEO_COPY_ARGS)

    @staticmethod
    def _add_audio_codec_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the audio codec settings args to the list of ffmpeg args.
        if encoding_task.is_no_audio or encoding_task.is_video_2_pass():
            ffmpeg_args.append(ffmpeg_helper.AUDIO_NONE_ARG)
        else:
            FFmpegArgs._add_audio_streams_codec_args(encoding_task, ffmpeg_args)

    @staticmethod
    def _add_audio_streams_codec_args(encoding_task: Task, ffmpeg_args: list):
        # Adds the audio codec settings for each audio stream to the list of ffmpeg args.
        for audio_stream, audio_codec in encoding_task.audio_streams.items():
            if audio_codec is None:
                ffmpeg_args.append(''.join(['-c:a:', str(encoding_task.get_audio_stream_index(audio_stream))]))
                ffmpeg_args.append('copy')
            else:
                ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(audio_codec.ffmpeg_args))

    @staticmethod
    def _add_filter_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the filter args to the list of ffmpeg args.
        ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.filter.ffmpeg_args))

    @staticmethod
    def _add_general_settings_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the general settings args to the list of ffmpeg args.
        if encoding_task.video_codec:
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.general_settings.ffmpeg_args))

    @staticmethod
    def _add_trim_duration_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the trim duration args to the list of ffmpeg args.
        if encoding_task.trim:
            ffmpeg_args.append('-to')
            ffmpeg_args.append(encoding_task.trim.ffmpeg_args['-to'])

    @staticmethod
    def _add_vsync_args(encoding_task: Task, ffmpeg_args: list):
        # Adds the vsync args to the list of ffmpeg args for an encoding task chunk.
        if encoding_task.is_video_chunk:
            ffmpeg_args.extend(ffmpeg_helper.VSYNC_ARGS)

    @staticmethod
    def _add_output_file_args(encoding_task: Task, ffmpeg_args: list, is_cli_args_enabled: bool):
        # Uses the given encoding task to add the output file args to the list of ffmpeg args.
        if encoding_task.is_using_temp_output_file:
            output_file = encoding_task.temp_output_file
        else:
            output_file = encoding_task.output_file

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"', output_file.file_path, '\"']))
        else:
            ffmpeg_args.append(output_file.file_path)

    @staticmethod
    def _add_2_pass_args(encoding_task: Task, ffmpeg_args: list):
        # Uses the given encoding task to add the necessary settings for a 2-pass encode to the list of ffmpeg args.
        if encoding_task.is_video_2_pass() and encoding_task.video_codec.encode_pass == 1:
            encoding_task_copy = encoding_task.get_copy()
            encoding_task_copy.video_codec.encode_pass = 2

            return [ffmpeg_args, FFmpegArgs.get_args(encoding_task_copy)[0]]
        return [ffmpeg_args]

    @staticmethod
    def get_args_from_dict(ffmpeg_args: dict):
        """
        Takes a dictionary containing ffmpeg args and returns a list containing those args.

        Returns:
            List of ffmpeg args based on the given dictionary of ffmpeg args.
        """
        args = []

        for setting, arg in ffmpeg_args.items():
            if arg is None or setting == '-map':
                continue

            args.append(setting)
            args.append(arg)

        return args
