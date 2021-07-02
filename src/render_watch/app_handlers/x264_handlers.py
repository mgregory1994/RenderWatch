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


from render_watch.ffmpeg.x264 import X264
from render_watch.signals.x264.x264_8x8dct_signal import X2648x8DctSignal
from render_watch.signals.x264.x264_advanced_settings_signal import X264AdvancedSettingsSignal
from render_watch.signals.x264.x264_aq_signal import X264AqSignal
from render_watch.signals.x264.x264_badapt_signal import X264BAdaptSignal
from render_watch.signals.x264.x264_bframes_signal import X264BFramesSignal
from render_watch.signals.x264.x264_bitrate_signal import X264BitrateSignal
from render_watch.signals.x264.x264_bpyramid_signal import X264BPyramidSignal
from render_watch.signals.x264.x264_crf_signal import X264CrfSignal
from render_watch.signals.x264.x264_deblock_signal import X264DeblockSignal
from render_watch.signals.x264.x264_direct_signal import X264DirectSignal
from render_watch.signals.x264.x264_keyframe_signal import X264KeyframeSignal
from render_watch.signals.x264.x264_level_signal import X264LevelSignal
from render_watch.signals.x264.x264_me_signal import X264MeSignal
from render_watch.signals.x264.x264_no_cabac_signal import X264NoCabacSignal
from render_watch.signals.x264.x264_no_dct_decimate_signal import X264NoDctDecimateSignal
from render_watch.signals.x264.x264_no_fast_pskip_signal import X264NoFastPSkipSignal
from render_watch.signals.x264.x264_partitions_signal import X264PartitionsSignal
from render_watch.signals.x264.x264_preset_signal import X264PresetSignal
from render_watch.signals.x264.x264_profile_signal import X264ProfileSignal
from render_watch.signals.x264.x264_psyrd_signal import X264PsyRDSignal
from render_watch.signals.x264.x264_qp_signal import X264QpSignal
from render_watch.signals.x264.x264_refs_signal import X264RefsSignal
from render_watch.signals.x264.x264_trellis_signal import X264TrellisSignal
from render_watch.signals.x264.x264_tune_signal import X264TuneSignal
from render_watch.signals.x264.x264_vbv_signal import X264VbvSignal
from render_watch.signals.x264.x264_weightb_signal import X264WeightBSignal
from render_watch.signals.x264.x264_weightp_signal import X264WeightPSignal
from render_watch.startup import GLib


class X264Handlers:
    """Handles all widget changes for the x264 codec."""

    def __init__(self, gtk_builder, inputs_page_handlers, preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences
        self.is_widgets_setting_up = False
        self.x264_8x8dct_signal = X2648x8DctSignal(self, inputs_page_handlers)
        self.x264_advanced_settings_signal = X264AdvancedSettingsSignal(self, inputs_page_handlers)
        self.x264_aq_signal = X264AqSignal(self, inputs_page_handlers)
        self.x264_badapt_signal = X264BAdaptSignal(self, inputs_page_handlers)
        self.x264_bframes_signal = X264BFramesSignal(self, inputs_page_handlers)
        self.x264_bitrate_signal = X264BitrateSignal(self, inputs_page_handlers, preferences)
        self.x264_bpyramid_signal = X264BPyramidSignal(self, inputs_page_handlers)
        self.x264_crf_signal = X264CrfSignal(self, inputs_page_handlers)
        self.x264_deblock_signal = X264DeblockSignal(self, inputs_page_handlers)
        self.x264_direct_signal = X264DirectSignal(self, inputs_page_handlers)
        self.x264_keyframe_signal = X264KeyframeSignal(self, inputs_page_handlers)
        self.x264_level_signal = X264LevelSignal(self, inputs_page_handlers)
        self.x264_me_signal = X264MeSignal(self, inputs_page_handlers)
        self.x264_no_cabac_signal = X264NoCabacSignal(self, inputs_page_handlers)
        self.x264_no_dct_decimate_signal = X264NoDctDecimateSignal(self, inputs_page_handlers)
        self.x264_no_fast_pskip_signal = X264NoFastPSkipSignal(self, inputs_page_handlers)
        self.x264_partitions_signal = X264PartitionsSignal(self, inputs_page_handlers)
        self.x264_preset_signal = X264PresetSignal(self, inputs_page_handlers)
        self.x264_profile_signal = X264ProfileSignal(self, inputs_page_handlers)
        self.x264_psyrd_signal = X264PsyRDSignal(self, inputs_page_handlers)
        self.x264_qp_signal = X264QpSignal(self, inputs_page_handlers)
        self.x264_refs_signal = X264RefsSignal(self, inputs_page_handlers)
        self.x264_trellis_signal = X264TrellisSignal(self, inputs_page_handlers)
        self.x264_tune_signal = X264TuneSignal(self, inputs_page_handlers)
        self.x264_vbv_signal = X264VbvSignal(self, inputs_page_handlers)
        self.x264_weightb_signal = X264WeightBSignal(self, inputs_page_handlers)
        self.x264_weightp_signal = X264WeightPSignal(self, inputs_page_handlers)
        self.signals_list = (
            self.x264_8x8dct_signal, self.x264_advanced_settings_signal, self.x264_aq_signal,
            self.x264_badapt_signal, self.x264_bframes_signal, self.x264_bitrate_signal,
            self.x264_bpyramid_signal, self.x264_crf_signal, self.x264_deblock_signal,
            self.x264_direct_signal, self.x264_keyframe_signal, self.x264_level_signal,
            self.x264_me_signal, self.x264_no_cabac_signal, self.x264_no_dct_decimate_signal,
            self.x264_no_fast_pskip_signal, self.x264_partitions_signal, self.x264_preset_signal,
            self.x264_profile_signal, self.x264_psyrd_signal, self.x264_qp_signal,
            self.x264_refs_signal, self.x264_trellis_signal, self.x264_tune_signal,
            self.x264_vbv_signal, self.x264_weightp_signal, self.x264_weightb_signal
        )
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
        video_settings = X264()
        video_settings.preset = self.x264_preset_combobox.get_active()
        video_settings.profile = self.x264_profile_combobox.get_active()
        video_settings.level = self.x264_level_combobox.get_active()
        video_settings.tune = self.x264_tune_combobox.get_active()
        self._apply_rate_control_settings(video_settings)
        self._apply_advanced_settings(video_settings)
        ffmpeg.video_settings = video_settings

    def _apply_rate_control_settings(self, video_settings):
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

    def _apply_advanced_settings(self, video_settings):
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
            self._apply_deblock_settings(video_settings)
            self._apply_partitions_settings(video_settings)

    def _apply_deblock_settings(self, video_settings):
        if self.x264_no_deblock_checkbox.get_active():
            video_settings.no_deblock = True
            video_settings.deblock = None
        else:
            video_settings.no_deblock = False
            video_settings.deblock = (self.x264_deblock_alpha_spinbutton.get_value_as_int(),
                                      self.x264_deblock_beta_spinbutton.get_value_as_int())

    def _apply_partitions_settings(self, video_settings):
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

    def set_settings(self, ffmpeg_param=None):
        """Sets widgets according to the ffmpeg settings object's settings."""
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        self._setup_x264_settings_widgets(ffmpeg)

    def _setup_x264_settings_widgets(self, ffmpeg):
        # Configures widgets using the ffmpeg settings object's settings.
        if ffmpeg.is_video_settings_x264():
            video_settings = ffmpeg.video_settings
            self.is_widgets_setting_up = True
            self.x264_preset_combobox.set_active(video_settings.preset)
            self.x264_profile_combobox.set_active(video_settings.profile)
            self.x264_level_combobox.set_active(video_settings.level)
            self.x264_tune_combobox.set_active(video_settings.tune)
            self._setup_x264_rate_control_widgets(video_settings)
            self._setup_x264_advanced_settings_widgets(video_settings)
            self.is_widgets_setting_up = False
        else:
            self.reset_settings()

    def _setup_x264_rate_control_widgets(self, video_settings):
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

    def _setup_x264_advanced_settings_widgets(self, video_settings):
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
        self._setup_x264_partitions_widgets(video_settings)
        self.x264_8x8dct_checkbox.set_active(video_settings.dct8x8)
        self._setup_x264_psy_rd_widgets(video_settings)
        self.x264_trellis_combobox.set_active(video_settings.trellis)
        self.x264_direct_combobox.set_active(video_settings.direct)
        self._setup_x264_deblock_widgets(video_settings)
        self.x264_no_fast_pskip_checkbox.set_active(video_settings.no_fast_pskip)
        self.x264_no_dct_decimate_checkbox.set_active(video_settings.no_dct_decimate)
        self.x264_no_cabac_checkbox.set_active(video_settings.no_cabac)

    def _setup_x264_partitions_widgets(self, video_settings):
        if video_settings.partitions:
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

    def _setup_x264_psy_rd_widgets(self, video_settings):
        psy_rd = video_settings.psy_rd
        psy_rd_value = psy_rd[0]
        psy_rd_trellis_value = psy_rd[1]
        self.x264_psy_rd_spinbutton.set_value(psy_rd_value)
        self.x264_psy_rd_trellis_spinbutton.set_value(psy_rd_trellis_value)

    def _setup_x264_deblock_widgets(self, video_settings):
        if video_settings.no_deblock:
            self.x264_no_deblock_checkbox.set_active(True)
            self.x264_deblock_alpha_spinbutton.set_value(0)
            self.x264_deblock_beta_spinbutton.set_value(0)
        else:
            alpha_value, beta_value = video_settings.deblock
            self.x264_no_deblock_checkbox.set_active(False)
            self.x264_deblock_alpha_spinbutton.set_value(alpha_value)
            self.x264_deblock_beta_spinbutton.set_value(beta_value)

    def reset_settings(self):
        """Sets the page's widgets to their default values."""
        self.is_widgets_setting_up = True
        self.x264_profile_combobox.set_active(0)
        self.x264_preset_combobox.set_active(0)
        self.x264_level_combobox.set_active(0)
        self.x264_tune_combobox.set_active(0)
        self.x264_crf_radiobutton.set_active(True)
        self.x264_crf_scale.set_value(20.0)
        self.x264_bitrate_spinbutton.set_value(2500)
        self.x264_average_radiobutton.set_active(True)
        self._reset_advanced_settings_widgets()
        self.is_widgets_setting_up = False

    def _reset_advanced_settings_widgets(self):
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

    def get_crf_value(self):
        return self.x264_crf_scale.get_value()

    def get_bitrate_value(self):
        return self.x264_bitrate_spinbutton.get_value_as_int()

    def get_partitions_settings(self):
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

    def get_psy_rd_value(self):
        return self.x264_psy_rd_spinbutton.get_value()

    def get_psy_rd_trellis_value(self):
        return self.x264_psy_rd_trellis_spinbutton.get_value()

    def get_deblock_settings(self):
        if self.x264_no_deblock_checkbox.get_active():
            return None
        alpha_value = self.x264_deblock_alpha_spinbutton.get_value_as_int()
        beta_value = self.x264_deblock_beta_spinbutton.get_value_as_int()
        return alpha_value, beta_value

    def is_crf_enabled(self):
        return self.x264_crf_radiobutton.get_active()

    def is_vbr_enabled(self):
        return self.x264_average_radiobutton.get_active() or self.x264_2pass_radiobutton.get_active()

    def is_advanced_settings_enabled(self):
        return self.x264_advanced_settings_switch.get_active()

    def set_crf_state(self):
        self.x264_rate_type_stack.set_visible_child(self.x264_crf_scale)
        self.x264_vbv_max_rate_spinbutton.set_sensitive(False)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(False)

    def set_bitrate_state(self):
        self.x264_rate_type_stack.set_visible_child(self.x264_bitrate_box)

    def set_vbr_state(self, enabled):
        self.x264_vbv_max_rate_spinbutton.set_sensitive(enabled)
        self.x264_vbv_bufsize_spinbutton.set_sensitive(enabled)

    def set_advanced_settings_state(self, enabled):
        self.x264_advanced_settings_revealer.set_reveal_child(enabled)

    def set_partitions_custom_state(self, enabled):
        self.x264_partitions_types_grid.set_sensitive(enabled)

    def set_deblock_state(self, enabled):
        self.x264_deblock_alpha_spinbutton.set_sensitive(enabled)
        self.x264_deblock_beta_spinbutton.set_sensitive(enabled)

    def update_vbr(self):
        bitrate_value = self.get_bitrate_value()
        if bitrate_value > self.x264_vbv_max_rate_spinbutton.get_value_as_int():
            self.x264_vbv_max_rate_spinbutton.set_value(bitrate_value)
        else:
            self.on_x264_vbv_max_rate_spinbutton_value_changed(self.x264_vbv_max_rate_spinbutton)
        self.on_x264_vbv_bufsize_spinbutton_value_changed(self.x264_vbv_bufsize_spinbutton)

    def update_vbv_maxrate(self):
        bitrate_value = self.get_bitrate_value()
        if bitrate_value > self.x264_vbv_max_rate_spinbutton.get_value_as_int():
            self.x264_vbv_max_rate_spinbutton.set_value(bitrate_value)
            return True
        return False

    def update_settings(self):
        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            self.apply_settings(ffmpeg)
            GLib.idle_add(row.setup_labels)
        GLib.idle_add(self.inputs_page_handlers.update_preview_page)

    def signal_average_radiobutton(self):
        self.x264_bitrate_signal.on_x264_average_radiobutton_toggled(self.x264_average_radiobutton)

    def signal_constant_radiobutton(self):
        self.x264_bitrate_signal.on_x264_constant_radiobutton_toggled(self.x264_constant_radiobutton)

    def signal_2pass_radiobutton(self):
        self.x264_bitrate_signal.on_x264_2pass_radiobutton_toggled(self.x264_2pass_radiobutton)
