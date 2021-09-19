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
from render_watch.signals.settings_sidebar.audio_codec_signal import AudioCodecSignal
from render_watch.signals.settings_sidebar.benchmark_start_signal import BenchmarkStartSignal
from render_watch.signals.settings_sidebar.benchmark_stop_signal import BenchmarkStopSignal
from render_watch.signals.settings_sidebar.container_signal import ContainerSignal
from render_watch.signals.settings_sidebar.crop_signal import CropSignal
from render_watch.signals.settings_sidebar.framerate_signal import FramerateSignal
from render_watch.signals.settings_sidebar.preview_signal import PreviewSignal
from render_watch.signals.settings_sidebar.streaming_signal import StreamingSignal
from render_watch.signals.settings_sidebar.trim_signal import TrimSignal
from render_watch.signals.settings_sidebar.video_codec_signal import VideoCodecSignal
from render_watch.helpers.ui_helper import UIHelper
from render_watch.helpers.nvidia_helper import NvidiaHelper
from render_watch.startup import GLib


class SettingsSidebarHandlers:
    """Handles all widget changes within the settings sidebar."""

    def __init__(self,
                 gtk_builder,
                 crop_page_handler,
                 trim_page_handlers,
                 preview_page_handlers,
                 inputs_page_handlers,
                 preferences):
        self.gtk_builder = gtk_builder
        self.inputs_page_handlers = inputs_page_handlers
        self.is_widgets_setting_up = False
        self.is_video_codec_transitioning = False
        self.is_audio_codec_transitioning = False
        self.benchmark_thread = None
        self.benchmark_thread_stopping = False
        self.benchmark_thread_lock = threading.Lock()
        self.x264_handlers = X264Handlers(gtk_builder, inputs_page_handlers, preferences)
        self.x265_handlers = X265Handlers(gtk_builder, inputs_page_handlers, preferences)
        self.nvenc_handlers = NvencHandlers(gtk_builder, inputs_page_handlers)
        self.vp9_handlers = VP9Handlers(gtk_builder, inputs_page_handlers, preferences)
        self.aac_handlers = AacHandlers(gtk_builder, inputs_page_handlers)
        self.opus_handlers = OpusHandlers(gtk_builder, inputs_page_handlers)
        self.audio_codec_signal = AudioCodecSignal(self, inputs_page_handlers)
        self.benchmark_start_signal = BenchmarkStartSignal(self, inputs_page_handlers, preferences)
        self.benchmark_stop_signal = BenchmarkStopSignal(self, inputs_page_handlers)
        self.container_signal = ContainerSignal(self, inputs_page_handlers)
        self.crop_signal = CropSignal(crop_page_handler, inputs_page_handlers)
        self.framerate_signal = FramerateSignal(self, inputs_page_handlers)
        self.preview_signal = PreviewSignal(preview_page_handlers, inputs_page_handlers)
        self.streaming_signal = StreamingSignal(self, inputs_page_handlers)
        self.trim_signal = TrimSignal(trim_page_handlers, inputs_page_handlers)
        self.video_codec_signal = VideoCodecSignal(self, inputs_page_handlers)
        self.handlers_list = (
            self.x264_handlers, self.x265_handlers, self.nvenc_handlers, self.vp9_handlers,
            self.aac_handlers, self.opus_handlers, self.audio_codec_signal, self.video_codec_signal,
            self.streaming_signal, self.framerate_signal, self.benchmark_start_signal,
            self.benchmark_stop_signal, self.container_signal, self.crop_signal, self.trim_signal,
            self.preview_signal
        )
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
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for handler in self.handlers_list:
            if hasattr(handler, signal_name):
                return getattr(handler, signal_name)
        raise AttributeError

    def get_settings(self, ffmpeg):
        """Applies settings to the ffmpeg settings object."""
        self._apply_general_settings_from_widgets(ffmpeg)
        self._apply_video_codec_settings_from_widgets(ffmpeg)
        self._apply_audio_codec_settings_from_widgets(ffmpeg)

    def _apply_general_settings_from_widgets(self, ffmpeg):
        # Applies the general settings to the ffmpeg settings object.
        general_settings = GeneralSettings()
        general_settings.fast_start = self.streaming_checkbox.get_active()
        self._apply_output_container_settings_from_widgets(ffmpeg)
        self._apply_frame_rate_settings_from_widgets(general_settings)
        ffmpeg.general_settings = general_settings

    def _apply_output_container_settings_from_widgets(self, ffmpeg):
        # Applies the output continer setting to the ffmpeg settings object.
        ffmpeg.output_container = GeneralSettings.CONTAINERS_UI_LIST[self.container_combobox.get_active()]

    def _apply_frame_rate_settings_from_widgets(self, general_settings):
        # Applies the frame rate setting to the ffmpeg settings object.
        if self.framerate_custom_button.get_active():
            general_settings.frame_rate = GeneralSettings.FRAME_RATE_ARGS_LIST[self.fps_combobox.get_active()]

    def _apply_video_codec_settings_from_widgets(self, ffmpeg):
        # Applies the video codec setting to the ffmpeg settings object.
        video_codec_text = self.video_codec_combobox.get_active_text()
        if video_codec_text == 'H264':
            self.x264_handlers.apply_settings(ffmpeg)
        elif video_codec_text == 'H265':
            self.x265_handlers.apply_settings(ffmpeg)
        elif 'NVENC' in video_codec_text:
            self.nvenc_handlers.get_settings(ffmpeg)
        elif video_codec_text == 'VP9':
            self.vp9_handlers.apply_settings(ffmpeg)
        else:
            ffmpeg.video_settings = None

    def _apply_audio_codec_settings_from_widgets(self, ffmpeg):
        # Applies the audio codec setting to the ffmpeg settings object.
        audio_codec_text = self.audio_codec_combobox.get_active_text()
        if audio_codec_text == 'aac':
            self.aac_handlers.get_settings(ffmpeg)
        elif audio_codec_text == 'opus':
            self.opus_handlers.get_settings(ffmpeg)
        else:
            ffmpeg.audio_settings = None

    def set_settings(self, ffmpeg_param=None):
        """Sets the settings widgets to match the ffmpeg settings object."""
        if ffmpeg_param is None:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        else:
            ffmpeg = ffmpeg_param
        self._set_general_settings(ffmpeg)
        self._set_settings_for_x264_handlers(ffmpeg_param)
        self._set_settings_for_x265_handlers(ffmpeg_param)
        self._set_settings_for_nvenc_handlers(ffmpeg_param)
        self._set_settings_for_vp9_handlers(ffmpeg_param)
        self._set_settings_for_aac_handlers(ffmpeg_param)
        self._set_settings_for_opus_handlers(ffmpeg_param)
        self.set_benchmark_state()

    def _set_general_settings(self, ffmpeg):
        # Set general settings widgets to match the ffmpeg settings object.
        video_settings = ffmpeg.video_settings
        audio_settings = ffmpeg.audio_settings
        general_settings = ffmpeg.general_settings
        output_container = ffmpeg.output_container
        is_output_container_set = ffmpeg.is_output_container_set()
        self.is_widgets_setting_up = True
        self._setup_output_container(output_container, is_output_container_set)
        self.streaming_checkbox.set_active(general_settings.fast_start)
        self._setup_frame_rate(general_settings)
        self._setup_video_codec(video_settings)
        self._setup_audio_codec(audio_settings)
        self.is_widgets_setting_up = False

    def _setup_output_container(self, output_container, is_output_container_set):
        # Set output container setting to match the ffmpeg settings object.
        if is_output_container_set:
            self.container_combobox.set_active(GeneralSettings.CONTAINERS_UI_LIST.index(output_container))
        else:
            self.container_combobox.set_active(1)

    def _setup_frame_rate(self, general_settings):
        # Set frame rate setting to match the ffmpeg settings object.
        if general_settings.frame_rate is not None:
            self.framerate_custom_button.set_active(True)
            self.fps_combobox.set_active(general_settings.frame_rate)
        else:
            self.framerate_auto_button.set_active(True)
            self.fps_combobox.set_active(0)

    def _setup_video_codec(self, video_settings):
        # Set video codec setting to match the ffmpeg settings object.
        if video_settings:
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

    def _setup_audio_codec(self, audio_settings):
        # Set audio codec setting to match the ffmpeg settings object.
        if audio_settings:
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

    def _set_settings_for_x264_handlers(self, ffmpeg=None):
        # Set x264 widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.x264_handlers.set_settings,)
        else:
            args = (self.x264_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_x265_handlers(self, ffmpeg=None):
        # Set x265 widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.x265_handlers.set_settings,)
        else:
            args = (self.x265_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_nvenc_handlers(self, ffmpeg=None):
        # Set NVENC widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.nvenc_handlers.set_settings,)
        else:
            args = (self.nvenc_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_vp9_handlers(self, ffmpeg=None):
        # Set VP9 widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.vp9_handlers.set_settings,)
        else:
            args = (self.vp9_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_aac_handlers(self, ffmpeg=None):
        # Set AAC widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.aac_handlers.set_settings,)
        else:
            args = (self.aac_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def _set_settings_for_opus_handlers(self, ffmpeg=None):
        # Set Opus widgets to match the ffmpeg settings object.
        if ffmpeg is None:
            args = (self.opus_handlers.set_settings,)
        else:
            args = (self.opus_handlers.set_settings, ffmpeg)
        threading.Thread(target=GLib.idle_add, args=args).start()

    def set_benchmark_state(self):
        """Toggles accessibility to the benchmark tool."""
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

    def reset_settings(self):
        """Resets the widgets to their default values."""
        self.is_widgets_setting_up = True
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
        self.set_benchmark_state()
        self.is_widgets_setting_up = False

    def set_benchmark_ready_state(self):
        """Sets the benchmark tool to it's ready state."""
        self.benchmark_stack.set_visible_child(self.benchmark_values_grid)
        self.benchmark_bottom_button_stack.set_sensitive(True)
        self.benchmark_bottom_button_stack.set_visible_child(self.benchmark_start_button)
        self.benchmark_speed_value_label.set_text('')
        self.benchmark_bitrate_value_label.set_text('')
        self.benchmark_proc_time_value_label.set_text('')
        self.benchmark_file_size_value_label.set_text('')
        self.benchmark_progress_bar.set_fraction(0.0)
        self.set_extra_settings_state(True)

    def _set_benchmark_not_available_state(self):
        # Sets the benchmark tool to an inaccessible state.
        self.benchmark_stack.set_visible_child(self.benchmark_noavail_label)
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
        self.benchmark_progress_bar.set_fraction(0.0)
        self.set_extra_settings_state(False)

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
        self.set_extra_settings_state(True)

    def set_mp4_state(self):
        """Setup widgets for the mp4 container."""
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()
        self.streaming_checkbox.set_sensitive(True)
        self._rebuild_mp4_video_codec_combobox()
        self._rebuild_mp4_audio_codec_combobox()
        if self.is_widgets_setting_up:
            return
        self.is_widgets_setting_up = True
        self._setup_mp4_video_codec_widgets(video_codec_text)
        self._setup_mp4_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

    def _rebuild_mp4_video_codec_combobox(self):
        # Populates the video codec combobox with mp4 video codecs.
        if NvidiaHelper.is_nvenc_supported():
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST)
        else:
            self._rebuild_video_codec_combobox(GeneralSettings.VIDEO_CODEC_MP4_UI_LIST)

    def _rebuild_video_codec_combobox(self, video_codec_combobox_list):
        # Clears the video codec combobox and repopulates it's entries.
        self.is_video_codec_transitioning = True
        UIHelper.rebuild_combobox(self.video_codec_combobox, video_codec_combobox_list)
        self.is_video_codec_transitioning = False

    def _rebuild_mp4_audio_codec_combobox(self):
        # Populates the audio codec combobox with mp4 relates codecs.
        self._rebuild_audio_codec_combobox(GeneralSettings.AUDIO_CODEC_MP4_UI_LIST)

    def _rebuild_audio_codec_combobox(self, audio_codec_combobox_list):
        # Clears the audio codec combobox and repopulates it's entries.
        self.is_audio_codec_transitioning = True
        UIHelper.rebuild_combobox(self.audio_codec_combobox, audio_codec_combobox_list)
        self.is_audio_codec_transitioning = False

    def _setup_mp4_video_codec_widgets(self, video_codec_text):
        if NvidiaHelper.is_nvenc_supported():
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MP4_NVENC_UI_LIST.index(video_codec_text))
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True
        else:
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MP4_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MP4_UI_LIST.index(video_codec_text))
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True

    def _setup_mp4_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_MP4_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_MP4_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)
            self.is_widgets_setting_up = True

    def set_mkv_state(self):
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self._rebuild_mkv_video_codec_combobox()
        self._rebuild_mkv_audio_codec_combobox()
        if self.is_widgets_setting_up:
            return
        self.is_widgets_setting_up = True
        self._setup_mkv_video_codec_widgets(video_codec_text)
        self._setup_mkv_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

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
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True
        else:
            if video_codec_text in GeneralSettings.VIDEO_CODEC_MKV_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_MKV_UI_LIST.index(video_codec_text))
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True

    def _setup_mkv_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_MKV_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_MKV_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)
            self.is_widgets_setting_up = True

    def set_ts_state(self):
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self._rebuild_ts_video_codec_combobox()
        self._rebuild_ts_audio_codec_combobox()
        if self.is_widgets_setting_up:
            return
        self.is_widgets_setting_up = True
        self._setup_ts_video_codec_widgets(video_codec_text)
        self._setup_ts_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

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
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True
        else:

            if video_codec_text in GeneralSettings.VIDEO_CODEC_TS_UI_LIST:
                self.video_codec_combobox.set_active(
                    GeneralSettings.VIDEO_CODEC_TS_UI_LIST.index(video_codec_text))
            else:
                self.is_widgets_setting_up = False
                self.video_codec_combobox.set_active(0)
                self.on_video_codec_combobox_changed(self.video_codec_combobox)
                self.is_widgets_setting_up = True

    def _setup_ts_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_TS_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_TS_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)
            self.is_widgets_setting_up = True

    def set_webm_state(self):
        video_codec_text = self.get_video_codec_value()
        audio_codec_text = self.get_audio_codec_value()
        self.streaming_checkbox.set_sensitive(False)
        self.streaming_checkbox.set_active(False)
        self._rebuild_webm_video_codec_combobox()
        self._rebuild_webm_audio_codec_combobox()
        if self.is_widgets_setting_up:
            return
        self.is_widgets_setting_up = True
        self._setup_webm_video_codec_widgets(video_codec_text)
        self._setup_webm_audio_codec_widgets(audio_codec_text)
        self.is_widgets_setting_up = False

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
            self.video_codec_combobox.set_active(0)
            self.on_video_codec_combobox_changed(self.video_codec_combobox)
            self.is_widgets_setting_up = True

    def _setup_webm_audio_codec_widgets(self, audio_codec_text):
        if audio_codec_text in GeneralSettings.AUDIO_CODEC_WEBM_UI_LIST:
            self.audio_codec_combobox.set_active(
                GeneralSettings.AUDIO_CODEC_WEBM_UI_LIST.index(audio_codec_text))
        else:
            self.is_widgets_setting_up = False
            self.audio_codec_combobox.set_active(0)
            self.on_audio_codec_combobox_changed(self.audio_codec_combobox)
            self.is_widgets_setting_up = True

    def set_framerate_state(self, enabled):
        if not enabled:
            self.fps_combobox.set_active(0)
        self.fps_box.set_sensitive(enabled)

    def set_framerate_locked_state(self, is_locked):
        self.framerate_auto_button.set_sensitive(not is_locked)
        self.framerate_custom_button.set_sensitive(not is_locked)

    def update_video_settings(self):
        video_codec_text = self.get_video_codec_value()
        if video_codec_text == "H264":
            video_settings = X264()

            self.video_stack.set_visible_child(self.x264_box)
            self._reset_settings_for_x265_handlers()
            self._reset_settings_for_nvenc_handlers()
            self._reset_settings_for_vp9_handlers()
        elif video_codec_text == "H265":
            video_settings = X265()

            self.video_stack.set_visible_child(self.x265_box)
            self._reset_settings_for_x264_handlers()
            self._reset_settings_for_nvenc_handlers()
            self._reset_settings_for_vp9_handlers()
        elif 'NVENC' in video_codec_text:
            if not self.is_widgets_setting_up:
                if video_codec_text == 'NVENC H264':
                    video_settings = H264Nvenc()

                    self.nvenc_handlers.set_h264_state()
                else:
                    video_settings = HevcNvenc()

                    self.nvenc_handlers.set_hevc_state()
                self._reset_settings_for_nvenc_handlers()
            else:
                video_settings = None
            self.video_stack.set_visible_child(self.nvenc_box)
            self._reset_settings_for_x264_handlers()
            self._reset_settings_for_x265_handlers()
            self._reset_settings_for_vp9_handlers()
        elif video_codec_text == 'VP9':
            video_settings = VP9()

            self.video_stack.set_visible_child(self.vp9_box)
            self._reset_settings_for_x264_handlers()
            self._reset_settings_for_x265_handlers()
            self._reset_settings_for_nvenc_handlers()
        else:
            video_settings = None

            self.video_stack.set_visible_child(self.video_noavail_label)
            self._reset_settings_for_x264_handlers()
            self._reset_settings_for_x265_handlers()
            self._reset_settings_for_nvenc_handlers()
            self._reset_settings_for_vp9_handlers()
        return video_settings

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

            self.audio_stack.set_visible_child(self.aac_box)
            self._reset_settings_for_opus_handlers()
        elif audio_text == 'opus':
            audio_settings = Opus()

            self.audio_stack.set_visible_child(self.opus_box)
            self._reset_settings_for_aac_handlers()
        else:
            audio_settings = None

            self.audio_stack.set_visible_child(self.audio_noavail_label)
            self._reset_settings_for_aac_handlers()
            self._reset_settings_for_opus_handlers()
        return audio_settings

    def _reset_settings_for_aac_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.aac_handlers.reset_settings,)).start()

    def _reset_settings_for_opus_handlers(self):
        threading.Thread(target=GLib.idle_add, args=(self.opus_handlers.reset_settings,)).start()

    def stop_benchmark_thread(self):
        with self.benchmark_thread_lock:
            if self.benchmark_thread is not None and self.benchmark_thread.is_alive():
                self.benchmark_thread_stopping = True
        if self.benchmark_thread_stopping:
            self.benchmark_thread.join()
            self.benchmark_thread_stopping = False

    def signal_framerate_auto_radiobutton(self):
        self.framerate_auto_button.set_active(True)
