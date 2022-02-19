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


import logging
import subprocess
import re


def process_auto_crop(ffmpeg):
    """
    Checks ffmpeg setting's input for "black bars" and automatically crops them out.

    :param ffmpeg: ffmpeg settings.
    """
    try:
        start_time = ffmpeg.duration_origin / 2
        auto_crop_args = _get_auto_crop_args(ffmpeg, start_time)
        width, height, x, y = _run_auto_crop_process(auto_crop_args)

        if _is_auto_crop_dimensions_valid(ffmpeg, width, height):
            ffmpeg.picture_settings.crop = width, height, x, y

            return True

        ffmpeg.picture_settings.crop = None
        logging.info('--- AUTO CROP NOT NEEDED FOR: ' + ffmpeg.input_file + ', DISABLING ---')

        return False
    except UnboundLocalError:
        logging.error('--- FAILED TO SET AUTO CROP FOR: ' + ffmpeg.input_file + ' ---')

        return False


def _get_auto_crop_args(ffmpeg, start_time):
    args = ffmpeg.FFMPEG_INIT_AUTO_CROP_ARGS.copy()
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


def _run_auto_crop_process(auto_crop_args):
    with subprocess.Popen(auto_crop_args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as auto_crop_process:
        while True:
            stdout = auto_crop_process.stdout.readline().strip()
            if stdout == '':
                break

            try:
                crop_settings_match = re.search('crop=\d+:\d+:\d+:\d+', stdout)
                if crop_settings_match:
                    crop_settings = crop_settings_match.group().split('=')[1]
            except:
                continue

    if auto_crop_process.poll():
        logging.error('--- AUTO CROP FAILED ---\n' + str(auto_crop_args))
    if crop_settings:
        return crop_settings.split(':')
    return None


def _is_auto_crop_dimensions_valid(ffmpeg, width, height):
    try:
        width_check = ((int(width) + 10) < ffmpeg.width_origin)
        height_check = ((int(height) + 10) < ffmpeg.height_origin)
        return width_check or height_check
    except:
        return False
