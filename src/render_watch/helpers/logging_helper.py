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

from render_watch.startup.preferences import Preferences


class _Decorators:
    """Decorator functions for the logging_helper module."""

    @staticmethod
    def setup_logging_type(setup_logging_func):
        """Decorator method that configures the logging type.

        :param setup_logging_func:
            Logging function to be decorated.
        """
        def apply_logging_type():
            """Checks for the debug application argument and configures the logging type."""
            logging_type = logging.ERROR
            for arg in sys.argv:
                if arg == '--debug':
                    faulthandler.enable()

                    # remove default handler so our new one takes effect globally.
                    for handler in logging.root.handlers[:]:
                        logging.root.removeHandler(handler)
                    logging_type = logging.DEBUG
                    logging_file_name = datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '.log'
                    logging_file_path = os.path.join(Preferences.default_config_directory, logging_file_name)
                    return setup_logging_func(logging_type, logging_file_path)
            return setup_logging_func(logging_type)

        return apply_logging_type


class LoggingHelper:
    """Manages application logging setup."""

    @staticmethod
    @_Decorators.setup_logging_type
    def setup_logging(logging_type=None, logging_file_path=None):
        """Configures the logging module.

        :param logging_type:
            The type of logging to use.
        :param logging_file_path:
            File path to store application logs.
        """
        logging.basicConfig(filename=logging_file_path, level=logging_type)

    @staticmethod
    def show_ffmpeg_not_found_message():
        """Logs a message that tells the user that ffmpeg couldn't be found.

        We need ffmpeg to be runnable by typing "ffmpeg" into the terminal.
        This message tells the user to install/compile ffmpeg and make sure you can run it this way.
        """
        logging.error(
            """--- FFMPEG NOT FOUND ---
            Install "ffmpeg" using your distributions's package manager
            or compile ffmpeg and allow it to run by typing "ffmpeg" into the terminal.""")

    @staticmethod
    def show_watchdog_not_found_message():
        """Logs a message that tells the user that watchdog couldn't be found.

        Watchdog is used for the watch folder functionality of this application.
        This 3rd-party module is not included with Render Watch, but it is listed as a dependency.
        This message tells the user that they need to install the watchdog module in order to use Render Watch.
        """
        logging.error(
            """--- WATCHDOG NOT FOUND ---
            Install "watchdog" using pip.
            Example: "pip install watchdog"
            Once "watchdog" has been installed, re-run Render Watch.""")
