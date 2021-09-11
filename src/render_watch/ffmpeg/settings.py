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


import copy
import logging

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.picture_settings import PictureSettings
from render_watch.helpers.nvidia_helper import NvidiaHelper


class Settings:
    """Manages all ffmpeg settings.

    This includes input file, output file, picture settings, trim settings,
    video codec settings, and audio codec settings.
    """

    VALID_INPUT_CONTAINERS = ('mp4', 'mkv', 'm4v', 'avi', 'ts', 'm2ts', 'mpg', 'vob', 'VOB', 'mov', 'webm', 'wmv')
    FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-loglevel', 'quiet', '-stats', "-y"]
    FFMPEG_INIT_AUTO_CROP_ARGS = ['ffmpeg', '-hide_banner', '-y']
    FFPROBE_ARGS = [
        'ffprobe', '-hide_banner', '-loglevel', 'warning', '-show_entries',
        'stream=codec_name,codec_type,width,height,r_frame_rate,bit_rate,channels,sample_rate,index:format=duration'
    ]
    FFPLAY_INIT_ARGS = ['ffplay']
    FFMPEG_CONCATENATION_INIT_ARGS = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i']
    VIDEO_COPY_ARGS = ('-c:v', 'copy')
    AUDIO_COPY_ARGS = ('-c:a', 'copy')
    AUDIO_NONE_ARG = '-an'
    VIDEO_NONE_ARG = '-vn'
    RAW_VIDEO_ARGS = ('-f', 'rawvideo')
    VSYNC_ARGS = ('-vsync', '0')
    NVDEC_ARGS = ('-hwaccel', 'nvdec')
    NVDEC_OUT_FORMAT_ARGS = ('-hwaccel_output_format', 'cuda')

    def __init__(self):
        self.input_file_info = {
            'filename': None,
            'resolution': None,
            'width': None,
            'height': None,
            'fps': None,
            'duration': None,
            'file_size': None,
            'codec_video': None,
            'codec_audio': None,
            'channels': None,
            'sample_rate': None,
            'video_streams': None,
            'audio_streams': None,
            'subtitle_streams': None
        }
        self.no_audio = False
        self.no_video = False
        self.video_chunk = False
        self._folder_state = False
        self.recursive_folder = False
        self.watch_folder = False
        self.folder_auto_crop = False
        self._temp_file_name = None
        self._input_file_path = None
        self.output_directory = None
        self.video_settings = None
        self.audio_settings = None
        self.video_stream_index = None
        self.audio_stream_index = None
        self._picture_settings = PictureSettings()
        self.trim_settings = None
        self._general_settings = GeneralSettings()
        self.input_container = None
        self._output_container = None

    @property
    def input_file(self):
        """Returns input's absolute file path."""
        return self._input_file_path

    @input_file.setter
    def input_file(self, input_file):
        """Sets input's file path and configures the file name and input container variables."""
        self._input_file_path = input_file
        self.filename = self._parse_input_file_name(input_file)
        self.input_container = self._parse_input_file_extension(input_file)

    @staticmethod
    def _parse_input_file_name(input_file_path):
        # Gets the file name from the given file path
        file_name_splits = input_file_path.split('/')[-1].split('.')[:-1]
        file_name = ''
        for name_split in file_name_splits:
            file_name += name_split
        return file_name

    @staticmethod
    def _parse_input_file_extension(input_file_path):
        # Gets the input's file extension from the given file path.
        file_container = 'N/A'
        try:
            file_container = input_file_path.split('/')[-1].split('.')[-1]
        finally:
            return file_container

    def input_folder(self, input_dir):
        """Sets a folder as the input instead of a file.

        :param input_dir:
            Input's absolute path.
        """
        self._input_file_path = input_dir
        self.filename = input_dir.split('/')[-1]
        self.input_container = 'N/A'
        self._folder_state = True

    @property
    def folder_state(self):
        return self._folder_state

    @property
    def temp_file_name(self):
        return self._temp_file_name

    @temp_file_name.setter
    def temp_file_name(self, name):
        self._temp_file_name = name

    @property
    def picture_settings(self):
        return self._picture_settings

    @picture_settings.setter
    def picture_settings(self, settings):
        if not settings:
            logging.error('--- CANNOT SET PICTURE SETTINGS TO NONE ---')
            raise ValueError()

        self._picture_settings = settings

    @property
    def general_settings(self):
        return self._general_settings

    @general_settings.setter
    def general_settings(self, settings):
        if not settings:
            logging.error('--- CANNOT SET GENERAL SETTINGS TO NONE ---')
            raise ValueError()

        self._general_settings = settings

    @property
    def output_container(self):
        if self._output_container is None:
            return '.' + self.input_container
        else:
            return self._output_container

    @output_container.setter
    def output_container(self, container):
        self._output_container = container

    def is_output_container_set(self):
        return self.output_container in GeneralSettings.CONTAINERS_UI_LIST

    @property
    def filename(self):
        return self.input_file_info['filename']

    @filename.setter
    def filename(self, name):
        self.input_file_info['filename'] = name

    @property
    def resolution_origin(self):
        return self.input_file_info['resolution']

    @resolution_origin.setter
    def resolution_origin(self, dimensions):
        width, height = dimensions
        self.input_file_info['resolution'] = str(width) + 'x' + str(height)

    @property
    def width_origin(self):
        return self.input_file_info['width']

    @width_origin.setter
    def width_origin(self, value):
        self.input_file_info['width'] = value

    @property
    def height_origin(self):
        return self.input_file_info['height']

    @height_origin.setter
    def height_origin(self, value):
        self.input_file_info['height'] = value

    @property
    def framerate_origin(self):
        return self.input_file_info['fps']

    @framerate_origin.setter
    def framerate_origin(self, value):
        self.input_file_info['fps'] = value

    @property
    def duration_origin(self):
        return self.input_file_info['duration']

    @duration_origin.setter
    def duration_origin(self, value):
        self.input_file_info['duration'] = value

    @property
    def file_size(self):
        return self.input_file_info['file_size']

    @file_size.setter
    def file_size(self, value):
        self.input_file_info['file_size'] = value

    @property
    def codec_video_origin(self):
        return self.input_file_info['codec_video']

    @codec_video_origin.setter
    def codec_video_origin(self, name):
        self.input_file_info['codec_video'] = name

    @property
    def codec_audio_origin(self):
        return self.input_file_info['codec_audio']

    @codec_audio_origin.setter
    def codec_audio_origin(self, name):
        self.input_file_info['codec_audio'] = name

    @property
    def audio_channels_origin(self):
        return self.input_file_info['channels']

    @audio_channels_origin.setter
    def audio_channels_origin(self, value):
        self.input_file_info['channels'] = value

    @property
    def audio_sample_rate_origin(self):
        return self.input_file_info['sample_rate']

    @audio_sample_rate_origin.setter
    def audio_sample_rate_origin(self, value):
        self.input_file_info['sample_rate'] = value

    def get_args(self, cmd_args_enabled=False):
        """Returns ffmpeg arguments with all settings applied.

        :param cmd_args_enabled:
            (Default False) Generates arguments that can be directly copy/pasted into a terminal.
        """
        ffmpeg_args = self.FFMPEG_INIT_ARGS.copy()

        self._apply_trim_start_args(ffmpeg_args)
        self._apply_nvdec_args(ffmpeg_args)
        self._apply_input_file_args(ffmpeg_args, cmd_args_enabled)
        self._apply_map_args(ffmpeg_args)
        self._apply_video_settings_args(ffmpeg_args)
        self._apply_audio_settings_args(ffmpeg_args)
        self._apply_picture_settings_args(ffmpeg_args)
        self._apply_general_settings_args(ffmpeg_args)
        self._apply_trim_settings_args(ffmpeg_args)
        self._apply_output_file_args(ffmpeg_args, cmd_args_enabled)
        self._apply_2pass_args(ffmpeg_args)

        return ffmpeg_args

    def _apply_map_args(self, ffmpeg_args):
        # Applies the ffmpeg "-map" option.
        if self.video_stream_index is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:' + str(self.video_stream_index))

        if self.audio_stream_index is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:' + str(self.audio_stream_index))

    def _apply_trim_start_args(self, ffmpeg_args):
        # Applies the ffmpeg "-ss" option.
        if self.trim_settings is not None:
            ffmpeg_args.append('-ss')
            ffmpeg_args.append(self.trim_settings.ffmpeg_args['-ss'])

    def _apply_nvdec_args(self, ffmpeg_args):
        # Applies the NVDEC options.
        if self.is_video_settings_nvenc() and NvidiaHelper.is_nvdec_supported():
            ffmpeg_args.extend(self.NVDEC_ARGS)
            if self.picture_settings.crop is None:
                ffmpeg_args.extend(self.NVDEC_OUT_FORMAT_ARGS)

    def _apply_input_file_args(self, ffmpeg_args, cmd_args_enabled):
        # Applies the ffmpeg "-i" option.
        ffmpeg_args.append('-i')

        input_file_path = self.input_file
        if cmd_args_enabled:
            input_file_path = '\"' + input_file_path + '\"'
        ffmpeg_args.append(input_file_path)

    def _apply_video_settings_args(self, ffmpeg_args):
        # Applies the video codec's ffmpeg settings
        if self.video_settings is not None:
            ffmpeg_args.extend(self._generate_video_settings_args())
            ffmpeg_args.extend(self._generate_advanced_video_settings_args())
        elif self.no_video:
            ffmpeg_args.append(self.VIDEO_NONE_ARG)
        else:
            ffmpeg_args.extend(self.VIDEO_COPY_ARGS)

    def _generate_video_settings_args(self):
        args = []
        for setting, arg in self.video_settings.ffmpeg_args.items():
            if arg is not None:
                args.append(setting)
                args.append(arg)
        return args

    def _generate_advanced_video_settings_args(self):
        args = []
        for setting, arg in self.video_settings.get_ffmpeg_advanced_args().items():
            if arg is not None:
                args.append(setting)
                args.append(arg)
        return args

    def _apply_audio_settings_args(self, ffmpeg_args):
        # Applies the audio codec's ffmpeg options
        if self.audio_settings is not None and not self.is_video_settings_2_pass():
            ffmpeg_args.extend(self._generate_audio_settings_args())
        elif self.no_audio or self.is_video_settings_2_pass():
            ffmpeg_args.append(self.AUDIO_NONE_ARG)
        else:
            ffmpeg_args.extend(self.AUDIO_COPY_ARGS)

    def _generate_audio_settings_args(self):
        args = []
        for setting, arg in self.audio_settings.ffmpeg_args.items():
            if arg is not None:
                args.append(setting)
                args.append(arg)
        return args

    def _apply_picture_settings_args(self, ffmpeg_args):
        # Applies all ffmpeg picture options.
        if self.video_settings is not None and not self.no_video:
            ffmpeg_args.extend(self._generate_picture_settings_args())

    def _generate_picture_settings_args(self):
        args = []
        if self.is_video_settings_nvenc() and NvidiaHelper.is_npp_supported() and self.picture_settings.crop is None:
            args.extend(self.picture_settings.get_scale_nvenc_args())
        else:
            for setting, arg in self.picture_settings.ffmpeg_args.items():
                if arg is not None:
                    args.append(setting)
                    args.append(arg)
        return args

    def _apply_general_settings_args(self, ffmpeg_args):
        # Applies all general ffmpeg options for container settings and frame rate settings.
        if not self.no_video:
            ffmpeg_args.extend(self._generate_general_settings_args())

    def _generate_general_settings_args(self):
        args = []
        for setting, arg in self.general_settings.ffmpeg_args.items():
            if arg is not None:
                args.append(setting)
                args.append(arg)
        return args

    def _apply_trim_settings_args(self, ffmpeg_args):
        # Applies the trim relates ffmpeg options.
        if self.trim_settings is not None:
            ffmpeg_args.append('-to')
            ffmpeg_args.append(self.trim_settings.ffmpeg_args['-to'])

    def _apply_output_file_args(self, ffmpeg_args, cmd_args_enabled):
        # Applies the ffmpeg options for setting the output file.
        if self.video_chunk:
            for arg in self.VSYNC_ARGS:
                ffmpeg_args.append(arg)

        if self.folder_state:
            output_file_path = self.output_directory
        else:
            output_file_path = self.output_directory + self.filename + self.output_container
        if cmd_args_enabled:
            output_file_path = '\"' + output_file_path + '\"'
        ffmpeg_args.append(output_file_path)

    def _apply_2pass_args(self, ffmpeg_args):
        # Applies the 2nd pass ffmpeg arguments.
        if self.is_video_settings_2_pass():
            ffmpeg_copy = self.get_copy()
            ffmpeg_copy.video_settings.encode_pass = 2
            ffmpeg_args.append('&&')
            ffmpeg_args.extend(ffmpeg_copy.get_args())

    def is_video_settings_x264(self):
        return self.video_settings is not None and self.video_settings.codec_name == 'libx264'

    def is_video_settings_x265(self):
        return self.video_settings is not None and self.video_settings.codec_name == 'libx265'

    def is_video_settings_vp9(self):
        return self.video_settings is not None and self.video_settings.codec_name == 'libvpx-vp9'

    def is_video_settings_nvenc(self):
        return self.video_settings is not None and not self.no_video and 'nvenc' in self.video_settings.codec_name

    def is_video_settings_2_pass(self):
        if self.video_settings is not None:
            if self.video_settings.encode_pass is not None and self.video_settings.encode_pass == 1:
                return True
        return False

    def get_copy(self):
        """Get separate copy of this ffmpeg settings object."""
        ffmpeg_copy = Settings()

        try:
            ffmpeg_copy.input_file_info = self.input_file_info.copy()
            ffmpeg_copy.input_file = self.input_file
            ffmpeg_copy.output_directory = self.output_directory
            ffmpeg_copy.filename = self.filename
            ffmpeg_copy.temp_file_name = self.temp_file_name
            ffmpeg_copy.general_settings.ffmpeg_args = self.general_settings.ffmpeg_args.copy()
            ffmpeg_copy.picture_settings.ffmpeg_args = self.picture_settings.ffmpeg_args.copy()
            ffmpeg_copy.video_stream_index = self.video_stream_index
            ffmpeg_copy.audio_stream_index = self.audio_stream_index
            ffmpeg_copy.no_video = self.no_video
            ffmpeg_copy.no_audio = self.no_audio
            ffmpeg_copy.video_chunk = self.video_chunk
            if self.is_output_container_set():
                ffmpeg_copy.output_container = self.output_container
            if self.video_settings is not None:
                ffmpeg_copy.video_settings = copy.deepcopy(self.video_settings)
            if self.audio_settings is not None:
                ffmpeg_copy.audio_settings = copy.deepcopy(self.audio_settings)
            if self.trim_settings is not None:
                ffmpeg_copy.trim_settings = copy.deepcopy(self.trim_settings)
        except:
            logging.exception('--- FAILED TO GENERATE FFMPEG SETTINGS COPY ---')
        finally:
            return ffmpeg_copy
