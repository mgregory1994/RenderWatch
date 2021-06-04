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


class AudioStreamSignal:
    def __init__(self, inputs_row):
        self.inputs_row = inputs_row

    def on_audio_stream_combobox_changed(self, audio_stream_combobox):
        ffmpeg = self.inputs_row.ffmpeg
        combobox_index = audio_stream_combobox.get_active()
        audio_streams = list(ffmpeg.input_file_info['audio_streams'].items())
        audio_stream_index = (audio_streams[combobox_index])[0]

        ffmpeg.audio_stream_index = audio_stream_index
        self.inputs_row.setup_labels()
