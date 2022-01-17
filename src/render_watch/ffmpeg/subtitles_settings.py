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


class SubtitlesSettings:
    """
    Stores all settings for subtitles settings.
    """

    def __init__(self, input_file_info):
        self.subtitle_streams = input_file_info['subtitle_streams']
        self.streams_available = {}
        self.streams_in_use = {}
        self._ffmpeg_args = {}
        self.burn_in_stream_index = None

        self._setup_available_streams()

    def _setup_available_streams(self):
        for index, stream_dictionary in self.subtitle_streams.items():
            self.streams_available[index] = stream_dictionary['info']

    def use_stream(self, stream_info):
        streams_available_keys = list(self.streams_available.keys())
        streams_available_values = list(self.streams_available.values())
        key = streams_available_keys[streams_available_values.index(stream_info)]

        self.streams_available.pop(key, 0)
        self.streams_in_use[key] = stream_info

    def remove_stream(self, stream_info):
        streams_in_use_keys = list(self.streams_in_use.keys())
        streams_in_use_values = list(self.streams_in_use.values())
        key = streams_in_use_keys[streams_in_use_values.index(stream_info)]

        self.streams_in_use.pop(key, 0)
        self.streams_available[key] = stream_info

    def set_stream_method_burn_in(self, stream_info):
        streams_in_use_keys = list(self.streams_in_use.keys())
        streams_in_use_values = list(self.streams_in_use.values())
        self.burn_in_stream_index = streams_in_use_keys[streams_in_use_values.index(stream_info)]

    @property
    def ffmpeg_args(self):
        map_args_list = []

        for key, stream_info in self.streams_in_use.items():
            if key == self.burn_in_stream_index:
                continue

            map_args_list.append('0:' + str(key))

        self._ffmpeg_args['-map'] = map_args_list

        if map_args_list:
            self._ffmpeg_args['-c:s'] = 'copy'
        else:
            self._ffmpeg_args['-c:s'] = None

        return self._ffmpeg_args
