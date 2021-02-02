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

import logging
import os

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.x265 import X265
from render_watch.ffmpeg.x264 import X264
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.ffmpeg.vp9 import VP9
from render_watch.ffmpeg.aac import Aac
from render_watch.ffmpeg.opus import Opus
from render_watch.app_handlers.handlers_manager import HandlersManager
from render_watch.startup.preferences import Preferences
from render_watch.startup.app_requirements import AppRequirements
from render_watch.startup import Gtk


class AppUI:
    def __init__(self, encoder, preferences):
        self.encoder = encoder
        self.preferences = preferences

        self.__setup_application_gtk_builder()

    def __setup_application_gtk_builder(self):
        this_file_directory_file_path = os.path.dirname(os.path.abspath(__file__))
        rw_ui_file_path = os.path.join(this_file_directory_file_path, '../render_watch_data/rw_ui.glade')
        self.gtk_settings = Gtk.Settings.get_default()
        self.gtk_builder = Gtk.Builder()

        self.gtk_builder.add_from_file(rw_ui_file_path)

    def setup_and_run_application(self):
        self.__setup_prefs_dialog()
        self.__setup_general_settings()
        self.__setup_x264()
        self.__setup_x265()
        self.__setup_nvenc()
        self.__setup_vp9()
        self.__setup_aac()
        self.__setup_opus()
        self.__setup_main_window()
        self.gtk_builder.connect_signals(HandlersManager(self.gtk_builder, self.gtk_settings, self.encoder,
                                                         self.preferences))
        Gtk.main()

    def __setup_prefs_dialog(self):
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
        parallel_tasks = self.preferences.parallel_tasks_as_string
        prefs_concurrent_combobox = self.gtk_builder.get_object('prefs_concurrent_combobox')
        prefs_concurrent_message_stack = self.gtk_builder.get_object('prefs_concurrent_message_stack')
        prefs_concurrent_message_8 = self.gtk_builder.get_object('prefs_concurrent_message_8')
        prefs_concurrent_message_12 = self.gtk_builder.get_object('prefs_concurrent_message_12')
        prefs_concurrent_message_24 = self.gtk_builder.get_object('prefs_concurrent_message_24')
        prefs_concurrent_message_32 = self.gtk_builder.get_object('prefs_concurrent_message_32')
        prefs_concurrent_message_final = self.gtk_builder.get_object('prefs_concurrent_message_final')

        self.__setup_combobox(prefs_concurrent_combobox, Preferences.parallel_tasks_values_list)

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
        concurrent_nvenc = self.preferences.concurrent_nvenc_value_as_string
        prefs_concurrent_nvenc_checkbox = self.gtk_builder.get_object('prefs_nvenc_concurrent_checkbox')
        prefs_nvenc_concurrent_warning_stack = self.gtk_builder.get_object('prefs_nvenc_concurrent_warning_stack')
        prefs_nvenc_concurrent_empty_label = self.gtk_builder.get_object('prefs_nvenc_concurrent_empty_label')
        prefs_nvenc_concurrent_warning_image = self.gtk_builder.get_object('prefs_nvenc_concurrent_warning_image')
        prefs_nvenc_concurrent_combobox = self.gtk_builder.get_object('prefs_nvenc_concurrent_combobox')

        self.__setup_combobox(prefs_nvenc_concurrent_combobox, Preferences.concurrent_nvenc_values_list)
        prefs_concurrent_nvenc_checkbox.set_active(self.preferences.concurrent_nvenc)

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
        self.__setup_general_settings_container_widgets()
        self.__setup_general_settings_video_codec_widgets()
        self.__setup_general_settings_audio_codec_widgets()
        self.__setup_general_settings_fps_widgets()

    def __setup_general_settings_container_widgets(self):
        container_combobox = self.gtk_builder.get_object("container_combobox")

        self.__setup_combobox(container_combobox, GeneralSettings.video_file_containers_list)

    def __setup_general_settings_video_codec_widgets(self):
        video_codec_combobox = self.gtk_builder.get_object("video_codec_combobox")

        if AppRequirements.is_nvenc_supported():
            video_codec_list = GeneralSettings.video_codec_mp4_nvenc_ui_list
        else:
            video_codec_list = GeneralSettings.video_codec_mp4_ui_list

        self.__setup_combobox(video_codec_combobox, video_codec_list)

    def __setup_general_settings_audio_codec_widgets(self):
        audio_codec_combobox = self.gtk_builder.get_object("audio_codec_combobox")

        self.__setup_combobox(audio_codec_combobox, GeneralSettings.audio_codec_mp4_ui_list)

    def __setup_general_settings_fps_widgets(self):
        fps_combobox = self.gtk_builder.get_object("fps_combobox")

        self.__setup_combobox(fps_combobox, GeneralSettings.frame_rate_ffmpeg_args_list)

    def __setup_x264(self):
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

        self.__setup_combobox(x264_preset_combobox, X264.preset_ffmpeg_args_list)

    def __setup_x264_profile_widgets(self):
        x264_profile_combobox = self.gtk_builder.get_object("x264_profile_combobox")

        self.__setup_combobox(x264_profile_combobox, X264.profile_ffmpeg_args_list)

    def __setup_x264_level_widgets(self):
        x264_level_combobox = self.gtk_builder.get_object("x264_level_combobox")

        self.__setup_combobox(x264_level_combobox, X264.level_ffmpeg_args_list)

    def __setup_x264_tune_widgets(self):
        x264_tune_combobox = self.gtk_builder.get_object("x264_tune_combobox")

        self.__setup_combobox(x264_tune_combobox, X264.tune_ffmpeg_args_list)

    def __setup_x264_aq_mode_widgets(self):
        x264_aq_mode_combobox = self.gtk_builder.get_object('x264_aq_mode_combobox')

        self.__setup_combobox(x264_aq_mode_combobox, X264.aq_mode_human_readable_list)

    def __setup_x264_b_adapt_widgets(self):
        x264_b_adapt_combobox = self.gtk_builder.get_object('x264_badapt_combobox')

        self.__setup_combobox(x264_b_adapt_combobox, X264.b_adapt_human_readable_list)

    def __setup_x264_b_pyramid_widgets(self):
        x264_b_pyramid_combobox = self.gtk_builder.get_object('x264_bpyramid_combobox')

        self.__setup_combobox(x264_b_pyramid_combobox, X264.b_pyramid_human_readable_list)

    def __setup_x264_weight_p_widgets(self):
        x264_weight_p_combobox = self.gtk_builder.get_object('x264_weight_p_combobox')

        self.__setup_combobox(x264_weight_p_combobox, X264.weight_p_human_readable_list)

    def __setup_x264_me_widgets(self):
        x264_motion_estimation_combobox = self.gtk_builder.get_object('x264_motion_estimation_combobox')

        self.__setup_combobox(x264_motion_estimation_combobox, X264.motion_estimation_ffmpeg_args_list)

    def __setup_x264_subme_widgets(self):
        x264_sub_me_combobox = self.gtk_builder.get_object('x264_sub_motion_estimation_combobox')

        self.__setup_combobox(x264_sub_me_combobox, X264.sub_me_human_readable_list)

    def __setup_x264_trellis_widgets(self):
        x264_trellis_combobox = self.gtk_builder.get_object('x264_trellis_combobox')

        self.__setup_combobox(x264_trellis_combobox, X264.trellis_human_readable_list)

    def __setup_x264_direct_widgets(self):
        x264_direct_combobox = self.gtk_builder.get_object('x264_direct_combobox')

        self.__setup_combobox(x264_direct_combobox, X264.direct_human_readable_list)

    def __setup_x265(self):
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

        self.__setup_combobox(x265_preset_combobox, X265.preset_ffmpeg_args_list)

    def __setup_x265_profile_widgets(self):
        x265_profile_combobox = self.gtk_builder.get_object("x265_profile_combobox")

        self.__setup_combobox(x265_profile_combobox, X265.profile_ffmpeg_args_list)

    def __setup_x265_level_widgets(self):
        x265_level_combobox = self.gtk_builder.get_object("x265_level_combobox")

        self.__setup_combobox(x265_level_combobox, X265.level_ffmpeg_args_list)

    def __setup_x265_tune_widgets(self):
        x265_tune_combobox = self.gtk_builder.get_object("x265_tune_combobox")

        self.__setup_combobox(x265_tune_combobox, X265.tune_ffmpeg_args_list)

    def __setup_x265_aq_mode_widgets(self):
        x265_aq_mode_combobox = self.gtk_builder.get_object('x265_aq_mode_combobox')

        self.__setup_combobox(x265_aq_mode_combobox, X265.aq_mode_human_readable_list)

    def __setup_x265_b_adapt_widgets(self):
        x265_badapt_combobox = self.gtk_builder.get_object('x265_badapt_combobox')

        self.__setup_combobox(x265_badapt_combobox, X265.b_adapt_human_readable_list)

    def __setup_x265_me_widgets(self):
        x265_me_combobox = self.gtk_builder.get_object('x265_me_combobox')

        self.__setup_combobox(x265_me_combobox, X265.me_ffmpeg_args_list)

    def __setup_x265_rdoq_level_widgets(self):
        x265_rdoq_level_combobox = self.gtk_builder.get_object('x265_rdoq_level_combobox')

        self.__setup_combobox(x265_rdoq_level_combobox, X265.rdoq_level_human_readable_list)

    def __setup_x265_max_cu_widgets(self):
        x265_max_cu_combobox = self.gtk_builder.get_object('x265_max_cu_combobox')

        self.__setup_combobox(x265_max_cu_combobox, X265.max_cu_size_ffmpeg_args_list)

    def __setup_x265_min_cu_widgets(self):
        x265_min_cu_combobox = self.gtk_builder.get_object('x265_min_cu_combobox')

        self.__setup_combobox(x265_min_cu_combobox, X265.min_cu_size_ffmpeg_args_list)

    def __setup_nvenc(self):
        self.__setup_nvenc_coder_widgets()

    def __setup_nvenc_coder_widgets(self):
        nvenc_coder_combobox = self.gtk_builder.get_object('nvenc_coder_combobox')

        self.__setup_combobox(nvenc_coder_combobox, H264Nvenc.coder_ffmpeg_args_list)

    def __setup_vp9(self):
        self.__setup_vp9_quality_widgets()
        self.__setup_vp9_speed_widgets()

    def __setup_vp9_quality_widgets(self):
        vp9_quality_combobox = self.gtk_builder.get_object('vp9_quality_combobox')

        self.__setup_combobox(vp9_quality_combobox, VP9.quality_ffmpeg_args_list)

    def __setup_vp9_speed_widgets(self):
        vp9_speed_combobox = self.gtk_builder.get_object('vp9_speed_combobox')

        self.__setup_combobox(vp9_speed_combobox, VP9.speed_ffmpeg_args_list)

    def __setup_aac(self):
        self.__setup_aac_channels_widgets()

    def __setup_aac_channels_widgets(self):
        aac_channels_combobox = self.gtk_builder.get_object("aac_channels_combobox")

        self.__setup_combobox(aac_channels_combobox, Aac.channels_human_readable_list)

    def __setup_opus(self):
        self.__setup_opus_channels_widgets()

    def __setup_opus_channels_widgets(self):
        opus_channels_combobox = self.gtk_builder.get_object('opus_channels_combobox')

        self.__setup_combobox(opus_channels_combobox, Opus.channels_human_readable_list)

    def __setup_main_window(self):
        self.__setup_main_window_output_chooser_widgets()
        self.__setup_and_show_main_window()

    def __setup_main_window_output_chooser_widgets(self):
        output_chooserbutton = self.gtk_builder.get_object('output_chooserbutton')

        output_chooserbutton.set_current_folder(self.preferences.output_directory)

    def __setup_and_show_main_window(self):
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
        window_dimensions = self.preferences.window_dimensions

        main_window.set_size_request(800, 500)
        main_window.resize(window_dimensions[0], window_dimensions[1])

        if self.preferences.window_maximized:
            main_window.maximize()

    def __on_size_allocate(self, application_window, allocation):
        if not application_window.is_maximized():
            application_window_size = application_window.get_size()
            self.preferences.window_dimensions = (application_window_size[0], application_window_size[1])

    def __quit(self, application_window):
        self.__finalize_preferences(application_window)
        self.encoder.kill()
        Gtk.main_quit()

    def __finalize_preferences(self, application_window):
        self.preferences.window_maximized = application_window.is_maximized()

        Preferences.save_preferences(self.preferences)
        Preferences.clear_temp_directory(self.preferences)

    @staticmethod
    def __setup_combobox(combobox, value_list):
        for value in value_list:
            combobox.append_text(value)

        combobox.set_entry_text_column(0)
        combobox.set_active(0)

    @staticmethod
    def rebuild_combobox(combobox, values_list):
        combobox.remove_all()

        for value in values_list:
            combobox.append_text(value)

        combobox.set_entry_text_column(0)
        combobox.set_active(0)
