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


class GeneralSettings:
    frame_rate_ffmpeg_args_list = ("23.98", "24", "25", "29.97", "30", "50", "59.94", "60")
    video_codec_mp4_nvenc_ui_list = ("copy", "H264", "H265", 'NVENC H264', 'NVENC H265')
    video_codec_mp4_ui_list = ("copy", "H264", "H265")
    video_codec_mkv_nvenc_ui_list = ("copy", "H264", "H265", 'NVENC H264', 'NVENC H265', 'VP9')
    video_codec_mkv_ui_list = ("copy", "H264", "H265", 'VP9')
    video_codec_ts_nvenc_ui_list = ("copy", "H264", 'NVENC H264')
    video_codec_ts_ui_list = ("copy", "H264")
    video_codec_webm_ui_list = ("copy", 'VP9')
    audio_codec_mp4_ui_list = ("copy", "aac")
    audio_codec_mkv_ui_list = ("copy", "aac", 'opus')
    audio_codec_ts_ui_list = ("copy", "aac")
    audio_codec_webm_ui_list = ("copy", 'opus')
    video_file_containers_list = (".mp4", ".mkv", ".ts", '.webm')

    def __init__(self):
        self.ffmpeg_args = {
            "-r": None,
            '-movflags': None
        }

    @property
    def frame_rate(self):
        try:
            frame_rate = self.ffmpeg_args['-r']

            return GeneralSettings.frame_rate_ffmpeg_args_list.index(frame_rate)
        except ValueError:
            return None

    @frame_rate.setter
    def frame_rate(self, frame_rate_index):
        if frame_rate_index is None or frame_rate_index < 0:
            self.ffmpeg_args['-r'] = None
        else:
            self.ffmpeg_args['-r'] = GeneralSettings.frame_rate_ffmpeg_args_list[frame_rate_index]

    @property
    def fast_start(self):
        return self.ffmpeg_args['-movflags'] is not None

    @fast_start.setter
    def fast_start(self, enabled):
        if enabled:
            self.ffmpeg_args['-movflags'] = 'faststart'
        else:
            self.ffmpeg_args['-movflags'] = None
