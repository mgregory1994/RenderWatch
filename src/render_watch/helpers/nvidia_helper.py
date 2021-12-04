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
import logging

from concurrent.futures import ThreadPoolExecutor

from render_watch.startup import Gtk, GLib


class NvidiaHelper:
    """
    Helpful functions for testing Nvidia's NVENC functionality.
    """

    nvenc_supported = None
    nvdec_supported = None
    npp_supported = None
    nvenc_max_workers = 1

    @staticmethod
    def is_nvenc_supported():
        """
        Checks if the system can run ffmpeg using the NVENC codec.
        """
        if NvidiaHelper.nvenc_supported is None:
            NvidiaHelper.nvenc_supported = NvidiaHelper._run_test_process(NvidiaHelper._get_nvenc_test_args())

        return NvidiaHelper.nvenc_supported

    @staticmethod
    def _run_test_process(ffmpeg_args):
        with subprocess.Popen(ffmpeg_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as process:
            return process.wait() == 0

    @staticmethod
    def _get_nvenc_test_args():
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-f')
        ffmpeg_args.append('lavfi')
        ffmpeg_args.append('-i')
        ffmpeg_args.append('nullsrc=s=256x256:d=5')
        ffmpeg_args.append('-c:v')
        ffmpeg_args.append('h264_nvenc')
        ffmpeg_args.append('-f')
        ffmpeg_args.append('null')
        ffmpeg_args.append('-')
        return ffmpeg_args

    @staticmethod
    def is_nvdec_supported():
        """
        Checks if NVDEC is supported by ffmpeg.
        """
        if NvidiaHelper.nvdec_supported is None:
            NvidiaHelper.nvdec_supported = NvidiaHelper._run_nvdec_process()

        return NvidiaHelper.nvdec_supported

    @staticmethod
    def _run_nvdec_process():
        nvdec_found = False

        with subprocess.Popen(NvidiaHelper._get_ffmpeg_decoders_args(),
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
    def _get_ffmpeg_decoders_args():
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-decoders')
        return ffmpeg_args

    @staticmethod
    def is_npp_supported():
        """
        Checks if npp is supported by ffmpeg.
        """
        if NvidiaHelper.npp_supported is None:
            NvidiaHelper.npp_supported = NvidiaHelper._run_npp_process()

        return NvidiaHelper.npp_supported

    @staticmethod
    def _run_npp_process():
        npp_found = False

        with subprocess.Popen(NvidiaHelper._get_ffmpeg_filters_args(),
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
    def _get_ffmpeg_filters_args():
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-filters')
        return ffmpeg_args

    @staticmethod
    def setup_nvenc_max_workers(application_preferences):
        if application_preferences.get_concurrent_nvenc_value():
            NvidiaHelper.nvenc_max_workers = application_preferences.get_concurrent_nvenc_value()
            logging.info('--- NVENC MAX WORKERS SET TO: %s ---',
                         str(application_preferences.get_concurrent_nvenc_value()))
        else:
            NvidiaHelper._test_nvenc_max_workers()

    @staticmethod
    def _test_nvenc_max_workers():
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(NvidiaHelper._run_nvenc_test_process, range(counter))

                if counter > 16 or NvidiaHelper._has_future_executor_results_failed(results):
                    NvidiaHelper.nvenc_max_workers = counter - 1
                    logging.info('--- NVENC MAX WORKERS SET TO: %s ---', str(counter - 1))
                    break

            counter = counter + 1

    @staticmethod
    def _run_nvenc_test_process(counter_id=None):  # Unused parameter necessary for this function.
        return NvidiaHelper._run_test_process(NvidiaHelper._get_nvenc_test_args())

    @staticmethod
    def _has_future_executor_results_failed(results):
        for result in results:
            if not result:
                return True
        return False

    @staticmethod
    def is_nvenc_available():
        """
        Tests if an NVENC process can be ran.
        Used to check if the system will allow another NVENC encode process. The driver may block
        another NVENC process from running.
        """
        return NvidiaHelper._run_test_process(NvidiaHelper._get_nvenc_test_args())

    @staticmethod
    def is_codec_settings_valid(video_codec_settings, main_window):
        from render_watch.ffmpeg.settings import Settings

        ffmpeg_args = Settings.FFMPEG_INIT_ARGS.copy()
        ffmpeg_args.append('-f')
        ffmpeg_args.append('lavfi')
        ffmpeg_args.append('-i')
        ffmpeg_args.append('nullsrc=s=256x256:d=5')
        ffmpeg_args.extend(Settings.generate_video_settings_args(video_codec_settings.ffmpeg_args))
        ffmpeg_args.extend(Settings.generate_video_settings_args(video_codec_settings.get_ffmpeg_advanced_args()))
        ffmpeg_args.append('-f')
        ffmpeg_args.append('null')
        ffmpeg_args.append('-')

        if not NvidiaHelper._run_test_process(ffmpeg_args):
            GLib.idle_add(NvidiaHelper._show_codec_settings_not_supported_message, main_window)

    @staticmethod
    def _show_codec_settings_not_supported_message(main_window):
        message_dialog = Gtk.MessageDialog(main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           'Current NVENC settings not supported on this system.')
        message_dialog.run()
        message_dialog.destroy()
