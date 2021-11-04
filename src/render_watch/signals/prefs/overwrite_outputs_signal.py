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


class OverwriteOutputsSignal:
    """
    Handles the signal emitted when the Overwrite Existing Outputs option is changed in the preferences dialog.
    """

    def __init__(self, application_preferences):
        self.application_preferences = application_preferences

    def on_overwrite_outputs_checkbutton_toggled(self, overwrite_outputs_checkbutton):
        """
        Applies the Overwrite Existing Outputs option in the application's preferences.

        :param overwrite_outputs_checkbutton: Checkbox that emitted the signal.
        """
        self.application_preferences.is_overwriting_outputs = overwrite_outputs_checkbutton.get_active()
