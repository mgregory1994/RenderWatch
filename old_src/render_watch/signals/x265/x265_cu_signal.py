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


class X265CuSignal:
    """
    Handles the signals emitted when x265 CU related options are changed.
    """

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_max_cu_combobox_changed(self, x265_max_cu_combobox):
        """
        Applies the Max CU option and updates the preview page.

        :param x265_max_cu_combobox: Combobox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        max_cu_index = x265_max_cu_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.ctu = max_cu_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_min_cu_combobox_changed(self, x265_min_cu_combobox):
        """
        Applies the Min CU option and updates the preview page.

        :param x265_min_cu_combobox: Combobox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        min_cu_index = x265_min_cu_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.min_cu_size = min_cu_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
