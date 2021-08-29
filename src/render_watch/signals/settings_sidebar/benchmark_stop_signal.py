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


class BenchmarkStopSignal:
    """Handles the signal emitted when the user stops a currently running benchmark."""

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_benchmark_stop_button_clicked(self, benchmark_stop_button):  # Unused parameters needed for this signal
        """Stops the currently running benchmark task.

        :param benchmark_stop_button:
            Button that emitted the signal.
        """
        benchmark_thread_stopping = self.settings_sidebar_handlers.benchmark_thread_stopping
        threading.Thread(target=benchmark_thread_stopping, args=(), daemon=True).start()
