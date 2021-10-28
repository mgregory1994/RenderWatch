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


class TrimSettings:
    """
    Stores all trim settings.
    """

    def __init__(self):
        self.ffmpeg_args = {}

    @property
    def start_time(self):
        """
        Returns start time as a float.
        """
        if '-ss' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-ss'])
        return None

    @start_time.setter
    def start_time(self, start_time):
        """
        Stores start time as a string.
        """
        if start_time is None or start_time < 0:
            self.ffmpeg_args.pop('-ss', 0)
        else:
            self.ffmpeg_args['-ss'] = str(start_time)

    @property
    def trim_duration(self):
        """
        Returns trim duration as a float.
        """
        if '-to' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-to'])
        return None

    @trim_duration.setter
    def trim_duration(self, trim_duration):
        """
        Stores trim duration as a string.
        """
        if trim_duration is None:
            self.ffmpeg_args.pop('-to', 0)
        else:
            self.ffmpeg_args['-to'] = str(trim_duration)
