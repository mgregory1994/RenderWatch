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


class GeneralSettings:
    FRAME_RATE = ('23.98', '24', '25', '29.97', '30', '50', '59.94', '60')
    FRAME_RATE_LENGTH = len(FRAME_RATE)

    VIDEO_CODECS_MP4_NVENC_UI = ('copy', 'H264', 'H265', 'NVENC H264', 'NVENC H265')
    VIDEO_CODECS_MP4_UI = ('copy', 'H264', 'H265')
    VIDEO_CODECS_MKV_NVENC_UI = ('copy', 'H264', 'H265', 'NVENC H264', 'NVENC H265', 'VP9')
    VIDEO_CODECS_MKV_UI = ('copy', 'H264', 'H265', 'VP9')
    VIDEO_CODECS_TS_NVENC_UI = ('copy', 'H264', 'NVENC H264')
    VIDEO_CODECS_TS_UI = ('copy', 'H264')
    VIDEO_CODECS_WEBM_UI = ('copy', 'VP9')

    AUDIO_CODECS_MP4_UI = ('copy', 'aac')
    AUDIO_CODECS_MKV_UI = ('copy', 'aac', 'opus')
    AUDIO_CODECS_TS_UI = ('copy', 'aac')
    AUDIO_CODECS_WEBM_UI = ('copy', 'opus')

    def __init__(self):
        self.ffmpeg_args = {}

    @property
    def frame_rate(self) -> int:
        """
        Returns frame rate as an index.
        """
        if '-r' in self.ffmpeg_args:
            frame_rate_arg = self.ffmpeg_args['-r']

            return GeneralSettings.FRAME_RATE.index(frame_rate_arg)
        return 0

    @frame_rate.setter
    def frame_rate(self, frame_rate_index: int | None):
        if frame_rate_index and 0 < frame_rate_index < GeneralSettings.FRAME_RATE_LENGTH:
            self.ffmpeg_args['-r'] = GeneralSettings.FRAME_RATE[frame_rate_index]
        else:
            self.ffmpeg_args.pop('-r', 0)

    @property
    def fast_start(self) -> bool:
        if '-movflags' in self.ffmpeg_args:
            return self.ffmpeg_args['-movflags'] == 'faststart'
        return False

    @fast_start.setter
    def fast_start(self, is_fast_start_enabled: bool):
        if is_fast_start_enabled:
            self.ffmpeg_args['-movflags'] = 'faststart'
        else:
            self.ffmpeg_args.pop('-movflags', 0)
