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


class StartSignal:
    def __init__(self, active_row):
        self.active_row = active_row

    def on_start_button_clicked(self, start_button):  # Unused parameters needed for this signal
        self.active_row.paused = False

        self.active_row.task_threading_event.set()
        self.active_row.set_encoding_state()
