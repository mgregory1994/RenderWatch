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


class SettingsSidebarSignal:
    """
    Handles the signals emitted when the settings sidebar is opened/closed.
    """

    def __init__(self, main_window_handlers):
        self.main_window_handlers = main_window_handlers

    # Unused parameters needed for this signal
    def on_toggle_settings_sidebar_button_clicked(self, toggle_settings_sidebar_button):
        """
        Toggles the settings sidebar.

        :param toggle_settings_sidebar_button: Button that emitted the signal.
        """
        self.main_window_handlers.toggle_settings_sidebar()
