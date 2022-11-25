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


import subprocess
import re
import os

from datetime import datetime
from pathlib import Path

from render_watch.ffmpeg import stream
from render_watch.helpers import format_converter
from render_watch import app_preferences


VALID_EXTENSIONS = ('.mp4',
                    '.m4v',
                    '.mov',
                    '.mkv',
                    '.ts',
                    '.m2ts',
                    '.mpg',
                    '.webm',
                    '.wmv',
                    '.vob',
                    '.avi',
                    '.aac',
                    '.wav',
                    '.flac',
                    '.mp3')
MP4_EXTENTION = '.mp4'
MKV_EXTENSION = '.mkv'
TS_EXTENSION = '.ts'
WEBM_EXTENSION = '.webm'
M4A_EXTENSION = '.m4a'
AAC_EXTENSION = '.aac'
OGG_EXTENSION = '.ogg'
VIDEO_OUTPUT_EXTENSIONS = [MP4_EXTENTION, MKV_EXTENSION, TS_EXTENSION, WEBM_EXTENSION]
AUDIO_OUTPUT_EXTENSIONS = [M4A_EXTENSION, AAC_EXTENSION, OGG_EXTENSION]
OUTPUT_EXTENSIONS = VIDEO_OUTPUT_EXTENSIONS.copy()
OUTPUT_EXTENSIONS.extend(AUDIO_OUTPUT_EXTENSIONS)
VALID_FAST_START_EXTENSION = '.mp4'

VALID_SUBTITLE_CODECS = ('hdmv_pgs_subtitle',)

FFPROBE_ARGS = [
    'ffprobe',
    '-hide_banner',
    '-loglevel',
    'warning',
    '-show_entries',
    'stream=codec_name,codec_type,width,height,r_frame_rate,bit_rate,channels,sample_rate,index:stream_tags=language:format=duration'
]

ALIAS_COUNTER = -1


class InputFile:
    """Class that generates all the necessary information for the given input file."""

    def __init__(self, input_file_path: str):
        """
        Initializes the InputFile class with all the necessary variables for the information of the given input file.
        """
        self.file_path = input_file_path
        self.dir = os.path.dirname(input_file_path)
        self.name = Path(input_file_path).resolve().stem
        self.size = None
        self.duration = None
        self.extension = Path(input_file_path).resolve().suffix
        self.video_streams = []
        self.audio_streams = []
        self.subtitle_streams = []
        self.is_folder = os.path.isdir(input_file_path)
        self.is_recursively_searching_folder = False
        self.is_video = False
        self.is_audio = False

        if self.is_folder:
            self._setup_folder_streams()
        else:
            _InputInformation(self)

    def _setup_folder_streams(self):
        self.video_streams.append(self._get_folder_video_stream())
        self.audio_streams.append(self._get_folder_audio_stream())

    @staticmethod
    def _get_folder_video_stream() -> stream.VideoStream:
        video_stream = stream.VideoStream()
        video_stream.index = 0
        video_stream.codec_name = 'N/A'
        video_stream.width = 'N/A'
        video_stream.height = 'N/A'

        return video_stream

    @staticmethod
    def _get_folder_audio_stream() -> stream.AudioStream:
        audio_stream = stream.AudioStream()
        audio_stream.index = 0
        audio_stream.codec_name = 'N/A'

        return audio_stream

    def is_valid(self) -> bool:
        """
        Returns whether the input file information is usable for the rest of the application or if the input folder
        is accessible.

        Returns:
            Boolean that represents whether the input file's information is valid.
        """
        if self.is_folder:
            return os.access(self.file_path, os.R_OK)

        if not (self.is_video or self.is_audio):
            return False

        if self.duration is None or self.size is None:
            return False
        return True

    def get_initial_video_stream(self) -> stream.VideoStream | None:
        if self.is_video or self.is_folder:
            return self.video_streams[0]
        return None

    def get_initial_audio_stream(self) -> stream.AudioStream | None:
        if self.is_audio or self.is_folder:
            return self.audio_streams[0]
        return None


class _InputInformation:
    """Class that generates the necessary information about an input file."""

    IMAGE_CODECS = ('mjpeg',)

    def __init__(self, input_file: InputFile):
        """
        Initializes the _InputInformation class with all the necessary variables for generating the information for an
        input file.
        """
        self.input_file = input_file
        self.stream_info = ''

        self.process_streams()
        self.set_input_file_info()

    def process_streams(self):
        """
        Runs a subprocess of FFprobe to gather information about the input file's video/audio/subtitle streams.

        Returns:
            None
        """
        with subprocess.Popen(self._get_ffprobe_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as process:
            while True:
                stdout = process.stdout.readline().strip()

                if stdout == '' and process.poll() is not None:
                    break

                if stdout == '[STREAM]' or stdout == '[FORMAT]':
                    self.stream_info = ''

                if stdout == '[/STREAM]':
                    self.process_stream_info()

                if stdout == '[/FORMAT]':
                    self.process_duration()

                self.stream_info = ' '.join([self.stream_info, stdout])

    def _get_ffprobe_args(self) -> list:
        # Generates and returns the FFprobe process arguments.
        args = FFPROBE_ARGS.copy()
        args.append(self.input_file.file_path)

        return args

    def process_stream_info(self):
        """
        Parses the stream info from stdout in order to get the information from FFprobe.

        Uses the re module for parsing strings from stdout.

        Returns:
            None
        """
        codec_type = re.search(r'codec_type=\w+', self.stream_info).group().split('=')[1]

        if codec_type == 'video':
            self.process_video_stream()
        elif codec_type == 'audio':
            self.process_audio_stream()
        elif codec_type == 'subtitle':
            self.process_subtitle_stream()

    def process_video_stream(self):
        """
        Parses the video stream info. from stdout in order to get the information from FFprobe.

        Uses the re module for parsing strings from stdout.

        Returns:
            None
        """
        video_stream = stream.VideoStream()
        video_stream.index = self.get_index_from_stream_info()
        video_stream.codec_name = self.get_codec_name_from_stream_info()
        video_stream.language = self.get_language_from_stream_info()
        video_stream.width = self.get_width_from_stream_info()
        video_stream.height = self.get_height_from_stream_info()
        video_stream.frame_rate = self.get_frame_rate_from_stream_info()
        video_stream.bitrate = self.get_bitrate_from_stream_info()

        self.add_video_stream(video_stream)

    def add_video_stream(self, video_stream: stream.VideoStream):
        """
        Checks to see if enough information was collected about the video stream and adds it to the list of
        video streams.

        Returns:
            None
        """
        if video_stream.index is None:
            return

        if video_stream.codec_name is None:
            return
        elif video_stream.codec_name in self.IMAGE_CODECS:
            return

        if video_stream.width is None or video_stream.height is None:
            return

        self.input_file.video_streams.append(video_stream)

    def process_audio_stream(self):
        """
        Parses the audio stream info. from stdout in order to get the information from FFprobe.

        Uses the re module for parsing strings from stdout.

        Returns:
            None
        """
        audio_stream = stream.AudioStream()
        audio_stream.index = self.get_index_from_stream_info()
        audio_stream.codec_name = self.get_codec_name_from_stream_info()
        audio_stream.language = self.get_language_from_stream_info()
        audio_stream.sample_rate = self.get_sample_rate_from_stream_info()
        audio_stream.channels = self.get_channels_from_stream_info()
        audio_stream.bitrate = self.get_bitrate_from_stream_info()

        self.add_audio_stream(audio_stream)

    def add_audio_stream(self, audio_stream: stream.AudioStream):
        """
        Checks to see if enough information was collected about the audio stream and adds it to the list of
        audio streams.

        Returns:
            None
        """
        if audio_stream.index is None:
            return

        if audio_stream.codec_name is None:
            return

        self.input_file.audio_streams.append(audio_stream)

    def process_subtitle_stream(self):
        """
        Parses the subtitle stream info. from stdout in order to get the information from FFprobe.

        Uses the re module for parsing strings from stdout.

        Returns:
            None
        """
        subtitle_stream = stream.SubtitleStream()
        subtitle_stream.index = self.get_index_from_stream_info()
        subtitle_stream.codec_name = self.get_codec_name_from_stream_info()
        subtitle_stream.language = self.get_language_from_stream_info()

        self.add_subtitle_stream(subtitle_stream)

    def add_subtitle_stream(self, subtitle_stream: stream.SubtitleStream):
        """
        Checks to see if enough information was collected about the subtitle stream and adds it to the list of
        subtitle streams.

        Returns:
            None
        """
        if subtitle_stream.index is None:
            return

        if subtitle_stream.codec_name is None or subtitle_stream.codec_name not in VALID_SUBTITLE_CODECS:
            return

        self.input_file.subtitle_streams.append(subtitle_stream)

    def get_index_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the index from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            index = re.search(r'index=\w+', self.stream_info).group().split('=')[1]

            return int(index)
        except:
            return None

    def get_codec_name_from_stream_info(self) -> str | None:
        """
        Uses regex to parse the codec name from FFprobe's stdout.

        Returns:
            String or None if no value.
        """
        try:
            return re.search(r'codec_name=\w+', self.stream_info).group().split('=')[1]
        except:
            return None

    def get_language_from_stream_info(self) -> str | None:
        """
        Uses regex to parse the language from FFprobe's stdout.

        Returns:
            String or None if no value.
        """
        try:
            return re.search(r'TAG:language=\w+', self.stream_info).group().split('=')[1]
        except:
            return None

    def get_width_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the width from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            width = re.search(r'width=\d+', self.stream_info).group().split('=')[1]

            return int(width)
        except:
            return None

    def get_height_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the height from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            height = re.search(r'height=\d+', self.stream_info).group().split('=')[1]

            return int(height)
        except:
            return None

    def get_frame_rate_from_stream_info(self) -> float | None:
        """
        Uses regex to parse the frame rate from FFprobe's stdout.

        Returns:
            Float or None if no value.
        """
        try:
            frame_rate = re.search(r'r_frame_rate=\d+/\d+', self.stream_info).group().split('=')[1]
            dividend = frame_rate.split('/')[0]
            divisor = frame_rate.split('/')[1]

            return float(dividend) / float(divisor)
        except:
            return None

    def get_bitrate_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the bitrate from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            bitrate = re.search(r'bit_rate=\d+', self.stream_info).group().split('=')[1]

            return int(bitrate)
        except:
            return None

    def get_sample_rate_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the sample rate from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            sample_rate = re.search(r'sample_rate=\d+', self.stream_info).group().split('=')[1]

            return int(sample_rate)
        except:
            return None

    def get_channels_from_stream_info(self) -> int | None:
        """
        Uses regex to parse the channels from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            channels = re.search(r'channels=\d+', self.stream_info).group().split('=')[1]

            return int(channels)
        except:
            return None

    def process_duration(self):
        """
        Uses regex to parse the duration from FFprobe's stdout.

        Returns:
            Int or None if no value.
        """
        try:
            duration = re.search(r'duration=\d+\.\d+', self.stream_info).group().split('=')[1]
            duration_in_seconds = round(float(duration), 1)

            if duration:
                self.input_file.duration = duration_in_seconds
        except:
            self.input_file.duration = None

    def set_input_file_info(self):
        """
        Sets information about the file's size and whether it's a video or audio file.

        Returns:
            None
        """
        self.set_file_size()
        self.set_input_file_type()

    def set_file_size(self):
        """
        Takes the input file's size and sets the input's information as a string representing the file size.

        Returns:
            None
        """
        file_size_in_bytes = os.path.getsize(self.input_file.file_path)
        self.input_file.size = format_converter.get_file_size_from_bytes(file_size_in_bytes)

    def set_input_file_type(self):
        """
        Checks if the video and audio stream lists are populated and sets the input information as a video or
        audio file.

        Returns:
            None
        """
        self.input_file.is_video = bool(self.input_file.video_streams)
        self.input_file.is_audio = bool(self.input_file.audio_streams)


class OutputFile:
    """Class that configures all the necessary information for the output file."""

    def __init__(self, input_file: InputFile, app_settings: app_preferences.Settings):
        """
        Initializes the OutputFile class with all the necessary variables for the information of the output file.
        """
        self.input_file = input_file
        self._dir = app_settings.output_directory
        self.name = input_file.name
        self._file_size = None
        self._average_bitrate = None
        self._average_bitrate_counter = 0

        if input_file.is_video or input_file.is_folder:
            self._extension = MP4_EXTENTION
        else:
            self._extension = M4A_EXTENSION

    @property
    def extension(self) -> str:
        """
        Returns the extension of the output file.

        Returns:
            String that represents the output file's extension.
        """
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        """
        Sets the output file's extension.

        Parameters:
            extension_value: Extension as a string.

        Returns:
            None
        """
        if extension_value is None:
            return

        self._extension = extension_value

    @property
    def dir(self) -> str:
        """
        Returns the directory path that contains the output file.

        Returns:
            String that represents the output file's directory path.
        """
        return self._dir

    @dir.setter
    def dir(self, dir_path: str | None):
        """
        Sets the directory path for the output file.

        Parameters:
            dir_path: Output file's directory path as a string.

        Returns:
            None
        """
        if dir_path is None:
            return

        self._dir = dir_path

    @property
    def file_path(self):
        """
        Returns the complete file path for the output file.

        Returns:
            Output file path as a string.
        """
        if self.input_file.is_folder:
            return self.dir
        return ''.join([self.dir, '/', self.name, self.extension])

    @property
    def file_size(self) -> int:
        return self._file_size

    @property
    def average_bitrate(self) -> float:
        return self._average_bitrate

    def add_file_size(self, new_file_size: int):
        if self._file_size:
            self._file_size += new_file_size

    def add_average_bitrate(self, new_bitrate_average: float):
        self._average_bitrate_counter += 1
        self._average_bitrate += new_bitrate_average
        self._average_bitrate /= self._average_bitrate_counter

    def get_name_and_extension(self):
        if self.input_file.is_folder:
            return self.name
        return ''.join([self.name, self.extension])


class TempFile:
    """Class that configures the necessary information for the temporary output file."""

    def __init__(self, input_file: InputFile, temp_output_file_dir: str):
        """
        Initializes the TempOutputFile class with all the necessary variables for the information of the
        temporary output file.
        """
        self._dir = temp_output_file_dir
        self.name = AliasGenerator.generate_alias_from_name(input_file.name)
        self._extension = '.mp4'

    @property
    def dir(self) -> str:
        """
        Returns the directory path that contains the temporary output file.

        Returns:
            String that represents the temporary output file's directory path.
        """
        return self._dir

    @dir.setter
    def dir(self, dir_path: str):
        """
        Sets the directory path for the temporary output file.

        Parameters:
            dir_path: Temporary output file's directory path as a string.

        Returns:
            None
        """
        if dir_path is None:
            return

        self._dir = dir_path

    @property
    def extension(self) -> str:
        """
        Returns the extension of the temporary output file.

        Returns:
            String that represents the temporary output file's extension.
        """
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        """
        Sets the temporary output file's extension.

        Parameters:
            extension_value: Extension as a string.

        Returns:
            None
        """
        if extension_value is None:
            return

        self._extension = extension_value

    @property
    def file_path(self):
        """
        Returns the complete file path for the temporary output file.

        Returns:
            Temporary output file path as a string.
        """
        return ''.join([self.dir, '/', self.name, self.extension])


class AliasGenerator:
    """Class that contains functions for generating a name alias."""

    global ALIAS_COUNTER

    @staticmethod
    def generate_alias_from_name(name: str) -> str:
        """
        Creates a unique alias based off of the first character of the given name.

        Parameters:
            name: Name to generate a unique alias from.

        Returns:
            Unique alias as a string.
        """
        global ALIAS_COUNTER
        ALIAS_COUNTER += 1

        current_date_time = datetime.now().strftime('_%m-%d-%Y_%H%M%S')

        return name[0] + str(ALIAS_COUNTER) + current_date_time
