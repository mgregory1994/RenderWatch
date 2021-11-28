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
import os
import re
import shutil

from render_watch.helpers import directory_helper


class ApplicationPreferences:
    """
    Saves, loads, and stores application preferences.
    """

    PARALLEL_TASKS_VALUES = ('2', '3', '4', '6', '8', '10', '12', '14', '16')
    PER_CODEC_TASKS_VALUES = ('1', '2', '3', '4', '6', '8', '10', '12', '14', '16')
    CONCURRENT_NVENC_VALUES = ('auto', '1', '2', '3', '4', '5', '6', '7', '8')
    DEFAULT_APPLICATION_DATA_DIRECTORY = os.path.join(os.getenv('HOME'), '.config', 'Render Watch')
    DEFAULT_APPLICATION_TEMP_DIRECTORY = os.path.join(DEFAULT_APPLICATION_DATA_DIRECTORY, 'temp')

    def __init__(self):
        self._parallel_tasks_value = 2
        self.is_concurrent_nvenc_enabled = True
        self._concurrent_nvenc_value = 0
        self.is_per_codec_parallel_tasks_enabled = False
        self.per_codec_parallel_tasks = {
            'x264': 1,
            'x265': 1,
            'vp9': 1
        }
        self.is_concurrent_watch_folder_enabled = False
        self.is_watch_folder_wait_for_tasks_enabled = True
        self.is_watch_folder_move_tasks_to_done_enabled = True
        self._temp_directory = ApplicationPreferences.DEFAULT_APPLICATION_TEMP_DIRECTORY
        self._new_temp_directory = None
        self.is_clear_temp_directory_enabled = False
        self.is_overwrite_outputs_enabled = True
        self.output_directory = os.getenv('HOME')
        self.is_dark_mode_enabled = True
        self.window_dimensions = (1000, 600)
        self.is_window_maximized = False
        self.settings_sidebar_position = -1

        directory_helper.create_application_config_directory(ApplicationPreferences.DEFAULT_APPLICATION_DATA_DIRECTORY,
                                                             self._temp_directory)

    @property
    def temp_directory(self):
        return self._temp_directory

    def get_currently_set_temp_directory(self):
        if self._new_temp_directory:
            return self._new_temp_directory
        return self._temp_directory

    def set_temp_directory(self, directory, overwrite=False):
        """
        Sets a new temp directory for Render Watch to store preview/encode temporary files.
        Applies on application restart.
        
        :param directory: New temp directory.
        :param overwrite: Overwrite the temp directory currently in use.
        """
        if overwrite:
            self._temp_directory = directory
        elif directory == self._temp_directory:
            self._new_temp_directory = None
        else:
            self._new_temp_directory = directory

    @property
    def parallel_tasks(self):
        return self._parallel_tasks_value

    @parallel_tasks.setter
    def parallel_tasks(self, value):
        if value in self.PARALLEL_TASKS_VALUES:
            self._parallel_tasks_value = int(value)

    def get_concurrent_nvenc_value(self, string=False):
        if string:
            return self._get_concurrent_nvenc_value_as_string()
        return self._concurrent_nvenc_value

    def _get_concurrent_nvenc_value_as_string(self):
        if self._concurrent_nvenc_value == 0:
            return 'auto'
        return str(self._concurrent_nvenc_value)

    def set_concurrent_nvenc_value(self, value):
        if value == 'auto':
            self._concurrent_nvenc_value = 0
        elif value in self.CONCURRENT_NVENC_VALUES:
            self._concurrent_nvenc_value = int(value)

    @staticmethod
    def create_temp_directory(application_preferences):
        """
        Creates the application's temp directory.

        :param application_preferences: Application's preferences.
        """
        try:
            os.mkdir(application_preferences.temp_directory)
        except FileExistsError:
            logging.info('--- TEMP DIRECTORY ALREADY EXISTS ---')

    @staticmethod
    def clear_temp_directory(application_preferences):
        """
        Deletes all files in the application's temporary directory.

        :param application_preferences: Application's preferences.
        """
        try:
            if application_preferences.is_clear_temp_directory_enabled:
                shutil.rmtree(application_preferences.get_currently_set_temp_directory())
        except OSError:
            logging.error('--- FAILED TO REMOVE TEMP DIRECTORY: %s ---', application_preferences.temp_directory)

    @staticmethod
    def save_preferences(application_preferences):
        """
        Writes the application's preferences to a 'prefs' file in the DEFAULT_APPLICATION_DATA_DIRECTORY.

        :param application_preferences: Application's preferences.
        """
        try:
            with open(os.path.join(ApplicationPreferences.DEFAULT_APPLICATION_DATA_DIRECTORY, 'prefs'),
                      'w') as preferences_file:
                preferences_file.writelines(ApplicationPreferences._get_preferences_args(application_preferences))
        except Exception() as excpetion:
            print(excpetion)
            logging.error('--- FAILED TO SAVE PREFERENCES ---')

    @staticmethod
    def _get_preferences_args(application_preferences):
        return [
            ApplicationPreferences._get_temp_directory_arg(application_preferences),
            ApplicationPreferences._get_clearing_temp_directory_arg(application_preferences),
            ApplicationPreferences._get_overwriting_outputs_arg(application_preferences),
            ApplicationPreferences._get_output_directory_arg(application_preferences),
            ApplicationPreferences._get_parallel_tasks_arg(application_preferences),
            ApplicationPreferences._get_per_codec_parallel_tasks_enabled_arg(application_preferences),
            ApplicationPreferences._get_per_codec_parallel_tasks_arg(application_preferences),
            ApplicationPreferences._get_concurrent_nvenc_arg(application_preferences),
            ApplicationPreferences._get_concurrent_nvenc_value_arg(application_preferences),
            ApplicationPreferences._get_concurrent_watch_folder_arg(application_preferences),
            ApplicationPreferences._get_watch_folder_move_tasks_to_done_arg(application_preferences),
            ApplicationPreferences._get_watch_folder_wait_for_tasks_arg(application_preferences),
            ApplicationPreferences._get_use_dark_mode_arg(application_preferences),
            ApplicationPreferences._get_window_dimensions_arg(application_preferences),
            ApplicationPreferences._get_window_maximized_arg(application_preferences),
            ApplicationPreferences._get_settings_sidebar_position_arg(application_preferences)
        ]

    @staticmethod
    def _get_output_directory_arg(application_preferences):
        return 'out_dir=' + application_preferences.output_directory + '\n'

    @staticmethod
    def _get_parallel_tasks_arg(application_preferences):
        return 'parallel_tasks=' + str(application_preferences.parallel_tasks) + '\n'

    @staticmethod
    def _get_per_codec_parallel_tasks_enabled_arg(application_preferences):
        return 'per_codec_tasks_enabled=' + str(application_preferences.is_per_codec_parallel_tasks_enabled) + '\n'

    @staticmethod
    def _get_per_codec_parallel_tasks_arg(application_preferences):
        return 'per_codec_task_values=' \
               + 'x264:' + str(application_preferences.per_codec_parallel_tasks['x264']) + ',' \
               + 'x265:' + str(application_preferences.per_codec_parallel_tasks['x265']) + ',' \
               + 'vp9:' + str(application_preferences.per_codec_parallel_tasks['vp9']) + '\n'

    @staticmethod
    def _get_concurrent_nvenc_value_arg(application_preferences):
        return 'concurrent_nvenc_value=' + application_preferences.get_concurrent_nvenc_value(string=True) + '\n'

    @staticmethod
    def _get_window_dimensions_arg(application_preferences):
        window_width, window_height = application_preferences.window_dimensions
        return 'window_size=' + str(window_width) + 'x' + str(window_height) + '\n'

    @staticmethod
    def _get_concurrent_nvenc_arg(application_preferences):
        return 'concurrent_nvenc=' + str(application_preferences.is_concurrent_nvenc_enabled) + '\n'

    @staticmethod
    def _get_concurrent_watch_folder_arg(application_preferences):
        return 'concurrent_watch_folder=' + str(application_preferences.is_concurrent_watch_folder_enabled) + '\n'

    @staticmethod
    def _get_watch_folder_wait_for_tasks_arg(application_preferences):
        return 'watch_folder_wait_for_tasks=' \
               + str(application_preferences.is_watch_folder_wait_for_tasks_enabled) \
               + '\n'

    @staticmethod
    def _get_watch_folder_move_tasks_to_done_arg(application_preferences):
        return 'watch_folder_move_tasks_to_done=' \
               + str(application_preferences.is_watch_folder_move_tasks_to_done_enabled) \
               + '\n'

    @staticmethod
    def _get_temp_directory_arg(application_preferences):
        return 'temp_dir=' + application_preferences.get_currently_set_temp_directory() + '\n'

    @staticmethod
    def _get_window_maximized_arg(application_preferences):
        return 'maximized=' + str(application_preferences.is_window_maximized) + '\n'

    @staticmethod
    def _get_settings_sidebar_position_arg(application_preferences):
        return 'sidebar_position=' + str(application_preferences.settings_sidebar_position) + '\n'

    @staticmethod
    def _get_use_dark_mode_arg(application_preferences):
        return 'dark_mode=' + str(application_preferences.is_dark_mode_enabled) + '\n'

    @staticmethod
    def _get_clearing_temp_directory_arg(application_preferences):
        return 'clear_temp=' + str(application_preferences.is_clear_temp_directory_enabled) + '\n'

    @staticmethod
    def _get_overwriting_outputs_arg(application_preferences):
        return 'overwrite_outputs=' + str(application_preferences.is_overwrite_outputs_enabled) + '\n'

    @staticmethod
    def load_preferences(application_preferences):
        """
        Loads application preferences from a 'prefs' file in the DEFAULT_APPLICATION_DATA_DIRECTORY.

        :param application_preferences: Application's preferences.
        """
        try:
            with open(os.path.join(ApplicationPreferences.DEFAULT_APPLICATION_DATA_DIRECTORY, 'prefs'), 'r') as preferences_file:
                for preferences_arg in preferences_file.readlines():
                    split_arg = preferences_arg.rstrip('\n').split('=')
                    ApplicationPreferences._set_preferences_args(split_arg, application_preferences)
        except:
            logging.info('--- USING DEFAULT PREFERENCES ---')

    @staticmethod
    def _set_preferences_args(split_arg, application_preferences):
        if ApplicationPreferences._set_temp_directory_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_output_directory_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_parallel_tasks_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_per_codec_parallel_tasks_enabled_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_per_codec_parallel_tasks_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_concurrent_nvenc_value_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_concurrent_nvenc_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_concurrent_watch_folder_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_watch_folder_wait_for_tasks_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_watch_folder_move_tasks_to_done_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_window_dimensions_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_window_maximized_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_settings_sidebar_position_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_use_dark_mode_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_clearing_temp_directory_arg(split_arg, application_preferences):
            return
        if ApplicationPreferences._set_overwriting_outputs_arg(split_arg, application_preferences):
            return

    @staticmethod
    def _set_temp_directory_arg(split_arg, application_preferences):
        try:
            if 'temp_dir' in split_arg:
                application_preferences.set_temp_directory(split_arg[1], overwrite=True)

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_output_directory_arg(split_arg, application_preferences):
        try:
            if 'out_dir' in split_arg:
                application_preferences.output_directory = split_arg[1]

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_parallel_tasks_arg(split_arg, application_preferences):
        try:
            if 'parallel_tasks' in split_arg:
                application_preferences.parallel_tasks = split_arg[1]

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_per_codec_parallel_tasks_enabled_arg(split_arg, application_preferences):
        try:
            if 'per_codec_tasks_enabled' in split_arg:
                application_preferences.is_per_codec_parallel_tasks_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False


    @staticmethod
    def _set_per_codec_parallel_tasks_arg(split_arg, application_preferences):
        try:
            if 'per_codec_task_values' in split_arg:
                ApplicationPreferences._set_per_codec_x264_arg(split_arg, application_preferences)
                ApplicationPreferences._set_per_codec_x265_arg(split_arg, application_preferences)
                ApplicationPreferences._set_per_codec_vp9_arg(split_arg, application_preferences)

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_per_codec_x264_arg(split_arg, application_preferences):
        per_codec_x264_value = int(re.search('x264:\d+', split_arg[1]).group().split(':')[1])
        application_preferences.per_codec_parallel_tasks['x264'] = per_codec_x264_value

    @staticmethod
    def _set_per_codec_x265_arg(split_arg, application_preferences):
        per_codec_x265_value = int(re.search('x265:\d+', split_arg[1]).group().split(':')[1])
        application_preferences.per_codec_parallel_tasks['x265'] = per_codec_x265_value

    @staticmethod
    def _set_per_codec_vp9_arg(split_arg, application_preferences):
        per_codec_vp9_value = int(re.search('vp9:\d+', split_arg[1]).group().split(':')[1])
        application_preferences.per_codec_parallel_tasks['vp9'] = per_codec_vp9_value

    @staticmethod
    def _set_concurrent_nvenc_value_arg(split_arg, application_preferences):
        try:
            if 'concurrent_nvenc_value' in split_arg:
                application_preferences.set_concurrent_nvenc_value(split_arg[1])

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_concurrent_nvenc_arg(split_arg, application_preferences):
        try:
            if 'concurrent_nvenc' in split_arg:
                application_preferences.is_concurrent_nvenc_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_concurrent_watch_folder_arg(split_arg, application_preferences):
        try:
            if 'concurrent_watch_folder' in split_arg:
                application_preferences.is_concurrent_watch_folder_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_watch_folder_wait_for_tasks_arg(split_arg, application_preferences):
        try:
            if 'watch_folder_wait_for_tasks' in split_arg:
                application_preferences.is_watch_folder_wait_for_tasks_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_watch_folder_move_tasks_to_done_arg(split_arg, application_preferences):
        try:
            if 'watch_folder_move_tasks_to_done' in split_arg:
                application_preferences.is_watch_folder_move_tasks_to_done_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_window_dimensions_arg(split_arg, application_preferences):
        try:
            if 'window_size' in split_arg:
                window_size = split_arg[1].split('x')
                application_preferences.window_dimensions = (int(window_size[0]), int(window_size[1]))

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_window_maximized_arg(split_arg, application_preferences):
        try:
            if 'maximized' in split_arg:
                application_preferences.is_window_maximized = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_settings_sidebar_position_arg(split_arg, application_preferences):
        try:
            if 'sidebar_position' in split_arg:
                application_preferences.settings_sidebar_position = int(split_arg[1])

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_use_dark_mode_arg(split_arg, application_preferences):
        try:
            if 'dark_mode' in split_arg:
                application_preferences.is_dark_mode_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_clearing_temp_directory_arg(split_arg, application_preferences):
        try:
            if 'clear_temp' in split_arg:
                application_preferences.is_clear_temp_directory_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def _set_overwriting_outputs_arg(split_arg, application_preferences):
        try:
            if 'overwrite_outputs' in split_arg:
                application_preferences.is_overwrite_outputs_enabled = split_arg[1] == 'True'

                return True
            else:
                return False
        except:
            return False
