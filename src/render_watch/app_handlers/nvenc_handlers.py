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

from render_watch.ffmpeg.hevc_nvenc import HevcNvenc
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.startup import GLib


class NvencHandlers:
    def __init__(self, gtk_builder):
        self.__is_widgets_setting_up = False
        self.inputs_page_handlers = None
        self.__is_h264_state = True
        self.nvenc_preset_combobox = gtk_builder.get_object('nvenc_preset_combobox')
        self.nvenc_profile_combobox = gtk_builder.get_object('nvenc_profile_combobox')
        self.nvenc_level_combobox = gtk_builder.get_object('nvenc_level_combobox')
        self.nvenc_tune_combobox = gtk_builder.get_object('nvenc_tune_combobox')
        self.nvenc_qp_radiobutton = gtk_builder.get_object('nvenc_qp_radiobutton')
        self.nvenc_bitrate_radiobutton = gtk_builder.get_object('nvenc_bitrate_radiobutton')
        self.nvenc_rate_type_stack = gtk_builder.get_object('nvenc_rate_type_stack')
        self.nvenc_rate_type_buttons_box = gtk_builder.get_object('nvenc_rate_type_buttons_box')
        self.nvenc_qp_scale = gtk_builder.get_object('nvenc_qp_scale')
        self.nvenc_bitrate_box = gtk_builder.get_object('nvenc_bitrate_box')
        self.nvenc_bitrate_spinbutton = gtk_builder.get_object('nvenc_bitrate_spinbutton')
        self.nvenc_bitrate_radiobutton = gtk_builder.get_object('nvenc_bitrate_radiobutton')
        self.nvenc_average_radiobutton = gtk_builder.get_object('nvenc_average_radiobutton')
        self.nvenc_2pass_radiobutton = gtk_builder.get_object('nvenc_2pass_radiobutton')
        self.nvenc_multi_pass_box = gtk_builder.get_object('nvenc_multi_pass_box')
        self.nvenc_multi_pass_combobox = gtk_builder.get_object('nvenc_multi_pass_combobox')
        self.nvenc_constant_radiobutton = gtk_builder.get_object('nvenc_constant_radiobutton')
        self.nvenc_advanced_settings_switch = gtk_builder.get_object('nvenc_advanced_settings_switch')
        self.nvenc_advanced_settings_revealer = gtk_builder.get_object('nvenc_advanced_settings_revealer')
        self.nvenc_qp_auto_radiobutton = gtk_builder.get_object('nvenc_qp_auto_radiobutton')
        self.nvenc_qp_custom_radiobutton = gtk_builder.get_object('nvenc_qp_custom_radiobutton')
        self.nvenc_qp_scales_box = gtk_builder.get_object('nvenc_qp_scales_box')
        self.nvenc_qp_i_scale = gtk_builder.get_object('nvenc_qp_i_scale')
        self.nvenc_qp_p_scale = gtk_builder.get_object('nvenc_qp_p_scale')
        self.nvenc_qp_b_scale = gtk_builder.get_object('nvenc_qp_b_scale')
        self.nvenc_rate_control_combobox = gtk_builder.get_object('nvenc_rate_control_combobox')
        self.nvenc_rate_control_lookahead_spinbutton = gtk_builder.get_object('nvenc_rate_control_lookahead_spinbutton')
        self.nvenc_surfaces_spinbutton = gtk_builder.get_object('nvenc_surfaces_spinbutton')
        self.nvenc_bref_mode_combobox = gtk_builder.get_object('nvenc_bref_mode_combobox')
        self.nvenc_nonref_pframes_checkbox = gtk_builder.get_object('nvenc_nonref_pframes_checkbox')
        self.nvenc_badapt_checkbox = gtk_builder.get_object('nvenc_badapt_checkbox')
        self.nvenc_spatial_radiobutton = gtk_builder.get_object('nvenc_spatial_radiobutton')
        self.nvenc_temporal_radiobutton = gtk_builder.get_object('nvenc_temporal_radiobutton')
        self.nvenc_aqstrength_box = gtk_builder.get_object('nvenc_aqstrength_box')
        self.nvenc_aqstrength_spinbutton = gtk_builder.get_object('nvenc_aqstrength_spinbutton')
        self.nvenc_tier_main_radiobutton = gtk_builder.get_object('nvenc_tier_main_radiobutton')
        self.nvenc_tier_high_radiobutton = gtk_builder.get_object('nvenc_tier_high_radiobutton')
        self.nvenc_tier_box = gtk_builder.get_object('nvenc_tier_box')
        self.nvenc_forced_idr_checkbox = gtk_builder.get_object('nvenc_forced_idr_checkbox')
        self.nvenc_strict_gop_checkbox = gtk_builder.get_object('nvenc_strict_gop_checkbox')
        self.nvenc_no_scenecut_checkbox = gtk_builder.get_object('nvenc_no_scenecut_checkbox')
        self.nvenc_bluray_compat_checkbox = gtk_builder.get_object('nvenc_bluray_compat_checkbox')
        self.nvenc_coder_combobox = gtk_builder.get_object('nvenc_coder_combobox')
        self.nvenc_coder_box = gtk_builder.get_object('nvenc_coder_box')
        self.nvenc_weighted_prediction_checkbox = gtk_builder.get_object('nvenc_weighted_prediction_checkbox')

    def reset_settings(self):
        self.__is_widgets_setting_up = True

        self.nvenc_qp_scale.set_value(20)
        self.nvenc_preset_combobox.set_active(0)
        self.nvenc_profile_combobox.set_active(0)
        self.nvenc_level_combobox.set_active(0)
        self.nvenc_tune_combobox.set_active(0)
        self.nvenc_qp_radiobutton.set_active(True)
        self.nvenc_bitrate_spinbutton.set_value(2500)
        self.nvenc_average_radiobutton.set_active(True)
        self.nvenc_multi_pass_combobox.set_active(0)
        self.__reset_advanced_settings_widgets()

        self.__is_widgets_setting_up = False

    def __reset_advanced_settings_widgets(self):
        self.nvenc_advanced_settings_switch.set_active(False)
        self.nvenc_qp_auto_radiobutton.set_active(True)
        self.nvenc_qp_i_scale.set_value(20)
        self.nvenc_qp_p_scale.set_value(20)
        self.nvenc_qp_b_scale.set_value(20)
        self.nvenc_rate_control_combobox.set_active(0)
        self.nvenc_rate_control_lookahead_spinbutton.set_value(0)
        self.nvenc_surfaces_spinbutton.set_value(0)
        self.nvenc_bref_mode_combobox.set_active(0)
        self.nvenc_nonref_pframes_checkbox.set_active(False)
        self.nvenc_badapt_checkbox.set_active(False)
        self.nvenc_spatial_radiobutton.set_active(True)
        self.nvenc_aqstrength_spinbutton.set_value(8)
        self.nvenc_tier_main_radiobutton.set_active(True)
        self.nvenc_forced_idr_checkbox.set_active(False)
        self.nvenc_strict_gop_checkbox.set_active(False)
        self.nvenc_no_scenecut_checkbox.set_active(False)
        self.nvenc_bluray_compat_checkbox.set_active(False)
        self.nvenc_coder_combobox.set_active(0)
        self.nvenc_weighted_prediction_checkbox.set_active(False)

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_nvenc_settings_widgets(ffmpeg)

    def __setup_nvenc_settings_widgets(self, ffmpeg):
        video_settings = ffmpeg.video_settings

        if video_settings is not None and 'nvenc' in video_settings.codec_name:
            self.__is_widgets_setting_up = True

            self.__setup_nvenc_rate_control_widgets_settings(video_settings)
            self.nvenc_preset_combobox.set_active(video_settings.preset)
            self.nvenc_profile_combobox.set_active(video_settings.profile)
            self.nvenc_level_combobox.set_active(video_settings.level)
            self.nvenc_tune_combobox.set_active(video_settings.tune)
            self.__setup_nvenc_advanced_settings_widgets_settings(video_settings)

            self.__is_widgets_setting_up = False
        else:
            self.reset_settings()

    def __setup_nvenc_rate_control_widgets_settings(self, video_settings):
        if video_settings.qp is not None:
            self.nvenc_qp_radiobutton.set_active(True)
            self.nvenc_qp_scale.set_value(video_settings.qp)
        elif video_settings.bitrate is not None:
            self.nvenc_bitrate_radiobutton.set_active(True)
            self.nvenc_bitrate_spinbutton.set_value(video_settings.bitrate)

        self.nvenc_2pass_radiobutton.set_active(video_settings.dual_pass_enabled)
        self.nvenc_constant_radiobutton.set_active(video_settings.cbr)
        self.nvenc_average_radiobutton.set_active(not (video_settings.cbr or video_settings.dual_pass_enabled))
        self.nvenc_multi_pass_combobox.set_active(video_settings.multi_pass)

    def __setup_nvenc_advanced_settings_widgets_settings(self, video_settings):
        self.nvenc_advanced_settings_switch.set_active(video_settings.advanced_enabled)
        self.__setup_nvenc_qp_custom_widgets_settings(video_settings)
        self.nvenc_rate_control_combobox.set_active(video_settings.rc)
        self.nvenc_rate_control_lookahead_spinbutton.set_value(video_settings.rc_lookahead)
        self.nvenc_surfaces_spinbutton.set_value(video_settings.surfaces)
        self.nvenc_no_scenecut_checkbox.set_active(video_settings.no_scenecut)
        self.nvenc_forced_idr_checkbox.set_active(video_settings.forced_idr)
        self.nvenc_spatial_radiobutton.set_active(video_settings.spatial_aq)
        self.nvenc_temporal_radiobutton.set_active(video_settings.temporal_aq)
        self.nvenc_nonref_pframes_checkbox.set_active(video_settings.non_ref_p)
        self.nvenc_strict_gop_checkbox.set_active(video_settings.strict_gop)
        self.nvenc_aqstrength_spinbutton.set_value(video_settings.aq_strength)
        self.nvenc_bluray_compat_checkbox.set_active(video_settings.bluray_compat)
        self.nvenc_weighted_prediction_checkbox.set_active(video_settings.weighted_pred)
        self.nvenc_bref_mode_combobox.set_active(video_settings.b_ref_mode)
        self.__setup_nvenc_h264_widgets_settings(video_settings)
        self.__setup_nvenc_hevc_widgets_settings(video_settings)

    def __setup_nvenc_qp_custom_widgets_settings(self, video_settings):
        is_qp_custom_enabled = video_settings.qp_custom_enabled

        self.nvenc_qp_custom_radiobutton.set_active(is_qp_custom_enabled)
        self.nvenc_qp_auto_radiobutton.set_active(not is_qp_custom_enabled)
        self.nvenc_qp_i_scale.set_value(video_settings.qp_i)
        self.nvenc_qp_p_scale.set_value(video_settings.qp_p)
        self.nvenc_qp_b_scale.set_value(video_settings.qp_b)

    def __setup_nvenc_h264_widgets_settings(self, video_settings):
        if video_settings.codec_name == 'h264_nvenc':
            self.nvenc_badapt_checkbox.set_active(video_settings.b_adapt)
            self.nvenc_coder_combobox.set_active(video_settings.coder)
            self.nvenc_tier_high_radiobutton.set_active(0)

    def __setup_nvenc_hevc_widgets_settings(self, video_settings):
        if video_settings.codec_name != 'h264_nvenc':
            self.nvenc_tier_high_radiobutton.set_active(video_settings.tier)
            self.nvenc_coder_combobox.set_active(0)
            self.nvenc_badapt_checkbox.set_active(False)

    def get_settings(self, ffmpeg):
        if self.__is_h264_state:
            video_settings = H264Nvenc()
        else:
            video_settings = HevcNvenc()

        video_settings.preset = self.nvenc_preset_combobox.get_active()
        video_settings.profile = self.nvenc_profile_combobox.get_active()
        video_settings.level = self.nvenc_level_combobox.get_active()
        video_settings.tune = self.nvenc_tune_combobox.get_active()

        self.__set_rate_control_settings_from_nvenc_widgets(video_settings)
        self.__set_advanced_settings_from_nvenc_widgets(video_settings)

        ffmpeg.video_settings = video_settings

    def __set_rate_control_settings_from_nvenc_widgets(self, video_settings):
        if self.nvenc_qp_radiobutton.get_active():
            video_settings.qp = self.nvenc_qp_scale.get_value()
        else:
            video_settings.bitrate = self.nvenc_bitrate_spinbutton.get_value_as_int()
            video_settings.dual_pass_enabled = self.nvenc_2pass_radiobutton.get_active()
            video_settings.cbr = self.nvenc_constant_radiobutton.get_active()
            video_settings.multi_pass = self.nvenc_multi_pass_combobox.get_active()

    def __set_advanced_settings_from_nvenc_widgets(self, video_settings):
        if self.nvenc_advanced_settings_switch.get_active():
            video_settings.advanced_enabled = True
            video_settings.no_scenecut = self.nvenc_no_scenecut_checkbox.get_active()
            video_settings.forced_idr = self.nvenc_forced_idr_checkbox.get_active()
            video_settings.spatial_aq = self.nvenc_spatial_radiobutton.get_active()
            video_settings.temporal_aq = self.nvenc_temporal_radiobutton.get_active()
            video_settings.strict_gop = self.nvenc_strict_gop_checkbox.get_active()
            video_settings.non_ref_p = self.nvenc_nonref_pframes_checkbox.get_active()
            video_settings.bluray_compat = self.nvenc_bluray_compat_checkbox.get_active()
            video_settings.weighted_pred = self.nvenc_weighted_prediction_checkbox.get_active()
            video_settings.rc_lookahead = self.nvenc_rate_control_lookahead_spinbutton.get_value_as_int()
            video_settings.surfaces = self.nvenc_surfaces_spinbutton.get_value_as_int()
            video_settings.aq_strength = self.nvenc_aqstrength_spinbutton.get_value_as_int()
            video_settings.rc = self.nvenc_rate_control_combobox.get_active()

            self.__set_qp_custom_settings_from_nvenc_widgets(video_settings)
            self.__set_h264_settings_from_nvenc_widgets(video_settings)
            self.__set_hevc_settings_from_nvenc_widgets(video_settings)

    def __set_qp_custom_settings_from_nvenc_widgets(self, video_settings):
        if self.nvenc_qp_custom_radiobutton.get_active():
            video_settings.bitrate = None
            video_settings.cbr = None
            video_settings.dual_pass = None
            video_settings.qp_i = self.nvenc_qp_i_scale.get_value()
            video_settings.qp_p = self.nvenc_qp_p_scale.get_value()
            video_settings.qp_b = self.nvenc_qp_b_scale.get_value()

    def __set_h264_settings_from_nvenc_widgets(self, video_settings):
        if self.__is_h264_state:
            video_settings.b_adapt = self.nvenc_badapt_checkbox.get_active()
            video_settings.coder = self.nvenc_coder_combobox.get_active()

    def __set_hevc_settings_from_nvenc_widgets(self, video_settings):
        if not self.__is_h264_state:
            video_settings.tier = self.nvenc_tier_high_radiobutton.get_active()

    def set_h264_state(self):
        self.__is_h264_state = True
        self.__is_widgets_setting_up = True

        self.nvenc_coder_box.set_sensitive(True)
        self.nvenc_badapt_checkbox.set_sensitive(True)
        self.nvenc_tier_box.set_sensitive(False)
        self.__rebuild_combobox(self.nvenc_preset_combobox, H264Nvenc.preset_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_profile_combobox, H264Nvenc.profile_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_profile_combobox, H264Nvenc.profile_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_level_combobox, H264Nvenc.level_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_tune_combobox, H264Nvenc.tune_human_readable_list)
        self.__rebuild_combobox(self.nvenc_multi_pass_combobox, H264Nvenc.multi_pass_human_readable_list)
        self.__rebuild_combobox(self.nvenc_rate_control_combobox, H264Nvenc.rate_control_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_bref_mode_combobox, H264Nvenc.bref_mode_ffmpeg_args_list)

        self.__is_widgets_setting_up = False

    def set_hevc_state(self):
        self.__is_h264_state = False
        self.__is_widgets_setting_up = True

        self.nvenc_coder_box.set_sensitive(False)
        self.nvenc_badapt_checkbox.set_sensitive(False)
        self.nvenc_tier_box.set_sensitive(True)
        self.__rebuild_combobox(self.nvenc_preset_combobox, HevcNvenc.preset_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_profile_combobox, HevcNvenc.profile_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_profile_combobox, HevcNvenc.profile_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_level_combobox, HevcNvenc.level_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_tune_combobox, HevcNvenc.tune_human_readable_list)
        self.__rebuild_combobox(self.nvenc_multi_pass_combobox, HevcNvenc.multi_pass_human_readable_list)
        self.__rebuild_combobox(self.nvenc_rate_control_combobox, HevcNvenc.rate_control_ffmpeg_args_list)
        self.__rebuild_combobox(self.nvenc_bref_mode_combobox, HevcNvenc.bref_mode_ffmpeg_args_list)

        self.__is_widgets_setting_up = False

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def on_nvenc_qp_radiobutton_toggled(self, qp_radiobutton):
        if not qp_radiobutton.get_active():
            return

        self.nvenc_rate_type_stack.set_visible_child(self.nvenc_qp_scale)

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        self.__setup_rc_widgets_from_qp(advanced_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = self.nvenc_qp_scale.get_value()
            ffmpeg.video_settings.dual_pass = None
            ffmpeg.video_settings.cbr = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __setup_rc_widgets_from_qp(self, advanced_enabled):
        if advanced_enabled and not self.__is_rc_valid_for_qp():

            if self.__is_h264_state:
                rc_index = H264Nvenc.rate_control_ffmpeg_args_list.index('constqp')
            else:
                rc_index = HevcNvenc.rate_control_ffmpeg_args_list.index('constqp')

            self.nvenc_rate_control_combobox.set_active(rc_index)

    def __is_rc_valid_for_qp(self):
        rc_index = self.nvenc_rate_control_combobox.get_active()

        if self.__is_h264_state:
            rc_value = H264Nvenc.rate_control_ffmpeg_args_list[rc_index]
        else:
            rc_value = HevcNvenc.rate_control_ffmpeg_args_list[rc_index]

        if rc_value == 'constqp' or rc_value == 'auto':
            return True

        return False

    def on_nvenc_bitrate_radiobutton_toggled(self, bitrate_radiobutton):
        if not bitrate_radiobutton.get_active():
            return

        self.nvenc_rate_type_stack.set_visible_child(self.nvenc_bitrate_box)

        if self.__is_widgets_setting_up:
            return

        self.on_nvenc_average_radiobutton_toggled(self.nvenc_average_radiobutton)
        self.on_nvenc_constant_radiobutton_toggled(self.nvenc_constant_radiobutton)
        self.on_nvenc_2pass_radiobutton_toggled(self.nvenc_2pass_radiobutton)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = self.nvenc_bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_average_radiobutton_toggled(self, average_radiobutton):
        if not average_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        self.__setup_rc_widgets_from_average_bitrate(advanced_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __setup_rc_widgets_from_average_bitrate(self, advanced_enabled):
        if advanced_enabled and not self.__is_rc_valid_for_vbr():

            if self.__is_h264_state:
                rc_index = H264Nvenc.rate_control_ffmpeg_args_list.index('vbr')
            else:
                rc_index = HevcNvenc.rate_control_ffmpeg_args_list.index('vbr')

            self.nvenc_rate_control_combobox.set_active(rc_index)

    def __is_rc_valid_for_vbr(self):
        rc_index = self.nvenc_rate_control_combobox.get_active()

        if self.__is_h264_state:
            rc_value = H264Nvenc.rate_control_ffmpeg_args_list[rc_index]
        else:
            rc_value = HevcNvenc.rate_control_ffmpeg_args_list[rc_index]

        if 'vbr' in rc_value or rc_value == 'auto':
            return True

        return False

    def on_nvenc_constant_radiobutton_toggled(self, constant_radiobutton):
        if not constant_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        self.__setup_rc_widgets_from_constant_bitrate(advanced_enabled)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.dual_pass_enabled = False
            ffmpeg.video_settings.multi_pass = None
            ffmpeg.video_settings.cbr = True

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __setup_rc_widgets_from_constant_bitrate(self, advanced_enabled):
        if advanced_enabled and not self.__is_rc_valid_for_cbr():

            if self.__is_h264_state:
                rc_index = H264Nvenc.rate_control_ffmpeg_args_list.index('cbr')
            else:
                rc_index = HevcNvenc.rate_control_ffmpeg_args_list.index('cbr')

            self.nvenc_rate_control_combobox.set_active(rc_index)

    def __is_rc_valid_for_cbr(self):
        rc_index = self.nvenc_rate_control_combobox.get_active()

        if self.__is_h264_state:
            rc_value = H264Nvenc.rate_control_ffmpeg_args_list[rc_index]
        else:
            rc_value = HevcNvenc.rate_control_ffmpeg_args_list[rc_index]

        if 'cbr' in rc_value or rc_value == 'auto':
            return True

        return False

    def on_nvenc_2pass_radiobutton_toggled(self, dual_pass_radiobutton):
        self.nvenc_multi_pass_box.set_sensitive(dual_pass_radiobutton.get_active())

        if not dual_pass_radiobutton.get_active():
            self.nvenc_multi_pass_combobox.set_active(0)

            return

        if self.__is_widgets_setting_up:
            return

        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        self.__setup_rc_widgets_from_2pass_bitrate(advanced_enabled)
        self.on_nvenc_multi_pass_combobox_changed(self.nvenc_multi_pass_combobox)

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.cbr = None
            ffmpeg.video_settings.dual_pass_enabled = True

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __setup_rc_widgets_from_2pass_bitrate(self, advanced_enabled):
        if advanced_enabled and not self.__is_rc_valid_for_vbr():

            if self.__is_h264_state:
                rc_index = H264Nvenc.rate_control_ffmpeg_args_list.index('vbr')
            else:
                rc_index = HevcNvenc.rate_control_ffmpeg_args_list.index('vbr')

            self.nvenc_rate_control_combobox.set_active(rc_index)

    def on_nvenc_multi_pass_combobox_changed(self, multi_pass_combobox):
        if self.__is_widgets_setting_up:
            return

        multi_pass_index = multi_pass_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.multi_pass = multi_pass_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_preset_combobox_changed(self, preset_combobox):
        if self.__is_widgets_setting_up:
            return

        preset_index = preset_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.preset = preset_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_profile_combobox_changed(self, profile_combobox):
        if self.__is_widgets_setting_up:
            return

        profile_index = profile_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.profile = profile_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_level_combobox_changed(self, level_combobox):
        if self.__is_widgets_setting_up:
            return

        level_index = level_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.level = level_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_tune_combobox_changed(self, tune_combobox):
        if self.__is_widgets_setting_up:
            return

        tune_index = tune_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.tune = tune_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bitrate = bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        qp_value = self.nvenc_qp_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp = qp_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_advanced_settings_switch_state_set(self, advanced_settings_switch, user_data):
        advanced_settings_enabled = advanced_settings_switch.get_active()

        self.nvenc_advanced_settings_revealer.set_reveal_child(advanced_settings_enabled)
        self.__setup_qp_custom_state_from_advanced_settings_switch(advanced_settings_enabled)

        if self.__is_widgets_setting_up:
            return

        threading.Thread(target=self.__update_settings, args=()).start()

    def __setup_qp_custom_state_from_advanced_settings_switch(self, advanced_settings_enabled):
        if self.nvenc_qp_custom_radiobutton.get_active():

            if advanced_settings_enabled:
                self.nvenc_qp_radiobutton.set_active(True)

            self.nvenc_qp_scale.set_sensitive(not advanced_settings_enabled)
            self.nvenc_bitrate_box.set_sensitive(not advanced_settings_enabled)
            self.nvenc_rate_type_buttons_box.set_sensitive(not advanced_settings_enabled)

    def __update_settings(self):
        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            self.get_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)

        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def on_nvenc_qp_auto_radiobutton_toggled(self, qp_auto_radiobutton):
        if not qp_auto_radiobutton.get_active():
            return

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_i = None
            ffmpeg.video_settings.qp_p = None
            ffmpeg.video_settings.qp_b = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_custom_radiobutton_toggled(self, qp_custom_radiobutton):
        is_qp_custom_enabled = qp_custom_radiobutton.get_active()

        self.__setup_qp_custom_state(is_qp_custom_enabled)

        if self.__is_widgets_setting_up:
            return

        qp_i_value = self.nvenc_qp_i_scale.get_value()
        qp_p_value = self.nvenc_qp_p_scale.get_value()
        qp_b_value = self.nvenc_qp_b_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            if is_qp_custom_enabled:
                ffmpeg.video_settings.qp_i = qp_i_value
                ffmpeg.video_settings.qp_p = qp_p_value
                ffmpeg.video_settings.qp_b = qp_b_value
                ffmpeg.video_settings.bitrate = None
                ffmpeg.video_settings.cbr = None
                ffmpeg.video_settings.dual_pass = None

            ffmpeg.video_settings.qp_custom_enabled = is_qp_custom_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def __setup_qp_custom_state(self, qp_custom_enabled):
        self.nvenc_qp_scales_box.set_sensitive(qp_custom_enabled)
        self.nvenc_qp_radiobutton.set_active(qp_custom_enabled)
        self.nvenc_qp_scale.set_sensitive(not qp_custom_enabled)
        self.nvenc_bitrate_box.set_sensitive(not qp_custom_enabled)
        self.nvenc_rate_type_buttons_box.set_sensitive(not qp_custom_enabled)

    def on_nvenc_qp_i_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        qp_i_value = self.nvenc_qp_i_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_i = qp_i_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_p_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        qp_p_value = self.nvenc_qp_p_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_p = qp_p_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_qp_b_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return

        qp_b_value = self.nvenc_qp_b_scale.get_value()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.qp_b = qp_b_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_rate_control_combobox_changed(self, rate_control_combobox):
        if self.__is_widgets_setting_up:
            return

        rate_control_index = rate_control_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rc = rate_control_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_rate_control_lookahead_spinbutton_value_changed(self, rc_lookahead_spinbutton):
        if self.__is_widgets_setting_up:
            return

        rc_lookahead_value = rc_lookahead_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.rc_lookahead = rc_lookahead_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_surfaces_spinbutton_value_changed(self, surfaces_spinbutton):
        if self.__is_widgets_setting_up:
            return

        surfaces_value = surfaces_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.surfaces = surfaces_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_bref_mode_combobox_changed(self, bref_mode_combobox):
        if self.__is_widgets_setting_up:
            return

        bref_mode_index = bref_mode_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_ref_mode = bref_mode_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_nonref_pframes_checkbox_toggled(self, nonref_pframes_checkbox):
        if self.__is_widgets_setting_up:
            return

        nonref_pframes_enabled = nonref_pframes_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.non_ref_p = nonref_pframes_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_badapt_checkbox_toggled(self, badapt_checkbox):
        if self.__is_widgets_setting_up:
            return

        badapt_enabled = badapt_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.b_adapt = badapt_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_spatial_radiobutton_toggled(self, spatial_radiobutton):
        self.nvenc_aqstrength_box.set_sensitive(spatial_radiobutton.get_active())

        if self.__is_widgets_setting_up:
            return

        spatial_enabled = spatial_radiobutton.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.spatial_aq = spatial_enabled
            ffmpeg.video_settings.temporal_aq = not spatial_enabled

            if not spatial_enabled:
                ffmpeg.video_settings.aq_strength = None
            else:
                self.on_nvenc_aqstrength_spinbutton_value_changed(self.nvenc_aqstrength_spinbutton)

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_aqstrength_spinbutton_value_changed(self, aqstrength_spinbutton):
        if self.__is_widgets_setting_up:
            return

        aq_strength_value = aqstrength_spinbutton.get_value_as_int()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.aq_strength = aq_strength_value

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_tier_high_radiobutton_toggled(self, tier_high_radiobutton):
        if self.__is_widgets_setting_up:
            return

        tier_high_enabled = tier_high_radiobutton.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.tier = tier_high_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_forced_idr_checkbox_toggled(self, forced_idr_checkbox):
        if self.__is_widgets_setting_up:
            return

        forced_idr_enabled = forced_idr_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.forced_idr = forced_idr_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_strict_gop_checkbox_toggled(self, strict_gop_checkbox):
        if self.__is_widgets_setting_up:
            return

        strict_gop_enabled = strict_gop_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.strict_gop = strict_gop_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_no_scenecut_checkbox_toggled(self, no_scenecut_checkbox):
        if self.__is_widgets_setting_up:
            return

        no_scenecut_enabled = no_scenecut_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.no_scenecut = no_scenecut_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_bluray_compat_checkbox_toggled(self, bluray_compat_checkbox):
        if self.__is_widgets_setting_up:
            return

        bluray_compat_enabled = bluray_compat_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.bluray_compat = bluray_compat_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_coder_combobox_changed(self, coder_combobox):
        if self.__is_widgets_setting_up:
            return

        coder_index = coder_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.coder = coder_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_nvenc_weighted_prediction_checkbox_toggled(self, weighted_prediction_checkbox):
        if self.__is_widgets_setting_up:
            return

        weighted_prediction_enabled = weighted_prediction_checkbox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.weighted_pred = weighted_prediction_enabled

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    @staticmethod
    def __rebuild_combobox(combobox, values_list):
        combobox.remove_all()

        for value in values_list:
            combobox.append_text(value)

        combobox.set_entry_text_column(0)
        combobox.set_active(0)
