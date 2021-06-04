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


class SettingsSidebarSignal:
    def __init__(self, main_window_handlers):
        self.main_window_handlers = main_window_handlers

    def on_show_settings_button_clicked(self, show_settings_button):  # Unused parameters needed for this signal
        self.main_window_handlers.show_settings_sidebar(True)

    def on_hide_settings_button_clicked(self, hide_settings_button):  # Unused parameters needed for this signal
        self.main_window_handlers.show_settings_sidebar(False)
