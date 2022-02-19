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


class NvencBAdaptSignal:
    """
    Handles the signal emitted when the NVENC BAdapt option is changed.
    """

    def __init__(self, nvenc_handlers, inputs_page_handlers, main_window_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_nvenc_b_adapt_checkbutton_toggled(self, nvenc_b_adapt_checkbutton):
        """
        Applies the BAdapt option and updates the preview page.

        :param nvenc_b_adapt_checkbutton: Checkbutton that emitted the signal.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        badapt_enabled = nvenc_b_adapt_checkbutton.get_active()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_adapt = badapt_enabled

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()
