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


class X264AdvancedSettingsSignal:
    """Handles the signal emitted when the x264 Advanced Settings option is toggled."""

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    # Unused parameters needed for this signal
    def on_x264_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        """Toggles the Advanced Settings widgets and applies the advanced settings.

        :param advanced_settings_switch:
            Switch that emitted the signal.
        :param user_data:
            Unused parameter.
        """
        self.x264_handlers.set_advanced_settings_state(advanced_settings_switch.get_active())

        if self.x264_handlers.is_widgets_setting_up:
            return

        threading.Thread(target=self.x264_handlers.update_settings, args=()).start()
