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


class X265VbvSignal:
    """
    Handles the signals emitted when x265 Variable Bitrate related options are changed.
    """

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_vbv_maxrate_spinbutton_value_changed(self, x265_vbv_maxrate_spinbutton):
        """
        Applies the VBV Maxrate option and updates the preview page.

        :param x265_vbv_maxrate_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return
        if not self.x265_handlers.is_advanced_settings_enabled():
            return
        if self.x265_handlers.update_vbv_maxrate():
            return

        vbv_maxrate_value = x265_vbv_maxrate_spinbutton.get_value_as_int()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_maxrate = vbv_maxrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_vbv_bufsize_spinbutton_value_changed(self, x265_vbv_bufsize_spinbutton):
        """
        Applies the VBV Bufsize option and updates the preview page.

        :param x265_vbv_bufsize_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return
        if not self.x265_handlers.is_advanced_settings_enabled():
            return

        vbv_bufsize_value = x265_vbv_bufsize_spinbutton.get_value_as_int()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_bufsize = vbv_bufsize_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
