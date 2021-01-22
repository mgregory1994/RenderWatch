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

import os
import logging


def create_config_directory():
    home_directory = os.getenv('HOME')
    application_config_directory = os.path.join(home_directory, '.config', 'Render Watch')
    application_config_temp_directory = os.path.join(application_config_directory, 'temp')

    __create_new_path(application_config_directory)
    __create_new_path(application_config_temp_directory)


def __create_new_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def is_directory_empty(directory):
    if os.path.exists(directory) and not os.path.isfile(directory):

        if not os.listdir(directory):
            return True
    else:
        return False


def is_directory_accessible(directory):
    try:
        test_directory = directory + '/test'
        os.mkdir(test_directory)
        os.rmdir(test_directory)

        return True
    except OSError:
        logging.warning('--- DIRECTORY IS NOT ACCESSIBLE:' + directory + ' ---')

        return False


def get_files_in_directory(directory, recursive=False):
    try:
        files_found, folders_found = __get_files_and_folders_in_directory(directory)

        if recursive:
            files_found.extend(__get_files_from_folders(directory, folders_found))
    except:
        logging.error('--- FAILED TO RETRIEVE FILES IN DIRECTORY:' + directory + ' ---')

        return []
    else:
        return files_found


def __get_files_and_folders_in_directory(directory):
    if is_directory_empty(directory):
        return [], []

    files_in_directory = os.listdir(directory)
    folders_found = []
    files_found = []

    for file in files_in_directory:
        file_path = os.path.join(directory, file)

        if os.path.isdir(file_path):
            folders_found.append(file)
        else:
            files_found.append(file_path)

    return files_found, folders_found


def __get_files_from_folders(folders_directory, folders):
    files_found = []

    for folder in folders:
        folder_directory = os.path.join(folders_directory, folder)

        files_found.extend(get_files_in_directory(folder_directory))

    return files_found


def fix_same_name_occurences(ffmpeg, preferences):
    file_name = ffmpeg.filename
    output_file_path = ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container
    counter = 0

    while True:
        if ffmpeg.input_file == output_file_path:
            output_file_path = __fix_output_file_path(ffmpeg, file_name, counter)
        elif not preferences.overwrite_outputs and os.path.exists(output_file_path):
            output_file_path = __fix_output_file_path(ffmpeg, file_name, counter)
        else:
            break

        counter += 1


def __fix_output_file_path(ffmpeg, file_name, counter):
    ffmpeg.filename = file_name + '_' + str(counter)
    output_file_path = ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container

    return output_file_path
