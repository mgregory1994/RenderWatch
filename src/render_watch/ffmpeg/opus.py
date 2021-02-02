"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""


class Opus:
    channels_human_readable_list = ("auto", "1", "2", "2.1", "4", "5.1", "7.1")
    channels_ffmpeg_args_list = ('auto', '1', '2', '3', '4', '6', '8')

    def __init__(self):
        self.ffmpeg_args = {
            "-c:a": "libopus",
            '-b:a': '128k',
            "-ac": None
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:a']

    @property
    def bitrate(self):
        try:
            bitrate = self.ffmpeg_args['-b:a']
            bitrate_value = int(bitrate.split('k')[0])
        except:
            return 128
        else:
            return bitrate_value

    @bitrate.setter
    def bitrate(self, bitrate_value):
        try:
            if bitrate_value is None or bitrate_value < 64 or bitrate_value > 999:
                raise ValueError

            self.ffmpeg_args['-b:a'] = str(bitrate_value) + 'k'
        except (ValueError, TypeError):
            self.ffmpeg_args['-b:a'] = '128k'

    @property
    def channels(self):
        try:
            channels = self.ffmpeg_args['-ac']

            if channels is None:
                channels_index = 0
            else:
                channels_index = self.channels_ffmpeg_args_list.index(channels)
        except ValueError:
            return 0
        else:
            return channels_index

    @property
    def channels_str(self):
        try:
            channels = self.ffmpeg_args['-ac']

            if channels is None:
                return 'N/A'

            channels_index = self.channels_ffmpeg_args_list.index(channels)
        except ValueError:
            return 'N/A'
        else:
            return self.channels_human_readable_list[channels_index]

    @channels.setter
    def channels(self, channels_index):
        try:
            if channels_index is None or channels_index < 1:
                self.ffmpeg_args['-ac'] = None
            else:
                self.ffmpeg_args['-ac'] = self.channels_ffmpeg_args_list[channels_index]
        except IndexError:
            self.ffmpeg_args['-ac'] = None
