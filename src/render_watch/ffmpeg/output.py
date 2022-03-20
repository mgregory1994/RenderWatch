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


from datetime import datetime

from render_watch.ffmpeg import input


CONTAINERS = ('.mp4', '.mkv', '.ts', '.webm')

ALIAS_COUNTER = -1


class OutputFile:
    def __init__(self, input_file: input.InputFile, output_file_dir: str, app_preferences):
        self.input_file = input_file
        self._dir = output_file_dir
        self._name = input_file.name
        self._extension = '.mp4'
        self._temp_output_file = TempOutputFile(input_file, app_preferences.get_temp_directory())
        self.size = None
        self.avg_bitrate = None
        self.is_use_temp_file = False

    @property
    def name(self) -> str:
        if self.is_use_temp_file:
            return self._temp_output_file.name
        return self._name

    @name.setter
    def name(self, name_value: str):
        if self.is_use_temp_file:
            self._temp_output_file.name = name_value
        else:
            self._name = name_value

    def get_temp_name(self) -> str:
        return self._temp_output_file.name

    @property
    def extension(self) -> str:
        if self.is_use_temp_file:
            return self._temp_output_file.extension
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        if extension_value is None:
            return

        if self.is_use_temp_file:
            self._temp_output_file.extension = extension_value
        else:
            self._extension = extension_value

    @property
    def dir(self) -> str:
        if self.is_use_temp_file:
            return self._temp_output_file.dir
        return self._dir

    @dir.setter
    def dir(self, dir_path: str | None):
        if dir_path is None:
            return

        if self.is_use_temp_file:
            self._temp_output_file.dir = dir_path
        else:
            self._dir = dir_path

    def get_temp_dir(self) -> str:
        return self._temp_output_file.dir

    @property
    def file_path(self):
        if self.input_file.is_folder:
            if self.is_use_temp_file:
                return self._temp_output_file.dir
            return self.dir

        if self.is_use_temp_file:
            return self._temp_output_file.file_path
        return ''.join([self.dir,
                        '/',
                        self.name,
                        self.extension])


class TempOutputFile:
    def __init__(self, input_file: input.InputFile, temp_output_file_dir: str):
        self._dir = temp_output_file_dir
        self.name = AliasGenerator.generate_alias_from_name(input_file.name)
        self._extension = '.mp4'

    @property
    def dir(self) -> str:
        return self._dir

    @dir.setter
    def dir(self, dir_path: str):
        if dir_path is None:
            return

        self._dir = dir_path

    @property
    def extension(self) -> str:
        return self._extension

    @extension.setter
    def extension(self, extension_value: str | None):
        if extension_value is None:
            return

        self._extension = extension_value

    @property
    def file_path(self):
        if self.extension:
            return ''.join([self.dir,
                            '/',
                            self.name,
                            self.extension])


class AliasGenerator:

    global ALIAS_COUNTER

    @staticmethod
    def generate_alias_from_name(name):
        """
        Creates a unique alias based off of the first character of the given name.

        :param name: Name to generate an alias from.
        """
        global ALIAS_COUNTER
        ALIAS_COUNTER += 1

        current_date_time = datetime.now().strftime('_%m-%d-%Y_%H%M%S')

        return name[0] + str(ALIAS_COUNTER) + current_date_time
