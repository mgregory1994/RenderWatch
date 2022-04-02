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

from render_watch import app_preferences
from render_watch.ffmpeg import input, output
from render_watch.ffmpeg import trim
from render_watch.ffmpeg import filters
from render_watch.ffmpeg import h264_nvenc, hevc_nvenc, x264, x265, vp9
from render_watch.helpers import ffmpeg_helper, nvidia_helper


MIN_CHUNK_LENGTH_SECONDS = 10


class Task:
    def __init__(self, input_file_path: str, app_settings: app_preferences.Settings, video_chunk=False):
        self.app_settings = app_settings
        self.input_file = input.InputFile(input_file_path)
        self.output_file = output.OutputFile(self.input_file, self.app_settings)
        self.temp_output_file = output.TempOutputFile(self.input_file, self.app_settings.temp_directory)
        self.general_settings = None
        self.video_stream = None
        self.video_codec = None
        self.audio_streams = {}
        self.trim = None
        self.filter = filters.Filter(self.input_file)
        self._bitrate = None
        self._file_size = None
        self._speed = None
        self._time_left = None
        self._bitrate_lock = threading.Lock()
        self._file_size_lock = threading.Lock()
        self._speed_lock = threading.Lock()
        self._time_left_lock = threading.Lock()
        self._task_thread_lock = threading.Lock()
        self.is_video_chunk = video_chunk
        self.is_no_video = False
        self.is_no_audio = False
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

    def add_audio_stream(self, audio_stream: input.AudioStream):
        self.audio_streams[audio_stream] = None

    def remove_audio_stream(self, audio_stream: input.AudioStream):
        self.audio_streams.pop(audio_stream, 0)

    def set_audio_stream_codec(self, audio_stream: input.AudioStream, audio_codec):
        if audio_stream in self.audio_streams:
            self.audio_streams[audio_stream] = audio_codec

    def get_audio_stream_codec(self, audio_stream: input.AudioStream):
        if audio_stream in self.audio_streams:
            return self.audio_streams[audio_stream]
        return None

    def get_audio_stream_index(self, audio_stream: input.AudioStream) -> int | None:
        if audio_stream in self.audio_streams:
            audio_streams_list = list(self.audio_streams)

            return audio_streams_list.index(audio_stream)
        return None

    def is_video_copy(self) -> bool:
        return self.video_codec is None

    def is_audio_copy(self) -> bool:
        for audio_stream, audio_codec in self.audio_streams.items():
            if audio_codec is None:
                return True
        return False

    def is_video_h264_nvenc(self) -> bool:
        return isinstance(self.video_codec, h264_nvenc.H264Nvenc)

    def is_video_hevc_nvenc(self) -> bool:
        return isinstance(self.video_codec, hevc_nvenc.HevcNvenc)

    def is_video_nvenc(self) -> bool:
        return self.is_video_hevc_nvenc() or self.is_video_h264_nvenc()

    def is_video_x264(self) -> bool:
        return isinstance(self.video_codec, x264.X264)

    def is_video_x265(self) -> bool:
        return isinstance(self.video_codec, x265.X265)

    def is_video_vp9(self) -> bool:
        return isinstance(self.video_codec, vp9.VP9)

    def is_video_2_pass(self):
        if self.video_codec:
            return self.video_codec.encode_pass == 1
        return False

    def is_nvenc_codec_settings_valid(self) -> bool:
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
        task_copy = Task(self.input_file.file_path, self.app_settings, self.is_video_chunk)

        try:
            task_copy.video_stream = self.video_stream
            task_copy.audio_streams = self.audio_streams
            task_copy.is_no_audio = self.is_no_audio
            task_copy.filter = copy.deepcopy(self.filter)
            task_copy.audio_streams = copy.deepcopy(self.audio_streams)

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


class Parallel:
    @staticmethod
    def get_task_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> tuple | None:
        number_of_chunks = Parallel._get_number_of_chunks(encoding_task, app_settings)

        if Parallel._is_task_chunkable(encoding_task, number_of_chunks):
            return Parallel._get_task_chunks_tuple(encoding_task, number_of_chunks)
        return None

    @staticmethod
    def _get_number_of_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> int:
        if encoding_task.is_video_nvenc():
            return nvidia_helper.Parallel.nvenc_max_workers
        return Parallel._get_per_codec_number_of_chunks(encoding_task, app_settings)

    @staticmethod
    def _get_per_codec_number_of_chunks(encoding_task: Task, app_settings: app_preferences.Settings) -> int:
        if encoding_task.is_video_x264():
            return app_settings.per_codec_parallel_tasks['x264']

        if encoding_task.is_video_x265():
            return app_settings.per_codec_parallel_tasks['x265']

        if encoding_task.is_video_vp9():
            return app_settings.per_codec_parallel_tasks['vp9']
        return 1

    @staticmethod
    def _is_task_chunkable(encoding_task: Task, number_of_chunks: int) -> bool:
        if encoding_task.is_video_copy() or encoding_task.is_no_video:
            return False

        if encoding_task.trim and not encoding_task.is_audio_copy():
            if (encoding_task.trim.trim_duration / number_of_chunks) >= MIN_CHUNK_LENGTH_SECONDS:
                return True
        elif (encoding_task.input_file.duration / number_of_chunks) >= MIN_CHUNK_LENGTH_SECONDS:
            return True
        return False

    @staticmethod
    def _get_task_chunks_tuple(encoding_task: Task, number_of_chunks: int) -> tuple:
        task_chunks = []

        for index in range(1, (number_of_chunks + 1)):
            task_chunks.append(Parallel._get_video_task_chunk(encoding_task, number_of_chunks, index))
        task_chunks.append(Parallel._get_audio_task_chunk(encoding_task))

        return tuple(task_chunks)

    @staticmethod
    def _get_video_task_chunk(encoding_task: Task, number_of_chunks: int, index: int) -> Task:
        video_task_chunk = encoding_task.get_copy()
        video_task_chunk.trim = Parallel._get_video_task_trim_settings(encoding_task, number_of_chunks, index)

        if video_task_chunk.is_video_2_pass():
            video_task_chunk.video_codec.stats = ''.join([video_task_chunk.temp_output_file.dir,
                                                          '/',
                                                          video_task_chunk.temp_output_file.name,
                                                          '.log'])

        video_task_chunk.is_no_audio = True
        video_task_chunk.is_video_chunk = True
        video_task_chunk.temp_output_file.name = ''.join([video_task_chunk.temp_output_file.name,
                                                          '_',
                                                          str(index)])

        if video_task_chunk.is_video_vp9():
            video_task_chunk.temp_output_file.extension = '.webm'
        else:
            video_task_chunk.temp_output_file.extension = '.mp4'

        return video_task_chunk

    @staticmethod
    def _get_video_task_trim_settings(encoding_task: Task, number_of_chunks: int, index: int) -> trim.TrimSettings:
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
        audio_task_chunk = encoding_task.get_copy()
        audio_task_chunk.is_no_video = True
        audio_task_chunk.temp_output_file.extension = '.mkv'
        audio_task_chunk.temp_output_file.name = audio_task_chunk.temp_output_file.name + '_audio'

        return audio_task_chunk

    @staticmethod
    def concatenate_video_task_chunks(task_chunks: tuple, encoding_task: Task):
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
        try:
            with open(chunk_list_file_path, 'w') as concatenation_file:
                concatenation_file.writelines(concatenation_args)

            return True
        except OSError:
            logging.error(''.join(['--- FAILED TO CONCAT VIDEO CHUNKS: ',
                                   encoding_task.input_file.name,
                                   ' ---']))

            return False

    @staticmethod
    def _get_concatenation_process_args(encoding_task: Task, chunk_list_file_path: str) -> list:
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

                stdout_log = ''.join([stdout_log,
                                     stdout,
                                     '\n'])

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
        mux_chunks_process_args = Parallel._get_mux_chunks_process_args(task_chunks, encoding_task, app_settings)
        Parallel._run_process_args(encoding_task, mux_chunks_process_args)

    @staticmethod
    def _get_mux_chunks_process_args(task_chunks: tuple,
                                     encoding_task: Task,
                                     app_settings: app_preferences.Settings) -> list:
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
    @staticmethod
    def get_args(encoding_task: Task, cli_args=False):
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
        FFmpegArgs._add_output_file_args(encoding_task, ffmpeg_args, cli_args)
        FFmpegArgs._add_2_pass_args(encoding_task, ffmpeg_args)

        return ffmpeg_args

    @staticmethod
    def _add_trim_start_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.trim:
            ffmpeg_args.append('-ss')
            ffmpeg_args.append(encoding_task.trim.ffmpeg_args['-ss'])

    @staticmethod
    def _add_nvdec_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.is_video_nvenc() and nvidia_helper.Compatibility.is_nvdec_supported():
            ffmpeg_args.extend(nvidia_helper.NVDEC_ARGS)
            ffmpeg_args.extend(nvidia_helper.NVDEC_OUT_FORMAT_ARGS)

    @staticmethod
    def _add_input_file_args(encoding_task: Task, ffmpeg_args: list, is_cli_args_enabled: bool):
        ffmpeg_args.append('-i')

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"',
                                        encoding_task.input_file.file_path,
                                        '\"']))
        else:
            ffmpeg_args.append(encoding_task.input_file.file_path)

    @staticmethod
    def _add_stream_map_args(encoding_task: Task, ffmpeg_args: list):
        FFmpegArgs._add_video_stream_args(encoding_task, ffmpeg_args)
        FFmpegArgs._add_audio_stream_args(encoding_task, ffmpeg_args)

    @staticmethod
    def _add_video_stream_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.video_stream is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(encoding_task.video_stream.index)]))

    @staticmethod
    def _add_audio_stream_args(encoding_task: Task, ffmpeg_args: list):
        for audio_stream, audio_codec in encoding_task.audio_streams.items():
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(audio_stream.index)]))

    @staticmethod
    def _add_subtitle_stream_args(encoding_task: Task, ffmpeg_args: list):
        for stream in encoding_task.filter.ffmpeg_args['-map']:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(stream)

    @staticmethod
    def _add_video_codec_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.is_no_video:
            ffmpeg_args.append(ffmpeg_helper.VIDEO_NONE_ARG)
        elif encoding_task.video_codec:
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.video_codec.ffmpeg_args))
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.video_codec.get_ffmpeg_advanced_args()))
        else:
            ffmpeg_args.extend(ffmpeg_helper.VIDEO_COPY_ARGS)

    @staticmethod
    def _add_audio_codec_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.is_no_audio or encoding_task.is_video_2_pass():
            ffmpeg_args.append(ffmpeg_helper.AUDIO_NONE_ARG)
        else:
            FFmpegArgs._add_audio_streams_codec_args(encoding_task, ffmpeg_args)

    @staticmethod
    def _add_audio_streams_codec_args(encoding_task: Task, ffmpeg_args: list):
        for audio_stream, audio_codec in encoding_task.audio_streams.items():
            if audio_codec is None:
                ffmpeg_args.append(''.join(['-c:a:', str(encoding_task.get_audio_stream_index(audio_stream))]))
                ffmpeg_args.append('copy')
            else:
                ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(audio_codec.ffmpeg_args))

    @staticmethod
    def _add_filter_args(encoding_task: Task, ffmpeg_args: list):
        ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.filter.ffmpeg_args))

    @staticmethod
    def _add_general_settings_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.general_settings and encoding_task.video_codec:
            ffmpeg_args.extend(FFmpegArgs.get_args_from_dict(encoding_task.general_settings.ffmpeg_args))

    @staticmethod
    def _add_trim_duration_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.trim:
            ffmpeg_args.append('-to')
            ffmpeg_args.append(encoding_task.trim.ffmpeg_args['-to'])

    @staticmethod
    def _add_output_file_args(encoding_task: Task, ffmpeg_args: list, is_cli_args_enabled: bool):
        FFmpegArgs._add_vsync_args(encoding_task, ffmpeg_args)

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"',
                                        encoding_task.output_file.file_path,
                                        '\"']))
        else:
            ffmpeg_args.append(encoding_task.output_file.file_path)

    @staticmethod
    def _add_vsync_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.is_video_chunk:
            ffmpeg_args.extend(ffmpeg_helper.VSYNC_ARGS)

    @staticmethod
    def _add_2_pass_args(encoding_task: Task, ffmpeg_args: list):
        if encoding_task.is_video_2_pass():
            encoding_task_copy = encoding_task.get_copy()
            encoding_task_copy.video_codec.encode_pass = 2

            ffmpeg_args.append('&&')
            ffmpeg_args.extend(FFmpegArgs.get_args(encoding_task_copy))

    @staticmethod
    def get_args_from_dict(ffmpeg_args: dict):
        args = []

        for setting, arg in ffmpeg_args.items():
            if arg is None or setting == '-map':
                continue

            args.append(setting)
            args.append(arg)

        return args
