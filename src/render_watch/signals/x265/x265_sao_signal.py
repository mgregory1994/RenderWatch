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


class X265SaoSignal:
    """
    Handles the signals emitted when x265 SAO related options are changed.
    """

    def __init__(self, x265_handlers, inputs_page_handlers):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x265_sao_checkbutton_toggled(self, x265_sao_checkbutton):
        """
        Configures the x265 widgets for SAO options, applies the SAO option, and updates the preview page.

        :param x265_sao_checkbutton: Checkbutton that emitted the signal.
        """
        self.x265_handlers.set_sao_state(x265_sao_checkbutton.get_active())

        if self.x265_handlers.is_widgets_setting_up:
            return

        is_sao_enabled = x265_sao_checkbutton.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            self._apply_x265_sao_settings(row, is_sao_enabled)

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def _apply_x265_sao_settings(self, row, is_sao_enabled):
        ffmpeg = row.ffmpeg
        ffmpeg.video_settings.no_sao = not is_sao_enabled

        if is_sao_enabled:
            ffmpeg.video_settings.sao_non_deblock = self.x265_handlers.is_sao_non_deblock_enabled()
            ffmpeg.video_settings.limit_sao = self.x265_handlers.is_limit_sao_enabled()
            ffmpeg.video_settings.selective_sao = self.x265_handlers.get_selective_sao_value()
        else:
            ffmpeg.video_settings.sao_non_deblock = False
            ffmpeg.video_settings.limit_sao = False
            ffmpeg.video_settings.selective_sao = None

    def on_x265_sao_no_deblock_checkbutton_toggled(self, x265_sao_no_deblock_checkbutton):
        """
        Toggles the No SAO option and updates the preview page.

        :param x265_sao_no_deblock_checkbutton: Checkbox that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        is_sao_no_deblock_enabled = x265_sao_no_deblock_checkbutton.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.sao_non_deblock = is_sao_no_deblock_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_limit_checkbutton_toggled(self, x265_sao_limit_checkbutton):
        """
        Toggles the Limit SAO option and updates the preview page.

        :param x265_sao_limit_checkbutton: Checkbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        is_sao_limit_enabled = x265_sao_limit_checkbutton.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.limit_sao = is_sao_limit_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_selective_spinbutton_value_changed(self, x265_sao_selective_spinbutton):
        """
        Toggles the Selective SAO option and updates the preview page.

        :param x265_sao_selective_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        sao_selective_value = x265_sao_selective_spinbutton.get_value_as_int()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.selective_sao = sao_selective_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
