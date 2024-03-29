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
    """
    Stores all settings for the VP9 codec.
    """

    QUALITY_ARGS_LIST = ('auto', 'good', 'best', 'realtime')
    QUALITY_LIST_LENGTH = len(QUALITY_ARGS_LIST)
    SPEED_ARGS_LIST = ('auto', '0', '1', '2', '3', '4', '5')
    SPEED_LIST_LENGTH = len(SPEED_ARGS_LIST)

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
        """
        Returns quality as an index.
        """
        if '-deadline' in self.ffmpeg_args:
            quality_arg = self.ffmpeg_args['-deadline']
            return self.QUALITY_ARGS_LIST.index(quality_arg)
        return 0

    @quality.setter
    def quality(self, quality_index):
        """
        Stores quality index as a string.
        """
        if quality_index is None or not 0 < quality_index < VP9.QUALITY_LIST_LENGTH:
            self.ffmpeg_args.pop('-deadline', 0)
        else:
            self.ffmpeg_args['-deadline'] = self.QUALITY_ARGS_LIST[quality_index]

    @property
    def speed(self):
        """
        Returns speed as an index.
        """
        if '-cpu-used' in self.ffmpeg_args:
            speed_arg = self.ffmpeg_args['-cpu-used']
            return self.SPEED_ARGS_LIST.index(speed_arg)
        return 0

    @speed.setter
    def speed(self, speed_index):
        """
        Stores speed index as a string.
        """
        if speed_index is None or not 0 < speed_index < VP9.SPEED_LIST_LENGTH:
            self.ffmpeg_args.pop('-cpu-used', 0)
        else:
            self.ffmpeg_args['-cpu-used'] = self.SPEED_ARGS_LIST[speed_index]

    @property
    def bitrate(self):
        """
        Returns bitrate as an int.
        """
        bitrate_arg = self.ffmpeg_args['-b:v']
        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate):
        """
        Stores bitrate as a string.
        """
        if bitrate is None or not 0 <= bitrate <= 99999:
            self.ffmpeg_args['-b:v'] = '2500k'
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate) + 'k'

    @property
    def crf(self):
        """
        Returns crf as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return None

    @crf.setter
    def crf(self, crf):
        """
        Stores crf as a string.
        """
        if crf is None or not 0 <= crf <= 63:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf)

    @property
    def maxrate(self):
        """
        Returns maxrate as an int.
        """
        if '-maxrate' in self.ffmpeg_args:
            maxrate_arg = self.ffmpeg_args['-maxrate']
            return int(maxrate_arg.split('k')[0])
        return None

    @maxrate.setter
    def maxrate(self, maxrate):
        """
        Stores maxrate as a string.
        """
        if maxrate is None or not 0 <= maxrate <= 99999:
            self.ffmpeg_args.pop('-maxrate', 0)
        else:
            self.ffmpeg_args['-maxrate'] = str(maxrate) + 'k'

    @property
    def minrate(self):
        """
        Returns minrate as an int.
        """
        if '-minrate' in self.ffmpeg_args:
            minrate_arg = self.ffmpeg_args['-minrate']
            return int(minrate_arg.split('k')[0])
        return None

    @minrate.setter
    def minrate(self, minrate):
        """
        Stores minrate as a string.
        """
        if minrate is None or not 0 <= minrate <= 99999:
            self.ffmpeg_args.pop('-minrate', 0)
        else:
            self.ffmpeg_args['-minrate'] = str(minrate) + 'k'

    @property
    def encode_pass(self):
        """
        Returns encode pass as an int.
        """
        if '-pass' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-pass'])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass):
        """
        Stores encode pass as a string.
        """
        if encode_pass is None or not 1 <= encode_pass <= 2:
            self.ffmpeg_args.pop('-pass', 0)
        else:
            self.ffmpeg_args['-pass'] = str(encode_pass)

    @property
    def stats(self):
        """
        Returns pass log file path as a string.
        """
        if '-passlogfile' in self.ffmpeg_args:
            return self.ffmpeg_args['-passlogfile']
        return None

    @stats.setter
    def stats(self, stats_file_path):
        """
        Stores pass log file path as a string.
        """
        if stats_file_path is None:
            self.ffmpeg_args.pop('-passlogfile', 0)
        else:
            self.ffmpeg_args['-passlogfile'] = stats_file_path

    @property
    def row_multithreading(self):
        """
        Returns row multithreading as a boolean.
        """
        if '-row-mt' in self.ffmpeg_args:
            row_multithreading_arg = self.ffmpeg_args['-row-mt']
            return row_multithreading_arg == '1'
        return False

    @row_multithreading.setter
    def row_multithreading(self, row_multithreading_enabled):
        """
        Stores row multithreading as a string argument.
        """
        if row_multithreading_enabled is None or not row_multithreading_enabled:
            self.ffmpeg_args.pop('-row-mt', 0)
        else:
            self.ffmpeg_args['-row-mt'] = '1'

    @staticmethod
    def get_ffmpeg_advanced_args():
        """
        Null dictionary for compatibility.
        """
        return {'': None}
