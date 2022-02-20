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


class VP9:
    """
    Stores all settings for the VP9 codec.
    """

    QUALITY = ('auto', 'good', 'best', 'realtime')
    QUALITY_LENGTH = len(QUALITY)

    SPEED = ('auto', '0', '1', '2', '3', '4', '5')
    SPEED_LENGTH = len(SPEED)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libvpx-vp9',
            '-b:v': '2500k'
        }

    @property
    def codec_name(self) -> str:
        return self.ffmpeg_args['-c:v']

    @property
    def quality(self) -> int:
        """
        Returns quality as an index.
        """
        if '-deadline' in self.ffmpeg_args:
            quality_arg = self.ffmpeg_args['-deadline']

            return self.QUALITY.index(quality_arg)
        return 0

    @quality.setter
    def quality(self, quality_index: int):
        if quality_index and 0 < quality_index < VP9.QUALITY_LENGTH:
            self.ffmpeg_args['-deadline'] = self.QUALITY[quality_index]
        else:
            self.ffmpeg_args.pop('-deadline', 0)

    @property
    def speed(self) -> int:
        """
        Returns speed as an index.
        """
        if '-cpu-used' in self.ffmpeg_args:
            speed_arg = self.ffmpeg_args['-cpu-used']

            return self.SPEED.index(speed_arg)
        return 0

    @speed.setter
    def speed(self, speed_index: int):
        if speed_index and 0 < speed_index < VP9.SPEED_LENGTH:
            self.ffmpeg_args['-cpu-used'] = self.SPEED[speed_index]
        else:
            self.ffmpeg_args.pop('-cpu-used', 0)

    @property
    def bitrate(self) -> int:
        bitrate_arg = self.ffmpeg_args['-b:v']

        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value: int):
        if bitrate_value is None:
            self.ffmpeg_args['-b:v'] = '2500k'
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'

    @property
    def crf(self) -> float:
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return 30.0

    @crf.setter
    def crf(self, crf_value: float):
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)

    @property
    def maxrate(self) -> int:
        if '-maxrate' in self.ffmpeg_args:
            maxrate_arg = self.ffmpeg_args['-maxrate']

            return int(maxrate_arg.split('k')[0])
        return 2500

    @maxrate.setter
    def maxrate(self, maxrate_value: int):
        if maxrate_value is None:
            self.ffmpeg_args.pop('-maxrate', 0)
        else:
            self.ffmpeg_args['-maxrate'] = str(maxrate_value) + 'k'

    @property
    def minrate(self) -> int:
        if '-minrate' in self.ffmpeg_args:
            minrate_arg = self.ffmpeg_args['-minrate']

            return int(minrate_arg.split('k')[0])
        return 2500

    @minrate.setter
    def minrate(self, minrate_value: int):
        if minrate_value is None:
            self.ffmpeg_args.pop('-minrate', 0)
        else:
            self.ffmpeg_args['-minrate'] = str(minrate_value) + 'k'

    @property
    def encode_pass(self) -> int:
        if '-pass' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-pass'])
        return 2500

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        if encode_pass_value:
            self.ffmpeg_args['-pass'] = str(encode_pass_value)
        else:
            self.ffmpeg_args.pop('-pass', 0)

    @property
    def stats(self) -> str:
        if '-passlogfile' in self.ffmpeg_args:
            return self.ffmpeg_args['-passlogfile']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str):
        if stats_file_path:
            self.ffmpeg_args['-passlogfile'] = stats_file_path
        else:
            self.ffmpeg_args.pop('-passlogfile', 0)

    @property
    def row_multithreading(self) -> bool:
        if '-row-mt' in self.ffmpeg_args:
            row_multithreading_arg = self.ffmpeg_args['-row-mt']

            return row_multithreading_arg == '1'
        return False

    @row_multithreading.setter
    def row_multithreading(self, is_row_multithreading_enabled: bool):
        if is_row_multithreading_enabled:
            self.ffmpeg_args['-row-mt'] = '1'
        else:
            self.ffmpeg_args.pop('-row-mt', 0)

    @staticmethod
    def get_ffmpeg_advanced_args() -> dict:
        """
        Null dictionary.
        """
        return {'': None}
