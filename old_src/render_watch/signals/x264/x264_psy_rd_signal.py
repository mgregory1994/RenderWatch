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


class X264PsyRDSignal:
    """
    Handles the signals emitted when x264 Psy RD related options are changed.
    """

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_psy_rd_spinbutton_value_changed(self, x264_psy_rd_spinbutton):
        """
        Applies the Psy RD options and updates the preview page.

        :param x264_psy_rd_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        psy_rd_value = round(x264_psy_rd_spinbutton.get_value(), 1)
        psy_rd_trellis_value = round(self.x264_handlers.get_psy_rd_trellis_value(), 2)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rd = psy_rd_value, psy_rd_trellis_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_psy_rd_trellis_spinbutton_value_changed(self, x264_psy_rd_trellis_spinbutton):
        """
        Applies the Psy RD options and updates the preview page.

        :param x264_psy_rd_trellis_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        psy_rd_value = round(self.x264_handlers.get_psy_rd_value(), 1)
        psy_rd_trellis_value = round(x264_psy_rd_trellis_spinbutton.get_value(), 2)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rd = psy_rd_value, psy_rd_trellis_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
