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


class X264MeSignal:
    """
    Handles the signals emitted when x264 Motion Estimation related options are changed.
    """

    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_me_combobox_changed(self, x264_me_combobox):
        """
        Applies the Motion Estimation option and updates the preview page.

        :param x264_me_combobox: Combobox that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        me_index = x264_me_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.me = me_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_subme_combobox_changed(self, x264_subme_combobox):
        """
        Applies the Sub-Motion Estimation option and updates the preview page.

        :param x264_subme_combobox: Combobox that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        subme_index = x264_subme_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.subme = subme_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_me_range_spinbutton_value_changed(self, x264_me_range_spinbutton):
        """
        Applies the Motion Estimation Range option and updates the preview page.

        :param x264_me_range_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.me_range = x264_me_range_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
