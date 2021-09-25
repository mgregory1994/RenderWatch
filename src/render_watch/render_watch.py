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
    """
    Configures and runs Render Watch.
    """

    @staticmethod
    def setup_and_run():
        """
        Starts the logger, loads application preferences, checks status of NVENC, starts the encoder queue,
        and starts the application's UI.
        """
        LoggingHelper.setup_logging()

        app_preferences = RenderWatch._load_preferences()
        AppRequirements.check_nvidia_requirements(app_preferences)
        encoder_queue = EncoderQueue(app_preferences)

        return RenderWatch._start_ui(encoder_queue, app_preferences)

    @staticmethod
    def _load_preferences():
        # Loads and returns the user preferences.
        app_preferences = Preferences()
        Preferences.load_preferences(app_preferences)
        Preferences.create_temp_directory(app_preferences)
        return app_preferences

    @staticmethod
    def _start_ui(encoder_queue, app_preferences):
        # Starts the application's UI.
        app_ui = AppUI(encoder_queue, app_preferences)
        return app_ui.setup_and_run_application()


def main(args=None):
    """
    Adds any application arguments and runs Render Watch if the startup requirements are met.
    """
    if args:
        sys.argv.extend(args)

    if AppRequirements.check_startup_requirements():
        sys.exit(RenderWatch.setup_and_run())


if __name__ == '__main__':
    main()
