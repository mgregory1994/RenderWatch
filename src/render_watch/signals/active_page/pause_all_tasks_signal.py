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


class PauseAllTasksSignal:
    """
    Handles the signal emitted by the pause all tasks button on the active page's options menu.
    """

    def __init__(self, active_page_handlers, main_window_handlers):
        self.active_page_handlers = active_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_pause_all_tasks_button_clicked(self, pause_all_tasks_button):  # Unused parameters needed for this signal
        """
        Pauses all tasks on the active page.

        :param pause_all_tasks_button: Button that emitted the signal.
        """
        self.main_window_handlers.popdown_app_preferences_popover()

        for row in self.active_page_handlers.get_rows():
            row.signal_pause_button()
