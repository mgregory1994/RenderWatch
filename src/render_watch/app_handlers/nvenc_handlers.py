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


from render_watch.ffmpeg.hevc_nvenc import HevcNvenc
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.signals.nvenc.nvenc_qp_signal import NvencQpSignal
from render_watch.signals.nvenc.nvenc_bitrate_signal import NvencBitrateSignal
from render_watch.signals.nvenc.nvenc_advanced_settings_signal import NvencAdvancedSettingsSignal
from render_watch.signals.nvenc.nvenc_aq_signal import NvencAQSignal
from render_watch.signals.nvenc.nvenc_badapt_signal import NvencBAdaptSignal
from render_watch.signals.nvenc.nvenc_bluray_compat_signal import NvencBlurayCompatSignal
from render_watch.signals.nvenc.nvenc_bref_mode_signal import NvencBRefModeSignal
from render_watch.signals.nvenc.nvenc_coder_signal import NvencCoderSignal
from render_watch.signals.nvenc.nvenc_forced_idr_signal import NvencForcedIDRSignal
from render_watch.signals.nvenc.nvenc_high_tier_signal import NvencHighTierSignal
from render_watch.signals.nvenc.nvenc_level_signal import NvencLevelSignal
from render_watch.signals.nvenc.nvenc_multi_pass_signal import NvencMultiPassSignal
from render_watch.signals.nvenc.nvenc_no_scenecut_signal import NvencNoScenecutSignal
from render_watch.signals.nvenc.nvenc_nonref_pframes_signal import NvencNonRefPFramesSignal
from render_watch.signals.nvenc.nvenc_preset_signal import NvencPresetSignal
from render_watch.signals.nvenc.nvenc_profile_signal import NvencProfileSignal
from render_watch.signals.nvenc.nvenc_rate_control_signal import NvencRateControlSignal
from render_watch.signals.nvenc.nvenc_strict_gop_signal import NvencStrictGOPSignal
from render_watch.signals.nvenc.nvenc_surfaces_signal import NvencSurfacesSignal
from render_watch.signals.nvenc.nvenc_tune_signal import NvencTuneSignal
from render_watch.signals.nvenc.nvenc_weighted_prediction_signal import NvencWeightedPredictionSignal
from render_watch.helpers.ui_helper import UIHelper
from render_watch.startup import GLib


class NvencHandlers:
    def __init__(self, gtk_builder, inputs_page_handlers):
        self.is_widgets_setting_up = False
        self.inputs_page_handlers = inputs_page_handlers
        self.__is_h264_state = True
        self.nvenc_qp_signal = NvencQpSignal(self, inputs_page_handlers)
        self.nvenc_bitrate_signal = NvencBitrateSignal(self, inputs_page_handlers)
        self.nvenc_advanced_settings_signal = NvencAdvancedSettingsSignal(self, inputs_page_handlers)
        self.nvenc_aq_signal = NvencAQSignal(self, inputs_page_handlers)
        self.nvenc_badapt_signal = NvencBAdaptSignal(self, inputs_page_handlers)
        self.nvenc_bluray_compat_signal = NvencBlurayCompatSignal(self, inputs_page_handlers)
        self.nvenc_bref_mode_signal = NvencBRefModeSignal(self, inputs_page_handlers)
        self.nvenc_coder_signal = NvencCoderSignal(self, inputs_page_handlers)
        self.nvenc_forced_idr_signal = NvencForcedIDRSignal(self, inputs_page_handlers)
        self.nvenc_high_tier_signal = NvencHighTierSignal(self, inputs_page_handlers)
        self.nvenc_level_signal = NvencLevelSignal(self, inputs_page_handlers)
        self.nvenc_multi_pass_signal = NvencMultiPassSignal(self, inputs_page_handlers)
        self.nvenc_no_scenecut_signal = NvencNoScenecutSignal(self, inputs_page_handlers)
        self.nvenc_nonref_pframes_signal = NvencNonRefPFramesSignal(self, inputs_page_handlers)
        self.nvenc_preset_signal = NvencPresetSignal(self, inputs_page_handlers)
        self.nvenc_profile_signal = NvencProfileSignal(self, inputs_page_handlers)
        self.nvenc_rate_control_signal = NvencRateControlSignal(self, inputs_page_handlers)
        self.nvenc_strict_gop_signal = NvencStrictGOPSignal(self, inputs_page_handlers)
        self.nvenc_surfaces_signal = NvencSurfacesSignal(self, inputs_page_handlers)
        self.nvenc_tune_signal = NvencTuneSignal(self, inputs_page_handlers)
        self.nvenc_weighted_prediction_signal = NvencWeightedPredictionSignal(self, inputs_page_handlers)
        self.signals_list = (self.nvenc_qp_signal, self.nvenc_bitrate_signal, self.nvenc_advanced_settings_signal,
                             self.nvenc_aq_signal, self.nvenc_badapt_signal, self.nvenc_bluray_compat_signal,
                             self.nvenc_bref_mode_signal, self.nvenc_coder_signal, self.nvenc_forced_idr_signal,
                             self.nvenc_high_tier_signal, self.nvenc_level_signal, self.nvenc_multi_pass_signal,
                             self.nvenc_no_scenecut_signal, self.nvenc_nonref_pframes_signal, self.nvenc_preset_signal,
                             self.nvenc_profile_signal, self.nvenc_rate_control_signal, self.nvenc_strict_gop_signal,
                             self.nvenc_surfaces_signal, self.nvenc_tune_signal, self.nvenc_weighted_prediction_signal)
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

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)

        raise AttributeError

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

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_nvenc_settings_widgets(ffmpeg)

    def __setup_nvenc_settings_widgets(self, ffmpeg):
        video_settings = ffmpeg.video_settings

        if video_settings is not None and 'nvenc' in video_settings.codec_name:
            self.is_widgets_setting_up = True

            self.__setup_nvenc_rate_control_widgets_settings(video_settings)
            self.nvenc_preset_combobox.set_active(video_settings.preset)
            self.nvenc_profile_combobox.set_active(video_settings.profile)
            self.nvenc_level_combobox.set_active(video_settings.level)
            self.nvenc_tune_combobox.set_active(video_settings.tune)
            self.__setup_nvenc_advanced_settings_widgets_settings(video_settings)

            self.is_widgets_setting_up = False
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

    def reset_settings(self):
        self.is_widgets_setting_up = True

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

        self.is_widgets_setting_up = False

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

    def get_qp_value(self):
        return self.nvenc_qp_scale.get_value()

    def get_bitrate_value(self):
        return self.nvenc_bitrate_spinbutton.get_value_as_int()

    def get_qp_i_value(self):
        return self.nvenc_qp_i_scale.get_value()

    def get_qp_p_value(self):
        return self.nvenc_qp_p_scale.get_value()

    def get_qp_b_value(self):
        return self.nvenc_qp_b_scale.get_value()

    def set_h264_state(self):
        self.__is_h264_state = True
        self.is_widgets_setting_up = True

        self.nvenc_coder_box.set_sensitive(True)
        self.nvenc_badapt_checkbox.set_sensitive(True)
        self.nvenc_tier_box.set_sensitive(False)
        UIHelper.rebuild_combobox(self.nvenc_preset_combobox, H264Nvenc.preset_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_profile_combobox, H264Nvenc.profile_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_profile_combobox, H264Nvenc.profile_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_level_combobox, H264Nvenc.level_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_tune_combobox, H264Nvenc.tune_human_readable_list)
        UIHelper.rebuild_combobox(self.nvenc_multi_pass_combobox, H264Nvenc.multi_pass_human_readable_list)
        UIHelper.rebuild_combobox(self.nvenc_rate_control_combobox, H264Nvenc.rate_control_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_bref_mode_combobox, H264Nvenc.bref_mode_ffmpeg_args_list)

        self.is_widgets_setting_up = False

    def set_hevc_state(self):
        self.__is_h264_state = False
        self.is_widgets_setting_up = True

        self.nvenc_coder_box.set_sensitive(False)
        self.nvenc_badapt_checkbox.set_sensitive(False)
        self.nvenc_tier_box.set_sensitive(True)
        UIHelper.rebuild_combobox(self.nvenc_preset_combobox, HevcNvenc.preset_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_profile_combobox, HevcNvenc.profile_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_profile_combobox, HevcNvenc.profile_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_level_combobox, HevcNvenc.level_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_tune_combobox, HevcNvenc.tune_human_readable_list)
        UIHelper.rebuild_combobox(self.nvenc_multi_pass_combobox, HevcNvenc.multi_pass_human_readable_list)
        UIHelper.rebuild_combobox(self.nvenc_rate_control_combobox, HevcNvenc.rate_control_ffmpeg_args_list)
        UIHelper.rebuild_combobox(self.nvenc_bref_mode_combobox, HevcNvenc.bref_mode_ffmpeg_args_list)

        self.is_widgets_setting_up = False

    def set_qp_state(self):
        self.nvenc_rate_type_stack.set_visible_child(self.nvenc_qp_scale)

    def set_bitrate_state(self):
        self.nvenc_rate_type_stack.set_visible_child(self.nvenc_bitrate_box)

    def set_multi_pass_state(self, enabled):
        self.nvenc_multi_pass_box.set_sensitive(enabled)

        if not enabled:
            self.nvenc_multi_pass_combobox.set_active(0)

    def set_advanced_settings_state(self, enabled):
        self.nvenc_advanced_settings_revealer.set_reveal_child(enabled)

    def set_qp_custom_state(self, enabled):
        self.nvenc_qp_scales_box.set_sensitive(enabled)
        self.nvenc_qp_radiobutton.set_active(enabled)
        self.nvenc_qp_scale.set_sensitive(not enabled)
        self.nvenc_bitrate_box.set_sensitive(not enabled)
        self.nvenc_rate_type_buttons_box.set_sensitive(not enabled)

    def set_aq_strength_state(self, enabled):
        self.nvenc_aqstrength_box.set_sensitive(enabled)

    def update_rc_from_qp(self):
        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

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

    def update_rc_from_average_bitrate(self):
        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

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

    def update_rc_from_constant_bitrate(self):
        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

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

    def update_rc_from_2pass_bitrate(self):
        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        if advanced_enabled and not self.__is_rc_valid_for_vbr():

            if self.__is_h264_state:
                rc_index = H264Nvenc.rate_control_ffmpeg_args_list.index('vbr')
            else:
                rc_index = HevcNvenc.rate_control_ffmpeg_args_list.index('vbr')

            self.nvenc_rate_control_combobox.set_active(rc_index)

    def update_qp_from_advanced_settings(self):
        advanced_enabled = self.nvenc_advanced_settings_switch.get_active()

        if self.nvenc_qp_custom_radiobutton.get_active():

            if advanced_enabled:
                self.nvenc_qp_radiobutton.set_active(True)

            self.nvenc_qp_scale.set_sensitive(not advanced_enabled)
            self.nvenc_bitrate_box.set_sensitive(not advanced_enabled)
            self.nvenc_rate_type_buttons_box.set_sensitive(not advanced_enabled)

    def update_settings(self):
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg

            self.get_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)

        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def signal_average_radiobutton(self):
        self.nvenc_bitrate_signal.on_nvenc_average_radiobutton_toggled(self.nvenc_average_radiobutton)

    def signal_constant_radiobutton(self):
        self.nvenc_bitrate_signal.on_nvenc_constant_radiobutton_toggled(self.nvenc_constant_radiobutton)

    def signal_2pass_radiobutton(self):
        self.nvenc_bitrate_signal.on_nvenc_2pass_radiobutton_toggled(self.nvenc_2pass_radiobutton)

    def signal_multi_pass_combobox(self):
        self.nvenc_multi_pass_signal.on_nvenc_multi_pass_combobox_changed(self.nvenc_multi_pass_combobox)

    def signal_aq_strength_spinbutton(self):
        self.nvenc_aq_signal.on_nvenc_aqstrength_spinbutton_value_changed(self.nvenc_aqstrength_spinbutton)
