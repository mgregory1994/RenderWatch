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


import os.path
import threading
import queue
import time
import shutil

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

from render_watch.encode import encoder, watch_folder
from render_watch.ffmpeg import task, video_codec
from render_watch.helpers import ffmpeg_helper
from render_watch import app_preferences, logger


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

    def add_task(self, encode_task: task.Encode | task.Folder | task.WatchFolder):
        """
        Adds the encoding task to the proper tasks queue based on whether the task is a watch folder or if the
        user has enabled parallel tasks.

        Parameters:
            encode_task: Encoding task to add to one of the task queues.

        Returns:
            None
        """
        if isinstance(encode_task, task.WatchFolder):
            self._watch_folder_tasks_queue.add_encoding_task(encode_task)
        elif self.is_using_parallel_tasks_queue:
            self._parallel_tasks_queue.add_encoding_task(encode_task)
        else:
            self._standard_tasks_queue.add_encoding_task(encode_task)

    def add_to_running_tasks(self, encode_task: task.Encode | task.Folder):
        """
        Adds the given encoding task to the list of currently running tasks.

        Parameters:
            encode_task: Encoding task to add to the list of currently running tasks.

        Returns:
            None
        """
        with self._running_tasks_lock:
            self._running_tasks.append(encode_task)

    def remove_from_running_tasks(self, encode_task: task.Encode | task.Folder):
        """
        Removes the given encoding task from the list of currently running tasks.

        Parameters:
            encode_task: Encoding task to removed from the list of running tasks.

        Returns:
            None
        """
        try:
            with self._running_tasks_lock:
                self._running_tasks.remove(encode_task)
        except ValueError:
            logger.log_task_not_in_running_tasks_list(encode_task.output_file.file_path)

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
        for encode_task in self.get_currently_running_tasks():
            if encode_task.is_watch_folder \
                    and not encode_task.is_idle \
                    and not encode_task.is_stopped \
                    and encode_task.has_started:
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

    def run_encoding_task(self, encode_task: task.Encode | task.Folder):
        """
        Sends the given encoding task to the encoder. If the encoding task is a folder task, then the files contained in
        that folder are sent to the encoder.

        Parameters:
            encode_task: Encoding task to send to the encoder.

        Returns:
            None
        """
        if encode_task.is_stopped:
            return

        if isinstance(encode_task, task.Folder):
            self._run_folder_encoding_task(encode_task)
        else:
            self._run_standard_encoding_task(encode_task)

    @staticmethod
    def _run_standard_encoding_task(encode_task: task.Encode):
        # Sends the given encoding task to the encoder.
        if video_codec.is_codec_nvenc(encode_task.get_video_codec()):
            ffmpeg_helper.Compatibility.wait_until_nvenc_available()

        encode_task.has_started = True
        encode_task.has_failed = encoder.run_encode_subprocess(encode_task) != 0
        encode_task.is_done = True

    def _run_folder_encoding_task(self, folder_task: task.Folder):
        # Creates a child encoding task for each file in the folder task and sends them to the encoder.
        while folder_task.next_encode_task:
            self._run_standard_encoding_task(folder_task.next_encode_task)

            if not folder_task.has_failed:
                folder_task.has_failed = folder_task.next_encode_task.has_failed

            folder_task.process_next_encode_task()

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
                encode_task = self.standard_tasks_queue.get()

                if not encode_task:
                    return

                try:
                    self.task_queue.wait_for_parallel_tasks()
                    self.task_queue.add_to_running_tasks(encode_task)
                    self.task_queue.run_encoding_task(encode_task)
                except:
                    logger.log_failed_to_run_standard_encoding_task(encode_task.output_file.file_path)
                finally:
                    self.task_queue.remove_from_running_tasks(encode_task)
                    self.standard_tasks_queue.task_done()
        except:
            logger.log_standard_tasks_queue_loop_failed()

    def add_encoding_task(self, encode_task: task.Encode | task.Folder):
        """
        Adds the given encoding task to the queue.

        Parameters:
            encode_task: Encoding task to add to the queue.

        Returns:
            None
        """
        self.standard_tasks_queue.put(encode_task)

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
        threading.Thread(target=self._initialize_copy_codec_queue_loop, args=(), daemon=True).start()

        if ffmpeg_helper.Compatibility.is_nvenc_supported():
            threading.Thread(target=self._initialize_nvenc_codec_queue_loop, args=(), daemon=True).start()
        else:
            logger.log_parallel_nvenc_queue_loop_disabled()

    def _initialize_x264_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of x264 encoding tasks.
        self.x264_codec_queue = queue.Queue()
        self.number_of_x264_tasks = app_settings.per_codec_x264

        with ThreadPoolExecutor(max_workers=self.number_of_x264_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance,
                                repeat(self.x264_codec_queue, self.number_of_x264_tasks))

    def _initialize_x265_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of x265 encoding tasks.
        self.x265_codec_queue = queue.Queue()
        self.number_of_x265_tasks = app_settings.per_codec_x265

        with ThreadPoolExecutor(max_workers=self.number_of_x265_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance,
                                repeat(self.x265_codec_queue, self.number_of_x265_tasks))

    def _initialize_vp9_codec_queue_loop(self, app_settings: app_preferences.Settings):
        # Starts queue loop instances for the user specified number of vp9 encoding tasks.
        self.vp9_codec_queue = queue.Queue()
        self.number_of_vp9_tasks = app_settings.per_codec_vp9

        with ThreadPoolExecutor(max_workers=self.number_of_vp9_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance,
                                repeat(self.vp9_codec_queue, self.number_of_vp9_tasks))

    def _initialize_nvenc_codec_queue_loop(self):
        # Starts queue loop instances for the user specified number of NVENC encoding tasks.
        try:
            self.nvenc_codec_queue = queue.Queue()
            self.number_of_nvenc_tasks = ffmpeg_helper.Parallel.nvenc_max_workers

            with ThreadPoolExecutor(max_workers=self.number_of_nvenc_tasks) as future_executor:
                future_executor.map(self._run_codec_queue_loop_instance,
                                    repeat(self.nvenc_codec_queue, self.number_of_nvenc_tasks))
        except ValueError:
            logger.log_parallel_nvenc_queue_loop_disabled()

    def _initialize_copy_codec_queue_loop(self):
        # Starts queue loop instances for the number of copy encoding tasks.
        self.copy_codec_queue = queue.Queue()
        self.number_of_copy_codec_tasks = COPY_CODEC_TASK_WORKERS

        with ThreadPoolExecutor(max_workers=self.number_of_copy_codec_tasks) as future_executor:
            future_executor.map(self._run_codec_queue_loop_instance,
                                repeat(self.copy_codec_queue, self.number_of_copy_codec_tasks))

    def _run_codec_queue_loop_instance(self, codec_queue: queue.Queue, codec_name: str):
        # Processes each encoding task added to the given codec queue.
        try:
            while True:
                if codec_queue.empty():
                    self._move_codec_queue_to_end_of_task_list(codec_queue)

                encode_task = codec_queue.get()

                if not encode_task:
                    break

                try:
                    self.task_queue.wait_for_standard_tasks()

                    if not video_codec.is_codec_nvenc(encode_task.get_video_codec) \
                            or not self.app_settings.is_nvenc_tasks_parallel:
                        self._wait_for_current_codec_queue_loop(codec_queue)

                    self.task_queue.add_to_running_tasks(encode_task)
                    self.task_queue.run_encoding_task(encode_task)
                except:
                    logger.log_failed_to_run_encoding_task(codec_name)
                finally:
                    self.task_queue.remove_from_running_tasks(encode_task)
                    codec_queue.task_done()
        except:
            logger.log_codec_queue_loop_instance_failed(codec_name)

    def _wait_for_current_codec_queue_loop(self, codec_queue: queue.Queue):
        # Blocks the calling thread until the given codec queue is first in the codec task list.
        with self._codec_task_list_lock:
            current_codec_queue = self._codec_task_list[0]

            if codec_queue == current_codec_queue:
                return

        current_codec_queue.join()
        self._wait_for_current_codec_queue_loop(codec_queue)

    def add_encoding_task(self, encode_task: task.Encode):
        """
        Adds the given encoding task to the proper codec queue.

        Parameters:
            encode_task: Encoding task to add to one of the codec queues.

        Returns:
            None
        """
        if video_codec.is_codec_x264(encode_task.get_video_codec()):
            self.x264_codec_queue.put(encode_task)
            self._add_codec_queue_to_task_list(self.x264_codec_queue)
        elif video_codec.is_codec_x265(encode_task.get_video_codec()):
            self.x265_codec_queue.put(encode_task)
            self._add_codec_queue_to_task_list(self.x265_codec_queue)
        elif video_codec.is_codec_vp9(encode_task.get_video_codec()):
            self.vp9_codec_queue.put(encode_task)
            self._add_codec_queue_to_task_list(self.vp9_codec_queue)
        elif video_codec.is_codec_nvenc(encode_task.get_video_codec()):
            self.nvenc_codec_queue.put(encode_task)
            self._add_codec_queue_to_task_list(self.nvenc_codec_queue)
        else:
            self.copy_codec_queue.put(encode_task)
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

        if ffmpeg_helper.Compatibility.is_nvenc_supported():
            self._add_codec_queue_stop_task(self.nvenc_codec_queue, self.number_of_nvenc_tasks)

    @staticmethod
    def _add_codec_queue_stop_task(codec_queue: queue.Queue, number_of_tasks: int):
        # Adds a False boolean to the given codec queue for each number of tasks that codec is running in parallel.
        for encode_task in range(number_of_tasks):
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

        if ffmpeg_helper.Compatibility.is_nvenc_supported():
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
                watch_folder_task = self.watch_folder_tasks_queue.get()

                if not watch_folder_task:
                    return

                self.task_queue.add_to_running_tasks(watch_folder_task)
                threading.Thread(target=self._schedule_watch_folder_task, args=(watch_folder_task,)).start()

                self.watch_folder_tasks_queue.task_done()
        except:
            logger.log_watch_folder_queue_loop_failed()

    def _schedule_watch_folder_task(self, watch_folder_task: task.WatchFolder):
        # Schedules and processes the given watch folder encoding task.
        self.watch_folder_scheduler.add_folder_path(watch_folder_task.input_file.dir)
        self._run_watch_folder_task_loop(watch_folder_task)
        watch_folder_task.has_started = True

    def _run_watch_folder_task_loop(self, watch_folder_task: task.WatchFolder):
        # Processes a child encoding task for each file in the watch folder task.
        try:
            while True:
                if watch_folder_task.is_stopped:
                    break

                if self.watch_folder_scheduler.is_instance_empty(watch_folder_task.input_file.dir):
                    watch_folder_task.is_idle = True

                next_encode_task = self._get_next_encode_task(watch_folder_task)

                if not next_encode_task:
                    continue

                try:
                    self._run_next_encode_task(next_encode_task, watch_folder_task)
                except:
                    logger.log_watch_folder_next_encode_task_failed(next_encode_task.output_file.file_path)
                finally:
                    if self.app_settings.is_watch_folders_moving_to_done:
                        self._move_next_encode_task_to_done_folder(next_encode_task)
        except:
            logger.log_watch_folder_encoding_task_loop_failed(watch_folder_task.output_file.file_path)

    def _get_next_encode_task(self, watch_folder_task: task.WatchFolder) -> task.Encode | None:
        # Returns a child encoding task from the watch folder encoding task that has a new file.
        new_input_file_path = self.watch_folder_scheduler.get_instance_new_file(watch_folder_task.input_file.dir)

        if new_input_file_path:
            watch_folder_task.process_next_encode_task(new_input_file_path)

            return watch_folder_task.next_encode_task
        else:
            return None

    def _run_next_encode_task(self, next_encode_task: task.Encode, watch_folder_task: task.WatchFolder):
        # Sends the given child encoding task to the encoder.
        if self.app_settings.is_watch_folders_waiting_for_tasks:
            self.task_queue.wait_for_all_tasks()

        if not self.app_settings.is_encoding_parallel_watch_folders:
            self.task_queue.wait_for_watch_folder_tasks()

        watch_folder_task.is_idle = False
        self.task_queue.run_encoding_task(next_encode_task)

        if not watch_folder_task.has_failed:
            watch_folder_task.has_failed = next_encode_task.has_failed

    @staticmethod
    def _move_next_encode_task_to_done_folder(next_encode_task: task.Encode):
        # Moves the encoded child encoding task's file to a done folder.
        original_file_path = next_encode_task.input_file.file_path
        next_encode_task.input_file.dir = os.path.join(next_encode_task.input_file.dir, 'done')

        if not os.path.exists(next_encode_task.input_file.dir):
            os.mkdir(next_encode_task.input_file.dir)

        shutil.move(original_file_path, next_encode_task.input_file.file_path)

    def add_encoding_task(self, watch_folder_task: task.WatchFolder):
        """
        Adds the given encoding task to the queue.

        Parameters:
            watch_folder_task: Watch folder task to add to the queue.

        Returns:
            None
        """
        self.watch_folder_tasks_queue.put(watch_folder_task)

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
