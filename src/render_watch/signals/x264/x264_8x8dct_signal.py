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


class X2648x8DctSignal:
    """Handles the signal emitted when the x264 8x8DCT option is changed."""

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_8x8dct_checkbox_toggled(self, dct8x8_checkbox):
        """Applies the 8x8DCT option and updates the preview page.

        :param dct8x8_checkbox:
            Checkbox that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dct8x8 = dct8x8_checkbox.get_active()
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
