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


class TrimSignal:
    """
    Handles the signal emitted when the Trim Page button is pressed.
    """

    def __init__(self, trim_page_handlers, inputs_page_handlers):
        self.trim_page_handlers = trim_page_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_trim_button_clicked(self, trim_button):  # Unused parameters needed for this signal
        """
        Configures and shows the Trim Page.

        :param trim_button: Button that emitted the signal.
        """
        if not self.inputs_page_handlers.is_trim_state():
            self.inputs_page_handlers.set_trim_state()
            self.trim_page_handlers.setup_trim_page()
