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


class Aac:
    """Class that configures all AAC codec settings available for Render Watch."""

    CHANNELS_UI = ('auto', '1', '2', '2.1', '4', '5.1', '7.1')
    CHANNELS = ('auto', '1', '2', '3', '4', '6', '8')
    CHANNELS_LENGTH = len(CHANNELS)

    def __init__(self, audio_stream_index):
        """
        Initializes the Aac class with all necessary variables for the codec's options.

        Parameters:
            audio_stream_index: Index of the audio stream that's using this codec.

        Returns:
            None
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
        if '-ac' in self.ffmpeg_args:
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
        Sets the codec's channels option.

        Parameters:
            channels_index: Index from the CHANNELS variable.

        Returns:
            None
        """
        if channels_index and 0 < channels_index < Aac.CHANNELS_LENGTH:
            self.ffmpeg_args[self.channels_arg] = self.CHANNELS[channels_index]
        else:
            self.ffmpeg_args.pop(self.channels_arg, 0)
