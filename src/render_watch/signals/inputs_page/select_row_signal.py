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


import threading

from render_watch.startup import GLib


class SelectRowSignal:
    """
    Handles the signal emitted when an input becomes selected.
    """

    def __init__(self, inputs_page_handlers, settings_sidebar_handlers, main_window_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.main_window_handlers = main_window_handlers

    def on_inputs_list_row_selected(self, inputs_page_listbox, inputs_row):  # Unused parameters needed for this signal
        """
        When selected, allows for accessing the settings sidebar.
        When deselected, removes accessibility of the settings sidebar unless the "apply to all" setting is enabled.

        :param inputs_page_listbox: Gtk.Listbox containing the input.
        :param inputs_row: Gtk.ListboxRow that's being selected/deselected.
        """
        if inputs_row:
            self._set_selected_row_state(inputs_row)
        else:
            self._set_deselected_row_state()

    def _set_selected_row_state(self, inputs_row):
        self.inputs_page_handlers.set_input_settings_state(True)

        self.settings_sidebar_handlers.set_extra_settings_state(not inputs_row.ffmpeg.folder_state)
        threading.Thread(target=self._update_settings_sidebar, args=()).start()

    def _set_deselected_row_state(self):
        self.settings_sidebar_handlers.set_extra_settings_state(False)

        if self.inputs_page_handlers.is_apply_all_selected():
            return

        self.inputs_page_handlers.set_input_settings_state(False)
        self.main_window_handlers.toggle_settings_sidebar(is_closing_settings_sidebar=True)

    def _update_settings_sidebar(self):
        GLib.idle_add(self.settings_sidebar_handlers.set_settings)
