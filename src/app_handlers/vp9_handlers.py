"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""


from ffmpeg.vp9 import VP9


class VP9Handlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.__is_widgets_setting_up = False
        self.inputs_page_handlers = None
        self.vp9_bitrate_spinbutton = gtk_builder.get_object('vp9_bitrate_spinbutton')
        self.vp9_max_bitrate_spinbutton = gtk_builder.get_object('vp9_max_bitrate_spinbutton')
        self.vp9_min_bitrate_spinbutton = gtk_builder.get_object('vp9_min_bitrate_spinbutton')
        self.vp9_bitrate_type_buttonsbox = gtk_builder.get_object('vp9_bitrate_type_buttonsbox')
        self.vp9_quality_combobox = gtk_builder.get_object('vp9_quality_combobox')
        self.vp9_crf_radiobutton = gtk_builder.get_object('vp9_crf_radiobutton')
        self.vp9_bitrate_radiobutton = gtk_builder.get_object('vp9_bitrate_radiobutton')
        self.vp9_constrained_radiobutton = gtk_builder.get_object('vp9_constrained_radiobutton')
        self.vp9_crf_scale = gtk_builder.get_object('vp9_crf_scale')
        self.vp9_2_pass_checkbox = gtk_builder.get_object('vp9_2_pass_checkbox')
        self.vp9_average_radiobutton = gtk_builder.get_object('vp9_average_radiobutton')
        self.vp9_vbr_radiobutton = gtk_builder.get_object('vp9_vbr_radiobutton')
        self.vp9_constant_radiobutton = gtk_builder.get_object('vp9_constant_radiobutton')
        self.vp9_speed_combobox = gtk_builder.get_object('vp9_speed_combobox')
        self.vp9_row_multithreading_checkbox = gtk_builder.get_object('vp9_row_multithreading_checkbox')

    def reset_settings(self):
        self.__is_widgets_setting_up = True

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

        self.__is_widgets_setting_up = False

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_vp9_settings_widgets(ffmpeg)

    def __setup_vp9_settings_widgets(self, ffmpeg):
        video_settings = ffmpeg.video_settings

        if video_settings is not None and video_settings.codec_name == 'libvpx-vp9':
            self.__is_widgets_setting_up = True

            self.vp9_quality_combobox.set_active(video_settings.quality)
            self.vp9_speed_combobox.set_active(video_settings.speed)
            self.vp9_row_multithreading_checkbox.set_active(video_settings.row_multithreading)
            self.__setup_vp9_rate_control_widgets_settings(video_settings)
            self.__setup_vp9_encode_pass_widgets_settings(video_settings)

            self.__is_widgets_setting_up = False
        else:
            self.reset_settings()

    def __setup_vp9_rate_control_widgets_settings(self, video_settings):
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

    def __setup_vp9_encode_pass_widgets_settings(self, video_settings):
        if video_settings.encode_pass:
            self.vp9_2_pass_checkbox.set_active(True)
        else:
            self.vp9_2_pass_checkbox.set_active(False)

    def get_settings(self, ffmpeg):
        video_settings = VP9()
        video_settings.quality = self.vp9_quality_combobox.get_active()
        video_settings.speed = self.vp9_speed_combobox.get_active()
        video_settings.row_multithreading = self.vp9_row_multithreading_checkbox.get_active()

        self.__set_rate_control_settings_from_vp9_widgets(video_settings)
        self.__set_encode_pass_settings_from_vp9_widgets(video_settings, ffmpeg.temp_file_name)

        ffmpeg.video_settings = video_settings

    def __set_rate_control_settings_from_vp9_widgets(self, video_settings):
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

    def __set_encode_pass_settings_from_vp9_widgets(self, video_settings, temp_file_name):
        if self.vp9_2_pass_checkbox.get_active():
            video_settings.encode_pass = 1
            video_settings.stats = self.preferences.temp_directory + '/' + temp_file_name + '.log'

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def on_vp9_quality_combobox_changed(self, quality_combobox):
        if self.__is_widgets_setting_up:
            return

        quality_setting_index = quality_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.quality = quality_setting_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_speed_combobox_changed(self, speed_combobox):
        if self.__is_widgets_setting_up:
            return

        speed_setting_index = speed_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.speed = speed_setting_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_row_multithreading_checkbox_toggled(self, row_multithreading_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.row_multithreading = row_multithreading_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_2_pass_checkbox_toggled(self, encode_2_pass_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            if encode_2_pass_checkbox.get_active():
                ffmpeg.video_settings.encode_pass = 1
                ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'
            else:
                ffmpeg.video_settings.encode_pass = None
                ffmpeg.video_settings.stats = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_crf_radiobutton_toggled(self, crf_radiobutton):
        if self.__is_widgets_setting_up or not crf_radiobutton.get_active():
            return

        crf_value = self.vp9_crf_scale.get_value()

        self.vp9_crf_scale.set_sensitive(True)
        self.vp9_bitrate_spinbutton.set_sensitive(False)
        self.vp9_max_bitrate_spinbutton.set_sensitive(False)
        self.vp9_min_bitrate_spinbutton.set_sensitive(False)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(False)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = crf_value
            ffmpeg.video_settings.bitrate = 0
            ffmpeg.video_settings.maxrate = None
            ffmpeg.video_settings.minrate = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_bitrate_radiobutton_toggled(self, bitrate_radiobutton):
        if self.__is_widgets_setting_up or not bitrate_radiobutton.get_active():
            return

        self.vp9_crf_scale.set_sensitive(False)
        self.vp9_bitrate_spinbutton.set_sensitive(True)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(True)
        self.on_vp9_average_radiobutton_toggled(self.vp9_average_radiobutton)
        self.on_vp9_vbr_radiobutton_toggled(self.vp9_vbr_radiobutton)
        self.on_vp9_constant_radiobutton_toggled(self.vp9_constant_radiobutton)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_average_radiobutton_toggled(self, average_radiobutton):
        if self.__is_widgets_setting_up or not average_radiobutton.get_active():
            return

        bitrate_value = self.vp9_bitrate_spinbutton.get_value_as_int()

        self.vp9_max_bitrate_spinbutton.set_sensitive(False)
        self.vp9_min_bitrate_spinbutton.set_sensitive(False)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = None
            ffmpeg.video_settings.minrate = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_vbr_radiobutton_toggled(self, vbr_radiobutton):
        if self.__is_widgets_setting_up or not vbr_radiobutton.get_active():
            return

        bitrate_value = self.vp9_bitrate_spinbutton.get_value_as_int()
        max_bitrate_value = self.vp9_max_bitrate_spinbutton.get_value_as_int()
        min_bitrate_value = self.vp9_min_bitrate_spinbutton.get_value_as_int()

        self.vp9_max_bitrate_spinbutton.set_sensitive(True)
        self.vp9_min_bitrate_spinbutton.set_sensitive(True)
        self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = max_bitrate_value
            ffmpeg.video_settings.minrate = min_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_vbr_widgets(self, bitrate_value):
        if bitrate_value < self.vp9_min_bitrate_spinbutton.get_value_as_int():
            self.vp9_min_bitrate_spinbutton.set_value(bitrate_value)

        if bitrate_value > self.vp9_max_bitrate_spinbutton.get_value_as_int():
            self.vp9_max_bitrate_spinbutton.set_value(bitrate_value)

    def on_vp9_constant_radiobutton_toggled(self, constant_radiobutton):
        if self.__is_widgets_setting_up or not constant_radiobutton.get_active():
            return

        bitrate_value = self.vp9_bitrate_spinbutton.get_value_as_int()

        self.vp9_max_bitrate_spinbutton.set_sensitive(False)
        self.vp9_min_bitrate_spinbutton.set_sensitive(False)
        self.__update_constant_bitrate_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value
            ffmpeg.video_settings.maxrate = bitrate_value
            ffmpeg.video_settings.minrate = bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_constant_bitrate_widgets(self, bitrate_value):
        self.vp9_min_bitrate_spinbutton.set_value(bitrate_value)
        self.vp9_max_bitrate_spinbutton.set_value(bitrate_value)

    def on_vp9_constrained_radiobutton_toggled(self, constrained_radiobutton):
        if self.__is_widgets_setting_up or not constrained_radiobutton.get_active():
            return

        crf_value = self.vp9_crf_scale.get_value()

        self.vp9_crf_scale.set_sensitive(True)
        self.vp9_bitrate_spinbutton.set_sensitive(True)
        self.vp9_average_radiobutton.set_active(True)
        self.vp9_bitrate_type_buttonsbox.set_sensitive(False)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = crf_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_crf_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        crf_value = self.vp9_crf_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = crf_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        bitrate_value = bitrate_spinbutton.get_value_as_int()

        if self.vp9_vbr_radiobutton.get_active():
            self.__update_vbr_widgets(bitrate_value)
        elif self.vp9_constant_radiobutton.get_active():
            self.__update_constant_bitrate_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_vp9_max_bitrate_spinbutton_value_changed(self, max_bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        max_bitrate_value = max_bitrate_spinbutton.get_value_as_int()

        self.__update_bitrate_widget_from_max_bitrate(max_bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.maxrate = max_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_bitrate_widget_from_max_bitrate(self, max_bitrate_value):
        if max_bitrate_value < self.vp9_bitrate_spinbutton.get_value_as_int():
            self.vp9_bitrate_spinbutton.set_value(max_bitrate_value)

    def on_vp9_min_bitrate_spinbutton_value_changed(self, min_bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        min_bitrate_value = min_bitrate_spinbutton.get_value_as_int()

        self.__update_bitrate_widget_from_min_bitrate(min_bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.minrate = min_bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_bitrate_widget_from_min_bitrate(self, min_bitrate_value):
        if min_bitrate_value > self.vp9_bitrate_spinbutton.get_value_as_int():
            self.vp9_bitrate_spinbutton.set_value(min_bitrate_value)
