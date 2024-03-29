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


import logging
import os
import sys
import faulthandler

from datetime import datetime

from render_watch.startup.application_preferences import ApplicationPreferences


class _Decorators:
    """
    Decorator function for the logging_helper module.
    """

    @staticmethod
    def setup_logging_type(setup_logging_func):
        """
        Decorator method that configures the logging type.

        :param setup_logging_func: Logging function to be decorated.
        """
        def apply_logging_type():
            """
            Checks for the debug application argument and configures the logging type.
            """
            logging_type = logging.ERROR

            for arg in sys.argv:
                if arg == '--debug':
                    faulthandler.enable()

                    for handler in logging.root.handlers[:]:
                        logging.root.removeHandler(handler)

                    logging_type = logging.DEBUG
                    logging_file_name = datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.log'
                    logging_file_path = os.path.join(ApplicationPreferences.DEFAULT_APPLICATION_DATA_DIRECTORY,
                                                     logging_file_name)
                    return setup_logging_func(logging_type, logging_file_path)
            return setup_logging_func(logging_type)

        return apply_logging_type


class LoggingHelper:
    """
    Manages application's logging setup.
    """

    @staticmethod
    @_Decorators.setup_logging_type
    def setup_logging(logging_type=None, logging_file_path=None):
        """
        Configures the logging module.

        :param logging_type: The type of logging to use.
        :param logging_file_path: File path to store application logs.
        """
        logging.basicConfig(filename=logging_file_path, level=logging_type)

    @staticmethod
    def show_ffmpeg_not_found_message():
        """
        Logs a message that tells the user that ffmpeg couldn't be found.
        """
        logging.error(
            """--- FFMPEG NOT FOUND ---
            Install "ffmpeg" using your distribution's package manager
            or compile ffmpeg and allow it to run by typing "ffmpeg" into the terminal."""
        )

    @staticmethod
    def show_watchdog_not_found_message():
        """
        Logs a message that tells the user that watchdog couldn't be found.
        """
        logging.error(
            """--- WATCHDOG NOT FOUND ---
            Install "watchdog" using pip.
            Example: "pip install watchdog"
            Once "watchdog" has been installed, re-run Render Watch."""
        )

    @staticmethod
    def log_encoder_error(ffmpeg, message):
        """
        Logs an error for failed encode tasks and includes ffmpeg arguments for debugging.
        The output_args can be copied straight into a terminal in order to investigate why the encode failed.

        :param ffmpeg: ffmpeg settings object used for the encode task.
        :param message: Message to display prepending the output_args.
        """
        ffmpeg_args = ffmpeg.get_args()
        output_args = ''

        for index, arg in enumerate(ffmpeg_args):
            output_args += arg
            if index != len(ffmpeg_args) - 1:
                output_args += ' '

        logging.error(message + '\n' + output_args)
