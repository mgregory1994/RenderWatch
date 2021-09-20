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


import subprocess

from render_watch.ffmpeg.settings import Settings
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.helpers.logging_helper import LoggingHelper


class AppRequirements:
    """Allows for checking all requirements needed for running Render Watch.

    This includes dependencies for ffmpeg and the watchdog module.
    This also includes checking for Nvidia's NVENC functionality and whether or not it's accessible on this machine.
    """

    @staticmethod
    def check_startup_requirements():
        """Check and return if both ffmpeg and the watchdog module is installed and accessible."""
        return AppRequirements.is_ffmpeg_installed() and AppRequirements.is_watchdog_installed()

    @staticmethod
    def is_ffmpeg_installed():
        """Checks if ffmpeg is installed and accessible. If not, then show a message to the user on what to do next."""
        try:
            return AppRequirements.__run_test_process(AppRequirements.__get_new_ffmpeg_test_args())
        except:
            LoggingHelper.show_ffmpeg_not_found_message()
            return False

    @staticmethod
    def __get_new_ffmpeg_test_args():
        # Setup a test ffmpeg settings object using a null source.
        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-f')
        ffmpeg_args.append('lavfi')
        ffmpeg_args.append('-i')
        ffmpeg_args.append('nullsrc=s=256x256:d=5')
        ffmpeg_args.append('-c:v')
        ffmpeg_args.append('libx264')
        ffmpeg_args.append('-f')
        ffmpeg_args.append('null')
        ffmpeg_args.append('-')
        return ffmpeg_args

    @staticmethod
    def __run_test_process(ffmpeg_args):
        # Creates and runs a process using the given ffmpeg arguments and checks if the process exits without errors.
        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True) as process:
            return process.wait() == 0

    @staticmethod
    def is_watchdog_installed():
        """Checks if the watchdog module is installed and accessible.

        If the module isn't installed or accessible, then show a message telling the user what to do next.
        """
        try:
            import watchdog
        except ModuleNotFoundError:
            LoggingHelper.show_watchdog_not_found_message()
            return False
        return True

    @staticmethod
    def check_nvidia_requirements(preferences):
        """Runs any functions needed to check if the system supports Nvidia's NVENC encoder.

        This functions will check if NVENC works and, if so, how many NVENC process can be ran in parallel.

        :param preferences:
            Application's preferences object.
        """
        NvidiaHelper.setup_nvenc_max_workers(preferences)
