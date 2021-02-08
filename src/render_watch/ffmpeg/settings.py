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


import copy
import logging

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.picture_settings import PictureSettings


class Settings:
    valid_input_containers = ('mp4', 'mkv', 'm4v', 'avi', 'ts', 'm2ts', 'mpg', 'vob', 'VOB', 'mov', 'webm', 'wmv')
    ffmpeg_init_args = ["ffmpeg", "-hide_banner", '-loglevel', 'quiet', '-stats', "-y"]
    ffmpeg_init_auto_crop_args = ["ffmpeg", "-hide_banner", "-y"]
    ffprobe_args = ['ffprobe', '-hide_banner', '-loglevel', 'warning', '-show_entries',
                    'stream=codec_name,codec_type,width,height,r_frame_rate,bit_rate,channels,sample_rate,index:'
                    'format=duration']
    ffplay_init_args = ['ffplay']
    ffmpeg_concatenation_init_args = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i']
    video_copy_args = ("-c:v", "copy")
    audio_copy_args = ("-c:a", "copy")
    audio_none_arg = '-an'
    video_none_arg = '-vn'
    raw_video_args = ('-f', 'rawvideo')
    vsync_args = ('-vsync', '0')
    nvdec_args = ('-hwaccel', 'nvdec')
    nvdec_out_format_args = ('-hwaccel_output_format', 'cuda')

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
        self.__folder_state = False
        self.recursive_folder = False
        self.watch_folder = False
        self.folder_auto_crop = False
        self.__temp_file_name = None
        self.__input_file_path = None
        self.output_directory = None
        self.video_settings = None
        self.audio_settings = None
        self.video_stream_index = None
        self.audio_stream_index = None
        self.__picture_settings = PictureSettings()
        self.trim_settings = None
        self.__general_settings = GeneralSettings()
        self.input_container = None
        self.__output_container = None

    @property
    def input_file(self):
        return self.__input_file_path

    @input_file.setter
    def input_file(self, input_file):
        self.__input_file_path = input_file
        self.filename = self.__parse_input_file_name(input_file)
        self.input_container = self.__parse_input_file_extension(input_file)

    @staticmethod
    def __parse_input_file_name(input_file):
        file_name_splits = input_file.split('/')[-1].split('.')[:-1]
        file_name = ''

        for name_split in file_name_splits:
            file_name += name_split

        return file_name

    @staticmethod
    def __parse_input_file_extension(input_file):
        file_container = 'N/A'

        try:
            file_container = input_file.split('/')[-1].split('.')[-1]
        finally:
            return file_container

    @input_file.setter
    def input_folder(self, input_dir):
        self.__input_file_path = input_dir
        self.filename = input_dir.split('/')[-1]
        self.input_container = 'N/A'
        self.__folder_state = True

    @property
    def folder_state(self):
        return self.__folder_state

    @property
    def temp_file_name(self):
        return self.__temp_file_name

    @temp_file_name.setter
    def temp_file_name(self, name):
        self.__temp_file_name = name

    @property
    def picture_settings(self):
        return self.__picture_settings

    @picture_settings.setter
    def picture_settings(self, settings):
        if not settings:
            logging.error('--- CANNOT SET PICTURE SETTINGS TO NONETYPE ---')
            raise ValueError('Illegal value: picture_settings cannot be set to NoneType')

        self.__picture_settings = settings

    @property
    def general_settings(self):
        return self.__general_settings

    @general_settings.setter
    def general_settings(self, settings):
        if not settings:
            logging.error('--- CANNOT SET GENERAL SETTINGS TO NONETYPE ---')
            raise ValueError('Illegal value: general_settings cannot be set to NoneType')

        self.__general_settings = settings

    @property
    def output_container(self):
        if self.__output_container is None:
            return '.' + self.input_container
        else:
            return self.__output_container

    @output_container.setter
    def output_container(self, container):
        self.__output_container = container

    def is_output_container_set(self):
        return self.output_container in GeneralSettings.video_file_containers_list

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
        resolution_arg = str(width) + 'x' + str(height)

        self.input_file_info['resolution'] = resolution_arg

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
        ffmpeg_args = self.ffmpeg_init_args.copy()

        self.__apply_trim_start_args(ffmpeg_args)
        self.__apply_nvdec_args(ffmpeg_args)
        self.__apply_input_file_args(ffmpeg_args, cmd_args_enabled)
        self.__apply_map_args(ffmpeg_args)
        self.__apply_video_settings_args(ffmpeg_args)
        self.__apply_audio_settings_args(ffmpeg_args)
        self.__apply_picture_settings_args(ffmpeg_args)
        self.__apply_general_settings_args(ffmpeg_args)
        self.__apply_trim_settings_args(ffmpeg_args)
        self.__apply_output_file_args(ffmpeg_args, cmd_args_enabled)
        self.__apply_2pass_args(ffmpeg_args)

        return ffmpeg_args

    def __apply_map_args(self, ffmpeg_args):
        if self.video_stream_index is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:' + str(self.video_stream_index))

        if self.audio_stream_index is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('0:' + str(self.audio_stream_index))

    def __apply_trim_start_args(self, ffmpeg_args):
        if self.trim_settings is not None:
            ffmpeg_args.append('-ss')
            ffmpeg_args.append(self.trim_settings.ffmpeg_args['-ss'])

    def __apply_nvdec_args(self, ffmpeg_args):
        if self.is_video_settings_nvenc():
            ffmpeg_args.extend(self.nvdec_args)

            if self.picture_settings.crop is None:
                ffmpeg_args.extend(self.nvdec_out_format_args)

    def __apply_input_file_args(self, ffmpeg_args, cmd_args_enabled):
        ffmpeg_args.append('-i')

        input_file_path = self.input_file

        if cmd_args_enabled:
            input_file_path = '\"' + input_file_path + '\"'

        ffmpeg_args.append(input_file_path)

    def __apply_video_settings_args(self, ffmpeg_args):
        if self.video_settings is not None:
            ffmpeg_args.extend(self.__generate_video_settings_args())
            ffmpeg_args.extend(self.__generate_advanced_video_settings_args())
        elif self.no_video:
            ffmpeg_args.append(self.video_none_arg)
        else:
            ffmpeg_args.extend(self.video_copy_args)

    def __generate_video_settings_args(self):
        args = []

        for key, value in self.video_settings.ffmpeg_args.items():
            if value is not None:
                args.append(key)
                args.append(value)

        return args

    def __generate_advanced_video_settings_args(self):
        args = []

        for setting, value in self.video_settings.get_ffmpeg_advanced_args().items():
            if value is not None:
                args.append(setting)
                args.append(value)

        return args

    def __apply_audio_settings_args(self, ffmpeg_args):
        if self.audio_settings is not None and not self.is_video_settings_2_pass():
            ffmpeg_args.extend(self.__generate_audio_settings_args())
        elif self.no_audio or self.is_video_settings_2_pass():
            ffmpeg_args.append(self.audio_none_arg)
        else:
            ffmpeg_args.extend(self.audio_copy_args)

    def __generate_audio_settings_args(self):
        args = []

        for key, value in self.audio_settings.ffmpeg_args.items():
            if value is not None:
                args.append(key)
                args.append(value)

        return args

    def __apply_picture_settings_args(self, ffmpeg_args):
        if self.video_settings is not None and not self.no_video:
            ffmpeg_args.extend(self.__generate_picture_settings_args())

    def __generate_picture_settings_args(self):
        args = []

        if self.is_video_settings_nvenc() and self.picture_settings.crop is None:
            args.extend(self.picture_settings.get_scale_nvenc_args())
        else:

            for key, value in self.picture_settings.ffmpeg_args.items():
                if value is not None:
                    args.append(key)
                    args.append(value)

        return args

    def __apply_general_settings_args(self, ffmpeg_args):
        if not self.no_video:
            ffmpeg_args.extend(self.__generate_general_settings_args())

    def __generate_general_settings_args(self):
        args = []

        for key, value in self.general_settings.ffmpeg_args.items():
            if value is not None:
                args.append(key)
                args.append(value)

        return args

    def __apply_trim_settings_args(self, ffmpeg_args):
        if self.trim_settings is not None:
            ffmpeg_args.append('-to')
            ffmpeg_args.append(self.trim_settings.ffmpeg_args['-to'])

    def __apply_output_file_args(self, ffmpeg_args, cmd_args_enabled):
        if self.video_chunk:
            for arg in self.vsync_args:
                ffmpeg_args.append(arg)

        if self.folder_state:
            output_file_path = self.output_directory
        else:
            output_file_path = self.output_directory + self.filename + self.output_container

        if cmd_args_enabled:
            output_file_path = '\"' + output_file_path + '\"'

        ffmpeg_args.append(output_file_path)

    def __apply_2pass_args(self, ffmpeg_args):
        if self.is_video_settings_2_pass():
            ffmpeg_copy = self.get_copy()
            ffmpeg_copy.video_settings.encode_pass = 2

            ffmpeg_args.append('&&')
            ffmpeg_args.extend(ffmpeg_copy.get_args())

    def is_video_settings_x264(self):
        if self.video_settings is not None and self.video_settings.codec_name == 'libx264':
            return True

        return False

    def is_video_settings_x265(self):
        if self.video_settings is not None and self.video_settings.codec_name == 'libx265':
            return True

        return False

    def is_video_settings_vp9(self):
        if self.video_settings is not None and self.video_settings.codec_name == 'libvpx-vp9':
            return True

        return False

    def is_video_settings_vp8(self):
        if self.video_settings is not None and self.video_settings.codec_name == 'libvpx-vp8':
            return True

        return False

    def is_video_settings_nvenc(self):
        if self.video_settings is not None and not self.no_video and 'nvenc' in self.video_settings.codec_name:
            return True

        return False

    def is_video_settings_2_pass(self):
        if self.video_settings is not None:

            if self.video_settings.encode_pass is not None and self.video_settings.encode_pass == 1:
                return True

        return False

    def get_copy(self):
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
