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

    def __init__(self):
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

        self._setup_directories()

    def _setup_directories(self):
        if not self._output_directory:
            self._output_directory = os.getenv('HOME')

        if not self._temp_directory:
            self._temp_directory = DEFAULT_APPLICATION_TEMP_DIRECTORY

    @property
    def output_directory(self) -> str:
        with self._settings_thread_lock:
            return self._output_directory

    @output_directory.setter
    def output_directory(self, directory: str):
        with self._settings_thread_lock:
            self._output_directory = directory

    @property
    def is_overwriting_output_files(self) -> bool:
        with self._settings_thread_lock:
            return self._is_overwriting_output_files

    @is_overwriting_output_files.setter
    def is_overwriting_output_files(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_overwriting_output_files = is_enabled

    @property
    def temp_directory(self) -> str:
        with self._settings_thread_lock:
            return self._temp_directory

    @temp_directory.setter
    def temp_directory(self, temp_directory_path: str):
        with self._settings_thread_lock:
            if temp_directory_path == self._temp_directory:
                self._new_temp_directory = None
            else:
                self._new_temp_directory = temp_directory_path

    def get_new_temp_directory(self) -> str:
        if self._new_temp_directory is None:
            return self.temp_directory

        with self._settings_thread_lock:
            return self._new_temp_directory

    @property
    def is_encoding_parallel_tasks(self) -> bool:
        with self._settings_thread_lock:
            return self._is_encoding_parallel_tasks

    @is_encoding_parallel_tasks.setter
    def is_encoding_parallel_tasks(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_encoding_parallel_tasks = is_enabled

    @property
    def is_encoding_parallel_method_chunking(self) -> bool:
        with self._settings_thread_lock:
            return self._is_encoding_parallel_method_chunking

    @is_encoding_parallel_method_chunking.setter
    def is_encoding_parallel_method_chunking(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_encoding_parallel_method_chunking = is_enabled

    @property
    def per_codec_x264(self) -> int:
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['x264']

    @per_codec_x264.setter
    def per_codec_x264(self, x264_tasks: int):
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['x264'] = x264_tasks

    @property
    def per_codec_x265(self) -> int:
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['x265']

    @per_codec_x265.setter
    def per_codec_x265(self, x265_tasks: int):
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['x265'] = x265_tasks

    @property
    def per_codec_vp9(self) -> int:
        with self._settings_thread_lock:
            return self._per_codec_parallel_tasks['vp9']

    @per_codec_vp9.setter
    def per_codec_vp9(self, vp9_tasks: int):
        with self._settings_thread_lock:
            self._per_codec_parallel_tasks['vp9'] = vp9_tasks

    @property
    def is_nvenc_tasks_parallel(self) -> bool:
        with self._settings_thread_lock:
            return self._is_nvenc_tasks_parallel

    @is_nvenc_tasks_parallel.setter
    def is_nvenc_tasks_parallel(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_nvenc_tasks_parallel = is_enabled

    @property
    def parallel_nvenc_workers(self) -> int:
        with self._settings_thread_lock:
            return self._parallel_nvenc_workers

    @parallel_nvenc_workers.setter
    def parallel_nvenc_workers(self, number_of_workers: int):
        with self._settings_thread_lock:
            if number_of_workers == 0:
                self._parallel_nvenc_workers = None
            else:
                self._parallel_nvenc_workers = number_of_workers

    @property
    def is_auto_cropping_inputs(self) -> bool:
        with self._settings_thread_lock:
            return self._is_auto_cropping_inputs

    @is_auto_cropping_inputs.setter
    def is_auto_cropping_inputs(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_auto_cropping_inputs = is_enabled

    @property
    def is_encoding_parallel_watch_folders(self) -> bool:
        with self._settings_thread_lock:
            return self._is_encoding_parallel_watch_folders

    @is_encoding_parallel_watch_folders.setter
    def is_encoding_parallel_watch_folders(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_encoding_parallel_watch_folders = is_enabled

    @property
    def is_watch_folders_waiting_for_tasks(self) -> bool:
        with self._settings_thread_lock:
            return self._is_watch_folders_waiting_for_tasks

    @is_watch_folders_waiting_for_tasks.setter
    def is_watch_folders_waiting_for_tasks(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_watch_folders_waiting_for_tasks = is_enabled

    @property
    def is_watch_folders_moving_to_done(self) -> bool:
        with self._settings_thread_lock:
            return self._is_watch_folders_moving_to_done

    @is_watch_folders_moving_to_done.setter
    def is_watch_folders_moving_to_done(self, is_enabled: bool):
        with self._settings_thread_lock:
            self._is_watch_folders_moving_to_done = is_enabled

    def save(self):
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
        self._save_parallel_nvenc_workers_option()
        self._save_per_codec_parallel_tasks_options()

    def _save_parallel_nvenc_workers_option(self):
        if self.parallel_nvenc_workers:
            self._settings.set_int(self.PARALLEL_NVENC_TASKS, self.parallel_nvenc_workers)
        else:
            self._settings.set_int(self.PARALLEL_NVENC_TASKS, 0)

    def _save_per_codec_parallel_tasks_options(self):
        self._settings.set_int(self.X264_TASKS, self._per_codec_parallel_tasks['x264'])
        self._settings.set_int(self.X265_TASKS, self._per_codec_parallel_tasks['x265'])
        self._settings.set_int(self.VP9_TASKS, self._per_codec_parallel_tasks['vp9'])


def create_config_directory():
    directory_helper.create_application_config_directory(APPLICATION_CONFIG_DIRECTORY,
                                                         DEFAULT_APPLICATION_TEMP_DIRECTORY)


def create_temp_directory(app_settings: Settings):
    try:
        os.mkdir(app_settings.temp_directory)
    except FileExistsError:
        logging.info('--- TEMP DIRECTORY ALREADY EXISTS ---\n' + app_settings.temp_directory)


def clear_temp_directory(app_settings: Settings):
    try:
        shutil.rmtree(app_settings.get_new_temp_directory())
    except OSError:
        logging.error('--- FAILED TO CLEAR TEMP DIRECTORY ---\n' + app_settings.get_new_temp_directory())
