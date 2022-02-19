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


class NvencRateControlSignal:
    """
    Handles the signal emitted when the NVENC Rate Control related settings are changed.
    """

    def __init__(self, nvenc_handlers, inputs_page_handlers, main_window_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_nvenc_rate_control_combobox_changed(self, nvenc_rate_control_combobox):
        """
        Applies the Rate Control type option and updates the preview page.

        :param nvenc_rate_control_combobox: Combobox that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        if not self.nvenc_handlers.is_advanced_settings_enabled():
            return

        rate_control_index = nvenc_rate_control_combobox.get_active()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rc = rate_control_index

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_rate_control_lookahead_spinbutton_value_changed(self, nvenc_rate_control_lookahead_spinbutton):
        """
        Applies the Rate Control Lookahead option and updates the preview page.

        :param nvenc_rate_control_lookahead_spinbutton: Spinbutton that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        rc_lookahead_value = nvenc_rate_control_lookahead_spinbutton.get_value_as_int()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rc_lookahead = rc_lookahead_value

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()
