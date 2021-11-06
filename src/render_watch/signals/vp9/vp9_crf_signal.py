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


class Vp9CrfSignal:
    """
    Handles the signals emitted when VP9 CRF related options are changed.
    """

    def __init__(self, vp9_handlers, inputs_page_handlers):
        self.vp9_handlers = vp9_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_vp9_crf_radiobutton_toggled(self, vp9_crf_radiobutton):
        """
        Configures the VP9 Widgets for CRF options, applies the CRF option, and updates the preview page.

        :param vp9_crf_radiobutton: Radiobutton that emitted the signal.
        """
        if not vp9_crf_radiobutton.get_active():
            return

        self.vp9_handlers.set_crf_state()

        if self.vp9_handlers.is_widgets_setting_up:
            return

        crf_value = self.vp9_handlers.get_crf_value()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = crf_value
            ffmpeg.video_settings.bitrate = 0
            ffmpeg.video_settings.maxrate = None
            ffmpeg.video_settings.minrate = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_crf_scale_button_release_event(self, vp9_crf_scale, event=None, user_data=None):
        """
        Applies the CRF value option and updates the preview page.

        :param vp9_crf_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        if self.vp9_handlers.is_widgets_setting_up:
            return

        crf_value = vp9_crf_scale.get_value()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = crf_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
