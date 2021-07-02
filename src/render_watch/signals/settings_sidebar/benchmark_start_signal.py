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

from render_watch.encoding import preview


class BenchmarkStartSignal:
    """Handles the signal emitted when the user starts the benchmark utility in the settings sidebar."""

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers, preferences):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences

    def on_benchmark_start_button_clicked(self, benchmark_start_button):  # Unused parameters needed for this signal
        """Runs a benchmark of the selected input's ffmpeg settings object.

        :param benchmark_start_button:
            Button that emitted the signal.
        """
        ffmpeg = self.inputs_page_handlers.get_selected_row().ffmpeg

        if ffmpeg is None:
            return

        threading.Thread(target=self._start_benchmark_thread, args=(ffmpeg,), daemon=True).start()

    def _start_benchmark_thread(self, ffmpeg):
        # Stops currently running benchmark, then runs a new benchmark.
        self.settings_sidebar_handlers.benchmark_thread_stopping()

        benchmark_thread_stopping = self.settings_sidebar_handlers.benchmark_thread_stopping
        with self.settings_sidebar_handlers.benchmark_thread_lock:
            self.benchmark_thread = threading.Thread(target=preview.start_benchmark,
                                                     args=(ffmpeg,
                                                           self,
                                                           lambda: benchmark_thread_stopping,
                                                           self.preferences))
            self.benchmark_thread.start()
