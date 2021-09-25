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


class X265ProfileSignal:
    """Handles the signal emitted when the x265 Profile option is changed."""

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_profile_combobox_changed(self, profile_combobox):
        """Applies the Profile option and updates the preview page.

        :param profile_combobox:
            Combobox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        profile_index = profile_combobox.get_active()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.profile = profile_index
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
