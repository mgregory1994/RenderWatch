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

import sys
import logging
import os
import faulthandler

from datetime import datetime
from render_watch.startup.app_ui import AppUI
from render_watch.startup.preferences import Preferences
from render_watch.startup.app_requirements import AppRequirements

application_preferences = None
encoder = None
app_ui = None


def __load_preferences():
    global application_preferences

    application_preferences = Preferences()

    Preferences.load_preferences(application_preferences)
    Preferences.create_temp_directory(application_preferences)


def __set_nvenc_max_workers():
    AppRequirements.setup_nvenc_max_workers(application_preferences)


def __setup_encoder():
    from render_watch.encoding.encoder import Encoder
    global encoder

    encoder = Encoder(application_preferences)


def __setup_application():
    global app_ui

    app_ui = AppUI(encoder, application_preferences)


def __start_application():
    __load_preferences()
    __setup_logging()
    __set_nvenc_max_workers()
    __setup_encoder()
    __setup_application()

    app_ui.setup_and_run_application()


def __show_ffmpeg_not_found_message():
    logging.error("""--- FFMPEG NOT FOUND ---
        Install \"ffmpeg\" using your distributions\'s package manager
        or compile ffmpeg and allow it to run by typing \"ffmpeg\" into the terminal.""")


def __show_watchdog_not_found_message():
    logging.error("""--- WATCHDOG NOT FOUND ---
        Install \"watchdog\" using pip.
        Example: \"pip install watchdog\"
        Once \"watchdog\" has been installed, re-run Render Watch.""")


def __setup_logging():
    for arg in sys.argv:
        if arg == '--debug':
            faulthandler.enable()
            __set_debug_logging_type()

            return

    logging.basicConfig(level=logging.ERROR)


def __set_debug_logging_type():
    log_file_name = datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '.log'
    log_file_path = os.path.join(Preferences.default_config_directory, log_file_name)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(filename=log_file_path, level=logging.DEBUG)


def __is_ffmpeg_installed():
    if not AppRequirements.is_ffmpeg_installed():
        __show_ffmpeg_not_found_message()

        return False

    return True


def __is_watchdog_installed():
    try:
        import watchdog
    except ModuleNotFoundError:
        __show_watchdog_not_found_message()

        return False
    else:
        return True


def main(args=None):
    if args is not None:
        sys.argv.extend(args)

    if __is_watchdog_installed() and __is_ffmpeg_installed():
        __start_application()


if __name__ == '__main__':
    main()
