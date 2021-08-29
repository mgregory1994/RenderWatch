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


class PreviewDurationSignal:
    """Handles the signal emitted when a Preview Duration option is changed on the preview page."""

    def __init__(self, preview_page_handlers):
        self.preview_page_handlers = preview_page_handlers

    def on_preview_duration_toggled(self, preview_duration_radiobutton):
        """Runs a preview for the selected duration.

        :param preview_duration_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not preview_duration_radiobutton.get_active():
            return

        self.preview_page_handlers.stop_preview_thumbnail_thread()

        start_time = round(self.preview_page_handlers.get_current_time_value(), 1)
        preview_duration = self.preview_page_handlers.get_preview_duration()
        self.preview_page_handlers.set_preview_duration_state()
        self.preview_page_handlers.run_preview_thumbnail_thread(start_time, preview_duration)
