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
        self._setup_inputs_page_widgets()
        self._setup_active_page_widgets()
        self._setup_main_window_widgets()

        self.gtk_builder.connect_signals(HandlersManager(self.gtk_builder,
                                                         self.gtk_settings,
                                                         self.encoder_queue,
                                                         self.application_preferences))

        return Gtk.main()

    def _setup_preferences_dialog_widgets(self):
        self._setup_preferences_dialog_per_codec_tasks_widgets()
        self._setup_preferences_dialog_dark_mode_widgets()

    def _setup_preferences_dialog_per_codec_tasks_widgets(self):
        try:
            if self.application_preferences.is_per_codec_parallel_tasks_enabled:
                per_codec_switch = self.gtk_builder.get_object('per_codec_switch')
                parallel_tasks_stack = self.gtk_builder.get_object('parallel_tasks_stack')
                per_codec_frame = self.gtk_builder.get_object('per_codec_frame')

                per_codec_switch.set_active(True)
                parallel_tasks_stack.set_visible_child(per_codec_frame)
        except IndexError:
            logging.error('--- FAILED TO SETUP PER CODEC TASKS WIDGETS ---')

    def _setup_preferences_dialog_dark_mode_widgets(self):
        dark_mode = self.application_preferences.is_dark_mode_enabled
        self.gtk_settings.set_property('gtk-application-prefer-dark-theme', dark_mode)

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
        self._setup_nvenc_coder_widgets()

    def _setup_nvenc_coder_widgets(self):
        nvenc_coder_combobox = self.gtk_builder.get_object('nvenc_coder_combobox')
        UIHelper.setup_combobox(nvenc_coder_combobox, H264Nvenc.CODER_ARGS_LIST)

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

    def _setup_inputs_page_widgets(self):
        self._setup_parallel_tasks_widgets()
        self._setup_auto_crop_inputs_widgets()

    def _setup_parallel_tasks_widgets(self):
        toggle_parallel_tasks_radiobutton = self.gtk_builder.get_object('toggle_parallel_tasks_radiobutton')
        toggle_parallel_tasks_radiobutton.set_active(self.application_preferences.is_parallel_tasks_enabled)
        parallel_tasks_type_options_box = self.gtk_builder.get_object('parallel_tasks_type_options_box')
        parallel_tasks_type_options_box.set_sensitive(self.application_preferences.is_parallel_tasks_enabled)
        parallel_tasks_chunks_radiobutton = self.gtk_builder.get_object('parallel_tasks_chunks_radiobutton')
        parallel_tasks_chunks_radiobutton.set_active(self.application_preferences.is_parallel_chunks_enabled)

        self.encoder_queue.is_parallel_tasks_enabled = self.application_preferences.is_parallel_tasks_enabled

    def _setup_auto_crop_inputs_widgets(self):
        auto_crop_inputs_checkbutton = self.gtk_builder.get_object('auto_crop_inputs_checkbutton')
        auto_crop_inputs_checkbutton.set_active(self.application_preferences.is_auto_crop_inputs_enabled)

    def _setup_active_page_widgets(self):
        self._setup_encode_preview_widgets()

    def _setup_encode_preview_widgets(self):
        preview_encode_switch = self.gtk_builder.get_object('preview_encode_switch')
        preview_encode_switch.set_active(self.application_preferences.is_encode_preview_enabled)

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
