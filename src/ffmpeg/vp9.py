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


class VP9:
    quality_ffmpeg_args_list = ('auto', 'good', 'best', 'realtime')
    speed_ffmpeg_args_list = ('auto', '0', '1', '2', '3', '4', '5')

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libvpx-vp9',
            '-b:v': '2500k',
            '-crf': None,
            '-minrate': None,
            '-maxrate': None,
            '-pass': None,
            '-passlogfile': None,
            '-deadline': None,
            '-cpu-used': None,
            '-row-mt': None
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def quality(self):
        try:
            quality_value = self.ffmpeg_args['-deadline']

            if quality_value is None:
                quality_index = 0
            else:
                quality_index = self.quality_ffmpeg_args_list.index(quality_value)
        except ValueError:
            return 0
        else:
            return quality_index

    @quality.setter
    def quality(self, quality_index):
        try:
            if quality_index is None or quality_index < 1:
                self.ffmpeg_args['-deadline'] = None
            else:
                self.ffmpeg_args['-deadline'] = self.quality_ffmpeg_args_list[quality_index]
        except IndexError:
            self.ffmpeg_args['-deadline'] = None

    @property
    def speed(self):
        try:
            speed_value = self.ffmpeg_args['-cpu-used']

            if speed_value is None:
                speed_index = 0
            else:
                speed_index = self.speed_ffmpeg_args_list.index(speed_value)
        except ValueError:
            return 0
        else:
            return speed_index

    @speed.setter
    def speed(self, speed_index):
        try:
            if speed_index is None or speed_index < 1:
                self.ffmpeg_args['-cpu-used'] = None
            else:
                self.ffmpeg_args['-cpu-used'] = self.speed_ffmpeg_args_list[speed_index]
        except IndexError:
            self.ffmpeg_args['-cpu-used'] = None

    @property
    def bitrate(self):
        try:
            bitrate = self.ffmpeg_args['-b:v']
            bitrate_value = int(bitrate.split('k')[0])
        except:
            return 2500
        else:
            return bitrate_value

    @bitrate.setter
    def bitrate(self, bitrate_value):
        try:
            if bitrate_value is None or bitrate_value < 0 or bitrate_value > 99999:
                raise ValueError

            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
        except (ValueError, TypeError):
            self.ffmpeg_args['-b:v'] = '2500k'

    @property
    def crf(self):
        try:
            crf = self.ffmpeg_args['-crf']
            crf_value = float(crf)

            if crf_value < 0 or crf_value > 63:
                raise ValueError
        except (ValueError, TypeError):
            return None
        else:
            return crf_value

    @crf.setter
    def crf(self, crf_value):
        try:
            if crf_value is None or crf_value < 0 or crf_value > 63:
                raise ValueError

            self.ffmpeg_args['-crf'] = str(crf_value)
        except (ValueError, TypeError):
            self.ffmpeg_args['-crf'] = None

    @property
    def maxrate(self):
        try:
            maxrate = self.ffmpeg_args['-maxrate']
            maxrate_value = int(maxrate.split('k')[0])

            if maxrate_value < 0 or maxrate_value > 99999:
                raise ValueError
        except:
            return None
        else:
            return maxrate_value

    @maxrate.setter
    def maxrate(self, maxrate_value):
        try:
            if maxrate_value is None or maxrate_value < 0 or maxrate_value > 99999:
                raise ValueError

            self.ffmpeg_args['-maxrate'] = str(maxrate_value) + 'k'
        except (ValueError, TypeError):
            self.ffmpeg_args['-maxrate'] = None

    @property
    def minrate(self):
        try:
            minrate = self.ffmpeg_args['-minrate']
            minrate_value = int(minrate.split('k')[0])

            if minrate_value < 0 or minrate_value > 99999:
                raise ValueError
        except:
            return None
        else:
            return minrate_value

    @minrate.setter
    def minrate(self, minrate_value):
        try:
            if minrate_value is None or minrate_value < 0 or minrate_value > 99999:
                raise ValueError

            self.ffmpeg_args['-minrate'] = str(minrate_value) + 'k'
        except (ValueError, TypeError):
            self.ffmpeg_args['-minrate'] = None

    @property
    def encode_pass(self):
        try:
            encode_pass = self.ffmpeg_args['-pass']
            encode_pass_value = int(encode_pass)

            if encode_pass_value < 1 or encode_pass_value > 2:
                raise ValueError
        except (ValueError, TypeError):
            return None
        else:
            return encode_pass_value

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        try:
            if encode_pass_value is None or encode_pass_value < 1 or encode_pass_value > 2:
                raise ValueError

            self.ffmpeg_args['-pass'] = str(encode_pass_value)
        except (ValueError, TypeError):
            self.ffmpeg_args['-pass'] = None

    @property
    def stats(self):
        return self.ffmpeg_args['-passlogfile']

    @stats.setter
    def stats(self, stats_file_path):
        self.ffmpeg_args['-passlogfile'] = stats_file_path

    @property
    def row_multithreading(self):
        row_multithreading_value = self.ffmpeg_args['-row-mt']

        if row_multithreading_value is None or row_multithreading_value != '1':
            return False

        return True

    @row_multithreading.setter
    def row_multithreading(self, row_multithreading_value):
        if row_multithreading_value is None or not row_multithreading_value:
            self.ffmpeg_args['-row-mt'] = None
        else:
            self.ffmpeg_args['-row-mt'] = '1'

    def get_ffmpeg_advanced_args(self):
        return {'': None}
