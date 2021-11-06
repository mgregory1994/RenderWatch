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


class Vp9QualitySignal:
    """
    Handles the signal emitted when the VP9 Quality option is toggled.
    """

    def __init__(self, vp9_handlers, inputs_page_handlers):
        self.vp9_handlers = vp9_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_vp9_quality_combobox_changed(self, quality_combobox):
        """
        Applies the Quality option and updates the preview page.

        :param quality_combobox: Combobox that emitted the signal.
        """
        if self.vp9_handlers.is_widgets_setting_up:
            return

        quality_index = quality_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.quality = quality_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
