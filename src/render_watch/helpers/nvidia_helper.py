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


import logging
import subprocess
import time

from concurrent.futures import ThreadPoolExecutor

from render_watch.helpers import ffmpeg_helper


NVDEC_ARGS = ('-hwaccel', 'nvdec')
NVDEC_OUT_FORMAT_ARGS = ('-hwaccel_output_format', 'cuda')

MAX_NVENC_WORKERS = 16


class Compatibility:
    _nvenc_supported = None
    _nvdec_supported = None
    _npp_supported = None

    @staticmethod
    def is_nvenc_supported() -> bool:
        if Compatibility._nvenc_supported is None:
            Compatibility._nvenc_supported = Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

        return Compatibility._nvenc_supported

    @staticmethod
    def run_test_process(test_process_args: list, counter=None) -> bool:  # Unused parameter necessary for this function
        with subprocess.Popen(test_process_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as test_process:
            return test_process.wait() == 0

    @staticmethod
    def get_nvenc_test_args() -> list:
        nvenc_test_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        nvenc_test_args.append('-f')
        nvenc_test_args.append('lavfi')
        nvenc_test_args.append('-i')
        nvenc_test_args.append('nullsrc=s=256x256:d=5')
        nvenc_test_args.append('-c:v')
        nvenc_test_args.append('h264_nvenc')
        nvenc_test_args.append('-f')
        nvenc_test_args.append('null')
        nvenc_test_args.append('-')

        return nvenc_test_args

    @staticmethod
    def is_nvdec_supported() -> bool:
        if Compatibility._nvdec_supported is None:
            Compatibility._nvdec_supported = Compatibility._run_nvdec_test_process()

        return Compatibility._nvdec_supported

    @staticmethod
    def _run_nvdec_test_process() -> bool:
        is_nvdec_found = False

        with subprocess.Popen(Compatibility._get_list_decoders_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as nvdec_test_process:
            while True:
                stdout = nvdec_test_process.stdout.readline().strip()

                if stdout == '' and nvdec_test_process.poll() is not None:
                    break

                if 'cuvid' in stdout:
                    is_nvdec_found = True

                    break

        return is_nvdec_found

    @staticmethod
    def _get_list_decoders_args() -> list:
        list_decoders_process_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        list_decoders_process_args.append('-decoders')

        return list_decoders_process_args

    @staticmethod
    def is_npp_supported() -> bool:
        if Compatibility._npp_supported is None:
            Compatibility._npp_supported = Compatibility._run_npp_test_process()

        return Compatibility._npp_supported

    @staticmethod
    def _run_npp_test_process() -> bool:
        is_npp_found = False

        with subprocess.Popen(Compatibility._get_npp_test_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as npp_test_process:
            while True:
                stdout = npp_test_process.stdout.readline().strip()

                if stdout == '' and npp_test_process.poll() is not None:
                    break

                if 'npp' in stdout:
                    is_npp_found = True

                    break

        return is_npp_found

    @staticmethod
    def _get_npp_test_args() -> list:
        npp_test_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        npp_test_args.append('-filters')

        return npp_test_args

    @staticmethod
    def is_nvenc_available() -> bool:
        return Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

    @staticmethod
    def wait_until_nvenc_available():
        while True:
            if Compatibility.is_nvenc_available():
                break
            else:
                time.sleep(3)


class Parallel:
    nvenc_max_workers = 1

    @staticmethod
    def setup_nvenc_max_workers(app_preferences):
        if app_preferences.get_parallel_nvenc_value():
            Parallel.nvenc_max_workers = app_preferences.get_parallel_nvenc_value()

            logging.info(''.join(['--- NVENC MAX WORKERS SET TO: ',
                                  str(app_preferences.get_parallel_nvenc_value),
                                  ' ---']))
        else:
            Parallel._test_nvenc_max_workers()

    @staticmethod
    def _test_nvenc_max_workers():
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(Compatibility.run_test_process,
                                              Compatibility.get_nvenc_test_args(),
                                              range(counter))

                if counter > MAX_NVENC_WORKERS or Parallel._has_future_executor_results_failed(results):
                    Parallel.nvenc_max_workers = counter - 1

                    logging.info(''.join(['--- NVENC MAX WORKERS SET TO: ',
                                          str(counter - 1),
                                          ' ---']))

                    break

            counter += 1

    @staticmethod
    def _has_future_executor_results_failed(results) -> bool:
        for result in results:
            if not result:
                return True
        return False
