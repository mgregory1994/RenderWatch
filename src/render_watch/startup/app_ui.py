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
from render_watch.startup.preferences import Preferences
from render_watch.helpers.ui_helper import UIHelper
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.startup import Gtk


class AppUI:
    """Allows for instantiating, setting up, and running the UI."""

    def __init__(self, encoder_queue, preferences):
        """Initializes the class and it's needed variables.

        This also initializes Gtk settings and Gtk builder in order to further setup the application's UI.

        :param encoder_queue:
            Initialized encoder queue object.
        :param preferences:
            Application's preferences object.
        """
        self.encoder_queue = encoder_queue
        self.preferences = preferences
        self.__setup_application_gtk_builder()

    def __setup_application_gtk_builder(self):
        # Load the glade UI file into Gtk builder and instantiate Gtk settings.
        this_file_directory_file_path = os.path.dirname(os.path.abspath(__file__))
        rw_ui_file_path = os.path.join(this_file_directory_file_path, '../render_watch_data/rw_ui.glade')

        self.gtk_settings = Gtk.Settings.get_default()
        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(rw_ui_file_path)

    def setup_and_run_application(self):
        """Instantiates and sets up all widgets and starts the Gtk main loop.

        This function also connects all the signals needed for Gtk builder using the HandlersManager class.
        """
        self.__setup_prefs_dialog()
        self.__setup_general_settings()
        self.__setup_x264()
        self.__setup_x265()
        self.__setup_nvenc()
        self.__setup_vp9()
        self.__setup_aac()
        self.__setup_opus()
        self.__setup_main_window()
        self.gtk_builder.connect_signals(HandlersManager(self.gtk_builder,
                                                         self.gtk_settings,
                                                         self.encoder_queue,
                                                         self.preferences))

        Gtk.main()

    def __setup_prefs_dialog(self):
        # Runs all functions needed to set up the preferences dialog's widgets.
        self.__setup_prefs_concurrent_widgets()
        self.__setup_prefs_nvenc_concurrent_widgets()
        self.__setup_prefs_temp_chooser_widgets()
        self.__setup_prefs_clear_widgets()
        self.__setup_prefs_overwrite_outputs_widgets()
        self.__setup_prefs_dark_theme_widgets()
        self.__setup_prefs_watch_folder_wait_for_tasks_widgets()
        self.__setup_prefs_watch_folder_concurrent_widgets()
        self.__setup_prefs_watch_folder_move_to_done_widgets()

    def __setup_prefs_concurrent_widgets(self):
        # Builds the preferences dialog's task concurrency combobox.
        prefs_concurrent_combobox = self.gtk_builder.get_object('prefs_concurrent_combobox')
        UIHelper.setup_combobox(prefs_concurrent_combobox, Preferences.parallel_tasks_values_list)
        prefs_concurrent_message_stack = self.gtk_builder.get_object('prefs_concurrent_message_stack')
        prefs_concurrent_message_8 = self.gtk_builder.get_object('prefs_concurrent_message_8')
        prefs_concurrent_message_12 = self.gtk_builder.get_object('prefs_concurrent_message_12')
        prefs_concurrent_message_24 = self.gtk_builder.get_object('prefs_concurrent_message_24')
        prefs_concurrent_message_32 = self.gtk_builder.get_object('prefs_concurrent_message_32')
        prefs_concurrent_message_final = self.gtk_builder.get_object('prefs_concurrent_message_final')

        parallel_tasks = self.preferences.parallel_tasks_as_string
        try:
            prefs_concurrent_combobox.set_active(Preferences.parallel_tasks_values_list.index(parallel_tasks))

            if parallel_tasks == '2':
                prefs_concurrent_message_stack.set_visible_child(prefs_concurrent_message_8)
            elif parallel_tasks == '3':
                prefs_concurrent_message_stack.set_visible_child(prefs_concurrent_message_12)
            elif parallel_tasks == '4':
                prefs_concurrent_message_stack.set_visible_child(prefs_concurrent_message_24)
            elif parallel_tasks == '6':
                prefs_concurrent_message_stack.set_visible_child(prefs_concurrent_message_32)
            else:
                prefs_concurrent_message_stack.set_visible_child(prefs_concurrent_message_final)
        except IndexError:
            logging.error('--- FAILED TO SETUP PARALLEL WIDGETS ---')

    def __setup_prefs_nvenc_concurrent_widgets(self):
        # Sets up the preferences dialog's NVENC concurrency related widgets and builds the concurrency combobox.
        prefs_nvenc_concurrent_combobox = self.gtk_builder.get_object('prefs_nvenc_concurrent_combobox')
        UIHelper.setup_combobox(prefs_nvenc_concurrent_combobox, Preferences.concurrent_nvenc_values_list)
        prefs_concurrent_nvenc_checkbox = self.gtk_builder.get_object('prefs_nvenc_concurrent_checkbox')
        prefs_concurrent_nvenc_checkbox.set_active(self.preferences.concurrent_nvenc)
        prefs_nvenc_concurrent_warning_stack = self.gtk_builder.get_object('prefs_nvenc_concurrent_warning_stack')
        prefs_nvenc_concurrent_empty_label = self.gtk_builder.get_object('prefs_nvenc_concurrent_empty_label')
        prefs_nvenc_concurrent_warning_image = self.gtk_builder.get_object('prefs_nvenc_concurrent_warning_image')

        concurrent_nvenc = self.preferences.concurrent_nvenc_value_as_string
        try:
            prefs_nvenc_concurrent_combobox.set_active(Preferences.concurrent_nvenc_values_list.index(concurrent_nvenc))

            if concurrent_nvenc != 'auto':
                prefs_nvenc_concurrent_warning_stack.set_visible_child(prefs_nvenc_concurrent_warning_image)
            else:
                prefs_nvenc_concurrent_warning_stack.set_visible_child(prefs_nvenc_concurrent_empty_label)
        except IndexError:
            logging.error('--- FAILED TO SETUP NVENC PARALLEL WIDGETS ---')

    def __setup_prefs_temp_chooser_widgets(self):
        prefs_temp_chooserbutton = self.gtk_builder.get_object('prefs_temp_chooserbutton')
        prefs_temp_chooserbutton.set_current_folder(self.preferences.temp_directory)

    def __setup_prefs_clear_widgets(self):
        prefs_clear_checkbox = self.gtk_builder.get_object('prefs_clear_checkbox')
        prefs_clear_checkbox.set_active(self.preferences.clear_temp_directory_on_exit)

    def __setup_prefs_overwrite_outputs_widgets(self):
        prefs_overwrite_outputs_checkbox = self.gtk_builder.get_object('prefs_overwrite_outputs_checkbox')
        prefs_overwrite_outputs_checkbox.set_active(self.preferences.overwrite_outputs)

    def __setup_prefs_dark_theme_widgets(self):
        prefs_dark_theme_switch = self.gtk_builder.get_object('prefs_dark_theme_switch')
        prefs_dark_theme_switch.set_active(self.preferences.use_dark_mode)
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", self.preferences.use_dark_mode)

    def __setup_prefs_watch_folder_wait_for_tasks_widgets(self):
        prefs_wait_for_tasks_checkbox = self.gtk_builder.get_object('prefs_wait_for_tasks_checkbox')
        prefs_wait_for_tasks_checkbox.set_active(self.preferences.watch_folder_wait_for_other_tasks)

    def __setup_prefs_watch_folder_concurrent_widgets(self):
        prefs_watch_concurrent_checkbox = self.gtk_builder.get_object('prefs_watch_concurrent_checkbox')
        prefs_watch_concurrent_checkbox.set_active(self.preferences.concurrent_watch_folder)

    def __setup_prefs_watch_folder_move_to_done_widgets(self):
        prefs_move_to_done_checkbox = self.gtk_builder.get_object('prefs_move_to_done_checkbox')
        prefs_move_to_done_checkbox.set_active(self.preferences.watch_folder_move_finished_to_done)

    def __setup_general_settings(self):
        # Runs all functions required to set up the general setting's widgets in the settings sidebar.
        self.__setup_general_settings_container_widgets()
        self.__setup_general_settings_video_codec_widgets()
        self.__setup_general_settings_audio_codec_widgets()
        self.__setup_general_settings_fps_widgets()

    def __setup_general_settings_container_widgets(self):
        container_combobox = self.gtk_builder.get_object("container_combobox")
        UIHelper.setup_combobox(container_combobox, GeneralSettings.CONTAINERS_UI_LIST)

    def __setup_general_settings_video_codec_widgets(self):
        video_codec_combobox = self.gtk_builder.get_object("video_codec_combobox")

        if NvidiaHelper.is_nvenc_supported():
            video_codec_list = GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST
        else:
            video_codec_list = GeneralSettings.VIDEO_CODEC_MP4_UI_LIST

        UIHelper.setup_combobox(video_codec_combobox, video_codec_list)

    def __setup_general_settings_audio_codec_widgets(self):
        audio_codec_combobox = self.gtk_builder.get_object("audio_codec_combobox")
        UIHelper.setup_combobox(audio_codec_combobox, GeneralSettings.AUDIO_CODEC_MP4_UI_LIST)

    def __setup_general_settings_fps_widgets(self):
        fps_combobox = self.gtk_builder.get_object("fps_combobox")
        UIHelper.setup_combobox(fps_combobox, GeneralSettings.FRAME_RATE_ARGS_LIST)

    def __setup_x264(self):
        # Runs all required functions to set up the x264 codec's widgets.
        self.__setup_x264_preset_widgets()
        self.__setup_x264_profile_widgets()
        self.__setup_x264_level_widgets()
        self.__setup_x264_tune_widgets()
        self.__setup_x264_aq_mode_widgets()
        self.__setup_x264_b_adapt_widgets()
        self.__setup_x264_b_pyramid_widgets()
        self.__setup_x264_weight_p_widgets()
        self.__setup_x264_me_widgets()
        self.__setup_x264_subme_widgets()
        self.__setup_x264_trellis_widgets()
        self.__setup_x264_direct_widgets()

    def __setup_x264_preset_widgets(self):
        x264_preset_combobox = self.gtk_builder.get_object("x264_preset_combobox")
        UIHelper.setup_combobox(x264_preset_combobox, X264.PRESET_ARGS_LIST)

    def __setup_x264_profile_widgets(self):
        x264_profile_combobox = self.gtk_builder.get_object("x264_profile_combobox")
        UIHelper.setup_combobox(x264_profile_combobox, X264.PROFILE_ARGS_LIST)

    def __setup_x264_level_widgets(self):
        x264_level_combobox = self.gtk_builder.get_object("x264_level_combobox")
        UIHelper.setup_combobox(x264_level_combobox, X264.LEVEL_ARGS_LIST)

    def __setup_x264_tune_widgets(self):
        x264_tune_combobox = self.gtk_builder.get_object("x264_tune_combobox")
        UIHelper.setup_combobox(x264_tune_combobox, X264.TUNE_ARGS_LIST)

    def __setup_x264_aq_mode_widgets(self):
        x264_aq_mode_combobox = self.gtk_builder.get_object('x264_aq_mode_combobox')
        UIHelper.setup_combobox(x264_aq_mode_combobox, X264.AQ_MODE_UI_LIST)

    def __setup_x264_b_adapt_widgets(self):
        x264_b_adapt_combobox = self.gtk_builder.get_object('x264_badapt_combobox')
        UIHelper.setup_combobox(x264_b_adapt_combobox, X264.B_ADAPT_UI_LIST)

    def __setup_x264_b_pyramid_widgets(self):
        x264_b_pyramid_combobox = self.gtk_builder.get_object('x264_bpyramid_combobox')
        UIHelper.setup_combobox(x264_b_pyramid_combobox, X264.B_PYRAMID_UI_LIST)

    def __setup_x264_weight_p_widgets(self):
        x264_weight_p_combobox = self.gtk_builder.get_object('x264_weight_p_combobox')
        UIHelper.setup_combobox(x264_weight_p_combobox, X264.WEIGHT_P_UI_LIST)

    def __setup_x264_me_widgets(self):
        x264_motion_estimation_combobox = self.gtk_builder.get_object('x264_motion_estimation_combobox')
        UIHelper.setup_combobox(x264_motion_estimation_combobox, X264.ME_ARGS_LIST)

    def __setup_x264_subme_widgets(self):
        x264_sub_me_combobox = self.gtk_builder.get_object('x264_sub_motion_estimation_combobox')
        UIHelper.setup_combobox(x264_sub_me_combobox, X264.SUB_ME_UI_LIST)

    def __setup_x264_trellis_widgets(self):
        x264_trellis_combobox = self.gtk_builder.get_object('x264_trellis_combobox')
        UIHelper.setup_combobox(x264_trellis_combobox, X264.TRELLIS_UI_LIST)

    def __setup_x264_direct_widgets(self):
        x264_direct_combobox = self.gtk_builder.get_object('x264_direct_combobox')
        UIHelper.setup_combobox(x264_direct_combobox, X264.DIRECT_UI_LIST)

    def __setup_x265(self):
        # Runs all required functions to set up the x265 codec's widgets.
        self.__setup_x265_preset_widgets()
        self.__setup_x265_profile_widgets()
        self.__setup_x265_level_widgets()
        self.__setup_x265_tune_widgets()
        self.__setup_x265_aq_mode_widgets()
        self.__setup_x265_b_adapt_widgets()
        self.__setup_x265_me_widgets()
        self.__setup_x265_rdoq_level_widgets()
        self.__setup_x265_max_cu_widgets()
        self.__setup_x265_min_cu_widgets()

    def __setup_x265_preset_widgets(self):
        x265_preset_combobox = self.gtk_builder.get_object("x265_preset_combobox")
        UIHelper.setup_combobox(x265_preset_combobox, X265.PRESET_ARGS_LIST)

    def __setup_x265_profile_widgets(self):
        x265_profile_combobox = self.gtk_builder.get_object("x265_profile_combobox")
        UIHelper.setup_combobox(x265_profile_combobox, X265.PROFILE_ARGS_LIST)

    def __setup_x265_level_widgets(self):
        x265_level_combobox = self.gtk_builder.get_object("x265_level_combobox")
        UIHelper.setup_combobox(x265_level_combobox, X265.LEVEL_ARGS_LIST)

    def __setup_x265_tune_widgets(self):
        x265_tune_combobox = self.gtk_builder.get_object("x265_tune_combobox")
        UIHelper.setup_combobox(x265_tune_combobox, X265.TUNE_ARGS_LIST)

    def __setup_x265_aq_mode_widgets(self):
        x265_aq_mode_combobox = self.gtk_builder.get_object('x265_aq_mode_combobox')
        UIHelper.setup_combobox(x265_aq_mode_combobox, X265.AQ_MODE_UI_LIST)

    def __setup_x265_b_adapt_widgets(self):
        x265_badapt_combobox = self.gtk_builder.get_object('x265_badapt_combobox')
        UIHelper.setup_combobox(x265_badapt_combobox, X265.B_ADAPT_UI_LIST)

    def __setup_x265_me_widgets(self):
        x265_me_combobox = self.gtk_builder.get_object('x265_me_combobox')
        UIHelper.setup_combobox(x265_me_combobox, X265.ME_ARGS_LIST)

    def __setup_x265_rdoq_level_widgets(self):
        x265_rdoq_level_combobox = self.gtk_builder.get_object('x265_rdoq_level_combobox')
        UIHelper.setup_combobox(x265_rdoq_level_combobox, X265.RDOQ_LEVEL_UI_LIST)

    def __setup_x265_max_cu_widgets(self):
        x265_max_cu_combobox = self.gtk_builder.get_object('x265_max_cu_combobox')
        UIHelper.setup_combobox(x265_max_cu_combobox, X265.MAX_CU_SIZE_ARGS_LIST)

    def __setup_x265_min_cu_widgets(self):
        x265_min_cu_combobox = self.gtk_builder.get_object('x265_min_cu_combobox')
        UIHelper.setup_combobox(x265_min_cu_combobox, X265.MIN_CU_SIZE_ARGS_LIST)

    def __setup_nvenc(self):
        # Runs all required functions to set up the NVENC codec's widgets.
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
        nvenc_no_scenecut_checkbutton = self.gtk_builder.get_object('nvenc_no_scenecut_checkbox')
        nvenc_no_scenecut_checkbutton.set_sensitive('-no-scenecut' in H264Nvenc.OPTIONS
                                                    and '-no-scenecut' in HevcNvenc.OPTIONS)

    def _setup_nvenc_forced_idr_widgets(self):
        nvenc_forced_idr_checkbutton = self.gtk_builder.get_object('nvenc_forced_idr_checkbox')
        nvenc_forced_idr_checkbutton.set_sensitive('-forced-idr' in H264Nvenc.OPTIONS
                                                   and '-forced-idr' in HevcNvenc.OPTIONS)

    def _setup_nvenc_aq_widgets(self):
        nvenc_aq_type_buttonbox = self.gtk_builder.get_object('nvenc_aq_type_buttonbox')
        nvenc_aq_type_buttonbox.set_sensitive('-spatial-aq' in H264Nvenc.OPTIONS
                                              and '-spatial-aq' in HevcNvenc.OPTIONS
                                              and '-temporal-aq' in H264Nvenc.OPTIONS
                                              and '-temporal-aq' in HevcNvenc.OPTIONS)
        nvenc_aq_strength_spinbutton = self.gtk_builder.get_object('nvenc_aqstrength_spinbutton')
        nvenc_aq_strength_spinbutton.set_sensitive('-aq-strength' in H264Nvenc.OPTIONS
                                                   and '-aq-strength' in HevcNvenc.OPTIONS)

    def _setup_nvenc_non_ref_p_widgets(self):
        nvenc_non_ref_p_checkbutton = self.gtk_builder.get_object('nvenc_nonref_pframes_checkbox')
        nvenc_non_ref_p_checkbutton.set_sensitive('-nonref_p' in H264Nvenc.OPTIONS and '-nonref_p' in HevcNvenc.OPTIONS)

    def _setup_nvenc_strict_gop_widgets(self):
        nvenc_strict_gop_checkbutton = self.gtk_builder.get_object('nvenc_strict_gop_checkbox')
        nvenc_strict_gop_checkbutton.set_sensitive('-strict_gop' in H264Nvenc.OPTIONS
                                                   and '-strict_gop' in HevcNvenc.OPTIONS)

    def _setup_nvenc_bluray_compat_widgets(self):
        nvenc_bluray_compat_checkbox = self.gtk_builder.get_object('nvenc_bluray_compat_checkbox')
        nvenc_bluray_compat_checkbox.set_sensitive('-bluray-compat' in H264Nvenc.OPTIONS
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
        nvenc_weighted_pred_checkbutton = self.gtk_builder.get_object('nvenc_weighted_prediction_checkbox')
        nvenc_weighted_pred_checkbutton.set_sensitive('-weighted_pred' in H264Nvenc.OPTIONS
                                                      and '-weighted_pred' in HevcNvenc.OPTIONS)

    def _setup_nvenc_b_ref_mode_widgets(self):
        nvenc_b_ref_mode_combobox = self.gtk_builder.get_object('nvenc_bref_mode_combobox')
        nvenc_b_ref_mode_combobox.set_sensitive('-b_ref_mode' in H264Nvenc.OPTIONS
                                                and '-b_ref_mode' in HevcNvenc.OPTIONS)

    def _setup_nvenc_multipass_widgets(self):
        nvenc_multipass_combobox = self.gtk_builder.get_object('nvenc_multi_pass_combobox')
        nvenc_multipass_combobox.set_sensitive('-multipass' in H264Nvenc.OPTIONS and '-multipass' in HevcNvenc.OPTIONS)

    def _setup_nvenc_b_adapt_widgets(self):
        nvenc_b_adapt_checkbox = self.gtk_builder.get_object('nvenc_badapt_checkbox')
        nvenc_b_adapt_checkbox.set_sensitive('-b_adapt' in H264Nvenc.OPTIONS)

    def _setup_nvenc_coder_widgets(self):
        if '-coder' in H264Nvenc.OPTIONS:
            nvenc_coder_combobox = self.gtk_builder.get_object('nvenc_coder_combobox')
            UIHelper.setup_combobox(nvenc_coder_combobox, H264Nvenc.OPTIONS['-coder'])

    def __setup_vp9(self):
        # Runs all required functions to set up the VP9 codec's widgets.
        self.__setup_vp9_quality_widgets()
        self.__setup_vp9_speed_widgets()

    def __setup_vp9_quality_widgets(self):
        vp9_quality_combobox = self.gtk_builder.get_object('vp9_quality_combobox')
        UIHelper.setup_combobox(vp9_quality_combobox, VP9.QUALITY_ARGS_LIST)

    def __setup_vp9_speed_widgets(self):
        vp9_speed_combobox = self.gtk_builder.get_object('vp9_speed_combobox')
        UIHelper.setup_combobox(vp9_speed_combobox, VP9.SPEED_ARGS_LIST)

    def __setup_aac(self):
        # Runs all required functions to set up the AAC codec's widgets.
        self.__setup_aac_channels_widgets()

    def __setup_aac_channels_widgets(self):
        aac_channels_combobox = self.gtk_builder.get_object("aac_channels_combobox")
        UIHelper.setup_combobox(aac_channels_combobox, Aac.CHANNELS_UI_LIST)

    def __setup_opus(self):
        # Runs all required functions to set up the Opus codec's widgets.
        self.__setup_opus_channels_widgets()

    def __setup_opus_channels_widgets(self):
        opus_channels_combobox = self.gtk_builder.get_object('opus_channels_combobox')
        UIHelper.setup_combobox(opus_channels_combobox, Opus.CHANNELS_UI_LIST)

    def __setup_main_window(self):
        # Runs all required functions to set up the main window's widgets.
        self.__setup_main_window_output_chooser_widgets()
        self.__setup_and_show_main_window()

    def __setup_main_window_output_chooser_widgets(self):
        output_chooserbutton = self.gtk_builder.get_object('output_chooserbutton')
        output_chooserbutton.set_current_folder(self.preferences.output_directory)

    def __setup_and_show_main_window(self):
        # Sets up the main window from Gtk builder and shows the window if no errors occur.
        try:
            main_window = self.gtk_builder.get_object('main_window')
            self.__setup_main_window_dimensions(main_window)
        except:
            logging.critical('--- FAILED TO SETUP AND SHOW MAIN WINDOW ---')
        else:
            main_window.connect('size-allocate', self.__on_size_allocate)
            main_window.connect('destroy', self.__quit)
            main_window.show_all()

    def __setup_main_window_dimensions(self, main_window):
        # Restore window's previous dimensions/state saved in defined user preferences.
        window_dimensions = self.preferences.window_dimensions
        main_window.set_size_request(800, 500)
        main_window.resize(window_dimensions[0], window_dimensions[1])

        if self.preferences.window_maximized:
            main_window.maximize()

    def __on_size_allocate(self, application_window, allocation):  # Unused parameter needed for this signal.
        # Signal function that saves the window's size to user preferences when the window is resized.
        if not application_window.is_maximized():
            application_window_size = application_window.get_size()
            self.preferences.window_dimensions = (application_window_size[0], application_window_size[1])

    def __quit(self, application_window):
        # Signal function that saves user preferences, stops the encoder, and quits the Gtk main loop.
        self.__finalize_preferences(application_window)
        self.encoder_queue.kill()
        Gtk.main_quit()

    def __finalize_preferences(self, application_window):
        # Saves window state and preferences and clears the temporary directory if applicable.
        self.preferences.window_maximized = application_window.is_maximized()
        Preferences.save_preferences(self.preferences)
        Preferences.clear_temp_directory(self.preferences)
