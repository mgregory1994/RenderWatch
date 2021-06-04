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
import time


class StartAllSignal:
    def __init__(self, inputs_page_handlers, main_window_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_start_all_button_clicked(self, start_all_button):  # Unused parameters needed for this signal
        self.main_window_handlers.popdown_app_preferences_popover()
        threading.Thread(target=self.__start_all, args=()).start()

    def __start_all(self):
        time.sleep(.2)

        for row in self.inputs_page_handlers.get_rows():
            row.on_start_button_clicked(None)
