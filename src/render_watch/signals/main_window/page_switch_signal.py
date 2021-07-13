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


class PageSwitchSignal:
    """Handles the signal emitted when the user switches to a different page."""

    def __init__(self, main_window_handlers, inputs_page_handlers):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_page_stack_visible_child_notify(self, page_stack, string):  # Unused parameters needed for this signal
        """Closes the settings sidebar and sets up the current page's state.

        :param page_stack:
            Stack that emitted the signal.
        :param string:
            Unused parameter.
        """
        self.main_window_handlers.show_settings_sidebar(False)

        current_page = page_stack.get_visible_child()
        if current_page == self.inputs_page_handlers.inputs_page_box:
            self.main_window_handlers.set_inputs_page_state()
        elif current_page == self.main_window_handlers.active_page_scroller:
            self.main_window_handlers.set_active_page_state()
        else:
            self.main_window_handlers.set_completed_page_state()
