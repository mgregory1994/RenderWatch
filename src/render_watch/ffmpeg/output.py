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


ALIAS_COUNTER = -1


class OutputFile:
    def __init__(self, input_file: input.InputFile, output_file_dir: str):
        self.dir = output_file_dir
        self.name = input_file.name
        self.extension = None
        self.size = None
        self.avg_bitrate = None

    @property
    def file_path(self):
        if self.extension:
            return ''.join([self.dir,
                            '/',
                            self.name,
                            '.',
                            self.extension])


class TempOutputFile:
    def __init__(self, input_file: input.InputFile, temp_output_file_dir: str):
        self.dir = temp_output_file_dir
        self.name = AliasGenerator.generate_alias_from_name(input_file.name)
        self.extension = None

    @property
    def file_path(self):
        if self.extension:
            return ''.join([self.dir,
                            '/',
                            self.name,
                            '.',
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
