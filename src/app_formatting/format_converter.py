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

gigabyte_in_bytes = 1000000000
megabyte_in_bytes = 1000000
kilobyte_in_bytes = 1000


def get_timecode_from_seconds(seconds):
    hours = int(seconds / 3600)
    seconds_left = seconds % 3600
    minutes = int(seconds_left / 60)
    seconds_left = round(seconds_left % 60, 1)
    timecode = ''
    timecode += __generate_hours_timecode_portion(hours)
    timecode += __generate_minutes_timecode_portion(minutes)
    timecode += __generate_seconds_timecode_portion(seconds_left)

    return timecode


def __generate_hours_timecode_portion(hours):
    if hours == 0:
        timecode_hours_portion = '00:'
    elif hours < 10:
        timecode_hours_portion = '0' + str(hours) + ':'
    else:
        timecode_hours_portion = str(hours) + ':'

    return timecode_hours_portion


def __generate_minutes_timecode_portion(minutes):
    if minutes == 0:
        timecode_minutes_portion = '00:'
    elif minutes < 10:
        timecode_minutes_portion = '0' + str(minutes) + ':'
    else:
        timecode_minutes_portion = str(minutes) + ':'

    return timecode_minutes_portion


def __generate_seconds_timecode_portion(seconds):
    if seconds == 0:
        timecode_seconds_portion = '00'
    elif seconds < 10:
        timecode_seconds_portion = '0' + str(seconds)
    else:
        timecode_seconds_portion = str(seconds)

    return timecode_seconds_portion


def get_seconds_from_timecode(timecode):
    timecode_values = timecode.split(':')
    hours = int(timecode_values[0]) * 3600
    minutes = int(timecode_values[1]) * 60
    seconds = round(float(timecode_values[2]), 1)

    return hours + minutes + seconds


def get_file_size_from_bytes(bytes_value):
    if __has_gigabytes(bytes_value):
        return __get_gigabytes_from_bytes(bytes_value)

    if __has_megabytes(bytes_value):
        return __get_megabytes_from_bytes(bytes_value)

    return __get_kilobytes_from_bytes(bytes_value)


def __has_gigabytes(bytes_value):
    return int(bytes_value / gigabyte_in_bytes) != 0


def __has_megabytes(bytes_value):
    return int(bytes_value / megabyte_in_bytes) != 0


def __get_gigabytes_from_bytes(bytes_value):
    gigabytes = round(bytes_value / gigabyte_in_bytes, 1)

    return str(gigabytes) + 'GB'


def __get_megabytes_from_bytes(bytes_value):
    megabytes = round(bytes_value / megabyte_in_bytes, 1)

    return str(megabytes) + 'MB'


def __get_kilobytes_from_bytes(bytes_value):
    kilobytes = round(bytes_value / kilobyte_in_bytes, 1)

    return str(kilobytes) + 'KB'
