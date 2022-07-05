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


class GeneralSettings:
    """Class that configures all general settings available for Render Watch."""

    FRAME_RATE = ('23.98', '24', '25', '29.97', '30', '50', '59.94', '60')
    FRAME_RATE_LENGTH = len(FRAME_RATE)

    def __init__(self):
        """Initializes the GeneralSettings class with all necessary variables the general options."""
        self.ffmpeg_args = {}

    @property
    def frame_rate(self) -> int | None:
        """
        Returns the frame rate option's index.

        Returns:
            Frame rate option as an index using the FRAME_RATE variable.
        """
        if '-r' in self.ffmpeg_args:
            frame_rate_arg = self.ffmpeg_args['-r']

            return GeneralSettings.FRAME_RATE.index(frame_rate_arg)
        return None

    @frame_rate.setter
    def frame_rate(self, frame_rate_index: int | None):
        """
        Sets the frame rate option.

        Parameters:
            frame_rate_index: Index from the FRAME_RATE variable.

        Returns:
            None
        """
        if frame_rate_index is not None and 0 <= frame_rate_index < GeneralSettings.FRAME_RATE_LENGTH:
            self.ffmpeg_args['-r'] = GeneralSettings.FRAME_RATE[frame_rate_index]
        else:
            self.ffmpeg_args.pop('-r', 0)

    @property
    def fast_start(self) -> bool:
        """
        Returns what the fast start option is set to.

        Returns:
            Fast start option as a boolean.
        """
        if '-movflags' in self.ffmpeg_args:
            return self.ffmpeg_args['-movflags'] == 'faststart'
        return False

    @fast_start.setter
    def fast_start(self, is_fast_start_enabled: bool):
        """
        Sets the fast start option.

        Parameters:
            is_fast_start_enabled: Boolean value to set the fast start option to.

        Returns:
            None
        """
        if is_fast_start_enabled:
            self.ffmpeg_args['-movflags'] = 'faststart'
        else:
            self.ffmpeg_args.pop('-movflags', 0)
