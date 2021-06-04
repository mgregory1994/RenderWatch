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


class Vp92PassSignal:
    def __init__(self, vp9_handlers, inputs_page_handlers, preferences):
        self.vp9_handlers = vp9_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences

    def on_vp9_2_pass_checkbox_toggled(self, encode_2_pass_checkbox):
        if self.vp9_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            stats_file_path = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'

            if encode_2_pass_checkbox.get_active():
                ffmpeg.video_settings.encode_pass = 1
                ffmpeg.video_settings.stats = stats_file_path
            else:
                ffmpeg.video_settings.encode_pass = None
                ffmpeg.video_settings.stats = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
