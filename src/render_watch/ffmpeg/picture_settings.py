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


class PictureSettings:
    """
    Stores all picture settings.
    """

    def __init__(self):
        self.ffmpeg_args = {}
        self.auto_crop_enabled = False

    @property
    def scale(self):
        """
        Returns scale as a tuple of ints.
        """
        if '-s' in self.ffmpeg_args:
            width, height = self.ffmpeg_args['-s'].split('x')
            return int(width), int(height)
        return None

    @scale.setter
    def scale(self, dimensions):
        """
        Stores dimensions tuple as a string.
        """
        if dimensions is None:
            self.ffmpeg_args.pop('-s', 0)
        else:
            width, height = dimensions
            self.ffmpeg_args['-s'] = str(width) + 'x' + str(height)

    def get_scale_nvenc_args(self):
        """
        Returns npp scale args as a list.
        """
        if '-s' in self.ffmpeg_args:
            width, height = self.scale
            nvenc_scale_arg = 'scale_npp=' + str(width) + ':' + str(height)
            return ['-vf', nvenc_scale_arg]
        return []

    @property
    def crop(self):
        """
        Returns crop as a tuple of ints.
        """
        if '-filter:v' in self.ffmpeg_args:
            crop = self.ffmpeg_args['-filter:v']
            width, height, x, y = crop.split('=')[1].split(':')
            return int(width), int(height), int(x), int(y)
        return None

    @crop.setter
    def crop(self, crop_parameters):
        """
        Stores crop parameters tuple as a string.
        """
        if crop_parameters is None:
            self.ffmpeg_args.pop('-filter:v', 0)
        else:
            width, height, x, y = crop_parameters
            crop_arg = 'crop=' + str(width) + ':' + str(height) + ':' + str(x) + ':' + str(y)
            self.ffmpeg_args['-filter:v'] = crop_arg
