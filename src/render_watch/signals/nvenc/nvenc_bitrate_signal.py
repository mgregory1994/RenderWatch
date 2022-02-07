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


import threading

from render_watch.helpers.nvidia_helper import NvidiaHelper


class NvencBitrateSignal:
    """
    Handles the signals emitted when NVENC Bitrate related options are changed.
    """

    def __init__(self, nvenc_handlers, inputs_page_handlers, main_window_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_nvenc_bitrate_radiobutton_toggled(self, nvenc_bitrate_radiobutton):
        """
        Applies the Bitrate option and updates the preview page.

        :param nvenc_bitrate_radiobutton: Radiobutton that emitted the signal.
        """
        if not nvenc_bitrate_radiobutton.get_active():
            return

        self.nvenc_handlers.set_bitrate_state()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.signal_average_radiobutton()
        self.nvenc_handlers.signal_constant_radiobutton()
        self.nvenc_handlers.signal_2pass_radiobutton()

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.nvenc_handlers.get_bitrate_value()

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_average_radiobutton_toggled(self, nvenc_average_radiobutton):
        """
        Applies the Average Bitrate option and updates the preview page.

        :param nvenc_average_radiobutton: Radiobutton that emitted the signal.
        """
        if not nvenc_average_radiobutton.get_active():
            return

        self.nvenc_handlers.update_rc_from_average_bitrate()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = None

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_constant_radiobutton_toggled(self, nvenc_constant_radiobutton):
        """
        Applies the Constant Bitrate option and updates the preview page.

        :param nvenc_constant_radiobutton: Radiobutton that emitted the signal.
        """
        if not nvenc_constant_radiobutton.get_active():
            return

        self.nvenc_handlers.update_rc_from_constant_bitrate()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = True

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_2_pass_radiobutton_toggled(self, nvenc_2_pass_radiobutton):
        """
        Applies the 2-Pass Bitrate option and updates the preview page.

        :param nvenc_2_pass_radiobutton: Radiobutton that emitted the signal.
        """
        self.nvenc_handlers.set_multi_pass_state(nvenc_2_pass_radiobutton.get_active())

        if not nvenc_2_pass_radiobutton.get_active():
            return

        self.nvenc_handlers.update_rc_from_2pass_bitrate()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        self.nvenc_handlers.signal_multi_pass_combobox()

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.cbr = None
            ffmpeg.video_settings.dual_pass_enabled = True

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_bitrate_spinbutton_value_changed(self, nvenc_bitrate_spinbutton):
        """
        Applies the Bitrate value and updates the preview page.

        :param nvenc_bitrate_spinbutton: Spinbutton that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = nvenc_bitrate_spinbutton.get_value_as_int()

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()
