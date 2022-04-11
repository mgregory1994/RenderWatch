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

from pathlib import Path

from render_watch.helpers import format_converter


VALID_EXTENSIONS = ('mp4',
                    'm4v',
                    'mov',
                    'mkv',
                    'ts',
                    'm2ts',
                    'mpg',
                    'webm',
                    'wmv',
                    'vob',
                    'avi',
                    'aac',
                    'wav',
                    'flac',
                    'mp3')
VALID_SUBTITLE_CODECS = ('hdmv_pgs_subtitle',)

FFPROBE_ARGS = [
    'ffprobe',
    '-hide_banner',
    '-loglevel',
    'warning',
    '-show_entries',
    'stream=codec_name,codec_type,width,height,r_frame_rate,bit_rate,channels,sample_rate,index:stream_tags=language:format=duration'
]


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

        if not self.is_folder:
            _InputInformation(self)

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


class VideoStream:
    """Class that configures the necessary information for the video stream of a video file."""

    def __init__(self):
        """
        Initializes the VideoStream class with all the necessary variables for the information of a video stream.
        """
        self.index = None
        self.codec_name = None
        self.width = None
        self.height = None
        self._frame_rate = None
        self._bitrate = None
        self._language = None

    @property
    def frame_rate(self) -> float | str:
        """
        Returns the frame rate of the video stream.

        Returns:
            Frame rate as a float or a string that represents no value.
        """
        if self._frame_rate is None:
            return 'N/A'
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, frame_rate_value: float | None):
        """
        Sets the frame rate value of the video stream.

        Parameters:
            frame_rate_value: The frame rate value as a float.

        Returns:
            None
        """
        self._frame_rate = float(('%.3f' % frame_rate_value).rstrip('0').rstrip('.'))

    @property
    def bitrate(self) -> int | str:
        """
        Returns the bitrate of the video stream.

        Returns:
            Bitrate as an int or a string that represents no value.
        """
        if self._bitrate is None:
            return 'N/A'
        return self._bitrate

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate value of the video stream.

        Parameters:
            bitrate_value: The bitrate value as an int.

        Returns:
            None
        """
        self._bitrate = bitrate_value

    @property
    def language(self) -> str:
        """
        Returns the language of the video stream.

        Returns:
            String that represents the language.
        """
        if self._language is None:
            return 'N/A'
        return self._language

    @language.setter
    def language(self, language_value: str | None):
        """
        Sets the language of the video stream.

        Parameters:
            language_value: String that represents the language.

        Returns:
            None
        """
        self._language = language_value

    def get_info(self) -> str:
        """
        Returns the video stream's information as a string.

        Returns:
            String that represents the video stream's information.
        """
        return ''.join(['[',
                        str(self.index),
                        ',',
                        self.language,
                        ']',
                        self.codec_name,
                        '(',
                        str(self.width),
                        'x',
                        str(self.height),
                        ',',
                        str(self.frame_rate),
                        ')'])


class AudioStream:
    """Class that configures the necessary information for the audio stream of a video/audio file."""

    def __init__(self):
        """
        Initializes the AudioStream class with all the necessary variables for the information of an audio stream.
        """
        self.index = None
        self.codec_name = None
        self._sample_rate = None
        self._channels = None
        self._bitrate = None
        self._language = None

    @property
    def sample_rate(self) -> int | str:
        """
        Returns the sample rate of the audio stream.

        Returns:
            Sample rate as an int or a string that represents no value.
        """
        if self._sample_rate is None:
            return 'N/A'
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, sample_rate_value: int | None):
        """
        Sets the frame rate value of the audio stream.

        Parameters:
            sample_rate_value: Sample rate value as an int.

        Returns:
            None
        """
        self._sample_rate = sample_rate_value

    @property
    def channels(self) -> int | str:
        """
        Returns the channels of the audio stream.

        Returns:
            Channels as an int or a string that represents no value.
        """
        if self._channels is None:
            return 'N/A'
        return self._channels

    @channels.setter
    def channels(self, channels_value: int | None):
        """
        Sets the channels value of the audio stream.

        Parameters:
            channels_value: The channels value as an int.

        Returns:
            None
        """
        self._channels = channels_value

    @property
    def bitrate(self) -> int | str:
        """
        Returns the bitrate of the audio stream.

        Returns:
            Bitrate as an int or a string that represents no value.
        """
        if self._bitrate is None:
            return 'N/A'
        return self._bitrate

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate value of the audio stream.

        Parameters:
            bitrate_value: The bitrate value as an int.

        Returns:
            None
        """
        self._bitrate = bitrate_value

    @property
    def language(self) -> str:
        """
        Returns the langauge of the audio stream as a string.

        Returns:
            A string that represents the language.
        """
        if self._language is None:
            return 'N/A'
        return self._language

    @language.setter
    def language(self, language_value: str | None):
        """
        Sets the language of the audio stream.

        Parameters:
            language_value: A string that represents the language.

        Returns:
            None
        """
        self._language = language_value

    def get_info(self) -> str:
        """
        Returns the audio stream's information as a string.

        Returns:
            String that represents the audio stream's information.
        """
        return ''.join(['[',
                        str(self.index),
                        ',',
                        self.language,
                        ']',
                        self.codec_name,
                        '(',
                        str(self.channels),
                        ' channels,',
                        str(self.sample_rate),
                        'hz)'])


class SubtitleStream:
    """Class that configures the necessary information for the subtitle stream of a video file."""

    def __init__(self):
        """
        Initializes the SubtitleStream class with all the necessary variables for the information of a subtitle stream.
        """
        self.index = None
        self.codec_name = None
        self._language = None

    @property
    def language(self) -> str:
        """
        Returns the language of the subtitle stream.

        Returns:
            String that represents the language.
        """
        if self._language is None:
            return 'N/A'
        return self._language

    @language.setter
    def language(self, language_value: str | None):
        """
        Sets the language of the subtitle stream.

        Parameters:
            language_value: String that represents the language.

        Returns:
            None
        """
        self._language = language_value

    def get_info(self) -> str:
        """
        Returns the subtitle stream's information as a string.

        Returns:
            String that represents the subtitles stream's information.
        """
        return ''.join(['[', str(self.index), ',', self.language, ']', self.codec_name])


class _InputInformation:
    """Class that generates the necessary information about an input file."""

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
        args = FFPROBE_ARGS
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
        video_stream = VideoStream()
        video_stream.index = self.get_index_from_stream_info()
        video_stream.codec_name = self.get_codec_name_from_stream_info()
        video_stream.language = self.get_language_from_stream_info()
        video_stream.width = self.get_width_from_stream_info()
        video_stream.height = self.get_height_from_stream_info()
        video_stream.frame_rate = self.get_frame_rate_from_stream_info()
        video_stream.bitrate = self.get_bitrate_from_stream_info()

        self.add_video_stream(video_stream)

    def add_video_stream(self, video_stream: VideoStream):
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
        audio_stream = AudioStream()
        audio_stream.index = self.get_index_from_stream_info()
        audio_stream.codec_name = self.get_codec_name_from_stream_info()
        audio_stream.language = self.get_language_from_stream_info()
        audio_stream.sample_rate = self.get_sample_rate_from_stream_info()
        audio_stream.channels = self.get_channels_from_stream_info()
        audio_stream.bitrate = self.get_bitrate_from_stream_info()

        self.add_audio_stream(audio_stream)

    def add_audio_stream(self, audio_stream: AudioStream):
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
        subtitle_stream = SubtitleStream()
        subtitle_stream.index = self.get_index_from_stream_info()
        subtitle_stream.codec_name = self.get_codec_name_from_stream_info()
        subtitle_stream.language = self.get_language_from_stream_info()

        self.add_subtitle_stream(subtitle_stream)

    def add_subtitle_stream(self, subtitle_stream: SubtitleStream):
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
            duration_in_seconds = round(float(duration))

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
