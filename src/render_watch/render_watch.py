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
from render_watch.encode import encoder_queue, preview, benchmark
from render_watch.helpers import nvidia_helper


def main(args=None):
    """Main function that starts the application."""
    if args:
        sys.argv.extend(args)

    _start_render_watch()


def _start_render_watch():
    # Creates application settings, configures NVENC and the logger, and starts the application.
    app_settings = _get_application_settings()

    _setup_nvenc_compatibility(app_settings)
    logger.setup_logging(app_preferences.APPLICATION_CONFIG_DIRECTORY)

    task_queue = encoder_queue.TaskQueue(app_settings)
    preview_generator = preview.PreviewGenerator(app_settings)
    benchmark_generator = benchmark.BenchmarkGenerator(app_settings)

    app = application.RenderWatch(app_settings, task_queue, preview_generator, benchmark_generator)
    sys.exit(app.run(sys.argv))


def _get_application_settings() -> app_preferences.Settings:
    # Creates, configures, and returns the application's settings.
    app_settings = app_preferences.Settings()
    app_preferences.create_config_directory()
    app_preferences.create_temp_directory(app_settings)

    return app_settings


def _setup_nvenc_compatibility(app_settings: app_preferences.Settings):
    # Checks for Nvenc compatibility and configures Nvenc if applicable.
    if nvidia_helper.Compatibility.is_nvenc_supported():
        nvidia_helper.Parallel.setup_nvenc_max_workers(app_settings)
