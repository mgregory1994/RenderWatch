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


class RemoveSignal:
    """
    Handles the signal emitted by the remove button from an input task.
    """

    def __init__(self, inputs_page_handlers, active_page_handlers, main_window_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.active_page_handlers = active_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_inputs_list_remove(self, inputs_page_listbox, inputs_row):  # Unused parameters needed for this signal
        """
        Updates the inputs page's options menu if there are no inputs and switches to the active page if there's any
        tasks running.

        :param inputs_page_listbox: Gtk.Listbox that lost a row.
        :param inputs_row: Gtk.Listboxrow that's being removed.
        """
        if self.inputs_page_handlers.get_rows():
            return

        self.inputs_page_handlers.set_remove_all_state()

        if self.active_page_handlers.get_rows():
            self.main_window_handlers.switch_to_active_page()
