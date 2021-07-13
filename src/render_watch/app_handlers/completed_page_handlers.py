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


from render_watch.signals.completed_page.add_task_signal import AddTaskSignal
from render_watch.signals.completed_page.remove_task_signal import RemoveTaskSignal
from render_watch.signals.completed_page.clear_all_tasks_signal import ClearAllTasksSignal
from render_watch.startup import Gtk


class CompletedPageHandlers:
    """Handles all widget changes on the completed page."""

    def __init__(self, gtk_builder, main_window_handlers):
        self.add_task_signal = AddTaskSignal(self)
        self.remove_task_signal = RemoveTaskSignal(self)
        self.clear_all_tasks_signal = ClearAllTasksSignal(self, main_window_handlers)
        self.signals_list = (self.add_task_signal, self.remove_task_signal, self.clear_all_tasks_signal)
        self.completed_page_listbox = gtk_builder.get_object('completed_list')
        self.clear_all_completed_button = gtk_builder.get_object("clear_all_completed_button")
        self.completed_page_listbox.set_header_func(self._completed_list_update_header, None)

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    # Unused parameters needed for this function
    @staticmethod
    def _completed_list_update_header(completed_page_listbox_row, previous_completed_page_listbox_row, data):
        # Adds a separator between Gtk.ListboxRow widgets.
        if previous_completed_page_listbox_row is None:
            completed_page_listbox_row.set_header(None)
        else:
            completed_page_listbox_row_header = completed_page_listbox_row.get_header()
            if completed_page_listbox_row_header is None:
                completed_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                completed_page_listbox_row_header.show()
                completed_page_listbox_row.set_header(completed_page_listbox_row_header)

    def get_rows(self):
        return self.completed_page_listbox.get_children()

    def set_clear_all_state(self, enabled):
        # Sets the page's options in the preferences menu for when the Gtk.Listbox is empty on the completed page.
        self.clear_all_completed_button.set_sensitive(enabled)

    def add_row(self, completed_page_listbox_row):
        self.completed_page_listbox.add(completed_page_listbox_row)
        self.completed_page_listbox.show_all()

    def remove_row(self, completed_row):
        self.completed_page_listbox.remove(completed_row)

    def remove_duplicate_row(self, completed_page_listbox_row):
        for listbox_row in self.get_rows():
            if listbox_row.file_path_link.get_uri() == completed_page_listbox_row.file_path_link.get_uri():
                listbox_row.on_remove_button_clicked(None)
                break
