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

from render_watch.ffmpeg.x265 import X265
from render_watch.startup import GLib


class X265Handlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.__is_widgets_setting_up = False
        self.inputs_page_handlers = None
        self.x265_crf_radiobutton = gtk_builder.get_object('x265_crf_radiobutton')
        self.x265_qp_radio_button = gtk_builder.get_object('x265_qp_radiobutton')
        self.x265_bitrate_radiobutton = gtk_builder.get_object('x265_bitrate_radiobutton')
        self.x265_rate_type_stack = gtk_builder.get_object('x265_rate_type_stack')
        self.x265_crf_scale = gtk_builder.get_object('x265_crf_scale')
        self.x265_bitrate_box = gtk_builder.get_object('x265_bitrate_box')
        self.x265_2pass_radiobutton = gtk_builder.get_object('x265_2pass_radiobutton')
        self.x265_average_radiobutton = gtk_builder.get_object('x265_average_radiobutton')
        self.x265_bitrate_spinbutton = gtk_builder.get_object('x265_bitrate_spinbutton')
        self.x265_preset_combobox = gtk_builder.get_object('x265_preset_combobox')
        self.x265_profile_combobox = gtk_builder.get_object('x265_profile_combobox')
        self.x265_level_combobox = gtk_builder.get_object('x265_level_combobox')
        self.x265_tune_combobox = gtk_builder.get_object('x265_tune_combobox')
        self.x265_advanced_settings_switch = gtk_builder.get_object('x265_advanced_settings_switch')
        self.x265_advanced_settings_revealer = gtk_builder.get_object('x265_advanced_settings_revealer')
        self.x265_vbv_maxrate_spinbutton = gtk_builder.get_object('x265_vbv_maxrate_spinbutton')
        self.x265_vbv_bufsize_spinbutton = gtk_builder.get_object('x265_vbv_bufsize_spinbutton')
        self.x265_aq_mode_combobox = gtk_builder.get_object('x265_aq_mode_combobox')
        self.x265_aq_strength_spinbutton = gtk_builder.get_object('x265_aq_strength_spinbutton')
        self.x265_hevc_aq_checkbox = gtk_builder.get_object('x265_hevc_aq_checkbox')
        self.x265_keyint_spinbutton = gtk_builder.get_object('x265_keyint_spinbutton')
        self.x265_min_keyint_spinbutton = gtk_builder.get_object('x265_min_keyint_spinbutton')
        self.x265_ref_spinbutton = gtk_builder.get_object('x265_ref_spinbutton')
        self.x265_bframes_spinbutton = gtk_builder.get_object('x265_bframes_spinbutton')
        self.x265_b_adapt_combobox = gtk_builder.get_object('x265_badapt_combobox')
        self.x265_no_bpyramid_checkbox = gtk_builder.get_object('x265_no_bpyramid_checkbox')
        self.x265_b_intra_checkbox = gtk_builder.get_object('x265_b_intra_checkbox')
        self.x265_closed_gop_checkbox = gtk_builder.get_object('x265_closed_gop_checkbox')
        self.x265_rc_lookahead_spinbutton = gtk_builder.get_object('x265_rc_lookahead_spinbutton')
        self.x265_no_scenecut_checkbox = gtk_builder.get_object('x265_no_scenecut_checkbox')
        self.x265_no_high_tier_checkbox = gtk_builder.get_object('x265_no_high_tier_checkbox')
        self.x265_psy_rd_spinbutton = gtk_builder.get_object('x265_psyrd_spinbutton')
        self.x265_psy_rdoq_spinbutton = gtk_builder.get_object('x265_psyrdoq_spinbutton')
        self.x265_me_combobox = gtk_builder.get_object('x265_me_combobox')
        self.x265_subme_spinbutton = gtk_builder.get_object('x265_subme_spinbutton')
        self.x265_weightb_checkbox = gtk_builder.get_object('x265_weightb_checkbox')
        self.x265_no_weightp_checkbox = gtk_builder.get_object('x265_no_weightp_checkbox')
        self.x265_no_deblock_checkbox = gtk_builder.get_object('x265_no_deblock_checkbox')
        self.x265_deblock_alpha_spinbutton = gtk_builder.get_object('x265_deblock_alpha_spinbutton')
        self.x265_deblock_beta_spinbutton = gtk_builder.get_object('x265_deblock_beta_spinbutton')
        self.x265_sao_checkbox = gtk_builder.get_object('x265_sao_checkbox')
        self.x265_sao_options_box = gtk_builder.get_object('x265_sao_options_box')
        self.x265_sao_nodeblock_checkbox = gtk_builder.get_object('x265_sao_nodeblock_checkbox')
        self.x265_sao_limit_checkbox = gtk_builder.get_object('x265_sao_limit_checkbox')
        self.x265_sao_selective_spinbutton = gtk_builder.get_object('x265_sao_selective_spinbutton')
        self.x265_rdo_level_spinbutton = gtk_builder.get_object('x265_rdo_level_spinbutton')
        self.x265_rdoq_level_combobox = gtk_builder.get_object('x265_rdoq_level_combobox')
        self.x265_rd_refine_checkbox = gtk_builder.get_object('x265_rd_refine_checkbox')
        self.x265_max_cu_combobox = gtk_builder.get_object('x265_max_cu_combobox')
        self.x265_min_cu_combobox = gtk_builder.get_object('x265_min_cu_combobox')
        self.x265_rect_checkbox = gtk_builder.get_object('x265_rect_checkbox')
        self.x265_amp_checkbox = gtk_builder.get_object('x265_amp_checkbox')
        self.x265_wpp_checkbox = gtk_builder.get_object('x265_wpp_checkbox')
        self.x265_pmode_checkbox = gtk_builder.get_object('x265_pmode_checkbox')
        self.x265_pme_checkbox = gtk_builder.get_object('x265_pme_checkbox')
        self.x265_uhd_bluray_checkbox = gtk_builder.get_object('x265_uhd_bluray_checkbox')

    def reset_settings(self):
        self.__is_widgets_setting_up = True

        self.x265_profile_combobox.set_active(0)
        self.x265_preset_combobox.set_active(0)
        self.x265_level_combobox.set_active(0)
        self.x265_tune_combobox.set_active(0)
        self.x265_crf_radiobutton.set_active(True)
        self.x265_crf_scale.set_value(20.0)
        self.__reset_advanced_settings_widgets()

        self.__is_widgets_setting_up = False

    def __reset_advanced_settings_widgets(self):
        self.x265_advanced_settings_switch.set_active(False)
        self.x265_vbv_maxrate_spinbutton.set_value(2500)
        self.x265_vbv_bufsize_spinbutton.set_value(2500)
        self.x265_aq_mode_combobox.set_active(0)
        self.x265_aq_strength_spinbutton.set_value(1.0)
        self.x265_hevc_aq_checkbox.set_active(False)
        self.x265_keyint_spinbutton.set_value(250)
        self.x265_min_keyint_spinbutton.set_value(0)
        self.x265_ref_spinbutton.set_value(3)
        self.x265_bframes_spinbutton.set_value(4)
        self.x265_b_adapt_combobox.set_active(0)
        self.x265_no_bpyramid_checkbox.set_active(False)
        self.x265_b_intra_checkbox.set_active(False)
        self.x265_closed_gop_checkbox.set_active(False)
        self.x265_rc_lookahead_spinbutton.set_value(20)
        self.x265_no_scenecut_checkbox.set_active(False)
        self.x265_no_high_tier_checkbox.set_active(False)
        self.x265_psy_rd_spinbutton.set_value(2.0)
        self.x265_psy_rdoq_spinbutton.set_value(0.0)
        self.x265_me_combobox.set_active(0)
        self.x265_subme_spinbutton.set_value(2)
        self.x265_weightb_checkbox.set_active(False)
        self.x265_no_weightp_checkbox.set_active(False)
        self.x265_no_deblock_checkbox.set_active(False)
        self.x265_deblock_alpha_spinbutton.set_value(0)
        self.x265_deblock_beta_spinbutton.set_value(0)
        self.x265_sao_checkbox.set_active(True)
        self.x265_sao_nodeblock_checkbox.set_active(False)
        self.x265_sao_limit_checkbox.set_active(False)
        self.x265_sao_selective_spinbutton.set_value(0)
        self.x265_rdo_level_spinbutton.set_value(3)
        self.x265_rdoq_level_combobox.set_active(0)
        self.x265_rd_refine_checkbox.set_active(False)
        self.x265_max_cu_combobox.set_active(0)
        self.x265_min_cu_combobox.set_active(0)
        self.x265_rect_checkbox.set_active(False)
        self.x265_amp_checkbox.set_active(False)
        self.x265_wpp_checkbox.set_active(False)
        self.x265_pmode_checkbox.set_active(False)
        self.x265_pme_checkbox.set_active(False)
        self.x265_uhd_bluray_checkbox.set_active(False)

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_x265_settings_widgets(ffmpeg)

    def __setup_x265_settings_widgets(self, ffmpeg):
        video_settings = ffmpeg.video_settings

        if video_settings is not None and video_settings.codec_name == 'libx265':
            self.__is_widgets_setting_up = True

            self.x265_preset_combobox.set_active(video_settings.preset)
            self.x265_profile_combobox.set_active(video_settings.profile)
            self.x265_level_combobox.set_active(video_settings.level)
            self.x265_tune_combobox.set_active(video_settings.tune)
            self.__setup_x265_rate_control_widgets_settings(video_settings)
            self.__setup_x265_encode_pass_widgets_settings(video_settings)
            self.__setup_x265_advanced_settings_widgets_settings(video_settings)

            self.__is_widgets_setting_up = False
        else:
            self.reset_settings()

    def __setup_x265_rate_control_widgets_settings(self, video_settings):
        if video_settings.crf is not None:
            self.x265_crf_radiobutton.set_active(True)
            self.x265_crf_scale.set_value(video_settings.crf)
        elif video_settings.qp is not None:
            self.x265_qp_radio_button.set_active(True)
            self.x265_crf_scale.set_value(video_settings.qp)
        else:
            self.x265_bitrate_radiobutton.set_active(True)
            self.x265_bitrate_spinbutton.set_value(video_settings.bitrate)

    def __setup_x265_encode_pass_widgets_settings(self, video_settings):
        if video_settings.encode_pass is not None:
            self.x265_2pass_radiobutton.set_active(True)
        else:
            self.x265_average_radiobutton.set_active(True)

    def __setup_x265_advanced_settings_widgets_settings(self, video_settings):
        self.x265_advanced_settings_switch.set_active(video_settings.advanced_enabled)
        self.x265_vbv_maxrate_spinbutton.set_value(video_settings.vbv_maxrate)
        self.x265_vbv_bufsize_spinbutton.set_value(video_settings.vbv_bufsize)
        self.x265_aq_mode_combobox.set_active(video_settings.aq_mode)
        self.x265_aq_strength_spinbutton.set_value(video_settings.aq_strength)
        self.x265_hevc_aq_checkbox.set_active(video_settings.hevc_aq)
        self.x265_keyint_spinbutton.set_value(video_settings.keyint)
        self.x265_min_keyint_spinbutton.set_value(video_settings.min_keyint)
        self.x265_ref_spinbutton.set_value(video_settings.ref)
        self.x265_bframes_spinbutton.set_value(video_settings.bframes)
        self.x265_b_adapt_combobox.set_active(video_settings.b_adapt)
        self.x265_no_bpyramid_checkbox.set_active(video_settings.no_b_pyramid)
        self.x265_b_intra_checkbox.set_active(video_settings.b_intra)
        self.x265_closed_gop_checkbox.set_active(video_settings.no_open_gop)
        self.x265_rc_lookahead_spinbutton.set_value(video_settings.rc_lookahead)
        self.x265_no_scenecut_checkbox.set_active(video_settings.no_scenecut)
        self.x265_no_high_tier_checkbox.set_active(video_settings.no_high_tier)
        self.x265_psy_rd_spinbutton.set_value(video_settings.psy_rd)
        self.x265_psy_rdoq_spinbutton.set_value(video_settings.psy_rdoq)
        self.x265_me_combobox.set_active(video_settings.me)
        self.x265_subme_spinbutton.set_value(video_settings.subme)
        self.x265_weightb_checkbox.set_active(video_settings.weightb)
        self.x265_no_weightp_checkbox.set_active(video_settings.no_weightp)
        self.__setup_x265_deblock_widgets_settings(video_settings)
        self.__setup_sao_widgets_settings(video_settings)
        self.x265_rdo_level_spinbutton.set_value(video_settings.rd)
        self.x265_rdoq_level_combobox.set_active(video_settings.rdoq_level)
        self.x265_rd_refine_checkbox.set_active(video_settings.rd_refine)
        self.x265_max_cu_combobox.set_active(video_settings.ctu)
        self.x265_min_cu_combobox.set_active(video_settings.min_cu_size)
        self.x265_rect_checkbox.set_active(video_settings.rect)
        self.x265_amp_checkbox.set_active(video_settings.amp)
        self.x265_wpp_checkbox.set_active(video_settings.wpp)
        self.x265_pmode_checkbox.set_active(video_settings.pmode)
        self.x265_pme_checkbox.set_active(video_settings.pme)
        self.x265_uhd_bluray_checkbox.set_active(video_settings.uhd_bd)

    def __setup_x265_deblock_widgets_settings(self, video_settings):
        if video_settings.no_deblock:
            self.x265_no_deblock_checkbox.set_active(True)
            self.x265_deblock_alpha_spinbutton.set_value(0)
            self.x265_deblock_beta_spinbutton.set_value(0)
        else:
            alpha_value, beta_value = video_settings.deblock

            self.x265_no_deblock_checkbox.set_active(False)
            self.x265_deblock_alpha_spinbutton.set_value(alpha_value)
            self.x265_deblock_beta_spinbutton.set_value(beta_value)

    def __setup_sao_widgets_settings(self, video_settings):
        if not video_settings.no_sao:
            self.x265_sao_checkbox.set_active(True)
            self.x265_sao_nodeblock_checkbox.set_active(video_settings.sao_non_deblock)
            self.x265_sao_limit_checkbox.set_active(video_settings.limit_sao)
        else:
            self.x265_sao_checkbox.set_active(False)
            self.x265_sao_nodeblock_checkbox.set_active(False)
            self.x265_sao_limit_checkbox.set_active(False)

        self.x265_sao_selective_spinbutton.set_value(video_settings.selective_sao)

    def get_settings(self, ffmpeg):
        video_settings = X265()
        video_settings.preset = self.x265_preset_combobox.get_active()
        video_settings.profile = self.x265_profile_combobox.get_active()
        video_settings.level = self.x265_level_combobox.get_active()
        video_settings.tune = self.x265_tune_combobox.get_active()
        video_settings.aq_mode = self.x265_aq_mode_combobox.get_active()
        video_settings.b_adapt = self.x265_b_adapt_combobox.get_active()
        video_settings.me = self.x265_me_combobox.get_active()
        video_settings.rdoq_level = self.x265_rdoq_level_combobox.get_active()
        video_settings.ctu = self.x265_max_cu_combobox.get_active()
        video_settings.min_cu_size = self.x265_min_cu_combobox.get_active()

        self.__set_rate_control_settings_from_x265_widgets(video_settings)
        self.__set_advanced_settings_from_x265_widgets(video_settings)

        ffmpeg.video_settings = video_settings

    def __set_rate_control_settings_from_x265_widgets(self, video_settings):
        if self.x265_crf_radiobutton.get_active():
            video_settings.crf = self.x265_crf_scale.get_value()
        elif self.x265_qp_radio_button.get_active():
            video_settings.qp = self.x265_crf_scale.get_value()
        else:
            video_settings.bitrate = self.x265_bitrate_spinbutton.get_value_as_int()

            if self.x265_2pass_radiobutton.get_active():
                video_settings.encode_pass = 1

            video_settings.vbv_maxrate = self.x265_vbv_maxrate_spinbutton.get_value_as_int()
            video_settings.vbv_bufsize = self.x265_vbv_bufsize_spinbutton.get_value_as_int()

    def __set_advanced_settings_from_x265_widgets(self, video_settings):
        if self.x265_advanced_settings_switch.get_active():
            video_settings.advanced_enabled = True
            video_settings.aq_strength = self.x265_aq_strength_spinbutton.get_value()
            video_settings.hevc_aq = self.x265_hevc_aq_checkbox.get_active()
            video_settings.keyint = self.x265_keyint_spinbutton.get_value_as_int()
            video_settings.min_keyint = self.x265_min_keyint_spinbutton.get_value_as_int()
            video_settings.ref = self.x265_ref_spinbutton.get_value_as_int()
            video_settings.bframes = self.x265_bframes_spinbutton.get_value_as_int()
            video_settings.no_b_pyramid = self.x265_no_bpyramid_checkbox.get_active()
            video_settings.b_intra = self.x265_b_intra_checkbox.get_active()
            video_settings.no_open_gop = self.x265_closed_gop_checkbox.get_active()
            video_settings.rc_lookahead = self.x265_rc_lookahead_spinbutton.get_value_as_int()
            video_settings.no_scenecut = self.x265_no_scenecut_checkbox.get_active()
            video_settings.no_high_tier = self.x265_no_high_tier_checkbox.get_active()
            video_settings.psy_rd = self.x265_psy_rd_spinbutton.get_value()
            video_settings.psy_rdoq = self.x265_psy_rdoq_spinbutton.get_value()
            video_settings.subme = self.x265_subme_spinbutton.get_value_as_int()
            video_settings.weightb = self.x265_weightb_checkbox.get_active()
            video_settings.no_weightp = self.x265_no_weightp_checkbox.get_active()
            video_settings.rd = self.x265_rdo_level_spinbutton.get_value_as_int()
            video_settings.rd_refine = self.x265_rd_refine_checkbox.get_active()
            video_settings.rect = self.x265_rect_checkbox.get_active()
            video_settings.amp = self.x265_amp_checkbox.get_active()
            video_settings.wpp = self.x265_wpp_checkbox.get_active()
            video_settings.pmode = self.x265_pmode_checkbox.get_active()
            video_settings.pme = self.x265_pme_checkbox.get_active()
            video_settings.uhd_bd = self.x265_uhd_bluray_checkbox.get_active()

            self.__set_deblock_settings_from_x265_widgets(video_settings)
            self.__set_sao_settings_from_x265_widgets(video_settings)

    def __set_deblock_settings_from_x265_widgets(self, video_settings):
        if self.x265_no_deblock_checkbox.get_active():
            video_settings.no_deblock = True
            video_settings.deblock = None
        else:
            video_settings.no_deblock = False
            alpha_value = self.x265_deblock_alpha_spinbutton.get_value_as_int()
            beta_value = self.x265_deblock_beta_spinbutton.get_value_as_int()
            video_settings.deblock = (alpha_value, beta_value)

    def __set_sao_settings_from_x265_widgets(self, video_settings):
        if not self.x265_sao_checkbox.get_active():
            video_settings.no_sao = True
            video_settings.sao_non_deblock = False
            video_settings.limit_sao = False
            video_settings.selective_sao = None
        else:
            video_settings.no_sao = False
            video_settings.sao_non_deblock = self.x265_sao_nodeblock_checkbox.get_active()
            video_settings.limit_sao = self.x265_sao_limit_checkbox.get_active()
            video_settings.selective_sao = self.x265_sao_selective_spinbutton.get_value_as_int()

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def on_x265_crf_radiobutton_clicked(self, crf_radiobutton):
        if not crf_radiobutton.get_active():
            return

        self.__set_crf_state()

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.crf = self.x265_crf_scale.get_value()
            ffmpeg.video_settings.advanced_enabled = self.x265_advanced_settings_switch.get_active()
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __set_crf_state(self):
        self.x265_rate_type_stack.set_visible_child(self.x265_crf_scale)
        self.x265_vbv_maxrate_spinbutton.set_sensitive(False)
        self.x265_vbv_bufsize_spinbutton.set_sensitive(False)

    def on_x265_qp_radiobutton_clicked(self, qp_radiobutton):
        if not qp_radiobutton.get_active():
            return

        self.__set_crf_state()

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = self.x265_crf_scale.get_value()
            ffmpeg.video_settings.advanced_enabled = self.x265_advanced_settings_switch.get_active()
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None
            ffmpeg.video_settings.vbv_maxrate = None
            ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_bitrate_radiobutton_clicked(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.__set_bitrate_state()

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x265_advanced_settings_switch.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.x265_bitrate_spinbutton.get_value_as_int()

            if advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = self.x265_vbv_maxrate_spinbutton.get_value_as_int()
                ffmpeg.video_settings.vbv_bufsize = self.x265_vbv_bufsize_spinbutton.get_value_as_int()
            else:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __set_bitrate_state(self):
        self.x265_rate_type_stack.set_visible_child(self.x265_bitrate_box)
        self.x265_vbv_maxrate_spinbutton.set_sensitive(True)
        self.x265_vbv_bufsize_spinbutton.set_sensitive(True)

    def on_x265_preset_combobox_changed(self, preset_combobox):
        if self.__is_widgets_setting_up:
            return

        preset_index = preset_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.preset = preset_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_profile_combobox_changed(self, profile_combobox):
        if self.__is_widgets_setting_up:
            return

        profile_index = profile_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.profile = profile_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_level_combobox_changed(self, level_combobox):
        if self.__is_widgets_setting_up:
            return

        level_index = level_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.level = level_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_tune_combobox_changed(self, tune_combobox):
        if self.__is_widgets_setting_up:
            return

        tune_index = tune_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.tune = tune_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_crf_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            quantizer_value = self.x265_crf_scale.get_value()

            if self.x265_crf_radiobutton.get_active():
                ffmpeg.video_settings.crf = quantizer_value
            else:
                ffmpeg.video_settings.qp = quantizer_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        vbr_enabled = self.x265_average_radiobutton.get_active() or self.x265_2pass_radiobutton.get_active()
        bitrate_value = bitrate_spinbutton.get_value_as_int()

        if vbr_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_average_radiobutton_toggled(self, average_bitrate_radiobutton):
        if not average_bitrate_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x265_advanced_settings_switch.get_active()
        bitrate_value = self.x265_bitrate_spinbutton.get_value_as_int()

        if advanced_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = None
            ffmpeg.video_settings.stats = None

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __update_vbr_widgets(self, bitrate_value):
        if bitrate_value > self.x265_vbv_maxrate_spinbutton.get_value_as_int():
            self.x265_vbv_maxrate_spinbutton.set_value(bitrate_value)
        else:
            self.on_x265_vbv_maxrate_spinbutton_value_changed(self.x265_vbv_maxrate_spinbutton)

        self.on_x265_vbv_bufsize_spinbutton_value_changed(self.x265_vbv_bufsize_spinbutton)

    def on_x265_2pass_radiobutton_toggled(self, dual_pass_bitrate_radiobutton):
        if not dual_pass_bitrate_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x265_advanced_settings_switch.get_active()
        bitrate_value = self.x265_bitrate_spinbutton.get_value_as_int()

        if advanced_enabled:
            self.__update_vbr_widgets(bitrate_value)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.encode_pass = 1
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'

            if not advanced_enabled:
                ffmpeg.video_settings.vbv_maxrate = None
                ffmpeg.video_settings.vbv_bufsize = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        self.x265_advanced_settings_revealer.set_reveal_child(advanced_settings_switch.get_active())

        if self.__is_widgets_setting_up:
            return

        threading.Thread(target=self.__update_settings, args=()).start()

    def __update_settings(self):
        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            self.get_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)

        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def on_x265_vbv_maxrate_spinbutton_value_changed(self, vbv_maxrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x265_advanced_settings_switch.get_active()
        bitrate_value = self.x265_bitrate_spinbutton.get_value_as_int()
        vbv_maxrate_value = vbv_maxrate_spinbutton.get_value_as_int()

        if not advanced_enabled:
            return

        if self.__fix_vbv_maxrate_widgets(bitrate_value):
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_maxrate = vbv_maxrate_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __fix_vbv_maxrate_widgets(self, bitrate_value):
        if bitrate_value > self.x265_vbv_maxrate_spinbutton.get_value_as_int():
            self.x265_vbv_maxrate_spinbutton.set_value(bitrate_value)

            return True

        return False

    def on_x265_vbv_bufsize_spinbutton_value_changed(self, vbv_bufsize_spinbutton):
        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.x265_advanced_settings_switch.get_active()
        vbv_bufsize_value = vbv_bufsize_spinbutton.get_value_as_int()

        if not advanced_enabled:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.vbv_bufsize = vbv_bufsize_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_aq_mode_combobox_changed(self, aq_mode_combobox):
        if self.__is_widgets_setting_up:
            return

        aq_mode_index = aq_mode_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_mode = aq_mode_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_aq_strength_spinbutton_value_changed(self, aq_strength_spinbutton):
        if self.__is_widgets_setting_up:
            return

        aq_strength_value = aq_strength_spinbutton.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_strength = aq_strength_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_hevc_aq_checkbox_toggled(self, hevc_aq_checkbox):
        if self.__is_widgets_setting_up:
            return

        hevc_aq_enabled = hevc_aq_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.hevc_aq = hevc_aq_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_keyint_spinbutton_value_changed(self, keyint_spinbutton):
        if self.__is_widgets_setting_up:
            return

        keyint_value = keyint_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.keyint = keyint_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_min_keyint_spinbutton_value_changed(self, min_keyint_spinbutton):
        if self.__is_widgets_setting_up:
            return

        min_keyint_value = min_keyint_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.min_keyint = min_keyint_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_ref_spinbutton_value_changed(self, ref_spinbutton):
        if self.__is_widgets_setting_up:
            return

        ref_value = ref_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.ref = ref_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_bframes_spinbutton_value_changed(self, bframes_spinbutton):
        if self.__is_widgets_setting_up:
            return

        bframes_value = bframes_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bframes = bframes_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_badapt_combobox_changed(self, b_adapt_combobox):
        if self.__is_widgets_setting_up:
            return

        b_adapt_index = b_adapt_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_adapt = b_adapt_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_no_bpyramid_checkbox_toggled(self, no_b_pyramid_checkbox):
        if self.__is_widgets_setting_up:
            return

        no_b_pyramid_enabled = no_b_pyramid_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_b_pyramid = no_b_pyramid_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_b_intra_checkbox_toggled(self, b_intra_checkbox):
        if self.__is_widgets_setting_up:
            return

        b_intra_enabled = b_intra_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_intra = b_intra_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_closed_gop_checkbox_toggled(self, closed_gop_checkbox):
        if self.__is_widgets_setting_up:
            return

        closed_gop_enabled = closed_gop_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_open_gop = closed_gop_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rc_lookahead_spinbutton_value_changed(self, rc_lookahead_spinbutton):
        if self.__is_widgets_setting_up:
            return

        rc_lookahead_value = rc_lookahead_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rc_lookahead = rc_lookahead_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_no_scenecut_checkbox_toggled(self, no_scenecut_checkbox):
        if self.__is_widgets_setting_up:
            return

        no_scenecut_enabled = no_scenecut_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_scenecut = no_scenecut_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_no_high_tier_checkbox_toggled(self, no_high_tier_checkbox):
        if self.__is_widgets_setting_up:
            return

        no_high_tier_enabled = no_high_tier_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_high_tier = no_high_tier_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_psyrd_spinbutton_value_changed(self, psy_rd_spinbutton):
        if self.__is_widgets_setting_up:
            return

        psy_rd_value = psy_rd_spinbutton.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rd = psy_rd_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_psyrdoq_spinbutton_value_changed(self, psy_rdoq_spinbutton):
        if self.__is_widgets_setting_up:
            return

        psy_rdoq_value = psy_rdoq_spinbutton.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.psy_rdoq = psy_rdoq_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_me_combobox_changed(self, me_combobox):
        if self.__is_widgets_setting_up:
            return

        me_index = me_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.me = me_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_subme_spinbutton_value_changed(self, subme_spinbutton):
        if self.__is_widgets_setting_up:
            return

        subme_value = subme_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.subme = subme_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_weightb_checkbox_toggled(self, weightb_checkbox):
        if self.__is_widgets_setting_up:
            return

        weightb_enabled = weightb_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.weightb = weightb_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_no_weightp_checkbox_toggled(self, no_weightp_checkbox):
        if self.__is_widgets_setting_up:
            return

        no_weightp_enabled = no_weightp_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_weightp = no_weightp_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_no_deblock_checkbox_toggled(self, no_deblock_checkbox):
        self.x265_deblock_alpha_spinbutton.set_sensitive(not no_deblock_checkbox.get_active())
        self.x265_deblock_beta_spinbutton.set_sensitive(not no_deblock_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x265_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_deblock = no_deblock_enabled
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __get_deblock_settings_from_x265_widgets(self, no_deblock_enabled):
        if no_deblock_enabled:
            return None

        alpha_value = self.x265_deblock_alpha_spinbutton.get_value_as_int()
        beta_value = self.x265_deblock_beta_spinbutton.get_value_as_int()

        return alpha_value, beta_value

    def on_x265_deblock_alpha_spinbutton_value_changed(self, deblock_alpha_spinbutton):
        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = self.x265_no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x265_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_deblock_beta_spinbutton_value_changed(self, deblock_beta_spinbutton):
        if self.__is_widgets_setting_up:
            return

        no_deblock_enabled = self.x265_no_deblock_checkbox.get_active()
        deblock_settings = self.__get_deblock_settings_from_x265_widgets(no_deblock_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.deblock = deblock_settings

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_checkbox_toggled(self, sao_checkbox):
        self.x265_sao_options_box.set_sensitive(sao_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        sao_enabled = sao_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_sao = not sao_enabled

            if sao_enabled:
                ffmpeg.video_settings.sao_non_deblock = self.x265_sao_nodeblock_checkbox.get_active()
                ffmpeg.video_settings.limit_sao = self.x265_sao_limit_checkbox.get_active()
                ffmpeg.video_settings.selective_sao = self.x265_sao_selective_spinbutton.get_value_as_int()
            else:
                ffmpeg.video_settings.sao_non_deblock = False
                ffmpeg.video_settings.limit_sao = False
                ffmpeg.video_settings.selective_sao = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_nodeblock_checkbox_toggled(self, sao_no_deblock_checkbox):
        if self.__is_widgets_setting_up:
            return

        sao_no_deblock_enabled = sao_no_deblock_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.sao_non_deblock = sao_no_deblock_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_limit_checkbox_toggled(self, sao_limit_checkbox):
        if self.__is_widgets_setting_up:
            return

        sao_limit_enabled = sao_limit_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.limit_sao = sao_limit_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_sao_selective_spinbutton_value_changed(self, sao_selective_spinbutton):
        if self.__is_widgets_setting_up:
            return

        sao_selective_value = sao_selective_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.selective_sao = sao_selective_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rdo_level_spinbutton_value_changed(self, rdo_level_spinbutton):
        if self.__is_widgets_setting_up:
            return

        rdo_level_value = rdo_level_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rd = rdo_level_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rdoq_level_combobox_changed(self, rdoq_level_combobox):
        if self.__is_widgets_setting_up:
            return

        rdoq_level_index = rdoq_level_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rdoq_level = rdoq_level_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rd_refine_checkbox_toggled(self, rd_refine_checkbox):
        if self.__is_widgets_setting_up:
            return

        rd_refine_enabled = rd_refine_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rd_refine = rd_refine_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_max_cu_combobox_changed(self, max_cu_combobox):
        if self.__is_widgets_setting_up:
            return

        max_cu_index = max_cu_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.ctu = max_cu_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_min_cu_combobox_changed(self, min_cu_combobox):
        if self.__is_widgets_setting_up:
            return

        min_cu_index = min_cu_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.min_cu_size = min_cu_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_rect_checkbox_toggled(self, rect_checkbox):
        if self.__is_widgets_setting_up:
            return

        rect_enabled = rect_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rect = rect_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_amp_checkbox_toggled(self, amp_checkbox):
        if self.__is_widgets_setting_up:
            return

        amp_enabled = amp_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.amp = amp_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_wpp_checkbox_toggled(self, wpp_checkbox):
        if self.__is_widgets_setting_up:
            return

        wpp_enabled = wpp_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.wpp = wpp_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_pmode_checkbox_toggled(self, pmode_checkbox):
        if self.__is_widgets_setting_up:
            return

        pmode_enabled = pmode_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.pmode = pmode_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_pme_checkbox_toggled(self, pme_checkbox):
        if self.__is_widgets_setting_up:
            return

        pme_enabled = pme_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.pme = pme_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x265_uhd_bluray_checkbox_toggled(self, uhd_bluray_checkbox):
        if self.__is_widgets_setting_up:
            return

        uhd_bluray_enabled = uhd_bluray_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.uhd_bd = uhd_bluray_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
