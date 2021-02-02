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
from ffmpeg.settings import Settings


class AppRequirements:
    nvenc_max_workers = 1
    nvenc_supported = None

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
    def __get_new_ffmpeg_nvenc_test_args():
        ffmpeg_args = Settings.ffmpeg_init_args.copy()

        ffmpeg_args.append('-f')
        ffmpeg_args.append('lavfi')
        ffmpeg_args.append('-i')
        ffmpeg_args.append('nullsrc=s=256x256:d=10')
        ffmpeg_args.append('-c:v')
        ffmpeg_args.append('h264_nvenc')
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
    def is_nvenc_available():
        is_nvenc_available = AppRequirements.__run_test_process(AppRequirements.__get_new_ffmpeg_nvenc_test_args())

        return is_nvenc_available

    @staticmethod
    def is_nvenc_supported():
        if AppRequirements.nvenc_supported is not None:
            return AppRequirements.nvenc_supported

        AppRequirements.nvenc_supported = AppRequirements.__run_test_process(AppRequirements.__get_new_ffmpeg_nvenc_test_args())

        return AppRequirements.nvenc_supported

    @staticmethod
    def setup_nvenc_max_workers(preferences):
        if preferences.concurrent_nvenc_value != 0:
            AppRequirements.nvenc_max_workers = preferences.concurrent_nvenc_value

            logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(preferences.concurrent_nvenc_value))
        else:
            AppRequirements.__test_nvenc_max_workers()

    @staticmethod
    def __test_nvenc_max_workers():
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(AppRequirements.__run_nvenc_test_process, range(counter))

                if counter > 16 or AppRequirements.__has_future_executor_results_failed(results):
                    AppRequirements.nvenc_max_workers = counter - 1

                    logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(counter - 1))

                    break

            counter = counter + 1

    @staticmethod
    def __has_future_executor_results_failed(results):
        for result in results:
            if not result:
                return True

        return False

    @staticmethod
    def __run_test_process(ffmpeg_args):
        with subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            return process.wait() == 0

    @staticmethod
    def __run_nvenc_test_process(counter_id=None):  # Parameter necessary for __test_nvenc_max_workers() function
        return AppRequirements.__run_test_process(AppRequirements.__get_new_ffmpeg_nvenc_test_args())
