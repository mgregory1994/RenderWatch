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


import subprocess
import logging

from concurrent.futures import ThreadPoolExecutor


class NvidiaHelper:
    nvenc_supported = None
    nvdec_supported = None
    npp_supported = None
    nvenc_max_workers = 1

    @staticmethod
    def is_nvenc_supported():
        if NvidiaHelper.nvenc_supported is not None:
            return NvidiaHelper.nvenc_supported

        NvidiaHelper.nvenc_supported = NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_ffmpeg_nvenc_test_args())

        return NvidiaHelper.nvenc_supported

    @staticmethod
    def __run_test_process(ffmpeg_args):
        with subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            return process.wait() == 0

    @staticmethod
    def __get_new_ffmpeg_nvenc_test_args():
        from render_watch.ffmpeg.settings import Settings

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
    def is_nvdec_supported():
        if NvidiaHelper.nvdec_supported is not None:
            return NvidiaHelper.nvdec_supported

        NvidiaHelper.nvdec_supported = NvidiaHelper.__run_nvdec_check_process()

        return NvidiaHelper.nvdec_supported

    @staticmethod
    def __run_nvdec_check_process():
        nvdec_found = False

        with subprocess.Popen(NvidiaHelper.__get_new_ffmpeg_nvdec_test_args(), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            while True:
                output = process.stdout.readline().strip().decode()

                if not output or output == '':
                    break

                if 'cuvid' in output:
                    nvdec_found = True

        return nvdec_found

    @staticmethod
    def __get_new_ffmpeg_nvdec_test_args():
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.ffmpeg_init_args.copy()

        ffmpeg_args.append('-decoders')

        return ffmpeg_args

    @staticmethod
    def is_npp_supported():
        if NvidiaHelper.npp_supported is not None:
            return NvidiaHelper.npp_supported

        NvidiaHelper.npp_supported = NvidiaHelper.__run_npp_check_process()

        return NvidiaHelper.npp_supported

    @staticmethod
    def __run_npp_check_process():
        npp_found = False

        with subprocess.Popen(NvidiaHelper.__get_new_ffmpeg_npp_test_args(), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            while True:
                output = process.stdout.readline().strip().decode()

                if not output or output == '':
                    break

                if 'npp' in output:
                    npp_found = True

        return npp_found

    @staticmethod
    def __get_new_ffmpeg_npp_test_args():
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.ffmpeg_init_args.copy()

        ffmpeg_args.append('-filters')

        return ffmpeg_args

    @staticmethod
    def setup_nvenc_max_workers(preferences):
        if preferences.concurrent_nvenc_value != 0:
            NvidiaHelper.nvenc_max_workers = preferences.concurrent_nvenc_value

            logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(preferences.concurrent_nvenc_value))
        else:
            NvidiaHelper.__test_nvenc_max_workers()

    @staticmethod
    def __test_nvenc_max_workers():
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(NvidiaHelper.__run_nvenc_test_process, range(counter))

                if counter > 16 or NvidiaHelper.__has_future_executor_results_failed(results):
                    NvidiaHelper.nvenc_max_workers = counter - 1

                    logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(counter - 1))

                    break

            counter = counter + 1

    @staticmethod
    def __run_nvenc_test_process(counter_id=None):  # Parameter necessary for __test_nvenc_max_workers() function
        return NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_ffmpeg_nvenc_test_args())

    @staticmethod
    def __has_future_executor_results_failed(results):
        for result in results:
            if not result:
                return True

        return False

    @staticmethod
    def is_nvenc_available():
        is_nvenc_available = NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_ffmpeg_nvenc_test_args())

        return is_nvenc_available
