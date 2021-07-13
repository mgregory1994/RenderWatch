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


import threading


class X265AdvancedSettingsSignal:
    """Handles the signal emitted when the x265 Advanced Settings option is changed."""

    def __init__(self, x265_handlers):
        self.x265_handlers = x265_handlers

    # Unused parameters needed for this signal
    def on_x265_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        """Toggles the advanced settings widgets and applies the advanced settings.

        :param advanced_settings_switch:
            Switch that emitted the signal.
        :param user_data:
            Unused parameter.
        """
        self.x265_handlers.set_advanced_settings_state(advanced_settings_switch.get_active())

        if self.x265_handlers.is_widgets_setting_up:
            return

        threading.Thread(target=self.x265_handlers.update_settings, args=()).start()
