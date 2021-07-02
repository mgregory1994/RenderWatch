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


class NvencAQSignal:
    """Handles the signals emitted when NVENC AQ related settings are changed."""

    def __init__(self, nvenc_handlers, inputs_page_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_nvenc_spatial_radiobutton_toggled(self, spatial_radiobutton):
        """Applies the spatial AQ option and updates the preview page.

        :param spatial_radiobutton:
            Radiobutton that emitted the signal.
        """
        self.nvenc_handlers.set_aq_strength_state(spatial_radiobutton.get_active())

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        spatial_enabled = spatial_radiobutton.get_active()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.spatial_aq = spatial_enabled
            ffmpeg.video_settings.temporal_aq = not spatial_enabled
            if spatial_enabled:
                self.nvenc_handlers.signal_aq_strength_spinbutton()
            else:
                ffmpeg.video_settings.aq_strength = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_aqstrength_spinbutton_value_changed(self, aqstrength_spinbutton):
        """Applies the AQ Strength option and updates the preview page.

        :param aqstrength_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        aq_strength_value = aqstrength_spinbutton.get_value_as_int()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_strength = aq_strength_value
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
