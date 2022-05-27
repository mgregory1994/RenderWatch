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


import threading
from datetime import datetime

from render_watch import app_preferences
from render_watch.ffmpeg import input


CONTAINERS = ('.mp4', '.mkv', '.ts', '.webm')

ALIAS_COUNTER = -1


class OutputFile:
    """Class that configures all the necessary information for the output file."""

    def __init__(self, input_file: input.InputFile, app_settings: app_preferences.Settings):
        """
        Initializes the OutputFile class with all the necessary variables for the information of the output file.
        """
        self.input_file = input_file
        self._dir = app_settings.output_directory
        self.name = input_file.name
        self._extension = '.mp4'
        self.size = None
        self.avg_bitrate = None

    @property
    def extension(self) -> str:
        """
        Returns the extension of the output file.

        Returns:
            String that represents the output file's extension.
        """
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        """
        Sets the output file's extension.

        Parameters:
            extension_value: Extension as a string.

        Returns:
            None
        """
        if extension_value is None:
            return

        self._extension = extension_value

    @property
    def dir(self) -> str:
        """
        Returns the directory path that contains the output file.

        Returns:
            String that represents the output file's directory path.
        """
        return self._dir

    @dir.setter
    def dir(self, dir_path: str | None):
        """
        Sets the directory path for the output file.

        Parameters:
            dir_path: Output file's directory path as a string.

        Returns:
            None
        """
        if dir_path is None:
            return

        self._dir = dir_path

    @property
    def file_path(self):
        """
        Returns the complete file path for the output file.

        Returns:
            Output file path as a string.
        """
        if self.input_file.is_folder:
            return self.dir
        return ''.join([self.dir, '/', self.name, self.extension])

    def get_name_and_extension(self):
        if self.input_file.is_folder:
            return self.dir

        return ''.join([self.name, self.extension])


class TempOutputFile:
    """Class that configures the necessary information for the temporary output file."""

    def __init__(self, input_file: input.InputFile, temp_output_file_dir: str):
        """
        Initializes the TempOutputFile class with all the necessary variables for the information of the
        temporary output file.
        """
        self._dir = temp_output_file_dir
        self.name = AliasGenerator.generate_alias_from_name(input_file.name)
        self._extension = '.mp4'
        self._crop_preview_file_path = None
        self._trim_preview_file_path = None
        self._settings_preview_file_path = None
        self._video_preview_file_path = None
        self._crop_preview_thread_lock = threading.Lock()
        self._trim_preview_thread_lock = threading.Lock()
        self._settings_preview_thread_lock = threading.Lock()
        self._video_preview_thread_lock = threading.Lock()
        self.crop_preview_threading_event = threading.Event()
        self.trim_preview_threading_event = threading.Event()
        self.settings_preview_threading_event = threading.Event()

    @property
    def dir(self) -> str:
        """
        Returns the directory path that contains the temporary output file.

        Returns:
            String that represents the temporary output file's directory path.
        """
        return self._dir

    @dir.setter
    def dir(self, dir_path: str):
        """
        Sets the directory path for the temporary output file.

        Parameters:
            dir_path: Temporary output file's directory path as a string.

        Returns:
            None
        """
        if dir_path is None:
            return

        self._dir = dir_path

    @property
    def extension(self) -> str:
        """
        Returns the extension of the temporary output file.

        Returns:
            String that represents the temporary output file's extension.
        """
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        """
        Sets the temporary output file's extension.

        Parameters:
            extension_value: Extension as a string.

        Returns:
            None
        """
        if extension_value is None:
            return

        self._extension = extension_value

    @property
    def file_path(self):
        """
        Returns the complete file path for the temporary output file.

        Returns:
            Temporary output file path as a string.
        """
        return ''.join([self.dir, '/', self.name, self.extension])

    @property
    def crop_preview_file_path(self) -> str | None:
        """
        Returns the complete file path for the crop preview file. This property is thread safe.

        Returns:
            Crop preview file path as a string or None if not set.
        """
        with self._crop_preview_thread_lock:
            return self._crop_preview_file_path

    @crop_preview_file_path.setter
    def crop_preview_file_path(self, file_path: str):
        """
        Sets the file path for the crop preview file. This property is thread safe.

        Parameters:
            file_path: Complete file path for the crop preview file.

        Returns:
            None
        """
        with self._crop_preview_thread_lock:
            self._crop_preview_file_path = file_path

    @property
    def trim_preview_file_path(self) -> str | None:
        """
        Returns the complete file path for the trim preview file. This property is thread safe.

        Returns:
            Trim preview file as a string or None if not set.
        """
        with self._trim_preview_thread_lock:
            return self._trim_preview_file_path

    @trim_preview_file_path.setter
    def trim_preview_file_path(self, file_path: str):
        """
        Sets the file path for the trim preview file. This property is thread safe.

        Parameters:
            file_path: Complete file path for the trim preview file.

        Returns:
            None
        """
        with self._trim_preview_thread_lock:
            self._trim_preview_file_path = file_path

    @property
    def settings_preview_file_path(self) -> str | None:
        """
        Returns the complete file path for the settings preview file. This property is thread safe.

        Returns:
            Settings preview file as a string or None if not set.
        """
        with self._settings_preview_thread_lock:
            return self._settings_preview_file_path

    @settings_preview_file_path.setter
    def settings_preview_file_path(self, file_path: str):
        """
        Sets the file path for the settings preview file. This property is thread safe.

        Parameters:
            file_path: Complete file path for the settings preview file.

        Returns:
            None
        """
        with self._settings_preview_thread_lock:
            self._settings_preview_file_path = file_path

    @property
    def video_preview_file_path(self) -> str | None:
        """
        Returns the complete file path for the video preview file. This property is thread safe.

        Returns:
            Video preview file as a string or None if not set.
        """
        with self._video_preview_thread_lock:
            return self._video_preview_file_path

    @video_preview_file_path.setter
    def video_preview_file_path(self, file_path: str):
        """
        Sets the file path for the video preview file. This property is thread safe.

        Parameters:
            file_path: Complete file path for the video preview file.

        Returns:
            None
        """
        with self._video_preview_thread_lock:
            self._video_preview_file_path = file_path


class AliasGenerator:
    """Class that contains functions for generating a name alias."""

    global ALIAS_COUNTER

    @staticmethod
    def generate_alias_from_name(name: str) -> str:
        """
        Creates a unique alias based off of the first character of the given name.

        Parameters:
            name: Name to generate a unique alias from.

        Returns:
            Unique alias as a string.
        """
        global ALIAS_COUNTER
        ALIAS_COUNTER += 1

        current_date_time = datetime.now().strftime('_%m-%d-%Y_%H%M%S')

        return name[0] + str(ALIAS_COUNTER) + current_date_time
