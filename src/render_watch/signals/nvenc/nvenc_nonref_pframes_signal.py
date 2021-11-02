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


class NvencNonRefPFramesSignal:
    """
    Handles the signal emitted when the NVENC Non-Ref P-Frames option is changed.
    """

    def __init__(self, nvenc_handlers, inputs_page_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_nvenc_nonref_p_frames_checkbutton_toggled(self, nvenc_nonref_p_frames_checkbutton):
        """
        Applies the Non-Ref P-Frames option and updates the preview page.

        :param nvenc_nonref_p_frames_checkbutton: Checkbox that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        nonref_pframes_enabled = nvenc_nonref_p_frames_checkbutton.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.non_ref_p = nonref_pframes_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
