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


class RemoveTaskSignal:
    """
    Handles the signal emitted from the remove task button on an input task.
    """

    def __init__(self, input_task, inputs_page_handlers):
        self.input_task = input_task
        self.inputs_page_handlers = inputs_page_handlers

    def on_remove_input_task_button_clicked(self, remove_task_button):  # Unused parameters needed for this signal
        """
        Removes the task from the inputs page.

        :param remove_task_button: Button that emitted the signal.
        """
        self.inputs_page_handlers.remove_row(self.input_task)
