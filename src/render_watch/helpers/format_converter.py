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

SECONDS_IN_HOUR = 3600.0
SECONDS_IN_MINUTE = 60.0


def get_timecode_from_seconds(seconds: float | int) -> str:
    """
    Creates and returns string that represents a timecode using the given number of seconds.

    Time code format: HH:MM:SS

    Parameters:
         seconds: Integer that represents the given number of seconds.

    Returns:
        String that represents a timecode using the given number of seconds.
    """
    hours = int(seconds / SECONDS_IN_HOUR)
    seconds_left = seconds % SECONDS_IN_HOUR
    minutes = int(seconds_left / SECONDS_IN_MINUTE)
    seconds_left = round(seconds_left % SECONDS_IN_MINUTE, 1)

    return _generate_timecode(hours, minutes, seconds_left)


def _generate_timecode(hours: int, minutes: int, seconds: float | int) -> str:
    # Returns a String formatted as a timecode for the given hours, minutes, and seconds.
    return ':'.join([_generate_hours_timecode_portion(hours),
                    _generate_minutes_timecode_portion(minutes),
                    _generate_seconds_timecode_portion(seconds)])


def _generate_hours_timecode_portion(hours: int) -> str:
    # Returns a String that represents the hours portion of a timecode.
    if hours == 0:
        timecode_hours_portion = '00'
    elif hours < 10:
        timecode_hours_portion = '0' + str(hours)
    else:
        timecode_hours_portion = str(hours)

    return timecode_hours_portion


def _generate_minutes_timecode_portion(minutes: int) -> str:
    # Returns a String that represents the minutes portion of a timecode.
    if minutes == 0:
        timecode_minutes_portion = '00'
    elif minutes < 10:
        timecode_minutes_portion = '0' + str(minutes)
    else:
        timecode_minutes_portion = str(minutes)

    return timecode_minutes_portion


def _generate_seconds_timecode_portion(seconds: float | int) -> str:
    # Returns a String that represents the seconds portion of a timecode.
    if seconds == 0:
        timecode_seconds_portion = '00'
    elif seconds < 10:
        timecode_seconds_portion = '0' + str(seconds)
    else:
        timecode_seconds_portion = str(seconds)

    return timecode_seconds_portion


def get_seconds_from_timecode(timecode: str) -> float:
    """
    Returns the total number of seconds that makes up the given timecode.

    Parameters:
         timecode: String that represents a timecode formatted as: HH:MM:SS .

     Returns:
         Float that represents the total number of seconds that makes up the given timecode.
    """
    timecode_values = timecode.split(':')
    hours = int(timecode_values[0]) * SECONDS_IN_HOUR
    minutes = int(timecode_values[1]) * SECONDS_IN_MINUTE
    seconds = round(float(timecode_values[2]), 1)

    return hours + minutes + seconds


def get_file_size_from_bytes(bytes_value: int) -> str:
    """
    Uses the given number of bytes and returns a String that represents the file size.

    Depending on the bytes value, this will return a String that represents a file size as large as GBs
    and as low as KBs.

    Parameters:
        bytes_value: Integer that represents the number of bytes.

    Returns:
        String that represents the file size using the given number of bytes.
    """
    if _is_gigabytes(bytes_value):
        return _get_gigabytes_from_bytes(bytes_value)
    if _is_megabytes(bytes_value):
        return _get_megabytes_from_bytes(bytes_value)
    return _get_kilobytes_from_bytes(bytes_value)


def _is_gigabytes(bytes_value: int) -> bool:
    # Returns whether the given number of bytes is large enough to represent a file size in Gigabytes.
    return int(bytes_value / GIGABYTE_IN_BYTES) != 0


def _is_megabytes(bytes_value: int) -> bool:
    # Returns whether the given number of bytes is large enough to represent a file size in Megabytes.
    return int(bytes_value / MEGABYTE_IN_BYTES) != 0


def _get_gigabytes_from_bytes(bytes_value: int) -> str:
    # Returns a String that represents a file size in Gigabytes using the given number of bytes.
    gigabytes = round(bytes_value / GIGABYTE_IN_BYTES, 1)

    return str(gigabytes) + 'GB'


def _get_megabytes_from_bytes(bytes_value: int) -> str:
    # Returns a String that represents a file size in Megabytes using the given number of bytes.
    megabytes = round(bytes_value / MEGABYTE_IN_BYTES, 1)

    return str(megabytes) + 'MB'


def _get_kilobytes_from_bytes(bytes_value: int) -> str:
    # Returns a String that represents a file size in Kilobytes using the given number of bytes.
    kilobytes = round(bytes_value / KILOBYTE_IN_BYTES, 1)

    return str(kilobytes) + 'KB'


def get_bytes_from_kilobytes(kilobytes: int) -> int:
    """
    Returns an Integer that represents the number of bytes that makes up the given number of Kilobytes.

    Parameters:
        kilobytes: Integer that represents the number of Kilobytes.

    Returns:
        Integer that represents the number of bytes that makes up the given number of Kilobytes.
    """
    return kilobytes * KILOBYTE_IN_BYTES
