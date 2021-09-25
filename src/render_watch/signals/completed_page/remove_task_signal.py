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


class RemoveTaskSignal:
    """Handles the signal emitted from remove button on a completed page's listbox row."""

    def __init__(self, completed_page_handlers):
        self.completed_page_handlers = completed_page_handlers

    def on_completed_list_remove(self, completed_page_listbox, completed_page_listbox_row):
        """Updates the completed page's menu options when a row is removed.

        :param completed_page_listbox:
            Gtk.Listbox that's losing a listbox row.
        :param completed_page_listbox_row:
            Gtk.Listboxrow that's being removed.
        """
        if not completed_page_listbox.get_children():
            self.completed_page_handlers.set_clear_all_state(False)

        completed_page_listbox_row.destroy()
