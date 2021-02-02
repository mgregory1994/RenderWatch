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


import threading

from render_watch.ffmpeg.x264 import X264
from render_watch.startup import GLib


class X264Handlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.__is_widgets_setting_up = False
        self.inputs_page_handlers = None
        self.x264_crf_radiobutton = gtk_builder.get_object("x264_crf_radiobutton")
        self.x264_qp_radiobutton = gtk_builder.get_object("x264_qp_radiobutton")
        self.x264_bitrate_radiobutton = gtk_builder.get_object("x264_bitrate_radiobutton")
        self.x264_average_radiobutton = gtk_builder.get_object('x264_average_radiobutton')
        self.x264_constant_radiobutton = gtk_builder.get_object('x264_constant_radiobutton')
        self.x264_2pass_radiobutton = gtk_builder.get_object('x264_2pass_radiobutton')
        self.x264_rate_type_stack = gtk_builder.get_object("x264_rate_type_stack")
        self.x264_crf_scale = gtk_builder.get_object("x264_crf_scale")
        self.x264_bitrate_box = gtk_builder.get_object("x264_bitrate_box")
        self.x264_bitrate_spinbutton = gtk_builder.get_object('x264_bitrate_spinbutton')
        self.x264_preset_combobox = gtk_builder.get_object('x264_preset_combobox')
        self.x264_profile_combobox = gtk_builder.get_object('x264_profile_combobox')
        self.x264_level_combobox = gtk_builder.get_object('x264_level_combobox')
        self.x264_tune_combobox = gtk_builder.get_object('x264_tune_combobox')
        self.x264_advanced_settings_revealer = gtk_builder.get_object('x264_advanced_settings_revealer')
        self.x264_advanced_settings_switch = gtk_builder.get_object('x264_advanced_settings_switch')
        self.x264_vbv_max_rate_spinbutton = gtk_builder.get_object('x264_vbv_max_rate_spinbutton')
        self.x264_vbv_bufsize_spinbutton = gtk_builder.get_object('x264_vbv_bufsize_spinbutton')
        self.x264_aq_mode_combobox = gtk_builder.get_object('x264_aq_mode_combobox')
        self.x264_aq_strength_spinbutton = gtk_builder.get_object('x264_aq_strength_spinbutton')
        self.x264_ref_spinbutton = gtk_builder.get_object('x264_reference_frames_spinbutton')
        self.x264_mixed_refs_checkbox = gtk_builder.get_object('x264_mixed_refs_checkbox')
        self.x264_bframes_spinbutton = gtk_builder.get_object('x264_bframes_spinbutton')
        self.x264_b_adapt_combobox = gtk_builder.get_object('x264_badapt_combobox')
        self.x264_b_pyramid_combobox = gtk_builder.get_object('x264_bpyramid_combobox')
        self.x264_weight_p_combobox = gtk_builder.get_object('x264_weight_p_combobox')
        self.x264_weight_b_checkbox = gtk_builder.get_object('x264_weight_b_checkbox')
        self.x264_keyint_spinbutton = gtk_builder.get_object('x264_keyframe_interval_spinbutton')
        self.x264_min_keyint_spinbutton = gtk_builder.get_object('x264_min_keyframe_interval_spinbutton')
        self.x264_me_combobox = gtk_builder.get_object('x264_motion_estimation_combobox')
        self.x264_subme_combobox = gtk_builder.get_object('x264_sub_motion_estimation_combobox')
        self.x264_me_range_spinbutton = gtk_builder.get_object('x264_me_range_spinbutton')
        self.x264_partitions_auto_radiobutton = gtk_builder.get_object('x264_partitions_auto_radiobutton')
        self.x264_partitions_custom_radiobutton = gtk_builder.get_object('x264_partitions_custom_radiobutton')
        self.x264_partitions_types_grid = gtk_builder.get_object('x264_partitions_types_grid')
        self.x264_i8x8_checkbox = gtk_builder.get_object('x264_i8x8_checkbox')
        self.x264_i4x4_checkbox = gtk_builder.get_object('x264_i4x4_checkbox')
        self.x264_p8x8_checkbox = gtk_builder.get_object('x264_p8x8_checkbox')
        self.x264_p4x4_checkbox = gtk_builder.get_object('x264_p4x4_checkbox')
        self.x264_b8x8_checkbox = gtk_builder.get_object('x264_b8x8_checkbox')
        self.x264_8x8dct_checkbox = gtk_builder.get_object('x264_8x8dct_checkbox')
        self.x264_psy_rd_spinbutton = gtk_builder.get_object('x264_psy_rd_spinbutton')
        self.x264_psy_rd_trellis_spinbutton = gtk_builder.get_object('x264_psy_rd_trellis_spinbutton')
        self.x264_trellis_combobox = gtk_builder.get_object('x264_trellis_combobox')
        self.x264_direct_combobox = gtk_builder.get_object('x264_direct_combobox')
        self.x264_no_deblock_checkbox = gtk_builder.get_object('x264_no_deblock_checkbox')
        self.x264_deblock_alpha_spinbutton = gtk_builder.get_object('x264_deblock_alpha_spinbutton')
        self.x264_deblock_beta_spinbutton = gtk_builder.get_object('x264_deblock_beta_spinbutton')
        self.x264_no_fast_pskip_checkbox = gtk_builder.get_object('x264_no_fast_pskip_checkbox')
        self.x264_no_dct_decimate_checkbox = gtk_builder.get_object('x264_no_dct_decimate_checkbox')
        self.x264_no_cabac_checkbox = gtk_builder.get_object('x264_no_cabac_checkbox')

    def reset_settings(self):
        self.__is_widgets_setting_up = True

        self.x264_profile_combobox.set_active(0)
        self.x264_preset_combobox.set_active(0)
        self.x264_level_combobox.set_active(0)
        self.x264_tune_combobox.set_active(0)
        self.x264_crf_radiobutton.set_active(True)
        self.x264_crf_scale.set_value(20.0)
        self.x264_bitrate_spinbutton.set_value(2500)
        self.x264_average_radiobutton.set_active(True)
        self.__reset_advanced_settings_widgets()

        self.__is_widgets_setting_up = False

    def __reset_advanced_settings_widgets(self):
        self.x264_advanced_settings_switch.set_active(False)
        self.x264_vbv_max_rate_spinbutton.set_value(2500)
        self.x264_vbv_bufsize_spinbutton.set_value(2500)
        self.x264_aq_mode_combobox.set_active(0)
        self.x264_aq_strength_spinbutton.set_value(1.0)
        self.x264_ref_spinbutton.set_value(3)
        self.x264_mixed_refs_checkbox.set_active(False)
        self.x264_bframes_spinbutton.set_value(3)
        self.x264_b_adapt_combobox.set_active(0)
        self.x264_b_pyramid_combobox.set_active(0)
        self.x264_weight_p_combobox.set_active(0)
        self.x264_weight_b_checkbox.set_active(False)
        self.x264_keyint_spinbutton.set_value(250)
        self.x264_min_keyint_spinbutton.set_value(25)
        self.x264_me_combobox.set_active(0)
        self.x264_subme_combobox.set_active(0)
        self.x264_me_range_spinbutton.set_value(16)
        self.x264_partitions_auto_radiobutton.set_active(True)
        self.x264_i4x4_checkbox.set_active(False)
        self.x264_i8x8_checkbox.set_active(False)
        self.x264_p4x4_checkbox.set_active(False)
        self.x264_p8x8_checkbox.set_active(False)
        self.x264_b8x8_checkbox.set_active(False)
        self.x264_8x8dct_checkbox.set_active(False)
        self.x264_psy_rd_spinbutton.set_value(1.0)
        self.x264_psy_rd_trellis_spinbutton.set_value(0.0)
        self.x264_trellis_combobox.set_active(0)
        self.x264_direct_combobox.set_active(0)
        self.x264_no_deblock_checkbox.set_active(False)
        self.x264_deblock_alpha_spinbutton.set_value(0)
        self.x264_deblock_beta_spinbutton.set_value(0)
        self.x264_no_fast_pskip_checkbox.set_active(False)
        self.x264_no_dct_decimate_checkbox.set_active(False)
        self.x264_no_cabac_checkbox.set_active(False)

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_x264_settings_widgets(ffmpeg)

    def __setup_x264_settings_widgets(self, ffmpeg):
        video_settings = ffmpeg.video_settings

        if video_settings is not None and video_settings.codec_name == 'libx264':
            self.__is_widgets_setting_up = True

            self.x264_preset_combobox.set_active(video_settings.preset)
            self.x264_profile_combobox.set_active(video_settings.profile)
            self.x264_level_combobox.set_active(video_settings.level)
            self.x264_tune_combobox.set_active(video_settings.tune)
            self.__setup_x264_rate_control_widgets_settings(video_settings)
            self.__setup_x264_advanced_settings_widgets_settings(video_settings)

            self.__is_widgets_setting_up = False
        else:
            self.reset_settings()

    def __setup_x264_rate_control_widgets_settings(self, video_settings):
        if video_settings.crf is not None:
            self.x264_crf_radiobutton.set_active(True)
            self.x264_crf_scale.set_value(video_settings.crf)
        elif video_settings.qp is not None:
            self.x264_qp_radiobutton.set_active(True)
            self.x264_crf_scale.set_value(video_settings.qp)
        else:
            self.x264_bitrate_radiobutton.set_active(True)
            self.x264_bitrate_spinbutton.set_value(video_settings.bitrate)

        if video_settings.constant_bitrate:
            self.x264_constant_radiobutton.set_active(True)
        elif video_settings.encode_pass is not None:
            self.x264_2pass_radiobutton.set_active(True)
        else:
            self.x264_average_radiobutton.set_active(True)

    def __setup_x264_advanced_settings_widgets_settings(self, video_settings):
        self.x264_advanced_settings_switch.set_active(video_settings.advanced_enabled)
        self.x264_vbv_max_rate_spinbutton.set_value(video_settings.vbv_maxrate)
        self.x264_vbv_bufsize_spinbutton.set_value(video_settings.vbv_bufsize)
        self.x264_aq_mode_combobox.set_active(video_settings.aq_mode)
        self.x264_aq_strength_spinbutton.set_value(video_settings.aq_strength)
        self.x264_ref_spinbutton.set_value(video_settings.ref)
        self.x264_mixed_refs_checkbox.set_active(video_settings.mixed_refs)
        self.x264_bframes_spinbutton.set_value(video_settings.bframes)
        self.x264_b_adapt_combobox.set_active(video_settings.b_adapt)
        self.x264_b_pyramid_combobox.set_active(video_settings.b_pyramid)
        self.x264_weight_p_combobox.set_active(video_settings.weightp)
        self.x264_weight_b_checkbox.set_active(video_settings.weightb)
        self.x264_keyint_spinbutton.set_value(video_settings.keyint)
        self.x264_min_keyint_spinbutton.set_value(video_settings.min_keyint)
        self.x264_me_combobox.set_active(video_settings.me)
        self.x264_subme_combobox.set_active(video_settings.subme)
        self.x264_me_range_spinbutton.set_value(video_settings.me_range)
        self.__setup_x264_partitions_widgets_settings(video_settings)
        self.x264_8x8dct_checkbox.set_active(video_settings.dct8x8)
        self.__setup_x264_psy_rd_widgets_settings(video_settings)
        self.x264_trellis_combobox.set_active(video_settings.trellis)
        self.x264_direct_combobox.set_active(video_settings.direct)
        self.__setup_x264_deblock_widgets_settings(video_settings)
        self.x264_no_fast_pskip_checkbox.set_active(video_settings.no_fast_pskip)
        self.x264_no_dct_decimate_checkbox.set_active(video_settings.no_dct_decimate)
        self.x264_no_cabac_checkbox.set_active(video_settings.no_cabac)

    def __setup_x264_partitions_widgets_settings(self, video_settings):
        if video_settings.partitions is not None:
            self.x264_partitions_custom_radiobutton.set_active(True)

            partitions_values = video_settings.partitions

            if partitions_values == 'all':
                self.x264_i4x4_checkbox.set_active(True)
                self.x264_i8x8_checkbox.set_active(True)
                self.x264_p4x4_checkbox.set_active(True)
                self.x264_p8x8_checkbox.set_active(True)
                self.x264_b8x8_checkbox.set_active(True)
            elif partitions_values == 'none':
                self.x264_i4x4_checkbox.set_active(False)
                self.x264_i8x8_checkbox.set_active(False)
                self.x264_p4x4_checkbox.set_active(False)
                self.x264_p8x8_checkbox.set_active(False)
                self.x264_b8x8_checkbox.set_active(False)
            else:
                self.x264_i4x4_checkbox.set_active('i4x4' in partitions_values)
                self.x264_i8x8_checkbox.set_active('i8x8' in partitions_values)
                self.x264_p4x4_checkbox.set_active('p4x4' in partitions_values)
                self.x264_p8x8_checkbox.set_active('p8x8' in partitions_values)
                self.x264_b8x8_checkbox.set_active('b8x8' in partitions_values)
        else:
            self.x264_partitions_auto_radiobutton.set_active(True)
            self.x264_i4x4_checkbox.set_active(False)
            self.x264_i8x8_checkbox.set_active(False)
            self.x264_p4x4_checkbox.set_active(False)
            self.x264_p8x8_checkbox.set_active(False)
            self.x264_b8x8_checkbox.set_active(False)

    def __setup_x264_psy_rd_widgets_settings(self, video_settings):
        psy_rd = video_settings.psy_rd
        psy_rd_value = psy_rd[0]
        psy_rd_trellis_value = psy_rd[1]

        self.x264_psy_rd_spinbutton.set_value(psy_rd_value)
        self.x264_psy_rd_trellis_spinbutton.set_value(psy_rd_trellis_value)

    def __setup_x264_deblock_widgets_settings(self, video_settings):
        if video_settings.no_deblock:
            self.x264_no_deblock_checkbox.set_active(True)
            self.x264_deblock_alpha_spinbutton.set_value(0)
            self.x264_deblock_beta_spinbutton.set_value(0)
        else:
            alpha_value, beta_value = video_settings.deblock

            self.x264_no_deblock_checkbox.set_active(False)
            self.x264_deblock_alpha_spinbutton.set_value(alpha_value)
            self.x264_deblock_beta_spinbutton.set_value(beta_value)

    def get_settings(self, ffmpeg):
        video_settings = X264()
        video_settings.preset = self.x264_preset_combobox.get_active()
        video_settings.profile = self.x264_profile_combobox.get_active()
        video_settings.level = self.x264_level_combobox.get_active()
        video_settings.tune = self.x264_tune_combobox.get_active()

        self.__set_rate_control_settings_from_x264_widgets(video_settings)
        self.__set_advanced_settings_from_x264_widgets(video_settings)

        ffmpeg.video_settings = video_settings

    def __set_rate_control_settings_from_x264_widgets(self, video_settings):
        if self.x264_crf_radiobutton.get_active():
            video_settings.crf = self.x264_crf_scale.get_value()
        elif self.x264_qp_radiobutton.get_active():
            video_settings.qp = self.x264_crf_scale.get_value()
        else:
            video_settings.bitrate = self.x264_bitrate_spinbutton.get_value_as_int()

            if self.x264_constant_radiobutton.get_active():
                video_settings.constant_bitrate = True
            else:

                if self.x264_2pass_radiobutton.get_active():
                    video_settings.encode_pass = 1

                video_settings.vbv_maxrate = self.x264_vbv_max_rate_spinbutton.get_value_as_int()
                video_settings.vbv_bufsize = self.x264_vbv_bufsize_spinbutton.get_value_as_int()

    def __set_advanced_settings_from_x264_widgets(self, video_settings):
        if self.x264_advanced_settings_switch.get_active():
            video_settings.advanced_enabled = True
            video_settings.aq_mode = self.x264_aq_mode_combobox.get_active()
            video_settings.b_adapt = self.x264_b_adapt_combobox.get_active()
            video_settings.b_pyramid = self.x264_b_pyramid_combobox.get_active()
            video_settings.weightp = self.x264_weight_p_combobox.get_active()
            video_settings.me = self.x264_subme_combobox.get_active()
            video_settings.subme = self.x264_subme_combobox.get_active()
            video_settings.trellis = self.x264_trellis_combobox.get_active()
            video_settings.direct = self.x264_direct_combobox.get_active()
            aq_strength_value = round(self.x264_aq_strength_spinbutton.get_value(), 1)
            video_settings.aq_strength = aq_strength_value
            video_settings.ref = self.x264_ref_spinbutton.get_value_as_int()
            video_settings.mixed_refs = self.x264_mixed_refs_checkbox.get_active()
            video_settings.bframes = self.x264_bframes_spinbutton.get_value_as_int()
            video_settings.weightb = self.x264_weight_b_checkbox.get_active()
            video_settings.keyint = self.x264_keyint_spinbutton.get_value_as_int()
            video_settings.min_keyint = self.x264_min_keyint_spinbutton.get_value_as_int()
            video_settings.me_range = self.x264_me_range_spinbutton.get_value_as_int()
            video_settings.dct8x8 = self.x264_8x8dct_checkbox.get_active()
            psy_rd_value = round(self.x264_psy_rd_spinbutton.get_value(), 1)
            psy_rd_trellis_value = round(self.x264_psy_rd_trellis_spinbutton.get_value(), 2)
            video_settings.psy_rd = (psy_rd_value, psy_rd_trellis_value)
            video_settings.no_fast_pskip = self.x264_no_fast_pskip_checkbox.get_active()
            video_settings.no_dct_decimate = self.x264_no_dct_decimate_checkbox.get_active()
            video_settings.no_cabac = self.x264_no_cabac_checkbox.get_active()

            self.__set_deblock_settings_from_x264_widgets(video_settings)
            self.__set_partitions_settings_from_x264_widgets(video_settings)

    def __set_deblock_settings_from_x264_widgets(self, video_settings):
        if self.x264_no_deblock_checkbox.get_active():
            video_settings.no_deblock = True
            video_settings.deblock = None
        else:
            video_settings.no_deblock = False
            video_settings.deblock = (self.x264_deblock_alpha_spinbutton.get_value_as_int(),
                                      self.x264_deblock_beta_spinbutton.get_value_as_int())

    def __set_partitions_settings_from_x264_widgets(self, video_settings):
        if self.x264_partitions_custom_radiobutton.get_active():
            partitions_settings = []

            if self.x264_i4x4_checkbox.get_active():
                partitions_settings.append('i4x4')

            if self.x264_i8x8_checkbox.get_active():
                partitions_settings.append('i8x8')

            if self.x264_p4x4_checkbox.get_active():
                partitions_settings.append('p4x4')

            if self.x264_p8x8_checkbox.get_active():
                partitions_settings.append('p8x8')

            if self.x264_b8x8_checkbox.get_active():
                partitions_settings.append('b8x8')

            if not partitions_settings:
                video_settings.partitions = 'none'
            elif len(partitions_settings) == 5:
                video_settings.partitions = 'all'
            else:
                video_settings.partitions = partitions_settings

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def on_x264_crf_radiobutton_clicked(self, crf_radiobutton):
        if not crf_radiobutton.get_active():
            return

        self.__set_crf_state()

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = self.x264_crf_scale.get_value()
            ffmpeg.video_settings.advanced_enabled = self.x264_advanced_settings_switch.get_active()
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __set_crf_state(self):
        self.x264_rate_type_stack.set_visible_child(self.x264_crf_scale)
        self.x264_vbv_max_rate_spinbutton.set_sensitive(False)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(False)

    def on_x264_qp_radiobutton_clicked(self, qp_radiobutton):
        if not qp_radiobutton.get_active():
            return

        self.__set_crf_state()

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = self.x264_crf_scale.get_value()
            ffmpeg.video_settings.advanced_enabled = self.x264_advanced_settings_switch.get_active()
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bitrate_radiobutton_clicked(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.x264_rate_type_stack.set_visible_child(self.x264_bitrate_box)
        self.on_x264_average_radiobutton_toggled(self.x264_average_radiobutton)
        self.on_x264_constant_radiobutton_toggled(self.x264_constant_radiobutton)
        self.on_x264_2pass_radiobutton_toggled(self.x264_2pass_radiobutton)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.x264_bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_average_radiobutton_toggled(self, average_radiobutton):
        if not average_radiobutton.get_active():
            return

        self.x264_vbv_max_rate_spinbutton.set_sensitive(True)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(True)

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x264_advanced_settings_switch.get_active()
        bitrate_value = self.x264_bitrate_spinbutton.get_value_as_int()

        if advanced_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = None

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_vbr_widgets(self, bitrate_value):
        if bitrate_value > self.x264_vbv_max_rate_spinbutton.get_value_as_int():
            self.x264_vbv_max_rate_spinbutton.set_value(bitrate_value)
        else:
            self.on_x264_vbv_max_rate_spinbutton_value_changed(self.x264_vbv_max_rate_spinbutton)

        self.on_x264_vbv_bufsize_spinbutton_value_changed(self.x264_vbv_bufsize_spinbutton)

    def on_x264_constant_radiobutton_toggled(self, constant_radiobutton):
        if not constant_radiobutton.get_active():
            return

        self.x264_vbv_max_rate_spinbutton.set_sensitive(False)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(False)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.constant_bitrate = True
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_2pass_radiobutton_toggled(self, dual_pass_radiobutton):
        if not dual_pass_radiobutton.get_active():
            return

        self.x264_vbv_max_rate_spinbutton.set_sensitive(True)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(True)

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x264_advanced_settings_switch.get_active()
        bitrate_value = self.x264_bitrate_spinbutton.get_value_as_int()

        if advanced_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = 1
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'
            ffmpeg.video_settings.constant_bitrate = None

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_preset_combobox_changed(self, preset_combobox):
        if self.__is_widgets_setting_up:
            return

        preset_index = preset_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.preset = preset_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_profile_combobox_changed(self, profile_combobox):
        if self.__is_widgets_setting_up:
            return

        profile_index = profile_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.profile = profile_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_level_combobox_changed(self, level_combobox):
        if self.__is_widgets_setting_up:
            return

        level_index = level_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.level = level_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_tune_combobox_changed(self, tune_combobox):
        if self.__is_widgets_setting_up:
            return

        tune_index = tune_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.tune = tune_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_crf_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        quantizer_value = self.x264_crf_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            if self.x264_crf_radiobutton.get_active():
                ffmpeg.video_settings.crf = quantizer_value
            else:
                ffmpeg.video_settings.qp = quantizer_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        vbr_enabled = self.x264_average_radiobutton.get_active() or self.x264_2pass_radiobutton.get_active()
        bitrate_value = bitrate_spinbutton.get_value_as_int()

        if vbr_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        self.x264_advanced_settings_revealer.set_reveal_child(advanced_settings_switch.get_active())

        if self.__is_widgets_setting_up:
            return

        threading.Thread(target=self.__update_settings, args=()).start()

    def __update_settings(self):
        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            self.get_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)

        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def on_x264_vbv_max_rate_spinbutton_value_changed(self, vbv_maxrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x264_advanced_settings_switch.get_active()
        bitrate_value = self.x264_bitrate_spinbutton.get_value_as_int()

        if not advanced_enabled:
            return

        if self.__fix_vbv_maxrate_widgets(bitrate_value):
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_maxrate = vbv_maxrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __fix_vbv_maxrate_widgets(self, bitrate_value):
        if bitrate_value > self.x264_vbv_max_rate_spinbutton.get_value_as_int():
            self.x264_vbv_max_rate_spinbutton.set_value(bitrate_value)

            return True

        return False

    def on_x264_vbv_bufsize_spinbutton_value_changed(self, vbv_bufsize_spinbutton):
        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x264_advanced_settings_switch.get_active()

        if not advanced_enabled:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_bufsize = vbv_bufsize_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_aq_mode_combobox_changed(self, aq_mode_spinbutton):
        if self.__is_widgets_setting_up:
            return

        aq_mode_index = aq_mode_spinbutton.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_mode = aq_mode_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_aq_strength_spinbutton_value_changed(self, aq_strength_spinbutton):
        if self.__is_widgets_setting_up:
            return

        aq_strength_value = round(aq_strength_spinbutton.get_value(), 1)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_strength = aq_strength_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_reference_frames_spinbutton_value_changed(self, ref_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.ref = ref_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_mixed_refs_checkbox_toggled(self, mixed_refs_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.mixed_refs = mixed_refs_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bframes_spinbutton_value_changed(self, bframes_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bframes = bframes_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_badapt_combobox_changed(self, b_adapt_combobox):
        if self.__is_widgets_setting_up:
            return

        b_adapt_index = b_adapt_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_adapt = b_adapt_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_bpyramid_combobox_changed(self, b_pyramid_combobox):
        if self.__is_widgets_setting_up:
            return

        b_pyramid_index = b_pyramid_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_pyramid = b_pyramid_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_weight_p_combobox_changed(self, weight_p_combobox):
        if self.__is_widgets_setting_up:
            return

        weight_p_index = weight_p_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.weightp = weight_p_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_weight_b_checkbox_toggled(self, weight_b_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.weightb = weight_b_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_keyframe_interval_spinbutton_value_changed(self, keyint_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.keyint = keyint_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_min_keyframe_interval_spinbutton_value_changed(self, min_keyint_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.min_keyint = min_keyint_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_motion_estimation_combobox_changed(self, me_combobox):
        if self.__is_widgets_setting_up:
            return

        me_index = me_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.me = me_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_sub_motion_estimation_combobox_changed(self, subme_combobox):
        if self.__is_widgets_setting_up:
            return

        subme_index = subme_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.subme = subme_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_me_range_spinbutton_value_changed(self, me_range_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.me_range = me_range_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_partitions_auto_radiobutton_toggled(self, partitions_auto_radiobutton):
        if not partitions_auto_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_partitions_custom_radiobutton_toggled(self, partitions_custom_radiobutton):
        self.x264_partitions_types_grid.set_sensitive(partitions_custom_radiobutton.get_active())

        if not partitions_custom_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        partitions_setting = self.__get_partitions_settings_from_x264_widgets()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = partitions_setting

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __get_partitions_settings_from_x264_widgets(self):
        partitions = []
        i4x4 = self.x264_i4x4_checkbox.get_active()
        i8x8 = self.x264_i8x8_checkbox.get_active()
        p4x4 = self.x264_p4x4_checkbox.get_active()
        p8x8 = self.x264_p8x8_checkbox.get_active()
        b8x8 = self.x264_b8x8_checkbox.get_active()

        if not (i4x4 or i8x8 or p4x4 or p8x8 or b8x8):
            partitions = 'none'
        elif i4x4 and i8x8 and p4x4 and p8x8 and b8x8:
            partitions = 'all'
        else:

            if self.x264_i4x4_checkbox.get_active():
                partitions.append('i4x4')

            if self.x264_i8x8_checkbox.get_active():
                partitions.append('i8x8')

            if self.x264_p4x4_checkbox.get_active():
                partitions.append('p4x4')

            if self.x264_p8x8_checkbox.get_active():
                partitions.append('p8x8')

            if self.x264_b8x8_checkbox.get_active():
                partitions.append('b8x8')

        return partitions

    def on_x264_partitions_type_checkbox_toggled(self, partitions_type_checkbox):
        if self.__is_widgets_setting_up:
            return

        partitions_setting = self.__get_partitions_settings_from_x264_widgets()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = partitions_setting

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_8x8dct_checkbox_toggled(self, dct8x8_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dct8x8 = dct8x8_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_psy_rd_spinbutton_value_changed(self, psy_rd_spinbutton):
        if self.__is_widgets_setting_up:
            return

        psy_rd_value = round(psy_rd_spinbutton.get_value(), 1)
        psy_rd_trellis_value = round(self.x264_psy_rd_trellis_spinbutton.get_value(), 2)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rd = psy_rd_value, psy_rd_trellis_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_psy_rd_trellis_spinbutton_value_changed(self, psy_rd_trellis_spinbutton):
        if self.__is_widgets_setting_up:
            return

        psy_rd_value = round(self.x264_psy_rd_spinbutton.get_value(), 1)
        psy_rd_trellis_value = round(psy_rd_trellis_spinbutton.get_value(), 2)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rd = psy_rd_value, psy_rd_trellis_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_trellis_combobox_changed(self, trellis_combobox):
        if self.__is_widgets_setting_up:
            return

        trellis_index = trellis_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.trellis = trellis_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_direct_combobox_changed(self, direct_combobox):
        if self.__is_widgets_setting_up:
            return

        direct_index = direct_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.direct = direct_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_no_deblock_checkbox_toggled(self, no_deblock_checkbox):
        self.x264_deblock_alpha_spinbutton.set_sensitive(not no_deblock_checkbox.get_active())
        self.x264_deblock_beta_spinbutton.set_sensitive(not no_deblock_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x264_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_deblock = no_deblock_enabled
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __get_deblock_settings_from_x264_widgets(self, no_deblock_enabled):
        if no_deblock_enabled:
            return None

        alpha_value = self.x264_deblock_alpha_spinbutton.get_value_as_int()
        beta_value = self.x264_deblock_beta_spinbutton.get_value_as_int()

        return alpha_value, beta_value

    def on_x264_deblock_alpha_spinbutton_value_changed(self, deblock_alpha_spinbutton):
        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = self.x264_no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x264_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_deblock_beta_spinbutton_value_changed(self, deblock_beta_spinbutton):
        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = self.x264_no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x264_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_no_fast_pskip_checkbox_toggled(self, no_fast_pskip_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_fast_pskip = no_fast_pskip_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_no_dct_decimate_checkbox_toggled(self, no_dct_decimate_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_dct_decimate = no_dct_decimate_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_no_cabac_checkbox_toggled(self, no_cabac_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_cabac = no_cabac_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
