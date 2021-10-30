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


class ClearAllTasksSignal:
    """
    Handles the signal emitted from the clear all completed tasks button on the completed page's options menu.
    """

    def __init__(self, completed_page_handlers, main_window_handlers):
        self.completed_page_handlers = completed_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_clear_all_completed_button_clicked(self, clear_all_completed_button):
        """
        Removes all completed tasks from the completed page.

        :param clear_all_completed_button: Button that emitted the signal.
        """
        self.completed_page_handlers.remove_all_rows()

        clear_all_completed_button.set_sensitive(False)
        self.main_window_handlers.popdown_app_preferences_popover()
