# Copyright 2022 Michael Gregory
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
import os.path
import threading
import queue
import time
import shutil

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from render_watch.encode import encoder, watch_folder
from render_watch.ffmpeg import encoding
from render_watch.helpers import nvidia_helper, directory_helper
from render_watch import app_preferences


COPY_CODEC_TASK_WORKERS = 1


class TaskQueue:
    """Class that schedules encoding tasks for encoding."""

    def __init__(self, app_settings: app_preferences.Settings):
        """
        Initializes the TaskQueue class with the variables necessary for scheduling encoding tasks into the
        proper tasks queue.

        Parameters:
            app_settings: Application settings.
        """
        self.app_settings = app_settings
        self.is_using_parallel_tasks_queue = self.app_settings.is_encoding_parallel_tasks
        self._running_tasks = []
        self._running_tasks_lock = threading.Lock()
        self._standard_tasks_queue = _StandardTasksQueue(self)
        self._parallel_tasks_queue = _ParallelTasksQueue(self, self.app_settings)
        self._watch_folder_tasks_queue = _WatchFolderTasksQueue(self, self.app_settings)

    def add_encoding_task(self, encoding_task: encoding.Task):
        """
        Adds the encoding task to the proper tasks queue based on whether the task is a watch folder or if the
        user has enabled parallel tasks.

        Parameters:
            encoding_task: Encoding task to add to one of the task queues.

        Returns:
            None
        """
        if encoding_task.is_watch_folder:
            self._watch_folder_tasks_queue.add_encoding_task(encoding_task)
        elif self.is_using_parallel_tasks_queue:
            self._parallel_tasks_queue.add_encoding_task(encoding_task)
        else:
            self._standard_tasks_queue.add_encoding_task(encoding_task)

    def add_to_running_tasks(self, encoding_task: encoding.Task):
        """
        Adds the given encoding task to the list of currently running tasks.

        Parameters:
            encoding_task: Encoding task to add to the list of currently running tasks.

        Returns:
            None
        """
        with self._running_tasks_lock:
            self._running_tasks.append(encoding_task)

    def remove_from_running_tasks(self, encoding_task: encoding.Task):
        """
        Removes the given encoding task from the list of currently running tasks.

        Parameters:
            encoding_task: Encoding task to removed from the list of running tasks.

        Returns:
            None
        """
        try:
            with self._running_tasks_lock:
                self._running_tasks.remove(encoding_task)
        except ValueError:
            logging.exception('--- TASK NOT IN RUNNING TASKS LIST ---\n' + encoding_task.output_file.file_path)

    def get_currently_running_tasks(self) -> list:
        """
        Returns a list that contains all the currently running encoding tasks when this method was called.

        Returns:
            List containing all the currently running encoding tasks when this method was called.
        """
        with self._running_tasks_lock:
            running_tasks_list_copy = []
            running_tasks_list_copy.extend(self._running_tasks)

            return running_tasks_list_copy

    def wait_for_standard_tasks(self):
        """
        Blocks the calling thread until the standard tasks queue is empty.

        Returns:
            None
        """
        if self.is_using_parallel_tasks_queue:
            self._standard_tasks_queue.join_queue()

    def wait_for_parallel_tasks(self):
        """
        Blocks the calling thread until the parallel tasks queue is empty.

        Returns:
            None
        """
        if not self.is_using_parallel_tasks_queue:
            self._parallel_tasks_queue.join_queue()

    def wait_for_watch_folder_tasks(self):
        """
        Polls the list of running encoding tasks and checks to see if any of them are watch folder tasks.
        Stops polling when there are no watch folder tasks running. This will block the calling thread until there are
        no running watch folder tasks.

        Returns:
            None
        """
        while self._watch_folder_task_exists_in_running_tasks():
            time.sleep(5)

    def _watch_folder_task_exists_in_running_tasks(self) -> bool:
        # Returns whether any of the currently running encoding tasks are watch folder tasks.
        for encoding_task in self.get_currently_running_tasks():
            if encoding_task.is_watch_folder \
                    and not encoding_task.is_idle \
                    and not encoding_task.is_stopped \
                    and encoding_task.has_started:
                return True
        return False

    def wait_for_all_tasks(self):
        """
        Blocks the calling thread until both the standard and parallel task queues are empty.

        Returns:
            None
        """
        self._standard_tasks_queue.join_queue()
        self._parallel_tasks_queue.join_queue()

    def run_encoding_task(self, encoding_task: encoding.Task):
        """
        Sends the given encoding task to the encoder. If the encoding task is a folder task, then the files contained in
        that folder are sent to the encoder.

        Parameters:
            encoding_task: Encoding task to send to the encoder.

        Returns:
            None
        """
        if encoding_task.is_stopped:
            return

        if encoding_task.input_file.is_folder:
            self._run_folder_encoding_task(encoding_task)
        else:
            TaskQueue._run_standard_encoding_task(encoding_task)

    @staticmethod
    def _run_standard_encoding_task(encoding_task: encoding.Task):
        # Sends the given encoding task to the encoder.
        if encoding_task.is_video_nvenc():
            nvidia_helper.Compatibility.wait_until_nvenc_available()

        encoding_task.has_started = True
        encoding_task.has_failed = encoder.run_encode_subprocess(encoding_task) != 0

    def _run_folder_encoding_task(self, encoding_task: encoding.Task):
        # Creates a child encoding task for each file in the folder task and sends them to the encoder.
        folder_dir = encoding_task.input_file.dir
        is_recursively_searching_folder = encoding_task.input_file.is_recursively_searching_folder

        for file_path in directory_helper.get_files_in_directory(folder_dir, recursive=is_recursively_searching_folder):
            child_encoding_task = encoding_task.get_copy()
            child_encoding_task.input_file = encoding.input.InputFile(file_path)
            child_encoding_task.output_file = encoding.output.OutputFile(file_path, self.app_settings)

            directory_helper.fix_same_name_occurences(encoding_task, self.app_settings)

            if child_encoding_task.input_file.is_valid():
                TaskQueue._run_standard_encoding_task(child_encoding_task)
                encoding_task.has_failed = child_encoding_task.has_failed

    def kill(self):
        """
        Empties and stops all task queues and stops all currently running encoding tasks.

        Returns:
            None
        """
        self._empty_task_queues()
        self._add_stop_tasks_to_queues()
        self._stop_running_tasks()

    def _empty_task_queues(self):
        # Empties all task queues.
        self._standard_tasks_queue.empty_queue()
        self._parallel_tasks_queue.empty_queue()
        self._watch_folder_tasks_queue.empty_queue()

    def _add_stop_tasks_to_queues(self):
        # Sends a stop task to all task queues.
        self._standard_tasks_queue.add_stop_task()
        self._parallel_tasks_queue.add_stop_task()
        self._watch_folder_tasks_queue.add_stop_task()

    def _stop_running_tasks(self):
        # Sets the stopped status for all running encoding tasks.
        for encoding_task in self._running_tasks:
            encoding_task.paused_threading_event.set()
            encoding_task.is_stopped = True


class _StandardTasksQueue:
    """Class that configures the queue for standard encoding tasks."""

    def __init__(self, task_queue: TaskQueue):
        """
        Initializes the _StandardTasksQueue class with the variables necessary to queue and process
        standard encoding tasks.

        Parameters:
            task_queue: The task queue that initialized this class.
        """
        self.task_queue = task_queue
        self.standard_tasks_queue = queue.Queue()

        self._initialize_queue_loop()

    def _initialize_queue_loop(self):
        # Starts the queue loop instance in another thread.
        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Processes each encoding task added to the queue.
        try:
            while True:
                encoding_task = self.standard_tasks_queue.get()

                if not encoding_task:
                    return

                try:
                    self.task_queue.wait_for_parallel_tasks()

                    self.task_queue.add_to_running_tasks(encoding_task)
                    self.task_queue.run_encoding_task(encoding_task)
                except:
                    logging.exception(''.join(['--- FAILED TO RUN STANDARD ENCODING TASK ---\n',
                                               encoding_task.output_file.file_path]))
                finally:
                    encoding_task.is_done = True
                    self.task_queue.remove_from_running_tasks(encoding_task)
                    self.standard_tasks_queue.task_done()
        except:
            logging.exception('--- STANDARD TASKS QUEUE LOOP FAILED ---')

    def add_encoding_task(self, encoding_task: encoding.Task):
        """
        Adds the given encoding task to the queue.

        Parameters:
            encoding_task: Encoding task to add to the queue.

        Returns:
            None
        """
        self.standard_tasks_queue.put(encoding_task)

    def add_stop_task(self):
        """
        Adds a False boolean to stop the queue loop instance thread.

        Returns:
            None
        """
        self.standard_tasks_queue.put(False)

    def join_queue(self):
        """
        Blocks the calling thread until the queue is empty.

        Returns:
            None
        """
        self.standard_tasks_queue.join()

    def empty_queue(self):
        """
        Empties the queue.

        Returns:
            None
        """
        while not self.standard_tasks_queue.empty():
            self.standard_tasks_queue.get()


class _ParallelTasksQueue:
    """Class that configures the queue for parallel encoding tasks."""

    def __init__(self, task_queue: TaskQueue, app_settings: app_preferences.Settings):
        """
        Initializes the _ParallelTasksQueue class with the variables necessary to queue and process
        parallel encoding tasks.

        Parameters:
            task_queue: Task queue that initializes this class.
            app_settings: Application settings.
        """
        self.task_queue = task_queue
        self.app_settings = app_settings
        self._codec_task_list = []
        self._codec_task_list_lock = threading.Lock()

        self._setup_codec_task_queues()

    def _setup_codec_task_queues(self):
        # Starts the queue loops for each codec type.
        threading.Thread(target=self._initialize_x264_codec_queue_loop, args=(self.app_settings,), daemon=True).start()
        threading.Thread(target=self._initialize_x265_codec_queue_loop, args=(self.app_settings,), daemon=True).start()
        threading.Thread(target=self._initialize_vp9_codec_queue_loop, args=(self.app_settings,), daemon=True).start()
        threading.Thread(target=self._initialize_copy_codec_queue_loop, args=(self.app_settings,), daemon=True).start()

        if nvidia_helper.Compatibility.is_nvenc_supported():
            threading.Thread(target=self._initialize_nvenc_codec_queue_loop, args=(), daemon=True).start()
        else:
            logging.info('--- PARALLEL NVENC QUEUE LOOP DISABLED ---')

    def _initialize_x264_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of x264 encoding tasks.
        self.x264_codec_queue = queue.Queue()
        self.number_of_x264_tasks = app_settings.per_codec_parallel_tasks['x264']

        with ThreadPoolExecutor(max_workers=self.number_of_x264_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance, repeat(self.x264_codec_queue))

    def _initialize_x265_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of x265 encoding tasks.
        self.x265_codec_queue = queue.Queue()
        self.number_of_x265_tasks = app_settings.per_codec_parallel_tasks['x265']

        with ThreadPoolExecutor(max_workers=self.number_of_x265_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance, repeat(self.x265_codec_queue))

    def _initialize_vp9_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of vp9 encoding tasks.
        self.vp9_codec_queue = queue.Queue()
        self.number_of_vp9_tasks = app_settings.per_codec_parallel_tasks['vp9']

        with ThreadPoolExecutor(max_workers=self.number_of_vp9_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance, repeat(self.vp9_codec_queue))

    def _initialize_nvenc_codec_queue_loop(self):
        # Starts queue loop instances for the user specified number of NVENC encoding tasks.
        try:
            self.nvenc_codec_queue = queue.Queue()
            self.number_of_nvenc_tasks = nvidia_helper.Parallel.nvenc_max_workers

            with ThreadPoolExecutor(max_workers=self.number_of_nvenc_tasks) as future_executor:
                future_executor.map(self._run_codec_queue_loop_instance, repeat(self.nvenc_codec_queue))
        except ValueError:
            logging.info('--- PARALLEL NVENC QUEUE LOOP DISABLED ---')

    def _initialize_copy_codec_queue_loop(self):
        # Starts queue loop instances for the number of copy encoding tasks.
        self.copy_codec_queue = queue.Queue()
        self.number_of_copy_codec_tasks = COPY_CODEC_TASK_WORKERS

        with ThreadPoolExecutor(max_workers=self.number_of_copy_codec_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance, repeat(self.copy_codec_queue))

    def _run_codec_queue_loop_instance(self, codec_queue: queue.Queue, codec_name: str):
        # Processes each encoding task added to the given codec queue.
        try:
            while True:
                if codec_queue.empty():
                    self._move_codec_queue_to_end_of_task_list(codec_queue)

                encoding_task = codec_queue.get()

                if not encoding_task:
                    break

                try:
                    self.task_queue.wait_for_standard_tasks()

                    if not encoding_task.is_video_nvenc() or not self.app_settings.is_nvenc_tasks_parallel:
                        self._wait_for_current_codec_queue_loop(codec_queue)

                    self.task_queue.add_to_running_tasks(encoding_task)
                    self.task_queue.run_encoding_task(encoding_task)
                except:
                    logging.exception(''.join(['--- FAILED TO RUN ', codec_name, ' ENCODING TASK ---']))
                finally:
                    encoding_task.is_done = True
                    self.task_queue.remove_from_running_tasks(encoding_task)
                    codec_queue.task_done()
        except:
            logging.exception(''.join(['--- ', codec_name, ' CODEC QUEUE LOOP INSTANCE FAILED ---']))

    def _wait_for_current_codec_queue_loop(self, codec_queue: queue.Queue):
        # Blocks the calling thread until the given codec queue is first in the codec task list.
        with self._codec_task_list_lock:
            current_codec_queue = self._codec_task_list[0]

            if codec_queue == current_codec_queue:
                return

        current_codec_queue.join()
        self._wait_for_current_codec_queue_loop(codec_queue)

    def add_encoding_task(self, encoding_task: encoding.Task):
        """
        Adds the given encoding task to the proper codec queue.

        Parameters:
            encoding_task: Encoding task to add to one of the codec queues.

        Returns:
            None
        """
        if encoding_task.is_video_x264():
            self.x264_codec_queue.put(encoding_task)
            self._add_codec_queue_to_task_list(self.x264_codec_queue)
        elif encoding_task.is_video_x265():
            self.x265_codec_queue.put(encoding_task)
            self._add_codec_queue_to_task_list(self.x265_codec_queue)
        elif encoding_task.is_video_vp9():
            self.vp9_codec_queue.put(encoding_task)
            self._add_codec_queue_to_task_list(self.vp9_codec_queue)
        elif encoding_task.is_video_nvenc():
            self.nvenc_codec_queue.put(encoding_task)
            self._add_codec_queue_to_task_list(self.nvenc_codec_queue)
        else:
            self.copy_codec_queue.put(encoding_task)
            self._add_codec_queue_to_task_list(self.copy_codec_queue)

    def _add_codec_queue_to_task_list(self, codec_queue: queue.Queue):
        # Adds the given codec queue to the codec task list if it doesn't already exist in the list.
        with self._codec_task_list_lock:
            if codec_queue not in self._codec_task_list:
                self._codec_task_list.append(codec_queue)

    def _move_codec_queue_to_end_of_task_list(self, codec_queue: queue.Queue):
        # Moves the given codec queue to the end of the codec task list.
        with self._codec_task_list_lock:
            if codec_queue in self._codec_task_list:
                self._codec_task_list.append(self._codec_task_list.pop(self._codec_task_list.index(codec_queue)))

    def add_stop_task(self):
        """
        Adds a False boolean to each codec queue to stop their queue loop instance threads.

        Returns:
            None
        """
        self._add_codec_queue_stop_task(self.x264_codec_queue, self.number_of_x264_tasks)
        self._add_codec_queue_stop_task(self.x265_codec_queue, self.number_of_x265_tasks)
        self._add_codec_queue_stop_task(self.vp9_codec_queue, self.number_of_vp9_tasks)
        self._add_codec_queue_stop_task(self.copy_codec_queue, self.number_of_copy_codec_tasks)

        if nvidia_helper.Compatibility.is_nvenc_supported():
            self._add_codec_queue_stop_task(self.nvenc_codec_queue, self.number_of_nvenc_tasks)

    @staticmethod
    def _add_codec_queue_stop_task(codec_queue: queue.Queue, number_of_tasks: int):
        # Adds a False boolean to the given codec queue for each number of tasks that codec is running in parallel.
        for task in range(number_of_tasks):
            codec_queue.put(False)

    def join_queue(self):
        """
        Blocks the calling thread until each codec queue is empty.

        Returns:
            None
        """
        self.x264_codec_queue.join()
        self.x265_codec_queue.join()
        self.vp9_codec_queue.join()
        self.nvenc_codec_queue.join()
        self.copy_codec_queue.join()

    def empty_queue(self):
        """
        Empties all codec queues.

        Returns:
            None
        """
        self._empty_codec_queue(self.x264_codec_queue)
        self._empty_codec_queue(self.x265_codec_queue)
        self._empty_codec_queue(self.vp9_codec_queue)
        self._empty_codec_queue(self.copy_codec_queue)

        if nvidia_helper.Compatibility.is_nvenc_supported():
            self._empty_codec_queue(self.nvenc_codec_queue)

    @staticmethod
    def _empty_codec_queue(codec_queue: queue.Queue):
        # Empties the given codec queue.
        while not codec_queue.empty():
            codec_queue.get()


class _WatchFolderTasksQueue:
    """Class that configures the queue for watch folder encoding tasks."""

    def __init__(self, task_queue: TaskQueue, app_settings: app_preferences.Settings):
        """
        Initializes the _WatchFolderTasksQueue class with the variables necessary to queue and process
        watch folder encoding tasks.

        Parameters:
            task_queue: Task queue that initialized this class.
            app_settings: Application settings.
        """
        self.task_queue = task_queue
        self.app_settings = app_settings
        self.watch_folder_tasks_queue = queue.Queue()
        self.watch_folder_scheduler = watch_folder.WatchFolderScheduler()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Processes each encoding task added to the queue and starts a scheduling task for each one.
        try:
            while True:
                encoding_task = self.watch_folder_tasks_queue.get()

                if not encoding_task:
                    return

                self.task_queue.add_to_running_tasks(encoding_task)
                threading.Thread(target=self._schedule_encoding_task, args=(encoding_task,)).start()

                self.watch_folder_tasks_queue.task_done()
        except:
            logging.exception('--- WATCH FOLDER QUEUE LOOP INSTANCE FAILED ---')

    def _schedule_encoding_task(self, encoding_task: encoding.Task):
        # Schedules and processes the given watch folder encoding task.
        self.watch_folder_scheduler.add_folder_path(encoding_task.input_file.dir)
        self._run_encoding_task(encoding_task)

    def _run_encoding_task(self, encoding_task: encoding.Task):
        # Processes a child encoding task for each file in the watch folder task.
        try:
            while True:
                if encoding_task.is_stopped:
                    break

                if self.watch_folder_scheduler.is_instance_empty(encoding_task.input_file.dir):
                    encoding_task.is_idle = True
                encoding_task.has_started = False

                child_encoding_task = self._get_child_encoding_task(encoding_task)

                if not child_encoding_task:
                    continue
                encoding_task.child_encoding_task = child_encoding_task

                try:
                    self._run_child_encoding_task(child_encoding_task, encoding_task)
                except:
                    logging.exception(''.join(['--- WATCH FOLDER CHILD ENCODING TASK FAILED ---\n',
                                               child_encoding_task.output_file.file_path]))
                finally:
                    encoding_task.has_failed = child_encoding_task.has_failed

                    if self.app_settings.is_watch_folders_moving_to_done:
                        self._move_child_encoding_task_to_done_folder(child_encoding_task)
        except:
            logging.exception('--- WATCH FOLDER ENCODING TASK LOOP FAILED ---\n', encoding_task.output_file.file_path)

    def _get_child_encoding_task(self, encoding_task: encoding.Task) -> encoding.Task | None:
        # Returns a child encoding task from the watch folder encoding task that has a new file.
        child_file_path = self.watch_folder_scheduler.get_instance_new_file(encoding_task.input_file.dir)

        if not child_file_path:
            return None

        child_encoding_task = encoding_task.get_copy()
        child_encoding_task.input_file = encoding.input.InputFile(child_file_path)
        child_encoding_task.output_file = encoding.output.OutputFile(child_encoding_task.input_file, self.app_settings)

        directory_helper.fix_same_name_occurences(encoding_task, self.app_settings)

        if not child_encoding_task.input_file.is_valid():
            return None
        return child_encoding_task

    def _run_child_encoding_task(self, child_encoding_task: encoding.Task, encoding_task: encoding.Task):
        # Sends the given child encoding task to the encoder.
        if self.app_settings.is_watch_folders_waiting_for_tasks:
            self.task_queue.wait_for_all_tasks()

        if not self.app_settings.is_encoding_parallel_watch_folders:
            self.task_queue.wait_for_watch_folder_tasks()

        encoding_task.has_started = True
        encoding_task.is_idle = False
        self.task_queue.run_encoding_task(child_encoding_task)

    @staticmethod
    def _move_child_encoding_task_to_done_folder(child_encoding_task: encoding.Task):
        # Moves the encoded child encoding task's file to a done folder.
        original_file_path = child_encoding_task.input_file.file_path

        child_encoding_task.input_file.dir = os.path.join(child_encoding_task.input_file.dir, 'done')

        if not os.path.exists(child_encoding_task.input_file.dir):
            os.mkdir(child_encoding_task.input_file.dir)

        shutil.move(original_file_path, child_encoding_task.input_file.file_path)

    def add_encoding_task(self, encoding_task: encoding.Task):
        """
        Adds the given encoding task to the queue.

        Parameters:
            encoding_task: Encoding task to add to the queue.

        Returns:
            None
        """
        self.watch_folder_tasks_queue.put(encoding_task)

    def add_stop_task(self):
        """
        Adds a False boolean to stop the queue loop instance.

        Returns:
            None
        """
        self.watch_folder_tasks_queue.put(False)

    def empty_queue(self):
        """
        Empties the queue.

        Returns:
            None
        """
        while not self.watch_folder_tasks_queue.empty():
            self.watch_folder_tasks_queue.get()
