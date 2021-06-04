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

import subprocess
import os
import logging

from render_watch.app_formatting import format_converter
from render_watch.ffmpeg.settings import Settings
from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.startup import GLib


def get_crop_preview_file(ffmpeg, preferences, preview_height=None, start_time_param=None):
    origin_width, origin_height = ffmpeg.width_origin, ffmpeg.height_origin
    output_file = preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_crop_preview.tiff'
    start_time = __get_crop_preview_start_time(ffmpeg, start_time_param)
    preview_width, preview_height = __get_crop_preview_dimensions(ffmpeg, origin_width, origin_height, preview_height)
    args = __generate_crop_preview_args(ffmpeg, start_time, preview_width, preview_height, output_file)

    if not __run_crop_preview_process(args):
        return None

    return output_file


def __get_crop_preview_start_time(ffmpeg, start_time_param):
    if start_time_param is not None:
        start_time = start_time_param
    else:
        start_time = ffmpeg.duration_origin / 2

    return start_time


def __get_crop_preview_dimensions(ffmpeg, origin_width, origin_height, preview_height):
    if ffmpeg.picture_settings.scale is not None:

        if preview_height:
            size = ffmpeg.picture_settings.scale
            width, height = size[0], size[1]
            ratio = width / height
            preview_width = preview_height * ratio
        else:
            size = ffmpeg.picture_settings.scale
            preview_width, preview_height = size[0], size[1]
    elif ffmpeg.picture_settings.crop is not None:

        if preview_height:
            crop = ffmpeg.picture_settings.crop
            width, height = crop[0], crop[1]
            ratio = width / height
            preview_width = preview_height * ratio
        else:
            crop = ffmpeg.picture_settings.crop
            preview_width, preview_height = crop[0], crop[1]
    else:

        if preview_height:
            ratio = origin_width / origin_height
            preview_width = preview_height * ratio
        else:
            preview_width = origin_width
            preview_height = origin_height

    return preview_width, preview_height


def __generate_crop_preview_args(ffmpeg, start_time, preview_width, preview_height, output_file):
    args = Settings.ffmpeg_init_args.copy()

    args.append('-ss')
    args.append(str(start_time))
    args.append('-i')
    args.append(ffmpeg.input_file)
    args.append('-vframes')
    args.append('1')

    if ffmpeg.picture_settings.crop is not None:
        args.append('-filter:v')
        args.append(ffmpeg.picture_settings.ffmpeg_args['-filter:v'])

    args.append('-s')
    args.append(str(int(preview_width)) + 'x' + str(preview_height))
    args.append(output_file)

    return args


def __run_crop_preview_process(args):
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        rc = process.wait()

    if rc != 0:
        logging.error('--- CROP PREVIEW FAILED ---\n' + str(args))

    return rc == 0


def get_trim_preview_file(ffmpeg, start_time, preferences):
    output_file = preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_trim_preview.tiff'
    args = __generate_trim_preview_args(ffmpeg, start_time, output_file)

    if not __run_trim_preview_process(args):
        return None

    return output_file


def __generate_trim_preview_args(ffmpeg, start_time, output_file):
    args = Settings.ffmpeg_init_args.copy()

    args.append('-ss')
    args.append(str(start_time))
    args.append('-i')
    args.append(ffmpeg.input_file)
    args.append('-vframes')
    args.append('1')
    args.append('-an')
    args.append(output_file)

    return args


def __run_trim_preview_process(args):
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        rc = process.wait()

    if rc != 0:
        logging.error('--- TRIM PREVIEW FAILED ---\n' + str(args))

    return rc == 0


def set_info(ffmpeg):
    width, height = None, None
    codec_type = None
    codec_name = None
    frame_rate = None
    duration = None
    sample_rate = None
    channels = None
    index = None
    audio_done, video_done, duration_done = False, False, False
    video_streams = {}
    audio_streams = {}

    args = Settings.ffprobe_args.copy()
    args.append(ffmpeg.input_file)

    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        while True:
            output = process.stdout.readline().strip()

            if not output:
                break

            if output == '[/STREAM]':
                if not audio_done and codec_type == 'audio':
                    stream_info = codec_name + ',' + channels + ' channels,' + sample_rate + 'hz'
                    ffmpeg.codec_audio_origin = codec_name
                    audio_streams[index] = stream_info
                    ffmpeg.audio_channels_origin = channels
                    ffmpeg.audio_sample_rate_origin = sample_rate
                    audio_done = True
                elif not video_done and codec_type == 'video':
                    stream_info = codec_name + ',' + str(width) + 'x' + str(height) + '(' + frame_rate + ')'
                    ffmpeg.codec_video_origin = codec_name
                    video_streams[index] = stream_info
                    ffmpeg.framerate_origin = frame_rate
                    ffmpeg.width_origin = width
                    ffmpeg.height_origin = height
                    ffmpeg.resolution_origin = width, height
                    video_done = True
            elif not duration_done and output == '[/FORMAT]':
                ffmpeg.duration_origin = duration

            if video_done and audio_done and duration_done:
                break

            output = output.split('=')

            try:
                if 'codec_type' in output:
                    if output[1] == 'video':
                        video_done = False
                    elif output[1] == 'audio':
                        audio_done = False

                    codec_type = output[1]
                elif 'codec_name' in output:
                    codec_name = output[1]
                elif 'index' in output:
                    index = output[1]

                if not video_done:

                    if 'width' in output:
                        width = int(output[1])
                    elif 'height' in output:
                        height = int(output[1])
                    elif 'r_frame_rate' in output:
                        numbers = output[1].split('/')

                        try:
                            fps_value = round(int(numbers[0]) / int(numbers[1]), 2)
                            frame_rate = str(fps_value)
                        except ZeroDivisionError:
                            continue

                if not duration_done:

                    if 'duration' in output:
                        duration = int(output[1].split('.')[0])

                if not audio_done:

                    if 'channels' in output:
                        channels = output[1]
                    elif 'sample_rate' in output:
                        sample_rate = output[1]
            except ValueError:
                logging.warning('--- FAILED TO SET INFO FOR FILE: ' + ffmpeg.input_file + ' ---')

                return False

    filesize = os.path.getsize(ffmpeg.input_file)
    ffmpeg.file_size = format_converter.get_file_size_from_bytes(filesize)
    ffmpeg.input_file_info['video_streams'] = video_streams
    ffmpeg.input_file_info['audio_streams'] = audio_streams
    logging.info('--- INPUT FILE INFO ---\n' + str(ffmpeg.input_file_info))

    return check_info_success(ffmpeg)


def check_info_success(ffmpeg):
    if ffmpeg.codec_video_origin is None:
        ffmpeg.codec_video_origin = 'N/A'

    if ffmpeg.codec_audio_origin is None:
        ffmpeg.codec_audio_origin = 'N/A'

    if ffmpeg.audio_channels_origin is None:
        ffmpeg.audio_channels_origin = 'N/A'

    if ffmpeg.audio_sample_rate_origin is None:
        ffmpeg.audio_sample_rate_origin = 'N/A'

    if ffmpeg.folder_state:
        ffmpeg.width_origin = 'N/A'
        ffmpeg.height_origin = 'N/A'
        ffmpeg.duration_origin = 'N/A'
        ffmpeg.resolution_origin = 'N/A', 'N/A'
        ffmpeg.framerate_origin = 'N/A'
    else:

        if ffmpeg.width_origin is None or ffmpeg.height_origin is None:
            return False

        if ffmpeg.duration_origin is None:
            return False

        if ffmpeg.resolution_origin is None:
            return False

        if ffmpeg.framerate_origin is None:
            return False

        if ffmpeg.file_size == '0.0KB':
            return False

    return True


def process_auto_crop(ffmpeg):
    try:
        start_time = ffmpeg.duration_origin / 2
        args = __generate_auto_crop_args(ffmpeg, start_time)
        width, height, x, y = __run_auto_crop_process(args)

        if __is_auto_crop_dimensions_not_valid(ffmpeg, width, height):
            ffmpeg.picture_settings.crop = None

            logging.info('--- AUTO CROP NOT NEEDED FOR: ' + ffmpeg.input_file + ', DISABLING ---')

            return False

        ffmpeg.picture_settings.crop = width, height, x, y

        return True
    except UnboundLocalError:
        logging.error('--- FAILED TO SET AUTO CROP FOR: ' + ffmpeg.input_file + ' ---')

        return False


def __generate_auto_crop_args(ffmpeg, start_time):
    args = ffmpeg.ffmpeg_init_auto_crop_args.copy()

    args.append('-ss')
    args.append(str(start_time))
    args.append('-i')
    args.append(ffmpeg.input_file)
    args.append('-an')
    args.append('-vframes')
    args.append('240')
    args.append('-vf')
    args.append('cropdetect')
    args.append('-f')
    args.append('null')
    args.append('-')

    return args


def __run_auto_crop_process(args):
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        while True:
            output = process.stdout.readline().strip().split('=')

            if '' in output:
                break

            if len(output) > 1:
                output = output[1].split(':')

                if len(output) == 4:
                    width = output[0]
                    height = output[1]
                    x = output[2]
                    y = output[3]

    return width, height, x, y


def __is_auto_crop_dimensions_not_valid(ffmpeg, width, height):
    width_check = not ((int(width) + 10) < ffmpeg.width_origin)
    height_check = not ((int(height) + 10) < ffmpeg.height_origin)

    return width_check and height_check


def get_preview_file(ffmpeg, start_time, preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    output_file = preferences.temp_directory + '/' + ffmpeg_copy.temp_file_name + '_preview.tiff'
    preview_width, preview_height = __get_preview_dimensions(ffmpeg_copy)
    ffmpeg_copy.trim_settings = __get_preview_trim_settings(ffmpeg, start_time)
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name

    if not __run_preview_ffmpeg_process(ffmpeg_copy):
        return None

    if not __run_preview_process(ffmpeg_copy, preview_width, preview_height, output_file):
        return None

    return output_file


def __get_preview_dimensions(ffmpeg):
    if ffmpeg.picture_settings.scale is not None:
        size = ffmpeg.picture_settings.scale
        preview_width, preview_height = size[0], size[1]
    elif ffmpeg.picture_settings.crop is not None:
        crop = ffmpeg.picture_settings.crop
        preview_width, preview_height = crop[0], crop[1]
    else:
        preview_width, preview_height = ffmpeg.width_origin, ffmpeg.height_origin

    return preview_width, preview_height


def __get_preview_trim_settings(ffmpeg, start_time):
    duration = ffmpeg.duration_origin
    trim_settings = TrimSettings()

    if start_time > (duration - 1):
        trim_settings.start_time = start_time - 1
    else:
        trim_settings.start_time = start_time

    trim_settings.trim_duration = 0.5

    return trim_settings


def __get_preview_ffmpeg_args(ffmpeg):
    ffmpeg_args = [ffmpeg.get_args()]

    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        ffmpeg_args = first_pass_args, second_pass_args

    return ffmpeg_args


def __run_preview_ffmpeg_process(ffmpeg):
    rc = -1

    for args in __get_preview_ffmpeg_args(ffmpeg):
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, bufsize=1) as process:
            rc = process.wait()

        if rc != 0:
            logging.error('--- PREVIEW THUMBNAIL ENCODE FAILED ---\n' + str(ffmpeg.get_args()))

            return False

    return rc == 0


def __get_preview_args(ffmpeg, preview_width, preview_height, output_file):
    preview_args = Settings.ffmpeg_init_args.copy()

    preview_args.append('-i')
    preview_args.append(ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container)
    preview_args.append('-f')
    preview_args.append('image2')
    preview_args.append('-an')
    preview_args.append('-s')
    preview_args.append(str(preview_width) + 'x' + str(preview_height))
    preview_args.append('-update')
    preview_args.append('1')
    preview_args.append(output_file)

    return preview_args


def __run_preview_process(ffmpeg, preview_width, preview_height, output_file):
    preview_args = __get_preview_args(ffmpeg, preview_width, preview_height, output_file)

    with subprocess.Popen(preview_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        rc = process.wait()

    if rc != 0:
        logging.error('--- PREVIEW THUMBNAIL GENERATION PROCESS FAILED ---\n' + str(preview_args))

        return False

    return rc == 0


def start_vid_preview(ffmpeg, start_time, duration, preview_page_handlers, stop, preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    file_name = ffmpeg_copy.temp_file_name + '_preview'
    output_file = preferences.temp_directory + '/' + file_name + ffmpeg_copy.output_container
    ffmpeg_copy.trim_settings = __get_vid_preview_trim_settings(start_time, duration)
    ffmpeg_copy.filename = file_name
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'

    if not __run_vid_preview_ffmpeg_process(ffmpeg_copy, duration, preview_page_handlers, stop):
        return None

    __reset_vid_preview_widgets(preview_page_handlers)
    __run_vid_preview_process(output_file, stop)


def __get_vid_preview_trim_settings(start_time, duration):
    trim_settings = TrimSettings()
    trim_settings.start_time = start_time
    trim_settings.trim_duration = duration

    return trim_settings


def __get_vid_preview_ffmpeg_args(ffmpeg):
    ffmpeg_args = [ffmpeg.get_args()]

    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        ffmpeg_args = first_pass_args, second_pass_args

    return ffmpeg_args


def __run_vid_preview_ffmpeg_process(ffmpeg, duration, preview_page_handlers, stop):
    ffmpeg_args = __get_vid_preview_ffmpeg_args(ffmpeg)
    rc = -1

    for encode_pass, args in enumerate(ffmpeg_args):
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, bufsize=1) as process:
            while True:
                if stop():
                    process.terminate()

                    break

                output = process.stdout.readline().strip()

                if output == '' and process.poll() is not None:
                    break

                try:
                    output = output.split('=')
                    output = output[5].split(' ')
                    current = format_converter.get_seconds_from_timecode(output[0])

                    if encode_pass == 0:
                        progress = (current / duration) / len(ffmpeg_args)
                    else:
                        progress = .5 + ((current / duration) / len(ffmpeg_args))

                    GLib.idle_add(preview_page_handlers.set_progress_fraction, progress)
                except:
                    continue

        rc = process.wait()

        if rc != 0:
            logging.error('--- VIDEO PREVIEW ENCODE PROCESS FAILED ---\n' + str(ffmpeg.get_args()))

            return False

    return rc == 0


def __reset_vid_preview_widgets(preview_page_handlers):
    GLib.idle_add(preview_page_handlers.reset_preview_buttons)


def __get_vid_preview_args(output_file):
    preview_args = Settings.ffplay_init_args.copy()

    preview_args.append('-i')
    preview_args.append(output_file)
    preview_args.append('-loop')
    preview_args.append('0')
    preview_args.append('-loglevel')
    preview_args.append('quiet')

    return preview_args


def __run_vid_preview_process(output_file, stop):
    preview_args = __get_vid_preview_args(output_file)

    with subprocess.Popen(preview_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        while process.poll() is None:
            if stop():
                process.terminate()

                break

    rc = process.poll()

    if rc != 0:
        logging.error('--- VIDEO PREVIEW FAILED ---\n' + str(preview_args))


def start_benchmark(ffmpeg, settings_sidebar_handlers, stop, preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    origin_duration = ffmpeg_copy.duration_origin
    start_time, duration = __get_benchmark_start_time_and_duration(settings_sidebar_handlers, origin_duration)
    ffmpeg_copy.trim_settings = __get_benchmark_trim_settings(start_time, duration)
    ffmpeg_copy.filename = 'benchmark'
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'

    __set_benchmark_widgets_start_state(settings_sidebar_handlers)

    if not __run_benchmark_process(ffmpeg_copy, settings_sidebar_handlers, duration, origin_duration, stop):
        return None


def __get_benchmark_start_time_and_duration(settings_sidebar_handlers, origin_duration):
    if settings_sidebar_handlers.is_benchmark_short_radiobutton_active():
        if (origin_duration / 15) >= 2:
            duration = 15
            start_time = origin_duration / 2
        elif (origin_duration / 15) >= 1:
            duration = 15
            start_time = 0
        else:
            duration = origin_duration
            start_time = 0
    else:
        if (origin_duration / 30) >= 2:
            duration = 30
            start_time = origin_duration / 2
        elif (origin_duration / 30) >= 1:
            duration = 30
            start_time = 0
        else:
            duration = origin_duration
            start_time = 0

    return start_time, duration


def __get_benchmark_trim_settings(start_time, duration):
    trim_settings = TrimSettings()
    trim_settings.start_time = start_time
    trim_settings.trim_duration = duration

    return trim_settings


def __set_benchmark_widgets_start_state(settings_sidebar_handlers):
    GLib.idle_add(settings_sidebar_handlers.set_benchmark_start_state)


def __run_benchmark_process(ffmpeg, settings_sidebar_handlers, duration, origin_duration, stop):
    ffmpeg_args = __get_benchmark_ffmpeg_args(ffmpeg)
    speed_value = None
    file_size_value = None

    for encode_pass, args in enumerate(ffmpeg_args):
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, bufsize=1) as process:
            while True:
                if stop():
                    process.terminate()

                    break

                output = process.stdout.readline().strip()

                if not output:
                    break

                try:
                    output = output.split('=')
                    bitrate = output[6].split(' ')

                    while '' in bitrate:
                        bitrate.remove('')

                    bitrate_value = bitrate[0]
                    file_size = output[4].split(' ')
                    file_size = file_size[-2].split('k')[0]
                    file_size_value = int(file_size)
                    speed = output[-1]
                    speed_temp = speed.split('x')
                    speed_value = float(speed_temp[0])
                    current_time = output[5].split(' ')
                    current_time = format_converter.get_seconds_from_timecode(current_time[0])

                    if encode_pass == 0:
                        progress = (current_time / duration) / len(ffmpeg_args)
                    else:
                        progress = .5 + ((current_time / duration) / len(ffmpeg_args))

                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_progress_bar_fraction, progress)
                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_bitrate_label_text, bitrate_value)
                    GLib.idle_add(settings_sidebar_handlers.set_benchmark_speed_label_text, speed)
                except:
                    continue

        process.wait()

    try:
        if speed_value is not None:
            time_estimate = (origin_duration * len(ffmpeg_args)) / speed_value
            timecode = format_converter.get_timecode_from_seconds(time_estimate)

            GLib.idle_add(settings_sidebar_handlers.set_benchmark_process_time_label_text, timecode)
    except ZeroDivisionError:
        logging.error('--- BENCHMARK SPEED LABEL CAN\'T BE SET ---')

    if file_size_value is not None:
        ratio = origin_duration / duration
        total = file_size_value * ratio * 1000
        total = format_converter.get_file_size_from_bytes(total)

        GLib.idle_add(settings_sidebar_handlers.set_benchmark_file_size_label_text, total)

    rc = process.poll()

    GLib.idle_add(settings_sidebar_handlers.set_benchmark_done_state)

    if rc != 0:
        if stop():
            GLib.idle_add(settings_sidebar_handlers.set_benchmark_ready_state)
        else:
            logging.error('--- BENCHMARK PROCESS FAILED ---\n' + str(ffmpeg.get_args()))

    return rc == 0


def __get_benchmark_ffmpeg_args(ffmpeg):
    ffmpeg_args = [ffmpeg.get_args()]

    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        ffmpeg_args = first_pass_args, second_pass_args

    return ffmpeg_args
