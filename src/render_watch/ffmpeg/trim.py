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


class TrimSettings:
    def __init__(self):
        self.ffmpeg_args = {}

    @property
    def start_time(self) -> float | None:
        if '-ss' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-ss'])
        return None

    @start_time.setter
    def start_time(self, start_time_in_seconds: int | None):
        if start_time_in_seconds:
            self.ffmpeg_args['-ss'] = str(start_time_in_seconds)
        else:
            self.ffmpeg_args.pop('-ss', 0)

    @property
    def trim_duration(self) -> float | None:
        if '-to' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-to'])
        return None

    @trim_duration.setter
    def trim_duration(self, trim_duration_in_seconds):
        if trim_duration_in_seconds is None:
            self.ffmpeg_args.pop('-to', 0)
        else:
            self.ffmpeg_args['-to'] = str(trim_duration_in_seconds)
