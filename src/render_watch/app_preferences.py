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

from PySide6 import QtCore


APP_NAME = 'io.github.renderwatch.RenderWatch'
ORG_NAME = 'Michael Gregory'

DEFAULT_APPLICATION_TEMP_DIRECTORY = os.path.join(os.getenv('HOME'), '.config', 'Render Watch', 'temp')


class Settings:
    def __init__(self):
        self._settings = QtCore.QSettings(ORG_NAME, APP_NAME)

        self.is_nvenc_tasks_parallel = self._settings.value('parallel_nvenc_tasks', 'true') == 'true'
        self._parallel_nvenc_workers = self._settings.value('parallel_nvenc_workers', None, int)
        self.is_encoding_parallel_tasks = self._settings.value('parallel_encoding_tasks', 'false') == 'true'
        self.per_codec_parallel_tasks = {
            'x264': self._settings.value('per_codec_x264', 2, int),
            'x265': self._settings.value('per_codec_x265', 2, int),
            'vp9': self._settings.value('per_codec_vp9', 2, int)
        }
        self.is_encoding_parallel_method_chunking = self._settings.value('parallel_encoding_method_chunking',
                                                                         'false') == 'true'
        self.is_auto_cropping_inputs = self._settings.value('auto_crop_inputs', 'true') == 'true'
        self.is_encoding_parallel_watch_folders = self._settings.value('parallel_encode_watch_folders',
                                                                       'false') == 'true'
        self.is_watch_folders_waiting_for_tasks = self._settings.value('watch_folders_wait_for_tasks', 'true') == 'true'
        self.is_watch_folders_moving_to_done = self._settings.value('watch_folders_move_to_done', 'true') == 'true'
        self._temp_directory = self._settings.value('temp_directory', DEFAULT_APPLICATION_TEMP_DIRECTORY, str)
        self._new_temp_directory = None
        self.is_clearing_temp_directory = self._settings.value('clear_temp_directory', 'false') == 'true'
        self.is_overwriting_output_files = self._settings.value('overwrite_output_files', 'true') == 'true'
        self.output_directory = self._settings.value('output_directory', os.getenv('HOME'), str)
        self.is_app_dark_mode = self._settings.value('dark_mode', 'true') == 'true'
        self.is_encoder_showing_preview = self._settings.value('encoder_preview', 'true') == 'true'
        self.app_window_state = self._settings.value('window_state', None)
        self.app_window_geometry = self._settings.value('window_geometry', None)
        self.sidebar_splitter_state = self._settings.value('sidebar_splitter_state', None)
        self.preview_splitter_state = self._settings.value('preview_splitter_state', None)

    @property
    def temp_directory(self) -> str:
        return self._temp_directory

    @temp_directory.setter
    def temp_directory(self, temp_directory_path: str):
        if temp_directory_path == self.temp_directory:
            self._new_temp_directory = None
        else:
            self._new_temp_directory = temp_directory_path

    def get_new_temp_directory(self) -> str:
        if self._new_temp_directory is None:
            return self.temp_directory
        return self._new_temp_directory

    @property
    def parallel_nvenc_workers(self) -> int:
        return self._parallel_nvenc_workers

    @parallel_nvenc_workers.setter
    def parallel_nvenc_workers(self, number_of_workers: int):
        if number_of_workers == 0:
            self._parallel_nvenc_workers = None
        else:
            self._parallel_nvenc_workers = number_of_workers

    def save(self):
        self._settings.setValue('parallel_nvenc_tasks', self.is_nvenc_tasks_parallel)
        self._settings.setValue('parallel_encoding_tasks', self.is_encoding_parallel_tasks)
        self._settings.setValue('parallel_encoding_method_chunking', self.is_encoding_parallel_method_chunking)
        self._settings.setValue('auto_crop_inputs', self.is_auto_cropping_inputs)
        self._settings.setValue('parallel_encode_watch_folders', self.is_encoding_parallel_watch_folders)
        self._settings.setValue('watch_folders_wait_for_tasks', self.is_watch_folders_waiting_for_tasks)
        self._settings.setValue('watch_folders_move_to_done', self.is_watch_folders_moving_to_done)
        self._settings.setValue('clear_temp_directory', self.is_clearing_temp_directory)
        self._settings.setValue('temp_directory', self.get_new_temp_directory())
        self._settings.setValue('overwrite_output_files', self.is_overwriting_output_files)
        self._settings.setValue('output_directory', self.output_directory)
        self._settings.setValue('dark_mode', self.is_app_dark_mode)
        self._settings.setValue('encoder_preview', self.is_encoder_showing_preview)
        self._settings.setValue('window_state', self.app_window_state)
        self._settings.setValue('window_geometry', self.app_window_geometry)
        self._settings.setValue('sidebar_splitter_state', self.sidebar_splitter_state)
        self._settings.setValue('preview_splitter_state', self.preview_splitter_state)
        self._save_parallel_nvenc_workers_option()
        self._save_per_codec_parallel_tasks_options()

        self._settings.sync()

    def _save_parallel_nvenc_workers_option(self):
        if self.parallel_nvenc_workers:
            self._settings.setValue('parallel_nvenc_workers', self.parallel_nvenc_workers)
        else:
            self._settings.remove('parallel_nvenc_workers')

    def _save_per_codec_parallel_tasks_options(self):
        self._settings.setValue('per_codec_x264', self.per_codec_parallel_tasks['x264'])
        self._settings.setValue('per_codec_x265', self.per_codec_parallel_tasks['x265'])
        self._settings.setValue('per_codec_vp9', self.per_codec_parallel_tasks['vp9'])


def create_temp_directory(app_settings: Settings):
    try:
        os.mkdir(app_settings.temp_directory)
    except FileExistsError:
        logging.info('--- TEMP DIRECTORY ALREADY EXISTS ---\n' + app_settings.temp_directory)


def clear_temp_directory(app_settings: Settings):
    try:
        if app_settings.is_clearing_temp_directory:
            shutil.rmtree(app_settings.get_new_temp_directory())
    except OSError:
        logging.error('--- FAILED TO CLEAR TEMP DIRECTORY ---\n' + app_settings.get_new_temp_directory())
