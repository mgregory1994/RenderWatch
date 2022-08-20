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


import logging
import faulthandler
import sys
import os

from datetime import datetime


def setup_logging(application_config_directory: str):
    """
    Sets the file path and logging level for the logger.

    Parameters:
        application_config_directory: String that represents the application's configuration directory.
    """
    logging.basicConfig(filename=_get_logging_file_path(application_config_directory), level=_get_logging_type())


def _get_logging_file_path(application_config_directory: str) -> str:
    # Returns the logger's file path using the date and time.
    logging_file_name = datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.log'
    logging_file_path = os.path.join(application_config_directory, logging_file_name)

    return logging_file_path


def _get_logging_type() -> int:
    # Returns the logging level type depending on whether the debug arg was passed into the application.
    logging_type = logging.ERROR

    for arg in sys.argv:
        if arg == '--debug':
            faulthandler.enable()

            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            logging_type = logging.DEBUG

            break

    return logging_type
