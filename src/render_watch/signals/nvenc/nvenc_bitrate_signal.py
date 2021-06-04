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


class NvencBitrateSignal:
    def __init__(self, nvenc_handlers, inputs_page_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_nvenc_bitrate_radiobutton_toggled(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.nvenc_handlers.set_bitrate_state()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.signal_average_radiobutton()
        self.nvenc_handlers.signal_constant_radiobutton()
        self.nvenc_handlers.signal_2pass_radiobutton()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.nvenc_handlers.get_bitrate_value()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_average_radiobutton_toggled(self, average_radiobutton):
        if not average_radiobutton.get_active():
            return

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.update_rc_from_average_bitrate()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_constant_radiobutton_toggled(self, constant_radiobutton):
        if not constant_radiobutton.get_active():
            return

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.update_rc_from_constant_bitrate()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = True

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_2pass_radiobutton_toggled(self, dual_pass_radiobutton):
        self.nvenc_handlers.set_multi_pass_state(dual_pass_radiobutton.get_active())

        if not dual_pass_radiobutton.get_active():
            return

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.update_rc_from_2pass_bitrate()
        self.nvenc_handlers.signal_multi_pass_combobox()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.cbr = None
            ffmpeg.video_settings.dual_pass_enabled = True

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
