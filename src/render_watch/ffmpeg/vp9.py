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


class VP9:
    """Manages all settings for the VP9 codec."""

    QUALITY_ARGS_LIST = ('auto', 'good', 'best', 'realtime')
    SPEED_ARGS_LIST = ('auto', '0', '1', '2', '3', '4', '5')

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libvpx-vp9',
            '-b:v': '2500k'
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def quality(self):
        """Returns quality argument as an index."""
        if '-deadline' in self.ffmpeg_args:
            quality_arg = self.ffmpeg_args['-deadline']
            return self.QUALITY_ARGS_LIST.index(quality_arg)
        return 0

    @quality.setter
    def quality(self, quality_index):
        """Stores index as a quality argument."""
        if quality_index is None or not 1 <= quality_index <= 3:
            self.ffmpeg_args.pop('-deadline', 0)
        else:
            self.ffmpeg_args['-deadline'] = self.QUALITY_ARGS_LIST[quality_index]

    @property
    def speed(self):
        """Returns speed argument as an index."""
        if '-cpu-used' in self.ffmpeg_args:
            speed_arg = self.ffmpeg_args['-cpu-used']
            return self.SPEED_ARGS_LIST.index(speed_arg)
        return 0

    @speed.setter
    def speed(self, speed_index):
        """Stores index as a speed argument."""
        if speed_index is None or not 1 <= speed_index <= 6:
            self.ffmpeg_args.pop('-cpu-used', 0)
        else:
            self.ffmpeg_args['-cpu-used'] = self.SPEED_ARGS_LIST[speed_index]

    @property
    def bitrate(self):
        """Returns bitrate argument as an int."""
        bitrate_arg = self.ffmpeg_args['-b:v']
        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value):
        """Stores bitrate value as a string argument."""
        if bitrate_value is None or not 0 <= bitrate_value <= 99999:
            self.ffmpeg_args['-b:v'] = '2500k'
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'

    @property
    def crf(self):
        """Returns crf argument as a float."""
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return None

    @crf.setter
    def crf(self, crf_value):
        """Stores crf value as a string argument."""
        if crf_value is None or not 0 <= crf_value <= 63:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)

    @property
    def maxrate(self):
        """Returns maxrate argument as an int."""
        if '-maxrate' in self.ffmpeg_args:
            maxrate_arg = self.ffmpeg_args['-maxrate']
            return int(maxrate_arg.split('k')[0])
        return None

    @maxrate.setter
    def maxrate(self, maxrate_value):
        """Stores maxrate value as a string argument."""
        if maxrate_value is None or not 0 <= maxrate_value <= 99999:
            self.ffmpeg_args.pop('-maxrate', 0)
        else:
            self.ffmpeg_args['-maxrate'] = str(maxrate_value) + 'k'

    @property
    def minrate(self):
        """Returns minrate argument as an int."""
        if '-minrate' in self.ffmpeg_args:
            minrate_arg = self.ffmpeg_args['-minrate']
            return int(minrate_arg.split('k')[0])
        return None

    @minrate.setter
    def minrate(self, minrate_value):
        """Stores minrate value as a string argument."""
        if minrate_value is None or not 0 <= minrate_value <= 99999:
            self.ffmpeg_args.pop('-minrate', 0)
        else:
            self.ffmpeg_args['-minrate'] = str(minrate_value) + 'k'

    @property
    def encode_pass(self):
        """Returns encode pass argument as an int."""
        if '-pass' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-pass'])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        """Stores encode pass value as a string argument."""
        if encode_pass_value is None or not 1 <= encode_pass_value <= 2:
            self.ffmpeg_args.pop('-pass', 0)
        else:
            self.ffmpeg_args['-pass'] = str(encode_pass_value)

    @property
    def stats(self):
        """Returns pass log file argument as a string."""
        if '-passlogfile' in self.ffmpeg_args:
            return self.ffmpeg_args['-passlogfile']
        return None

    @stats.setter
    def stats(self, stats_file_path):
        """Stores pass log file path as a string argument."""
        if stats_file_path is None:
            self.ffmpeg_args.pop('-passlogfile', 0)
        else:
            self.ffmpeg_args['-passlogfile'] = stats_file_path

    @property
    def row_multithreading(self):
        """Returns row multithreading argument as a boolean."""
        if '-row-mt' in self.ffmpeg_args:
            row_multithreading_arg = self.ffmpeg_args['-row-mt']
            return row_multithreading_arg == '1'
        return False

    @row_multithreading.setter
    def row_multithreading(self, row_multithreading_value):
        """Stores row multithreading boolean as a string argument."""
        if row_multithreading_value is None or not row_multithreading_value:
            self.ffmpeg_args.pop('-row-mt', 0)
        else:
            self.ffmpeg_args['-row-mt'] = '1'

    @staticmethod
    def get_ffmpeg_advanced_args():
        """Returns null advanced settings dictionary."""
        return {'': None}
