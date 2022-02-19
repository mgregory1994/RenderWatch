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


class X264BitrateSignal:
    """
    Handles the signals emitted when x264 Bitrate related options are changed.
    """

    def __init__(self, x264_handlers, inputs_page_handlers, application_preferences):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.application_preferences = application_preferences

    def on_x264_bitrate_radiobutton_clicked(self, x264_bitrate_radiobutton):
        """
        Applies the bitrate option, configures the x264 widgets, and updates the preview page.

        :param x264_bitrate_radiobutton: Radiobutton that emitted the signal.
        """
        if not x264_bitrate_radiobutton.get_active():
            return

        self.x264_handlers.set_bitrate_state()
        self.x264_handlers.signal_average_radiobutton()
        self.x264_handlers.signal_constant_radiobutton()
        self.x264_handlers.signal_2pass_radiobutton()

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.x264_handlers.get_bitrate_value()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_average_radiobutton_toggled(self, x264_average_radiobutton):
        """
        Applies the bitrate option, configures the x264 widgets for average bitrate, and updates the preview page.

        :param x264_average_radiobutton: Radiobutton that emitted the signal.
        """
        if not x264_average_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(True)

        if self.x264_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x264_handlers.is_advanced_settings_enabled()
        if advanced_enabled:
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None
            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_constant_radiobutton_toggled(self, x264_constant_radiobutton):
        """
        Applies the bitrate option, configures the x264 widgets for constant bitrate, and updates the preview page.

        :param x264_constant_radiobutton: Radiobutton that emitted the signal.
        """
        if not x264_constant_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(False)

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = True
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_2_pass_radiobutton_toggled(self, x264_2_pass_radiobutton):
        """Configures the x264 widgets for 2-pass options, applies the Bitrate option, and updates the preview page.

        :param x264_2_pass_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not x264_2_pass_radiobutton.get_active():
            return

        self.x264_handlers.set_vbr_state(True)

        if self.x264_handlers.is_widgets_setting_up:
            return

        advanced_enabled = self.x264_handlers.is_advanced_settings_enabled()
        if advanced_enabled:
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = 1
            ffmpeg.video_settings.stats = self.application_preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'
            ffmpeg.video_settings.constant_bitrate = None
            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bitrate_spinbutton_value_changed(self, x264_bitrate_spinbutton):
        """
        Applies the Bitrate option and updates the preview page.

        :param x264_bitrate_spinbutton: Spinbutton that emitted the signal.
        """
        if self.x264_handlers.is_widgets_setting_up:
            return

        if self.x264_handlers.is_vbr_enabled():
            self.x264_handlers.update_vbr()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = x264_bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
