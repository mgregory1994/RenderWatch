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


class X264DeblockSignal:
    """Handles the signals emitted when the x264 Deblock related options are changed."""

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_no_deblock_checkbox_toggled(self, no_deblock_checkbox):
        """Applies the No Deblock option and updates the preview page.

        :param no_deblock_checkbox:
            Checkbox that emitted the signal.
        """
        self.x264_handlers.set_deblock_state(not no_deblock_checkbox.get_active())

        if self.x264_handlers.is_widgets_setting_up:
            return

        no_deblock_enabled = no_deblock_checkbox.get_active()
        deblock_settings = self.x264_handlers.get_deblock_settings()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_deblock = no_deblock_enabled
            ffmpeg.video_settings.deblock = deblock_settings
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    # Unused parameters needed for this signal
    def on_x264_deblock_alpha_spinbutton_value_changed(self, deblock_alpha_spinbutton):
        """Applies the Deblock option and updates the preview page.

        :param deblock_alpha_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        deblock_settings = self.x264_handlers.get_deblock_settings()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    # Unused parameters needed for this signal
    def on_x264_deblock_beta_spinbutton_value_changed(self, deblock_beta_spinbutton):
        """Applies the Deblock option and updates the preview page.

        :param deblock_beta_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        deblock_settings = self.x264_handlers.get_deblock_settings()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
