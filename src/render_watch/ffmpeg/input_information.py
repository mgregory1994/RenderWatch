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
import logging

from render_watch.app_formatting import format_converter
from render_watch.ffmpeg.settings import Settings


class InputInformation:
    """
    Gathers various information about an ffmpeg setting's input file.
    """

    VALID_SUBTITLE_CODECS = ['hdmv_pgs_subtitle']

    def __init__(self):
        self.width, self.height = None, None
        self.codec_type = None
        self.codec_name = None
        self.frame_rate = None
        self.duration = None
        self.sample_rate = None
        self.channels = None
        self.language = None
        self.index = None
        self.audio_done, self.video_done, self.duration_done = False, False, False
        self.video_streams = {}
        self.audio_streams = {}
        self.subtitle_streams = {}

    def reset_stream_information(self):
        self.width, self.height = None, None
        self.codec_type = None
        self.codec_name = None
        self.frame_rate = None
        self.duration = None
        self.sample_rate = None
        self.channels = None
        self.index = None

    def is_video_codec(self):
        return self.codec_type == 'video'

    def is_audio_codec(self):
        return self.codec_type == 'audio'

    def is_subtitle_codec(self):
        return self.codec_type == 'subtitle'

    @staticmethod
    def generate_input_information(ffmpeg):
        """
        Runs ffprobe to get information about ffmpeg setting's input file.

        :param ffmpeg: ffmpeg settings.
        """
        input_information = InputInformation()

        with subprocess.Popen(
                InputInformation._get_args(ffmpeg),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1) as process:
            while True:
                stdout = process.stdout.readline().strip()

                if stdout == '':
                    break

                InputInformation._process_input_information(stdout, ffmpeg, input_information)

        InputInformation._set_file_size_item(ffmpeg)
        InputInformation._set_processed_streams(ffmpeg, input_information)
        InputInformation._set_non_critical_input_information(ffmpeg)

        logging.info('--- INPUT FILE INFO ---\n' + str(ffmpeg.input_file_info))
        return InputInformation._is_information_valid(ffmpeg)

    @staticmethod
    def _get_args(ffmpeg):
        args = Settings.FFPROBE_ARGS.copy()
        args.append(ffmpeg.input_file)
        return args

    @staticmethod
    def _process_input_information(stdout, ffmpeg, input_information):
        if stdout == '[STREAM]':
            input_information.reset_stream_information()
        elif stdout == '[/STREAM]':
            InputInformation._add_stream_information_to_ffmpeg_settings(ffmpeg, input_information)
        elif stdout == '[/FORMAT]':
            ffmpeg.duration_origin = input_information.duration

        InputInformation._process_stream_information_item(stdout, input_information)

    @staticmethod
    def _add_stream_information_to_ffmpeg_settings(ffmpeg, input_information):
        try:
            if input_information.is_video_codec():
                InputInformation._add_video_stream_information_to_ffmpeg_settings(ffmpeg, input_information)
            elif input_information.is_audio_codec():
                InputInformation._add_audio_stream_information_to_ffmpeg_settings(ffmpeg, input_information)
            elif input_information.is_subtitle_codec():
                InputInformation._add_subtitle_stream_information_to_ffmpeg_settings(input_information)
        except:
            pass

    @staticmethod
    def _add_video_stream_information_to_ffmpeg_settings(ffmpeg, input_information):
        index = input_information.index
        codec_name = input_information.codec_name
        width = input_information.width
        height = input_information.height
        frame_rate = input_information.frame_rate
        stream_info = codec_name + ',' + str(width) + 'x' + str(height) + '(' + frame_rate + ')'
        input_information.video_streams[index] = {
            'codec_name': codec_name,
            'width': width,
            'height': height,
            'frame_rate': frame_rate,
            'info': stream_info
        }

        ffmpeg.codec_video_origin = codec_name
        ffmpeg.framerate_origin = frame_rate
        ffmpeg.width_origin = width
        ffmpeg.height_origin = height
        ffmpeg.resolution_origin = width, height

    @staticmethod
    def _add_audio_stream_information_to_ffmpeg_settings(ffmpeg, input_information):
        index = input_information.index
        codec_name = input_information.codec_name
        channels = input_information.channels
        sample_rate = input_information.sample_rate
        stream_info = codec_name + ',' + channels + ' channels,' + sample_rate + 'hz'
        input_information.audio_streams[index] = {
            'codec_name': codec_name,
            'channels': channels,
            'sample_rate': sample_rate,
            'info': stream_info
        }

        ffmpeg.codec_audio_origin = codec_name
        ffmpeg.audio_channels_origin = channels
        ffmpeg.audio_sample_rate_origin = sample_rate

    @staticmethod
    def _add_subtitle_stream_information_to_ffmpeg_settings(input_information):
        if input_information.codec_name in InputInformation.VALID_SUBTITLE_CODECS:
            index = input_information.index
            codec_name = input_information.codec_name
            language = input_information.language
            stream_info = '[' + index + ']' + language + ':' + codec_name
            input_information.subtitle_streams[index] = {
                'codec_name': codec_name,
                'language': language,
                'info': stream_info
            }

    @staticmethod
    def _process_stream_information_item(stdout, input_information):
        split_stdout = stdout.split('=')

        if InputInformation._set_index_item(split_stdout, input_information):
            return
        if InputInformation._set_codec_name_item(split_stdout, input_information):
            return
        if InputInformation._set_codec_type_item(split_stdout, input_information):
            return
        if InputInformation._set_width_item(split_stdout, input_information):
            return
        if InputInformation._set_height_item(split_stdout, input_information):
            return
        if InputInformation._set_frame_rate_item(split_stdout, input_information):
            return
        if InputInformation._set_channels_item(split_stdout, input_information):
            return
        if InputInformation._set_sample_rate_item(split_stdout, input_information):
            return
        if InputInformation._set_language_item(split_stdout, input_information):
            return
        if InputInformation._set_duration_item(split_stdout, input_information):
            return

    @staticmethod
    def _set_index_item(split_stdout, input_information):
        if 'index' in split_stdout:
            input_information.index = split_stdout[1]

    @staticmethod
    def _set_codec_name_item(split_stdout, input_information):
        if 'codec_name' in split_stdout:
            input_information.codec_name = split_stdout[1]

    @staticmethod
    def _set_codec_type_item(split_stdout, input_information):
        if 'codec_type' in split_stdout:
            input_information.codec_type = split_stdout[1]

    @staticmethod
    def _set_width_item(split_stdout, input_information):
        try:
            if 'width' in split_stdout:
                input_information.width = int(split_stdout[1])
        except ValueError:
            pass

    @staticmethod
    def _set_height_item(split_stdout, input_information):
        try:
            if 'height' in split_stdout:
                input_information.height = int(split_stdout[1])
        except ValueError:
            pass

    @staticmethod
    def _set_frame_rate_item(split_stdout, input_information):
        try:
            if 'r_frame_rate' in split_stdout:
                frame_rate_fraction = split_stdout[1].split('/')
                frame_rate_value = round(int(frame_rate_fraction[0]) / int(frame_rate_fraction[1]), 2)
                input_information.frame_rate = str(frame_rate_value)
        except ZeroDivisionError:
            pass

    @staticmethod
    def _set_channels_item(split_stdout, input_information):
        if 'channels' in split_stdout:
            input_information.channels = split_stdout[1]

    @staticmethod
    def _set_sample_rate_item(split_stdout, input_information):
        if 'sample_rate' in split_stdout:
            input_information.sample_rate = split_stdout[1]

    @staticmethod
    def _set_language_item(split_stdout, input_information):
        if 'TAG:language' in split_stdout:
            input_information.language = split_stdout[1]

    @staticmethod
    def _set_duration_item(split_stdout, input_information):
        try:
            if 'duration' in split_stdout:
                input_information.duration = int(split_stdout[1].split('.')[0])
        except ValueError:
            pass

    @staticmethod
    def _set_file_size_item(ffmpeg):
        filesize = os.path.getsize(ffmpeg.input_file)
        ffmpeg.file_size = format_converter.get_file_size_from_bytes(filesize)

    @staticmethod
    def _set_processed_streams(ffmpeg, input_information):
        ffmpeg.input_file_info['video_streams'] = input_information.video_streams
        ffmpeg.input_file_info['audio_streams'] = input_information.audio_streams
        ffmpeg.input_file_info['subtitle_streams'] = input_information.subtitle_streams

    @staticmethod
    def _set_non_critical_input_information(ffmpeg):
        if ffmpeg.codec_video_origin is None:
            ffmpeg.codec_video_origin = 'N/A'

        if ffmpeg.codec_audio_origin is None:
            ffmpeg.codec_audio_origin = 'N/A'

        if ffmpeg.audio_channels_origin is None:
            ffmpeg.audio_channels_origin = 'N/A'

        if ffmpeg.audio_sample_rate_origin is None:
            ffmpeg.audio_sample_rate_origin = 'N/A'

        if ffmpeg.folder_state:
            ffmpeg.width_origin = 'N/A'
            ffmpeg.height_origin = 'N/A'
            ffmpeg.duration_origin = 'N/A'
            ffmpeg.resolution_origin = 'N/A', 'N/A'
            ffmpeg.framerate_origin = 'N/A'

    @staticmethod
    def _is_information_valid(ffmpeg):
        if ffmpeg.width_origin is None or ffmpeg.height_origin is None:
            return False

        if ffmpeg.duration_origin is None:
            return False

        if ffmpeg.resolution_origin is None:
            return False

        if ffmpeg.framerate_origin is None:
            return False

        if ffmpeg.file_size == '0.0KB':
            return False

        return True
