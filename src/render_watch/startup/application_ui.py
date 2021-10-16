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


import logging
import os

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.x265 import X265
from render_watch.ffmpeg.x264 import X264
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.ffmpeg.hevc_nvenc import HevcNvenc
from render_watch.ffmpeg.vp9 import VP9
from render_watch.ffmpeg.aac import Aac
from render_watch.ffmpeg.opus import Opus
from render_watch.app_handlers.handlers_manager import HandlersManager
from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.helpers.ui_helper import UIHelper
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.startup import Gtk


class ApplicationUI:
    """
    Sets up and runs the application's UI.
    """

    def __init__(self, encoder_queue, application_preferences):
        """
        Loads rw_ui.glade into Gtk.Builder and loads all the Gtk widgets.

        :param encoder_queue: Queue that the encoder pulls from.
        :param application_preferences: Application's preferences.
        """
        self.encoder_queue = encoder_queue
        self.application_preferences = application_preferences
        self._setup_gtk_builder()
        self.gtk_settings = Gtk.Settings.get_default()

    def _setup_gtk_builder(self):
        working_directory = os.path.dirname(os.path.abspath(__file__))
        glade_file_path = os.path.join(working_directory, '../render_watch_data/rw_ui.glade')

        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(glade_file_path)

    def setup_and_run(self):
        """
        Loads all widgets for the application's UI using Gtk.Builder and runs Gtk.main().
        """
        self._setup_preferences_dialog_widgets()
        self._setup_general_settings_widgets()
        self._setup_x264_widgets()
        self._setup_x265_widgets()
        self._setup_nvenc_widgets()
        self._setup_vp9_widgets()
        self._setup_aac_widgets()
        self._setup_opus_widgets()
        self._setup_main_window_widgets()

        self.gtk_builder.connect_signals(HandlersManager(self.gtk_builder,
                                                         self.gtk_settings,
                                                         self.encoder_queue,
                                                         self.application_preferences))

        return Gtk.main()

    def _setup_preferences_dialog_widgets(self):
        self._setup_preferences_dialog_parallel_tasks_widgets()
        self._setup_preferences_dialog_nvenc_concurrent_widgets()
        self._setup_preferences_dialog_temp_chooser_widgets()
        self._setup_preferences_dialog_clear_temp_widgets()
        self._setup_preferences_dialog_overwrite_outputs_widgets()
        self._setup_preferences_dialog_dark_mode_widgets()
        self._setup_preferences_dialog_watch_folder_wait_for_tasks_widgets()
        self._setup_preferences_dialog_watch_folder_concurrent_widgets()
        self._setup_preferences_dialog_watch_folder_move_to_done_widgets()

    def _setup_preferences_dialog_parallel_tasks_widgets(self):
        try:
            concurrent_tasks_combobox = self.gtk_builder.get_object('concurrent_tasks_combobox')
            UIHelper.setup_combobox(concurrent_tasks_combobox, ApplicationPreferences.PARALLEL_TASKS_VALUES)
            concurrent_tasks_message_stack = self.gtk_builder.get_object('concurrent_tasks_message_stack')
            concurrent_tasks_message_8 = self.gtk_builder.get_object('concurrent_tasks_message_8')
            concurrent_tasks_message_12 = self.gtk_builder.get_object('concurrent_tasks_message_12')
            concurrent_tasks_message_24 = self.gtk_builder.get_object('concurrent_tasks_message_24')
            concurrent_tasks_message_32 = self.gtk_builder.get_object('concurrent_tasks_message_32')
            concurrent_tasks_message_max = self.gtk_builder.get_object('concurrent_tasks_message_max')

            parallel_tasks = self.application_preferences.parallel_tasks_as_string
            concurrent_tasks_combobox.set_active(ApplicationPreferences.PARALLEL_TASKS_VALUES.index(parallel_tasks))
            if parallel_tasks == '2':
                concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_8)
            elif parallel_tasks == '3':
                concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_12)
            elif parallel_tasks == '4':
                concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_24)
            elif parallel_tasks == '6':
                concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_32)
            else:
                concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_max)
        except IndexError:
            logging.error('--- FAILED TO SETUP PARALLEL TASKS WIDGETS ---')

    def _setup_preferences_dialog_nvenc_concurrent_widgets(self):
        try:
            concurrent_nvenc_tasks_combobox = self.gtk_builder.get_object('concurrent_nvenc_tasks_combobox')
            UIHelper.setup_combobox(concurrent_nvenc_tasks_combobox, ApplicationPreferences.CONCURRENT_NVENC_VALUES)
            simultaneous_concurrent_nvenc_tasks_checkbox = self.gtk_builder.get_object(
                'simultaneous_concurrent_nvenc_tasks_checkbox')
            simultaneous_concurrent_nvenc_tasks_checkbox.set_active(
                self.application_preferences.is_concurrent_nvenc_enabled)
            concurrent_nvenc_tasks_warning_stack = self.gtk_builder.get_object('concurrent_nvenc_tasks_warning_stack')
            concurrent_nvenc_tasks_warning_blank_label = self.gtk_builder.get_object(
                'concurrent_nvenc_tasks_warning_blank_label')
            concurrent_nvenc_tasks_warning_icon = self.gtk_builder.get_object('concurrent_nvenc_tasks_warning_icon')

            concurrent_nvenc = self.application_preferences.concurrent_nvenc_value_as_string
            concurrent_nvenc_tasks_combobox.set_active(
                ApplicationPreferences.CONCURRENT_NVENC_VALUES.index(concurrent_nvenc))
            if concurrent_nvenc != 'auto':
                concurrent_nvenc_tasks_warning_stack.set_visible_child(concurrent_nvenc_tasks_warning_icon)
            else:
                concurrent_nvenc_tasks_warning_stack.set_visible_child(concurrent_nvenc_tasks_warning_blank_label)
        except IndexError:
            logging.error('--- FAILED TO SETUP NVENC PARALLEL TASKS WIDGETS ---')

    def _setup_preferences_dialog_temp_chooser_widgets(self):
        temporary_files_chooserbutton = self.gtk_builder.get_object('temporary_files_chooserbutton')
        temporary_files_chooserbutton.set_current_folder(self.application_preferences.temp_directory)

    def _setup_preferences_dialog_clear_temp_widgets(self):
        clear_temporary_files_checkbox = self.gtk_builder.get_object('clear_temporary_files_checkbox')
        clear_temporary_files_checkbox.set_active(self.application_preferences.is_clearing_temp_directory)

    def _setup_preferences_dialog_overwrite_outputs_widgets(self):
        overwrite_outputs_checkbox = self.gtk_builder.get_object('overwrite_outputs_checkbox')
        overwrite_outputs_checkbox.set_active(self.application_preferences.is_overwriting_outputs)

    def _setup_preferences_dialog_dark_mode_widgets(self):
        dark_mode_switch = self.gtk_builder.get_object('dark_mode_switch')
        dark_mode_switch.set_active(self.application_preferences.is_dark_mode)
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", self.application_preferences.is_dark_mode)

    def _setup_preferences_dialog_watch_folder_wait_for_tasks_widgets(self):
        wait_for_tasks_checkbox = self.gtk_builder.get_object('wait_for_tasks_checkbox')
        wait_for_tasks_checkbox.set_active(self.application_preferences.is_watch_folder_wait_for_tasks_enabled)

    def _setup_preferences_dialog_watch_folder_concurrent_widgets(self):
        run_concurrently_checkbox = self.gtk_builder.get_object('run_concurrently_checkbox')
        run_concurrently_checkbox.set_active(self.application_preferences.is_concurrent_watch_folder_enabled)

    def _setup_preferences_dialog_watch_folder_move_to_done_widgets(self):
        move_to_done_checkbox = self.gtk_builder.get_object('move_to_done_checkbox')
        move_to_done_checkbox.set_active(self.application_preferences.is_watch_folder_move_tasks_to_done_enabled)

    def _setup_general_settings_widgets(self):
        self._setup_video_container_widgets()
        self._setup_video_codec_widgets()
        self._setup_audio_codec_widgets()
        self._setup_frame_rate_widgets()

    def _setup_video_container_widgets(self):
        container_combobox = self.gtk_builder.get_object("container_combobox")
        UIHelper.setup_combobox(container_combobox, GeneralSettings.CONTAINERS_UI_LIST)

    def _setup_video_codec_widgets(self):
        video_codec_combobox = self.gtk_builder.get_object("video_codec_combobox")

        if NvidiaHelper.is_nvenc_supported():
            video_codec_list = GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST
        else:
            video_codec_list = GeneralSettings.VIDEO_CODEC_MP4_UI_LIST
        UIHelper.setup_combobox(video_codec_combobox, video_codec_list)

    def _setup_audio_codec_widgets(self):
        audio_codec_combobox = self.gtk_builder.get_object("audio_codec_combobox")
        UIHelper.setup_combobox(audio_codec_combobox, GeneralSettings.AUDIO_CODEC_MP4_UI_LIST)

    def _setup_frame_rate_widgets(self):
        fps_combobox = self.gtk_builder.get_object("fps_combobox")
        UIHelper.setup_combobox(fps_combobox, GeneralSettings.FRAME_RATE_ARGS_LIST)

    def _setup_x264_widgets(self):
        self._setup_x264_preset_widgets()
        self._setup_x264_profile_widgets()
        self._setup_x264_level_widgets()
        self._setup_x264_tune_widgets()
        self._setup_x264_aq_mode_widgets()
        self._setup_x264_b_adapt_widgets()
        self._setup_x264_b_pyramid_widgets()
        self._setup_x264_weight_p_widgets()
        self._setup_x264_me_widgets()
        self._setup_x264_subme_widgets()
        self._setup_x264_trellis_widgets()
        self._setup_x264_direct_widgets()

    def _setup_x264_preset_widgets(self):
        x264_preset_combobox = self.gtk_builder.get_object("x264_preset_combobox")
        UIHelper.setup_combobox(x264_preset_combobox, X264.PRESET_ARGS_LIST)

    def _setup_x264_profile_widgets(self):
        x264_profile_combobox = self.gtk_builder.get_object("x264_profile_combobox")
        UIHelper.setup_combobox(x264_profile_combobox, X264.PROFILE_ARGS_LIST)

    def _setup_x264_level_widgets(self):
        x264_level_combobox = self.gtk_builder.get_object("x264_level_combobox")
        UIHelper.setup_combobox(x264_level_combobox, X264.LEVEL_ARGS_LIST)

    def _setup_x264_tune_widgets(self):
        x264_tune_combobox = self.gtk_builder.get_object("x264_tune_combobox")
        UIHelper.setup_combobox(x264_tune_combobox, X264.TUNE_ARGS_LIST)

    def _setup_x264_aq_mode_widgets(self):
        x264_aq_mode_combobox = self.gtk_builder.get_object('x264_aq_mode_combobox')
        UIHelper.setup_combobox(x264_aq_mode_combobox, X264.AQ_MODE_UI_LIST)

    def _setup_x264_b_adapt_widgets(self):
        x264_b_adapt_combobox = self.gtk_builder.get_object('x264_b_adapt_combobox')
        UIHelper.setup_combobox(x264_b_adapt_combobox, X264.B_ADAPT_UI_LIST)

    def _setup_x264_b_pyramid_widgets(self):
        x264_b_pyramid_combobox = self.gtk_builder.get_object('x264_b_pyramid_combobox')
        UIHelper.setup_combobox(x264_b_pyramid_combobox, X264.B_PYRAMID_UI_LIST)

    def _setup_x264_weight_p_widgets(self):
        x264_weight_p_combobox = self.gtk_builder.get_object('x264_weight_p_combobox')
        UIHelper.setup_combobox(x264_weight_p_combobox, X264.WEIGHT_P_UI_LIST)

    def _setup_x264_me_widgets(self):
        x264_me_combobox = self.gtk_builder.get_object('x264_me_combobox')
        UIHelper.setup_combobox(x264_me_combobox, X264.ME_ARGS_LIST)

    def _setup_x264_subme_widgets(self):
        x264_subme_combobox = self.gtk_builder.get_object('x264_subme_combobox')
        UIHelper.setup_combobox(x264_subme_combobox, X264.SUB_ME_UI_LIST)

    def _setup_x264_trellis_widgets(self):
        x264_trellis_combobox = self.gtk_builder.get_object('x264_trellis_combobox')
        UIHelper.setup_combobox(x264_trellis_combobox, X264.TRELLIS_UI_LIST)

    def _setup_x264_direct_widgets(self):
        x264_direct_combobox = self.gtk_builder.get_object('x264_direct_combobox')
        UIHelper.setup_combobox(x264_direct_combobox, X264.DIRECT_UI_LIST)

    def _setup_x265_widgets(self):
        self._setup_x265_preset_widgets()
        self._setup_x265_profile_widgets()
        self._setup_x265_level_widgets()
        self._setup_x265_tune_widgets()
        self._setup_x265_aq_mode_widgets()
        self._setup_x265_b_adapt_widgets()
        self._setup_x265_me_widgets()
        self._setup_x265_rdoq_level_widgets()
        self._setup_x265_max_cu_widgets()
        self._setup_x265_min_cu_widgets()

    def _setup_x265_preset_widgets(self):
        x265_preset_combobox = self.gtk_builder.get_object("x265_preset_combobox")
        UIHelper.setup_combobox(x265_preset_combobox, X265.PRESET_ARGS_LIST)

    def _setup_x265_profile_widgets(self):
        x265_profile_combobox = self.gtk_builder.get_object("x265_profile_combobox")
        UIHelper.setup_combobox(x265_profile_combobox, X265.PROFILE_ARGS_LIST)

    def _setup_x265_level_widgets(self):
        x265_level_combobox = self.gtk_builder.get_object("x265_level_combobox")
        UIHelper.setup_combobox(x265_level_combobox, X265.LEVEL_ARGS_LIST)

    def _setup_x265_tune_widgets(self):
        x265_tune_combobox = self.gtk_builder.get_object("x265_tune_combobox")
        UIHelper.setup_combobox(x265_tune_combobox, X265.TUNE_ARGS_LIST)

    def _setup_x265_aq_mode_widgets(self):
        x265_aq_mode_combobox = self.gtk_builder.get_object('x265_aq_mode_combobox')
        UIHelper.setup_combobox(x265_aq_mode_combobox, X265.AQ_MODE_UI_LIST)

    def _setup_x265_b_adapt_widgets(self):
        x265_b_adapt_combobox = self.gtk_builder.get_object('x265_b_adapt_combobox')
        UIHelper.setup_combobox(x265_b_adapt_combobox, X265.B_ADAPT_UI_LIST)

    def _setup_x265_me_widgets(self):
        x265_me_combobox = self.gtk_builder.get_object('x265_me_combobox')
        UIHelper.setup_combobox(x265_me_combobox, X265.ME_ARGS_LIST)

    def _setup_x265_rdoq_level_widgets(self):
        x265_rdoq_level_combobox = self.gtk_builder.get_object('x265_rdoq_level_combobox')
        UIHelper.setup_combobox(x265_rdoq_level_combobox, X265.RDOQ_LEVEL_UI_LIST)

    def _setup_x265_max_cu_widgets(self):
        x265_max_cu_combobox = self.gtk_builder.get_object('x265_max_cu_combobox')
        UIHelper.setup_combobox(x265_max_cu_combobox, X265.MAX_CU_SIZE_ARGS_LIST)

    def _setup_x265_min_cu_widgets(self):
        x265_min_cu_combobox = self.gtk_builder.get_object('x265_min_cu_combobox')
        UIHelper.setup_combobox(x265_min_cu_combobox, X265.MIN_CU_SIZE_ARGS_LIST)

    def _setup_nvenc_widgets(self):
        self._setup_nvenc_profile_widgets()
        self._setup_nvenc_preset_widgets()
        self._setup_nvenc_tune_widgets()
        self._setup_nvenc_level_widgets()
        self._setup_nvenc_rate_control_widgets()
        self._setup_nvenc_tier_widgets()
        self._setup_nvenc_rc_lookahead_widgets()
        self._setup_nvenc_surfaces_widgets()
        self._setup_nvenc_no_scenecut_widgets()
        self._setup_nvenc_forced_idr_widgets()
        self._setup_nvenc_aq_widgets()
        self._setup_nvenc_non_ref_p_widgets()
        self._setup_nvenc_strict_gop_widgets()
        self._setup_nvenc_bluray_compat_widgets()
        self._setup_nvenc_init_qp_widgets()
        self._setup_nvenc_weighted_pred_widgets()
        self._setup_nvenc_b_ref_mode_widgets()
        self._setup_nvenc_multipass_widgets()
        self._setup_nvenc_b_adapt_widgets()
        self._setup_nvenc_coder_widgets()

    def _setup_nvenc_profile_widgets(self):
        nvenc_profile_combobox = self.gtk_builder.get_object('nvenc_profile_combobox')
        nvenc_profile_combobox.set_sensitive('-profile' in H264Nvenc.OPTIONS and '-profile' in HevcNvenc.OPTIONS)

    def _setup_nvenc_preset_widgets(self):
        nvenc_preset_combobox = self.gtk_builder.get_object('nvenc_preset_combobox')
        nvenc_preset_combobox.set_sensitive('-preset' in H264Nvenc.OPTIONS and '-preset' in HevcNvenc.OPTIONS)

    def _setup_nvenc_tune_widgets(self):
        nvenc_tune_combobox = self.gtk_builder.get_object('nvenc_tune_combobox')
        nvenc_tune_combobox.set_sensitive('-tune' in H264Nvenc.OPTIONS and '-tune' in HevcNvenc.OPTIONS)

    def _setup_nvenc_level_widgets(self):
        nvenc_level_combobox = self.gtk_builder.get_object('nvenc_level_combobox')
        nvenc_level_combobox.set_sensitive('-level' in H264Nvenc.OPTIONS and '-level' in HevcNvenc.OPTIONS)

    def _setup_nvenc_rate_control_widgets(self):
        nvenc_rate_control_combobox = self.gtk_builder.get_object('nvenc_rate_control_combobox')
        nvenc_rate_control_combobox.set_sensitive('-rc' in H264Nvenc.OPTIONS and '-rc' in HevcNvenc.OPTIONS)

    def _setup_nvenc_tier_widgets(self):
        nvenc_tier_box = self.gtk_builder.get_object('nvenc_tier_box')
        nvenc_tier_box.set_sensitive('-tier' in HevcNvenc.OPTIONS)

    def _setup_nvenc_rc_lookahead_widgets(self):
        nvenc_rc_lookahead_spinbutton = self.gtk_builder.get_object('nvenc_rate_control_lookahead_spinbutton')
        nvenc_rc_lookahead_spinbutton.set_sensitive('-rc-lookahead' in H264Nvenc.OPTIONS
                                                    and '-rc-lookahead' in HevcNvenc.OPTIONS)

    def _setup_nvenc_surfaces_widgets(self):
        nvenc_surfaces_spinbutton = self.gtk_builder.get_object('nvenc_surfaces_spinbutton')
        nvenc_surfaces_spinbutton.set_sensitive('-surfaces' in H264Nvenc.OPTIONS and '-surfaces' in HevcNvenc.OPTIONS)

    def _setup_nvenc_no_scenecut_widgets(self):
        nvenc_no_scenecut_checkbutton = self.gtk_builder.get_object('nvenc_no_scenecut_checkbutton')
        nvenc_no_scenecut_checkbutton.set_sensitive('-no-scenecut' in H264Nvenc.OPTIONS
                                                    and '-no-scenecut' in HevcNvenc.OPTIONS)

    def _setup_nvenc_forced_idr_widgets(self):
        nvenc_forced_idr_checkbutton = self.gtk_builder.get_object('nvenc_forced_idr_checkbutton')
        nvenc_forced_idr_checkbutton.set_sensitive('-forced-idr' in H264Nvenc.OPTIONS
                                                   and '-forced-idr' in HevcNvenc.OPTIONS)

    def _setup_nvenc_aq_widgets(self):
        nvenc_aq_type_box = self.gtk_builder.get_object('nvenc_aq_type_box')
        nvenc_aq_type_box.set_sensitive('-spatial-aq' in H264Nvenc.OPTIONS
                                        and '-spatial-aq' in HevcNvenc.OPTIONS
                                        and '-temporal-aq' in H264Nvenc.OPTIONS
                                        and '-temporal-aq' in HevcNvenc.OPTIONS)
        nvenc_aq_strength_spinbutton = self.gtk_builder.get_object('nvenc_aq_strength_spinbutton')
        nvenc_aq_strength_spinbutton.set_sensitive('-aq-strength' in H264Nvenc.OPTIONS
                                                   and '-aq-strength' in HevcNvenc.OPTIONS)

    def _setup_nvenc_non_ref_p_widgets(self):
        nvenc_non_ref_p_checkbutton = self.gtk_builder.get_object('nvenc_nonref_p_frames_checkbutton')
        nvenc_non_ref_p_checkbutton.set_sensitive('-nonref_p' in H264Nvenc.OPTIONS and '-nonref_p' in HevcNvenc.OPTIONS)

    def _setup_nvenc_strict_gop_widgets(self):
        nvenc_strict_gop_checkbutton = self.gtk_builder.get_object('nvenc_strict_gop_checkbutton')
        nvenc_strict_gop_checkbutton.set_sensitive('-strict_gop' in H264Nvenc.OPTIONS
                                                   and '-strict_gop' in HevcNvenc.OPTIONS)

    def _setup_nvenc_bluray_compat_widgets(self):
        nvenc_bluray_compat_checkbutton = self.gtk_builder.get_object('nvenc_bluray_compat_checkbutton')
        nvenc_bluray_compat_checkbutton.set_sensitive('-bluray-compat' in H264Nvenc.OPTIONS
                                                      and '-bluray-compat' in HevcNvenc.OPTIONS)

    def _setup_nvenc_init_qp_widgets(self):
        nvenc_qp_init_enabled_box = self.gtk_builder.get_object('nvenc_qp_init_enabled_box')
        nvenc_qp_i_scale = self.gtk_builder.get_object('nvenc_qp_i_scale')
        nvenc_qp_p_scale = self.gtk_builder.get_object('nvenc_qp_p_scale')
        nvenc_qp_b_scale = self.gtk_builder.get_object('nvenc_qp_b_scale')

        is_widgets_sensitive = '-init_qpI' in H264Nvenc.OPTIONS and '-init_qpI' in HevcNvenc.OPTIONS \
                               and '-init_qpP' in H264Nvenc.OPTIONS and '-init_qpP' in HevcNvenc.OPTIONS \
                               and '-init_qpB' in H264Nvenc.OPTIONS and '-init_qpB' in HevcNvenc.OPTIONS
        nvenc_qp_init_enabled_box.set_sensitive(is_widgets_sensitive)
        nvenc_qp_i_scale.set_sensitive(is_widgets_sensitive)
        nvenc_qp_p_scale.set_sensitive(is_widgets_sensitive)
        nvenc_qp_b_scale.set_sensitive(is_widgets_sensitive)

    def _setup_nvenc_weighted_pred_widgets(self):
        nvenc_weighted_prediction_checkbutton = self.gtk_builder.get_object('nvenc_weighted_prediction_checkbutton')
        nvenc_weighted_prediction_checkbutton.set_sensitive('-weighted_pred' in H264Nvenc.OPTIONS
                                                            and '-weighted_pred' in HevcNvenc.OPTIONS)

    def _setup_nvenc_b_ref_mode_widgets(self):
        nvenc_b_ref_mode_combobox = self.gtk_builder.get_object('nvenc_b_ref_mode_combobox')
        nvenc_b_ref_mode_combobox.set_sensitive('-b_ref_mode' in H264Nvenc.OPTIONS
                                                and '-b_ref_mode' in HevcNvenc.OPTIONS)

    def _setup_nvenc_multipass_widgets(self):
        nvenc_multi_pass_combobox = self.gtk_builder.get_object('nvenc_multi_pass_combobox')
        nvenc_multi_pass_combobox.set_sensitive('-multipass' in H264Nvenc.OPTIONS and '-multipass' in HevcNvenc.OPTIONS)

    def _setup_nvenc_b_adapt_widgets(self):
        nvenc_b_adapt_checkbutton = self.gtk_builder.get_object('nvenc_b_adapt_checkbutton')
        nvenc_b_adapt_checkbutton.set_sensitive('-b_adapt' in H264Nvenc.OPTIONS)

    def _setup_nvenc_coder_widgets(self):
        if '-coder' in H264Nvenc.OPTIONS:
            nvenc_coder_combobox = self.gtk_builder.get_object('nvenc_coder_combobox')
            UIHelper.setup_combobox(nvenc_coder_combobox, H264Nvenc.OPTIONS['-coder'])

    def _setup_vp9_widgets(self):
        self._setup_vp9_quality_widgets()
        self._setup_vp9_speed_widgets()

    def _setup_vp9_quality_widgets(self):
        vp9_quality_combobox = self.gtk_builder.get_object('vp9_quality_combobox')
        UIHelper.setup_combobox(vp9_quality_combobox, VP9.QUALITY_ARGS_LIST)

    def _setup_vp9_speed_widgets(self):
        vp9_speed_combobox = self.gtk_builder.get_object('vp9_speed_combobox')
        UIHelper.setup_combobox(vp9_speed_combobox, VP9.SPEED_ARGS_LIST)

    def _setup_aac_widgets(self):
        self._setup_aac_channels_widgets()

    def _setup_aac_channels_widgets(self):
        aac_channels_combobox = self.gtk_builder.get_object("aac_channels_combobox")
        UIHelper.setup_combobox(aac_channels_combobox, Aac.CHANNELS_UI_LIST)

    def _setup_opus_widgets(self):
        self._setup_opus_channels_widgets()

    def _setup_opus_channels_widgets(self):
        opus_channels_combobox = self.gtk_builder.get_object('opus_channels_combobox')
        UIHelper.setup_combobox(opus_channels_combobox, Opus.CHANNELS_UI_LIST)

    def _setup_main_window_widgets(self):
        self._setup_main_window_output_chooser_widgets()
        self._setup_and_show_main_window()

    def _setup_main_window_output_chooser_widgets(self):
        output_chooserbutton = self.gtk_builder.get_object('output_directory_chooserbutton')
        output_chooserbutton.set_current_folder(self.application_preferences.output_directory)

    def _setup_and_show_main_window(self):
        try:
            main_window = self.gtk_builder.get_object('main_window')
            self._setup_main_window_dimensions(main_window)
        except:
            logging.critical('--- FAILED TO SETUP AND SHOW MAIN WINDOW ---')
        else:
            main_window.connect('size-allocate', self._on_main_window_size_allocate)
            main_window.connect('destroy', self._on_main_window_destroy)

            main_window.show_all()

    def _setup_main_window_dimensions(self, main_window):
        window_dimensions = self.application_preferences.window_dimensions
        main_window.set_size_request(800, 500)
        main_window.resize(window_dimensions[0], window_dimensions[1])

        if self.application_preferences.is_window_maximized:
            main_window.maximize()

    def _on_main_window_size_allocate(self, application_window, allocation):  # Unused parameter needed for this signal.
        if application_window.is_maximized():
            return

        application_window_size = application_window.get_size()
        self.application_preferences.window_dimensions = (application_window_size[0], application_window_size[1])

    def _on_main_window_destroy(self, application_window):
        self._save_application_preferences(application_window)
        self.encoder_queue.kill()
        Gtk.main_quit()

    def _save_application_preferences(self, application_window):
        self.application_preferences.is_window_maximized = application_window.is_maximized()

        ApplicationPreferences.save_preferences(self.application_preferences)
        ApplicationPreferences.clear_temp_directory(self.application_preferences)
