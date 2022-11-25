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


AUDIO_CODECS_MP4_UI = ('copy', 'aac')
AUDIO_CODECS_MP4 = ('copy', 'aac')
AUDIO_CODECS_MKV_UI = ('copy', 'aac', 'opus')
AUDIO_CODECS_MKV = ('copy', 'aac', 'libopus')
AUDIO_CODECS_TS_UI = ('copy', 'aac')
AUDIO_CODECS_TS = ('copy', 'aac')
AUDIO_CODECS_WEBM_UI = ('copy', 'opus')
AUDIO_CODECS_WEBM = ('copy', 'libopus')
AUDIO_CODECS_AAC_UI = ('copy', 'aac')
AUDIO_CODECS_AAC = ('copy', 'aac')
AUDIO_CODECS_M4A_UI = ('copy', 'aac')
AUDIO_CODECS_M4A = ('copy', 'aac')
AUDIO_CODECS_OGG_UI = ('copy', 'libopus')
AUDIO_CODECS_OGG = ('copy', 'opus')


def is_codec_copy(audio_codec) -> bool:
    """
    Returns whether the given audio codec is a Copy codec.

    Parameters:
        audio_codec: Audio codec to check.

    Returns:
        Boolean that represents whether the given audio codec is a Copy codec.
    """
    return isinstance(audio_codec, Copy)


def is_copy_codec_in_audio_streams(audio_streams: dict) -> bool:
    """
    Returns whether there's an audio stream that has a copy codec.

    Parameters:
        audio_streams: Dictionary that contains audio stream keys and audio codec items.

    Returns:
        Boolean that represents whether there's an audio stream that has a copy codec.
    """
    for audio_stream, audio_codec in audio_streams.items():
        if is_codec_copy(audio_codec):
            return True
    return False


def is_codec_aac(audio_codec) -> bool:
    """
    Returns whether the given audio codec is an Aac codec.

    Parameters:
        audio_codec: Audio codec to check.

    Returns:
        Boolean that represents whether the given audio codec is an Aac codec.
    """
    return isinstance(audio_codec, Aac)


def is_codec_opus(audio_codec) -> bool:
    """
    Returns whether the given audio codec is an Opus codec.

    Parameters:
        audio_codec: Audio codec to check.

    Returns:
        Boolean that represents whether the given audio codec is an Opus codec.
    """
    return isinstance(audio_codec, Opus)


class Copy:
    """Class that configures all Copy codec settings available for Render Watch."""

    def __init__(self, audio_stream_index):
        """
        Initializes the Aac class with all necessary variables for the codec's options.

        Parameters:
            audio_stream_index: Index of the audio stream that's using this codec.
        """
        self.codec_name_arg = ''.join(['-c:a:', str(audio_stream_index)])
        self.ffmpeg_args = {
            self.codec_name_arg: 'aac',
        }


class Aac:
    """Class that configures all AAC codec settings available for Render Watch."""

    CHANNELS_UI = ('auto', '1', '2', '2.1', '4', '5.1', '7.1')
    CHANNELS = ('auto', '1', '2', '3', '4', '6', '8')
    CHANNELS_LENGTH = len(CHANNELS)

    BITRATE_MIN = 32
    BITRATE_MAX = 996

    def __init__(self, audio_stream_index):
        """
        Initializes the Aac class with all necessary variables for the codec's options.

        Parameters:
            audio_stream_index: Index of the audio stream that's using this codec.
        """
        self.codec_name_arg = ''.join(['-c:a:', str(audio_stream_index)])
        self.bitrate_arg = ''.join(['-b:a:', str(audio_stream_index)])
        self.channels_arg = ''.join(['-ac:a:', str(audio_stream_index)])
        self.ffmpeg_args = {
            self.codec_name_arg: 'aac',
            self.bitrate_arg: '128k'
        }

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args[self.codec_name_arg]

    @property
    def bitrate(self) -> int:
        """
        Returns what the bitrate option is set to.

        Returns:
            Bitrate as an int.
        """
        bitrate_arg = self.ffmpeg_args[self.bitrate_arg]

        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate option to the specified value.

        Parameters:
            bitrate_value: The value to set the bitrate to.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args[self.bitrate_arg] = '128k'
        else:
            self.ffmpeg_args[self.bitrate_arg] = str(bitrate_value) + 'k'

    @property
    def channels(self) -> int:
        """
        Returns what the channels option is set to.

        Returns:
            Channels as an index using the CHANNELS variable.
        """
        if self.channels_arg in self.ffmpeg_args:
            channels_arg = self.ffmpeg_args[self.channels_arg]

            return self.CHANNELS.index(channels_arg)
        return 0

    @property
    def channels_str(self) -> str:
        """
        Returns what the channels option is set to.

        Returns:
            Channels as a string using the CHANNELS_UI variable.
        """
        channels_index = self.channels

        if channels_index:
            return self.CHANNELS_UI[channels_index]
        return 'N/A'

    @channels.setter
    def channels(self, channels_index: int | None):
        """
        Sets the channels option.

        Parameters:
            channels_index: Index from the CHANNELS variable.

        Returns:
            None
        """
        if channels_index and 0 < channels_index < Aac.CHANNELS_LENGTH:
            self.ffmpeg_args[self.channels_arg] = self.CHANNELS[channels_index]
        else:
            self.ffmpeg_args.pop(self.channels_arg, 0)


class Opus:
    """Class that configures all Opus codec settings available for Render Watch"""

    CHANNELS_UI = ('auto', '1', '2', '2.1', '4', '5.1', '7.1')
    CHANNELS = ('auto', '1', '2', '3', '4', '6', '8')
    CHANNELS_LENGTH = len(CHANNELS)

    BITRATE_MIN = 32
    BITRATE_MAX = 996

    def __init__(self, audio_stream_index: int):
        """
        Initializes the Opus class with all necessary variables for the codec's options.

        Parameters:
            audio_stream_index: Index of the audio stream that's using this codec.
        """
        self.codec_name_arg = ''.join(['-c:a:', str(audio_stream_index)])
        self.bitrate_arg = ''.join(['-b:a:', str(audio_stream_index)])
        self.channels_arg = ''.join(['-ac:a:', str(audio_stream_index)])
        self.ffmpeg_args = {
            self.codec_name_arg: 'libopus',
            self.bitrate_arg: '128k'
        }

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args[self.codec_name_arg]

    @property
    def bitrate(self) -> int:
        """
        Returns what the bitrate option is set to.

        Returns:
            Bitrate as an int.
        """
        bitrate_arg = self.ffmpeg_args[self.bitrate_arg]

        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate option to the specified value.

        Parameters:
            bitrate_value: The value to set the bitrate to.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args[self.bitrate_arg] = '128k'
        else:
            self.ffmpeg_args[self.bitrate_arg] = str(bitrate_value) + 'k'

    @property
    def channels(self) -> int:
        """
        Returns what the channels option is set to.

        Returns:
            Channels as an index using the CHANNELS variable.
        """
        if self.channels_arg in self.ffmpeg_args:
            channels_arg = self.ffmpeg_args[self.channels_arg]

            return self.CHANNELS.index(channels_arg)
        return 0

    @property
    def channels_str(self) -> str:
        """
        Returns what the channels option is set to.

        Returns:
            Channels as a string using the CHANNELS_UI variable.
        """
        channels_index = self.channels

        if channels_index:
            return self.CHANNELS[channels_index]
        return 'N/A'

    @channels.setter
    def channels(self, channels_index: int | None):
        """
        Sets the channels option.

        Parameters:
            channels_index: Index from the CHANNELS variable.

        Returns:
            None
        """
        if channels_index and 0 < channels_index < Opus.CHANNELS_LENGTH:
            self.ffmpeg_args[self.channels_arg] = self.CHANNELS[channels_index]
        else:
            self.ffmpeg_args.pop(self.channels_arg, 0)
