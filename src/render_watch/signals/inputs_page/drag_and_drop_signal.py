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


import os

from urllib.parse import unquote, urlparse

from render_watch.helpers import directory_helper

TARGET_TYPE_URI_LIST = 80


class DragAndDropSignal:
    """Handles the signal emitted when a user drags files over the inputs listbox."""

    def __init__(self, main_window_handlers):
        self.main_window_handlers = main_window_handlers

    # Unused parameters needed for this signal
    def on_inputs_list_drag_data_received(self,
                                          inputs_page_listbox,
                                          drag_context,
                                          x,
                                          y,
                                          data,
                                          target_type,
                                          timestamp):
        """Takes valid files or folders and adds them to the inputs page."""
        if target_type == TARGET_TYPE_URI_LIST:
            inputs = []
            inputs_uri = data.get_data().decode()
            for file_path_uri in inputs_uri.split():
                input_path = unquote(urlparse(file_path_uri).path)
                if self.main_window_handlers.is_file_inputs_enabled():
                    if os.path.isfile(input_path):
                        inputs.append(input_path)
                    else:
                        inputs.extend(directory_helper.get_files_in_directory(input_path, recursive=True))
                else:
                    if os.path.isdir(input_path):
                        inputs.append(input_path)
            if inputs:
                self.main_window_handlers.on_add_button_clicked(self.main_window_handlers.add_button, inputs=inputs)
