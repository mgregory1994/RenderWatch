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


class PageReturnSignal:
    def __init__(self, inputs_page_handlers, trim_page_handlers, crop_page_handlers, preview_page_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.trim_page_handlers = trim_page_handlers
        self.crop_page_handlers = crop_page_handlers
        self.preview_page_handlers = preview_page_handlers

    def on_return_to_inputs_button_clicked(self, return_to_inputs_button):  # Unused parameters needed for this signal
        self.inputs_page_handlers.set_inputs_state()
        self.trim_page_handlers.reset_trim_page()
        self.crop_page_handlers.reset_crop_page()
        self.preview_page_handlers.reset_preview_page()
        threading.Thread(target=self.__update_selected_row, args=()).start()

    def __update_selected_row(self):
        row = self.inputs_page_handlers.get_selected_row()

        GLib.idle_add(row.setup_labels)
        row.setup_preview_thumbnail()
