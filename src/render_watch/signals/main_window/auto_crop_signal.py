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


class AutoCropSignal:
    """Handles the signal emitted when the auto crop setting is toggled from the options menu."""

    def __init__(self, inputs_page_handlers):
        self.inputs_page_handlers = inputs_page_handlers

    def on_auto_crop_button_toggled(self, auto_crop_checkbox):
        """Applies the folder auto crop setting for all folder inputs.

        :param auto_crop_checkbox:
            Checkbox that emitted the signal.
        """
        for inputs_page_listbox_row in self.inputs_page_handlers.get_rows():
            if inputs_page_listbox_row.ffmpeg.folder_state:
                inputs_page_listbox_row.ffmpeg.folder_auto_crop = auto_crop_checkbox.get_active()
