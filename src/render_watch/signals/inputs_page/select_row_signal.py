"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""


import threading

from render_watch.startup import GLib


class SelectRowSignal:
    def __init__(self, inputs_page_handlers, settings_sidebar_handlers, main_window_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.main_window_handlers = main_window_handlers

    def on_inputs_list_row_selected(self, inputs_page_listbox, inputs_row):  # Unused parameters needed for this signal
        if inputs_row is not None:
            self.inputs_page_handlers.set_input_settings_state(True)
            self.settings_sidebar_handlers.set_extra_settings_state(not inputs_row.ffmpeg.folder_state)
            threading.Thread(target=self.__update_settings_sidebar, args=()).start()
        else:
            self.settings_sidebar_handlers.set_extra_settings_state(False)

            if self.inputs_page_handlers.is_apply_all_selected():
                return

            self.inputs_page_handlers.set_input_settings_state(False)
            self.main_window_handlers.show_settings_sidebar(False)

    def __update_settings_sidebar(self):
        GLib.idle_add(self.settings_sidebar_handlers.set_settings)
