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


import logging
import re
import subprocess

from render_watch.ffmpeg import input
from render_watch.helpers import ffmpeg_helper
from render_watch import app_preferences


class Crop:
    """Class that configures all necessary crop options for Render Watch."""

    AUTO_CROP_SEGMENTS = 3
    AUTO_CROP_LENGTH = 15
    AUTO_CROP_THRESHOLD = 10

    def __init__(self, encoding_task, app_settings: app_preferences.Settings, autocrop=True):
        """
        Initializes the Crop class with all necessary variables for the crop option.

        Parameters:
            app_settings: Application settings.
        """
        self.auto_crop_enabled = app_settings.is_auto_cropping_inputs
        self._auto_crop_dimensions = None
        self.ffmpeg_args = None

        if self.auto_crop_enabled and autocrop:
            self.process_auto_crop(encoding_task)

    @property
    def dimensions(self) -> tuple:
        """
        Returns the dimensions of the crop option.

        Returns:
            Tuple that contains the width, height, x padding, and y padding respectively.
        """
        if self.ffmpeg_args:
            crop = re.search(r'\d+:\d+:\d+:\d+', self.ffmpeg_args).group()
            width, height, x_pad, y_pad = crop.split(':')

            return int(width), int(height), int(x_pad), int(y_pad)
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
            width, height, x_pad, y_pad = dimensions_tuple
            crop_arg = 'crop=' + str(width) + ':' + str(height) + ':' + str(x_pad) + ':' + str(y_pad)
            self.ffmpeg_args = crop_arg

    def process_auto_crop(self, encoding_task) -> bool:
        """
        Detects letterboxing for the video stream in the encoding task's video stream and removes it by
        automatically setting the crop dimensions.

        Parameters:
            encoding_task: Encoding task to use for the auto cropper.

        Returns:
            Boolean that represents whether the auto cropper was able to set the crop dimensions.
        """
        if self._auto_crop_dimensions is None:
            self._auto_crop_dimensions = [0] * self.AUTO_CROP_SEGMENTS
            subprocess_args_list = self._get_auto_crop_subprocess_args_list(encoding_task)

            if self._run_auto_crop_subprocess(subprocess_args_list):
                return False

        if self._is_auto_crop_dimensions_valid(encoding_task):
            self.dimensions = self._auto_crop_dimensions

            return True
        return False

    def _get_auto_crop_subprocess_args_list(self, encoding_task) -> list:
        # Returns a list of subprocess args for each split of the encoding task.
        subprocess_args_list = []

        for index in range(1, self.AUTO_CROP_SEGMENTS + 1):
            subprocess_args = self._get_auto_crop_subprocess_args(encoding_task, index)
            subprocess_args_list.append(subprocess_args)

        return subprocess_args_list

    def _get_auto_crop_subprocess_args(self, encoding_task, segment_count: int):
        # Returns subprocess args for detecting letterboxing in the encoding task's video stream.
        start_time = self._get_auto_crop_subprocess_start_time(encoding_task, segment_count)

        subprocess_args = ffmpeg_helper.FFMPEG_INIT_AUTO_CROP_ARGS.copy()
        subprocess_args.append('-ss')
        subprocess_args.append(str(start_time))
        subprocess_args.append('-i')
        subprocess_args.append(encoding_task.input_file.file_path)
        subprocess_args.append('-map')
        subprocess_args.append('0:' + str(encoding_task.video_stream.index))
        subprocess_args.append('-an')
        subprocess_args.append('-vframes')
        subprocess_args.append(str(self.AUTO_CROP_LENGTH))
        subprocess_args.append('-vf')
        subprocess_args.append('cropdetect')
        subprocess_args.append('-f')
        subprocess_args.append('null')
        subprocess_args.append('-')

        return subprocess_args

    def _get_auto_crop_subprocess_start_time(self, encoding_task, segment_count: int):
        time_split_length = encoding_task.input_file.duration / (self.AUTO_CROP_SEGMENTS + 1)

        return round(time_split_length * segment_count, 2)

    def _run_auto_crop_subprocess(self, subprocess_args_list: list) -> int:
        # Runs the subprocess for the auto crop and checks stdout for auto crop values.
        for index, subprocess_args in enumerate(subprocess_args_list):
            with subprocess.Popen(subprocess_args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as auto_crop_subprocess:
                while True:
                    stdout = auto_crop_subprocess.stdout.readline().strip()
                    if stdout == '' and auto_crop_subprocess.poll() is not None:
                        break

                    stdout_last_line = stdout

                    try:
                        crop_values = re.search(r'crop=\d+:\d+:\d+:\d+', stdout)
                        if crop_values:
                            self._set_crop_values(crop_values.group().split('=')[-1], index)
                    except (TypeError, AttributeError, ValueError):
                        continue

                if auto_crop_subprocess.poll():
                    logging.error(''.join(['--- AUTO CROP FAILED ---\n',
                                           stdout_last_line,
                                           '\n\n',
                                           str(subprocess_args)]))

                    break

        self._set_best_auto_crop_dimension()

        return auto_crop_subprocess.wait()

    def _set_crop_values(self, crop_values: str, index: int):
        # Sets crop values for the tuple at the specified index if the values are greater than existing values.
        width, height, x_pad, y_pad = crop_values.split(':')
        width = int(width)
        height = int(height)
        x_pad = int(x_pad)
        y_pad = int(y_pad)

        if self._auto_crop_dimensions[index]:
            width_origin, height_origin, x_pad_origin, y_pad_origin = self._auto_crop_dimensions[index]

            if width > width_origin or height > height_origin or x_pad < x_pad_origin or y_pad < y_pad_origin:
                self._auto_crop_dimensions[index] = (width, height, x_pad, y_pad)
        else:
            self._auto_crop_dimensions[index] = (width, height, x_pad, y_pad)

    def _set_best_auto_crop_dimension(self):
        # Uses the highest auto crop dimensions in the tuple of auto crop dimensions.
        self._auto_crop_dimensions = max(self._auto_crop_dimensions)

    def _is_auto_crop_dimensions_valid(self, encoding_task) -> bool:
        # Determines whether the auto crop dimensions can be used for the crop dimensions.
        width, height, x_pad, y_pad = self._auto_crop_dimensions

        try:
            is_width_valid = ((int(width) + self.AUTO_CROP_THRESHOLD) < encoding_task.video_stream.width)
            is_height_valid = ((int(height) + self.AUTO_CROP_THRESHOLD) < encoding_task.video_stream.height)

            return is_width_valid or is_height_valid
        except (TypeError, ValueError):
            return False


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

        if self.burn_in_stream_index == subtitle_stream.index:
            self.burn_in_stream_index = None

    def set_stream_method_burn_in(self, subtitle_stream: input.SubtitleStream):
        """
        Sets the burn in subtitle stream index as the subtitle stream's index.

        Returns:
            None
        """
        self.burn_in_stream_index = subtitle_stream.index

    def get_stream_burn_in_index_tag(self) -> str:
        """
        Returns the filter tag that represents the burn-in stream's index.

        Returns:
            String that represents the filter tag for the burn-in stream's index.
        """
        return ''.join(['[0:', str(self.burn_in_stream_index), ']'])

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

    @property
    def ffmpeg_args(self):
        if self.method is None:
            return ''
        return self.DEINT_FILTERS[self.method]


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
            '-filter_complex': None,
            '-map': {}
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
        return (self.crop is not None) and self.crop.dimensions

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
        return (self.scale is not None) and self.scale.dimensions

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

        if filter_args:
            self.ffmpeg_args['-filter_complex'] = filter_args
        else:
            self.ffmpeg_args['-filter_complex'] = None

        subtitle_args = self.subtitles.ffmpeg_args
        self.ffmpeg_args['-map'] = subtitle_args['-map']
        self.ffmpeg_args['-c:s'] = subtitle_args['-c:s']

    def _get_filter_arg(self) -> str:
        # Returns a string that represents the ffmpeg argument for all the filter settings.
        deint_arg, next_tag = self._get_deinterlace_arg()
        crop_arg, next_tag = self._get_crop_arg(next_tag)
        scale_arg, next_tag = self._get_scale_arg(next_tag)
        subtitle_arg, subtitle_tag = self._get_subtitle_arg(next_tag)
        overlay_arg = self._get_overlay_arg(next_tag, subtitle_tag, subtitle_arg)

        return ''.join(filter(None, [deint_arg, crop_arg, scale_arg, subtitle_arg, overlay_arg]))

    def _get_deinterlace_arg(self) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the deinterlace settings.
        if self.is_deinterlace_enabled():
            return self.deinterlace.ffmpeg_args, self.DEINT_TAG
        return '', ''

    def _get_crop_arg(self, next_tag: str) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the crop settings.
        if self.is_crop_enabled():
            if next_tag:
                next_tag = ''.join([next_tag, ';', next_tag])
            crop_arg = ''.join([next_tag, self.crop.ffmpeg_args])

            return crop_arg, self.CROP_TAG
        return '', next_tag

    def _get_scale_arg(self, next_tag: str) -> tuple:
        # Returns a tuple of strings for the ffmpeg arguments for the scale settings.
        if self.is_scale_enabled():
            if next_tag:
                next_tag = ''.join([next_tag, ';', next_tag])
            scale_arg = ''.join([next_tag, self.scale.ffmpeg_args])

            return scale_arg, self.SCALE_TAG
        return '', next_tag

    def _get_subtitle_arg(self, next_tag: str) -> tuple:
        # Returns a string for the ffmpeg argument for the subtitle settings.
        if self.subtitles.burn_in_stream_index is None:
            return '', ''

        if self.is_scale_enabled():
            subtitle_arg = ''.join([next_tag,
                                    ';',
                                    self.subtitles.get_stream_burn_in_index_tag(),
                                    self.scale.ffmpeg_args])
            subtitle_tag = self.SUBTITLE_TAG
        elif self.is_crop_enabled():
            width, height, x, y = self.crop.dimensions
            subtitle_arg = ''.join([next_tag,
                                    ';',
                                    self.subtitles.get_stream_burn_in_index_tag(),
                                    'scale=',
                                    str(width),
                                    ':',
                                    str(height)])
            subtitle_tag = self.SUBTITLE_TAG
        else:
            subtitle_arg = ''
            subtitle_tag = self.subtitles.get_stream_burn_in_index_tag()

        return subtitle_arg, subtitle_tag

    @staticmethod
    def _get_overlay_arg(next_tag: str, subtitle_tag: str, subtitle_arg: str) -> str:
        # Returns a string for the ffmpeg argument for the filter overlay setting.
        if subtitle_tag:
            if subtitle_arg:
                return ''.join([subtitle_tag, ';', next_tag, subtitle_tag, 'overlay'])
            elif next_tag:
                return ''.join([next_tag, ';', next_tag, subtitle_tag, 'overlay'])
            else:
                return ''.join([subtitle_tag, 'overlay'])
        return ''
