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


import threading

from render_watch.ffmpeg.general_settings import GeneralSettings
from render_watch.ffmpeg.x264 import X264
from render_watch.ffmpeg.x265 import X265
from render_watch.ffmpeg.vp9 import VP9
from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.ffmpeg.hevc_nvenc import HevcNvenc
from render_watch.ffmpeg.aac import Aac
from render_watch.ffmpeg.opus import Opus
from render_watch.app_handlers.x264_handlers import X264Handlers
from render_watch.app_handlers.x265_handlers import X265Handlers
from render_watch.app_handlers.nvenc_handlers import NvencHandlers
from render_watch.app_handlers.vp9_handlers import VP9Handlers
from render_watch.app_handlers.aac_handlers import AacHandlers
from render_watch.app_handlers.opus_handlers import OpusHandlers
from render_watch.app_handlers.subtitles_handlers import SubtitlesHandlers
from render_watch.signals.settings_sidebar.audio_codec_signal import AudioCodecSignal
from render_watch.signals.settings_sidebar.start_benchmark_signal import StartBenchmarkSignal
from render_watch.signals.settings_sidebar.stop_benchmark_signal import StopBenchmarkSignal
from render_watch.signals.settings_sidebar.container_signal import ContainerSignal
from render_watch.signals.settings_sidebar.crop_signal import CropSignal
from render_watch.signals.settings_sidebar.framerate_signal import FramerateSignal
from render_watch.signals.settings_sidebar.preview_signal import PreviewSignal
from render_watch.signals.settings_sidebar.streaming_optimized_signal import StreamingOptimizedSignal
from render_watch.signals.settings_sidebar.trim_signal import TrimSignal
from render_watch.signals.settings_sidebar.video_codec_signal import VideoCodecSignal
from render_watch.helpers.ui_helper import UIHelper
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.startup import GLib


class SettingsSidebarHandlers:
    """
    Handles all widget changes within the settings sidebar.
    """

    def __init__(self,
                 gtk_builder,
                 crop_page_handler,
                 trim_page_handlers,
                 preview_page_handlers,
                 inputs_page_handlers,
                 main_window_handlers,
                 application_preferences):
        self.gtk_builder = gtk_builder
        self.inputs_page_handlers = inputs_page_handlers
        self.is_widgets_setting_up = False
        self.is_video_codec_transitioning = False
        self.is_audio_codec_transitioning = False
        self.benchmark_thread = None
        self.is_benchmark_thread_stopping = False
        self.benchmark_thread_lock = threading.Lock()
        self.x264_handlers = X264Handlers(gtk_builder, inputs_page_handlers, application_preferences)
        self.x265_handlers = X265Handlers(gtk_builder, inputs_page_handlers, application_preferences)
        self.nvenc_handlers = NvencHandlers(gtk_builder, inputs_page_handlers, main_window_handlers)
        self.vp9_handlers = VP9Handlers(gtk_builder, inputs_page_handlers, application_preferences)
        self.aac_handlers = AacHandlers(gtk_builder, inputs_page_handlers)
        self.opus_handlers = OpusHandlers(gtk_builder, inputs_page_handlers)
        self.subtitles_handlers = SubtitlesHandlers(gtk_builder, inputs_page_handlers)

        self.audio_codec_signal = AudioCodecSignal(self, inputs_page_handlers)
        self.benchmark_start_signal = StartBenchmarkSignal(self, inputs_page_handlers, application_preferences)
        self.benchmark_stop_signal = StopBenchmarkSignal(self)
        self.container_signal = ContainerSignal(self, inputs_page_handlers)
        self.crop_signal = CropSignal(crop_page_handler, inputs_page_handlers)
        self.framerate_signal = FramerateSignal(self, inputs_page_handlers)
        self.preview_signal = PreviewSignal(preview_page_handlers, inputs_page_handlers)
        self.streaming_signal = StreamingOptimizedSignal(self, inputs_page_handlers)
        self.trim_signal = TrimSignal(trim_page_handlers, inputs_page_handlers)
        self.video_codec_signal = VideoCodecSignal(self, inputs_page_handlers)
        self.handlers_list = (
            self.x264_handlers, self.x265_handlers, self.nvenc_handlers, self.vp9_handlers,
            self.aac_handlers, self.opus_handlers, self.subtitles_handlers, self.audio_codec_signal,
            self.video_codec_signal, self.streaming_signal, self.framerate_signal, self.benchmark_start_signal,
            self.benchmark_stop_signal, self.container_signal, self.crop_signal, self.trim_signal,
            self.preview_signal
        )

        self.container_combobox = gtk_builder.get_object("container_combobox")
        self.streaming_optimized_checkbutton = gtk_builder.get_object("streaming_optimized_checkbutton")
        self.video_codec_combobox = gtk_builder.get_object("video_codec_combobox")
        self.video_settings_stack = gtk_builder.get_object("video_settings_stack")
        self.x264_settings_box = gtk_builder.get_object("x264_settings_box")
        self.x265_settings_box = gtk_builder.get_object("x265_settings_box")
        self.nvenc_settings_box = gtk_builder.get_object('nvenc_settings_box')
        self.vp9_settings_box = gtk_builder.get_object('vp9_settings_box')
        self.video_settings_not_available_label = gtk_builder.get_object("video_settings_not_available_label")
        self.audio_codec_combobox = gtk_builder.get_object("audio_codec_combobox")
        self.audio_settings_stack = gtk_builder.get_object("audio_settings_stack")
        self.audio_settings_not_available_label = gtk_builder.get_object("audio_settings_not_available_label")
        self.aac_settings_box = gtk_builder.get_object("aac_settings_box")
        self.opus_settings_box = gtk_builder.get_object('opus_settings_box')
        self.fps_box = gtk_builder.get_object("fps_box")
        self.fps_combobox = gtk_builder.get_object('fps_combobox')
        self.same_frame_rate_radiobutton = gtk_builder.get_object("same_frame_rate_radiobutton")
        self.custom_frame_rate_radiobutton = gtk_builder.get_object("custom_frame_rate_radiobutton")
        self.benchmark_run_button = gtk_builder.get_object('benchmark_run_button')
        self.benchmark_stop_button = gtk_builder.get_object('benchmark_stop_button')
        self.benchmark_status_stack = gtk_builder.get_object('benchmark_status_stack')
        self.benchmark_not_available_label = gtk_builder.get_object('benchmark_not_available_label')
        self.benchmark_values_grid = gtk_builder.get_object('benchmark_values_grid')
        self.benchmark_speed_value_label = gtk_builder.get_object('benchmark_speed_value_label')
        self.benchmark_bitrate_value_label = gtk_builder.get_object('benchmark_bitrate_value_label')
        self.benchmark_proc_time_value_label = gtk_builder.get_object('benchmark_proc_time_value_label')
        self.benchmark_file_size_value_label = gtk_builder.get_object('benchmark_file_size_value_label')
        self.benchmark_progressbar = gtk_builder.get_object('benchmark_progressbar')
        self.benchmark_short_radiobutton = gtk_builder.get_object('benchmark_short_radiobutton')
        self.benchmark_bottom_button_stack = gtk_builder.get_object('benchmark_button_stack')
        self.crop_button = gtk_builder.get_object('crop_button')
        self.trim_button = gtk_builder.get_object('trim_button')
        self.preview_button = gtk_builder.get_object('preview_button')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for handler in self.handlers_list:
            if hasattr(handler, signal_name):
                return getattr(handler, signal_name)
        raise AttributeError

    def apply_settings(self, ffmpeg):
        """
        Applies settings from the Settings Sidebar widgets to ffmpeg settings.
        """
        self._apply_general_settings(ffmpeg)
        self._apply_video_codec_settings(ffmpeg)
        self._apply_audio_codec_settings(ffmpeg)

    def _apply_general_settings(self, ffmpeg):
        general_settings = GeneralSettings()
        general_settings.fast_start = self.streaming_optimized_checkbutton.get_active()
        self._apply_output_container_settings(ffmpeg)
        self._apply_frame_rate_settings(general_settings)
        ffmpeg.general_settings = general_settings

    def _apply_output_container_settings(self, ffmpeg):
        ffmpeg.output_container = GeneralSettings.CONTAINERS_UI_LIST[self.container_combobox.get_active()]

    def _apply_frame_rate_settings(self, general_settings):
        if self.custom_frame_rate_radiobutton.get_active():
            general_settings.frame_rate = GeneralSettings.FRAME_RATE_ARGS_LIST[self.fps_combobox.get_active()]

    def _apply_video_codec_settings(self, ffmpeg):
        video_codec_name = self.video_codec_combobox.get_active_text()
        if video_codec_name == 'H264':
            self.x264_handlers.apply_settings(ffmpeg)
        elif video_codec_name == 'H265':
            self.x265_handlers.apply_settings(ffmpeg)
        elif 'NVENC' in video_codec_name:
            self.nvenc_handlers.get_settings(ffmpeg)
        elif video_codec_name == 'VP9':
            self.vp9_handlers.apply_settings(ffmpeg)
        else:
            ffmpeg.video_settings = None

    def _apply_audio_codec_settings(self, ffmpeg):
        audio_codec_name = self.audio_codec_combobox.get_active_text()
        if audio_codec_name == 'aac':
            self.aac_handlers.get_settings(ffmpeg)
        elif audio_codec_name == 'opus':
            self.opus_handlers.get_settings(ffmpeg)
        else:
            ffmpeg.audio_settings = None

    def set_settings(self, ffmpeg_param=None):
        """
        Configures the Settings Sidebar widgets to match the selected task's ffmpeg settings.
        """
        if ffmpeg_param:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self._set_general_settings(ffmpeg)
        self._set_settings_for_x264_handlers(ffmpeg_param)
        self._set_settings_for_x265_handlers(ffmpeg_param)
        self._set_settings_for_nvenc_handlers(ffmpeg_param)
        self._set_settings_for_vp9_handlers(ffmpeg_param)
        self._set_settings_for_aac_handlers(ffmpeg_param)
        self._set_settings_for_opus_handlers(ffmpeg_param)
        self.subtitles_handlers.set_settings()
        self.set_benchmark_state()

    def _set_general_settings(self, ffmpeg):
        video_settings = ffmpeg.video_settings
        audio_settings = ffmpeg.audio_settings
        general_settings = ffmpeg.general_settings
        output_container = ffmpeg.output_container
        is_output_container_set = ffmpeg.is_output_container_set()

        self.is_widgets_setting_up = True
        self._setup_output_container(output_container, is_output_container_set)
        self.streaming_optimized_checkbutton.set_active(general_settings.fast_start)
        self._setup_frame_rate(general_settings)
        self._setup_video_codec(video_settings)
        self._setup_audio_codec(audio_settings)
        self.is_widgets_setting_up = False

    def _setup_output_container(self, output_container, is_output_container_set):
        if is_output_container_set:
            self.container_combobox.set_active(GeneralSettings.CONTAINERS_UI_LIST.index(output_container))
        else:
            self.container_combobox.set_active(1)

    def _setup_frame_rate(self, general_settings):
        if general_settings.frame_rate is not None:
            self.custom_frame_rate_radiobutton.set_active(True)
            self.fps_combobox.set_active(general_settings.frame_rate)
        else:
            self.same_frame_rate_radiobutton.set_active(True)
            self.fps_combobox.set_active(0)

    def _setup_video_codec(self, video_settings):
        if video_settings:
            self._setup_video_codec_combobox(video_settings)
        else:
            self._reset_video_codec_combobox()

    def _setup_video_codec_combobox(self, video_settings):
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

    def _reset_video_codec_combobox(self):
        if self.video_codec_combobox.get_active() != 0:
            self.video_codec_combobox.set_active(0)
        else:
            self.on_video_codec_combobox_changed(self.video_codec_combobox)

    def _setup_audio_codec(self, audio_settings):
        if not self.inputs_page_handlers.get_selected_row_ffmpeg().input_file_info['audio_streams']:
            self._reset_audio_codec_combobox()
            self.audio_codec_combobox.set_sensitive(False)
        else:
            self.audio_codec_combobox.set_sensitive(True)

        if audio_settings:
            self._setup_audio_codec_combobox(audio_settings)
        else:
            self._reset_audio_codec_combobox()

    def _setup_audio_codec_combobox(self, audio_settings):
        if audio_settings.codec_name == 'aac':
            self.audio_codec_combobox.set_active(1)
        elif audio_settings.codec_name == 'libopus':
            if self.container_combobox.get_active() == 1:
                self.audio_codec_combobox.set_active(2)
            else:
                self.audio_codec_combobox.set_active(1)

    def _reset_audio_codec_combobox(self):
        if self.audio_codec_combobox.get_active() != 0:
            self.audio_codec_combobox.set_active(0)
        else:
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

    def _set_settings_for_x264_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.x264_handlers.set_settings, ffmpeg)
        else:
            args = (self.x264_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_x265_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.x265_handlers.set_settings, ffmpeg)
        else:
            args = (self.x265_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_nvenc_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.nvenc_handlers.set_settings, ffmpeg)
        else:
            args = (self.nvenc_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_vp9_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.vp9_handlers.set_settings, ffmpeg)
        else:
            args = (self.vp9_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_aac_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.aac_handlers.set_settings, ffmpeg)
        else:
            args = (self.aac_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_opus_handlers(self, ffmpeg=None):
        if ffmpeg:
            args = (self.opus_handlers.set_settings, ffmpeg)
        else:
            args = (self.opus_handlers.set_settings,)

        threading.Thread(target=GLib.idle_add, args=args).start()

    def reset_settings(self):
        """
        Resets the Settings Sidebar widgets to their default values.
        """
        self.is_widgets_setting_up = True
        self.container_combobox.set_active(0)
        self.fps_combobox.set_active(0)
        self.video_codec_combobox.set_active(0)
        self.audio_codec_combobox.set_active(0)
        self.streaming_optimized_checkbutton.set_active(False)
        self.same_frame_rate_radiobutton.set_active(True)
        self.x265_handlers.reset_settings()
        self.x264_handlers.reset_settings()
        self.nvenc_handlers.reset_settings()
        self.vp9_handlers.reset_settings()
        self.aac_handlers.reset_settings()
        self.opus_handlers.reset_settings()
        self.set_benchmark_state()
        self.is_widgets_setting_up = False

    def set_benchmark_state(self):
        """
        Toggles accessibility to the benchmark tool.
        """
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            is_video_settings_enabled = inputs_row.ffmpeg.video_settings is not None
            is_folder_state_enabled = inputs_row.ffmpeg.folder_state
            state = is_video_settings_enabled and not is_folder_state_enabled
        else:
            state = False

        if state:
            self.set_benchmark_ready_state()
        else:
            self._set_benchmark_not_available_state()

    def set_benchmark_ready_state(self):
        """
        Sets the benchmark tool to it's ready state.
        """
        self.benchmark_status_stack.set_visible_child(self.benchmark_values_grid)
        self.benchmark_bottom_button_stack.set_sensitive(True)
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_run_button)
        self.benchmark_speed_value_label.set_text('')
        self.benchmark_bitrate_value_label.set_text('')
        self.benchmark_proc_time_value_label.set_text('')
        self.benchmark_file_size_value_label.set_text('')
        self.benchmark_progressbar.set_fraction(0.0)
        self.set_extra_settings_state(True)

    def _set_benchmark_not_available_state(self):
        self.benchmark_status_stack.set_visible_child(self.benchmark_not_available_label)
        self.benchmark_bottom_button_stack.set_sensitive(False)
        self.on_benchmark_stop_button_clicked(self.benchmark_stop_button)

    def get_video_codec_value(self):
        return self.video_codec_combobox.get_active_text()

    def get_audio_codec_value(self):
        return self.audio_codec_combobox.get_active_text()

    def get_framerate_value(self):
        return self.fps_combobox.get_active()

    def is_benchmark_short_radiobutton_active(self):
        return self.benchmark_short_radiobutton.get_active()

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
        self.benchmark_progressbar.set_fraction(0.0)
        self.set_extra_settings_state(False)

    def set_benchmark_progress_bar_fraction(self, progress_fraction):
        self.benchmark_progressbar.set_fraction(progress_fraction)

    def set_benchmark_bitrate_label_text(self, bitrate_label_text):
        self.benchmark_bitrate_value_label.set_text(bitrate_label_text)

    def set_benchmark_speed_label_text(self, speed_label_text):
        self.benchmark_speed_value_label.set_text(speed_label_text)

    def set_benchmark_process_time_label_text(self, process_time_label_text):
        self.benchmark_proc_time_value_label.set_text(process_time_label_text)

    def set_benchmark_file_size_label_text(self, file_size_label_text):
        self.benchmark_file_size_value_label.set_text(file_size_label_text)

    def set_benchmark_done_state(self):
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_run_button)
        self.set_extra_settings_state(True)

    def set_mp4_state(self):
        """
        Setup Settings Sidebar widgets for the mp4 container.
        """
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()

        self.streaming_optimized_checkbutton.set_sensitive(True)
        self._rebuild_mp4_video_codec_combobox()
        self._rebuild_mp4_audio_codec_combobox()

        if self.is_widgets_setting_up:
            return

        self.is_widgets_setting_up = True
        self._setup_mp4_video_codec_widgets(video_codec_text)
        self._setup_mp4_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

        self.subtitles_handlers.set_restricted_state()

    def _rebuild_mp4_video_codec_combobox(self):
        if NvidiaHelper.is_nvenc_supported():
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST)
        else:
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MP4_UI_LIST)

    def _rebuild_video_codec_combobox(self, video_codec_combobox_list):
        self.is_video_codec_transitioning = True
        UIHelper.rebuild_combobox(self.video_codec_combobox, video_codec_combobox_list)
        self.is_video_codec_transitioning = False

    def _rebuild_mp4_audio_codec_combobox(self):
        self._rebuild_audio_codec_combobox(GeneralSettings.AUDIO_CODEC_MP4_UI_LIST)

    def _rebuild_audio_codec_combobox(self, audio_codec_combobox_list):
        self.is_audio_codec_transitioning = True
        UIHelper.rebuild_combobox(self.audio_codec_combobox, audio_codec_combobox_list)
        self.is_audio_codec_transitioning = False

    def _setup_mp4_video_codec_widgets(self, video_codec_text):
        if NvidiaHelper.is_nvenc_supported():
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST.index(video_codec_text))

                return
        else:
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MP4_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MP4_UI_LIST.index(video_codec_text))

                return

        self.is_widgets_setting_up = False
        self._reset_and_signal_video_codec_combobox()
        self.is_widgets_setting_up = True

    def _reset_and_signal_video_codec_combobox(self):
        self.video_codec_combobox.set_active(0)
        self.on_video_codec_combobox_changed(self.video_codec_combobox)

    def _setup_mp4_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_MP4_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_MP4_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self._reset_and_signal_audio_codec_combobox()
            self.is_widgets_setting_up = True

    def _reset_and_signal_audio_codec_combobox(self):
        self.audio_codec_combobox.set_active(0)
        self.on_audio_codec_combobox_changed(self.audio_codec_combobox)

    def set_mkv_state(self):
        """
        Setup Settings Sidebar widgets for the mkv container.
        """
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()

        self.streaming_optimized_checkbutton.set_sensitive(False)
        self.streaming_optimized_checkbutton.set_active(False)
        self._rebuild_mkv_video_codec_combobox()
        self._rebuild_mkv_audio_codec_combobox()

        if self.is_widgets_setting_up:
            return

        self.is_widgets_setting_up = True
        self._setup_mkv_video_codec_widgets(video_codec_text)
        self._setup_mkv_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

        self.subtitles_handlers.set_unrestricted_state()

    def _rebuild_mkv_video_codec_combobox(self):
        if NvidiaHelper.is_nvenc_supported():
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MKV_NVENC_UI_LIST)
        else:
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MKV_UI_LIST)

    def _rebuild_mkv_audio_codec_combobox(self):
        self._rebuild_audio_codec_combobox(GeneralSettings.AUDIO_CODEC_MKV_UI_LIST)

    def _setup_mkv_video_codec_widgets(self, video_codec_text):
        if NvidiaHelper.is_nvenc_supported():
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MKV_NVENC_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MKV_NVENC_UI_LIST.index(video_codec_text))

                return
        else:
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MKV_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MKV_UI_LIST.index(video_codec_text))

                return

        self.is_widgets_setting_up = False
        self._reset_and_signal_video_codec_combobox()
        self.is_widgets_setting_up = True

    def _setup_mkv_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_MKV_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_MKV_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self._reset_and_signal_audio_codec_combobox()
            self.is_widgets_setting_up = True

    def set_ts_state(self):
        """
        Setup Settings Sidebar widgets for the ts container.
        """
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()

        self.streaming_optimized_checkbutton.set_sensitive(False)
        self.streaming_optimized_checkbutton.set_active(False)
        self._rebuild_ts_video_codec_combobox()
        self._rebuild_ts_audio_codec_combobox()

        if self.is_widgets_setting_up:
            return

        self.is_widgets_setting_up = True
        self._setup_ts_video_codec_widgets(video_codec_text)
        self._setup_ts_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

        self.subtitles_handlers.set_restricted_state()

    def _rebuild_ts_video_codec_combobox(self):
        if NvidiaHelper.is_nvenc_supported():
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_TS_NVENC_UI_LIST)
        else:
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_TS_UI_LIST)

    def _rebuild_ts_audio_codec_combobox(self):
        self._rebuild_audio_codec_combobox(GeneralSettings.AUDIO_CODEC_TS_UI_LIST)

    def _setup_ts_video_codec_widgets(self, video_codec_text):
        if NvidiaHelper.is_nvenc_supported():
            if video_codec_text in GeneralSettings.VIDEO_CODEC_TS_NVENC_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_TS_NVENC_UI_LIST.index(video_codec_text))

                return
        else:

            if video_codec_text in GeneralSettings.VIDEO_CODEC_TS_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_TS_UI_LIST.index(video_codec_text))

                return

        self.is_widgets_setting_up = False
        self._reset_and_signal_video_codec_combobox()
        self.is_widgets_setting_up = True

    def _setup_ts_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_TS_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_TS_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self._reset_and_signal_audio_codec_combobox()
            self.is_widgets_setting_up = True

    def set_webm_state(self):
        """
        Setup Settings Sidebar widgets for the webm container.
        """
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()

        self.streaming_optimized_checkbutton.set_sensitive(False)
        self.streaming_optimized_checkbutton.set_active(False)
        self._rebuild_webm_video_codec_combobox()
        self._rebuild_webm_audio_codec_combobox()

        if self.is_widgets_setting_up:
            return

        self.is_widgets_setting_up = True
        self._setup_webm_video_codec_widgets(video_codec_text)
        self._setup_webm_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

        self.subtitles_handlers.set_restricted_state()

    def _rebuild_webm_video_codec_combobox(self):
        self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_WEBM_UI_LIST)

    def _rebuild_webm_audio_codec_combobox(self):
        self._rebuild_audio_codec_combobox(GeneralSettings.AUDIO_CODEC_WEBM_UI_LIST)

    def _setup_webm_video_codec_widgets(self, video_codec_text):
        if video_codec_text in GeneralSettings.VIDEO_CODEC_WEBM_UI_LIST:
            self.video_codec_combobox.set_active(
                GeneralSettings.VIDEO_CODEC_WEBM_UI_LIST.index(video_codec_text))
        else:
            self.is_widgets_setting_up = False
            self._reset_and_signal_video_codec_combobox()
            self.is_widgets_setting_up = True

    def _setup_webm_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_WEBM_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_WEBM_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self._reset_and_signal_audio_codec_combobox()
            self.is_widgets_setting_up = True

    def set_framerate_state(self, is_enabled):
        self.fps_box.set_sensitive(is_enabled)

        if not is_enabled:
            self.fps_combobox.set_active(0)

    def set_framerate_locked_state(self, is_framerate_locked_state):
        """
        Toggles access to the frame rate settings.
        """
        self.same_frame_rate_radiobutton.set_sensitive(not is_framerate_locked_state)
        self.custom_frame_rate_radiobutton.set_sensitive(not is_framerate_locked_state)

    def get_changed_video_codec_settings(self):
        video_codec_text = self.get_video_codec_value()

        if video_codec_text == "H264":
            video_settings = X264()
            self._change_to_x264_state()
        elif video_codec_text == "H265":
            video_settings = X265()
            self._change_to_x265_state()
        elif 'NVENC' in video_codec_text:
            if self.is_widgets_setting_up:
                video_settings = None
            else:
                if video_codec_text == 'NVENC H264':
                    video_settings = H264Nvenc()
                    self.nvenc_handlers.set_h264_state()
                else:
                    video_settings = HevcNvenc()
                    self.nvenc_handlers.set_hevc_state()

                self._reset_settings_for_nvenc_handlers()

            self._change_to_nvenc_state()
        elif video_codec_text == 'VP9':
            video_settings = VP9()
            self._change_to_vp9_state()
        else:
            video_settings = None
            self._change_to_video_copy_state()

        return video_settings

    def _change_to_x264_state(self):
        self.video_settings_stack.set_visible_child(self.x264_settings_box)
        self._reset_settings_for_x265_handlers()
        self._reset_settings_for_nvenc_handlers()
        self._reset_settings_for_vp9_handlers()

    def _change_to_x265_state(self):
        self.video_settings_stack.set_visible_child(self.x265_settings_box)
        self._reset_settings_for_x264_handlers()
        self._reset_settings_for_nvenc_handlers()
        self._reset_settings_for_vp9_handlers()

    def _change_to_nvenc_state(self):
        self.video_settings_stack.set_visible_child(self.nvenc_settings_box)
        self._reset_settings_for_x264_handlers()
        self._reset_settings_for_x265_handlers()
        self._reset_settings_for_vp9_handlers()

    def _change_to_vp9_state(self):
        self.video_settings_stack.set_visible_child(self.vp9_settings_box)
        self._reset_settings_for_x264_handlers()
        self._reset_settings_for_x265_handlers()
        self._reset_settings_for_nvenc_handlers()

    def _change_to_video_copy_state(self):
        self.video_settings_stack.set_visible_child(self.video_settings_not_available_label)
        self._reset_settings_for_x264_handlers()
        self._reset_settings_for_x265_handlers()
        self._reset_settings_for_nvenc_handlers()
        self._reset_settings_for_vp9_handlers()

    def _reset_settings_for_x264_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.x264_handlers.reset_settings,)).start()

    def _reset_settings_for_x265_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.x265_handlers.reset_settings,)).start()

    def _reset_settings_for_nvenc_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.nvenc_handlers.reset_settings,)).start()

    def _reset_settings_for_vp9_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.vp9_handlers.reset_settings,)).start()

    def update_audio_settings(self):
        audio_text = self.get_audio_codec_value()

        if audio_text == "aac":
            audio_settings = Aac()
            self._change_to_aac_state()
        elif audio_text == 'opus':
            audio_settings = Opus()
            self._change_to_opus_state()
        else:
            audio_settings = None
            self._change_to_audio_copy_state()

        return audio_settings

    def _change_to_aac_state(self):
        self.audio_settings_stack.set_visible_child(self.aac_settings_box)
        self._reset_settings_for_opus_handlers()

    def _change_to_opus_state(self):
        self.audio_settings_stack.set_visible_child(self.opus_settings_box)
        self._reset_settings_for_aac_handlers()

    def _change_to_audio_copy_state(self):
        self.audio_settings_stack.set_visible_child(self.audio_settings_not_available_label)
        self._reset_settings_for_aac_handlers()
        self._reset_settings_for_opus_handlers()

    def _reset_settings_for_aac_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.aac_handlers.reset_settings,)).start()

    def _reset_settings_for_opus_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.opus_handlers.reset_settings,)).start()

    def stop_benchmark_thread(self):
        with self.benchmark_thread_lock:
            if self.benchmark_thread and self.benchmark_thread.is_alive():
                self.is_benchmark_thread_stopping = True

        if self.is_benchmark_thread_stopping:
            self.benchmark_thread.join()
            self.is_benchmark_thread_stopping = False

    def signal_framerate_auto_radiobutton(self):
        self.same_frame_rate_radiobutton.set_active(True)
