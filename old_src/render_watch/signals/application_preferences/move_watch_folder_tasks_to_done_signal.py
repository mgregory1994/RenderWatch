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


class MoveWatchFolderTasksToDoneSignal:
    """
    Handles the signal emitted when the Move Completed Watch Folder Tasks to the Done Folder option is changed in the
    preferences dialog.
    """

    def __init__(self, application_preferences):
        self.application_preferences = application_preferences

    def on_move_watch_folder_tasks_to_done_switch_state_set(self,
                                                            move_watch_folder_tasks_to_done_switch,
                                                            user_data=None):
        """
        Applies the Move Completed Watch Folder Tasks to the Done Folder option in the application's preferences.

        :param move_watch_folder_tasks_to_done_switch: Switch that emitted the signal.
        """
        self.application_preferences.is_watch_folder_move_tasks_to_done_enabled = move_watch_folder_tasks_to_done_switch.get_active()
