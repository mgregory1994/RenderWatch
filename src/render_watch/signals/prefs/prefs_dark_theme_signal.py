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


class PrefsDarkThemeSignal:
    def __init__(self, gtk_settings, preferences):
        self.gtk_settings = gtk_settings
        self.preferences = preferences

    # Unused parameters needed for this signal
    def on_prefs_dark_theme_switch_state_set(self, dark_theme_switch, user_data):
        dark_mode = dark_theme_switch.get_active()
        self.preferences.use_dark_mode = dark_mode

        self.gtk_settings.set_property('gtk-application-prefer-dark-theme', dark_mode)
