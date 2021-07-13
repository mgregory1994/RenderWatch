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
    """Manages all trim ffmpeg settings."""

    def __init__(self):
        self.ffmpeg_args = {}

    @property
    def start_time(self):
        """Returns start time argument as a float."""
        if '-ss' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-ss'])
        return None

    @start_time.setter
    def start_time(self, start_time_value):
        """Stores start time value as a string argument."""
        if start_time_value is None or start_time_value < 0:
            self.ffmpeg_args.pop('-ss', 0)
        else:
            self.ffmpeg_args['-ss'] = str(start_time_value)

    @property
    def trim_duration(self):
        """Returns trim duration argument as a float."""
        if '-to' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-to'])
        return None

    @trim_duration.setter
    def trim_duration(self, trim_duration_value):
        """Stores trim duration value as a string argument."""
        if trim_duration_value is None:
            self.ffmpeg_args.pop('-to', 0)
        else:
            self.ffmpeg_args['-to'] = str(trim_duration_value)
