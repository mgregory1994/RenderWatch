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


from render_watch.ffmpeg.x265 import X265
from render_watch.signals.x265.x265_advanced_settings_signal import X265AdvancedSettingsSignal
from render_watch.signals.x265.x265_amp_signal import X265AmpSignal
from render_watch.signals.x265.x265_aq_signal import X265AqSignal
from render_watch.signals.x265.x265_b_intra_signal import X265BIntraSignal
from render_watch.signals.x265.x265_badapt_signal import X265BAdaptSignal
from render_watch.signals.x265.x265_bframes_signal import X265BFramesSignal
from render_watch.signals.x265.x265_bitrate_signal import X265BitrateSignal
from render_watch.signals.x265.x265_closed_gop_signal import X265ClosedGopSignal
from render_watch.signals.x265.x265_crf_signal import X265CrfSignal
from render_watch.signals.x265.x265_cu_signal import X265CuSignal
from render_watch.signals.x265.x265_deblock_signal import X265DeblockSignal
from render_watch.signals.x265.x265_keyframe_signal import X265KeyframeSignal
from render_watch.signals.x265.x265_level_signal import X265LevelSignal
from render_watch.signals.x265.x265_me_signal import X265MeSignal
from render_watch.signals.x265.x265_no_bpyramid_signal import X265NoBPyramidSignal
from render_watch.signals.x265.x265_no_high_tier_signal import X265NoHighTierSignal
from render_watch.signals.x265.x265_no_scenecut_signal import X265NoScenecutSignal
from render_watch.signals.x265.x265_no_weightp_signal import X265NoWeightPSignal
from render_watch.signals.x265.x265_pme_signal import X265PmeSignal
from render_watch.signals.x265.x265_pmode_signal import X265PModeSignal
from render_watch.signals.x265.x265_preset_signal import X265PresetSignal
from render_watch.signals.x265.x265_profile_signal import X265ProfileSignal
from render_watch.signals.x265.x265_psyrd_signal import X265PsyRdSignal
from render_watch.signals.x265.x265_qp_signal import X265QpSignal
from render_watch.signals.x265.x265_rc_lookahead_signal import X265RcLookaheadSignal
from render_watch.signals.x265.x265_rd_signal import X265RdSignal
from render_watch.signals.x265.x265_rect_signal import X265RectSignal
from render_watch.signals.x265.x265_ref_signal import X265RefSignal
from render_watch.signals.x265.x265_sao_signal import X265SaoSignal
from render_watch.signals.x265.x265_tune_signal import X265TuneSignal
from render_watch.signals.x265.x265_uhd_bluray_signal import X265UhdBluraySignal
from render_watch.signals.x265.x265_vbv_signal import X265VbvSignal
from render_watch.signals.x265.x265_weightb_signal import X265WeightBSignal
from render_watch.signals.x265.x265_wpp_signal import X265WppSignal
from render_watch.startup import GLib


class X265Handlers:
    """Handles all widget changes for the x265 codec."""

    def __init__(self, gtk_builder, inputs_page_handlers, preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences
        self.is_widgets_setting_up = False
        self.advanced_settings_signal = X265AdvancedSettingsSignal(self)
        self.amp_signal = X265AmpSignal(self, inputs_page_handlers)
        self.aq_signal = X265AqSignal(self, inputs_page_handlers)
        self.b_intra_signal = X265BIntraSignal(self, inputs_page_handlers)
        self.badapt_signal = X265BAdaptSignal(self, inputs_page_handlers)
        self.bframes_signal = X265BFramesSignal(self, inputs_page_handlers)
        self.bitrate_signal = X265BitrateSignal(self, inputs_page_handlers, preferences)
        self.closed_gop_signal = X265ClosedGopSignal(self, inputs_page_handlers)
        self.crf_signal = X265CrfSignal(self, inputs_page_handlers)
        self.cu_signal = X265CuSignal(self, inputs_page_handlers)
        self.deblock_signal = X265DeblockSignal(self, inputs_page_handlers)
        self.keyframe_signal = X265KeyframeSignal(self, inputs_page_handlers)
        self.level_signal = X265LevelSignal(self, inputs_page_handlers)
        self.me_signal = X265MeSignal(self, inputs_page_handlers)
        self.no_bpyramid_signal = X265NoBPyramidSignal(self, inputs_page_handlers)
        self.no_high_tier_signal = X265NoHighTierSignal(self, inputs_page_handlers)
        self.no_scenecut_signal = X265NoScenecutSignal(self, inputs_page_handlers)
        self.no_weightp_signal = X265NoWeightPSignal(self, inputs_page_handlers)
        self.pme_signal = X265PmeSignal(self, inputs_page_handlers)
        self.pmode_signal = X265PModeSignal(self, inputs_page_handlers)
        self.preset_signal = X265PresetSignal(self, inputs_page_handlers)
        self.profile_signal = X265ProfileSignal(self, inputs_page_handlers)
        self.psyrd_signal = X265PsyRdSignal(self, inputs_page_handlers)
        self.qp_signal = X265QpSignal(self, inputs_page_handlers)
        self.rc_lookahead_signal = X265RcLookaheadSignal(self, inputs_page_handlers)
        self.rd_signal = X265RdSignal(self, inputs_page_handlers)
        self.rect_signal = X265RectSignal(self, inputs_page_handlers)
        self.ref_signal = X265RefSignal(self, inputs_page_handlers)
        self.sao_signal = X265SaoSignal(self, inputs_page_handlers)
        self.tune_signal = X265TuneSignal(self, inputs_page_handlers)
        self.uhd_bluray_signal = X265UhdBluraySignal(self, inputs_page_handlers)
        self.vbv_signal = X265VbvSignal(self, inputs_page_handlers)
        self.weightb_signal = X265WeightBSignal(self, inputs_page_handlers)
        self.wpp_signal = X265WppSignal(self, inputs_page_handlers)
        self.signals_list = (
            self.advanced_settings_signal, self.amp_signal, self.aq_signal, self.b_intra_signal,
            self.badapt_signal, self.bframes_signal, self.bitrate_signal, self.closed_gop_signal,
            self.crf_signal, self.cu_signal, self.deblock_signal, self.keyframe_signal,
            self.level_signal, self.me_signal, self.no_bpyramid_signal, self.no_high_tier_signal,
            self.no_scenecut_signal, self.no_weightp_signal, self.pme_signal, self.pmode_signal,
            self.preset_signal, self.profile_signal, self.psyrd_signal, self.qp_signal,
            self.rc_lookahead_signal, self.rd_signal, self.rect_signal, self.ref_signal,
            self.sao_signal, self.tune_signal, self.uhd_bluray_signal, self.vbv_signal,
            self.weightb_signal, self.wpp_signal
        )
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

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def apply_settings(self, ffmpeg):
        """Applies settings from the widgets to the ffmpeg settings object."""
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
        self._apply_rate_control_settings(video_settings)
        self._apply_advanced_settings(video_settings)
        ffmpeg.video_settings = video_settings

    def _apply_rate_control_settings(self, video_settings):
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

    def _apply_advanced_settings(self, video_settings):
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
            self._apply_deblock_settings(video_settings)
            self._apply_sao_settings(video_settings)

    def _apply_deblock_settings(self, video_settings):
        if self.x265_no_deblock_checkbox.get_active():
            video_settings.no_deblock = True
            video_settings.deblock = None
        else:
            video_settings.no_deblock = False
            alpha_value = self.x265_deblock_alpha_spinbutton.get_value_as_int()
            beta_value = self.x265_deblock_beta_spinbutton.get_value_as_int()
            video_settings.deblock = (alpha_value, beta_value)

    def _apply_sao_settings(self, video_settings):
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

    def set_settings(self, ffmpeg_param=None):
        """Sets widgets according to the ffmpeg settings object's settings."""
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        self._setup_x265_settings_widgets(ffmpeg)

    def _setup_x265_settings_widgets(self, ffmpeg):
        # Configures widgets using the ffmpeg settings object's settings.
        video_settings = ffmpeg.video_settings
        if video_settings is not None and video_settings.codec_name == 'libx265':
            self.is_widgets_setting_up = True
            self.x265_preset_combobox.set_active(video_settings.preset)
            self.x265_profile_combobox.set_active(video_settings.profile)
            self.x265_level_combobox.set_active(video_settings.level)
            self.x265_tune_combobox.set_active(video_settings.tune)
            self._setup_x265_rate_control_widgets(video_settings)
            self._setup_x265_encode_pass_widgets(video_settings)
            self._setup_x265_advanced_settings_widgets(video_settings)
            self.is_widgets_setting_up = False
        else:
            self.reset_settings()

    def _setup_x265_rate_control_widgets(self, video_settings):
        if video_settings.crf is not None:
            self.x265_crf_radiobutton.set_active(True)
            self.x265_crf_scale.set_value(video_settings.crf)
        elif video_settings.qp is not None:
            self.x265_qp_radio_button.set_active(True)
            self.x265_crf_scale.set_value(video_settings.qp)
        else:
            self.x265_bitrate_radiobutton.set_active(True)
            self.x265_bitrate_spinbutton.set_value(video_settings.bitrate)

    def _setup_x265_encode_pass_widgets(self, video_settings):
        if video_settings.encode_pass is not None:
            self.x265_2pass_radiobutton.set_active(True)
        else:
            self.x265_average_radiobutton.set_active(True)

    def _setup_x265_advanced_settings_widgets(self, video_settings):
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
        self._setup_x265_deblock_widgets(video_settings)
        self._setup_sao_widgets(video_settings)
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

    def _setup_x265_deblock_widgets(self, video_settings):
        if video_settings.no_deblock:
            self.x265_no_deblock_checkbox.set_active(True)
            self.x265_deblock_alpha_spinbutton.set_value(0)
            self.x265_deblock_beta_spinbutton.set_value(0)
        else:
            alpha_value, beta_value = video_settings.deblock
            self.x265_no_deblock_checkbox.set_active(False)
            self.x265_deblock_alpha_spinbutton.set_value(alpha_value)
            self.x265_deblock_beta_spinbutton.set_value(beta_value)

    def _setup_sao_widgets(self, video_settings):
        if not video_settings.no_sao:
            self.x265_sao_checkbox.set_active(True)
            self.x265_sao_nodeblock_checkbox.set_active(video_settings.sao_non_deblock)
            self.x265_sao_limit_checkbox.set_active(video_settings.limit_sao)
        else:
            self.x265_sao_checkbox.set_active(False)
            self.x265_sao_nodeblock_checkbox.set_active(False)
            self.x265_sao_limit_checkbox.set_active(False)
        self.x265_sao_selective_spinbutton.set_value(video_settings.selective_sao)

    def reset_settings(self):
        """Sets the page's widgets to their default values."""
        self.is_widgets_setting_up = True
        self.x265_profile_combobox.set_active(0)
        self.x265_preset_combobox.set_active(0)
        self.x265_level_combobox.set_active(0)
        self.x265_tune_combobox.set_active(0)
        self.x265_crf_radiobutton.set_active(True)
        self.x265_crf_scale.set_value(20.0)
        self._reset_advanced_settings_widgets()
        self.is_widgets_setting_up = False

    def _reset_advanced_settings_widgets(self):
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

    def get_crf_value(self):
        return self.x265_crf_scale.get_value()

    def get_bitrate_value(self):
        return self.x265_bitrate_spinbutton.get_value_as_int()

    def get_max_bitrate_value(self):
        return self.x265_vbv_maxrate_spinbutton.get_value_as_int()

    def get_bufsize_value(self):
        return self.x265_vbv_bufsize_spinbutton.get_value_as_int()

    def get_deblock_settings(self):
        if not self.is_deblock_enabled():
            return None

        alpha_value = self.x265_deblock_alpha_spinbutton.get_value_as_int()
        beta_value = self.x265_deblock_beta_spinbutton.get_value_as_int()

        return alpha_value, beta_value

    def get_selective_sao_value(self):
        return self.x265_sao_selective_spinbutton.get_value_as_int()

    def is_crf_enabled(self):
        return self.x265_crf_radiobutton.get_active()

    def is_vbr_enabled(self):
        return self.x265_average_radiobutton.get_active() or self.x265_2pass_radiobutton.get_active()

    def is_advanced_settings_enabled(self):
        return self.x265_advanced_settings_switch.get_active()

    def is_deblock_enabled(self):
        return not self.x265_no_deblock_checkbox.get_active()

    def is_sao_non_deblock_enabled(self):
        return self.x265_sao_nodeblock_checkbox.get_active()

    def is_limit_sao_enabled(self):
        return self.x265_sao_limit_checkbox.get_active()

    def set_crf_state(self):
        self.x265_rate_type_stack.set_visible_child(self.x265_crf_scale)
        self.x265_vbv_maxrate_spinbutton.set_sensitive(False)
        self.x265_vbv_bufsize_spinbutton.set_sensitive(False)

    def set_bitrate_state(self):
        self.x265_rate_type_stack.set_visible_child(self.x265_bitrate_box)
        self.x265_vbv_maxrate_spinbutton.set_sensitive(True)
        self.x265_vbv_bufsize_spinbutton.set_sensitive(True)

    def set_advanced_settings_state(self, enabled):
        self.x265_advanced_settings_revealer.set_reveal_child(enabled)

    def set_deblock_state(self, enabled):
        self.x265_deblock_alpha_spinbutton.set_sensitive(enabled)
        self.x265_deblock_beta_spinbutton.set_sensitive(enabled)

    def set_sao_state(self, enabled):
        self.x265_sao_options_box.set_sensitive(enabled)

    def update_vbr(self):
        bitrate_value = self.x265_bitrate_spinbutton.get_value_as_int()

        if bitrate_value > self.x265_vbv_maxrate_spinbutton.get_value_as_int():
            self.x265_vbv_maxrate_spinbutton.set_value(bitrate_value)
        else:
            self.signal_vbv_maxrate_spinbutton()

        self.signal_vbv_bufsize_spinbutton()

    def update_vbv_maxrate(self):
        bitrate_value = self.x265_bitrate_spinbutton.get_value_as_int()

        if bitrate_value > self.x265_vbv_maxrate_spinbutton.get_value_as_int():
            self.x265_vbv_maxrate_spinbutton.set_value(bitrate_value)

            return True

        return False

    def update_settings(self):
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg

            self.apply_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)

        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def signal_vbv_maxrate_spinbutton(self):
        self.vbv_signal.on_x265_vbv_maxrate_spinbutton_value_changed(self.x265_vbv_maxrate_spinbutton)

    def signal_vbv_bufsize_spinbutton(self):
        self.vbv_signal.on_x265_vbv_bufsize_spinbutton_value_changed(self.x265_vbv_bufsize_spinbutton)
