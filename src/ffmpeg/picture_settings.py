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


class PictureSettings:
    def __init__(self):
        self.ffmpeg_args = {
            '-s': None,
            '-filter:v': None
        }
        self.auto_crop = False

    @property
    def scale(self):
        scale = self.ffmpeg_args['-s']

        if scale is None:
            return None

        width, height = scale.split('x')

        return int(width), int(height)

    @scale.setter
    def scale(self, dimensions):
        try:
            if dimensions is None:
                raise ValueError

            width, height = dimensions
        except ValueError:
            self.ffmpeg_args['-s'] = None
        else:
            self.ffmpeg_args['-s'] = str(width) + 'x' + str(height)

    @property
    def crop(self):
        crop = self.ffmpeg_args['-filter:v']

        if crop is None:
            return None

        width, height, x, y = crop.split('=')[1].split(':')

        return int(width), int(height), int(x), int(y)

    @crop.setter
    def crop(self, crop_parameters):
        try:
            if crop_parameters is None:
                raise ValueError

            width, height, x, y = crop_parameters
            crop_arg = 'crop=' + str(width) + ':' + str(height) + ':' + str(x) + ':' + str(y)
        except ValueError:
            self.ffmpeg_args['-filter:v'] = None
        else:
            self.ffmpeg_args['-filter:v'] = crop_arg
