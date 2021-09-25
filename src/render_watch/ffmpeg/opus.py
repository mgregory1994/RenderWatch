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


class Opus:
    """Manages all settings for the Opus codec."""

    CHANNELS_UI_LIST = ('auto', '1', '2', '2.1', '4', '5.1', '7.1')
    CHANNELS_ARGS_LIST = ('auto', '1', '2', '3', '4', '6', '8')
    CHANNELS_LIST_LENGTH = len(CHANNELS_ARGS_LIST)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:a': 'libopus',
            '-b:a': '128k'
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:a']

    @property
    def bitrate(self):
        """Returns bitrate argument as an int."""
        bitrate_arg = self.ffmpeg_args['-b:a']
        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value):
        """Stores bitrate value as a string argument."""
        if bitrate_value is None or not 64 <= bitrate_value <= 999:
            self.ffmpeg_args['-b:a'] = '128k'
        else:
            self.ffmpeg_args['-b:a'] = str(bitrate_value) + 'k'

    @property
    def channels(self):
        """Returns channels argument as an index."""
        if '-ac' in self.ffmpeg_args:
            channels_arg = self.ffmpeg_args['-ac']
            return self.CHANNELS_ARGS_LIST.index(channels_arg)
        return 0

    @property
    def channels_str(self):
        """Returns channels argument as a UI string."""
        channels_index = self.channels
        if channels_index:
            return self.CHANNELS_ARGS_LIST[channels_index]
        return 'N/A'

    @channels.setter
    def channels(self, channels_index):
        """Stores index as a channels argument."""
        if channels_index is None or not 0 < channels_index < Opus.CHANNELS_LIST_LENGTH:
            self.ffmpeg_args.pop('-ac', 0)
        else:
            self.ffmpeg_args['-ac'] = self.CHANNELS_ARGS_LIST[channels_index]
