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


import os
import shutil
import logging
import threading

from render_watch.ui import Gio
from render_watch.helpers import directory_helper


APP_NAME = 'io.github.renderwatch.RenderWatch'
ORG_NAME = 'Michael Gregory'

APPLICATION_CONFIG_DIRECTORY = os.path.join(os.getenv('HOME'), '.config', 'Render Watch')
DEFAULT_APPLICATION_TEMP_DIRECTORY = os.path.join(APPLICATION_CONFIG_DIRECTORY, 'temp')


class Settings:
    """Class that stores, saves, and loads settings for Render Watch."""

    PARALLEL_TASKS_ENABLED = 'parallel-encoding-tasks'
    PARALLEL_TASKS_CHUNKING_ENABLED = 'parallel-encoding-method-chunking'
    X264_TASKS = 'per-codec-x264'
    X265_TASKS = 'per-codec-x265'
    VP9_TASKS = 'per-codec-vp9'
    PARALLEL_NVENC_ENABLED = 'parallel-nvenc-tasks'
    PARALLEL_NVENC_TASKS = 'parallel-nvenc-workers'
    AUTO_CROP_ENABLED = 'auto-crop-inputs'
    PARALLEL_WATCH_FOLDERS_ENABLED = 'parallel-encode-watch-folders'
    WATCH_FOLDERS_WAIT_FOR_TASKS_ENABLED = 'watch-folders-wait-for-tasks'
    WATCH_FOLDERS_MOVE_TO_DONE_ENABLED = 'watch-folders-move-to-done'
    OUTPUT_DIRECTORY = 'output-directory'
    OVERWRITE_OUTPUT_DIRECTORY_ENABLED = 'overwrite-output-files'
    TEMP_DIRECTORY = 'temp-directory'
    ENCODER_PREVIEW_ENABLED = 'encoder-preview'
    WINDOW_WIDTH = 'window-width'
    WINDOW_HEIGHT = 'window-height'
    IS_WINDOW_MAXIMIZED = 'window-maximized'

    TASK_MIN = 2
    TASK_MAX = 8
    NVENC_TASK_MIN = 2
    NVENC_TASK_MAX = 12

    def __init__(self):
        """
        Initializes the Settings class with the variables necessary for storing, saving, and loading the settings for
        Render Watch. Each setting is loaded with Gio.Settings.
        """
        self._settings = Gio.Settings.new(APP_NAME)
        self._settings_thread_lock = threading.Lock()

        self._is_nvenc_tasks_parallel = self._settings.get_boolean(self.PARALLEL_NVENC_ENABLED)
        self._parallel_nvenc_workers = self._settings.get_int(self.PARALLEL_NVENC_TASKS)
        self._is_encoding_parallel_tasks = self._settings.get_boolean(self.PARALLEL_TASKS_ENABLED)
        self._per_codec_parallel_tasks = {
            'x264': self._settings.get_int(self.X264_TASKS),
            'x265': self._settings.get_int(self.X265_TASKS),
            'vp9': self._settings.get_int(self.VP9_TASKS)
        }
        self._is_encoding_parallel_method_chunking = self._settings.get_boolean(self.PARALLEL_TASKS_CHUNKING_ENABLED)
        self._is_auto_cropping_inputs = self._settings.get_boolean(self.AUTO_CROP_ENABLED)
        self._is_encoding_parallel_watch_folders = self._settings.get_boolean(self.PARALLEL_WATCH_FOLDERS_ENABLED)
        self._is_watch_folders_waiting_for_tasks = self._settings.get_boolean(self.WATCH_FOLDERS_WAIT_FOR_TASKS_ENABLED)
        self._is_watch_folders_moving_to_done = self._settings.get_boolean(self.WATCH_FOLDERS_MOVE_TO_DONE_ENABLED)
        self._temp_directory = self._settings.get_string(self.TEMP_DIRECTORY)
        self._new_temp_directory = None
        self._output_directory = self._settings.get_string(self.OUTPUT_DIRECTORY)
        self._is_overwriting_output_files = self._settings.get_boolean(self.OVERWRITE_OUTPUT_DIRECTORY_ENABLED)
        self._is_encoder_showing_preview = self._settings.get_boolean(self.ENCODER_PREVIEW_ENABLED)
        self._window_width = self._settings.get_int(self.WINDOW_WIDTH)
        self._window_height = self._settings.get_int(self.WINDOW_HEIGHT)
        self._is_window_maximized = self._settings.get_boolean(self.IS_WINDOW_MAXIMIZED)

        self._set_default_directories()

    def _set_default_directories(self):
        # Sets the output and temp directories to their default values if they weren't set after loading settings.
        if not self._output_directory:
            self._output_directory = os.getenv('HOME')

        if not self._temp_directory:
            self._temp_directory = DEFAULT_APPLICATION_TEMP_DIRECTORY

    @property
    def output_directory(self) -> str:
        """
        Returns the value of the output directory. This property is thread safe.

        Returns:
            Output directory as a string.
        """
        with self._settings_thread_lock:
            return self._output_directory

    @output_directory.setter
    def output_directory(self, directory: str):
        """
        Sets the output directory to the directory specified. This property is thread safe.

        Parameters:
            directory: The directory to use for the output directory.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._output_directory = directory

    @property
    def is_overwriting_output_files(self) -> bool:
        """
        Returns a boolean that represents whether existing output files will be overwritten when
        running an encoding task. This property is thread safe.

        Returns:
            Boolean that represents whether encoding tasks will overwrite existing outputs.
        """
        with self._settings_thread_lock:
            return self._is_overwriting_output_files

    @is_overwriting_output_files.setter
    def is_overwriting_output_files(self, is_enabled: bool):
        """
        Sets whether existing output files will be overwritten when running an encoding task. This property
        is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether encoding tasks will overwrite existing outputs.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._is_overwriting_output_files = is_enabled

    @property
    def temp_directory(self) -> str:
        """
        Returns the value of the temp directory. This property is thread safe.

        Returns:
            Temp directory as a string.
        """
        with self._settings_thread_lock:
            return self._temp_directory

    @temp_directory.setter
    def temp_directory(self, directory: str):
        """
        Sets the temp directory to the directory specified. This property is thread safe.

        Parameters:
            directory: The directory to use for the temp directory.

        Returns:
            None
        """
        with self._settings_thread_lock:
            if directory == self._temp_directory:
                self._new_temp_directory = None
            else:
                self._new_temp_directory = directory

    def get_new_temp_directory(self) -> str:
        """
        Returns the new temp directory that's been set. The original temp directory is overwritten after the application
        is restarted. You then have a new and an original temp directory that's stored. This function is thread safe.

        Returns:
            Newly set temp directory as a string.
        """
        if self._new_temp_directory is None:
            return self.temp_directory

        with self._settings_thread_lock:
            return self._new_temp_directory

    @property
    def is_encoding_parallel_tasks(self) -> bool:
        """
        Returns whether encoding tasks are run in parallel. This property is thread safe.

        Returns:
            Boolean that represents whether encoding tasks are run in parallel.
        """
        with self._settings_thread_lock:
            return self._is_encoding_parallel_tasks

    @is_encoding_parallel_tasks.setter
    def is_encoding_parallel_tasks(self, is_enabled: bool):
        """
        Sets whether encoding tasks are run in parallel. This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether encoding tasks will be run in parallel.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._is_encoding_parallel_tasks = is_enabled

    @property
    def is_encoding_parallel_method_chunking(self) -> bool:
        """
        Returns weather parallel tasks will be processes as chunks. This property is thread safe.

        Returns:
            Boolean that represents whether parallel tasks will be processed as chunks.
        """
        with self._settings_thread_lock:
            return self._is_encoding_parallel_method_chunking

    @is_encoding_parallel_method_chunking.setter
    def is_encoding_parallel_method_chunking(self, is_enabled: bool):
        """
        Sets whether parallel tasks will be processed as chunks. This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether parallel tasks will be processed as chunks.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._is_encoding_parallel_method_chunking = is_enabled

    @property
    def per_codec_x264(self) -> int:
        """
        Returns the number of x264 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Returns:
            Integer that represents how many x264 tasks that will run when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['x264']

    @per_codec_x264.setter
    def per_codec_x264(self, x264_tasks: int):
        """
        Sets the number of x264 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Parameters:
            x264_tasks: Number of x264 tasks that will run when parallel encoding is enabled.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['x264'] = x264_tasks

    @property
    def per_codec_x265(self) -> int:
        """
        Returns the number of x265 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Returns:
            Integer that represents how many x265 tasks that will run when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['x265']

    @per_codec_x265.setter
    def per_codec_x265(self, x265_tasks: int):
        """
        Sets the number of x265 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Parameters:
            x265_tasks: Number of x265 tasks that will run when parallel encoding is enabled.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['x265'] = x265_tasks

    @property
    def per_codec_vp9(self) -> int:
        """
        Returns the number of vp9 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Returns:
            Integer that represents how many vp9 tasks that will run when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['vp9']

    @per_codec_vp9.setter
    def per_codec_vp9(self, vp9_tasks: int):
        """
        Sets the number of vp9 tasks that will run when parallel encoding is enabled. This property is thread safe.

        Parameters:
            vp9_tasks: Number of vp9 tasks that will run when parallel encoding is enabled.

        Returns:
            None
        """
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['vp9'] = vp9_tasks

    @property
    def is_nvenc_tasks_parallel(self) -> bool:
        """
        Returns whether Nvenc tasks will be processed in parallel when parallel encoding is enabled.
        This property is thread safe.

        Returns:
            Boolean that represents whether Nvenc tasks will be processed in parallel when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._is_nvenc_tasks_parallel

    @is_nvenc_tasks_parallel.setter
    def is_nvenc_tasks_parallel(self, is_enabled: bool):
        """
        Sets whether Nvenc tasks will be processed in parallel when parallel encoding is enabled.
        This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether Nvenc tasks will be processed in parallel
            when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            self._is_nvenc_tasks_parallel = is_enabled

    @property
    def parallel_nvenc_workers(self) -> int:
        """
        Returns the number of Nvenc tasks that will run when parallel encoding is enabled. This property is thread safe.

        Returns:
            Integer that represents how many Nvenc tasks that will run when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._parallel_nvenc_workers

    @parallel_nvenc_workers.setter
    def parallel_nvenc_workers(self, number_of_workers: int):
        """
        Sets the number of Nvenc tasks that will run when parallel encoding is enabled. This property is thread safe.

        Parameters:
            number_of_workers: Number of Nvenc tasks that will run when parallel encoding is enabled.

        Returns:
            None
        """
        with self._settings_thread_lock:
            if number_of_workers == 0:
                self._parallel_nvenc_workers = None
            else:
                self._parallel_nvenc_workers = number_of_workers

    @property
    def is_auto_cropping_inputs(self) -> bool:
        """
        Returns whether inputs are automatically cropped when imported to get rid of "black bars" in the video stream.
        This property is thread safe.

        Returns:
            Boolean that represents whether inputs are automatically cropped when imported.
        """
        with self._settings_thread_lock:
            return self._is_auto_cropping_inputs

    @is_auto_cropping_inputs.setter
    def is_auto_cropping_inputs(self, is_enabled: bool):
        """
        Sets whether inputs are automatically cropped when imported to get rid of "black bars" in the video stream.
        This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether inputs are automatically cropped when imported.
        """
        with self._settings_thread_lock:
            self._is_auto_cropping_inputs = is_enabled

    @property
    def is_encoding_parallel_watch_folders(self) -> bool:
        """
        Returns whether watch folder tasks are processed in parallel when parallel encoding is enabled.
        This property is thread safe.

        Returns:
            Boolean that represents whether watch folder tasks are processed in parallel
            when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            return self._is_encoding_parallel_watch_folders

    @is_encoding_parallel_watch_folders.setter
    def is_encoding_parallel_watch_folders(self, is_enabled: bool):
        """
        Sets whether watch folder tasks are processed in parallel when parallel encoding is enabled.
        This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether watch folder tasks are processed in parallel
            when parallel encoding is enabled.
        """
        with self._settings_thread_lock:
            self._is_encoding_parallel_watch_folders = is_enabled

    @property
    def is_watch_folders_waiting_for_tasks(self) -> bool:
        """
        Returns whether watch folder tasks wait for other tasks to complete before processing.
        This property is thread safe.

        Returns:
            Boolean that represents whether watch folder tasks wait for other tasks to complete before processing.
        """
        with self._settings_thread_lock:
            return self._is_watch_folders_waiting_for_tasks

    @is_watch_folders_waiting_for_tasks.setter
    def is_watch_folders_waiting_for_tasks(self, is_enabled: bool):
        """
        Sets whether watch folder tasks wait for other tasks to complete before processing.
        This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether watch folder tasks wait for
            other tasks to complete before processing.
        """
        with self._settings_thread_lock:
            self._is_watch_folders_waiting_for_tasks = is_enabled

    @property
    def is_watch_folders_moving_to_done(self) -> bool:
        """
        Returns whether inputs are moved to a "done" folder once the watch folder task has completed.
        This property is thread safe.

        Returns:
            Boolean that represents whether inputs are moved to a "done" folder
            once the watch folder task has completed.
        """
        with self._settings_thread_lock:
            return self._is_watch_folders_moving_to_done

    @is_watch_folders_moving_to_done.setter
    def is_watch_folders_moving_to_done(self, is_enabled: bool):
        """
        Sets whether inputs are moved to a "done" folder once the watch folder task has completed.
        This property is thread safe.

        Parameters:
            is_enabled: Boolean that represents whether inputs are moved to a "done" folder
            once the watch folder task has completed.
        """
        with self._settings_thread_lock:
            self._is_watch_folders_moving_to_done = is_enabled

    @property
    def window_width(self) -> int:
        """
        Returns the width of the application's main window. This property is thread safe.

        Returns:
            Integer that represents the width of the application's main window.
        """
        with self._settings_thread_lock:
            return self._window_width

    @window_width.setter
    def window_width(self, width: int):
        """
        Sets the width of the application's main window. This property is thread safe.

        Parameters:
            width: Integer that represents the width of the application's main window.
        """
        with self._settings_thread_lock:
            if width > 0:
                self._window_width = width
            else:
                self._window_width = 1280

    @property
    def window_height(self) -> int:
        """
        Returns the height of the application's main window. This property is thread safe.

        Returns:
            Integer that represents the height of the application's main window.
        """
        with self._settings_thread_lock:
            return self._window_height

    @window_height.setter
    def window_height(self, height: int):
        """
        Sets the height of the application's main window. This property is thread safe.

        Parameters:
            height: Integer that represents the height of the application's main window.
        """
        with self._settings_thread_lock:
            if height > 0:
                self._window_height = height
            else:
                self._window_height = 720

    @property
    def is_window_maximized(self) -> bool:
        """
        Returns whether the main window is maximized. This property is thread safe.

        Returns:
            Boolean that represents whether the main window is maximized.
        """
        with self._settings_thread_lock:
            return self._is_window_maximized

    @is_window_maximized.setter
    def is_window_maximized(self, is_maximized: bool):
        """
        Sets whether the main window is maximized. This property is thread safe.

        Parameters:
            is_maximized: Boolean that represents whether the main window is maximized.
        """
        with self._settings_thread_lock:
            self._is_window_maximized = is_maximized

    def save(self):
        """
        Uses Gio.Settings to save all settings in Render Watch.

        Returns:
            None
        """
        self._settings.set_boolean(self.PARALLEL_NVENC_ENABLED, self._is_nvenc_tasks_parallel)
        self._settings.set_boolean(self.PARALLEL_TASKS_ENABLED, self._is_encoding_parallel_tasks)
        self._settings.set_boolean(self.PARALLEL_TASKS_CHUNKING_ENABLED, self._is_encoding_parallel_method_chunking)
        self._settings.set_boolean(self.AUTO_CROP_ENABLED, self._is_auto_cropping_inputs)
        self._settings.set_boolean(self.PARALLEL_WATCH_FOLDERS_ENABLED, self._is_encoding_parallel_watch_folders)
        self._settings.set_boolean(self.WATCH_FOLDERS_WAIT_FOR_TASKS_ENABLED, self._is_watch_folders_waiting_for_tasks)
        self._settings.set_boolean(self.WATCH_FOLDERS_MOVE_TO_DONE_ENABLED, self._is_watch_folders_moving_to_done)
        self._settings.set_string(self.TEMP_DIRECTORY, self.get_new_temp_directory())
        self._settings.set_boolean(self.OVERWRITE_OUTPUT_DIRECTORY_ENABLED, self._is_overwriting_output_files)
        self._settings.set_string(self.OUTPUT_DIRECTORY, self._output_directory)
        self._settings.set_boolean(self.ENCODER_PREVIEW_ENABLED, self._is_encoder_showing_preview)
        self._settings.set_int(self.WINDOW_WIDTH, self._window_width)
        self._settings.set_int(self.WINDOW_HEIGHT, self._window_height)
        self._settings.set_boolean(self.IS_WINDOW_MAXIMIZED, self._is_window_maximized)
        self._save_parallel_nvenc_workers_option()
        self._save_per_codec_parallel_tasks_options()

    def _save_parallel_nvenc_workers_option(self):
        # Saves the parallel nvenc workers option using Gio.Settings
        if self.parallel_nvenc_workers:
            self._settings.set_int(self.PARALLEL_NVENC_TASKS, self.parallel_nvenc_workers)
        else:
            self._settings.set_int(self.PARALLEL_NVENC_TASKS, 0)

    def _save_per_codec_parallel_tasks_options(self):
        # Saves each per-codec parallel tasks value using Gio.Settings
        self._settings.set_int(self.X264_TASKS, self._per_codec_parallel_tasks['x264'])
        self._settings.set_int(self.X265_TASKS, self._per_codec_parallel_tasks['x265'])
        self._settings.set_int(self.VP9_TASKS, self._per_codec_parallel_tasks['vp9'])


def create_config_directory():
    """Creates the application's configuration directory to store logs and temporary files."""
    directory_helper.create_application_config_directory(APPLICATION_CONFIG_DIRECTORY)


def create_default_temp_directory():
    """Creates the application's default temp directory."""
    directory_helper.create_application_default_temp_directory(DEFAULT_APPLICATION_TEMP_DIRECTORY)


def create_temp_directory(app_settings: Settings):
    """
    Creates the application's temporary directory if it doesn't already exist.

    Parameters:
        app_settings: Application's settings.
    """
    try:
        os.mkdir(app_settings.temp_directory)
    except FileExistsError:
        logging.info('--- TEMP DIRECTORY ALREADY EXISTS ---\n' + app_settings.temp_directory)


def clear_temp_directory(app_settings: Settings):
    """
    Removes the application's temporary directory.

    Parameters:
        app_settings: Application's settings.
    """
    try:
        shutil.rmtree(app_settings.get_new_temp_directory())
    except OSError:
        logging.error('--- FAILED TO CLEAR TEMP DIRECTORY ---\n' + app_settings.get_new_temp_directory())
