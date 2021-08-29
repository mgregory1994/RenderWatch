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


class PrefsWaitForTasksSignal:
    """Handles the signal emitted when the Watch Folder Wait For Other Tasks
    option is changed in the preferences dialog."""

    def __init__(self, preferences):
        self.preferences = preferences

    def on_prefs_wait_for_tasks_checkbox_toggled(self, watch_folder_wait_for_other_tasks_checkbox):
        """Applies the Watch Folder Wait For Other Tasks option in the application's preferences.

        :param watch_folder_wait_for_other_tasks_checkbox:
            Checkbox that emitted the signal.
        """
        self.preferences.watch_folder_wait_for_other_tasks = watch_folder_wait_for_other_tasks_checkbox.get_active()
