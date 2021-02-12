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

import logging
import subprocess

from concurrent.futures import ThreadPoolExecutor
from render_watch.ffmpeg.settings import Settings


class AppRequirements:
    @staticmethod
    def __get_new_ffmpeg_test_args():
        ffmpeg_args = Settings.ffmpeg_init_args.copy()

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
    def is_ffmpeg_installed():
        try:
            return AppRequirements.__run_test_process(AppRequirements.__get_new_ffmpeg_test_args())
        except:
            return False

    @staticmethod
    def __run_test_process(ffmpeg_args):
        with subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            return process.wait() == 0
