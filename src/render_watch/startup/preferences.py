"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import os
import shutil

from render_watch.encoding import directory_helper


class Preferences:
    parallel_tasks_values_list = ('2', '3', '4', '6', '8')
    concurrent_nvenc_values_list = ('auto', '1', '2', '3', '4', '5', '6', '7', '8')
    default_config_directory = os.path.join(os.getenv('HOME'), '.config', 'Render Watch')
    default_temp_directory = os.path.join(default_config_directory, 'temp')

    def __init__(self):
        self.__parallel_tasks_value = 2
        self.concurrent_nvenc = True
        self.__concurrent_nvenc_value = 0
        self.concurrent_watch_folder = False
        self.watch_folder_wait_for_other_tasks = True
        self.watch_folder_move_finished_to_done = True
        self.__temp_directory = Preferences.default_temp_directory
        self.__new_temp_directory = None
        self.clear_temp_directory_on_exit = False
        self.overwrite_outputs = True
        self.output_directory = os.getenv('HOME')
        self.use_dark_mode = True
        self.window_dimensions = (1000, 600)
        self.window_maximized = False

        directory_helper.create_config_directory()

    @property
    def temp_directory(self):
        return self.__temp_directory

    @temp_directory.setter
    def temp_directory(self, directory_path):
        if directory_path == self.__temp_directory:
            self.__new_temp_directory = None
        else:
            self.__new_temp_directory = directory_path

    @temp_directory.setter
    def temp_directory_overwrite(self, directory_path):
        self.__temp_directory = directory_path

    @property
    def parallel_tasks(self):
        return self.__parallel_tasks_value

    @property
    def parallel_tasks_as_string(self):
        return str(self.__parallel_tasks_value)

    @parallel_tasks.setter
    def parallel_tasks(self, value):
        if value in self.parallel_tasks_values_list:
            self.__parallel_tasks_value = int(value)

    @property
    def concurrent_nvenc_value(self):
        return self.__concurrent_nvenc_value

    @property
    def concurrent_nvenc_value_as_string(self):
        if self.concurrent_nvenc_value == 0:
            return 'auto'

        return str(self.__concurrent_nvenc_value)

    @concurrent_nvenc_value.setter
    def concurrent_nvenc_value(self, value):
        if value == 'auto':
            self.__concurrent_nvenc_value = 0
        elif value in self.concurrent_nvenc_values_list:
            self.__concurrent_nvenc_value = int(value)

    @staticmethod
    def create_temp_directory(preferences):
        try:
            os.mkdir(preferences.temp_directory)
        except FileExistsError:
            logging.info('--- TEMP DIRECTORY ALREADY EXISTS ---')

    @staticmethod
    def clear_temp_directory(preferences):
        try:
            if preferences.clear_temp_directory_on_exit:
                shutil.rmtree(Preferences.__get_preferences_temp_directory_to_clear(preferences))
        except OSError:
            logging.error('--- FAILED TO REMOVE TEMP DIRECTORY: %s ---', preferences.temp_directory)

    @staticmethod
    def __get_preferences_temp_directory_to_clear(preferences):
        if preferences.__new_temp_directory is None:
            return preferences.temp_directory
        else:
            return preferences.__new_temp_directory

    @staticmethod
    def save_preferences(preferences):
        with open(os.path.join(Preferences.default_config_directory, 'prefs'), 'w') as preferences_file:
            try:
                preferences_file.writelines(Preferences.__get_preferences_lines(preferences))
            except:
                logging.error('--- FAILED TO SAVE PREFERENCES ---')

    @staticmethod
    def __get_preferences_lines(preferences):
        output_directory_arg = 'out_dir=' + preferences.output_directory + '\n'
        parallel_tasks_arg = 'parallel_tasks=' + preferences.parallel_tasks_as_string + '\n'
        concurrent_nvenc_value_arg = 'concurrent_nvenc_value=' + preferences.concurrent_nvenc_value_as_string + '\n'
        temp_directory_arg = Preferences.__get_temp_directory_arg(preferences)
        clear_temp_directory_on_exit_arg = Preferences.__get_clear_temp_directory_on_exit_arg(preferences)
        overwrite_outputs_arg = Preferences.__get_overwrite_outputs_arg(preferences)
        concurrent_watch_folder_arg = Preferences.__get_concurrent_watch_folder_arg(preferences)
        watch_folder_move_to_done_arg = Preferences.__get_watch_folder_move_to_done_arg(preferences)
        watch_folder_wait_for_others_arg = Preferences.__get_watch_folder_wait_for_other_tasks_arg(preferences)
        window_dimensions_arg = Preferences.__get_window_dimensions_arg(preferences)
        window_maximized_arg = Preferences.__get_window_maximized_arg(preferences)
        use_dark_mode_arg = Preferences.__get_use_dark_mode_arg(preferences)
        concurrent_nvenc_arg = Preferences.__get_concurrent_nvenc_arg(preferences)

        return [temp_directory_arg, clear_temp_directory_on_exit_arg, overwrite_outputs_arg, output_directory_arg,
                parallel_tasks_arg, concurrent_nvenc_arg, concurrent_nvenc_value_arg, concurrent_watch_folder_arg,
                watch_folder_move_to_done_arg, watch_folder_wait_for_others_arg, window_dimensions_arg,
                window_maximized_arg, use_dark_mode_arg]

    @staticmethod
    def __get_window_dimensions_arg(preferences):
        window_width, window_height = preferences.window_dimensions
        return 'window_size=' + str(window_width) + 'x' + str(window_height) + '\n'

    @staticmethod
    def __get_concurrent_nvenc_arg(preferences):
        if preferences.concurrent_nvenc:
            concurrent_nvenc_arg = 'concurrent_nvenc=true\n'
        else:
            concurrent_nvenc_arg = 'concurrent_nvenc=false\n'

        return concurrent_nvenc_arg

    @staticmethod
    def __get_concurrent_watch_folder_arg(preferences):
        if preferences.concurrent_watch_folder:
            concurrent_watch_folder_arg = 'concurrent_watch_folder=true\n'
        else:
            concurrent_watch_folder_arg = 'concurrent_watch_folder=false\n'

        return concurrent_watch_folder_arg

    @staticmethod
    def __get_watch_folder_wait_for_other_tasks_arg(preferences):
        if preferences.watch_folder_wait_for_other_tasks:
            watch_folder_wait_for_others_arg = 'watch_folder_wait_for_others=true\n'
        else:
            watch_folder_wait_for_others_arg = 'watch_folder_wait_for_others=false\n'

        return watch_folder_wait_for_others_arg

    @staticmethod
    def __get_watch_folder_move_to_done_arg(preferences):
        if preferences.watch_folder_move_finished_to_done:
            watch_folder_move_to_done_arg = 'watch_folder_move_finished_to_done=true\n'
        else:
            watch_folder_move_to_done_arg = 'watch_folder_move_finished_to_done=false\n'

        return watch_folder_move_to_done_arg

    @staticmethod
    def __get_temp_directory_arg(preferences):
        if preferences.__new_temp_directory is not None:
            temp_directory_arg = 'temp_dir=' + preferences.__new_temp_directory + '\n'
        else:
            temp_directory_arg = 'temp_dir=' + preferences.temp_directory + '\n'

        return temp_directory_arg

    @staticmethod
    def __get_window_maximized_arg(preferences):
        if preferences.window_maximized:
            window_maximized_arg = 'maximized=true\n'
        else:
            window_maximized_arg = 'maximized=false\n'

        return window_maximized_arg

    @staticmethod
    def __get_use_dark_mode_arg(preferences):
        if preferences.use_dark_mode:
            use_dark_mode_arg = 'dark_mode=true\n'
        else:
            use_dark_mode_arg = 'dark_mode=false\n'

        return use_dark_mode_arg

    @staticmethod
    def __get_clear_temp_directory_on_exit_arg(preferences):
        if preferences.clear_temp_directory_on_exit:
            clear_temp_directory_on_exit_arg = 'clear_temp=true\n'
        else:
            clear_temp_directory_on_exit_arg = 'clear_temp=false\n'

        return clear_temp_directory_on_exit_arg

    @staticmethod
    def __get_overwrite_outputs_arg(preferences):
        if preferences.overwrite_outputs:
            overwrite_outputs_arg = 'overwrite_outputs=true\n'
        else:
            overwrite_outputs_arg = 'overwrite_outputs=false\n'

        return overwrite_outputs_arg

    @staticmethod
    def load_preferences(preferences):
        try:
            with open(os.path.join(Preferences.default_config_directory, 'prefs'), 'r') as preferences_file:
                for preferences_string_line in preferences_file.readlines():
                    args = preferences_string_line.rstrip('\n').split('=')

                    if Preferences.__processed_temp_directory_overwrite_arg(args, preferences):
                        continue

                    if Preferences.__processed_output_directory_arg(args, preferences):
                        continue

                    if Preferences.__processed_parallel_tasks_arg(args, preferences):
                        continue

                    if Preferences.__processed_concurrent_nvenc_value_arg(args, preferences):
                        continue

                    if Preferences.__processed_concurrent_nvenc_arg(args, preferences):
                        continue

                    if Preferences.__processed_concurrent_watch_folder_arg(args, preferences):
                        continue

                    if Preferences.__processed_watch_folder_wait_for_other_tasks_arg(args, preferences):
                        continue

                    if Preferences.__processed_watch_folder_move_finished_to_done_arg(args, preferences):
                        continue

                    if Preferences.__processed_window_dimensions_arg(args, preferences):
                        continue

                    if Preferences.__processed_window_maximized_arg(args, preferences):
                        continue

                    if Preferences.__processed_use_dark_mode_arg(args, preferences):
                        continue

                    if Preferences.__processed_clear_temp_directory_on_exit_arg(args, preferences):
                        continue

                    if Preferences.__processed_overwrite_outputs_arg(args, preferences):
                        continue
        except:
            logging.info('--- USING DEFAULT PREFERENCES ---')

    @staticmethod
    def __processed_temp_directory_overwrite_arg(args, preferences):
        if 'temp_dir' in args:
            try:
                preferences.temp_directory_overwrite = args[1]
            finally:
                return True

        return False

    @staticmethod
    def __processed_output_directory_arg(args, preferences):
        if 'out_dir' in args:
            try:
                preferences.output_directory = args[1]
            finally:
                return True

        return False

    @staticmethod
    def __processed_parallel_tasks_arg(args, preferences):
        if 'parallel_tasks' in args:
            try:
                preferences.parallel_tasks = args[1]
            finally:
                return True

        return False

    @staticmethod
    def __processed_concurrent_nvenc_value_arg(args, preferences):
        if 'concurrent_nvenc_value' in args:
            try:
                preferences.concurrent_nvenc_value = args[1]
            finally:
                return True

        return False

    @staticmethod
    def __processed_concurrent_nvenc_arg(args, preferences):
        if 'concurrent_nvenc' in args:
            try:
                preferences.concurrent_nvenc = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_concurrent_watch_folder_arg(args, preferences):
        if 'concurrent_watch_folder' in args:
            try:
                preferences.concurrent_watch_folder = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_watch_folder_wait_for_other_tasks_arg(args, preferences):
        if 'watch_folder_wait_for_others' in args:
            try:
                preferences.watch_folder_wait_for_other_tasks = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_watch_folder_move_finished_to_done_arg(args, preferences):
        if 'watch_folder_move_finished_to_done' in args:
            try:
                preferences.watch_folder_move_finished_to_done = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_window_dimensions_arg(args, preferences):
        if 'window_size' in args:
            try:
                window_size = args[1].split('x')
                preferences.window_dimensions = (int(window_size[0]), int(window_size[1]))
            finally:
                return True

        return False

    @staticmethod
    def __processed_window_maximized_arg(args, preferences):
        if 'maximized' in args:
            try:
                preferences.window_maximized = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_use_dark_mode_arg(args, preferences):
        if 'dark_mode' in args:
            try:
                preferences.use_dark_mode = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_clear_temp_directory_on_exit_arg(args, preferences):
        if 'clear_temp' in args:
            try:
                preferences.clear_temp_directory_on_exit = 'true' in args
            finally:
                return True

        return False

    @staticmethod
    def __processed_overwrite_outputs_arg(args, preferences):
        if 'overwrite_outputs' in args:
            try:
                preferences.overwrite_outputs = 'true' in args
            finally:
                return True

        return False
