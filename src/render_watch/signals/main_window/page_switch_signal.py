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
    """
    Handles the signal emitted when the user switches to a different page.
    """

    def __init__(self, main_window_handlers, inputs_page_handlers):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers

    # Unused parameters needed for this signal
    def on_page_stack_visible_child_notify(self, page_stack, user_data=None):
        """
        Closes the settings sidebar and configures the current page's state.

        :param page_stack: Stack that emitted the signal.
        :param user_data: Signal user data.
        """
        self.main_window_handlers.toggle_settings_sidebar(is_closing_settings_sidebar=True)

        current_page = page_stack.get_visible_child()
        if current_page == self.main_window_handlers.inputs_page_paned:
            self.main_window_handlers.set_inputs_page_state()
        elif current_page == self.main_window_handlers.active_page_scroller:
            self.main_window_handlers.set_active_page_state()
        else:
            self.main_window_handlers.set_completed_page_state()
