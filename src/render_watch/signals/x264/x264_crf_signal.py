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


class X264CrfSignal:
    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_crf_radiobutton_clicked(self, crf_radiobutton):
        if not crf_radiobutton.get_active():
            return

        self.x264_handlers.set_crf_state()

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = self.x264_handlers.get_crf_value()
            ffmpeg.video_settings.advanced_enabled = self.x264_handlers.is_advanced_settings_enabled()
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_crf_scale_button_release_event(self, event, data):  # Unused parameters needed for this signal
        if self.x264_handlers.is_widgets_setting_up:
            return

        quantizer_value = self.x264_handlers.get_crf_value()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg

            if self.x264_handlers.is_crf_enabled():
                ffmpeg.video_settings.crf = quantizer_value
            else:
                ffmpeg.video_settings.qp = quantizer_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
