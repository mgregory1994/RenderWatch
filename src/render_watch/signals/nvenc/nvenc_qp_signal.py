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


class NvencQpSignal:
    """
    Handles the signals emitted when the NVENC QP related options are changed.
    """

    def __init__(self, nvenc_handlers, inputs_page_handlers, main_window_handlers):
        self.nvenc_handlers = nvenc_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_nvenc_qp_radiobutton_toggled(self, nvenc_qp_radiobutton):
        """
        Applies the QP option and updates the preview page.

        :param nvenc_qp_radiobutton: Radiobutton that emitted the signal.
        """
        if not nvenc_qp_radiobutton.get_active():
            return

        self.nvenc_handlers.set_qp_state()
        self.nvenc_handlers.update_rc_from_qp()

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = self.nvenc_handlers.get_qp_value()
            ffmpeg.video_settings.dual_pass = None
            ffmpeg.video_settings.cbr = None

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    # Unused parameters needed for this signal
    def on_nvenc_qp_scale_button_release_event(self, nvenc_qp_scale, event=None, user_data=None):
        """
        Applies the QP value option and updates the preview page.

        :param nvenc_qp_scale: Scale that emitted the signal.
        :param event: Unused parameter.
        :param user_data: Unused parameter.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        qp_value = self.nvenc_handlers.get_qp_value()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = qp_value

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_scale_key_release_event(self, nvenc_qp_scale, event, user_data):
        self.on_nvenc_qp_scale_button_release_event(nvenc_qp_scale, event, user_data)

    def on_nvenc_qp_auto_radiobutton_toggled(self, nvenc_qp_auto_radiobutton):
        """
        Removes the QP_i, QP_p, and QP_b options and updates the preview page.

        :param nvenc_qp_auto_radiobutton: Radiobutton that emitted the signal.
        """
        if not nvenc_qp_auto_radiobutton.get_active():
            return
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_i = None
            ffmpeg.video_settings.qp_p = None
            ffmpeg.video_settings.qp_b = None

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_custom_radiobutton_toggled(self, qp_custom_radiobutton):
        """
        Applies the QP_i, QP_p, and QP_b options and updates the preview page.

        :param qp_custom_radiobutton: Radiobutton that emitted the signal.
        """
        qp_custom_enabled = qp_custom_radiobutton.get_active()
        self.nvenc_handlers.set_qp_custom_state(qp_custom_enabled)

        if self.nvenc_handlers.is_widgets_setting_up:
            return

        qp_i_value = self.nvenc_handlers.get_qp_i_value()
        qp_p_value = self.nvenc_handlers.get_qp_p_value()
        qp_b_value = self.nvenc_handlers.get_qp_b_value()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg

            if qp_custom_enabled:
                ffmpeg.video_settings.qp_i = qp_i_value
                ffmpeg.video_settings.qp_p = qp_p_value
                ffmpeg.video_settings.qp_b = qp_b_value
                ffmpeg.video_settings.bitrate = None
                ffmpeg.video_settings.cbr = None
                ffmpeg.video_settings.dual_pass = None
            ffmpeg.video_settings.qp_custom_enabled = qp_custom_enabled

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    # Unused parameters needed for this signal
    def on_nvenc_qp_i_scale_button_release_event(self, nvenc_qp_i_scale, event=None, user_data=None):
        """
        Applies the QP_i value option and updates the preview page.

        :param nvenc_qp_i_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        qp_i_value = self.nvenc_handlers.get_qp_i_value()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_i = qp_i_value

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_i_scale_key_release_event(self, nvenc_qp_i_scale, event, user_data):
        self.on_nvenc_qp_i_scale_button_release_event(nvenc_qp_i_scale, event, user_data)

    # Unused parameters needed for this signal
    def on_nvenc_qp_p_scale_button_release_event(self, nvenc_qp_p_scale, event=None, user_data=None):
        """
        Applies the QP_p value option and updates the preview page.

        :param nvenc_qp_p_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user_data.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        qp_p_value = self.nvenc_handlers.get_qp_p_value()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_p = qp_p_value

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_p_scale_key_release_event(self, nvenc_qp_p_scale, event, user_data):
        self.on_nvenc_qp_p_scale_button_release_event(nvenc_qp_p_scale, event, user_data)

    # Unused parameters needed for this signal
    def on_nvenc_qp_b_scale_button_release_event(self, nvenc_qp_b_scale, event=None, user_data=None):
        """
        Applies the QP_b value option and updates the preview page.

        :param nvenc_qp_b_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        if self.nvenc_handlers.is_widgets_setting_up:
            return

        qp_b_value = self.nvenc_handlers.get_qp_b_value()
        codec_settings = None

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_b = qp_b_value

            if codec_settings is None:
                codec_settings = ffmpeg.video_settings

            row.setup_labels()

        threading.Thread(target=NvidiaHelper.is_codec_settings_valid,
                         args=(codec_settings, self.main_window_handlers.main_window)).start()
        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_b_scale_key_release_event(self, nvenc_qp_b_scale, event, user_data):
        """
        Applies the QP_b value option and updates the preview page.

        :param nvenc_qp_b_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self.on_nvenc_qp_b_scale_button_release_event(nvenc_qp_b_scale, event, user_data)
