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


class DarkModeSignal:
    """
    Handles the signal emitted when the Dark Mode option is toggled in the preferences dialog.
    """

    def __init__(self, gtk_settings, application_preferences):
        self.gtk_settings = gtk_settings
        self.application_preferences = application_preferences

    # Unused parameters needed for this signal
    def on_dark_mode_switch_state_set(self, dark_mode_switch, user_data=None):
        """
        Toggles the Dark Mode option in the application's preferences and Toggles the dark mode UI immediately.

        :param dark_mode_switch: Switch that emitted the signal.
        :param user_data: Signal user data.
        """
        dark_mode = dark_mode_switch.get_active()
        self.application_preferences.is_dark_mode_enabled = dark_mode
        self.gtk_settings.set_property('gtk-application-prefer-dark-theme', dark_mode)
