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


import sys

from render_watch.startup.app_ui import AppUI
from render_watch.startup.preferences import Preferences
from render_watch.startup.app_requirements import AppRequirements
from render_watch.encoding.encoder_queue import EncoderQueue
from render_watch.helpers.logging_helper import LoggingHelper


class RenderWatch:
    """Sets up and starts Render Watch"""

    def __init__(self):
        LoggingHelper.setup_logging()
        self.app_prefs = self._load_preferences()
        AppRequirements.check_nvidia_requirements(self.app_prefs)
        self.encoder_queue = EncoderQueue(self.app_prefs)
        self._start_app()

    @staticmethod
    def _load_preferences():
        # Loads and returns the user preferences.
        prefs = Preferences()
        Preferences.load_preferences(prefs)
        Preferences.create_temp_directory(prefs)
        return prefs

    def _start_app(self):
        # Starts the application's UI.
        self.app_ui = AppUI(self.encoder_queue, self.app_prefs)
        self.app_ui.setup_and_run_application()


def main(args=None):
    """Adds any arguments and starts the application.

    The application's minimum startup requirements are checked before starting the application.

    :param args:
        Application arguments.
    """
    if args:
        sys.argv.extend(args)

    #if AppRequirements.check_startup_requirements():
    RenderWatch()


if __name__ == '__main__':
    main()
