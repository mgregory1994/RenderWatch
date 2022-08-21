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


import os
import logging

from render_watch.ui import Gio


def create_application_config_directory(app_config_directory: str):
    """
    Creates the application's configuration directory if it doesn't already exist.

    Parameters:
        app_config_directory: String that represents the path for the application's configuration directory.
    """
    _create_new_directory(app_config_directory)


def create_application_default_temp_directory(app_temp_directory: str):
    """
    Creates the application's default temp directory if it doesn't already exist.

    Parameters:
        app_temp_directory: String that represents the path for the application's default temp directory.
    """
    _create_new_directory(app_temp_directory)


def _create_new_directory(directory_path: str):
    # Creates the given directory if it doesn't already exist.
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


def is_directory_empty(directory_path: str) -> bool:
    """
    Returns whether the given directory is empty.

    Parameters:
        directory_path: String that represents the path for the given directory.
    """
    if os.path.exists(directory_path) and not os.path.isfile(directory_path):
        return not os.listdir(directory_path)
    return False


def is_directory_accessible(directory_path: str) -> bool:
    """
    Returns whether the given directory is accessible to the application.

    Parameters:
        directory_path: String that represents the path for the given directory.

    Returns:
        Boolean that represents whether the given directory is accessible to the application.
    """
    try:
        test_file_path = _generate_test_folder(directory_path)
        os.mkdir(test_file_path)
        os.rmdir(test_file_path)

        return True
    except OSError:
        logging.warning('--- DIRECTORY IS NOT ACCESSIBLE:' + directory_path + ' ---')

        return False


def _generate_test_folder(directory_path: str) -> str:
    # Creates a unique test folder in the given directory and returns its path.
    counter = 0
    original_file_path = directory_path + '/test'
    test_file_path = original_file_path

    while True:
        if os.path.exists(test_file_path):
            test_file_path = original_file_path
            test_file_path += str(counter)

            counter += 1
        else:
            return test_file_path


def get_files_in_directory(directory_path: str, recursive=False) -> list:
    """
    Returns a list of file paths for each file in the given directory.

    Parameters:
        directory_path: String that represents the path for the given directory.
        recursive: (Default: False) Boolean that represents whether a recursive search is performed.

    Returns:
        List that contains Strings that represent file paths for each file found in the given directory.
    """
    try:
        files_found, folders_found = _get_files_and_folders_in_directory(directory_path)

        if recursive:
            files_found.extend(_get_files_in_folders(directory_path, folders_found))
    except Exception:
        logging.error('--- FAILED TO RETRIEVE FILES IN DIRECTORY:' + directory_path + ' ---')

        return []
    else:
        return files_found


def _get_files_and_folders_in_directory(directory_path: str) -> tuple:
    # Returns a tuple of lists that contain all files and folders found in the given directory.
    if is_directory_empty(directory_path):
        return [], []

    files_in_directory = os.listdir(directory_path)
    folders_found = []
    files_found = []

    for file in files_in_directory:
        file_path = os.path.join(directory_path, file)
        if os.path.isdir(file_path):
            folders_found.append(file)
        else:
            files_found.append(file_path)

    return files_found, folders_found


def _get_files_in_folders(directory_path: str, folders_list: list) -> list:
    # Returns a list of all files found in all the given list of folders.
    files_found = []

    for folder in folders_list:
        folder_path = os.path.join(directory_path, folder)
        files_found.extend(get_files_in_directory(folder_path))

    return files_found


def get_gfiles_from_directory(directory_path: str) -> list:
    """
    Returns a list of Gio.File objects for each file found in the given directory.

    Parameters:
        directory_path: String that represents the path of the given directory.

    Returns:
        List that contains Gio.File objects for each file that was found.
    """
    gfiles = []

    for file in get_files_in_directory(directory_path):
        if not os.path.isdir(file):
            gfiles.append(Gio.File.new_for_path(file))

    return gfiles


def get_unique_file_name(output_file_path: str, output_file_name: str) -> str:
    """
    Returns a file name that doesn't exist in the directory of the given output file path by appending a counter
    at the end of the given file name.

    Parameters:
        output_file_path: String that represents the path of the output file.
        output_file_name: String that represents the name of the output file.

    Returns:
        String that represents a unique version of the given output file name that doesn't exist in the directory
        of the given output file path.
    """
    counter = 0

    while True:
        if _is_output_file_path_exist(output_file_path):
            output_file_name = ''.join([output_file_name, '_', str(counter)])
        else:
            break

        counter += 1

    return output_file_name


def _is_output_file_path_exist(output_file_path: str) -> bool:
    # Returns whether the given output file path already exists.
    return os.path.exists(output_file_path)
