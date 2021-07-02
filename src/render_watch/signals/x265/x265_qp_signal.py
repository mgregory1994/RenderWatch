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


class X265QpSignal:
    """Handles the signal emitted when the x265 QP option is changed."""

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_qp_radiobutton_clicked(self, qp_radiobutton):
        """Configures the x265 widgets for QP options, applies the QP option, and updates the preview page.

        :param qp_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not qp_radiobutton.get_active():
            return

        self.x265_handlers.set_crf_state()

        if self.x265_handlers.is_widgets_setting_up:
            return

        qp_value = self.x265_handlers.get_crf_value()
        advanced_settings_enabled = self.x265_handlers.is_advanced_settings_enabled()
        for row in self.inputs_page_handlers.get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = qp_value
            ffmpeg.video_settings.advanced_enabled = advanced_settings_enabled
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
