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


class X265RdSignal:
    """
    Handles the signals emitted when x265 Rate Distortion related options are changed.
    """

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_rdo_level_spinbutton_value_changed(self, x265_rdo_level_spinbutton):
        """
        Applies the RDO Level option and updates the preview page.

        :param x265_rdo_level_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        rdo_level_value = x265_rdo_level_spinbutton.get_value_as_int()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rd = rdo_level_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rdoq_level_combobox_changed(self, x265_rdoq_level_combobox):
        """
        Applies the RDOQ Level option and updates the preview page.

        :param x265_rdoq_level_combobox: Combobox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        rdoq_level_index = x265_rdoq_level_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rdoq_level = rdoq_level_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rd_refine_checkbutton_toggled(self, x265_rd_refine_checkbutton):
        """
        Applies the RD Refine option and updates the preview page.

        :param x265_rd_refine_checkbutton: Checkbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        is_rd_refine_enabled = x265_rd_refine_checkbutton.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rd_refine = is_rd_refine_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
