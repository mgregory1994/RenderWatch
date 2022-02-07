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


class VideoStreamSignal:
    """
    Handles the signal emitted when a video stream is selected on an input task.
    """

    def __init__(self, input_task):
        self.input_task = input_task

    def on_video_stream_combobox_changed(self, video_stream_combobox):
        """
        Sets the video stream index for the input's ffmpeg settings and updates the inputs task's labels.

        :param video_stream_combobox: Combobox that emitted the signal.
        """
        ffmpeg = self.input_task.ffmpeg
        video_stream_combobox_index = video_stream_combobox.get_active()
        video_streams = list(ffmpeg.input_file_info['video_streams'].items())

        self._set_video_stream_index(ffmpeg, video_streams, video_stream_combobox_index)
        self._set_video_stream_codec_name(ffmpeg, video_streams, video_stream_combobox_index)
        self._set_video_stream_dimensions(ffmpeg, video_streams, video_stream_combobox_index)

        self.input_task.setup_labels()

    @staticmethod
    def _set_video_stream_index(ffmpeg, video_streams, video_stream_combobox_index):
        video_stream_index = video_streams[video_stream_combobox_index][0]
        ffmpeg.video_stream_index = video_stream_index

    @staticmethod
    def _set_video_stream_codec_name(ffmpeg, video_streams, video_stream_combobox_index):
        codec_name = video_streams[video_stream_combobox_index][1]['codec_name']
        ffmpeg.input_file_info['codec_video'] = codec_name

    @staticmethod
    def _set_video_stream_dimensions(ffmpeg, video_streams, video_stream_combobox_index):
        width = video_streams[video_stream_combobox_index][1]['width']
        height = video_streams[video_stream_combobox_index][1]['height']
        resolution = str(width) + 'x' + str(height)
        ffmpeg.input_file_info['width'] = width
        ffmpeg.input_file_info['height'] = height
        ffmpeg.input_file_info['resolution'] = resolution
