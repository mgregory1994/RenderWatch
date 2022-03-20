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


GIGABYTE_IN_BYTES = 1073741824
MEGABYTE_IN_BYTES = 1048576
KILOBYTE_IN_BYTES = 1024


def get_timecode_from_seconds(seconds: int) -> str:
    """
    Creates and returns a time code string using the number of seconds.

    Time code format: HH:MM:SS.

    :param seconds: Number of seconds.
    """
    hours = int(seconds / 3600)
    seconds_left = seconds % 3600
    minutes = int(seconds_left / 60)
    seconds_left = round(seconds_left % 60, 1)

    return _generate_timecode(hours, minutes, seconds_left)


def _generate_timecode(hours: int, minutes: int, seconds: int) -> str:
    return ':'.join([_generate_hours_timecode_portion(hours),
                    _generate_minutes_timecode_portion(minutes),
                    _generate_seconds_timecode_portion(seconds)])


def _generate_hours_timecode_portion(hours: int) -> str:
    if hours == 0:
        timecode_hours_portion = '00'
    elif hours < 10:
        timecode_hours_portion = '0' + str(hours)
    else:
        timecode_hours_portion = str(hours)

    return timecode_hours_portion


def _generate_minutes_timecode_portion(minutes: int) -> str:
    if minutes == 0:
        timecode_minutes_portion = '00'
    elif minutes < 10:
        timecode_minutes_portion = '0' + str(minutes)
    else:
        timecode_minutes_portion = str(minutes)

    return timecode_minutes_portion


def _generate_seconds_timecode_portion(seconds: int) -> str:
    if seconds == 0:
        timecode_seconds_portion = '00'
    elif seconds < 10:
        timecode_seconds_portion = '0' + str(seconds)
    else:
        timecode_seconds_portion = str(seconds)

    return timecode_seconds_portion


def get_seconds_from_timecode(timecode: str) -> float:
    """
    Returns the total seconds that makes up the given timecode.

    :param timecode: Timecode string formatted as: HH:MM:SS.
    """
    timecode_values = timecode.split(':')
    hours = int(timecode_values[0]) * 3600
    minutes = int(timecode_values[1]) * 60
    seconds = round(float(timecode_values[2]), 1)

    return hours + minutes + seconds


def get_file_size_from_bytes(bytes_value: int) -> str:
    """
    Converts the given bytes value into a file size string.
    Depending on the bytes value, this will return a string with file sizes as large as GBs and as low as KBs.

    :param bytes_value: Amount of bytes.
    """
    if _is_gigabytes(bytes_value):
        return _get_gigabytes_from_bytes(bytes_value)
    if _is_megabytes(bytes_value):
        return _get_megabytes_from_bytes(bytes_value)
    return _get_kilobytes_from_bytes(bytes_value)


def _is_gigabytes(bytes_value: int) -> bool:
    return int(bytes_value / GIGABYTE_IN_BYTES) != 0


def _is_megabytes(bytes_value: int) -> bool:
    return int(bytes_value / MEGABYTE_IN_BYTES) != 0


def _get_gigabytes_from_bytes(bytes_value: int) -> str:
    gigabytes = round(bytes_value / GIGABYTE_IN_BYTES, 1)

    return str(gigabytes) + 'GB'


def _get_megabytes_from_bytes(bytes_value: int) -> str:
    megabytes = round(bytes_value / MEGABYTE_IN_BYTES, 1)

    return str(megabytes) + 'MB'


def _get_kilobytes_from_bytes(bytes_value: int) -> str:
    kilobytes = round(bytes_value / KILOBYTE_IN_BYTES, 1)

    return str(kilobytes) + 'KB'


def get_bytes_from_kilobytes(kilobytes: int) -> int:
    """
    Converts kilobytes to bytes.
    """
    return kilobytes * KILOBYTE_IN_BYTES
