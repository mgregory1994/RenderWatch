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


class X265BitrateSignal:
    """Handles the signals emitted when the x265 Bitrate related options are changed."""

    def __init__(self, x265_handlers, inputs_page_handlers, preferences):
        self.x265_handlers = x265_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences

    def on_x265_bitrate_radiobutton_clicked(self, bitrate_radiobutton):
        """Configures the x265 widgets for Bitrate options, applies the Bitrate option, and updates the preview page.

        :param bitrate_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not bitrate_radiobutton.get_active():
            return

        self.x265_handlers.set_bitrate_state()

        if self.x265_handlers.is_widgets_setting_up:
            return

        bitrate_value = self.x265_handlers.get_bitrate_value()
        advanced_enabled = self.x265_handlers.is_advanced_settings_enabled()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            if advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = self.x265_handlers.get_max_bitrate_value()
                ffmpeg.video_settings.vbv_bufsize = self.x265_handlers.get_bufsize_value()
            else:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        """Applies the Bitrate value option and updates the preview page.

        :param bitrate_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.x265_handlers.is_widgets_setting_up:
            return

        if self.x265_handlers.is_vbr_enabled():
            self.x265_handlers.update_vbr()
        bitrate_value = bitrate_spinbutton.get_value_as_int()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_average_radiobutton_toggled(self, average_bitrate_radiobutton):
        """Configures the x265 widgets for Average Bitrate option,
        applies the Bitrate option, and updates the preview page.

        :param average_bitrate_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not average_bitrate_radiobutton.get_active():
            return
        if self.x265_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x265_handlers.is_advanced_settings_enabled()
        if advanced_enabled:
            self.x265_handlers.update_vbr()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_2pass_radiobutton_toggled(self, dual_pass_bitrate_radiobutton):
        """Configures the x265 widgets for 2-pass Bitrate option,
        applies the Bitrate option, and updates the preview page.

        :param dual_pass_bitrate_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not dual_pass_bitrate_radiobutton.get_active():
            return
        if self.x265_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x265_handlers.is_advanced_settings_enabled()
        if advanced_enabled:
            self.x265_handlers.update_vbr()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = 1
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'
            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
