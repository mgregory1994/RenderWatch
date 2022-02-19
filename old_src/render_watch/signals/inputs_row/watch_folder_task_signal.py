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


class WatchFolderTaskSignal:
    """
    Handles the signal emitted when the watch folder option is selected on an input task.
    """

    def __init__(self, input_task):
        self.input_task = input_task

    def on_watch_folder_task_radiobutton_toggled(self, watch_folder_task_radiobutton):
        """
        Sets the watch folder option for the input task.

        :param watch_folder_task_radiobutton: Radiobutton that emitted the signal.
        """
        self.input_task.ffmpeg.watch_folder = watch_folder_task_radiobutton.get_active()
