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


import os
import logging


def create_config_directory(application_config_directory, application_config_temp_directory):
    """Creates the application's config directory if it doesn't already exist."""
    __create_new_path(application_config_directory)
    __create_new_path(application_config_temp_directory)


def __create_new_path(path):
    if not os.path.exists(path):
        os.mkdir(path)


def is_directory_empty(directory):
    """Returns if the given directory is empty or not.

    Checks if the directory given exists and is a directory and also checks if that directory is empty.

    :param directory:
        Directory to check.
    """
    if os.path.exists(directory) and not os.path.isfile(directory):
        return not os.listdir(directory)

    return False


def is_directory_accessible(top_directory):
    """Returns if the given directory can be accessed by this application.

    Generates a unique folder in the given directory and tests if it can create and remove that unique directory.

    :param top_directory:
        Directory to check.
    """
    try:
        test_file_path = __generate_unique_folder(top_directory)
        os.mkdir(test_file_path)
        os.rmdir(test_file_path)

        return True
    except OSError:
        logging.warning('--- DIRECTORY IS NOT ACCESSIBLE:' + top_directory + ' ---')

        return False


def __generate_unique_folder(top_directory):
    counter = 0

    original_file_path = top_directory + '/test'
    test_file_path = original_file_path
    while True:
        if os.path.exists(test_file_path):
            test_file_path = original_file_path
            test_file_path += str(counter)

            counter += 1
        else:
            break
    return test_file_path


def get_files_in_directory(directory, recursive=False):
    """Returns a list of all files inside the root of the given directory.

    Recursive parameter allow for a recursive search instead of searching the top directory only.

    :param directory:
        Directory to check.
    :param recursive:
        (Default False) Enable checking directory's contents recursively.
    """
    try:
        files_found, folders_found = __find_files_and_folders_in_directory(directory)

        if recursive:
            files_found.extend(__find_files_in_folders(directory, folders_found))
    except:
        logging.error('--- FAILED TO RETRIEVE FILES IN DIRECTORY:' + directory + ' ---')

        return []
    else:
        return files_found


def __find_files_and_folders_in_directory(directory):
    # Returns a list of files and a list of folders that exist in the given directory.
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


def __find_files_in_folders(top_directory, folders_list):
    # Returns all files inside a list of folders
    files_found = []
    for folder in folders_list:
        folder_path = os.path.join(top_directory, folder)
        files_found.extend(get_files_in_directory(folder_path))
    return files_found


def fix_same_name_occurences(ffmpeg, preferences):
    """Changes the output file name to ensure that an existing file isn't being overwritten.

    Prevents user from setting an output that matches the input.
    Prevents user from overwriting a file that already exists if user defined preferences prevents this.

    :param ffmpeg:
        ffmpeg settings object.
    :param preferences:
        Application's preferences object.
    """
    counter = 0

    file_name = ffmpeg.filename
    output_file_path = ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container
    while True:
        if ffmpeg.input_file == output_file_path:
            output_file_path = __fix_output_file_path(ffmpeg, file_name, counter)
        elif not preferences.overwrite_outputs and os.path.exists(output_file_path):
            output_file_path = __fix_output_file_path(ffmpeg, file_name, counter)
        else:
            break

        counter += 1


def __fix_output_file_path(ffmpeg, file_name, counter):
    # Changes the ffmpeg output file name to include an incremental number to achieve a unique file name.
    ffmpeg.filename = file_name + '_' + str(counter)
    output_file_path = ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container
    return output_file_path
