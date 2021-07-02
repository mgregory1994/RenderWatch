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


class X265AqSignal:
    """Handles the signals emitted when the x265 AQ related options are changed."""

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_aq_mode_combobox_changed(self, aq_mode_combobox):
        """Applies the AQ Mode option and updates the preview page.

        :param aq_mode_combobox:
            Combobox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        aq_mode_index = aq_mode_combobox.get_active()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_mode = aq_mode_index
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_aq_strength_spinbutton_value_changed(self, aq_strength_spinbutton):
        """Applies the AQ Strength option and updates the preview page.

        :param aq_strength_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        aq_strength_value = aq_strength_spinbutton.get_value()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_strength = aq_strength_value
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_hevc_aq_checkbox_toggled(self, hevc_aq_checkbox):
        """Applies the HEVC AQ option and updates the preview page.

        :param hevc_aq_checkbox:
            Checkbox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        hevc_aq_enabled = hevc_aq_checkbox.get_active()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.hevc_aq = hevc_aq_enabled
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
