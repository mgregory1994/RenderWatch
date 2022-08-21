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


"""Constants for modules in the ffmpeg package."""


# FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-loglevel', 'quiet', '-stats', "-y"]
FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-stats', "-y"]
FFMPEG_INIT_AUTO_CROP_ARGS = ['ffmpeg', '-hide_banner', '-y']
FFMPEG_CONCATENATION_INIT_ARGS = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i']

VIDEO_COPY_ARGS = ('-c:v', 'copy')
AUDIO_COPY_ARGS = ('-c:a', 'copy')

AUDIO_NONE_ARG = '-an'
VIDEO_NONE_ARG = '-vn'

RAW_VIDEO_ARGS = ('-f', 'rawvideo')

VSYNC_ARGS = ('-vsync', '0')
