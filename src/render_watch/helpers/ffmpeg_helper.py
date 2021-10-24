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


def get_duration_in_seconds(ffmpeg):
    if ffmpeg.trim_settings:
        return ffmpeg.trim_settings.trim_duration
    return ffmpeg.duration_origin


def get_parsed_ffmpeg_args(ffmpeg):
    ffmpeg_args = (ffmpeg.get_args())

    if '&&' in ffmpeg_args[0]:
        first_pass_args = ffmpeg_args[0][:ffmpeg_args[0].index('&&')]
        second_pass_args = ffmpeg_args[0][(ffmpeg_args[0].index('&&') + 1):]
        return first_pass_args, second_pass_args

    return ffmpeg_args
