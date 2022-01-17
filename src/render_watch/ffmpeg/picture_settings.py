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


import re

from render_watch.ffmpeg.subtitles_settings import SubtitlesSettings


class PictureSettings:
    """
    Stores all picture settings.
    """

    def __init__(self):
        self._ffmpeg_args = {
            '-filter_complex': None
        }
        self.crop_arg = None
        self.scale_arg = None
        self.auto_crop_enabled = False
        self.subtitles_settings = None

    @property
    def scale(self):
        """
        Returns scale as a tuple of ints.
        """
        if self.scale_arg:
            scale = re.search('\d+:\d+', self.scale_arg).group()
            width, height = scale.split(':')
            return int(width), int(height)
        return None

    @scale.setter
    def scale(self, dimensions):
        """
        Stores dimensions tuple as a string.
        """
        if dimensions is None:
            self.scale_arg = None
        else:
            width, height = dimensions
            scale_arg = 'scale=' + str(width) + ':' + str(height)
            self.scale_arg = scale_arg

    def get_scale_nvenc_args(self):
        """
        Returns npp scale args as a list.
        """
        if 'scale' in self._ffmpeg_args:
            width, height = self.scale
            nvenc_scale_arg = 'scale_npp=' + str(width) + ':' + str(height)
            return ['-vf', nvenc_scale_arg]
        return []

    @property
    def crop(self):
        """
        Returns crop as a tuple of ints.
        """
        if self.crop_arg:
            crop = re.search('\d+:\d+:\d+:\d+', self.crop_arg).group()
            width, height, x, y = crop.split(':')
            return int(width), int(height), int(x), int(y)
        return None

    @crop.setter
    def crop(self, crop_parameters):
        """
        Stores crop parameters tuple as a string.
        """
        if crop_parameters is None:
            self.crop_arg = None
        else:
            width, height, x, y = crop_parameters
            crop_arg = 'crop=' + str(width) + ':' + str(height) + ':' + str(x) + ':' + str(y)
            self.crop_arg = crop_arg

    @property
    def ffmpeg_args(self):
        self._ffmpeg_args['-map'] = self.subtitles_settings.ffmpeg_args['-map']

        if self.subtitles_settings.burn_in_stream_index is not None:
            if self.crop and self.scale:
                width, height = self.scale
                burn_in_index = self.subtitles_settings.burn_in_stream_index
                sub_scale_arg = '[0:' + str(burn_in_index) + ']scale=' + str(width) + ':' + str(height)

                filter_arg = self.crop_arg + '[crop];'
                filter_arg += '[crop]' + self.scale_arg + '[scale];'
                filter_arg += sub_scale_arg + '[sub];'
                filter_arg += '[scale][sub]overlay'
            elif self.crop:
                width, height, x, y = self.crop
                burn_in_index = self.subtitles_settings.burn_in_stream_index
                sub_scale_arg = '[0:' + str(burn_in_index) + ']scale=' + str(width) + ':' + str(height)

                filter_arg = self.crop_arg + '[crop];'
                filter_arg += sub_scale_arg + '[sub];'
                filter_arg += '[crop][sub]overlay'
            elif self.scale:
                width, height = self.scale
                burn_in_index = self.subtitles_settings.burn_in_stream_index
                sub_scale_arg = '[0:' + str(burn_in_index) + ']scale=' + str(width) + ':' + str(height)

                filter_arg = self.scale_arg + '[scale];'
                filter_arg += sub_scale_arg + '[sub];'
                filter_arg += '[scale][sub]overlay'
            else:
                burn_in_index = self.subtitles_settings.burn_in_stream_index

                filter_arg = '[0:' + str(burn_in_index) + ']' + 'overlay'
        else:
            if self.crop and self.scale:
                filter_arg = self.crop_arg + '[crop];'
                filter_arg += '[crop]' + self.scale_arg
            elif self.crop:
                filter_arg = self.crop_arg
            elif self.scale:
                filter_arg = self.scale_arg
            else:
                filter_arg = None

        self._ffmpeg_args['-filter_complex'] = filter_arg
        self._ffmpeg_args['-c:s'] = self.subtitles_settings.ffmpeg_args['-c:s']
        return self._ffmpeg_args

    @ffmpeg_args.setter
    def ffmpeg_args(self, ffmpeg_args):
        self._ffmpeg_args = ffmpeg_args

    def setup_subtitles_settings(self, input_file_info):
        self.subtitles_settings = SubtitlesSettings(input_file_info)
