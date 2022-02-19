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

from render_watch.startup.application_ui import ApplicationUI
from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.startup.application_requirements import ApplicationRequirements
from render_watch.encoding.encoder_queue import EncoderQueue
from render_watch.helpers.logging_helper import LoggingHelper


class RenderWatch:
    """
    Configures and runs Render Watch.
    """

    @staticmethod
    def setup_and_run():
        """
        Starts the logger, loads application preferences, checks requirements for NVENC, starts the encoder queue,
        and starts the application's UI.
        """
        LoggingHelper.setup_logging()

        application_preferences = RenderWatch._load_preferences()
        ApplicationRequirements.check_nvidia_requirements(application_preferences)
        encoder_queue = EncoderQueue(application_preferences)

        return RenderWatch._run_ui(encoder_queue, application_preferences)

    @staticmethod
    def _load_preferences():
        application_preferences = ApplicationPreferences()
        ApplicationPreferences.load_preferences(application_preferences)
        ApplicationPreferences.create_temp_directory(application_preferences)
        return application_preferences

    @staticmethod
    def _run_ui(encoder_queue, application_preferences):
        application_ui = ApplicationUI(encoder_queue, application_preferences)
        return application_ui.setup_and_run()


def main(args=None):
    """
    Adds any application arguments and runs Render Watch if the startup requirements are met.
    """
    if args:
        sys.argv.extend(args)

    if ApplicationRequirements.check_startup_requirements():
        sys.exit(RenderWatch.setup_and_run())


if __name__ == '__main__':
    main()
