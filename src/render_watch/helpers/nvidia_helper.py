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
import re
import subprocess
import logging

from concurrent.futures import ThreadPoolExecutor


class NvidiaHelper:
    """Contains methods for testing Nvidia's NVENC functionality on the system."""

    nvenc_supported = None
    nvdec_supported = None
    npp_supported = None
    nvenc_max_workers = 1

    @staticmethod
    def is_nvenc_supported():
        """Checks if the system can run ffmpeg using the NVENC codec."""
        if NvidiaHelper.nvenc_supported is None:
            NvidiaHelper.nvenc_supported = NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_nvenc_test_args())

        return NvidiaHelper.nvenc_supported

    @staticmethod
    def __run_test_process(ffmpeg_args):
        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            return process.wait() == 0

    @staticmethod
    def __get_new_nvenc_test_args():
        # Generates ffmpeg arguments for running a test encode using a null source.
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
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
        """Checks if NVDEC is supported by ffmpeg.

        Only runs once and then returns the same value every time afterwards until the application is restarted.
        """
        if NvidiaHelper.nvdec_supported is None:
            NvidiaHelper.nvdec_supported = NvidiaHelper.__run_check_nvdec_process()

        return NvidiaHelper.nvdec_supported

    @staticmethod
    def __run_check_nvdec_process():
        # Runs a process that tests if ffmpeg can use NVDEC.
        nvdec_found = False

        with subprocess.Popen(NvidiaHelper.__get_new_nvdec_test_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            while True:
                stdout = process.stdout.readline().strip().decode()
                if stdout == '':
                    break
                if 'cuvid' in stdout:
                    nvdec_found = True

        return nvdec_found

    @staticmethod
    def __get_new_nvdec_test_args():
        # Returns ffmpeg arguments to test if NVDEC is supported.
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-decoders')
        return ffmpeg_args

    @staticmethod
    def is_npp_supported():
        """Checks if npp is supported by ffmpeg.

        Only runs once and then returns the same value every time afterwards until the application is restarted.
        """
        if NvidiaHelper.npp_supported is None:
            NvidiaHelper.npp_supported = NvidiaHelper.__run_check_npp_process()

        return NvidiaHelper.npp_supported

    @staticmethod
    def __run_check_npp_process():
        # Runs a process that tests if ffmpeg can use npp.
        npp_found = False

        with subprocess.Popen(NvidiaHelper.__get_new_npp_test_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            while True:
                stdout = process.stdout.readline().strip().decode()
                if stdout == '':
                    break
                if 'npp' in stdout:
                    npp_found = True

        return npp_found

    @staticmethod
    def __get_new_npp_test_args():
        # Returns ffmpeg arguments to test if npp is supported.
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-filters')
        return ffmpeg_args

    @staticmethod
    def setup_nvenc_max_workers(preferences):
        # Sets the maximum number of parallel NVENC tasks using preferences or by running a test.
        if preferences.concurrent_nvenc_value != 0:
            NvidiaHelper.nvenc_max_workers = preferences.concurrent_nvenc_value
            logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(preferences.concurrent_nvenc_value))
        else:
            NvidiaHelper.__test_nvenc_max_workers()

    @staticmethod
    def __test_nvenc_max_workers():
        # Increments and runs a number of concurrent processes to find the max supported concurrent NVENC processes.
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
    def __run_nvenc_test_process(counter_id=None):  # Unused parameter necessary for this function.
        # Runs a test process to test if NVENC is supported on the system.
        return NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_nvenc_test_args())

    @staticmethod
    def __has_future_executor_results_failed(results):
        for result in results:
            if not result:
                return True
        return False

    @staticmethod
    def is_nvenc_available():
        """Tests if we can successfully run another NVENC encode process.

        Used to check if the system will allow another NVENC encode process because the driver may block
        another NVENC process from running.
        """
        return NvidiaHelper.__run_test_process(NvidiaHelper.__get_new_nvenc_test_args())

    @staticmethod
    def get_h264_nvenc_options():
        """Checks what h264 NVENC options are available on current version of ffmpeg."""
        ffmpeg_args = NvidiaHelper._get_h264_nvenc_options_args()
        return NvidiaHelper._run_nvenc_options_args(ffmpeg_args)

    @staticmethod
    def _get_h264_nvenc_options_args():
        # Create and return the args needed to show all h264_nvenc options.
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-h')
        ffmpeg_args.append('encoder=h264_nvenc')
        return ffmpeg_args

    @staticmethod
    def get_hevc_nvenc_options():
        """Checks what h264 NVENC options are available on current version of ffmpeg."""
        ffmpeg_args = NvidiaHelper._get_hevc_nvenc_options_args()
        return NvidiaHelper._run_nvenc_options_args(ffmpeg_args)

    @staticmethod
    def _get_hevc_nvenc_options_args():
        # Create and return the args needed to show all h264_nvenc options.
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-h')
        ffmpeg_args.append('encoder=hevc_nvenc')
        return ffmpeg_args

    @staticmethod
    def _run_nvenc_options_args(ffmpeg_args):
        # Run ffmpeg to display all h264_nvenc options and return those values as a dictionary.
        h264_nvenc_options = {}
        last_option_found = None

        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            while True:
                stdout = process.stdout.readline().strip().decode()
                if stdout == '':
                    break

                option_match = re.search('^-\w+-\w+|^-\w+', stdout)
                option_value_match = re.search('^\d.\w+|^\w+', stdout)
                if option_match:
                    last_option_found = option_match.group()
                    h264_nvenc_options[last_option_found] = []
                if option_value_match and last_option_found:
                    h264_nvenc_options[last_option_found].append(option_value_match.group())
        print(h264_nvenc_options)
        return h264_nvenc_options
