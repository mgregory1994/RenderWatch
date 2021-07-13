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


class LiveThumbnailsSignal:
    """Handles the signals emitted from the live thumbnails switch on the active page's options menu."""

    def __init__(self, active_page_handlers):
        self.active_page_handlers = active_page_handlers

    # Unused parameters needed for this signal
    def on_live_thumbnails_switch_state_set(self, live_thumbnails_switch, user_data):
        """Toggles the live preview for all Gtk.Listboxrow items on the active page.

        :param live_thumbnails_switch:
            Switch button that's emitting the signal.
        :param user_data:
            Unused parameter.
        """
        for row in self.active_page_handlers.get_rows():
            row.live_thumbnail = live_thumbnails_switch.get_active()
