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


VALID_EXTENSIONS = (
    'mp4', 'm4v', 'mov', 'mkv', 'ts', 'm2ts', 'mpg', 'webm', 'wmv', 'vob', 'avi', 'aac', 'wav', 'flac', 'mp3'
)


class InputFile:
    def __init__(self, input_file_path: str, folder=False):
        self.file_path = input_file_path
        self.name = None
        self.size = None
        self.duration = None
        self.extension = None
        self.video_streams = {}
        self.audio_streams = {}
        self.subtitle_streams = {}
        self.is_video = False
        self.is_audio = False
        self.is_folder = folder

        generate_info(self)


def generate_info(input_file: InputFile):
    pass
