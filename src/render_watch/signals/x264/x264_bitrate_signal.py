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


class X264BitrateSignal:
    def __init__(self, x264_handlers, inputs_page_handlers, preferences):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences

    def on_x264_bitrate_radiobutton_clicked(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.x264_handlers.set_bitrate_state()
        self.x264_handlers.signal_average_radiobutton()
        self.x264_handlers.signal_constant_radiobutton()
        self.x264_handlers.signal_2pass_radiobutton()

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.x264_handlers.get_bitrate_value()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_average_radiobutton_toggled(self, average_radiobutton):
        if not average_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(True)

        if self.x264_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x264_handlers.is_advanced_settings_enabled()

        if advanced_enabled:
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_constant_radiobutton_toggled(self, constant_radiobutton):
        if not constant_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(False)

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = True
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_2pass_radiobutton_toggled(self, dual_pass_radiobutton):
        if not dual_pass_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(True)

        if self.x264_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x264_handlers.is_advanced_settings_enabled()

        if advanced_enabled:
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = 1
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'
            ffmpeg.video_settings.constant_bitrate = None

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.x264_handlers.is_widgets_setting_up:
            return

        if self.x264_handlers.is_vbr_enabled():
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
