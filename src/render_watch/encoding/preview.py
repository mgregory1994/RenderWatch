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


import subprocess
import logging
import re
import copy

from render_watch.app_formatting import format_converter
from render_watch.ffmpeg.settings import Settings
from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.helpers.logging_helper import LoggingHelper
from render_watch.startup import GLib


def run_preview_process(generate_preview_func):
    def process_args(*args, **kwargs):
        args_list, output_file = generate_preview_func(*args, **kwargs)

        for args in args_list:
            with subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1) as process:
                process_return_code = process.wait()
            if process_return_code != 0:
                output_args = ''

                for index, arg in enumerate(args):
                    output_args += arg

                    if index != len(args) - 1:
                        output_args += ' '

                logging.error('--- PREVIEW FAILED ---\n' + output_args)

                return None
        return output_file
    return process_args


@run_preview_process
def generate_crop_preview_file(ffmpeg, preferences, preview_height=None, start_time=None):
    """
    Creates a crop preview image and returns the image's file path.

    :param ffmpeg: ffmpeg settings.
    :param preferences: Application preferences.
    :param preview_height: (Default None) Specifies a specific height for the preview image (maintains aspect ratio).
    :param start_time: (Default None) Specifies what time in the video to make the preview image.
    """
    origin_width, origin_height = ffmpeg.width_origin, ffmpeg.height_origin
    preview_width, preview_height = _get_crop_preview_dimensions(ffmpeg, origin_width, origin_height, preview_height)

    if start_time is None:
        start_time = _get_crop_preview_start_time(ffmpeg)

    output_file_path = preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_crop_preview.tiff'
    crop_preview_args = _get_crop_preview_args(ffmpeg,
                                               start_time,
                                               preview_width,
                                               preview_height,
                                               output_file_path)
    return (crop_preview_args,), output_file_path


def _get_crop_preview_start_time(ffmpeg):
    return ffmpeg.duration_origin / 2


def _get_crop_preview_dimensions(ffmpeg, origin_width, origin_height, preview_height):
    if ffmpeg.picture_settings.scale:
        return _get_crop_preview_scale_dimensions(ffmpeg, preview_height)
    elif ffmpeg.picture_settings.crop:
        return _get_crop_preview_crop_dimensions(ffmpeg, preview_height)
    else:
        return _get_crop_preview_origin_dimensions(origin_width, origin_height, preview_height)


def _get_crop_preview_scale_dimensions(ffmpeg, preview_height):
    if preview_height:
        size = ffmpeg.picture_settings.scale
        width, height = size[0], size[1]
        ratio = width / height
        return (preview_height * ratio), preview_height
    else:
        size = ffmpeg.picture_settings.scale
        return size[0], size[1]


def _get_crop_preview_crop_dimensions(ffmpeg, preview_height):
    if preview_height:
        crop = ffmpeg.picture_settings.crop
        width, height = crop[0], crop[1]
        ratio = width / height
        return (preview_height * ratio), preview_height
    else:
        crop = ffmpeg.picture_settings.crop
        return crop[0], crop[1]


def _get_crop_preview_origin_dimensions(origin_width, origin_height, preview_height):
    if preview_height:
        ratio = origin_width / origin_height
        return (preview_height * ratio), preview_height
    else:
        return origin_width, origin_height


def _get_crop_preview_args(ffmpeg, start_time, preview_width, preview_height, output_file_path):
    picture_settings = copy.deepcopy(ffmpeg.picture_settings)
    picture_settings.scale = int(preview_width), preview_height

    args = Settings.FFMPEG_INIT_ARGS.copy()
    args.append('-ss')
    args.append(str(start_time))
    args.append('-i')
    args.append(ffmpeg.input_file)
    args.append('-vframes')
    args.append('1')
    args.append('-filter_complex')
    args.append(picture_settings.ffmpeg_args['-filter_complex'])
    args.append(output_file_path)
    return args


@run_preview_process
def generate_trim_preview_file(ffmpeg, start_time, application_preferences):
    """
    Creates a trim preview image and returns the image's file path.
    """
    output_file_path = application_preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_trim_preview.tiff'
    trim_preview_args = _get_trim_preview_args(ffmpeg, start_time, output_file_path)
    return (trim_preview_args,), output_file_path


def _get_trim_preview_args(ffmpeg, start_time, output_file_path):
    args = Settings.FFMPEG_INIT_ARGS.copy()
    args.append('-ss')
    args.append(str(start_time))
    args.append('-i')
    args.append(ffmpeg.input_file)
    args.append('-vframes')
    args.append('1')
    args.append('-an')
    args.append(output_file_path)
    return args


@run_preview_process
def generate_preview_file(ffmpeg, start_time, application_preferences):
    """
    Creates a preview image at the start time and returns the image's file path.

    :param ffmpeg: The ffmpeg settings object.
    :param start_time: Time in the video to make a preview.
    :param application_preferences: The application's preferences object.
    """
    ffmpeg_copy = ffmpeg.get_copy()
    output_file = application_preferences.temp_directory + '/' + ffmpeg_copy.temp_file_name + '_preview.tiff'
    preview_width, preview_height = _get_preview_dimensions(ffmpeg_copy)
    _setup_preview_ffmpeg_settings(ffmpeg_copy, start_time, application_preferences)
    
    args_list = []
    preview_ffmpeg_args = _get_preview_ffmpeg_settings_args(ffmpeg_copy)
    preview_args = _get_preview_args(ffmpeg_copy, preview_width, preview_height, output_file)
    for args in preview_ffmpeg_args:
        args_list.append(args)
    args_list.append(preview_args)
    return args_list, output_file


def _setup_preview_ffmpeg_settings(ffmpeg, start_time, application_preferences):
    ffmpeg.trim_settings = _get_preview_trim_settings(ffmpeg, start_time)
    ffmpeg.output_directory = application_preferences.temp_directory + '/'
    ffmpeg.filename = ffmpeg.temp_file_name


def _get_preview_dimensions(ffmpeg):
    if ffmpeg.picture_settings.scale:
        return _get_preview_scale_dimensions(ffmpeg)
    elif ffmpeg.picture_settings.crop:
        return _get_preview_crop_dimensions(ffmpeg)
    else:
        return ffmpeg.width_origin, ffmpeg.height_origin


def _get_preview_scale_dimensions(ffmpeg):
    size = ffmpeg.picture_settings.scale
    return size[0], size[1]


def _get_preview_crop_dimensions(ffmpeg):
    crop = ffmpeg.picture_settings.crop
    return crop[0], crop[1]


def _get_preview_trim_settings(ffmpeg, start_time):
    duration = ffmpeg.duration_origin
    trim_settings = TrimSettings()

    if start_time > (duration - 1):
        trim_settings.start_time = start_time - 1
    else:
        trim_settings.start_time = start_time
    trim_settings.trim_duration = 0.5

    return trim_settings


def _get_preview_ffmpeg_settings_args(ffmpeg):
    ffmpeg_args = [ffmpeg.get_args()]
    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        ffmpeg_args = first_pass_args, second_pass_args
    return ffmpeg_args


def _get_preview_args(ffmpeg, preview_width, preview_height, output_file_path):
    preview_args = Settings.FFMPEG_INIT_ARGS.copy()
    preview_args.append('-i')
    preview_args.append(ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container)
    preview_args.append('-f')
    preview_args.append('image2')
    preview_args.append('-an')
    preview_args.append('-s')
    preview_args.append(str(preview_width) + 'x' + str(preview_height))
    preview_args.append('-update')
    preview_args.append('1')
    preview_args.append(output_file_path)
    return preview_args


def start_vid_preview(ffmpeg,
                      start_time,
                      preview_duration,
                      preview_page_handlers,
                      stop_preview,
                      application_preferences):
    """
    Encodes a video preview and plays the preview using ffplay.

    :param ffmpeg: ffmpeg settings.
    :param start_time: The time in the video to start the preview.
    :param preview_duration: The duration of the video preview.
    :param preview_page_handlers: Preview page handlers.
    :param stop_preview: Stops the preview process.
    :param application_preferences: Application preferences.
    """
    ffmpeg_copy = ffmpeg.get_copy()
    file_name = ffmpeg_copy.temp_file_name + '_preview'
    output_file = application_preferences.temp_directory + '/' + file_name + ffmpeg_copy.output_container
    _setup_vid_preview_ffmpeg_settings(ffmpeg_copy, file_name, start_time, preview_duration, application_preferences)

    is_vid_preview_successful = _run_vid_preview_encode_process(ffmpeg_copy,
                                                                preview_duration,
                                                                preview_page_handlers,
                                                                stop_preview)
    _reset_vid_preview_widgets(preview_page_handlers)

    if is_vid_preview_successful:
        _run_vid_preview_process(output_file, stop_preview)


def _setup_vid_preview_ffmpeg_settings(ffmpeg, file_name, start_time, preview_duration, application_preferences):
    ffmpeg.trim_settings = _get_vid_preview_trim_settings(start_time, preview_duration)
    ffmpeg.filename = file_name
    ffmpeg.output_directory = application_preferences.temp_directory + '/'


def _get_vid_preview_trim_settings(start_time, preview_duration):
    trim_settings = TrimSettings()
    trim_settings.start_time = start_time
    trim_settings.trim_duration = preview_duration
    return trim_settings


def _reset_vid_preview_widgets(preview_page_handlers):
    GLib.idle_add(preview_page_handlers.reset_preview_buttons)


def _run_vid_preview_encode_process(ffmpeg, preview_duration, preview_page_handlers, stop_preview):
    ffmpeg_args = _get_vid_preview_ffmpeg_args(ffmpeg)
    process_return_code = -1

    for encode_pass, args in enumerate(ffmpeg_args):
        with subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1) as vid_preview_encode_process:
            while True:
                if stop_preview():
                    vid_preview_encode_process.terminate()
                    break

                process_stdout = vid_preview_encode_process.stdout.readline().strip()
                if process_stdout == '' and vid_preview_encode_process.poll() is not None:
                    break

                try:
                    current_timecode = re.search('time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                                 process_stdout).group().split('=')[1]
                    current_time_in_seconds = format_converter.get_seconds_from_timecode(current_timecode)

                    if encode_pass == 0:
                        progress = (current_time_in_seconds / preview_duration) / len(ffmpeg_args)
                    else:
                        progress = .5 + ((current_time_in_seconds / preview_duration) / len(ffmpeg_args))

                    GLib.idle_add(preview_page_handlers.set_progress_fraction, progress)
                except:
                    continue

            process_return_code = vid_preview_encode_process.wait()
        if process_return_code != 0:
            LoggingHelper.log_encoder_error(ffmpeg, '--- VIDEO PREVIEW ENCODE PROCESS FAILED ---')
    return process_return_code == 0


def _get_vid_preview_ffmpeg_args(ffmpeg):
    ffmpeg_args = [ffmpeg.get_args()]
    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        ffmpeg_args = first_pass_args, second_pass_args
    return ffmpeg_args


def _run_vid_preview_process(output_file_path, stop_preview):
    preview_args = _get_vid_preview_args(output_file_path)

    with subprocess.Popen(
            preview_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1) as vid_preview_process:
        while vid_preview_process.poll() is None:
            if stop_preview():
                vid_preview_process.terminate()
                break

    process_return_code = vid_preview_process.poll()
    if process_return_code != 0:
        logging.error('--- VIDEO PREVIEW FAILED ---\n' + str(preview_args))


def _get_vid_preview_args(output_file_path):
    preview_args = Settings.FFPLAY_INIT_ARGS.copy()
    preview_args.append('-i')
    preview_args.append(output_file_path)
    preview_args.append('-loop')
    preview_args.append('0')
    preview_args.append('-loglevel')
    preview_args.append('quiet')
    return preview_args
