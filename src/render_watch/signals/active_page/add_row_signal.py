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


class AddRowSignal:
    """
    Handles the signal emitted from adding a task to the active page.
    """

    def __init__(self, active_page_handlers):
        self.active_page_handlers = active_page_handlers

    def on_active_list_add(self, active_page_listbox, active_row):  # Unused parameters needed for this signal
        """
        Configures the new task's active row and updates the active page's options menu.

        :param active_page_listbox: Gtk.Listbox that's being added to.
        :param active_row: Gtk.Listboxrow being added.
        """
        active_row.live_thumbnail = self.active_page_handlers.is_live_thumbnails_enabled()

        self.active_page_handlers.set_page_options_state(True)
