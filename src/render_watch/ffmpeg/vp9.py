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
    """Class that configures all VP9 codec settings available for Render Watch."""

    QUALITY = ('auto', 'good', 'best', 'realtime')
    QUALITY_LENGTH = len(QUALITY)

    SPEED = ('auto', '0', '1', '2', '3', '4', '5')
    SPEED_LENGTH = len(SPEED)

    def __init__(self):
        """Initializes the VP9 class with all necessary variables for the codec's options."""
        self.ffmpeg_args = {
            '-c:v': 'libvpx-vp9',
            '-b:v': '2500k'
        }

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def quality(self) -> int:
        """
        Returns what the quality option is set to.

        Returns:
            Quality option as an index using the QUALITY variable.
        """
        if '-deadline' in self.ffmpeg_args:
            quality_arg = self.ffmpeg_args['-deadline']

            return self.QUALITY.index(quality_arg)
        return 0

    @quality.setter
    def quality(self, quality_index: int | None):
        """
        Sets the quality option.

        Parameters:
            quality_index: Index from the QUALITY variable.

        Returns:
            None
        """
        if quality_index and 0 < quality_index < VP9.QUALITY_LENGTH:
            self.ffmpeg_args['-deadline'] = self.QUALITY[quality_index]
        else:
            self.ffmpeg_args.pop('-deadline', 0)

    @property
    def speed(self) -> int:
        """
        Returns what the speed option is set to.

        Returns:
            Speed option as an index using the SPEED variable.
        """
        if '-cpu-used' in self.ffmpeg_args:
            speed_arg = self.ffmpeg_args['-cpu-used']

            return self.SPEED.index(speed_arg)
        return 0

    @speed.setter
    def speed(self, speed_index: int | None):
        """
        Sets the speed option.

        Parameters:
            speed_index: Index from the SPEED variable.

        Returns:
            None
        """
        if speed_index and 0 < speed_index < VP9.SPEED_LENGTH:
            self.ffmpeg_args['-cpu-used'] = self.SPEED[speed_index]
        else:
            self.ffmpeg_args.pop('-cpu-used', 0)

    @property
    def bitrate(self) -> int:
        """
        Returns what the bitrate option is set to.

        Returns:
            Bitrate as an int.
        """
        bitrate_arg = self.ffmpeg_args['-b:v']

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
            self.ffmpeg_args['-b:v'] = '2500k'
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'

    @property
    def crf(self) -> float:
        """
        Returns what the CRF option is set to.

        Returns:
            CRF as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return 30.0

    @crf.setter
    def crf(self, crf_value: float | None):
        """
        Sets the CRF option to the specified value.

        Parameters:
            crf_value: The value to set the CRF option to.

        Returns:
            None
        """
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)

    @property
    def maxrate(self) -> int:
        """
        Returns what the maxrate option is set to.

        Returns:
            Maxrate as an int.
        """
        if '-maxrate' in self.ffmpeg_args:
            maxrate_arg = self.ffmpeg_args['-maxrate']

            return int(maxrate_arg.split('k')[0])
        return 2500

    @maxrate.setter
    def maxrate(self, maxrate_value: int | None):
        """
        Sets the maxrate option to the specified value.

        Parameters:
            maxrate_value: The value to set the maxrate option to.

        Returns:
            None
        """
        if maxrate_value is None:
            self.ffmpeg_args.pop('-maxrate', 0)
        else:
            self.ffmpeg_args['-maxrate'] = str(maxrate_value) + 'k'

    @property
    def minrate(self) -> int:
        """
        Returns what the minrate option is set to.

        Returns:
            Minrate as an int.
        """
        if '-minrate' in self.ffmpeg_args:
            minrate_arg = self.ffmpeg_args['-minrate']

            return int(minrate_arg.split('k')[0])
        return 2500

    @minrate.setter
    def minrate(self, minrate_value: int | None):
        """
        Sets the minrate option to the specified value.

        Parameters:
            minrate_value: The value to set the minrate option to.

        Returns:
            None
        """
        if minrate_value is None:
            self.ffmpeg_args.pop('-minrate', 0)
        else:
            self.ffmpeg_args['-minrate'] = str(minrate_value) + 'k'

    @property
    def encode_pass(self) -> int:
        """
        Returns what the encode pass option is set to.

        Returns:
            Encode pass as an int.
        """
        if '-pass' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-pass'])
        return 2500

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        """
        Sets the encode pass option to the specified value.

        Parameters:
            encode_pass_value: The value to set the encode pass option to.

        Returns:
            None
        """
        if encode_pass_value:
            self.ffmpeg_args['-pass'] = str(encode_pass_value)
        else:
            self.ffmpeg_args.pop('-pass', 0)

    @property
    def stats(self) -> str:
        """
        Returns what the stats option is set to.

        Returns:
            Stats as a string representing the file path to use.
        """
        if '-passlogfile' in self.ffmpeg_args:
            return self.ffmpeg_args['-passlogfile']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        """
        Sets the stats option to the specified value.

        Parameters:
            stats_file_path: File path string to set the stats option to.
        """
        if stats_file_path:
            self.ffmpeg_args['-passlogfile'] = stats_file_path
        else:
            self.ffmpeg_args.pop('-passlogfile', 0)

    @property
    def row_multithreading(self) -> bool:
        """
        Returns what the row multithreading option is set to.

        Returns:
            Row multithreading as a boolean.
        """
        if '-row-mt' in self.ffmpeg_args:
            row_multithreading_arg = self.ffmpeg_args['-row-mt']

            return row_multithreading_arg == '1'
        return False

    @row_multithreading.setter
    def row_multithreading(self, is_row_multithreading_enabled: bool):
        """
        Toggles the row multithreading option.

        Parameters:
            is_row_multithreading_enabled: Boolean value to set the row multithreading option to.
        """
        if is_row_multithreading_enabled:
            self.ffmpeg_args['-row-mt'] = '1'
        else:
            self.ffmpeg_args.pop('-row-mt', 0)

    @staticmethod
    def get_ffmpeg_advanced_args() -> dict:
        """Null dictionary for compatibility with the encoding module for the FFmpegArgs class."""
        return {'': None}
