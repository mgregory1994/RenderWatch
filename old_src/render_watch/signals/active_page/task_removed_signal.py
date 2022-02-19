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


from render_watch.app_handlers.completed_row import CompletedRow


class TaskRemovedSignal:
    """
    Handles the signal emitted when a task is removed from the active page.
    """

    def __init__(self, active_page_handlers, completed_page_handlers, preferences):
        self.active_page_handlers = active_page_handlers
        self.completed_page_handlers = completed_page_handlers
        self.preferences = preferences

    def on_active_list_remove(self, active_page_listbox, active_page_listbox_row):
        """
        Moves task to the completed page and updates the active page.

        :param active_page_listbox: Gtk.Listbox that's losing a row.
        :param active_page_listbox_row: Gtk.Listboxrow that's being removed.
        """
        self._add_row_to_completed_page(active_page_listbox_row)

        if active_page_listbox.get_children() is None:
            self.active_page_handlers.set_page_options_state(False)

    def _add_row_to_completed_page(self, active_row):
        if self._is_row_finished(active_row):
            completed_row = CompletedRow(active_row, self.completed_page_handlers, self.preferences)
            self.completed_page_handlers.remove_duplicate_row(completed_row)
            self.completed_page_handlers.add_row(completed_row)

    @staticmethod
    def _is_row_finished(active_row):
        return active_row \
               and active_row.finished \
               and not active_row.stopped \
               and not active_row.failed
