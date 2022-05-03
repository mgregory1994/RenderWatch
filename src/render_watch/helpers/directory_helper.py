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


def create_application_config_directory(app_config_directory: str, app_temp_directory: str):
    _create_new_directory(app_config_directory)
    _create_new_directory(app_temp_directory)


def _create_new_directory(directory_path: str):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)


def is_directory_empty(directory_path: str) -> bool:
    if os.path.exists(directory_path) and not os.path.isfile(directory_path):
        return not os.listdir(directory_path)
    return False


def is_directory_accessible(directory_path: str) -> bool:
    try:
        test_file_path = _generate_test_folder(directory_path)
        os.mkdir(test_file_path)
        os.rmdir(test_file_path)

        return True
    except OSError:
        logging.warning('--- DIRECTORY IS NOT ACCESSIBLE:' + directory_path + ' ---')

        return False


def _generate_test_folder(directory_path: str) -> str:
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
    files_found = []

    for folder in folders_list:
        folder_path = os.path.join(directory_path, folder)
        files_found.extend(get_files_in_directory(folder_path))

    return files_found


def get_unique_file_name(output_file_path: str, output_file_name: str) -> str:
    counter = 0

    while True:
        if _output_file_path_exists(output_file_path):
            output_file_name = ''.join([output_file_name, '_', str(counter)])
        else:
            break

        counter += 1

    return output_file_name


def _output_file_path_exists(output_file_path: str) -> bool:
    return os.path.exists(output_file_path)
