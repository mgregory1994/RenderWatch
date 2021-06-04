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


class Vp9BitrateSignal:
    def __init__(self, vp9_handlers, inputs_page_handlers):
        self.vp9_handlers = vp9_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_vp9_bitrate_radiobutton_toggled(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.vp9_handlers.set_bitrate_state()

        if self.vp9_handlers.is_widgets_setting_up:
            return

        self.vp9_handlers.signal_average_radiobutton()
        self.vp9_handlers.signal_vbr_radiobutton()
        self.vp9_handlers.signal_constant_radiobutton()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_average_radiobutton_toggled(self, average_radiobutton):
        if self.vp9_handlers.is_widgets_setting_up or not average_radiobutton.get_active():
            return

        bitrate_value = self.vp9_handlers.get_bitrate_value()

        self.vp9_handlers.set_vbr_state(False)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = None
            ffmpeg.video_settings.minrate = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_vbr_radiobutton_toggled(self, vbr_radiobutton):
        if self.vp9_handlers.is_widgets_setting_up or not vbr_radiobutton.get_active():
            return

        bitrate_value = self.vp9_handlers.get_bitrate_value()
        max_bitrate_value = self.vp9_handlers.get_max_bitrate_value()
        min_bitrate_value = self.vp9_handlers.get_min_bitrate_value()

        self.vp9_handlers.set_vbr_state(True)
        self.vp9_handlers.update_vbr_widgets(bitrate_value)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = max_bitrate_value
            ffmpeg.video_settings.minrate = min_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_constant_radiobutton_toggled(self, constant_radiobutton):
        if self.vp9_handlers.is_widgets_setting_up or not constant_radiobutton.get_active():
            return

        bitrate_value = self.vp9_handlers.get_bitrate_value()

        self.vp9_handlers.set_vbr_state(False)
        self.vp9_handlers.update_constant_bitrate_widgets(bitrate_value)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = bitrate_value
            ffmpeg.video_settings.minrate = bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.vp9_handlers.is_widgets_setting_up:
            return

        bitrate_value = bitrate_spinbutton.get_value_as_int()

        if self.vp9_handlers.is_vbr_active():
            self.vp9_handlers.update_vbr_widgets(bitrate_value)
        elif self.vp9_handlers.is_constant_bitrate_active():
            self.vp9_handlers.update_constant_bitrate_widgets(bitrate_value)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_max_bitrate_spinbutton_value_changed(self, max_bitrate_spinbutton):
        if self.vp9_handlers.is_widgets_setting_up:
            return

        max_bitrate_value = max_bitrate_spinbutton.get_value_as_int()

        self.vp9_handlers.update_bitrate_from_max_bitrate(max_bitrate_value)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.maxrate = max_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_min_bitrate_spinbutton_value_changed(self, min_bitrate_spinbutton):
        if self.vp9_handlers.is_widgets_setting_up:
            return

        min_bitrate_value = min_bitrate_spinbutton.get_value_as_int()

        self.vp9_handlers.update_bitrate_from_min_bitrate(min_bitrate_value)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.minrate = min_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
