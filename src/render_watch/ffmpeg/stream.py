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

    def get_dimensions(self) -> tuple:
        """
        Returns the video stream's dimensions.

        Returns:
            Tuple that contains the video stream's width and height respectively.
        """
        return self.width, self.height

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
                        '] ',
                        self.codec_name,
                        ' (',
                        str(self.channels),
                        ' Ch,',
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
