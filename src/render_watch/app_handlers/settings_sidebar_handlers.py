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

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.x264 import X264
from render_watch.ffmpeg.x265 import X265
from render_watch.ffmpeg.vp9 import VP9
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.ffmpeg.hevc_nvenc import HevcNvenc
from render_watch.ffmpeg.aac import Aac
from render_watch.ffmpeg.opus import Opus
from render_watch.encoding import preview
from render_watch.app_handlers.x264_handlers import X264Handlers
from render_watch.app_handlers.x265_handlers import X265Handlers
from render_watch.app_handlers.nvenc_handlers import NvencHandlers
from render_watch.app_handlers.vp9_handlers import VP9Handlers
from render_watch.app_handlers.aac_handlers import AacHandlers
from render_watch.app_handlers.opus_handlers import OpusHandlers
from render_watch.startup.app_requirements import AppRequirements
from render_watch.startup import GLib


class SettingsSidebarHandlers:
    def __init__(self, gtk_builder, preferences):
        self.gtk_builder = gtk_builder
        self.inputs_page_handlers = None
        self.crop_page_handlers = None
        self.preview_page_handlers = None
        self.trim_page_handlers = None
        self.x264_handlers = X264Handlers(gtk_builder, preferences)
        self.x265_handlers = X265Handlers(gtk_builder, preferences)
        self.nvenc_handlers = NvencHandlers(gtk_builder)
        self.vp9_handlers = VP9Handlers(gtk_builder, preferences)
        self.aac_handlers = AacHandlers(gtk_builder)
        self.opus_handlers = OpusHandlers(gtk_builder)
        self.handlers_list = (self.x264_handlers, self.x265_handlers, self.nvenc_handlers, self.vp9_handlers,
                              self.aac_handlers, self.opus_handlers)
        self.__is_widgets_setting_up = False
        self.__is_video_codec_combobox_being_rebuilt = False
        self.__is_audio_codec_combobox_being_rebuilt = False
        self.benchmark_thread = None
        self.stop_benchmark_thread = False
        self.__benchmark_thread_lock = threading.Lock()
        self.container_combobox = gtk_builder.get_object("container_combobox")
        self.streaming_checkbox = gtk_builder.get_object("streaming_checkbox")
        self.video_codec_combobox = gtk_builder.get_object("video_codec_combobox")
        self.video_stack = gtk_builder.get_object("video_stack")
        self.x264_box = gtk_builder.get_object("x264_box")
        self.x265_box = gtk_builder.get_object("x265_box")
        self.nvenc_box = gtk_builder.get_object('nvenc_box')
        self.vp9_box = gtk_builder.get_object('vp9_box')
        self.video_noavail_label = gtk_builder.get_object("video_noavail_label")
        self.audio_codec_combobox = gtk_builder.get_object("audio_codec_combobox")
        self.audio_stack = gtk_builder.get_object("audio_stack")
        self.audio_noavail_label = gtk_builder.get_object("audio_noavail_label")
        self.aac_box = gtk_builder.get_object("aac_box")
        self.opus_box = gtk_builder.get_object('opus_box')
        self.fps_box = gtk_builder.get_object("fps_box")
        self.fps_combobox = gtk_builder.get_object('fps_combobox')
        self.framerate_auto_button = gtk_builder.get_object("framerate_auto_radiobutton")
        self.framerate_custom_button = gtk_builder.get_object("framerate_custom_radiobutton")
        self.benchmark_start_button = gtk_builder.get_object('benchmark_start_button')
        self.benchmark_stop_button = gtk_builder.get_object('benchmark_stop_button')
        self.benchmark_stack = gtk_builder.get_object('benchmark_stack')
        self.benchmark_noavail_label = gtk_builder.get_object('benchmark_noavail_label')
        self.benchmark_values_grid = gtk_builder.get_object('benchmark_values_grid')
        self.benchmark_speed_value_label = gtk_builder.get_object('benchmark_speed_value_label')
        self.benchmark_bitrate_value_label = gtk_builder.get_object('benchmark_bitrate_value_label')
        self.benchmark_proc_time_value_label = gtk_builder.get_object('benchmark_proc_time_value_label')
        self.benchmark_file_size_value_label = gtk_builder.get_object('benchmark_file_size_value_label')
        self.benchmark_progress_bar = gtk_builder.get_object('benchmark_progress_bar')
        self.benchmark_short_radiobutton = gtk_builder.get_object('benchmark_short_radiobutton')
        self.benchmark_bottom_button_stack = gtk_builder.get_object('benchmark_bottom_button_stack')
        self.crop_button = gtk_builder.get_object('crop_button')
        self.trim_button = gtk_builder.get_object('trim_button')
        self.preview_button = gtk_builder.get_object('preview_button')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        for handler in self.handlers_list:
            if hasattr(handler, signal_name):
                return getattr(handler, signal_name)

    def reset_settings(self):
        self.__is_widgets_setting_up = True

        self.container_combobox.set_active(0)
        self.fps_combobox.set_active(0)
        self.video_codec_combobox.set_active(0)
        self.audio_codec_combobox.set_active(0)
        self.streaming_checkbox.set_active(False)
        self.framerate_auto_button.set_active(True)
        self.x265_handlers.reset_settings()
        self.x264_handlers.reset_settings()
        self.nvenc_handlers.reset_settings()
        self.vp9_handlers.reset_settings()
        self.aac_handlers.reset_settings()
        self.opus_handlers.reset_settings()
        self.__set_benchmark_state()

        self.__is_widgets_setting_up = False

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is None:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        else:
            ffmpeg = ffmpeg_param

        self.__set_settings_for_settings_sidebar(ffmpeg)
        self.__set_settings_for_x264_handlers(ffmpeg_param)
        self.__set_settings_for_x265_handlers(ffmpeg_param)
        self.__set_settings_for_nvenc_handlers(ffmpeg_param)
        self.__set_settings_for_vp9_handlers(ffmpeg_param)
        self.__set_settings_for_aac_handlers(ffmpeg_param)
        self.__set_settings_for_opus_handlers(ffmpeg_param)
        self.__set_benchmark_state()

    def __set_settings_for_x264_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.x264_handlers.set_settings,)
        else:
            args = (self.x264_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_settings_for_x265_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.x265_handlers.set_settings,)
        else:
            args = (self.x265_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_settings_for_nvenc_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.nvenc_handlers.set_settings,)
        else:
            args = (self.nvenc_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_settings_for_vp9_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.vp9_handlers.set_settings,)
        else:
            args = (self.vp9_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_settings_for_aac_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.aac_handlers.set_settings,)
        else:
            args = (self.aac_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_settings_for_opus_handlers(self, ffmpeg=None):
        if ffmpeg is None:
            args = (self.opus_handlers.set_settings,)
        else:
            args = (self.opus_handlers.set_settings, ffmpeg)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def __set_benchmark_state(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()

        if inputs_row is not None:
            is_video_settings_enabled = inputs_row.ffmpeg.video_settings is not None
            is_folder_state_enabled = inputs_row.ffmpeg.folder_state
            state = is_video_settings_enabled and not is_folder_state_enabled
        else:
            state = False

        if state:
            self.set_benchmark_ready_state()
        else:
            self.__set_benchmark_not_available_state()

    def set_benchmark_ready_state(self):
        self.benchmark_stack.set_visible_child(self.benchmark_values_grid)
        self.benchmark_bottom_button_stack.set_sensitive(True)
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_start_button)
        self.benchmark_speed_value_label.set_text('')
        self.benchmark_bitrate_value_label.set_text('')
        self.benchmark_proc_time_value_label.set_text('')
        self.benchmark_file_size_value_label.set_text('')
        self.benchmark_progress_bar.set_fraction(0.0)

    def __set_benchmark_not_available_state(self):
        self.benchmark_stack.set_visible_child(self.benchmark_noavail_label)
        self.benchmark_bottom_button_stack.set_sensitive(False)
        self.on_benchmark_stop_button_clicked(self.benchmark_stop_button)

    def __set_settings_for_settings_sidebar(self, ffmpeg):
        video_settings = ffmpeg.video_settings
        audio_settings = ffmpeg.audio_settings
        general_settings = ffmpeg.general_settings
        output_container = ffmpeg.output_container
        is_output_container_set = ffmpeg.is_output_container_set()
        self.__is_widgets_setting_up = True

        self.__setup_settings_sidebar_output_container_widgets_settings(output_container, is_output_container_set)
        self.streaming_checkbox.set_active(general_settings.fast_start)
        self.__setup_settings_sidebar_frame_rate_widgets_settings(general_settings)
        self.__setup_settings_sidebar_video_codec_widgets_settings(video_settings)
        self.__setup_settings_sidebar_audio_codec_widgets_settings(audio_settings)

        self.__is_widgets_setting_up = False

    def __setup_settings_sidebar_output_container_widgets_settings(self, output_container, is_output_container_set):
        if is_output_container_set:
            self.container_combobox.set_active(GeneralSettings.video_file_containers_list.index(output_container))
        else:
            self.container_combobox.set_active(0)

    def __setup_settings_sidebar_frame_rate_widgets_settings(self, general_settings):
        if general_settings.frame_rate is not None:
            self.framerate_custom_button.set_active(True)
            self.fps_combobox.set_active(general_settings.frame_rate)
        else:
            self.framerate_auto_button.set_active(True)
            self.fps_combobox.set_active(0)

    def __setup_settings_sidebar_video_codec_widgets_settings(self, video_settings):
        if video_settings is not None:

            if video_settings.codec_name == 'libx264':
                self.video_codec_combobox.set_active(1)
            elif video_settings.codec_name == 'libx265':
                self.video_codec_combobox.set_active(2)
            elif video_settings.codec_name == 'h264_nvenc':
                self.video_codec_combobox.set_active(3)
            elif video_settings.codec_name == 'hevc_nvenc':
                self.video_codec_combobox.set_active(4)
            elif video_settings.codec_name == 'libvpx-vp9':

                if self.container_combobox.get_active() == 1:
                    self.video_codec_combobox.set_active(5)
                else:
                    self.video_codec_combobox.set_active(1)
        else:
            if self.video_codec_combobox.get_active() != 0:
                self.video_codec_combobox.set_active(0)
            else:
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

    def __setup_settings_sidebar_audio_codec_widgets_settings(self, audio_settings):
        if audio_settings is not None:

            if audio_settings.codec_name == 'aac':
                self.audio_codec_combobox.set_active(1)
            elif audio_settings.codec_name == 'libopus':

                if self.container_combobox.get_active() == 1:
                    self.audio_codec_combobox.set_active(2)
                else:
                    self.audio_codec_combobox.set_active(1)
        else:
            if self.audio_codec_combobox.get_active() != 0:
                self.audio_codec_combobox.set_active(0)
            else:
                self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

    def get_settings(self, ffmpeg):
        self.__set_general_settings_from_settings_sidebar_widgets(ffmpeg)
        self.__set_video_codec_settings_from_settings_sidebar_widgets(ffmpeg)
        self.__set_audio_codec_settings_from_settings_sidebar_widgets(ffmpeg)

    def __set_general_settings_from_settings_sidebar_widgets(self, ffmpeg):
        general_settings = GeneralSettings()
        general_settings.fast_start = self.streaming_checkbox.get_active()

        self.__set_output_container_settings_from_settings_sidebar_widgets(ffmpeg)
        self.__set_frame_rate_settings_from_settings_sidebar_widgets(general_settings)

        ffmpeg.general_settings = general_settings

    def __set_output_container_settings_from_settings_sidebar_widgets(self, ffmpeg):
        if self.container_combobox.get_active() != 0:
            ffmpeg.output_container = GeneralSettings.video_file_containers_list[self.container_combobox.get_active()]

    def __set_frame_rate_settings_from_settings_sidebar_widgets(self, general_settings):
        if self.framerate_custom_button.get_active():
            general_settings.frame_rate = GeneralSettings.frame_rate_ffmpeg_args_list[self.fps_combobox.get_active()]

    def __set_video_codec_settings_from_settings_sidebar_widgets(self, ffmpeg):
        video_codec_text = GeneralSettings.video_codec_mp4_nvenc_ui_list[self.video_codec_combobox.get_active()]

        if video_codec_text == 'H264':
            self.x264_handlers.get_settings(ffmpeg)
        elif video_codec_text == 'H265':
            self.x265_handlers.get_settings(ffmpeg)
        elif 'NVENC' in video_codec_text:
            self.nvenc_handlers.get_settings(ffmpeg)
        elif video_codec_text == 'VP9':
            self.vp9_handlers.get_settings(ffmpeg)
        else:
            ffmpeg.video_settings = None

    def __set_audio_codec_settings_from_settings_sidebar_widgets(self, ffmpeg):
        audio_codec_text = GeneralSettings.audio_codec_mp4_ui_list[self.audio_codec_combobox.get_active()]

        if audio_codec_text == 'aac':
            self.aac_handlers.get_settings(ffmpeg)
        elif audio_codec_text == 'libopus':
            self.opus_handlers.get_settings(ffmpeg)
        else:
            ffmpeg.audio_settings = None

    def set_extra_settings_state(self, state):
        self.crop_button.set_sensitive(state)
        self.trim_button.set_sensitive(state)
        self.preview_button.set_sensitive(state)

    def set_benchmark_start_state(self):
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_stop_button)
        self.benchmark_speed_value_label.set_text('')
        self.benchmark_bitrate_value_label.set_text('')
        self.benchmark_proc_time_value_label.set_text('')
        self.benchmark_file_size_value_label.set_text('')
        self.benchmark_progress_bar.set_fraction(0.0)

    def set_benchmark_progress_bar_fraction(self, progress_fraction):
        self.benchmark_progress_bar.set_fraction(progress_fraction)

    def set_benchmark_bitrate_label_text(self, bitrate_label_text):
        self.benchmark_bitrate_value_label.set_text(bitrate_label_text)

    def set_benchmark_speed_label_text(self, speed_label_text):
        self.benchmark_speed_value_label.set_text(speed_label_text)

    def set_benchmark_process_time_label_text(self, process_time_label_text):
        self.benchmark_proc_time_value_label.set_text(process_time_label_text)

    def set_benchmark_file_size_label_text(self, file_size_label_text):
        self.benchmark_file_size_value_label.set_text(file_size_label_text)

    def set_benchmark_done_state(self):
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_start_button)

    def is_benchmark_short_radiobutton_active(self):
        return self.benchmark_short_radiobutton.get_active()

    def on_container_combobox_changed(self, container_combobox):
        container_text = GeneralSettings.video_file_containers_list[container_combobox.get_active()]
        video_codec_text = self.video_codec_combobox.get_active_text()
        audio_codec_text = self.audio_codec_combobox.get_active_text()

        if container_text == '.mp4':
            self.__set_mp4_state(video_codec_text, audio_codec_text)
        elif container_text == '.mkv':
            self.__set_mkv_state(video_codec_text, audio_codec_text)
        elif container_text == '.ts':
            self.__set_ts_state(video_codec_text, audio_codec_text)
        elif container_text == '.webm':
            self.__setup_webm_state(video_codec_text, audio_codec_text)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg

            if container_text == 'copy':
                ffmpeg.output_container = None
            else:
                ffmpeg.output_container = container_text

            row.setup_labels()

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def __set_mp4_state(self, video_codec_text, audio_codec_text):
        self.streaming_checkbox.set_sensitive(True)
        self.__rebuild_mp4_video_codec_combobox()
        self.__rebuild_mp4_audio_codec_combobox()

        if self.__is_widgets_setting_up:
            return

        self.__is_widgets_setting_up = True

        self.__setup_mp4_video_codec_widgets(video_codec_text)
        self.__setup_mp4_audio_codec_widgets(audio_codec_text)

        self.__is_widgets_setting_up = False

    def __rebuild_mp4_video_codec_combobox(self):
        if AppRequirements.is_nvenc_supported():
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_mp4_nvenc_ui_list)
        else:
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_mp4_ui_list)

    def __rebuild_video_codec_combobox(self, video_codec_combobox_list):
        from render_watch.startup.app_ui import AppUI  # Can't do a global import because app_ui imports this class too

        self.__is_video_codec_combobox_being_rebuilt = True

        AppUI.rebuild_combobox(self.video_codec_combobox, video_codec_combobox_list)

        self.__is_video_codec_combobox_being_rebuilt = False

    def __rebuild_mp4_audio_codec_combobox(self):
        self.__rebuild_audio_codec_combobox(GeneralSettings.audio_codec_mp4_ui_list)

    def __rebuild_audio_codec_combobox(self, audio_codec_combobox_list):
        from render_watch.startup.app_ui import AppUI  # Can't do a global import because app_ui imports this class too

        self.__is_audio_codec_combobox_being_rebuilt = True

        AppUI.rebuild_combobox(self.audio_codec_combobox, audio_codec_combobox_list)

        self.__is_audio_codec_combobox_being_rebuilt = False

    def __setup_mp4_video_codec_widgets(self, video_codec_text):
        if AppRequirements.is_nvenc_supported():

            if video_codec_text in GeneralSettings.video_codec_mp4_nvenc_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_mp4_nvenc_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True
        else:

            if video_codec_text in GeneralSettings.video_codec_mp4_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_mp4_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True

    def __setup_mp4_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.audio_codec_mp4_ui_list:
            self.audio_codec_combobox.set_active(
                GeneralSettings.audio_codec_mp4_ui_list.index(audio_codec_text))
        else:
            self.__is_widgets_setting_up = False

            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

            self.__is_widgets_setting_up = True

    def __set_mkv_state(self, video_codec_text, audio_codec_text):
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self.__rebuild_mkv_video_codec_combobox()
        self.__rebuild_mkv_audio_codec_combobox()

        if self.__is_widgets_setting_up:
            return

        self.__is_widgets_setting_up = True

        self.__setup_mkv_video_codec_widgets(video_codec_text)
        self.__setup_mkv_audio_codec_widgets(audio_codec_text)

        self.__is_widgets_setting_up = False

    def __rebuild_mkv_video_codec_combobox(self):
        if AppRequirements.is_nvenc_supported():
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_mkv_nvenc_ui_list)
        else:
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_mkv_ui_list)

    def __rebuild_mkv_audio_codec_combobox(self):
        self.__rebuild_audio_codec_combobox(GeneralSettings.audio_codec_mkv_ui_list)

    def __setup_mkv_video_codec_widgets(self, video_codec_text):
        if AppRequirements.is_nvenc_supported():

            if video_codec_text in GeneralSettings.video_codec_mkv_nvenc_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_mkv_nvenc_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True
        else:

            if video_codec_text in GeneralSettings.video_codec_mkv_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_mkv_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True

    def __setup_mkv_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.audio_codec_mkv_ui_list:
            self.audio_codec_combobox.set_active(
                GeneralSettings.audio_codec_mkv_ui_list.index(audio_codec_text))
        else:
            self.__is_widgets_setting_up = False

            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

            self.__is_widgets_setting_up = True

    def __set_ts_state(self, video_codec_text, audio_codec_text):
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self.__rebuild_ts_video_codec_combobox()
        self.__rebuild_ts_audio_codec_combobox()

        if self.__is_widgets_setting_up:
            return

        self.__is_widgets_setting_up = True

        self.__setup_ts_video_codec_widgets(video_codec_text)
        self.__setup_ts_audio_codec_widgets(audio_codec_text)

        self.__is_widgets_setting_up = False

    def __rebuild_ts_video_codec_combobox(self):
        if AppRequirements.is_nvenc_supported():
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_ts_nvenc_ui_list)
        else:
            self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_ts_ui_list)

    def __rebuild_ts_audio_codec_combobox(self):
        self.__rebuild_audio_codec_combobox(GeneralSettings.audio_codec_ts_ui_list)

    def __setup_ts_video_codec_widgets(self, video_codec_text):
        if AppRequirements.is_nvenc_supported():

            if video_codec_text in GeneralSettings.video_codec_ts_nvenc_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_ts_nvenc_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True
        else:

            if video_codec_text in GeneralSettings.video_codec_ts_ui_list:
                self.video_codec_combobox.set_active(
                    GeneralSettings.video_codec_ts_ui_list.index(video_codec_text))
            else:
                self.__is_widgets_setting_up = False

                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)

                self.__is_widgets_setting_up = True

    def __setup_ts_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.audio_codec_ts_ui_list:
            self.audio_codec_combobox.set_active(
                GeneralSettings.audio_codec_ts_ui_list.index(audio_codec_text))
        else:
            self.__is_widgets_setting_up = False

            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

            self.__is_widgets_setting_up = True

    def __setup_webm_state(self, video_codec_text, audio_codec_text):
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self.__rebuild_webm_video_codec_combobox()
        self.__rebuild_webm_audio_codec_combobox()

        if self.__is_widgets_setting_up:
            return

        self.__is_widgets_setting_up = True

        self.__setup_webm_video_codec_widgets(video_codec_text)
        self.__setup_webm_audio_codec_widgets(audio_codec_text)

        self.__is_widgets_setting_up = False

    def __rebuild_webm_video_codec_combobox(self):
        self.__rebuild_video_codec_combobox(GeneralSettings.video_codec_webm_ui_list)

    def __rebuild_webm_audio_codec_combobox(self):
        self.__rebuild_audio_codec_combobox(GeneralSettings.audio_codec_webm_ui_list)

    def __setup_webm_video_codec_widgets(self, video_codec_text):
        if video_codec_text in GeneralSettings.video_codec_webm_ui_list:
            self.video_codec_combobox.set_active(
                GeneralSettings.video_codec_webm_ui_list.index(video_codec_text))
        else:
            self.__is_widgets_setting_up = False

            self.video_codec_combobox.set_active(0)
            self.on_video_codec_combobox_changed(self.video_codec_combobox)

            self.__is_widgets_setting_up = True

    def __setup_webm_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.audio_codec_webm_ui_list:
            self.audio_codec_combobox.set_active(
                GeneralSettings.audio_codec_webm_ui_list.index(audio_codec_text))
        else:
            self.__is_widgets_setting_up = False

            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

            self.__is_widgets_setting_up = True

    def on_video_codec_combobox_changed(self, video_codec_combobox):
        video_codec_text = video_codec_combobox.get_active_text()

        if video_codec_text is None or self.__is_video_codec_combobox_being_rebuilt:
            return

        video_settings = self.__setup_video_settings(video_codec_text)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings = video_settings

            row.setup_labels()

        self.__set_benchmark_state()
        self.inputs_page_handlers.update_preview_page()

    def __setup_video_settings(self, video_codec_text):
        if video_codec_text == "H264":
            video_settings = X264()

            self.video_stack.set_visible_child(self.x264_box)
            self.__reset_settings_for_x265_handlers()
            self.__reset_settings_for_nvenc_handlers()
            self.__reset_settings_for_vp9_handlers()
        elif video_codec_text == "H265":
            video_settings = X265()

            self.video_stack.set_visible_child(self.x265_box)
            self.__reset_settings_for_x264_handlers()
            self.__reset_settings_for_nvenc_handlers()
            self.__reset_settings_for_vp9_handlers()
        elif 'NVENC' in video_codec_text:
            if not self.__is_widgets_setting_up:
                if video_codec_text == 'NVENC H264':
                    video_settings = H264Nvenc()

                    self.nvenc_handlers.set_h264_state()
                else:
                    video_settings = HevcNvenc()

                    self.nvenc_handlers.set_hevc_state()

                self.__reset_settings_for_nvenc_handlers()
            else:
                video_settings = None

            self.video_stack.set_visible_child(self.nvenc_box)
            self.__reset_settings_for_x264_handlers()
            self.__reset_settings_for_x265_handlers()
            self.__reset_settings_for_vp9_handlers()
        elif video_codec_text == 'VP9':
            video_settings = VP9()

            self.video_stack.set_visible_child(self.vp9_box)
            self.__reset_settings_for_x264_handlers()
            self.__reset_settings_for_x265_handlers()
            self.__reset_settings_for_nvenc_handlers()
        else:
            video_settings = None

            self.video_stack.set_visible_child(self.video_noavail_label)
            self.__reset_settings_for_x264_handlers()
            self.__reset_settings_for_x265_handlers()
            self.__reset_settings_for_nvenc_handlers()
            self.__reset_settings_for_vp9_handlers()

        return video_settings

    def __reset_settings_for_x264_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.x264_handlers.reset_settings,)).start()

    def __reset_settings_for_x265_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.x265_handlers.reset_settings,)).start()

    def __reset_settings_for_nvenc_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.nvenc_handlers.reset_settings,)).start()

    def __reset_settings_for_vp9_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.vp9_handlers.reset_settings,)).start()

    def on_audio_codec_combobox_changed(self, audio_codec_combobox):
        audio_text = audio_codec_combobox.get_active_text()

        if audio_text is None or self.__is_audio_codec_combobox_being_rebuilt:
            return

        audio_settings = self.__setup_audio_settings(audio_text)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings = audio_settings

            row.setup_labels()

    def __setup_audio_settings(self, audio_text):
        if audio_text == "aac":
            audio_settings = Aac()

            self.audio_stack.set_visible_child(self.aac_box)
            self.__reset_settings_for_opus_handlers()
        elif audio_text == 'opus':
            audio_settings = Opus()

            self.audio_stack.set_visible_child(self.opus_box)
            self.__reset_settings_for_aac_handlers()
        else:
            audio_settings = None

            self.audio_stack.set_visible_child(self.audio_noavail_label)
            self.__reset_settings_for_aac_handlers()
            self.__reset_settings_for_opus_handlers()

        return audio_settings

    def __reset_settings_for_aac_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.aac_handlers.reset_settings,)).start()

    def __reset_settings_for_opus_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.opus_handlers.reset_settings,)).start()

    def on_framerate_auto_radiobutton_clicked(self, frame_rate_auto_radiobutton):
        if not frame_rate_auto_radiobutton.get_active():
            return

        self.fps_box.set_sensitive(False)

        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_framerate_custom_radiobutton_clicked(self, frame_rate_custom_radiobutton):
        if not frame_rate_custom_radiobutton.get_active():
            return

        self.fps_box.set_sensitive(True)

        if self.__is_widgets_setting_up:
            return

        frame_rate_index = self.fps_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = frame_rate_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_fps_combobox_changed(self, frame_rate_combobox):
        if self.__is_widgets_setting_up:
            return

        frame_rate_index = frame_rate_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = frame_rate_index

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_streaming_checkbox_toggled(self, streaming_checkbox):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.fast_start = streaming_checkbox.get_active()

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_benchmark_start_button_clicked(self, benchmark_start_button):
        ffmpeg = self.inputs_page_handlers.get_selected_row().ffmpeg

        if ffmpeg is None:
            return

        threading.Thread(target=self.__start_benchmark_thread, args=(ffmpeg,), daemon=True).start()

    def __start_benchmark_thread(self, ffmpeg):
        self.__stop_benchmark_thread()

        with self.__benchmark_thread_lock:
            self.benchmark_thread = threading.Thread(target=preview.start_benchmark,
                                                     args=(ffmpeg, self, lambda: self.stop_benchmark_thread,
                                                           self.preferences))

            self.benchmark_thread.start()

    def on_benchmark_stop_button_clicked(self, benchmark_stop_button):
        threading.Thread(target=self.__stop_benchmark_thread, args=(), daemon=True).start()

    def __stop_benchmark_thread(self):
        with self.__benchmark_thread_lock:
            if self.benchmark_thread is not None and self.benchmark_thread.is_alive():
                self.stop_benchmark_thread = True
                self.benchmark_thread.join()
                self.stop_benchmark_thread = False

    def on_crop_button_clicked(self, crop_button):
        if not self.inputs_page_handlers.is_crop_state():
            self.inputs_page_handlers.set_crop_state()
            self.crop_page_handlers.setup_crop_page()

    def on_trim_button_clicked(self, trim_button):
        if not self.inputs_page_handlers.is_trim_state():
            self.inputs_page_handlers.set_trim_state()
            self.trim_page_handlers.setup_trim_page()

    def on_preview_button_clicked(self, preview_button):
        if not self.inputs_page_handlers.is_preview_state():
            self.inputs_page_handlers.set_preview_state()
            self.preview_page_handlers.setup_preview_page()
