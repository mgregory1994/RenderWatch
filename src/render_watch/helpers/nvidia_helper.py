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

from itertools import repeat
from concurrent.futures import ThreadPoolExecutor

from render_watch import app_preferences
from render_watch.ffmpeg import encoding
from render_watch.helpers import ffmpeg_helper


NVDEC_ARGS = ('-hwaccel', 'nvdec')
NVDEC_OUT_FORMAT_ARGS = ('-hwaccel_output_format', 'cuda')

MAX_NVENC_WORKERS = 16


class Compatibility:
    """Class that checks for Nvenc and Nvdec compatibility with the system that's running the application."""
    _nvenc_supported = None
    _nvdec_supported = None
    _npp_supported = None

    @staticmethod
    def is_nvenc_supported() -> bool:
        """
        Returns whether Nvenc is supported on the system that's running the application.

        Returns:
            Boolean that represents whether Nvenc is supported.
        """
        if Compatibility._nvenc_supported is None:
            Compatibility._nvenc_supported = Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

            if Compatibility._nvenc_supported:
                encoding.Task.VIDEO_CODECS_MP4_UI.extend(['NVENC H264', 'NVENC H265'])
                encoding.Task.VIDEO_CODECS_MKV_UI.extend(['NVENC H264', 'NVENC H265'])
                encoding.Task.VIDEO_CODECS_TS_UI.extend(['NVENC H264', 'NVENC H265'])

        return Compatibility._nvenc_supported

    @staticmethod
    def run_test_process(test_process_args: list, counter=None) -> bool:  # Unused parameter necessary for this function
        """
        Runs subprocess.Popen using the given list of arguments. Used to test if the given arguments will result in a
        successful run of subprocess.Popen.

        Parameters:
            test_process_args: List of Strings that represent the args to pass into subprocess.Popen.
            counter: (Default: None) Variable passed in from ThreadPoolExecutor.

        Returns:
            Boolean that represents whether subprocess.Popen had a successful return code.
        """
        with subprocess.Popen(test_process_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as test_process:
            return test_process.wait() == 0

    @staticmethod
    def get_nvenc_test_args() -> list:
        """
        Returns a list of Strings that represent the arguments for running ffmpeg to test the H264 Nvenc codec.

        Returns:
            List of Strings that represent the arguments for running ffmpeg using the H264 Nvenc codec.
        """
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
    def is_encoding_task_compatible(encoding_task) -> bool:
        """
        Returns whether the given encoding task will run successfully with its current settings.

        Returns:
            Boolean that represents whether the given encoding task will run successfully.
        """
        nvenc_test_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        nvenc_test_args.append('-f')
        nvenc_test_args.append('lavfi')
        nvenc_test_args.append('-i')
        nvenc_test_args.append('nullsrc=s=256x256:d=5')

        for setting, arg in encoding_task.video_codec.ffmpeg_args.items():
            nvenc_test_args.append(setting)
            nvenc_test_args.append(arg)

        for setting, arg in encoding_task.video_codec.get_ffmpeg_advanced_args().items():
            nvenc_test_args.append(setting)
            nvenc_test_args.append(arg)

        nvenc_test_args.append('-f')
        nvenc_test_args.append('null')
        nvenc_test_args.append('-')

        return Compatibility.run_test_process(nvenc_test_args)

    @staticmethod
    def is_nvdec_supported() -> bool:
        """
        Returns whether Nvdec is supported on the system running the application.

        Returns:
            Boolean that represents whether Nvdec is supported.
        """
        if Compatibility._nvdec_supported is None:
            Compatibility._nvdec_supported = Compatibility._run_nvdec_test_process()

        return Compatibility._nvdec_supported

    @staticmethod
    def _run_nvdec_test_process() -> bool:
        # Returns whether cuvid was found in ffmpeg's list of decoders.
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
        # Returns a list of Strings that represent the args that will show ffmpeg's available decoders.
        list_decoders_process_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        list_decoders_process_args.append('-decoders')

        return list_decoders_process_args

    @staticmethod
    def is_npp_supported() -> bool:
        """
        Returns whether NPP is supported on the system running this application.

        Returns:
            Boolean that represents whether NPP is supported.
        """
        if Compatibility._npp_supported is None:
            Compatibility._npp_supported = Compatibility._run_npp_test_process()

        return Compatibility._npp_supported

    @staticmethod
    def _run_npp_test_process() -> bool:
        # Returns whether NPP was found in ffmpeg's list of filters.
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
        # Returns a list of Strings that represent the args that will show ffmpeg's available filters.
        npp_test_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        npp_test_args.append('-filters')

        return npp_test_args

    @staticmethod
    def is_nvenc_available() -> bool:
        """
        Returns whether the system running this application can run another process that's utilizing Nvenc.

        Returns:
            Boolean that represents whether the system that's running this application can run another process
            that's utilizing Nvenc.
        """
        return Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

    @staticmethod
    def wait_until_nvenc_available():
        """
        Suspends the calling thread until the system that's running this application is able to run
        a process that's utilizing Nvenc.
        """
        while True:
            if Compatibility.is_nvenc_available():
                break
            else:
                time.sleep(3)


class Parallel:
    """Class that checks/sets parallel processing for Nvenc tasks."""
    nvenc_max_workers = 1

    @staticmethod
    def setup_nvenc_max_workers(app_settings: app_preferences.Settings):
        """
        Sets the maximum number of Nvenc workers that can run simultaneously when parallel encoding is enabled.

        Parameters:
            app_settings: Application's settings.
        """
        if app_settings.parallel_nvenc_workers:
            Parallel.nvenc_max_workers = app_settings.parallel_nvenc_workers

            logging.info(''.join(['--- NVENC MAX WORKERS SET TO: ',
                                  str(app_settings.parallel_nvenc_workers),
                                  ' ---']))
        else:
            Parallel._test_nvenc_max_workers()

    @staticmethod
    def _test_nvenc_max_workers():
        # Runs multiple Nvenc processes simultaneously until it fails or reaches the global max amount of workers.
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(Compatibility.run_test_process,
                                              repeat(Compatibility.get_nvenc_test_args()),
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
        # Returns whether the ThreadPoolExecutor results have failed.
        for result in results:
            if not result:
                return True
        return False
