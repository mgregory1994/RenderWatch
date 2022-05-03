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


import sys

from render_watch import logger
from render_watch import app_preferences
from render_watch.ui import application


def main(args=None):
    if args:
        sys.argv.extend(args)

    _start_render_watch()


def _start_render_watch():
    app_settings = app_preferences.Settings()
    app_preferences.create_config_directory()

    logger.setup_logging(app_preferences.APPLICATION_CONFIG_DIRECTORY)

    sys.exit(application.Application(app_settings).start_application())
