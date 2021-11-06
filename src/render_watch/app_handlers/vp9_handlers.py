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


from render_watch.ffmpeg.vp9 import VP9
from render_watch.signals.vp9.vp9_crf_signal import Vp9CrfSignal
from render_watch.signals.vp9.vp9_bitrate_signal import Vp9BitrateSignal
from render_watch.signals.vp9.vp9_constrained_signal import Vp9ConstrainedSignal
from render_watch.signals.vp9.vp9_2_pass_signal import Vp92PassSignal
from render_watch.signals.vp9.vp9_quality_signal import Vp9QualitySignal
from render_watch.signals.vp9.vp9_speed_signal import Vp9SpeedSignal
from render_watch.signals.vp9.vp9_row_multithreading_signal import Vp9RowMultithreadingSignal


class VP9Handlers:
    """
    Handles all widget changes for the VP9 codec.
    """

    def __init__(self, gtk_builder, inputs_page_handlers, application_preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.application_preferences = application_preferences
        self.is_widgets_setting_up = False

        self.vp9_crf_signal = Vp9CrfSignal(self, inputs_page_handlers)
        self.vp9_bitrate_signal = Vp9BitrateSignal(self, inputs_page_handlers)
        self.vp9_constrained_signal = Vp9ConstrainedSignal(self, inputs_page_handlers)
        self.vp9_2_pass_signal = Vp92PassSignal(self, inputs_page_handlers, application_preferences)
        self.vp9_quality_signal = Vp9QualitySignal(self, inputs_page_handlers)
        self.vp9_speed_signal = Vp9SpeedSignal(self, inputs_page_handlers)
        self.vp9_row_multithreading_signal = Vp9RowMultithreadingSignal(self, inputs_page_handlers)
        self.signals_list = (
            self.vp9_crf_signal, self.vp9_bitrate_signal, self.vp9_constrained_signal,
            self.vp9_2_pass_signal, self.vp9_quality_signal, self.vp9_speed_signal,
            self.vp9_row_multithreading_signal
        )

        self.vp9_bitrate_spinbutton = gtk_builder.get_object('vp9_bitrate_spinbutton')
        self.vp9_max_bitrate_spinbutton = gtk_builder.get_object('vp9_max_bitrate_spinbutton')
        self.vp9_min_bitrate_spinbutton = gtk_builder.get_object('vp9_min_bitrate_spinbutton')
        self.vp9_rate_type_buttonbox = gtk_builder.get_object('vp9_rate_type_buttonbox')
        self.vp9_quality_combobox = gtk_builder.get_object('vp9_quality_combobox')
        self.vp9_crf_radiobutton = gtk_builder.get_object('vp9_crf_radiobutton')
        self.vp9_bitrate_radiobutton = gtk_builder.get_object('vp9_bitrate_radiobutton')
        self.vp9_constrained_radiobutton = gtk_builder.get_object('vp9_constrained_radiobutton')
        self.vp9_crf_scale = gtk_builder.get_object('vp9_crf_scale')
        self.vp9_2_pass_checkbutton = gtk_builder.get_object('vp9_2_pass_checkbutton')
        self.vp9_average_radiobutton = gtk_builder.get_object('vp9_average_radiobutton')
        self.vp9_vbr_radiobutton = gtk_builder.get_object('vp9_vbr_radiobutton')
        self.vp9_constant_radiobutton = gtk_builder.get_object('vp9_constant_radiobutton')
        self.vp9_speed_combobox = gtk_builder.get_object('vp9_speed_combobox')
        self.vp9_row_multithreading_checkbutton = gtk_builder.get_object('vp9_row_multithreading_checkbutton')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def apply_settings(self, ffmpeg):
        """
        Applies settings from the vp9 widgets to ffmpeg settings.
        """
        video_settings = VP9()
        video_settings.quality = self.vp9_quality_combobox.get_active()
        video_settings.speed = self.vp9_speed_combobox.get_active()
        video_settings.row_multithreading = self.vp9_row_multithreading_checkbox.get_active()
        self._apply_rate_control_settings(video_settings)
        self._apply_encode_pass_settings(video_settings, ffmpeg.temp_file_name)

        ffmpeg.video_settings = video_settings

    def _apply_rate_control_settings(self, video_settings):
        if self.vp9_crf_radiobutton.get_active():
            video_settings.crf = self.vp9_crf_scale.get_value()
            video_settings.bitrate = 0
        elif self.vp9_bitrate_radiobutton.get_active():
            video_settings.bitrate = self.vp9_bitrate_spinbutton.get_value_as_int()

            if not self.vp9_average_radiobutton.get_active():
                video_settings.maxrate = self.vp9_max_bitrate_spinbutton.get_value_as_int()
                video_settings.minrate = self.vp9_min_bitrate_spinbutton.get_value_as_int()
        else:
            video_settings.bitrate = self.vp9_bitrate_spinbutton.get_value_as_int()
            video_settings.crf = self.vp9_crf_scale.get_value()

    def _apply_encode_pass_settings(self, video_settings, temp_file_name):
        if self.vp9_2_pass_checkbox.get_active():
            video_settings.encode_pass = 1
            video_settings.stats = self.application_preferences.temp_directory + '/' + temp_file_name + '.log'

    def set_settings(self, ffmpeg_param=None):
        """
        Configures the vp9 widgets to match the selected task's ffmpeg settings.
        """
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self._setup_vp9_settings_widgets(ffmpeg)

    def _setup_vp9_settings_widgets(self, ffmpeg):
        if ffmpeg.is_video_settings_vp9():
            video_settings = ffmpeg.video_settings

            self.is_widgets_setting_up = True
            self.vp9_quality_combobox.set_active(video_settings.quality)
            self.vp9_speed_combobox.set_active(video_settings.speed)
            self.vp9_row_multithreading_checkbox.set_active(video_settings.row_multithreading)
            self._setup_vp9_rate_control_widgets(video_settings)
            self._setup_vp9_encode_pass_widgets(video_settings)
            self.is_widgets_setting_up = False
        else:
            self.reset_settings()

    def _setup_vp9_rate_control_widgets(self, video_settings):
        bitrate_value = video_settings.bitrate
        max_bitrate_value = video_settings.maxrate
        min_bitrate_value = video_settings.minrate
        crf_value = video_settings.crf

        if bitrate_value == 0:
            self.vp9_crf_radiobutton.set_active(True)
            self.vp9_crf_scale.set_value(crf_value)
        elif crf_value and bitrate_value:
            self.vp9_constrained_radiobutton.set_active(True)
            self.vp9_crf_scale.set_value(crf_value)
            self.vp9_bitrate_spinbutton.set_value(bitrate_value)
        else:
            self._setup_vp9_bitrate_widgets(bitrate_value, max_bitrate_value, min_bitrate_value)

    def _setup_vp9_bitrate_widgets(self, bitrate_value, max_bitrate_value, min_bitrate_value):
        self.vp9_bitrate_radiobutton.set_active(True)
        self.vp9_bitrate_spinbutton.set_value(bitrate_value)

        if max_bitrate_value and min_bitrate_value:
            if max_bitrate_value == min_bitrate_value:
                min_bitrate_value = bitrate_value
                max_bitrate_value = bitrate_value
                self.vp9_constant_radiobutton.set_active(True)
            else:
                self.vp9_vbr_radiobutton.set_active(True)

            self.vp9_max_bitrate_spinbutton.set_value(max_bitrate_value)
            self.vp9_min_bitrate_spinbutton.set_value(min_bitrate_value)
        else:
            self.vp9_average_radiobutton.set_active(True)

    def _setup_vp9_encode_pass_widgets(self, video_settings):
        if video_settings.encode_pass:
            self.vp9_2_pass_checkbox.set_active(True)
        else:
            self.vp9_2_pass_checkbox.set_active(False)

    def reset_settings(self):
        """
        Resets the vp9 widgets to their default values.
        """
        self.is_widgets_setting_up = True
        self.vp9_quality_combobox.set_active(0)
        self.vp9_bitrate_radiobutton.set_active(True)
        self.vp9_crf_scale.set_value(30.0)
        self.vp9_bitrate_spinbutton.set_value(2500)
        self.vp9_min_bitrate_spinbutton.set_value(2500)
        self.vp9_max_bitrate_spinbutton.set_value(2500)
        self.vp9_average_radiobutton.set_active(True)
        self.vp9_2_pass_checkbox.set_active(False)
        self.vp9_speed_combobox.set_active(0)
        self.vp9_row_multithreading_checkbox.set_active(False)
        self.is_widgets_setting_up = False

    def get_crf_value(self):
        return self.vp9_crf_scale.get_value()

    def get_bitrate_value(self):
        return self.vp9_bitrate_spinbutton.get_value_as_int()

    def get_max_bitrate_value(self):
        return self.vp9_max_bitrate_spinbutton.get_value_as_int()

    def get_min_bitrate_value(self):
        return self.vp9_min_bitrate_spinbutton.get_value_as_int()

    def is_vbr_active(self):
        return self.vp9_vbr_radiobutton.get_active()

    def is_constant_bitrate_active(self):
        return self.vp9_constant_radiobutton.get_active()

    def set_crf_state(self):
        self.vp9_crf_scale.set_sensitive(True)
        self.vp9_bitrate_spinbutton.set_sensitive(False)
        self.vp9_max_bitrate_spinbutton.set_sensitive(False)
        self.vp9_min_bitrate_spinbutton.set_sensitive(False)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(False)

    def set_bitrate_state(self):
        self.vp9_crf_scale.set_sensitive(False)
        self.vp9_bitrate_spinbutton.set_sensitive(True)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(True)

    def set_vbr_state(self, enabled):
        self.vp9_max_bitrate_spinbutton.set_sensitive(enabled)
        self.vp9_min_bitrate_spinbutton.set_sensitive(enabled)

    def set_constrained_state(self):
        self.vp9_crf_scale.set_sensitive(True)
        self.vp9_bitrate_spinbutton.set_sensitive(True)
        self.vp9_average_radiobutton.set_active(True)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(False)

    def update_vbr_widgets(self, bitrate_value):
        if bitrate_value < self.get_min_bitrate_value():
            self.vp9_min_bitrate_spinbutton.set_value(bitrate_value)

        if bitrate_value > self.get_max_bitrate_value():
            self.vp9_max_bitrate_spinbutton.set_value(bitrate_value)

    def update_constant_bitrate_widgets(self, bitrate_value):
        self.vp9_min_bitrate_spinbutton.set_value(bitrate_value)
        self.vp9_max_bitrate_spinbutton.set_value(bitrate_value)

    def update_bitrate_from_max_bitrate(self, max_bitrate_value):
        if max_bitrate_value < self.vp9_bitrate_spinbutton.get_value_as_int():
            self.vp9_bitrate_spinbutton.set_value(max_bitrate_value)

    def update_bitrate_from_min_bitrate(self, min_bitrate_value):
        if min_bitrate_value > self.vp9_bitrate_spinbutton.get_value_as_int():
            self.vp9_bitrate_spinbutton.set_value(min_bitrate_value)

    def signal_average_radiobutton(self):
        self.vp9_bitrate_signal.on_vp9_average_radiobutton_toggled(self.vp9_average_radiobutton)

    def signal_vbr_radiobutton(self):
        self.vp9_bitrate_signal.on_vp9_vbr_radiobutton_toggled(self.vp9_vbr_radiobutton)

    def signal_constant_radiobutton(self):
        self.vp9_bitrate_signal.on_vp9_constant_radiobutton_toggled(self.vp9_constant_radiobutton)
