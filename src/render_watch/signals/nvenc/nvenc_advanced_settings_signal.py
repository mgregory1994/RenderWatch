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


class NvencAdvancedSettingsSignal:
    """Handles the signal emitted when the NVENC advanced settings are toggled."""

    def __init__(self, nvenc_handlers, inputs_page_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers

    # Unused parameter needed for signal
    def on_nvenc_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        """Updates the NVENC widgets and shows the advanced settings options.

        :param advanced_settings_switch:
            Switch that emitted the signal.
        :param user_data:
            Unused parameter.
        """
        advanced_settings_enabled = advanced_settings_switch.get_active()
        self.nvenc_handlers.set_advanced_settings_state(advanced_settings_enabled)
        self.nvenc_handlers.update_qp_from_advanced_settings()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        threading.Thread(target=self.nvenc_handlers.update_settings, args=()).start()
