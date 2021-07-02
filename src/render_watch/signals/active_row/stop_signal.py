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


class StopSignal:
    """Handles the signals emitted from the active row's stop widget."""

    def __init__(self, active_row):
        self.active_row = active_row

    def on_stop_button_clicked(self, stop_button):  # Unused parameters needed for this signal
        """Stops this task.

        :param stop_button:
            Button that emitted the signal.
        """
        threading.Thread(target=self.active_row.stop_and_remove_row, args=()).start()
