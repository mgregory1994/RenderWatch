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


class GeneralSettings:
    """Manages all settings for general ffmpeg settings.

    This includes setting frame rate and container settings.
    """

    FRAME_RATE_ARGS_LIST = ('23.98', '24', '25', '29.97', '30', '50', '59.94', '60')
    VIDEO_CODEC_MP4_NVENC_UI_LIST = ('copy', 'H264', 'H265', 'NVENC H264', 'NVENC H265')
    VIDEO_CODEC_MP4_UI_LIST = ('copy', 'H264', 'H265')
    VIDEO_CODEC_MKV_NVENC_UI_LIST = ('copy', 'H264', 'H265', 'NVENC H264', 'NVENC H265', 'VP9')
    VIDEO_CODEC_MKV_UI_LIST = ('copy', 'H264', 'H265', 'VP9')
    VIDEO_CODEC_TS_NVENC_UI_LIST = ('copy', 'H264', 'NVENC H264')
    VIDEO_CODEC_TS_UI_LIST = ('copy', 'H264')
    VIDEO_CODEC_WEBM_UI_LIST = ('copy', 'VP9')
    AUDIO_CODEC_MP4_UI_LIST = ('copy', 'aac')
    AUDIO_CODEC_MKV_UI_LIST = ('copy', 'aac', 'opus')
    AUDIO_CODEC_TS_UI_LIST = ('copy', 'aac')
    AUDIO_CODEC_WEBM_UI_LIST = ('copy', 'opus')
    CONTAINERS_UI_LIST = ('.mp4', '.mkv', '.ts', '.webm')

    def __init__(self):
        self.ffmpeg_args = {}

    @property
    def frame_rate(self):
        """Returns frame rate argument as an index."""
        if '-r' in self.ffmpeg_args:
            frame_rate_arg = self.ffmpeg_args['-r']
            return GeneralSettings.FRAME_RATE_ARGS_LIST.index(frame_rate_arg)
        return None

    @frame_rate.setter
    def frame_rate(self, frame_rate_index):
        """Stores index as a frame rate argument."""
        if frame_rate_index is None or frame_rate_index < 0:
            self.ffmpeg_args.pop('-r', 0)
        else:
            self.ffmpeg_args['-r'] = GeneralSettings.FRAME_RATE_ARGS_LIST[frame_rate_index]

    @property
    def fast_start(self):
        """Returns fast start argument as a boolean."""
        if '-movflags' in self.ffmpeg_args:
            return self.ffmpeg_args['-movflags'] == 'faststart'
        return False

    @fast_start.setter
    def fast_start(self, fast_start_enabled):
        """Stores fast start boolean as a string argument."""
        if fast_start_enabled:
            self.ffmpeg_args['-movflags'] = 'faststart'
        else:
            self.ffmpeg_args.pop('-movflags', 0)
