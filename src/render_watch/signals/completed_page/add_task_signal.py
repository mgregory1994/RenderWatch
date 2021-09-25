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


class AddTaskSignal:
    """Handles the signal emitted from the completed page's Gtk.Listbox when a row is added."""

    def __init__(self, completed_page_handlers):
        self.completed_page_handlers = completed_page_handlers

    def on_completed_list_add(self, completed_page_listbox, row):  # Unused parameters needed for this signal
        """Updates the completed page's options menu when a new row is added.

        :param completed_page_listbox:
            Gtk.Listbox that was added to.
        :param row:
            Gtk.Listboxrow that was added.
        """
        self.completed_page_handlers.set_clear_all_state(True)
