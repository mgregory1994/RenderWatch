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


class Opus:
    """
    Stores all settings for the Opus codec.
    """

    CHANNELS_UI = ('auto', '1', '2', '2.1', '4', '5.1', '7.1')
    CHANNELS = ('auto', '1', '2', '3', '4', '6', '8')
    CHANNELS_LENGTH = len(CHANNELS)

    def __init__(self, index: int):
        self.codec_name_arg = ''.join(['-c:a:', str(index)])
        self.bitrate_arg = ''.join(['-b:a:', str(index)])
        self.channels_arg = ''.join(['-ac:a:', str(index)])
        self.ffmpeg_args = {
            self.codec_name_arg: 'libopus',
            self.bitrate_arg: '128k'
        }

    @property
    def codec_name(self) -> str:
        return self.ffmpeg_args[self.codec_name_arg]

    @property
    def bitrate(self) -> int:
        bitrate_arg = self.ffmpeg_args[self.bitrate_arg]

        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        if bitrate_value is None:
            self.ffmpeg_args[self.bitrate_arg] = '128k'
        else:
            self.ffmpeg_args[self.bitrate_arg] = str(bitrate_value) + 'k'

    @property
    def channels(self) -> int:
        """
        Returns channels as an index.
        """
        if '-ac' in self.ffmpeg_args:
            channels_arg = self.ffmpeg_args[self.channels_arg]

            return self.CHANNELS.index(channels_arg)
        return 0

    @property
    def channels_str(self) -> str:
        channels_index = self.channels

        if channels_index:
            return self.CHANNELS[channels_index]
        return 'N/A'

    @channels.setter
    def channels(self, channels_index: int | None):
        if channels_index and 0 < channels_index < Opus.CHANNELS_LENGTH:
            self.ffmpeg_args[self.channels_arg] = self.CHANNELS[channels_index]
        else:
            self.ffmpeg_args.pop(self.channels_arg, 0)
