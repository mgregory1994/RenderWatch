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


class AudioStreamSignal:
    """
    Handles the signal emitted from the audio stream selection combobox on an input task.
    """

    def __init__(self, input_task):
        self.input_task = input_task

    def on_audio_stream_combobox_changed(self, audio_stream_combobox):
        """
        Sets the audio stream index for the input's ffmpeg settings and updates the input task's labels.

        :param audio_stream_combobox: Combobox that emitted the signal.
        """
        ffmpeg = self.input_task.ffmpeg
        audio_stream_combobox_index = audio_stream_combobox.get_active()
        audio_streams = list(ffmpeg.input_file_info['audio_streams'].items())



        self._set_audio_stream_index(ffmpeg, audio_streams, audio_stream_combobox_index)
        self._set_audio_stream_codec_name(ffmpeg, audio_streams, audio_stream_combobox_index)
        self._set_audio_stream_sample_rate(ffmpeg, audio_streams, audio_stream_combobox_index)

        self.input_task.setup_labels()

    @staticmethod
    def _set_audio_stream_index(ffmpeg, audio_streams, audio_stream_combobox_index):
        audio_stream_index = audio_streams[audio_stream_combobox_index][0]
        ffmpeg.audio_stream_index = audio_stream_index

    @staticmethod
    def _set_audio_stream_codec_name(ffmpeg, audio_streams, audio_streams_combobox_index):
        codec_name = audio_streams[audio_streams_combobox_index][1]['codec_name']
        ffmpeg.input_file_info['codec_audio'] = codec_name

    @staticmethod
    def _set_audio_stream_sample_rate(ffmpeg, audio_streams, audio_stream_combobox_index):
        sample_rate = audio_streams[audio_stream_combobox_index][1]['sample_rate']
        ffmpeg.input_file_info['sample_rate'] = sample_rate
