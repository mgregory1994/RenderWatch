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


import logging
import threading
import queue

from concurrent.futures import ThreadPoolExecutor

from render_watch.startup import GLib


class ParallelEncodeTask:
    """
    Queues parallel encode tasks and runs them through the encoder.
    """

    def __init__(self, encoder_queue, application_preferences):
        self.encoder_queue = encoder_queue
        self.parallel_tasks_queue = queue.Queue()
        self.number_of_tasks = application_preferences.parallel_tasks

        self.parallel_tasks_startup_thread = threading.Thread(target=self._start_parallel_tasks_thread,
                                                              args=(),
                                                              daemon=True)
        self.parallel_tasks_startup_thread.start()

    def _start_parallel_tasks_thread(self):
        with ThreadPoolExecutor(max_workers=self.number_of_tasks) as future_executor:
            future_executor.map(self._parse_parallel_tasks_queue, range(self.number_of_tasks))

    def _parse_parallel_tasks_queue(self, worker_id):  # Unused parameter required for this function
        try:
            while True:
                active_row = self.parallel_tasks_queue.get()
                if not active_row:
                    break

                try:
                    self.encoder_queue.wait_for_standard_tasks()

                    self.encoder_queue.add_to_running_tasks(active_row)
                    self._run_parallel_encode_task(active_row)
                except:
                    logging.exception('--- FAILED TO RUN PARALLEL TASK PROCESS ---')
                finally:
                    if active_row.ffmpeg.folder_state and not active_row.ffmpeg.watch_folder:
                        GLib.idle_add(active_row.set_finished_state)
                    if not active_row.ffmpeg.watch_folder:
                        self.encoder_queue.remove_from_running_tasks(active_row)

                    self.parallel_tasks_queue.task_done()
        except:
            logging.exception('--- PARALLEL TASKS THREAD FAILED ---')

    def _run_parallel_encode_task(self, active_row):
        if active_row.stopped:
            return

        with ThreadPoolExecutor(max_workers=2) as future_executor:
            if active_row.ffmpeg.is_video_settings_nvenc():
                self.encoder_queue.start_parallel_nvenc_task(active_row, wait=False)

                return
            elif active_row.ffmpeg.folder_state:
                future_executor.submit(self.encoder_queue.start_folder_task, active_row)
            else:
                future_executor.submit(self.encoder_queue.run_encode_task, active_row)

            future_executor.submit(active_row.set_start_state)

    def add_task(self, active_row):
        """
        Adds a Gtk.ListboxRow to the encoder queue as a new task.
        """
        self.parallel_tasks_queue.put(active_row)

    def set_stop_state(self):
        """
        Sends a stop task to the encoder queue.
        """
        for index in range(self.number_of_tasks):
            self.parallel_tasks_queue.put(False)

    def is_queue_empty(self):
        return self.parallel_tasks_queue.empty()

    def join_queue(self):
        self.parallel_tasks_queue.join()

    def empty_queue(self):
        while not self.is_queue_empty():
            self.parallel_tasks_queue.get()
