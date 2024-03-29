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


class StopBenchmarkSignal:
    """
    Handles the signal emitted when the user stops the currently running benchmark.
    """

    def __init__(self, settings_sidebar_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers

    def on_benchmark_stop_button_clicked(self, benchmark_stop_button):  # Unused parameters needed for this signal
        """
        Stops the currently running benchmark.

        :param benchmark_stop_button: Button that emitted the signal.
        """
        threading.Thread(target=self.settings_sidebar_handlers.stop_benchmark_thread, args=(), daemon=True).start()
