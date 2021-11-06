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


class X264RefsSignal:
    """
    Handles the signals emitted when x264 References Frames related options are changed.
    """

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_reference_frames_spinbutton_value_changed(self, x264_ref_spinbutton):
        """
        Applies the Reference Frames option and updates the preview page.

        :param x264_ref_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.ref = x264_ref_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_mixed_refs_checkbutton_toggled(self, x264_mixed_refs_checkbutton):
        """
        Applies the Mixed Reference Frames option and updates the preview page.

        :param x264_mixed_refs_checkbutton: Checkbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.mixed_refs = x264_mixed_refs_checkbutton.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
