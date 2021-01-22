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


class TrimSettings:
    def __init__(self):
        self.ffmpeg_args = {
            "-ss": None,
            "-to": None
        }

    @property
    def start_time(self):
        try:
            start_time = self.ffmpeg_args['-ss']
            start_time_value = float(start_time)
        except TypeError:
            return None
        else:
            return start_time_value

    @start_time.setter
    def start_time(self, start_time_value):
        try:
            if start_time_value is None or start_time_value < 0:
                raise ValueError
        except ValueError:
            self.ffmpeg_args['-ss'] = None
        else:
            self.ffmpeg_args['-ss'] = str(start_time_value)

    @property
    def trim_duration(self):
        try:
            trim_duration = self.ffmpeg_args['-to']
            trim_duration_value = float(trim_duration)
        except TypeError:
            return None
        else:
            return float(trim_duration_value)

    @trim_duration.setter
    def trim_duration(self, trim_duration_value):
        try:
            if trim_duration_value is None:
                raise ValueError
        except ValueError:
            self.ffmpeg_args['-to'] = None
        else:
            self.ffmpeg_args['-to'] = str(trim_duration_value)
