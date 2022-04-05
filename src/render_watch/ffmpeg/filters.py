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


import re

from render_watch.ffmpeg import input


class Crop:
    """Class that configures all necessary crop options for Render Watch."""

    def __init__(self):
        """Initializes the Crop class with all necessary variables for the crop option."""
        self.auto_crop_enabled = False
        self.ffmpeg_args = None

    @property
    def dimensions(self) -> tuple:
        """
        Returns the dimensions of the crop option.

        Returns:
            Tuple that contains the width, height, x padding, and y padding respectively.
        """
        if self.ffmpeg_args:
            crop = re.search(r'\d+:\d+:\d+:\d+', self.ffmpeg_args).group()
            width, height, x, y = crop.split(':')

            return int(width), int(height), int(x), int(y)
        return ()

    @dimensions.setter
    def dimensions(self, dimensions_tuple: tuple | None):
        """
        Sets the dimensions for the crop option.

        Parameters:
            dimensions_tuple: Tuple that represents the width, height, x padding, and y padding respectively.

        Returns:
            None
        """
        if dimensions_tuple is None:
            self.ffmpeg_args = None
        else:
            width, height, x, y = dimensions_tuple
            crop_arg = 'crop=' + str(width) + ':' + str(height) + ':' + str(x) + ':' + str(y)
            self.ffmpeg_args = crop_arg


class Scale:
    """Class that configures all necessary scale options for Render Watch."""

    def __init__(self):
        """Initializes the Scale class with all necessary variables for the scale option."""
        self.ffmpeg_args = None

    @property
    def dimensions(self) -> tuple:
        """
        Returns the dimensions of the scale option.

        Returns:
            Tuple that contains the width and height respectively.
        """
        if self.ffmpeg_args:
            scale = re.search(r'\d+:\d+', self.ffmpeg_args).group()
            width, height = scale.split(':')

            return int(width), int(height)
        return ()

    @dimensions.setter
    def dimensions(self, dimensions_tuple: tuple | None):
        """
        Sets the dimensions for the scale option.

        Parameters:
            dimensions_tuple: Tuple that represents the width and height respectively.

        Returns:
            None
        """
        if dimensions_tuple is None:
            self.ffmpeg_args = None
        else:
            width, height = dimensions_tuple
            scale_arg = 'scale=' + str(width) + ':' + str(height)
            self.ffmpeg_args = scale_arg

    def get_scale_nvenc_arg(self) -> str:
        """
        Returns the scale ffmpeg argument that uses NPP instead of the CPU.

        Returns:
            String that represents the NPP scale ffmpeg argument.
        """
        if self.dimensions:
            width, height = self.dimensions

            return 'scale_npp=' + str(width) + ':' + str(height)
        return ''


class Subtitles:
    """Class that configures all necessary subtitle options for Render Watch."""

    def __init__(self, input_file: input.InputFile):
        """Initializes the Subtitles class with all necessary variables for the subtitles option."""
        self.subtitle_streams = input_file.subtitle_streams
        self.streams_available = []
        self.streams_available.extend(self.subtitle_streams)
        self.streams_in_use = []
        self._subtitle_args = {}
        self.burn_in_stream_index = None

    def use_stream(self, subtitle_stream: input.SubtitleStream):
        """
        Adds the subtitle stream to the list of streams to use and removes it from the list of available streams.

        Returns:
            None
        """
        self.streams_available.remove(subtitle_stream)
        self.streams_in_use.append(subtitle_stream)

    def remove_stream(self, subtitle_stream: input.SubtitleStream):
        """
        Removes the subtitle stream from the list of streams to use and adds it to the list of available streams.

        Returns:
            None
        """
        self.streams_in_use.remove(subtitle_stream)
        self.streams_available.append(subtitle_stream)

    def set_stream_method_burn_in(self, subtitle_stream: input.SubtitleStream):
        """
        Sets the burn in subtitle stream index as the subtitle stream's index.

        Returns:
            None
        """
        self.burn_in_stream_index = subtitle_stream.index

    @property
    def ffmpeg_args(self) -> dict:
        """
        Returns the ffmpeg arguments that reflect the subtitle streams that are being used.

        Returns:
            Dictionary that represents the argument (key) and it's setting (item).
        """
        self._generate_map_args()
        self._generate_subtitle_args()

        return self._subtitle_args

    def _generate_map_args(self):
        # Returns the ffmpeg map arguments for each subtitle stream in use.
        map_args = []

        for subtitle_stream in self.streams_in_use:
            if subtitle_stream.index == self.burn_in_stream_index:
                continue

            map_args.append('0:' + str(subtitle_stream.index))

        self._subtitle_args['-map'] = map_args

    def _generate_subtitle_args(self):
        # Returns the subtitle codec ffmpeg argument if there are any subtitle streams being used.
        if self._subtitle_args['-map']:
            self._subtitle_args['-c:s'] = 'copy'
        else:
            self._subtitle_args['-c:s'] = None


class Deinterlace:
    """Class that configures all necessary deinterlace options for Render Watch."""

    YADIF = 'yadif'
    BOB_WEAVER = 'bwdif'
    EDGE_SLOPE = 'estdif'
    KERNEL = 'kerndeint'
    BLEND = 'linblenddeint'
    INTERP = 'linipoldeint'
    CUBIC = 'cubicipoldeint'
    MEDIAN = 'mediandeint'
    FFMPEG = 'ffmpegdeint'
    WESTON = 'w3fdif'

    DEINT_FILTERS = (YADIF, BOB_WEAVER, EDGE_SLOPE, KERNEL, BLEND, INTERP, CUBIC, MEDIAN, FFMPEG, WESTON)
    DEINT_FILTERS_LENGTH = len(DEINT_FILTERS)

    def __init__(self):
        """Initializes the Deinterlace class with all necessary variables for the deinterlace option."""
        self._method = None

    @property
    def method(self) -> int:
        """
        Returns deinterlace method that's being used.

        Returns:
            Deinterlace option as an index using the DEINT_FILTERS variable.
        """
        if self._method in Deinterlace.DEINT_FILTERS:
            return Deinterlace.DEINT_FILTERS.index(self._method)
        return 0

    @method.setter
    def method(self, method_index: int | None):
        """
        Sets the deinterlace method option.

        Parameters:
            method_index: Index from the DEINT_FILTERS variable.

        Returns:
            None
        """
        if method_index and 0 < method_index < Deinterlace.DEINT_FILTERS_LENGTH:
            self._method = Deinterlace.DEINT_FILTERS[method_index]
        else:
            self._method = None


class Filter:
    """Class that configures all necessary filter options for Render Watch."""

    CROP_TAG = '[crop]'
    SCALE_TAG = '[scale]'
    DEINT_TAG = '[deint]'
    SUBTITLE_TAG = '[sub]'

    def __init__(self, input_file: input.InputFile):
        """Initializes the Filter class with all necessary variables for the filter options."""
        self._crop = None
        self._scale = None
        self._subtitles = Subtitles(input_file)
        self._deinterlace = None
        self.ffmpeg_args = {
            '-filter_complex': None
        }

    @property
    def crop(self) -> Crop:
        """
        Returns the crop settings object.

        Returns:
            Crop object that contains the crop settings.
        """
        return self._crop

    @crop.setter
    def crop(self, crop_settings: Crop | None):
        """
        Sets the crop settings object to use.

        Parameters:
            crop_settings: Crop settings object.

        Returns:
            None
        """
        self._crop = crop_settings
        self.update_args()

    def is_crop_enabled(self) -> bool:
        """
        Returns whether any crop settings have been enabled.

        Returns:
            Boolean that represents if any crop settings are enabled.
        """
        return (self.crop is not None) and (self.crop.dimensions is not None)

    @property
    def scale(self) -> Scale:
        """
        Returns the scale settings object.

        Returns:
            Scale object that contains the scale settings.
        """
        return self._scale

    @scale.setter
    def scale(self, scale_settings: Scale | None):
        """
        Sets the scale settings object to use.

        Parameters:
            scale_settings: Scale settings object.

        Returns:
            None
        """
        self._scale = scale_settings
        self.update_args()

    def is_scale_enabled(self) -> bool:
        """
        Returns whether any scale settings have been enabled.

        Returns:
            Boolean that represents if any scale settings are enabled.
        """
        return (self.scale is not None) and (self.scale.dimensions is not None)

    @property
    def subtitles(self) -> Subtitles:
        """
        Returns the subtitle settings object.

        Returns:
            Subtitles object that contains the subtitle settings.
        """
        return self._subtitles

    @subtitles.setter
    def subtitles(self, subtitles_settings: Subtitles | None):
        """
        Sets the subtitles settings object to use.

        Parameters:
            subtitles_settings: Subtitles settings object.

        Returns:
            None
        """
        self._subtitles = subtitles_settings
        self.update_args()

    @property
    def deinterlace(self) -> Deinterlace:
        """
        Returns the deinterlace settings object.

        Returns:
            Deinterlace object that contains the deinterlace settings.
        """
        return self._deinterlace

    @deinterlace.setter
    def deinterlace(self, deinterlace_settings: Deinterlace | None):
        """
        Sets the deinterlace settings object to use.

        Parameters:
            deinterlace_settings: Deinterlace settings object.

        Returns:
            None
        """
        self._deinterlace = deinterlace_settings
        self.update_args()

    def is_deinterlace_enabled(self) -> bool:
        """
        Returns whether any deinterlace settings have been enabled.

        Returns:
            Boolean that represents if any deinterlace settings are enabled.
        """
        return (self.deinterlace is not None) and (self.deinterlace.method is not None)

    def update_args(self):
        """
        Updates the ffmpeg arguments with the current filter settings. This includes crop, scale, subtitles,
        and deinterlace settings

        Returns:
            None
        """
        filter_args = self._get_filter_arg()
        self.ffmpeg_args['-filter_complex'] = ''.join(['\"', filter_args, '\"'])

        subtitle_args = self.subtitles.ffmpeg_args
        self.ffmpeg_args['-map'] = subtitle_args['-map']
        self.ffmpeg_args['-c:s'] = subtitle_args['-c:s']

    def _get_filter_arg(self) -> str:
        # Returns a string that represents the ffmpeg argument for all the filter settings.
        deint_arg, next_tag = self._get_deinterlace_arg()
        crop_arg, next_tag = self._get_crop_arg(next_tag)
        scale_arg, next_tag = self._get_scale_arg(next_tag)
        subtitle_arg = self._get_subtitle_arg()
        overlay_arg = self._get_overlay_arg(subtitle_arg, next_tag)

        return ''.join(filter(None, [deint_arg, crop_arg, scale_arg, subtitle_arg, overlay_arg]))

    def _get_deinterlace_arg(self) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the deinterlace settings.
        if self.is_deinterlace_enabled():
            return self.deinterlace.method, self.DEINT_TAG
        return '', ''

    def _get_crop_arg(self, next_tag) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the crop settings.
        if self.is_crop_enabled():
            if next_tag:
                next_tag = ''.join([next_tag, ';', next_tag])
            crop_arg = ''.join([next_tag, self.crop.ffmpeg_args])

            return crop_arg, self.CROP_TAG
        return '', next_tag

    def _get_scale_arg(self, next_tag) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the scale settings.
        if self.is_scale_enabled():
            if next_tag:
                next_tag = ''.join([next_tag, ';', next_tag])
            scale_arg = ''.join([next_tag, self.scale.ffmpeg_args])

            return scale_arg, self.SCALE_TAG
        return '', next_tag

    def _get_subtitle_arg(self) -> str:
        # Returns a string for the ffmpeg argument for the subtitle settings.
        if self.subtitles.burn_in_stream_index is not None:
            burn_in_index = self.subtitles.burn_in_stream_index
            subtitle_arg = ''.join(['[0:', str(burn_in_index), ']'])

            if self.is_scale_enabled():
                return ''.join([subtitle_arg, self.scale.ffmpeg_args, self.SUBTITLE_TAG])
            elif self.is_crop_enabled():
                width, height, x, y = self.crop.dimensions

                return ''.join([subtitle_arg, 'scale=', str(width), ':', str(height), self.SUBTITLE_TAG])
        return ''

    def _get_overlay_arg(self, subtitle_arg, next_tag) -> str:
        # Returns a string for the ffmpeg argument for the filter overlay setting.
        if subtitle_arg:
            if next_tag:
                return ''.join([next_tag, self.SUBTITLE_TAG, 'overlay'])
            else:
                return ''.join([subtitle_arg, 'overlay'])
        return ''
