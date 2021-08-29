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
    """Handles the signal emitted from the remove button on an inputs row."""

    def __init__(self, inputs_row, inputs_page_handlers):
        self.inputs_row = inputs_row
        self.inputs_page_handlers = inputs_page_handlers

    def on_remove_button_clicked(self, remove_button):  # Unused parameters needed for this signal
        """Removes the row from the inputs page.

        :param remove_button:
            Button that emitted the signal.
        """
        self.inputs_page_handlers.remove_row(self.inputs_row)
