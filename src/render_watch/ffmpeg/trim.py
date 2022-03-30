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
    """Class that configures all trim settings available for Render Watch."""

    def __init__(self):
        """Initializes the TrimSettings class with all necessary variables for the trim options."""
        self.ffmpeg_args = {}

    @property
    def start_time(self) -> float | None:
        """
        Returns the trim start time.

        Returns:
            Trim start time as a float in seconds.
        """
        if '-ss' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-ss'])
        return None

    @start_time.setter
    def start_time(self, start_time_in_seconds: float | None):
        """
        Sets the trim start time.

        Parameters:
            start_time_in_seconds: Trim segment start time in seconds.

        Returns:
            None
        """
        if start_time_in_seconds:
            self.ffmpeg_args['-ss'] = str(round(start_time_in_seconds, 2))
        else:
            self.ffmpeg_args.pop('-ss', 0)

    @property
    def trim_duration(self) -> float | None:
        """
        Returns the trim duration.

        Returns:
            Trim duration as a float in seconds.
        """
        if '-to' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-to'])
        return None

    @trim_duration.setter
    def trim_duration(self, trim_duration_in_seconds: float | None):
        """
        Sets the trim duration.

        Parameters:
            trim_duration_in_seconds: Duration of the trim segment in seconds.

        Returns:
            None
        """
        if trim_duration_in_seconds is None:
            self.ffmpeg_args.pop('-to', 0)
        else:
            self.ffmpeg_args['-to'] = str(round(trim_duration_in_seconds, 2))
