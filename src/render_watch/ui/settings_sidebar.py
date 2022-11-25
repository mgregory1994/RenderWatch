# Copyright 2022 Michael Gregory
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


import copy
import os.path
import queue
import threading
import time

from collections import OrderedDict

from render_watch.ui import Gtk, GLib, Adw
from render_watch.ffmpeg import task, media_file, filter, stream, video_codec, audio_codec
from render_watch.helpers import ffmpeg_helper
from render_watch import app_preferences


class SettingsSidebarWidgets:
    SIDEBAR_WIDTH = 450

    def __init__(self, inputs_page, app_settings: app_preferences.Settings):
        self.inputs_page = inputs_page
        self.app_settings = app_settings
        self.main_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.is_widgets_setting_up = False

        self._setup_settings_sidebar_widgets()

    def _setup_settings_sidebar_widgets(self):
        self._setup_settings_pages()
        self._setup_settings_view_switcher()
        self._setup_preview_buttons()

        self.main_widget.append(self.settings_view_switcher)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.settings_page_stack)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.preview_buttons_horizontal_box)
        self.main_widget.set_size_request(self.SIDEBAR_WIDTH, -1)
        self.main_widget.set_hexpand(False)

    def _setup_settings_pages(self):
        self._setup_general_settings_page()
        self._setup_video_codec_settings_page()
        self._setup_audio_codec_settings_page()
        self._setup_filter_settings_page()
        self._setup_subtitle_settings_page()

    def _setup_general_settings_page(self):
        self.general_settings_page = self.GeneralSettingsPage(self.inputs_page)
        self.general_settings_page.extension_combo_row.connect('notify::selected-item',
                                                               self.on_general_page_extension_combo_row_selected_item)

    def _setup_video_codec_settings_page(self):
        self.video_codec_settings_page = self.VideoCodecSettingsPage(self.inputs_page)
        self.video_codec_settings_page.video_codec_row.connect(
            'notify::selected-item',
            self.on_video_codec_settings_page_video_codec_combo_row_selected_item
        )

    def _setup_audio_codec_settings_page(self):
        self.audio_codec_settings_page = self.AudioCodecSettingsPage(self.inputs_page)

    def _setup_filter_settings_page(self):
        self.filter_settings_page = self.FilterSettingsPage(self.inputs_page)

    def _setup_subtitle_settings_page(self):
        self.subtitle_settings_page = self.SubtitleSettingsPage(self.inputs_page)

    def _setup_settings_view_switcher(self):
        self._setup_settings_page_stack()

        self.settings_view_switcher = Adw.ViewSwitcher()
        self.settings_view_switcher.set_policy(Adw.ViewSwitcherPolicy.NARROW)
        self.settings_view_switcher.set_stack(self.settings_page_stack)

    def _setup_settings_page_stack(self):
        self.settings_page_stack = Adw.ViewStack()
        self.settings_page_stack.add_titled(self.general_settings_page, 'general_settings_page', 'General')
        self.settings_page_stack.add_titled(self.video_codec_settings_page, 'video_codec_settings_page', 'Video Codec')
        self.settings_page_stack.add_titled(self.audio_codec_settings_page, 'audio_codec_settings_page', 'Audio Codec')
        self.settings_page_stack.add_titled(self.filter_settings_page, 'filter_settings_page', 'Filters')
        self.settings_page_stack.add_titled(self.subtitle_settings_page, 'subtitle_settings_page', 'Subtitles')
        self.settings_page_stack.get_page(self.general_settings_page).set_icon_name('preferences-system-symbolic')
        self.settings_page_stack.get_page(self.video_codec_settings_page).set_icon_name('video-x-generic-symbolic')
        self.settings_page_stack.get_page(self.audio_codec_settings_page).set_icon_name('audio-x-generic-symbolic')
        self.settings_page_stack.get_page(self.filter_settings_page).set_icon_name('insert-image-symbolic')
        self.settings_page_stack.get_page(self.subtitle_settings_page).set_icon_name('insert-text-symbolic')

    def _setup_preview_buttons(self):
        self.settings_preview_button = Gtk.Button.new_from_icon_name('video-display-symbolic')
        self.crop_preview_button = Gtk.Button.new_from_icon_name('zoom-fit-best-symbolic')
        self.trim_preview_button = Gtk.Button.new_from_icon_name('edit-cut-symbolic')
        self.benchmark_button = Gtk.Button.new_from_icon_name('system-run-symbolic')

        self.preview_buttons_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.preview_buttons_horizontal_box.append(self.settings_preview_button)
        self.preview_buttons_horizontal_box.append(self.crop_preview_button)
        self.preview_buttons_horizontal_box.append(self.trim_preview_button)
        self.preview_buttons_horizontal_box.append(self.benchmark_button)
        self.preview_buttons_horizontal_box.set_hexpand(False)
        self.preview_buttons_horizontal_box.set_halign(Gtk.Align.CENTER)
        self.preview_buttons_horizontal_box.set_margin_top(10)
        self.preview_buttons_horizontal_box.set_margin_bottom(10)

    def set_widgets_setting_up(self, is_widgets_setting_up: bool):
        self.is_widgets_setting_up = is_widgets_setting_up

    def apply_settings_to_widgets(self, encode_task: task.Encode):
        GLib.idle_add(self.set_widgets_setting_up, True)
        self.general_settings_page.apply_settings_to_widgets(encode_task)
        self.video_codec_settings_page.apply_settings_to_widgets(encode_task)
        self.audio_codec_settings_page.apply_settings_to_widgets(encode_task)
        self.filter_settings_page.apply_settings_to_widgets(encode_task)
        self.subtitle_settings_page.apply_settings_to_widgets(encode_task)
        GLib.idle_add(self.set_widgets_setting_up, False)

    def on_general_page_extension_combo_row_selected_item(self, combo_row, parameter):
        if self.is_widgets_setting_up:
            return

        self.general_settings_page.on_extension_combo_row_selected_item()

        self.video_codec_settings_page.update_video_codec_settings_from_extension(self.general_settings_page)
        self.audio_codec_settings_page.update_audio_streams_from_extension(self.general_settings_page)

    def on_video_codec_settings_page_video_codec_combo_row_selected_item(self, combo_row, parameter):
        if self.is_widgets_setting_up:
            return

        self.video_codec_settings_page.on_widget_changed_clicked_set(combo_row)

        if combo_row.get_selected() == 0:
            self.general_settings_page.set_custom_frame_rate_unavailable_state()
            self.filter_settings_page.set_filters_not_available_state()
            self.subtitle_settings_page.set_video_copy_state()
        else:
            self.general_settings_page.set_custom_frame_rate_available_state()
            self.filter_settings_page.set_filters_available_state()

    class SettingsGroup(Adw.PreferencesGroup):
        def __init__(self):
            super().__init__()

            self.children = []
            self.number_of_children = 0

        def add(self, preferences_row: Adw.PreferencesRow):
            super().add(preferences_row)

            if preferences_row not in self.children:
                self.children.append(preferences_row)
                self.number_of_children += 1

        def remove(self, preferences_row: Adw.PreferencesRow):
            if preferences_row in self.children:
                super().remove(preferences_row)
                self.children.remove(preferences_row)
                self.number_of_children -= 1

                self.update_children()

        def remove_children(self):
            for child in self.children:
                super().remove(child)

            self.children = []
            self.number_of_children = 0

        def update_children(self):
            for index, child in enumerate(self.children):
                child.row_count = index + 1
                child.update_title()

    class GeneralSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page
            self.is_widgets_setting_up = False

            self._setup_preset_settings()
            self._setup_output_file_settings()
            self._setup_frame_rate_settings()

            general_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            general_settings_vertical_box.append(self.preset_settings_group)
            general_settings_vertical_box.append(self.output_settings_group)
            general_settings_vertical_box.append(self.frame_rate_settings_group)
            general_settings_vertical_box.set_margin_top(20)
            general_settings_vertical_box.set_margin_bottom(20)
            general_settings_vertical_box.set_margin_start(20)
            general_settings_vertical_box.set_margin_end(20)

            self.set_child(general_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_preset_settings(self):
            self.preset_settings_group = Adw.PreferencesGroup()
            self.preset_settings_group.set_title('Preset')

        def _setup_output_file_settings(self):
            self._setup_extension_row()
            self._setup_fast_start_row()

            self.output_settings_group = Adw.PreferencesGroup()
            self.output_settings_group.set_title('Output File')
            self.output_settings_group.add(self.extension_combo_row)
            self.output_settings_group.add(self.fast_start_row)

        def _setup_extension_row(self):
            self._setup_extension_string_list()

            self.extension_combo_row = Adw.ComboRow()
            self.extension_combo_row.set_title('Extension')
            self.extension_combo_row.set_subtitle('Output file extension type')
            self.extension_combo_row.set_model(self.extension_string_list)

        def _setup_extension_string_list(self):
            self.extension_string_list = Gtk.StringList.new(media_file.OUTPUT_EXTENSIONS)

        def _setup_fast_start_row(self):
            self._setup_fast_start_switch()

            self.fast_start_row = Adw.ActionRow()
            self.fast_start_row.set_title('Fast Start')
            self.fast_start_row.set_subtitle('Move MOV atom to the beginning of the file')
            self.fast_start_row.add_suffix(self.fast_start_switch)

        def _setup_fast_start_switch(self):
            self.fast_start_switch = Gtk.Switch()
            self.fast_start_switch.set_vexpand(False)
            self.fast_start_switch.set_valign(Gtk.Align.CENTER)
            self.fast_start_switch.connect('state-set', self.on_widget_changed_clicked_set)

        def _setup_frame_rate_settings(self):
            self._setup_custom_frame_rate_row()

            self.custom_frame_rate_switch = Gtk.Switch()
            self.custom_frame_rate_switch.set_vexpand(False)
            self.custom_frame_rate_switch.set_valign(Gtk.Align.CENTER)
            self.custom_frame_rate_switch.connect('state-set', self.on_custom_frame_rate_switch_state_set)

            self.frame_rate_settings_group = Adw.PreferencesGroup()
            self.frame_rate_settings_group.set_title('Frame Rate')
            self.frame_rate_settings_group.set_header_suffix(self.custom_frame_rate_switch)
            self.frame_rate_settings_group.add(self.custom_frame_rate_row)

        def _setup_custom_frame_rate_row(self):
            self._setup_custom_frame_rate_string_list()

            self.custom_frame_rate_row = Adw.ComboRow()
            self.custom_frame_rate_row.set_title('Frames Per Second')
            self.custom_frame_rate_row.set_subtitle('Output\'s frame rate')
            self.custom_frame_rate_row.set_model(self.custom_frame_rate_string_list)
            self.custom_frame_rate_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
            self.custom_frame_rate_row.set_sensitive(False)

        def _setup_custom_frame_rate_string_list(self):
            self.custom_frame_rate_string_list = Gtk.StringList.new(task.GeneralSettings.FRAME_RATE)

        def update_fast_start_available_state(self):
            if self.get_selected_extension() in media_file.VALID_FAST_START_EXTENSION:
                self.fast_start_row.set_sensitive(True)
            else:
                self.fast_start_switch.set_active(False)
                self.fast_start_row.set_sensitive(False)

        def get_selected_extension(self) -> str:
            return self.extension_combo_row.get_selected_item().get_string()

        def is_video_extension(self) -> bool:
            return self.get_selected_extension() in media_file.VIDEO_OUTPUT_EXTENSIONS

        def is_audio_extension(self) -> bool:
            return self.get_selected_extension() in media_file.AUDIO_OUTPUT_EXTENSIONS

        def set_audio_state(self):
            self.update_fast_start_available_state()
            self.set_custom_frame_rate_unavailable_state()

        def set_custom_frame_rate_unavailable_state(self):
            self.frame_rate_settings_group.set_sensitive(False)
            self.custom_frame_rate_switch.set_active(False)

            custom_frame_rate_string_list = Gtk.StringList.new(['N/A'])
            self.custom_frame_rate_row.set_model(custom_frame_rate_string_list)

        def set_custom_frame_rate_available_state(self):
            self.frame_rate_settings_group.set_sensitive(True)

            custom_frame_rate_string_list = Gtk.StringList.new(task.GeneralSettings.FRAME_RATE)
            self.custom_frame_rate_row.set_model(custom_frame_rate_string_list)
            self.custom_frame_rate_row.set_sensitive(self.custom_frame_rate_switch.get_active())

        def set_audio_extensions(self, selected_extension=None):
            audio_extensions_string_list = Gtk.StringList.new(media_file.AUDIO_OUTPUT_EXTENSIONS)
            self.extension_combo_row.set_model(audio_extensions_string_list)

            if selected_extension:
                extension_index = media_file.AUDIO_OUTPUT_EXTENSIONS.index(selected_extension)
                self.extension_combo_row.set_selected(extension_index)

        def set_video_extensions(self, selected_extension=None):
            video_extensions_string_list = Gtk.StringList.new(media_file.VIDEO_OUTPUT_EXTENSIONS)
            self.extension_combo_row.set_model(video_extensions_string_list)

            if selected_extension:
                extension_index = media_file.VIDEO_OUTPUT_EXTENSIONS.index(selected_extension)
                self.extension_combo_row.set_selected(extension_index)

        def set_all_extensions(self, selected_extension=None):
            all_extensions_string_list = Gtk.StringList.new(media_file.OUTPUT_EXTENSIONS)
            self.extension_combo_row.set_model(all_extensions_string_list)

            if selected_extension:
                extension_index = media_file.OUTPUT_EXTENSIONS.index(selected_extension)
                self.extension_combo_row.set_selected(extension_index)

        def set_video_state(self):
            self.update_fast_start_available_state()
            self.set_custom_frame_rate_available_state()

        def set_widgets_setting_up(self, is_widgets_setting_up: bool):
            self.is_widgets_setting_up = is_widgets_setting_up

        def apply_settings_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.set_widgets_setting_up, True)

            if encode_task.input_file.is_video:
                self._apply_fast_start_setting_to_widgets(encode_task)
                self._apply_frame_rate_setting_to_widgets(encode_task)

            GLib.idle_add(self._apply_extension_setting_to_widgets, encode_task)
            GLib.idle_add(self.set_widgets_setting_up, False)

        def _apply_extension_setting_to_widgets(self, encode_task: task.Encode):
            if encode_task.input_file.is_folder or (encode_task.input_file.is_video and encode_task.input_file.is_audio):
                self.set_all_extensions(encode_task.output_file.extension)
                self.set_video_state()
            elif encode_task.input_file.is_video:
                self.set_video_extensions(encode_task.output_file.extension)
                self.set_video_state()
            else:
                self.set_audio_extensions(encode_task.output_file.extension)
                self.set_audio_state()

        def _apply_fast_start_setting_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.fast_start_switch.set_active, encode_task.general_settings.fast_start)

        def _apply_frame_rate_setting_to_widgets(self, encode_task: task.Encode):
            frame_rate_index = encode_task.general_settings.frame_rate

            if frame_rate_index is not None:
                GLib.idle_add(self.custom_frame_rate_switch.set_active, True)
                GLib.idle_add(self.custom_frame_rate_row.set_selected, frame_rate_index)
            else:
                GLib.idle_add(self.custom_frame_rate_switch.set_active, False)
                GLib.idle_add(self.custom_frame_rate_row.set_selected, 0)

            GLib.idle_add(self.on_custom_frame_rate_switch_state_set, self.custom_frame_rate_switch, None)

        def apply_settings_from_widgets(self):
            task_general_settings = task.GeneralSettings()

            if self.custom_frame_rate_switch.get_active():
                task_general_settings.frame_rate = self.custom_frame_rate_row.get_selected()

            if self.fast_start_row.get_sensitive():
                task_general_settings.fast_start = self.fast_start_switch.get_active()

            for input_row in self.inputs_page.get_selected_rows():
                encode_task = input_row.encode_task
                encode_task.output_file.extension = media_file.OUTPUT_EXTENSIONS[self.extension_combo_row.get_selected()]
                encode_task.general_settings = copy.deepcopy(task_general_settings)
                print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

            self.inputs_page.update_preview_page_encode_task()

        def on_widget_changed_clicked_set(self, *args, **kwargs):
            if self.is_widgets_setting_up:
                return

            threading.Thread(target=self.apply_settings_from_widgets, args=()).start()

        def on_extension_combo_row_selected_item(self):
            if self.is_widgets_setting_up:
                self.update_fast_start_available_state()

                return

            GLib.idle_add(self.set_widgets_setting_up, True)
            GLib.idle_add(self.update_fast_start_available_state)

            if self.is_video_extension():
                GLib.idle_add(self.set_video_state)
            else:
                GLib.idle_add(self.set_audio_state)

            GLib.idle_add(self.set_widgets_setting_up, False)

            self.on_widget_changed_clicked_set()

        def on_custom_frame_rate_switch_state_set(self, switch, user_data):
            self.custom_frame_rate_row.set_sensitive(switch.get_active())

            if self.is_widgets_setting_up:
                return

            self.on_widget_changed_clicked_set()

    class VideoCodecSettingsPage(Gtk.ScrolledWindow):

        X264_PAGE = 'x264'
        X265_page = 'x265'
        NVENC_PAGE = 'nvenc'
        VP9_PAGE = 'vp9'
        UNAVAILABLE_PAGE = 'unavailable'

        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page
            self.is_widgets_setting_up = False

            self._setup_video_stream_settings()
            self._setup_video_codec_settings_pages()

            video_codec_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            video_codec_settings_vertical_box.append(self.video_stream_settings_group)
            video_codec_settings_vertical_box.append(self.video_codec_settings_stack)
            video_codec_settings_vertical_box.set_margin_top(20)
            video_codec_settings_vertical_box.set_margin_bottom(20)
            video_codec_settings_vertical_box.set_margin_start(20)
            video_codec_settings_vertical_box.set_margin_end(20)

            self.set_child(video_codec_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_video_stream_settings(self):
            self._setup_video_stream_row()
            self._setup_video_codec_row()

            self.video_stream_settings_group = Adw.PreferencesGroup()
            self.video_stream_settings_group.set_title('Video Stream')
            self.video_stream_settings_group.add(self.video_stream_row)
            self.video_stream_settings_group.add(self.video_codec_row)

        def _setup_video_stream_row(self):
            self.video_stream_row = Adw.ComboRow()
            self.video_stream_row.set_title('Selected Stream')
            self.video_stream_row.set_use_subtitle(True)
            self.video_stream_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

        def _setup_video_codec_row(self):
            self.video_codec_row = Adw.ComboRow()
            self.video_codec_row.set_title('Video Codec')
            self.video_codec_row.set_subtitle('Codec to encode the video stream')

        def _setup_video_codec_settings_pages(self):
            self.x264_page = self.X264StackPage(self.inputs_page)
            self.x265_page = self.X265StackPage(self.inputs_page)
            self.vp9_page = self.Vp9StackPage(self.inputs_page)
            self.nvenc_page = self.NvencStackPage(self.inputs_page)
            codec_settings_no_avail_page = self.CodecSettingsNoAvailPage()

            self.video_codec_settings_stack = Gtk.Stack()
            self.video_codec_settings_stack.add_named(self.x264_page, self.X264_PAGE)
            self.video_codec_settings_stack.add_named(self.x265_page, self.X265_page)
            self.video_codec_settings_stack.add_named(self.vp9_page, self.VP9_PAGE)
            self.video_codec_settings_stack.add_named(self.nvenc_page, self.NVENC_PAGE)
            self.video_codec_settings_stack.add_named(codec_settings_no_avail_page, self.UNAVAILABLE_PAGE)
            self.video_codec_settings_stack.set_visible_child_name(self.UNAVAILABLE_PAGE)
            self.video_codec_settings_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
            self.video_codec_settings_stack.set_vhomogeneous(False)

        def update_video_codec_settings_from_extension(self, general_settings_page):
            selected_video_codec = self.video_codec_row.get_selected_item().get_string()
            video_codecs_list = self._get_codecs_list_from_extension(general_settings_page.get_selected_extension())

            self.is_widgets_setting_up = True
            self._repopulate_video_codec_row(video_codecs_list)

            if general_settings_page.is_video_extension() and selected_video_codec in video_codecs_list:
                self.video_codec_row.set_selected(video_codecs_list.index(selected_video_codec))
            elif general_settings_page.is_video_extension():
                self.video_codec_row.set_selected(1)
            else:
                self.video_codec_row.set_selected(0)

            self.is_widgets_setting_up = False

            self.on_widget_changed_clicked_set()

        @staticmethod
        def _get_codecs_list_from_extension(extension: str) -> list[str]:
            if extension == media_file.MP4_EXTENTION:
                video_codecs_list = video_codec.VIDEO_CODECS_MP4_UI
            elif extension == media_file.MKV_EXTENSION:
                video_codecs_list = video_codec.VIDEO_CODECS_MKV_UI
            elif extension == media_file.TS_EXTENSION:
                video_codecs_list = video_codec.VIDEO_CODECS_TS_UI
            elif extension == media_file.WEBM_EXTENSION:
                video_codecs_list = video_codec.VIDEO_CODECS_WEBM_UI
            else:
                video_codecs_list = ['N/A']

            return video_codecs_list

        def set_not_available_state(self):
            self._set_video_streams_not_available_state()
            self._set_video_codec_not_available_state()
            self.video_codec_settings_stack.set_visible_child_name(self.UNAVAILABLE_PAGE)

        def _set_video_streams_not_available_state(self):
            video_stream_string_list = Gtk.StringList.new(['N/A'])
            self.video_stream_row.set_model(video_stream_string_list)
            self.video_stream_row.set_sensitive(False)

        def _set_video_codec_not_available_state(self):
            video_codec_string_list = Gtk.StringList.new(['N/A'])
            self.video_codec_row.set_model(video_codec_string_list)
            self.video_codec_row.set_sensitive(False)

        def set_available_state(self):
            self.video_stream_row.set_sensitive(True)
            self.video_codec_row.set_sensitive(True)

        def set_widgets_setting_up(self, is_widgets_setting_up: bool):
            self.is_widgets_setting_up = is_widgets_setting_up

        def apply_settings_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.set_widgets_setting_up, True)

            if self._is_encode_task_valid(encode_task):
                GLib.idle_add(self.set_available_state)
                self._apply_video_stream_setting_to_widgets(encode_task)
                self._apply_video_codec_settings_to_widgets(encode_task)
            else:
                GLib.idle_add(self.set_not_available_state)

            GLib.idle_add(self.set_widgets_setting_up, False)

        @staticmethod
        def _is_encode_task_valid(encode_task: task.Encode) -> bool:
            return encode_task.input_file.is_video or encode_task.input_file.is_folder

        def _apply_video_stream_setting_to_widgets(self, encode_task: task.Encode):
            video_stream_string_list = Gtk.StringList.new()

            for video_stream in encode_task.input_file.video_streams:
                video_stream_string_list.append(video_stream.get_info())

            GLib.idle_add(self.video_stream_row.set_model, video_stream_string_list)

            video_stream_index = encode_task.input_file.video_streams.index(encode_task.get_video_stream())
            GLib.idle_add(self.video_stream_row.set_selected, video_stream_index)

        def _apply_video_codec_settings_to_widgets(self, encode_task: task.Encode):
            video_codecs_list = self._get_codecs_list_from_extension(encode_task.output_file.extension)
            GLib.idle_add(self._repopulate_video_codec_row, video_codecs_list)
            self._set_video_codec_row(encode_task, video_codecs_list)

        def _repopulate_video_codec_row(self, video_codecs_list: list[str]):
            video_codecs_string_list = Gtk.StringList.new(video_codecs_list)
            self.video_codec_row.set_model(video_codecs_string_list)

        def _set_video_codec_row(self, encode_task: task.Encode, video_codecs_list: list):
            if video_codec.is_codec_x264(encode_task.get_video_codec()):
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('H264'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.X264_PAGE)
                self.x264_page.apply_settings_to_widgets(encode_task)
            elif video_codec.is_codec_x265(encode_task.get_video_codec()):
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('H265'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.X265_page)
                self.x265_page.apply_settings_to_widgets(encode_task)
            elif video_codec.is_codec_h264_nvenc(encode_task.get_video_codec()):
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('NVENC H264'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.NVENC_PAGE)
                self.nvenc_page.apply_settings_to_widgets(encode_task)
            elif video_codec.is_codec_hevc_nvenc(encode_task.get_video_codec()):
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('NVENC H265'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.NVENC_PAGE)
                self.nvenc_page.apply_settings_to_widgets(encode_task)
            elif video_codec.is_codec_vp9(encode_task.get_video_codec()):
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('VP9'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.VP9_PAGE)
                self.vp9_page.apply_settings_to_widgets(encode_task)
            else:
                GLib.idle_add(self.video_codec_row.set_selected, video_codecs_list.index('copy'))
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.UNAVAILABLE_PAGE)

        def apply_settings_from_widgets(self):
            input_row = self.inputs_page.get_selected_rows()[-1]
            encode_task = input_row.encode_task

            if not encode_task.input_file.is_video:
                return

            self._apply_video_stream_setting_from_widgets(encode_task)
            self._apply_video_codec_settings_from_widgets(encode_task)
            print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

            self.inputs_page.update_preview_page_encode_task()

        def _apply_video_stream_setting_from_widgets(self, encode_task: task.Encode):
            selected_video_stream = encode_task.input_file.video_streams[self.video_stream_row.get_selected()]
            encode_task.set_video_stream(selected_video_stream)

        def _apply_video_codec_settings_from_widgets(self, encode_task: task.Encode):
            if self.video_codec_row.get_selected_item().get_string() == 'H264':
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.X264_PAGE)

                if not video_codec.is_codec_x264(encode_task.get_video_codec()):
                    encode_task.set_video_codec(video_codec.X264())
                    self.x264_page.apply_settings_to_widgets(encode_task)
            elif self.video_codec_row.get_selected_item().get_string() == 'H265':
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.X265_page)

                if not video_codec.is_codec_x265(encode_task.get_video_codec()):
                    encode_task.set_video_codec(video_codec.X265())
                    self.x265_page.apply_settings_to_widgets(encode_task)
            elif self.video_codec_row.get_selected_item().get_string() == 'NVENC H264':
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.NVENC_PAGE)

                if not video_codec.is_codec_h264_nvenc(encode_task.get_video_codec()):
                    encode_task.set_video_codec(video_codec.H264Nvenc())
                    self.nvenc_page.apply_settings_to_widgets(encode_task)
            elif self.video_codec_row.get_selected_item().get_string() == 'NVENC H265':
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.NVENC_PAGE)

                if video_codec.is_codec_hevc_nvenc(encode_task.get_video_codec()):
                    encode_task.set_video_codec(video_codec.HevcNvenc())
                    self.nvenc_page.apply_settings_to_widgets(encode_task)
            elif self.video_codec_row.get_selected_item().get_string() == 'VP9':
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.VP9_PAGE)

                if not video_codec.is_codec_vp9(encode_task.get_video_codec()):
                    encode_task.set_video_codec(video_codec.VP9())
                    self.vp9_page.apply_settings_to_widgets(encode_task)
            else:
                GLib.idle_add(self.video_codec_settings_stack.set_visible_child_name, self.UNAVAILABLE_PAGE)
                encode_task.video_codec = None

        def on_widget_changed_clicked_set(self, *args, **kwargs):
            if self.is_widgets_setting_up:
                return

            threading.Thread(target=self.apply_settings_from_widgets, args=()).start()

        class X264StackPage(Gtk.Box):
            def __init__(self, inputs_page):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self.inputs_page = inputs_page
                self.is_widgets_setting_up = False
                self._crf_scale_callback_queue = queue.Queue()

                self._setup_codec_settings()
                self._setup_codec_advanced_settings()

                self.append(self.codec_settings_group)
                self.append(self.advanced_codec_settings_group)

            def _setup_codec_settings(self):
                self._setup_preset_row()
                self._setup_profile_row()
                self._setup_level_row()
                self._setup_tune_row()
                self._setup_rate_type_row()
                self._setup_rate_type_settings_row()

                self.codec_settings_group = Adw.PreferencesGroup()
                self.codec_settings_group.set_title('X264 Settings')
                self.codec_settings_group.add(self.preset_row)
                self.codec_settings_group.add(self.profile_row)
                self.codec_settings_group.add(self.level_row)
                self.codec_settings_group.add(self.tune_row)
                self.codec_settings_group.add(self.rate_type_row)
                self.codec_settings_group.add(self.rate_type_settings_row)

            def _setup_preset_row(self):
                self.preset_string_list = Gtk.StringList.new(video_codec.X264.PRESET)

                self.preset_row = Adw.ComboRow()
                self.preset_row.set_title('Preset')
                self.preset_row.set_subtitle('Encoding preset')
                self.preset_row.set_model(self.preset_string_list)
                self.preset_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_profile_row(self):
                self.profile_string_list = Gtk.StringList.new(video_codec.X264.PROFILE)

                self.profile_row = Adw.ComboRow()
                self.profile_row.set_title('Profile')
                self.profile_row.set_subtitle('Profile restrictions')
                self.profile_row.set_model(self.profile_string_list)
                self.profile_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_level_row(self):
                self.level_string_list = Gtk.StringList.new(video_codec.X264.LEVEL)

                self.level_row = Adw.ComboRow()
                self.level_row.set_title('Level')
                self.level_row.set_subtitle('Specified level')
                self.level_row.set_model(self.level_string_list)
                self.level_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_tune_row(self):
                self.tune_string_list = Gtk.StringList.new(video_codec.X264.TUNE)

                self.tune_row = Adw.ComboRow()
                self.tune_row.set_title('Tune')
                self.tune_row.set_subtitle('Tune encoder parameters')
                self.tune_row.set_model(self.tune_string_list)
                self.tune_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_rate_type_row(self):
                self._setup_rate_type_radio_buttons()

                self.rate_type_row = Adw.ActionRow()
                self.rate_type_row.set_title('Rate Type')
                self.rate_type_row.set_subtitle('Codec rate type method')
                self.rate_type_row.add_suffix(self.rate_type_horizontal_box)

            def _setup_rate_type_radio_buttons(self):
                self.crf_check_button = Gtk.CheckButton(label='CRF')
                self.crf_check_button.set_active(True)
                self.crf_check_button.connect('toggled', self.on_crf_check_button_toggled)

                self.qp_check_button = Gtk.CheckButton(label='QP')
                self.qp_check_button.set_group(self.crf_check_button)
                self.qp_check_button.connect('toggled', self.on_qp_check_button_toggled)

                self.bitrate_check_button = Gtk.CheckButton(label='Bitrate')
                self.bitrate_check_button.set_group(self.crf_check_button)
                self.bitrate_check_button.connect('toggled', self.on_bitrate_check_button_toggled)

                self.rate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.rate_type_horizontal_box.append(self.crf_check_button)
                self.rate_type_horizontal_box.append(self.qp_check_button)
                self.rate_type_horizontal_box.append(self.bitrate_check_button)

            def _setup_rate_type_settings_row(self):
                self._setup_rate_type_settings_stack()

                self.rate_type_settings_row = Adw.ActionRow()
                self.rate_type_settings_row.set_title('CRF')
                self.rate_type_settings_row.set_subtitle('Constant Ratefactor')
                self.rate_type_settings_row.add_suffix(self.rate_type_stack)

            def _setup_rate_type_settings_stack(self):
                self._setup_crf_page()
                self._setup_qp_page()
                self._setup_bitrate_page()

                self.rate_type_stack = Gtk.Stack()
                self.rate_type_stack.add_named(self.crf_scale, 'crf_page')
                self.rate_type_stack.add_named(self.qp_scale, 'qp_page')
                self.rate_type_stack.add_named(self.bitrate_page_vertical_box, 'bitrate_page')
                self.rate_type_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

            def _setup_crf_page(self):
                self._setup_crf_gesture_click()
                self._setup_crf_event_controller_key()
                self._setup_crf_event_controller_scroll()

                self.crf_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                          min=video_codec.X264.CRF_MIN,
                                                          max=video_codec.X264.CRF_MAX,
                                                          step=0.1)
                self.crf_scale.set_increments(step=0.1, page=1.0)
                self.crf_scale.set_value(video_codec.X264.CRF_DEFAULT)
                self.crf_scale.set_digits(1)
                self.crf_scale.set_draw_value(True)
                self.crf_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.crf_scale.set_hexpand(True)
                self.crf_scale.add_controller(self.crf_gesture_click)
                self.crf_scale.add_controller(self.crf_event_controller_key)
                self.crf_scale.add_controller(self.crf_event_controller_scroll)

            def _setup_crf_gesture_click(self):
                self.crf_gesture_click = Gtk.GestureClick.new()
                self.crf_gesture_click.connect('stopped', self.on_scale_gesture_stopped, self.crf_gesture_click)
                self.crf_gesture_click.connect('unpaired-release', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_key(self):
                self.crf_event_controller_key = Gtk.EventControllerKey.new()
                self.crf_event_controller_key.connect('key-released', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_scroll(self):
                self.crf_event_controller_scroll = Gtk.EventControllerScroll.new(
                    Gtk.EventControllerScrollFlags.BOTH_AXES
                )
                self.crf_event_controller_scroll.connect('scroll', self.on_widget_changed_clicked_set)

            def _setup_qp_page(self):
                self._setup_qp_gesture_click()
                self._setup_qp_event_controller_key()
                self._setup_qp_event_controller_scroll()

                self.qp_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                         min=video_codec.X264.QP_MIN,
                                                         max=video_codec.X264.QP_MAX,
                                                         step=1.0)
                self.qp_scale.set_value(video_codec.X264.CRF_DEFAULT)
                self.qp_scale.set_digits(1)
                self.qp_scale.set_draw_value(True)
                self.qp_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_scale.set_hexpand(True)
                self.qp_scale.add_controller(self.qp_gesture_click)
                self.qp_scale.add_controller(self.qp_event_controller_key)

            def _setup_qp_gesture_click(self):
                self.qp_gesture_click = Gtk.GestureClick.new()
                self.qp_gesture_click.connect('stopped', self.on_scale_gesture_stopped, self.qp_gesture_click)
                self.qp_gesture_click.connect('unpaired-release', self.on_widget_changed_clicked_set)

            def _setup_qp_event_controller_key(self):
                self.qp_event_controller_key = Gtk.EventControllerKey.new()
                self.qp_event_controller_key.connect('key-released', self.on_widget_changed_clicked_set)

            def _setup_qp_event_controller_scroll(self):
                self.qp_event_controller_scroll = Gtk.EventControllerScroll.new(
                    Gtk.EventControllerScrollFlags.BOTH_AXES)
                self.qp_event_controller_scroll.connect('scroll', self.on_widget_changed_clicked_set)

            def _setup_bitrate_page(self):
                self._setup_bitrate_spin_button()
                self._setup_bitrate_type_widgets()

                self.bitrate_page_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.bitrate_page_vertical_box.append(self.bitrate_spin_button)
                self.bitrate_page_vertical_box.append(self.bitrate_type_horizontal_box)
                self.bitrate_page_vertical_box.set_margin_top(10)
                self.bitrate_page_vertical_box.set_margin_bottom(10)
                self.bitrate_page_vertical_box.set_hexpand(False)
                self.bitrate_page_vertical_box.set_halign(Gtk.Align.END)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(video_codec.X264.BITRATE_MIN, video_codec.X264.BITRATE_MAX)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(100, 500)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)
                self.bitrate_spin_button.set_value(2500)
                self.bitrate_spin_button.set_size_request(125, -1)
                self.bitrate_spin_button.set_vexpand(True)
                self.bitrate_spin_button.set_valign(Gtk.Align.END)
                self.bitrate_spin_button.set_hexpand(True)
                self.bitrate_spin_button.set_halign(Gtk.Align.CENTER)
                self.bitrate_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_bitrate_type_widgets(self):
                self.average_check_button = Gtk.CheckButton(label='Average')
                self.average_check_button.set_active(True)
                self.average_check_button.connect('toggled', self.on_bitrate_type_check_button_toggled)

                self.constant_check_button = Gtk.CheckButton(label='Constant')
                self.constant_check_button.set_group(self.average_check_button)
                self.constant_check_button.connect('toggled', self.on_bitrate_type_check_button_toggled)

                self.dual_pass_check_button = Gtk.CheckButton(label='2-Pass')
                self.dual_pass_check_button.set_group(self.average_check_button)
                self.dual_pass_check_button.connect('toggled', self.on_bitrate_type_check_button_toggled)

                self.bitrate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.bitrate_type_horizontal_box.append(self.average_check_button)
                self.bitrate_type_horizontal_box.append(self.constant_check_button)
                self.bitrate_type_horizontal_box.append(self.dual_pass_check_button)
                self.bitrate_type_horizontal_box.set_vexpand(True)
                self.bitrate_type_horizontal_box.set_valign(Gtk.Align.START)

            def _setup_codec_advanced_settings(self):
                self._setup_keyint_row()
                self._setup_min_keyint_row()
                self._setup_scenecut_row()
                self._setup_b_frames_row()
                self._setup_b_adapt_row()
                self._setup_b_pyramid_row()
                self._setup_no_cabac_row()
                self._setup_ref_row()
                self._setup_deblock_row()
                self._setup_vbv_maxrate_row()
                self._setup_vbv_bufsize_row()
                self._setup_aq_mode_row()
                self._setup_aq_strength_row()
                self._setup_partitions_row()
                self._setup_direct_row()
                self._setup_weight_b_row()
                self._setup_me_row()
                self._setup_me_range_row()
                self._setup_subme_row()
                self._setup_psy_rd_row()
                self._setup_mixed_refs_row()
                self._setup_dct8x8_row()
                self._setup_trellis_row()
                self._setup_no_fast_pskip_row()
                self._setup_no_dct_decimate_row()
                self._setup_weight_p_row()

                self.advanced_settings_switch = Gtk.Switch()
                self.advanced_settings_switch.set_vexpand(False)
                self.advanced_settings_switch.set_valign(Gtk.Align.CENTER)
                self.advanced_settings_switch.connect('state-set', self.on_advanced_settings_switch_state_set)

                self.advanced_codec_settings_group = Adw.PreferencesGroup()
                self.advanced_codec_settings_group.set_title('Advanced Settings')
                self.advanced_codec_settings_group.set_header_suffix(self.advanced_settings_switch)
                self.advanced_codec_settings_group.add(self.vbv_maxrate_row)
                self.advanced_codec_settings_group.add(self.vbv_bufsize_row)
                self.advanced_codec_settings_group.add(self.keyint_row)
                self.advanced_codec_settings_group.add(self.min_keyint_row)
                self.advanced_codec_settings_group.add(self.scenecut_row)
                self.advanced_codec_settings_group.add(self.b_frames_row)
                self.advanced_codec_settings_group.add(self.b_adapt_row)
                self.advanced_codec_settings_group.add(self.b_pyramid_row)
                self.advanced_codec_settings_group.add(self.weight_b_row)
                self.advanced_codec_settings_group.add(self.weight_p_row)
                self.advanced_codec_settings_group.add(self.no_fast_pskip_row)
                self.advanced_codec_settings_group.add(self.ref_row)
                self.advanced_codec_settings_group.add(self.mixed_refs_row)
                self.advanced_codec_settings_group.add(self.no_cabac_row)
                self.advanced_codec_settings_group.add(self.deblock_row)
                self.advanced_codec_settings_group.add(self.aq_mode_row)
                self.advanced_codec_settings_group.add(self.aq_strength_row)
                self.advanced_codec_settings_group.add(self.partitions_row)
                self.advanced_codec_settings_group.add(self.dct8x8_row)
                self.advanced_codec_settings_group.add(self.direct_row)
                self.advanced_codec_settings_group.add(self.me_row)
                self.advanced_codec_settings_group.add(self.me_range_row)
                self.advanced_codec_settings_group.add(self.subme_row)
                self.advanced_codec_settings_group.add(self.psyrd_row)
                self.advanced_codec_settings_group.add(self.trellis_row)
                self.advanced_codec_settings_group.add(self.no_dct_decimate_row)

            def _setup_keyint_row(self):
                self._setup_keyint_spin_button()

                self.keyint_row = Adw.ActionRow()
                self.keyint_row.set_title('Keyint')
                self.keyint_row.set_subtitle('Maximum interval between keyframes')
                self.keyint_row.add_suffix(self.keyint_spin_button)
                self.keyint_row.set_sensitive(False)

            def _setup_keyint_spin_button(self):
                self.keyint_spin_button = Gtk.SpinButton()
                self.keyint_spin_button.set_range(video_codec.X264.KEYINT_MIN, video_codec.X264.KEYINT_MAX)
                self.keyint_spin_button.set_digits(0)
                self.keyint_spin_button.set_increments(10, 100)
                self.keyint_spin_button.set_numeric(True)
                self.keyint_spin_button.set_snap_to_ticks(True)
                self.keyint_spin_button.set_value(250)
                self.keyint_spin_button.set_vexpand(False)
                self.keyint_spin_button.set_valign(Gtk.Align.CENTER)
                self.keyint_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_min_keyint_row(self):
                self._setup_min_keyint_spin_button()

                self.min_keyint_row = Adw.ActionRow()
                self.min_keyint_row.set_title('Min Keyint')
                self.min_keyint_row.set_subtitle('Minimum interval between keyframes')
                self.min_keyint_row.add_suffix(self.min_keyint_spin_button)
                self.min_keyint_row.set_sensitive(False)

            def _setup_min_keyint_spin_button(self):
                self.min_keyint_spin_button = Gtk.SpinButton()
                self.min_keyint_spin_button.set_range(video_codec.X264.KEYINT_MIN, video_codec.X264.KEYINT_MAX)
                self.min_keyint_spin_button.set_digits(0)
                self.min_keyint_spin_button.set_increments(10, 100)
                self.min_keyint_spin_button.set_numeric(True)
                self.min_keyint_spin_button.set_snap_to_ticks(True)
                self.min_keyint_spin_button.set_value(25)
                self.min_keyint_spin_button.set_vexpand(False)
                self.min_keyint_spin_button.set_valign(Gtk.Align.CENTER)
                self.min_keyint_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_scenecut_row(self):
                self._setup_scenecut_spin_button()

                self.scenecut_row = Adw.ActionRow()
                self.scenecut_row.set_title('Scenecut')
                self.scenecut_row.set_subtitle('Threshold for keyframe placement')
                self.scenecut_row.add_suffix(self.scenecut_spin_button)
                self.scenecut_row.set_sensitive(False)

            def _setup_scenecut_spin_button(self):
                self.scenecut_spin_button = Gtk.SpinButton()
                self.scenecut_spin_button.set_range(video_codec.X264.SCENECUT_MIN, video_codec.X264.SCENECUT_MAX)
                self.scenecut_spin_button.set_digits(0)
                self.scenecut_spin_button.set_increments(10, 100)
                self.scenecut_spin_button.set_numeric(True)
                self.scenecut_spin_button.set_snap_to_ticks(True)
                self.scenecut_spin_button.set_value(40)
                self.scenecut_spin_button.set_vexpand(False)
                self.scenecut_spin_button.set_valign(Gtk.Align.CENTER)
                self.scenecut_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_b_frames_row(self):
                self._setup_b_frames_spin_button()

                self.b_frames_row = Adw.ActionRow()
                self.b_frames_row.set_title('B-Frames')
                self.b_frames_row.set_subtitle('Maximum concurrent B-frames that can be used')
                self.b_frames_row.add_suffix(self.b_frames_spin_button)
                self.b_frames_row.set_sensitive(False)

            def _setup_b_frames_spin_button(self):
                self.b_frames_spin_button = Gtk.SpinButton()
                self.b_frames_spin_button.set_range(video_codec.X264.B_FRAMES_MIN, video_codec.X264.B_FRAMES_MAX)
                self.b_frames_spin_button.set_digits(0)
                self.b_frames_spin_button.set_increments(1, 5)
                self.b_frames_spin_button.set_numeric(True)
                self.b_frames_spin_button.set_snap_to_ticks(True)
                self.b_frames_spin_button.set_value(3)
                self.b_frames_spin_button.set_vexpand(False)
                self.b_frames_spin_button.set_valign(Gtk.Align.CENTER)
                self.b_frames_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_b_adapt_row(self):
                self._setup_b_adapt_string_list()

                self.b_adapt_row = Adw.ComboRow()
                self.b_adapt_row.set_title('B-Adapt')
                self.b_adapt_row.set_subtitle('B-frame placement method')
                self.b_adapt_row.set_model(self.b_adapt_string_list)
                self.b_adapt_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.b_adapt_row.set_sensitive(False)

            def _setup_b_adapt_string_list(self):
                self.b_adapt_string_list = Gtk.StringList.new(video_codec.X264.B_ADAPT_UI)

            def _setup_b_pyramid_row(self):
                self._setup_b_pyramid_string_list()

                self.b_pyramid_row = Adw.ComboRow()
                self.b_pyramid_row.set_title('B-Pyramid')
                self.b_pyramid_row.set_subtitle('Allows B-frames to be referenced by other frames')
                self.b_pyramid_row.set_model(self.b_pyramid_string_list)
                self.b_pyramid_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.b_pyramid_row.set_sensitive(False)

            def _setup_b_pyramid_string_list(self):
                self.b_pyramid_string_list = Gtk.StringList.new(video_codec.X264.B_PYRAMID_UI)

            def _setup_no_cabac_row(self):
                self._setup_no_cabac_switch()

                self.no_cabac_row = Adw.ActionRow()
                self.no_cabac_row.set_title('No CABAC')
                self.no_cabac_row.set_subtitle('Disables the Context Adaptive Binary Arithmetic Coder')
                self.no_cabac_row.add_suffix(self.no_cabac_switch)
                self.no_cabac_row.set_sensitive(False)

            def _setup_no_cabac_switch(self):
                self.no_cabac_switch = Gtk.Switch()
                self.no_cabac_switch.set_vexpand(False)
                self.no_cabac_switch.set_valign(Gtk.Align.CENTER)
                self.no_cabac_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_ref_row(self):
                self._setup_ref_spin_button()

                self.ref_row = Adw.ActionRow()
                self.ref_row.set_title('Reference Frames')
                self.ref_row.set_subtitle('Number of previous frames each P-frame can reference')
                self.ref_row.add_suffix(self.ref_spin_button)
                self.ref_row.set_sensitive(False)

            def _setup_ref_spin_button(self):
                self.ref_spin_button = Gtk.SpinButton()
                self.ref_spin_button.set_range(video_codec.X264.REF_MIN, video_codec.X264.REF_MAX)
                self.ref_spin_button.set_digits(0)
                self.ref_spin_button.set_increments(1, 5)
                self.ref_spin_button.set_numeric(True)
                self.ref_spin_button.set_snap_to_ticks(True)
                self.ref_spin_button.set_value(3)
                self.ref_spin_button.set_vexpand(False)
                self.ref_spin_button.set_valign(Gtk.Align.CENTER)
                self.ref_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_deblock_row(self):
                self._setup_no_deblock_check_button()
                self._setup_deblock_alpha_spin_button()
                self._setup_deblock_beta_spin_button()

                self.deblock_values_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.deblock_values_vertical_box.append(self.deblock_alpha_horizontal_box)
                self.deblock_values_vertical_box.append(self.deblock_beta_horizontal_box)
                self.deblock_values_vertical_box.set_margin_top(10)
                self.deblock_values_vertical_box.set_margin_bottom(10)

                deblock_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                deblock_horizontal_box.append(self.no_deblock_check_button)
                deblock_horizontal_box.append(self.deblock_values_vertical_box)

                self.deblock_row = Adw.ActionRow()
                self.deblock_row.set_title('Deblocker')
                self.deblock_row.set_subtitle('Controls the state of the inloop deblocker')
                self.deblock_row.add_suffix(deblock_horizontal_box)
                self.deblock_row.set_sensitive(False)

            def _setup_no_deblock_check_button(self):
                self.no_deblock_check_button = Gtk.CheckButton(label='No Deblock')
                self.no_deblock_check_button.connect('toggled', self.on_no_deblock_check_button_toggled)

            def _setup_deblock_alpha_spin_button(self):
                deblock_alpha_label = Gtk.Label(label='Alpha')

                self.deblock_alpha_spin_button = Gtk.SpinButton()
                self.deblock_alpha_spin_button.set_range(video_codec.X264.DEBLOCK_MIN, video_codec.X264.DEBLOCK_MAX)
                self.deblock_alpha_spin_button.set_digits(0)
                self.deblock_alpha_spin_button.set_increments(1, 5)
                self.deblock_alpha_spin_button.set_numeric(True)
                self.deblock_alpha_spin_button.set_snap_to_ticks(True)
                self.deblock_alpha_spin_button.set_value(0)
                self.deblock_alpha_spin_button.set_vexpand(False)
                self.deblock_alpha_spin_button.set_valign(Gtk.Align.CENTER)
                self.deblock_alpha_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

                self.deblock_alpha_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.deblock_alpha_horizontal_box.append(deblock_alpha_label)
                self.deblock_alpha_horizontal_box.append(self.deblock_alpha_spin_button)
                self.deblock_alpha_horizontal_box.set_hexpand(False)
                self.deblock_alpha_horizontal_box.set_halign(Gtk.Align.END)

            def _setup_deblock_beta_spin_button(self):
                deblock_beta_label = Gtk.Label(label='Beta')

                self.deblock_beta_spin_button = Gtk.SpinButton()
                self.deblock_beta_spin_button.set_range(video_codec.X264.DEBLOCK_MIN, video_codec.X264.DEBLOCK_MAX)
                self.deblock_beta_spin_button.set_digits(0)
                self.deblock_beta_spin_button.set_increments(1, 5)
                self.deblock_beta_spin_button.set_numeric(True)
                self.deblock_beta_spin_button.set_snap_to_ticks(True)
                self.deblock_beta_spin_button.set_value(0)
                self.deblock_beta_spin_button.set_vexpand(False)
                self.deblock_beta_spin_button.set_valign(Gtk.Align.CENTER)
                self.deblock_beta_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

                self.deblock_beta_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.deblock_beta_horizontal_box.append(deblock_beta_label)
                self.deblock_beta_horizontal_box.append(self.deblock_beta_spin_button)
                self.deblock_beta_horizontal_box.set_hexpand(False)
                self.deblock_beta_horizontal_box.set_halign(Gtk.Align.END)

            def _setup_vbv_maxrate_row(self):
                self._setup_vbv_maxrate_spin_button()

                self.vbv_maxrate_row = Adw.ActionRow()
                self.vbv_maxrate_row.set_title('VBV Max Rate')
                self.vbv_maxrate_row.set_subtitle('VBV maximum bitrate in kbps')
                self.vbv_maxrate_row.add_suffix(self.vbv_maxrate_spin_button)
                self.vbv_maxrate_row.set_sensitive(False)

            def _setup_vbv_maxrate_spin_button(self):
                self.vbv_maxrate_spin_button = Gtk.SpinButton()
                self.vbv_maxrate_spin_button.set_range(video_codec.X264.BITRATE_MIN, video_codec.X264.BITRATE_MAX)
                self.vbv_maxrate_spin_button.set_digits(0)
                self.vbv_maxrate_spin_button.set_increments(100, 500)
                self.vbv_maxrate_spin_button.set_numeric(True)
                self.vbv_maxrate_spin_button.set_snap_to_ticks(True)
                self.vbv_maxrate_spin_button.set_value(2500)
                self.vbv_maxrate_spin_button.set_size_request(125, -1)
                self.vbv_maxrate_spin_button.set_vexpand(False)
                self.vbv_maxrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.vbv_maxrate_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_vbv_bufsize_row(self):
                self._setup_vbv_bufsize_spin_button()

                self.vbv_bufsize_row = Adw.ActionRow()
                self.vbv_bufsize_row.set_title('VBV Buffer Size')
                self.vbv_bufsize_row.set_subtitle('VBV buffer size in kbps')
                self.vbv_bufsize_row.add_suffix(self.vbv_bufsize_spin_button)
                self.vbv_bufsize_row.set_sensitive(False)

            def _setup_vbv_bufsize_spin_button(self):
                self.vbv_bufsize_spin_button = Gtk.SpinButton()
                self.vbv_bufsize_spin_button.set_range(video_codec.X264.BITRATE_MIN, video_codec.X264.BITRATE_MAX)
                self.vbv_bufsize_spin_button.set_digits(0)
                self.vbv_bufsize_spin_button.set_increments(100, 500)
                self.vbv_bufsize_spin_button.set_numeric(True)
                self.vbv_bufsize_spin_button.set_snap_to_ticks(True)
                self.vbv_bufsize_spin_button.set_value(2500)
                self.vbv_bufsize_spin_button.set_size_request(125, -1)
                self.vbv_bufsize_spin_button.set_vexpand(False)
                self.vbv_bufsize_spin_button.set_valign(Gtk.Align.CENTER)
                self.vbv_bufsize_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_aq_mode_row(self):
                self._setup_aq_mode_string_list()

                self.aq_mode_row = Adw.ComboRow()
                self.aq_mode_row.set_title('AQ Mode')
                self.aq_mode_row.set_subtitle('Mode to distribute available bits across all macroblocks')
                self.aq_mode_row.set_model(self.aq_mode_string_list)
                self.aq_mode_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.aq_mode_row.set_sensitive(False)

            def _setup_aq_mode_string_list(self):
                self.aq_mode_string_list = Gtk.StringList.new(video_codec.X264.AQ_MODE_UI)

            def _setup_aq_strength_row(self):
                self._setup_aq_strength_spin_button()

                self.aq_strength_row = Adw.ActionRow()
                self.aq_strength_row.set_title('AQ Strength')
                self.aq_strength_row.set_subtitle('Strength of AQ bias towards low detail macroblocks')
                self.aq_strength_row.add_suffix(self.aq_strength_spin_button)
                self.aq_strength_row.set_sensitive(False)

            def _setup_aq_strength_spin_button(self):
                self.aq_strength_spin_button = Gtk.SpinButton()
                self.aq_strength_spin_button.set_range(video_codec.X264.AQ_STRENGTH_MIN,
                                                       video_codec.X264.AQ_STRENGTH_MAX)
                self.aq_strength_spin_button.set_digits(1)
                self.aq_strength_spin_button.set_increments(0.1, 0.5)
                self.aq_strength_spin_button.set_numeric(True)
                self.aq_strength_spin_button.set_snap_to_ticks(True)
                self.aq_strength_spin_button.set_value(1.0)
                self.aq_strength_spin_button.set_vexpand(False)
                self.aq_strength_spin_button.set_valign(Gtk.Align.CENTER)
                self.aq_strength_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_partitions_row(self):
                self._setup_partitions_enabled_radio_buttons()
                self._setup_partitions_check_buttons()

                partitions_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                partitions_horizontal_box.append(self.partitions_enabled_horizontal_box)
                partitions_horizontal_box.append(self.partitions_options_vertical_box)
                partitions_horizontal_box.set_margin_top(10)
                partitions_horizontal_box.set_margin_bottom(10)

                self.partitions_row = Adw.ActionRow()
                self.partitions_row.set_title('Partitions')
                self.partitions_row.set_subtitle('Per-frametype macroblock partitions')
                self.partitions_row.add_suffix(partitions_horizontal_box)
                self.partitions_row.set_sensitive(False)

            def _setup_partitions_enabled_radio_buttons(self):
                self.partitions_auto_radio_button = Gtk.CheckButton(label='Auto')
                self.partitions_auto_radio_button.set_active(True)

                self.partitions_custom_radio_button = Gtk.CheckButton(label='Custom')
                self.partitions_custom_radio_button.set_group(self.partitions_auto_radio_button)
                self.partitions_custom_radio_button.connect('toggled', self.on_partitions_custom_check_button_toggled)

                self.partitions_enabled_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.partitions_enabled_horizontal_box.append(self.partitions_auto_radio_button)
                self.partitions_enabled_horizontal_box.append(self.partitions_custom_radio_button)

            def _setup_partitions_check_buttons(self):
                self.i4x4_check_button = Gtk.CheckButton(label='i4x4')
                self.i4x4_check_button.set_hexpand(False)
                self.i4x4_check_button.set_halign(Gtk.Align.START)
                self.i4x4_check_button.connect('toggled', self.on_widget_changed_clicked_set)
                self.i8x8_check_button = Gtk.CheckButton(label='i8x8')
                self.i8x8_check_button.set_hexpand(False)
                self.i8x8_check_button.set_halign(Gtk.Align.START)
                self.i8x8_check_button.connect('toggled', self.on_widget_changed_clicked_set)
                self.p4x4_check_button = Gtk.CheckButton(label='p4x4')
                self.p4x4_check_button.set_hexpand(False)
                self.p4x4_check_button.set_halign(Gtk.Align.START)
                self.p4x4_check_button.connect('toggled', self.on_widget_changed_clicked_set)
                self.p8x8_check_button = Gtk.CheckButton(label='p8x8')
                self.p8x8_check_button.set_hexpand(False)
                self.p8x8_check_button.set_halign(Gtk.Align.START)
                self.p8x8_check_button.connect('toggled', self.on_widget_changed_clicked_set)
                self.b8x8_check_button = Gtk.CheckButton(label='b8x8')
                self.b8x8_check_button.set_hexpand(False)
                self.b8x8_check_button.set_halign(Gtk.Align.START)
                self.b8x8_check_button.connect('toggled', self.on_widget_changed_clicked_set)

                i_partitions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                i_partitions_box.append(self.i4x4_check_button)
                i_partitions_box.append(self.i8x8_check_button)

                p_partitions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                p_partitions_box.append(self.p4x4_check_button)
                p_partitions_box.append(self.p8x8_check_button)

                self.partitions_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                self.partitions_options_vertical_box.append(i_partitions_box)
                self.partitions_options_vertical_box.append(p_partitions_box)
                self.partitions_options_vertical_box.append(self.b8x8_check_button)

            def _setup_direct_row(self):
                self._setup_direct_string_list()

                self.direct_row = Adw.ComboRow()
                self.direct_row.set_title('Direct')
                self.direct_row.set_subtitle('Sets prediction mode for direct motion vectors')
                self.direct_row.set_model(self.direct_string_list)
                self.direct_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.direct_row.set_sensitive(False)

            def _setup_direct_string_list(self):
                self.direct_string_list = Gtk.StringList.new(video_codec.X264.DIRECT_UI)

            def _setup_weight_b_row(self):
                self._setup_weight_b_switch()

                self.weight_b_row = Adw.ActionRow()
                self.weight_b_row.set_title('Weight B')
                self.weight_b_row.set_subtitle('Allow non-symmetric weighting between references in B-frames')
                self.weight_b_row.add_suffix(self.weight_b_switch)
                self.weight_b_row.set_sensitive(False)

            def _setup_weight_b_switch(self):
                self.weight_b_switch = Gtk.Switch()
                self.weight_b_switch.set_vexpand(False)
                self.weight_b_switch.set_valign(Gtk.Align.CENTER)
                self.weight_b_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_me_row(self):
                self._setup_me_string_list()

                self.me_row = Adw.ComboRow()
                self.me_row.set_title('Motion Estimation')
                self.me_row.set_subtitle('Sets full-pixel motion estimation method')
                self.me_row.set_model(self.me_string_list)
                self.me_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.me_row.set_sensitive(False)

            def _setup_me_string_list(self):
                self.me_string_list = Gtk.StringList.new(video_codec.X264.ME)

            def _setup_me_range_row(self):
                self._setup_me_range_spin_button()

                self.me_range_row = Adw.ActionRow()
                self.me_range_row.set_title('ME Range')
                self.me_range_row.set_subtitle('Controls the max range of the motion search')
                self.me_range_row.add_suffix(self.me_range_spin_button)
                self.me_range_row.set_sensitive(False)

            def _setup_me_range_spin_button(self):
                self.me_range_spin_button = Gtk.SpinButton()
                self.me_range_spin_button.set_range(video_codec.X264.ME_RANGE_MIN, video_codec.X264.ME_RANGE_MAX)
                self.me_range_spin_button.set_digits(0)
                self.me_range_spin_button.set_increments(4, 8)
                self.me_range_spin_button.set_numeric(True)
                self.me_range_spin_button.set_snap_to_ticks(True)
                self.me_range_spin_button.set_value(16)
                self.me_range_spin_button.set_vexpand(False)
                self.me_range_spin_button.set_valign(Gtk.Align.CENTER)
                self.me_range_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_subme_row(self):
                self._setup_subme_string_list()

                self.subme_row = Adw.ComboRow()
                self.subme_row.set_title('SubME')
                self.subme_row.set_subtitle('Sets sub-pixel estimation complexity')
                self.subme_row.set_model(self.subme_string_list)
                self.subme_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.subme_row.set_sensitive(False)

            def _setup_subme_string_list(self):
                self.subme_string_list = Gtk.StringList.new(video_codec.X264.SUB_ME_UI)

            def _setup_psy_rd_row(self):
                self._setup_psyrd_spin_button()
                self._setup_psyrd_trellis_spin_button()

                psyrd_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                psyrd_vertical_box.append(self.psyrd_spin_button)
                psyrd_vertical_box.append(self.psyrd_trellis_spin_button)
                psyrd_vertical_box.set_margin_top(10)
                psyrd_vertical_box.set_margin_bottom(10)

                self.psyrd_row = Adw.ActionRow()
                self.psyrd_row.set_title('PsyRD')
                self.psyrd_row.set_subtitle('Psychovisual rate distortion strength')
                self.psyrd_row.add_suffix(psyrd_vertical_box)
                self.psyrd_row.set_sensitive(False)

            def _setup_psyrd_spin_button(self):
                self.psyrd_spin_button = Gtk.SpinButton()
                self.psyrd_spin_button.set_range(video_codec.X264.PSYRD_MIN, video_codec.X264.PSYRD_MAX)
                self.psyrd_spin_button.set_digits(1)
                self.psyrd_spin_button.set_increments(0.1, 0.5)
                self.psyrd_spin_button.set_numeric(True)
                self.psyrd_spin_button.set_snap_to_ticks(True)
                self.psyrd_spin_button.set_value(1.0)
                self.psyrd_spin_button.set_vexpand(False)
                self.psyrd_spin_button.set_valign(Gtk.Align.CENTER)
                self.psyrd_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_psyrd_trellis_spin_button(self):
                self.psyrd_trellis_spin_button = Gtk.SpinButton()
                self.psyrd_trellis_spin_button.set_range(video_codec.X264.PSYRD_TRELLIS_MIN,
                                                         video_codec.X264.PSYRD_TRELLIS_MAX)
                self.psyrd_trellis_spin_button.set_digits(2)
                self.psyrd_trellis_spin_button.set_increments(0.05, 0.1)
                self.psyrd_trellis_spin_button.set_numeric(True)
                self.psyrd_trellis_spin_button.set_snap_to_ticks(True)
                self.psyrd_trellis_spin_button.set_value(0.0)
                self.psyrd_trellis_spin_button.set_vexpand(False)
                self.psyrd_trellis_spin_button.set_valign(Gtk.Align.CENTER)
                self.psyrd_trellis_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_mixed_refs_row(self):
                self._setup_mixed_refs_switch()

                self.mixed_refs_row = Adw.ActionRow()
                self.mixed_refs_row.set_title('Mixed Refs')
                self.mixed_refs_row.set_subtitle('Allows reference selection on a per-8x8 partition basis')
                self.mixed_refs_row.add_suffix(self.mixed_refs_switch)
                self.mixed_refs_row.set_sensitive(False)

            def _setup_mixed_refs_switch(self):
                self.mixed_refs_switch = Gtk.Switch()
                self.mixed_refs_switch.set_vexpand(False)
                self.mixed_refs_switch.set_valign(Gtk.Align.CENTER)
                self.mixed_refs_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_dct8x8_row(self):
                self._setup_dct8x8_switch()

                self.dct8x8_row = Adw.ActionRow()
                self.dct8x8_row.set_title('dct8x8')
                self.dct8x8_row.set_subtitle('Adaptive use of 8x8 transforms in I-frames')
                self.dct8x8_row.add_suffix(self.dct8x8_switch)
                self.dct8x8_row.set_sensitive(False)

            def _setup_dct8x8_switch(self):
                self.dct8x8_switch = Gtk.Switch()
                self.dct8x8_switch.set_vexpand(False)
                self.dct8x8_switch.set_valign(Gtk.Align.CENTER)
                self.dct8x8_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_trellis_row(self):
                self._setup_trellis_string_list()

                self.trellis_row = Adw.ComboRow()
                self.trellis_row.set_title('Trellis')
                self.trellis_row.set_subtitle('Trellis quantization to increase efficiency')
                self.trellis_row.set_model(self.trellis_string_list)
                self.trellis_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.trellis_row.set_sensitive(False)

            def _setup_trellis_string_list(self):
                self.trellis_string_list = Gtk.StringList.new(video_codec.X264.TRELLIS_UI)

            def _setup_no_fast_pskip_row(self):
                self._setup_no_fast_pskip_switch()

                self.no_fast_pskip_row = Adw.ActionRow()
                self.no_fast_pskip_row.set_title('No Fast PSkip')
                self.no_fast_pskip_row.set_subtitle('Disables early skip detection on P-frames')
                self.no_fast_pskip_row.add_suffix(self.no_fast_pskip_switch)
                self.no_fast_pskip_row.set_sensitive(False)

            def _setup_no_fast_pskip_switch(self):
                self.no_fast_pskip_switch = Gtk.Switch()
                self.no_fast_pskip_switch.set_vexpand(False)
                self.no_fast_pskip_switch.set_valign(Gtk.Align.CENTER)
                self.no_fast_pskip_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_no_dct_decimate_row(self):
                self._setup_no_dct_decimate_switch()

                self.no_dct_decimate_row = Adw.ActionRow()
                self.no_dct_decimate_row.set_title('No DCT Decimate')
                self.no_dct_decimate_row.set_subtitle('Disables coefficient thresholding on P-frames')
                self.no_dct_decimate_row.add_suffix(self.no_dct_decimate_switch)
                self.no_dct_decimate_row.set_sensitive(False)

            def _setup_no_dct_decimate_switch(self):
                self.no_dct_decimate_switch = Gtk.Switch()
                self.no_dct_decimate_switch.set_vexpand(False)
                self.no_dct_decimate_switch.set_valign(Gtk.Align.CENTER)
                self.no_dct_decimate_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_weight_p_row(self):
                self._setup_weight_p_switch()

                self.weight_p_row = Adw.ActionRow()
                self.weight_p_row.set_title('Weight P')
                self.weight_p_row.set_subtitle('Allow non-symmetric weighting between references in P-frames')
                self.weight_p_row.add_suffix(self.weight_p_switch)
                self.weight_p_row.set_sensitive(False)

            def _setup_weight_p_switch(self):
                self.weight_p_switch = Gtk.Switch()
                self.weight_p_switch.set_vexpand(False)
                self.weight_p_switch.set_valign(Gtk.Align.CENTER)
                self.weight_p_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def set_widgets_setting_up(self, is_widgets_setting_up: bool):
                self.is_widgets_setting_up = is_widgets_setting_up

            def set_vbv_state(self, is_vbv_state_enabled: bool):
                if self.advanced_settings_switch.get_active():
                    is_sensitive = is_vbv_state_enabled and not self.constant_check_button.get_active()
                    self.vbv_maxrate_row.set_sensitive(is_sensitive)
                    self.vbv_bufsize_row.set_sensitive(is_sensitive)
                else:
                    self.vbv_maxrate_row.set_sensitive(False)
                    self.vbv_bufsize_row.set_sensitive(False)

            def apply_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.set_widgets_setting_up, True)
                self._apply_preset_setting_to_widgets(encode_task)
                self._apply_profile_setting_to_widgets(encode_task)
                self._apply_level_setting_to_widgets(encode_task)
                self._apply_tune_setting_to_widgets(encode_task)
                self._apply_rate_type_settings_to_widgets(encode_task)
                self._apply_crf_setting_to_widgets(encode_task)
                self._apply_qp_setting_to_widgets(encode_task)
                self._apply_bitrate_setting_to_widgets(encode_task)
                self._apply_bitrate_type_settings_to_widgets(encode_task)
                self._apply_advanced_settings_to_widgets(encode_task)
                GLib.idle_add(self.set_widgets_setting_up, False)

            def _apply_preset_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.preset_row.set_selected, encode_task.get_video_codec().preset)

            def _apply_profile_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.profile_row.set_selected, encode_task.get_video_codec().profile)

            def _apply_level_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.level_row.set_selected, encode_task.get_video_codec().level)

            def _apply_tune_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.tune_row.set_selected, encode_task.get_video_codec().tune)

            def _apply_rate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_crf_enabled:
                    GLib.idle_add(self.crf_check_button.set_active, True)
                elif encode_task.get_video_codec().is_qp_enabled:
                    GLib.idle_add(self.qp_check_button.set_active, True)
                else:
                    GLib.idle_add(self.bitrate_check_button.set_active, True)

            def _apply_crf_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.crf_scale.set_value, encode_task.get_video_codec().crf)

            def _apply_qp_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.qp_scale.set_value, encode_task.get_video_codec().qp)

            def _apply_bitrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.bitrate_spin_button.set_value, encode_task.get_video_codec().bitrate)

            def _apply_bitrate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().constant_bitrate:
                    GLib.idle_add(self.constant_check_button.set_active, True)
                elif encode_task.get_video_codec().encode_pass:
                    GLib.idle_add(self.dual_pass_check_button.set_active, True)
                else:
                    GLib.idle_add(self.average_check_button.set_active, True)

            def _apply_advanced_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.advanced_settings_switch.set_active,
                              encode_task.get_video_codec().is_advanced_enabled)
                self._apply_keyint_setting_to_widgets(encode_task)
                self._apply_min_keyint_setting_to_widgets(encode_task)
                self._apply_scenecut_setting_to_widgets(encode_task)
                self._apply_b_frames_setting_to_widgets(encode_task)
                self._apply_b_adapt_setting_to_widgets(encode_task)
                self._apply_b_pyramid_setting_to_widgets(encode_task)
                self._apply_no_cabac_setting_to_widgets(encode_task)
                self._apply_ref_setting_to_widgets(encode_task)
                self._apply_deblock_settings_to_widgets(encode_task)
                self._apply_vbv_maxrate_setting_to_widgets(encode_task)
                self._apply_vbv_bufsize_setting_to_widgets(encode_task)
                self._apply_aq_mode_setting_to_widgets(encode_task)
                self._apply_aq_strength_setting_to_widgets(encode_task)
                self._apply_partitions_setting_to_widgets(encode_task)
                self._apply_direct_setting_to_widgets(encode_task)
                self._apply_weight_b_setting_to_widgets(encode_task)
                self._apply_me_setting_to_widgets(encode_task)
                self._apply_me_range_setting_to_widgets(encode_task)
                self._apply_subme_setting_to_widgets(encode_task)
                self._apply_psy_rd_setting_to_widgets(encode_task)
                self._apply_mixed_refs_to_widgets(encode_task)
                self._apply_dct8x8_setting_to_widgets(encode_task)
                self._apply_trellis_setting_to_widgets(encode_task)
                self._apply_no_fast_p_skip_setting_to_widgets(encode_task)
                self._apply_no_dct_decimate_setting_to_widgets(encode_task)
                self._apply_weight_p_setting_to_widgets(encode_task)

            def _apply_keyint_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.keyint_spin_button.set_value, encode_task.get_video_codec().keyint)

            def _apply_min_keyint_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.min_keyint_spin_button.set_value, encode_task.get_video_codec().min_keyint)

            def _apply_scenecut_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.scenecut_spin_button.set_value, encode_task.get_video_codec().scenecut)

            def _apply_b_frames_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_frames_spin_button.set_value, encode_task.get_video_codec().bframes)

            def _apply_b_adapt_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_adapt_row.set_selected, encode_task.get_video_codec().b_adapt)

            def _apply_b_pyramid_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_pyramid_row.set_selected, encode_task.get_video_codec().b_pyramid)

            def _apply_no_cabac_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_cabac_switch.set_active, encode_task.get_video_codec().no_cabac)

            def _apply_ref_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.ref_spin_button.set_value, encode_task.get_video_codec().ref)

            def _apply_deblock_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_deblock_check_button.set_active, encode_task.get_video_codec().no_deblock)

                deblock_alpha, deblock_beta = encode_task.get_video_codec().deblock
                GLib.idle_add(self.deblock_alpha_spin_button.set_value, deblock_alpha)
                GLib.idle_add(self.deblock_beta_spin_button.set_value, deblock_beta)

            def _apply_vbv_maxrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.vbv_maxrate_spin_button.set_value, encode_task.get_video_codec().vbv_maxrate)

            def _apply_vbv_bufsize_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.vbv_bufsize_spin_button.set_value, encode_task.get_video_codec().vbv_bufsize)

            def _apply_aq_mode_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.aq_mode_row.set_selected, encode_task.get_video_codec().aq_mode)

            def _apply_aq_strength_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.aq_strength_spin_button.set_value, encode_task.get_video_codec().aq_strength)

            def _apply_partitions_setting_to_widgets(self, encode_task: task.Encode):
                partitions_tuple = encode_task.get_video_codec().partitions

                if partitions_tuple == 'all':
                    GLib.idle_add(self.partitions_custom_radio_button.set_active, True)
                    GLib.idle_add(self.i4x4_check_button.set_active, True)
                    GLib.idle_add(self.i8x8_check_button.set_active, True)
                    GLib.idle_add(self.p4x4_check_button.set_active, True)
                    GLib.idle_add(self.p8x8_check_button.set_active, True)
                    GLib.idle_add(self.b8x8_check_button.set_active, True)
                elif partitions_tuple == 'none':
                    GLib.idle_add(self.partitions_custom_radio_button.set_active, True)
                    GLib.idle_add(self.i4x4_check_button.set_active, False)
                    GLib.idle_add(self.i8x8_check_button.set_active, False)
                    GLib.idle_add(self.p4x4_check_button.set_active, False)
                    GLib.idle_add(self.p8x8_check_button.set_active, False)
                    GLib.idle_add(self.b8x8_check_button.set_active, False)
                elif partitions_tuple:
                    GLib.idle_add(self.partitions_custom_radio_button.set_active, True)
                    GLib.idle_add(self.i4x4_check_button.set_active, 'i4x4' in partitions_tuple)
                    GLib.idle_add(self.i8x8_check_button.set_active, 'i8x8' in partitions_tuple)
                    GLib.idle_add(self.p4x4_check_button.set_active, 'p4x4' in partitions_tuple)
                    GLib.idle_add(self.p8x8_check_button.set_active, 'p8x8' in partitions_tuple)
                    GLib.idle_add(self.b8x8_check_button.set_active, 'b8x8' in partitions_tuple)
                else:
                    GLib.idle_add(self.partitions_auto_radio_button.set_active, True)
                    GLib.idle_add(self.i4x4_check_button.set_active, False)
                    GLib.idle_add(self.i8x8_check_button.set_active, False)
                    GLib.idle_add(self.p4x4_check_button.set_active, False)
                    GLib.idle_add(self.p8x8_check_button.set_active, False)
                    GLib.idle_add(self.b8x8_check_button.set_active, False)

            def _apply_direct_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.direct_row.set_selected, encode_task.get_video_codec().direct)

            def _apply_weight_b_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.weight_b_switch.set_active, encode_task.get_video_codec().weightb)

            def _apply_me_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.me_row.set_selected, encode_task.get_video_codec().me)

            def _apply_me_range_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.me_range_spin_button.set_value, encode_task.get_video_codec().me_range)

            def _apply_subme_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.subme_row.set_selected, encode_task.get_video_codec().subme)

            def _apply_psy_rd_setting_to_widgets(self, encode_task: task.Encode):
                psyrd, psyrd_trellis = encode_task.get_video_codec().psy_rd
                GLib.idle_add(self.psyrd_spin_button.set_value, psyrd)
                GLib.idle_add(self.psyrd_trellis_spin_button.set_value, psyrd_trellis)

            def _apply_mixed_refs_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.mixed_refs_switch.set_active, encode_task.get_video_codec().mixed_refs)

            def _apply_dct8x8_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.dct8x8_switch.set_active, encode_task.get_video_codec().dct8x8)

            def _apply_trellis_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.trellis_row.set_selected, encode_task.get_video_codec().trellis)

            def _apply_no_fast_p_skip_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_fast_pskip_switch.set_active, encode_task.get_video_codec().no_fast_pskip)

            def _apply_no_dct_decimate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_dct_decimate_switch.set_active, encode_task.get_video_codec().no_dct_decimate)

            def _apply_weight_p_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.weight_p_switch.set_active, encode_task.get_video_codec().weightp)

            def apply_settings_from_widgets(self, is_delay_enabled: bool):
                if is_delay_enabled:
                    time.sleep(0.25)

                x264_settings = video_codec.X264()
                x264_settings.preset = self.preset_row.get_selected()
                x264_settings.profile = self.profile_row.get_selected()
                x264_settings.level = self.level_row.get_selected()
                x264_settings.tune = self.tune_row.get_selected()
                x264_settings.is_advanced_enabled = self.advanced_settings_switch.get_active()

                self._apply_rate_type_settings_from_widgets(x264_settings)

                if self.advanced_settings_switch.get_active():
                    x264_settings.keyint = self.keyint_spin_button.get_value_as_int()
                    x264_settings.min_keyint = self.min_keyint_spin_button.get_value_as_int()
                    x264_settings.scenecut = self.scenecut_spin_button.get_value_as_int()
                    x264_settings.bframes = self.b_frames_spin_button.get_value_as_int()
                    x264_settings.b_adapt = self.b_adapt_row.get_selected()
                    x264_settings.b_pyramid = self.b_pyramid_row.get_selected()
                    x264_settings.no_cabac = self.no_cabac_switch.get_active()
                    x264_settings.ref = self.ref_spin_button.get_value_as_int()
                    x264_settings.aq_mode = self.aq_mode_row.get_selected()
                    x264_settings.aq_strength = self.aq_strength_spin_button.get_value()
                    x264_settings.direct = self.direct_row.get_selected()
                    x264_settings.weightb = self.weight_b_switch.get_active()
                    x264_settings.me = self.me_row.get_selected()
                    x264_settings.me_range = self.me_range_spin_button.get_value_as_int()
                    x264_settings.subme = self.subme_row.get_selected()
                    x264_settings.psy_rd = (self.psyrd_spin_button.get_value(),
                                            self.psyrd_trellis_spin_button.get_value())
                    x264_settings.mixed_refs = self.mixed_refs_switch.get_active()
                    x264_settings.dct8x8 = self.dct8x8_switch.get_active()
                    x264_settings.trellis = self.trellis_row.get_selected()
                    x264_settings.no_fast_pskip = self.no_fast_pskip_switch.get_active()
                    x264_settings.no_dct_decimate = self.no_dct_decimate_switch.get_active()
                    x264_settings.weightp = self.weight_p_switch.get_active()

                    self._apply_vbv_settings_from_widgets(x264_settings)
                    self._apply_deblock_settings_from_widgets(x264_settings)
                    self._apply_partitions_setting_from_widgets(x264_settings)

                for input_row in self.inputs_page.get_selected_rows():
                    encode_task = input_row.encode_task
                    encode_task.set_video_codec(copy.deepcopy(x264_settings))

                    if video_codec.is_codec_2_pass(encode_task.get_video_codec()):
                        stats_file_path = os.path.join(encode_task.temp_output_file.dir,
                                                       encode_task.temp_output_file.name + '.log')
                        encode_task.video_codec.stats = stats_file_path

                    print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

                self.inputs_page.update_preview_page_encode_task()

            def _apply_rate_type_settings_from_widgets(self, x264_settings: video_codec.X264):
                if self.crf_check_button.get_active():
                    x264_settings.crf = self.crf_scale.get_value()
                elif self.qp_check_button.get_active():
                    x264_settings.qp = self.qp_scale.get_value()
                else:
                    x264_settings.bitrate = self.bitrate_spin_button.get_value_as_int()

                    if self.constant_check_button.get_active():
                        x264_settings.constant_bitrate = True
                    elif self.dual_pass_check_button.get_active():
                        x264_settings.encode_pass = 1

            def _apply_deblock_settings_from_widgets(self, x264_settings: video_codec.X264):
                x264_settings.no_deblock = self.no_deblock_check_button.get_active()

                if self.no_deblock_check_button.get_active():
                    x264_settings.deblock = None
                else:
                    x264_settings.deblock = (self.deblock_alpha_spin_button.get_value_as_int(),
                                             self.deblock_beta_spin_button.get_value_as_int())

            def _apply_vbv_settings_from_widgets(self, x264_settings: video_codec.X264):
                x264_settings.vbv_maxrate = self.vbv_maxrate_spin_button.get_value_as_int()
                x264_settings.vbv_bufsize = self.vbv_bufsize_spin_button.get_value_as_int()

            def _apply_partitions_setting_from_widgets(self, x264_settings: video_codec.X264):
                if self.partitions_auto_radio_button.get_active():
                    x264_settings.partitions = None

                    return

                is_all_partitions = self.i4x4_check_button.get_active() \
                                    and self.i8x8_check_button.get_active() \
                                    and self.p4x4_check_button.get_active() \
                                    and self.p8x8_check_button.get_active() \
                                    and self.b8x8_check_button.get_active()
                is_any_partitions = self.i4x4_check_button.get_active() \
                                    or self.i8x8_check_button.get_active() \
                                    or self.p4x4_check_button.get_active() \
                                    or self.p8x8_check_button.get_active() \
                                    or self.b8x8_check_button.get_active()

                if is_all_partitions:
                    x264_settings.partitions = 'all'
                elif is_any_partitions:
                    partitions_list = []

                    if self.i4x4_check_button.get_active():
                        partitions_list.append('i4x4')

                    if self.i8x8_check_button.get_active():
                        partitions_list.append('i8x8')

                    if self.p4x4_check_button.get_active():
                        partitions_list.append('p4x4')

                    if self.p8x8_check_button.get_active():
                        partitions_list.append('p8x8')

                    if self.b8x8_check_button.get_active():
                        partitions_list.append('b8x8')

                    x264_settings.partitions = tuple(partitions_list)
                else:
                    x264_settings.partitions = 'none'

            def on_widget_changed_clicked_set(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                is_delay_enabled = (self.crf_event_controller_scroll in args or self.qp_event_controller_scroll in args)

                threading.Thread(target=self.apply_settings_from_widgets, args=(is_delay_enabled,)).start()

            def on_scale_gesture_stopped(self, user_data, gesture_click):
                if gesture_click.get_device():
                    return

                self.on_widget_changed_clicked_set()

            def on_crf_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('crf_page')
                    self.rate_type_settings_row.set_title('CRF')
                    self.rate_type_settings_row.set_subtitle('Constant Rate Factor')

                    self.on_widget_changed_clicked_set(check_button)

            def on_qp_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('qp_page')
                    self.rate_type_settings_row.set_title('QP')
                    self.rate_type_settings_row.set_subtitle('Constant Quantizer: P-frames')

                    self.on_widget_changed_clicked_set(check_button)

            def on_bitrate_check_button_toggled(self, check_button):
                self.set_vbv_state(check_button.get_active())

                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('bitrate_page')
                    self.rate_type_settings_row.set_title('Bitrate')
                    self.rate_type_settings_row.set_subtitle('Target video bitrate in kbps')

                    self.on_widget_changed_clicked_set(check_button)

            def on_advanced_settings_switch_state_set(self, switch, user_data):
                is_state_enabled = switch.get_active()
                self._set_vbv_rows_enabled(is_state_enabled)
                self.keyint_row.set_sensitive(is_state_enabled)
                self.min_keyint_row.set_sensitive(is_state_enabled)
                self.scenecut_row.set_sensitive(is_state_enabled)
                self.b_frames_row.set_sensitive(is_state_enabled)
                self.b_adapt_row.set_sensitive(is_state_enabled)
                self.b_pyramid_row.set_sensitive(is_state_enabled)
                self.weight_b_row.set_sensitive(is_state_enabled)
                self.weight_p_row.set_sensitive(is_state_enabled)
                self.no_fast_pskip_row.set_sensitive(is_state_enabled)
                self.ref_row.set_sensitive(is_state_enabled)
                self.mixed_refs_row.set_sensitive(is_state_enabled)
                self.no_cabac_row.set_sensitive(is_state_enabled)
                self._set_deblock_row_enabled(is_state_enabled)
                self.aq_mode_row.set_sensitive(is_state_enabled)
                self.aq_strength_row.set_sensitive(is_state_enabled)
                self.partitions_row.set_sensitive(is_state_enabled)
                self.dct8x8_row.set_sensitive(is_state_enabled)
                self.direct_row.set_sensitive(is_state_enabled)
                self.me_row.set_sensitive(is_state_enabled)
                self.me_range_row.set_sensitive(is_state_enabled)
                self.subme_row.set_sensitive(is_state_enabled)
                self.psyrd_row.set_sensitive(is_state_enabled)
                self.trellis_row.set_sensitive(is_state_enabled)
                self.no_dct_decimate_row.set_sensitive(is_state_enabled)

                self.on_widget_changed_clicked_set(switch)

            def _set_vbv_rows_enabled(self, is_enabled: bool):
                self.set_vbv_state(is_enabled and self.bitrate_check_button.get_active())

            def _set_deblock_row_enabled(self, is_enabled: bool):
                self.deblock_row.set_sensitive(is_enabled)
                self.deblock_values_vertical_box.set_sensitive(not self.no_deblock_check_button.get_active())

            def on_partitions_custom_check_button_toggled(self, check_button):
                self.i4x4_check_button.set_sensitive(check_button.get_active())
                self.i8x8_check_button.set_sensitive(check_button.get_active())
                self.p4x4_check_button.set_sensitive(check_button.get_active())
                self.p8x8_check_button.set_sensitive(check_button.get_active())
                self.b8x8_check_button.set_sensitive(check_button.get_active())

                self.on_widget_changed_clicked_set(check_button)

            def on_no_deblock_check_button_toggled(self, check_button):
                self.deblock_values_vertical_box.set_sensitive(not check_button.get_active())

                self.on_widget_changed_clicked_set(check_button)

            def on_bitrate_type_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.set_vbv_state(True)

                    self.on_widget_changed_clicked_set(check_button)

        class X265StackPage(Gtk.Box):
            def __init__(self, inputs_page):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self.inputs_page = inputs_page
                self.is_widgets_setting_up = False

                self._setup_codec_settings()
                self._setup_codec_advanced_settings()

                self.append(self.codec_settings_group)
                self.append(self.advanced_settings_group)

            def _setup_codec_settings(self):
                self._setup_preset_row()
                self._setup_profile_row()
                self._setup_level_row()
                self._setup_tune_row()
                self._setup_rate_type_row()
                self._setup_rate_type_settings_row()

                self.codec_settings_group = Adw.PreferencesGroup()
                self.codec_settings_group.set_title('X265 Settings')
                self.codec_settings_group.add(self.preset_row)
                self.codec_settings_group.add(self.profile_row)
                self.codec_settings_group.add(self.level_row)
                self.codec_settings_group.add(self.tune_row)
                self.codec_settings_group.add(self.rate_type_row)
                self.codec_settings_group.add(self.rate_type_settings_row)

            def _setup_preset_row(self):
                self._setup_preset_string_list()

                self.preset_row = Adw.ComboRow()
                self.preset_row.set_title('Preset')
                self.preset_row.set_subtitle('Encoder preset')
                self.preset_row.set_model(self.preset_string_list)
                self.preset_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_preset_string_list(self):
                self.preset_string_list = Gtk.StringList.new(video_codec.X265.PRESET)

            def _setup_profile_row(self):
                self._setup_profile_string_list()

                self.profile_row = Adw.ComboRow()
                self.profile_row.set_title('Profile')
                self.profile_row.set_subtitle('Encoder profile')
                self.profile_row.set_model(self.profile_string_list)
                self.profile_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_profile_string_list(self):
                self.profile_string_list = Gtk.StringList.new(video_codec.X265.PROFILE)

            def _setup_level_row(self):
                self._setup_level_string_list()

                self.level_row = Adw.ComboRow()
                self.level_row.set_title('Level')
                self.level_row.set_subtitle('Encoder level')
                self.level_row.set_model(self.level_string_list)
                self.level_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_level_string_list(self):
                self.level_string_list = Gtk.StringList.new(video_codec.X265.LEVEL)

            def _setup_tune_row(self):
                self._setup_tune_string_list()

                self.tune_row = Adw.ComboRow()
                self.tune_row.set_title('Tune')
                self.tune_row.set_subtitle('Encoder tune')
                self.tune_row.set_model(self.tune_string_list)
                self.tune_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_tune_string_list(self):
                self.tune_string_list = Gtk.StringList.new(video_codec.X265.TUNE)

            def _setup_rate_type_row(self):
                self._setup_rate_type_radio_buttons()

                self.rate_type_row = Adw.ActionRow()
                self.rate_type_row.set_title('Rate Type')
                self.rate_type_row.set_subtitle('Codec rate type method')
                self.rate_type_row.add_suffix(self.rate_type_horizontal_box)

            def _setup_rate_type_radio_buttons(self):
                self.crf_check_button = Gtk.CheckButton(label='CRF')
                self.crf_check_button.set_active(True)
                self.crf_check_button.connect('toggled', self.on_crf_check_button_toggled)

                self.qp_check_button = Gtk.CheckButton(label='QP')
                self.qp_check_button.set_group(self.crf_check_button)
                self.qp_check_button.connect('toggled', self.on_qp_check_button_toggled)

                self.bitrate_check_button = Gtk.CheckButton(label='Bitrate')
                self.bitrate_check_button.set_group(self.crf_check_button)
                self.bitrate_check_button.connect('toggled', self.on_bitrate_check_button_toggled)

                self.rate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.rate_type_horizontal_box.append(self.crf_check_button)
                self.rate_type_horizontal_box.append(self.qp_check_button)
                self.rate_type_horizontal_box.append(self.bitrate_check_button)

            def _setup_rate_type_settings_row(self):
                self._setup_rate_type_settings_stack()

                self.rate_type_settings_row = Adw.ActionRow()
                self.rate_type_settings_row.set_title('CRF')
                self.rate_type_settings_row.set_subtitle('Constant Ratefactor')
                self.rate_type_settings_row.add_suffix(self.rate_type_stack)

            def _setup_rate_type_settings_stack(self):
                self._setup_crf_page()
                self._setup_qp_page()
                self._setup_bitrate_page()

                self.rate_type_stack = Gtk.Stack()
                self.rate_type_stack.add_named(self.crf_scale, 'crf_page')
                self.rate_type_stack.add_named(self.qp_scale, 'qp_page')
                self.rate_type_stack.add_named(self.bitrate_page_vertical_box, 'bitrate_page')
                self.rate_type_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

            def _setup_crf_page(self):
                self._setup_crf_gesture_click()
                self._setup_crf_event_controller_key()
                self._setup_crf_event_controller_scroll()

                self.crf_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                          min=video_codec.X265.CRF_MIN,
                                                          max=video_codec.X265.CRF_MAX,
                                                          step=1.0)
                self.crf_scale.set_value(20)
                self.crf_scale.set_digits(0)
                self.crf_scale.set_draw_value(True)
                self.crf_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.crf_scale.set_hexpand(True)
                self.crf_scale.add_controller(self.crf_gesture_click)
                self.crf_scale.add_controller(self.crf_event_controller_key)
                self.crf_scale.add_controller(self.crf_event_controller_scroll)

            def _setup_crf_gesture_click(self):
                self.crf_gesture_click = Gtk.GestureClick.new()
                self.crf_gesture_click.connect('stopped', self.on_scale_gesture_stopped, self.crf_gesture_click)
                self.crf_gesture_click.connect('unpaired-release', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_key(self):
                self.crf_event_controller_key = Gtk.EventControllerKey.new()
                self.crf_event_controller_key.connect('key-released', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_scroll(self):
                self.crf_event_controller_scroll = Gtk.EventControllerScroll.new(
                    Gtk.EventControllerScrollFlags.BOTH_AXES)
                self.crf_event_controller_scroll.connect('scroll', self.on_widget_changed_clicked_set)

            def _setup_qp_page(self):
                self._setup_qp_gesture_click()
                self._setup_qp_event_controller_key()
                self._setup_qp_event_controller_scroll()

                self.qp_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                         min=video_codec.X265.QP_MIN,
                                                         max=video_codec.X265.QP_MAX,
                                                         step=1.0)
                self.qp_scale.set_value(20)
                self.qp_scale.set_digits(0)
                self.qp_scale.set_draw_value(True)
                self.qp_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_scale.set_hexpand(True)
                self.qp_scale.add_controller(self.qp_gesture_click)
                self.qp_scale.add_controller(self.qp_event_controller_key)
                self.qp_scale.add_controller(self.qp_event_controller_scroll)

            def _setup_qp_gesture_click(self):
                self.qp_gesture_click = Gtk.GestureClick.new()
                self.qp_gesture_click.connect('stopped', self.on_scale_gesture_stopped, self.qp_gesture_click)
                self.qp_gesture_click.connect('unpaired-release', self.on_widget_changed_clicked_set)

            def _setup_qp_event_controller_key(self):
                self.qp_event_controller_key = Gtk.EventControllerKey.new()
                self.qp_event_controller_key.connect('key-released', self.on_widget_changed_clicked_set)

            def _setup_qp_event_controller_scroll(self):
                self.qp_event_controller_scroll = Gtk.EventControllerScroll.new(
                    Gtk.EventControllerScrollFlags.BOTH_AXES)
                self.qp_event_controller_scroll.connect('scroll', self.on_widget_changed_clicked_set)

            def _setup_bitrate_page(self):
                self._setup_bitrate_spin_button()
                self._setup_bitrate_type_widgets()

                self.bitrate_page_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.bitrate_page_vertical_box.append(self.bitrate_spin_button)
                self.bitrate_page_vertical_box.append(self.bitrate_type_horizontal_box)
                self.bitrate_page_vertical_box.set_margin_top(10)
                self.bitrate_page_vertical_box.set_margin_bottom(10)
                self.bitrate_page_vertical_box.set_hexpand(False)
                self.bitrate_page_vertical_box.set_halign(Gtk.Align.END)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(video_codec.X265.BITRATE_MIN, video_codec.X265.BITRATE_MAX)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(100, 500)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)
                self.bitrate_spin_button.set_value(2500)
                self.bitrate_spin_button.set_size_request(125, -1)
                self.bitrate_spin_button.set_vexpand(True)
                self.bitrate_spin_button.set_valign(Gtk.Align.END)
                self.bitrate_spin_button.set_hexpand(True)
                self.bitrate_spin_button.set_halign(Gtk.Align.CENTER)
                self.bitrate_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_bitrate_type_widgets(self):
                self.average_check_button = Gtk.CheckButton(label='Average')
                self.average_check_button.set_active(True)
                self.average_check_button.connect('toggled', self.on_bitrate_type_check_button_toggled)

                self.dual_pass_check_button = Gtk.CheckButton(label='2-Pass')
                self.dual_pass_check_button.set_group(self.average_check_button)
                self.dual_pass_check_button.connect('toggled', self.on_bitrate_type_check_button_toggled)

                self.bitrate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.bitrate_type_horizontal_box.append(self.average_check_button)
                self.bitrate_type_horizontal_box.append(self.dual_pass_check_button)
                self.bitrate_type_horizontal_box.set_vexpand(True)
                self.bitrate_type_horizontal_box.set_valign(Gtk.Align.START)

            def _setup_codec_advanced_settings(self):
                self._setup_vbv_maxrate_row()
                self._setup_vbv_bufsize_row()
                self._setup_aq_mode_row()
                self._setup_aq_strength_row()
                self._setup_hevc_aq_row()
                self._setup_keyint_row()
                self._setup_min_keyint_row()
                self._setup_ref_row()
                self._setup_b_frames_row()
                self._setup_b_adapt_row()
                self._setup_no_b_pyramid_row()
                self._setup_b_intra_row()
                self._setup_no_gop_row()
                self._setup_rc_lookahead_row()
                self._setup_no_scenecut_row()
                self._setup_no_high_tier_row()
                self._setup_psy_rd_row()
                self._setup_psy_rdoq_row()
                self._setup_me_row()
                self._setup_subme_row()
                self._setup_weight_b_row()
                self._setup_no_weight_p_row()
                self._setup_deblock_row()
                self._setup_no_sao_row()
                self._setup_sao_non_deblock_row()
                self._setup_limit_sao_row()
                self._setup_selective_sao_row()
                self._setup_rd_row()
                self._setup_rdoq_level_row()
                self._setup_rd_refine_row()
                self._setup_max_cu_size_row()
                self._setup_min_cu_size_row()
                self._setup_rect_row()
                self._setup_amp_row()
                self._setup_wpp_row()
                self._setup_pmode_row()
                self._setup_pme_row()
                self._setup_uhd_bd_row()

                self.advanced_settings_switch = Gtk.Switch()
                self.advanced_settings_switch.set_vexpand(False)
                self.advanced_settings_switch.set_valign(Gtk.Align.CENTER)
                self.advanced_settings_switch.connect('state-set', self.on_advanced_settings_switch_state_set)

                self.advanced_settings_group = Adw.PreferencesGroup()
                self.advanced_settings_group.set_title('Advanced Settings')
                self.advanced_settings_group.set_header_suffix(self.advanced_settings_switch)
                self.advanced_settings_group.add(self.vbv_maxrate_row)
                self.advanced_settings_group.add(self.vbv_bufsize_row)
                self.advanced_settings_group.add(self.keyint_row)
                self.advanced_settings_group.add(self.min_keyint_row)
                self.advanced_settings_group.add(self.ref_row)
                self.advanced_settings_group.add(self.b_frames_row)
                self.advanced_settings_group.add(self.b_adapt_row)
                self.advanced_settings_group.add(self.no_b_pyramid_row)
                self.advanced_settings_group.add(self.b_intra_row)
                self.advanced_settings_group.add(self.weight_b_row)
                self.advanced_settings_group.add(self.no_weight_p_row)
                self.advanced_settings_group.add(self.no_high_tier_row)
                self.advanced_settings_group.add(self.no_gop_row)
                self.advanced_settings_group.add(self.no_scenecut_row)
                self.advanced_settings_group.add(self.me_row)
                self.advanced_settings_group.add(self.subme_row)
                self.advanced_settings_group.add(self.deblock_row)
                self.advanced_settings_group.add(self.aq_mode_row)
                self.advanced_settings_group.add(self.aq_strength_row)
                self.advanced_settings_group.add(self.hevc_aq_row)
                self.advanced_settings_group.add(self.rc_lookahead_row)
                self.advanced_settings_group.add(self.psy_rd_row)
                self.advanced_settings_group.add(self.psy_rdoq_row)
                self.advanced_settings_group.add(self.rd_row)
                self.advanced_settings_group.add(self.rd_refine_row)
                self.advanced_settings_group.add(self.rdoq_level_row)
                self.advanced_settings_group.add(self.no_sao_row)
                self.advanced_settings_group.add(self.limit_sao_row)
                self.advanced_settings_group.add(self.sao_non_deblock_row)
                self.advanced_settings_group.add(self.selective_sao_row)
                self.advanced_settings_group.add(self.min_cu_size_row)
                self.advanced_settings_group.add(self.max_cu_size_row)
                self.advanced_settings_group.add(self.rect_row)
                self.advanced_settings_group.add(self.amp_row)
                self.advanced_settings_group.add(self.wpp_row)
                self.advanced_settings_group.add(self.pmode_row)
                self.advanced_settings_group.add(self.pme_row)
                self.advanced_settings_group.add(self.uhd_bd_row)

            def _setup_vbv_maxrate_row(self):
                self._setup_vbv_maxrate_spin_button()

                self.vbv_maxrate_row = Adw.ActionRow()
                self.vbv_maxrate_row.set_title('VBV Max Rate')
                self.vbv_maxrate_row.set_subtitle('Maximum local bitrate in kbps')
                self.vbv_maxrate_row.add_suffix(self.vbv_maxrate_spin_button)
                self.vbv_maxrate_row.set_sensitive(False)

            def _setup_vbv_maxrate_spin_button(self):
                self.vbv_maxrate_spin_button = Gtk.SpinButton()
                self.vbv_maxrate_spin_button.set_range(video_codec.X265.BITRATE_MIN, video_codec.X265.BITRATE_MAX)
                self.vbv_maxrate_spin_button.set_digits(0)
                self.vbv_maxrate_spin_button.set_increments(100, 500)
                self.vbv_maxrate_spin_button.set_numeric(True)
                self.vbv_maxrate_spin_button.set_snap_to_ticks(True)
                self.vbv_maxrate_spin_button.set_value(2500)
                self.vbv_maxrate_spin_button.set_size_request(125, -1)
                self.vbv_maxrate_spin_button.set_vexpand(False)
                self.vbv_maxrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.vbv_maxrate_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_vbv_bufsize_row(self):
                self._setup_vbv_bufsize_spin_button()

                self.vbv_bufsize_row = Adw.ActionRow()
                self.vbv_bufsize_row.set_title('VBV Bufsize')
                self.vbv_bufsize_row.set_subtitle('Size of the VBV buffer in kb')
                self.vbv_bufsize_row.add_suffix(self.vbv_bufsize_spin_button)
                self.vbv_bufsize_row.set_sensitive(False)

            def _setup_vbv_bufsize_spin_button(self):
                self.vbv_bufsize_spin_button = Gtk.SpinButton()
                self.vbv_bufsize_spin_button.set_range(video_codec.X265.BITRATE_MIN, video_codec.X265.BITRATE_MAX)
                self.vbv_bufsize_spin_button.set_digits(0)
                self.vbv_bufsize_spin_button.set_increments(100, 500)
                self.vbv_bufsize_spin_button.set_numeric(True)
                self.vbv_bufsize_spin_button.set_snap_to_ticks(True)
                self.vbv_bufsize_spin_button.set_value(2500)
                self.vbv_bufsize_spin_button.set_size_request(125, -1)
                self.vbv_bufsize_spin_button.set_vexpand(False)
                self.vbv_bufsize_spin_button.set_valign(Gtk.Align.CENTER)
                self.vbv_bufsize_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_aq_mode_row(self):
                self._setup_aq_mode_string_list()

                self.aq_mode_row = Adw.ComboRow()
                self.aq_mode_row.set_title('AQ Mode')
                self.aq_mode_row.set_subtitle('Adaptive quantization operating mode')
                self.aq_mode_row.set_model(self.aq_mode_string_list)
                self.aq_mode_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.aq_mode_row.set_sensitive(False)

            def _setup_aq_mode_string_list(self):
                self.aq_mode_string_list = Gtk.StringList.new(video_codec.X265.AQ_MODE_UI)

            def _setup_aq_strength_row(self):
                self._setup_aq_strength_spin_button()

                self.aq_strength_row = Adw.ActionRow()
                self.aq_strength_row.set_title('AQ Strength')
                self.aq_strength_row.set_subtitle('Strength of the adaptive quantization offsets')
                self.aq_strength_row.add_suffix(self.aq_strength_spin_button)
                self.aq_strength_row.set_sensitive(False)

            def _setup_aq_strength_spin_button(self):
                self.aq_strength_spin_button = Gtk.SpinButton()
                self.aq_strength_spin_button.set_range(video_codec.X265.AQ_STRENGTH_MIN,
                                                       video_codec.X265.AQ_STRENGTH_MAX)
                self.aq_strength_spin_button.set_digits(1)
                self.aq_strength_spin_button.set_increments(0.1, 0.5)
                self.aq_strength_spin_button.set_numeric(True)
                self.aq_strength_spin_button.set_snap_to_ticks(True)
                self.aq_strength_spin_button.set_value(1.0)
                self.aq_strength_spin_button.set_vexpand(False)
                self.aq_strength_spin_button.set_valign(Gtk.Align.CENTER)
                self.aq_strength_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_hevc_aq_row(self):
                self._setup_hevc_aq_switch()

                self.hevc_aq_row = Adw.ActionRow()
                self.hevc_aq_row.set_title('HEVC AQ')
                self.hevc_aq_row.set_subtitle(
                    'Adaptive quantization that scales the quantization step size to spatial activity')
                self.hevc_aq_row.add_suffix(self.hevc_aq_switch)
                self.hevc_aq_row.set_sensitive(False)

            def _setup_hevc_aq_switch(self):
                self.hevc_aq_switch = Gtk.Switch()
                self.hevc_aq_switch.set_vexpand(False)
                self.hevc_aq_switch.set_valign(Gtk.Align.CENTER)
                self.hevc_aq_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_keyint_row(self):
                self._setup_keyint_spin_button()

                self.keyint_row = Adw.ActionRow()
                self.keyint_row.set_title('Keyframe Interval')
                self.keyint_row.set_subtitle('Maximum intra period in frames')
                self.keyint_row.add_suffix(self.keyint_spin_button)
                self.keyint_row.set_sensitive(False)

            def _setup_keyint_spin_button(self):
                self.keyint_spin_button = Gtk.SpinButton()
                self.keyint_spin_button.set_range(video_codec.X265.KEYINT_MIN, video_codec.X265.KEYINT_MAX)
                self.keyint_spin_button.set_digits(0)
                self.keyint_spin_button.set_increments(10, 50)
                self.keyint_spin_button.set_numeric(True)
                self.keyint_spin_button.set_snap_to_ticks(True)
                self.keyint_spin_button.set_value(240)
                self.keyint_spin_button.set_vexpand(False)
                self.keyint_spin_button.set_valign(Gtk.Align.CENTER)
                self.keyint_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_min_keyint_row(self):
                self._setup_min_keyint_spin_button()

                self.min_keyint_row = Adw.ActionRow()
                self.min_keyint_row.set_title('Min Keyframe Interval')
                self.min_keyint_row.set_subtitle('Minimum GOP size')
                self.min_keyint_row.add_suffix(self.min_keyint_spin_button)
                self.min_keyint_row.set_sensitive(False)

            def _setup_min_keyint_spin_button(self):
                self.min_keyint_spin_button = Gtk.SpinButton()
                self.min_keyint_spin_button.set_range(video_codec.X265.MIN_KEYINT_MIN, video_codec.X265.MIN_KEYINT_MAX)
                self.min_keyint_spin_button.set_digits(0)
                self.min_keyint_spin_button.set_increments(10, 50)
                self.min_keyint_spin_button.set_numeric(True)
                self.min_keyint_spin_button.set_snap_to_ticks(True)
                self.min_keyint_spin_button.set_value(24)
                self.min_keyint_spin_button.set_vexpand(False)
                self.min_keyint_spin_button.set_valign(Gtk.Align.CENTER)
                self.min_keyint_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_ref_row(self):
                self._setup_ref_spin_button()

                self.ref_row = Adw.ActionRow()
                self.ref_row.set_title('Reference Frames')
                self.ref_row.set_subtitle('Maximum number of L0 references')
                self.ref_row.add_suffix(self.ref_spin_button)
                self.ref_row.set_sensitive(False)

            def _setup_ref_spin_button(self):
                self.ref_spin_button = Gtk.SpinButton()
                self.ref_spin_button.set_range(video_codec.X265.REFS_MIN, video_codec.X265.REFS_MAX)
                self.ref_spin_button.set_digits(0)
                self.ref_spin_button.set_increments(1, 5)
                self.ref_spin_button.set_numeric(True)
                self.ref_spin_button.set_snap_to_ticks(True)
                self.ref_spin_button.set_value(3)
                self.ref_spin_button.set_vexpand(False)
                self.ref_spin_button.set_valign(Gtk.Align.CENTER)
                self.ref_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_b_frames_row(self):
                self._setup_b_frames_spin_button()

                self.b_frames_row = Adw.ActionRow()
                self.b_frames_row.set_title('B-Frames')
                self.b_frames_row.set_subtitle('Maximum number of consecutive B-frames')
                self.b_frames_row.add_suffix(self.b_frames_spin_button)
                self.b_frames_row.set_sensitive(False)

            def _setup_b_frames_spin_button(self):
                self.b_frames_spin_button = Gtk.SpinButton()
                self.b_frames_spin_button.set_range(video_codec.X265.REFS_MIN, video_codec.X265.REFS_MAX)
                self.b_frames_spin_button.set_digits(0)
                self.b_frames_spin_button.set_increments(1, 5)
                self.b_frames_spin_button.set_numeric(True)
                self.b_frames_spin_button.set_snap_to_ticks(True)
                self.b_frames_spin_button.set_value(3)
                self.b_frames_spin_button.set_vexpand(False)
                self.b_frames_spin_button.set_valign(Gtk.Align.CENTER)
                self.b_frames_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_b_adapt_row(self):
                self._setup_b_adapt_string_list()

                self.b_adapt_row = Adw.ComboRow()
                self.b_adapt_row.set_title('B-adapt')
                self.b_adapt_row.set_subtitle('Level of optimization to place B-frames')
                self.b_adapt_row.set_model(self.b_adapt_string_list)
                self.b_adapt_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.b_adapt_row.set_sensitive(False)

            def _setup_b_adapt_string_list(self):
                self.b_adapt_string_list = Gtk.StringList.new(video_codec.X265.B_ADAPT_UI)

            def _setup_no_b_pyramid_row(self):
                self._setup_no_b_pyramid_switch()

                self.no_b_pyramid_row = Adw.ActionRow()
                self.no_b_pyramid_row.set_title('No B-pyramid')
                self.no_b_pyramid_row.set_subtitle('Disables B-frames as references')
                self.no_b_pyramid_row.add_suffix(self.no_b_pyramid_switch)
                self.no_b_pyramid_row.set_sensitive(False)

            def _setup_no_b_pyramid_switch(self):
                self.no_b_pyramid_switch = Gtk.Switch()
                self.no_b_pyramid_switch.set_vexpand(False)
                self.no_b_pyramid_switch.set_valign(Gtk.Align.CENTER)
                self.no_b_pyramid_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_b_intra_row(self):
                self._setup_b_intra_switch()

                self.b_intra_row = Adw.ActionRow()
                self.b_intra_row.set_title('B-Intra')
                self.b_intra_row.set_subtitle('Evaluation of intra modes in B slices')
                self.b_intra_row.add_suffix(self.b_intra_switch)
                self.b_intra_row.set_sensitive(False)

            def _setup_b_intra_switch(self):
                self.b_intra_switch = Gtk.Switch()
                self.b_intra_switch.set_vexpand(False)
                self.b_intra_switch.set_valign(Gtk.Align.CENTER)
                self.b_intra_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_no_gop_row(self):
                self._setup_no_gop_switch()

                self.no_gop_row = Adw.ActionRow()
                self.no_gop_row.set_title('No Open GOP')
                self.no_gop_row.set_subtitle('Disables I-slices to be non-IDR')
                self.no_gop_row.add_suffix(self.no_gop_switch)
                self.no_gop_row.set_sensitive(False)

            def _setup_no_gop_switch(self):
                self.no_gop_switch = Gtk.Switch()
                self.no_gop_switch.set_vexpand(False)
                self.no_gop_switch.set_valign(Gtk.Align.CENTER)
                self.no_gop_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_rc_lookahead_row(self):
                self._setup_rc_lookahead_spin_button()

                self.rc_lookahead_row = Adw.ActionRow()
                self.rc_lookahead_row.set_title('RC Lookahead')
                self.rc_lookahead_row.set_subtitle('Lookahead for slice-type decisions in frames')
                self.rc_lookahead_row.add_suffix(self.rc_lookahead_spin_button)
                self.rc_lookahead_row.set_sensitive(False)

            def _setup_rc_lookahead_spin_button(self):
                self.rc_lookahead_spin_button = Gtk.SpinButton()
                self.rc_lookahead_spin_button.set_range(video_codec.X265.RC_LOOKAHEAD_MIN,
                                                        video_codec.X265.RC_LOOKAHEAD_MAX)
                self.rc_lookahead_spin_button.set_digits(0)
                self.rc_lookahead_spin_button.set_increments(10, 50)
                self.rc_lookahead_spin_button.set_numeric(True)
                self.rc_lookahead_spin_button.set_snap_to_ticks(True)
                self.rc_lookahead_spin_button.set_value(20)
                self.rc_lookahead_spin_button.set_vexpand(False)
                self.rc_lookahead_spin_button.set_valign(Gtk.Align.CENTER)
                self.rc_lookahead_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_no_scenecut_row(self):
                self._setup_no_scenecut_switch()

                self.no_scenecut_row = Adw.ActionRow()
                self.no_scenecut_row.set_title('No Scenecut')
                self.no_scenecut_row.set_subtitle('Disabled adaptive I-frame placement')
                self.no_scenecut_row.add_suffix(self.no_scenecut_switch)
                self.no_scenecut_row.set_sensitive(False)

            def _setup_no_scenecut_switch(self):
                self.no_scenecut_switch = Gtk.Switch()
                self.no_scenecut_switch.set_vexpand(False)
                self.no_scenecut_switch.set_valign(Gtk.Align.CENTER)
                self.no_scenecut_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_no_high_tier_row(self):
                self._setup_no_high_tier_switch()

                self.no_high_tier_row = Adw.ActionRow()
                self.no_high_tier_row.set_title('No High Tier')
                self.no_high_tier_row.set_subtitle('Allow high tier at encoder level when necessary')
                self.no_high_tier_row.add_suffix(self.no_high_tier_switch)
                self.no_high_tier_row.set_sensitive(False)

            def _setup_no_high_tier_switch(self):
                self.no_high_tier_switch = Gtk.Switch()
                self.no_high_tier_switch.set_vexpand(False)
                self.no_high_tier_switch.set_valign(Gtk.Align.CENTER)
                self.no_high_tier_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_psy_rd_row(self):
                self._setup_psy_rd_spin_button()

                self.psy_rd_row = Adw.ActionRow()
                self.psy_rd_row.set_title('PsyRD')
                self.psy_rd_row.set_subtitle('Bias RDO to preserve energy from source image')
                self.psy_rd_row.add_suffix(self.psy_rd_spin_button)
                self.psy_rd_row.set_sensitive(False)

            def _setup_psy_rd_spin_button(self):
                self.psy_rd_spin_button = Gtk.SpinButton()
                self.psy_rd_spin_button.set_range(video_codec.X265.PSY_RD_MIN, video_codec.X265.PSY_RD_MAX)
                self.psy_rd_spin_button.set_digits(1)
                self.psy_rd_spin_button.set_increments(.1, .5)
                self.psy_rd_spin_button.set_numeric(True)
                self.psy_rd_spin_button.set_snap_to_ticks(True)
                self.psy_rd_spin_button.set_value(2.0)
                self.psy_rd_spin_button.set_vexpand(False)
                self.psy_rd_spin_button.set_valign(Gtk.Align.CENTER)
                self.psy_rd_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_psy_rdoq_row(self):
                self._setup_psy_rdoq_spin_button()

                self.psy_rdoq_row = Adw.ActionRow()
                self.psy_rdoq_row.set_title('Psy RDOQ')
                self.psy_rdoq_row.set_subtitle('Bias RDOQ towards higher energy in the reconstructed image')
                self.psy_rdoq_row.add_suffix(self.psy_rdoq_spin_button)
                self.psy_rdoq_row.set_sensitive(False)

            def _setup_psy_rdoq_spin_button(self):
                self.psy_rdoq_spin_button = Gtk.SpinButton()
                self.psy_rdoq_spin_button.set_range(video_codec.X265.PSY_RDOQ_MIN, video_codec.X265.PSY_RDOQ_MAX)
                self.psy_rdoq_spin_button.set_digits(1)
                self.psy_rdoq_spin_button.set_increments(.1, .5)
                self.psy_rdoq_spin_button.set_numeric(True)
                self.psy_rdoq_spin_button.set_snap_to_ticks(True)
                self.psy_rdoq_spin_button.set_value(2.0)
                self.psy_rdoq_spin_button.set_vexpand(False)
                self.psy_rdoq_spin_button.set_valign(Gtk.Align.CENTER)
                self.psy_rdoq_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_me_row(self):
                self._setup_me_string_list()

                self.me_row = Adw.ComboRow()
                self.me_row.set_title('Motion Estimation')
                self.me_row.set_subtitle('Motion search complexity method to use')
                self.me_row.set_model(self.me_string_list)
                self.me_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.me_row.set_sensitive(False)

            def _setup_me_string_list(self):
                self.me_string_list = Gtk.StringList.new(video_codec.X265.ME)

            def _setup_subme_row(self):
                self._setup_subme_spin_button()

                self.subme_row = Adw.ActionRow()
                self.subme_row.set_title('Sub-Motion Estimation')
                self.subme_row.set_subtitle('Amount of subpel refinement to perform')
                self.subme_row.add_suffix(self.subme_spin_button)
                self.subme_row.set_sensitive(False)

            def _setup_subme_spin_button(self):
                self.subme_spin_button = Gtk.SpinButton()
                self.subme_spin_button.set_range(video_codec.X265.SUBME_MIN, video_codec.X265.SUBME_MAX)
                self.subme_spin_button.set_digits(0)
                self.subme_spin_button.set_increments(1, 5)
                self.subme_spin_button.set_numeric(True)
                self.subme_spin_button.set_snap_to_ticks(True)
                self.subme_spin_button.set_value(2)
                self.subme_spin_button.set_vexpand(False)
                self.subme_spin_button.set_valign(Gtk.Align.CENTER)
                self.subme_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_weight_b_row(self):
                self._setup_weight_b_switch()

                self.weight_b_row = Adw.ActionRow()
                self.weight_b_row.set_title('Weight-B')
                self.weight_b_row.set_subtitle('Enable weighted prediction in B slices')
                self.weight_b_row.add_suffix(self.weight_b_switch)
                self.weight_b_row.set_sensitive(False)

            def _setup_weight_b_switch(self):
                self.weight_b_switch = Gtk.Switch()
                self.weight_b_switch.set_vexpand(False)
                self.weight_b_switch.set_valign(Gtk.Align.CENTER)
                self.weight_b_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_no_weight_p_row(self):
                self._setup_no_weight_p_switch()

                self.no_weight_p_row = Adw.ActionRow()
                self.no_weight_p_row.set_title('No Weight-P')
                self.no_weight_p_row.set_subtitle('Disable weighted prediction in P slices')
                self.no_weight_p_row.add_suffix(self.no_weight_p_switch)
                self.no_weight_p_row.set_sensitive(False)

            def _setup_no_weight_p_switch(self):
                self.no_weight_p_switch = Gtk.Switch()
                self.no_weight_p_switch.set_vexpand(False)
                self.no_weight_p_switch.set_valign(Gtk.Align.CENTER)
                self.no_weight_p_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_deblock_row(self):
                self._setup_no_deblock_check_button()
                self._setup_deblock_strength_widgets()

                deblock_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                deblock_horizontal_box.append(self.no_deblock_check_button)
                deblock_horizontal_box.append(self.deblock_strength_vertical_box)
                deblock_horizontal_box.set_margin_top(10)
                deblock_horizontal_box.set_margin_bottom(10)

                self.deblock_row = Adw.ActionRow()
                self.deblock_row.set_title('Deblock')
                self.deblock_row.set_subtitle('Deblocking loop filter strength offsets')
                self.deblock_row.add_suffix(deblock_horizontal_box)
                self.deblock_row.set_sensitive(False)

            def _setup_no_deblock_check_button(self):
                self.no_deblock_check_button = Gtk.CheckButton(label='No Deblock')
                self.no_deblock_check_button.connect('toggled', self.on_non_deblock_check_button_toggled)

            def _setup_deblock_strength_widgets(self):
                self.deblock_alpha_spin_button = Gtk.SpinButton()
                self.deblock_alpha_spin_button.set_range(video_codec.X265.DEBLOCK_MIN, video_codec.X265.DEBLOCK_MAX)
                self.deblock_alpha_spin_button.set_digits(0)
                self.deblock_alpha_spin_button.set_increments(1, 5)
                self.deblock_alpha_spin_button.set_numeric(True)
                self.deblock_alpha_spin_button.set_snap_to_ticks(True)
                self.deblock_alpha_spin_button.set_value(0)
                self.deblock_alpha_spin_button.set_vexpand(False)
                self.deblock_alpha_spin_button.set_valign(Gtk.Align.CENTER)
                self.deblock_alpha_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

                self.deblock_beta_spin_button = Gtk.SpinButton()
                self.deblock_beta_spin_button.set_range(video_codec.X265.DEBLOCK_MIN, video_codec.X265.DEBLOCK_MAX)
                self.deblock_beta_spin_button.set_digits(0)
                self.deblock_beta_spin_button.set_increments(1, 5)
                self.deblock_beta_spin_button.set_numeric(True)
                self.deblock_beta_spin_button.set_snap_to_ticks(True)
                self.deblock_beta_spin_button.set_value(0)
                self.deblock_beta_spin_button.set_vexpand(False)
                self.deblock_beta_spin_button.set_valign(Gtk.Align.CENTER)
                self.deblock_beta_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

                self.deblock_strength_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                self.deblock_strength_vertical_box.append(self.deblock_alpha_spin_button)
                self.deblock_strength_vertical_box.append(self.deblock_beta_spin_button)

            def _setup_no_sao_row(self):
                self._setup_no_sao_switch()

                self.no_sao_row = Adw.ActionRow()
                self.no_sao_row.set_title('No SAO')
                self.no_sao_row.set_subtitle('Whether non-deblocked pixels are used for SAO analysis')
                self.no_sao_row.add_suffix(self.no_sao_switch)
                self.no_sao_row.set_sensitive(False)

            def _setup_no_sao_switch(self):
                self.no_sao_switch = Gtk.Switch()
                self.no_sao_switch.set_vexpand(False)
                self.no_sao_switch.set_valign(Gtk.Align.CENTER)
                self.no_sao_switch.connect('state-set', self.on_no_sao_switch_state_set)

            def _setup_sao_non_deblock_row(self):
                self._setup_sao_non_deblock_switch()

                self.sao_non_deblock_row = Adw.ActionRow()
                self.sao_non_deblock_row.set_title('SAO Non-Deblock')
                self.sao_non_deblock_row.set_subtitle('SAO Non-Deblock')
                self.sao_non_deblock_row.add_suffix(self.sao_non_deblock_switch)
                self.sao_non_deblock_row.set_sensitive(False)

            def _setup_sao_non_deblock_switch(self):
                self.sao_non_deblock_switch = Gtk.Switch()
                self.sao_non_deblock_switch.set_vexpand(False)
                self.sao_non_deblock_switch.set_valign(Gtk.Align.CENTER)
                self.sao_non_deblock_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_limit_sao_row(self):
                self._setup_limit_sao_switch()

                self.limit_sao_row = Adw.ActionRow()
                self.limit_sao_row.set_title('Limit SAO')
                self.limit_sao_row.set_subtitle('Early terminates SAO process based on inter prediction mode')
                self.limit_sao_row.add_suffix(self.limit_sao_switch)
                self.limit_sao_row.set_sensitive(False)

            def _setup_limit_sao_switch(self):
                self.limit_sao_switch = Gtk.Switch()
                self.limit_sao_switch.set_vexpand(False)
                self.limit_sao_switch.set_valign(Gtk.Align.CENTER)
                self.limit_sao_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_selective_sao_row(self):
                self._setup_selective_sao_spin_button()

                self.selective_sao_row = Adw.ActionRow()
                self.selective_sao_row.set_title('Selective SAO')
                self.selective_sao_row.set_subtitle('Enables SAO at the slice level')
                self.selective_sao_row.add_suffix(self.selective_sao_spin_button)
                self.selective_sao_row.set_sensitive(False)

            def _setup_selective_sao_spin_button(self):
                self.selective_sao_spin_button = Gtk.SpinButton()
                self.selective_sao_spin_button.set_range(video_codec.X265.SELECTIVE_SAO_MIN,
                                                         video_codec.X265.SELECTIVE_SAO_MAX)
                self.selective_sao_spin_button.set_digits(0)
                self.selective_sao_spin_button.set_increments(1, 5)
                self.selective_sao_spin_button.set_numeric(True)
                self.selective_sao_spin_button.set_snap_to_ticks(True)
                self.selective_sao_spin_button.set_value(0)
                self.selective_sao_spin_button.set_vexpand(False)
                self.selective_sao_spin_button.set_valign(Gtk.Align.CENTER)
                self.selective_sao_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_rd_row(self):
                self._setup_rd_spin_button()

                self.rd_row = Adw.ActionRow()
                self.rd_row.set_title('Rate Distortion')
                self.rd_row.set_subtitle('Level of RDO in mode decision')
                self.rd_row.add_suffix(self.rd_spin_button)
                self.rd_row.set_sensitive(False)

            def _setup_rd_spin_button(self):
                self.rd_spin_button = Gtk.SpinButton()
                self.rd_spin_button.set_range(video_codec.X265.RD_MIN, video_codec.X265.RD_MAX)
                self.rd_spin_button.set_digits(0)
                self.rd_spin_button.set_increments(1, 5)
                self.rd_spin_button.set_numeric(True)
                self.rd_spin_button.set_snap_to_ticks(True)
                self.rd_spin_button.set_value(0)
                self.rd_spin_button.set_vexpand(False)
                self.rd_spin_button.set_valign(Gtk.Align.CENTER)
                self.rd_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_rdoq_level_row(self):
                self._setup_rdoq_level_string_list()

                self.rdoq_level_row = Adw.ComboRow()
                self.rdoq_level_row.set_title('RDOQ Level')
                self.rdoq_level_row.set_subtitle('Amount of rate-distortion analysis to use within quantization')
                self.rdoq_level_row.set_model(self.rdoq_level_string_list)
                self.rdoq_level_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.rdoq_level_row.set_sensitive(False)

            def _setup_rdoq_level_string_list(self):
                self.rdoq_level_string_list = Gtk.StringList.new(video_codec.X265.RDOQ_LEVEL_UI)

            def _setup_rd_refine_row(self):
                self._setup_rd_refine_switch()

                self.rd_refine_row = Adw.ActionRow()
                self.rd_refine_row.set_title('Rate Distortion Refine')
                self.rd_refine_row.set_subtitle('Calculate R-D cost on the best partition mode for each analysed CU')
                self.rd_refine_row.add_suffix(self.rd_refine_switch)
                self.rd_refine_row.set_sensitive(False)

            def _setup_rd_refine_switch(self):
                self.rd_refine_switch = Gtk.Switch()
                self.rd_refine_switch.set_vexpand(False)
                self.rd_refine_switch.set_valign(Gtk.Align.CENTER)
                self.rd_refine_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_max_cu_size_row(self):
                self._setup_max_cu_size_string_list()

                self.max_cu_size_row = Adw.ComboRow()
                self.max_cu_size_row.set_title('Max CU Size')
                self.max_cu_size_row.set_subtitle('Larger CU threshold is considered')
                self.max_cu_size_row.set_model(self.max_cu_size_string_list)
                self.max_cu_size_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.max_cu_size_row.set_sensitive(False)

            def _setup_max_cu_size_string_list(self):
                self.max_cu_size_string_list = Gtk.StringList.new(video_codec.X265.MAX_CU_SIZE)

            def _setup_min_cu_size_row(self):
                self._setup_min_cu_size_string_list()

                self.min_cu_size_row = Adw.ComboRow()
                self.min_cu_size_row.set_title('Min CU Size')
                self.min_cu_size_row.set_subtitle('Cost of CUs below minimum threshold not considered')
                self.min_cu_size_row.set_model(self.min_cu_size_string_list)
                self.min_cu_size_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.min_cu_size_row.set_sensitive(False)

            def _setup_min_cu_size_string_list(self):
                self.min_cu_size_string_list = Gtk.StringList.new(video_codec.X265.MIN_CU_SIZE)

            def _setup_rect_row(self):
                self._setup_rect_switch()

                self.rect_row = Adw.ActionRow()
                self.rect_row.set_title('Rect')
                self.rect_row.set_subtitle('Analysis of rectangular motion partitions')
                self.rect_row.add_suffix(self.rect_switch)
                self.rect_row.set_sensitive(False)

            def _setup_rect_switch(self):
                self.rect_switch = Gtk.Switch()
                self.rect_switch.set_vexpand(False)
                self.rect_switch.set_valign(Gtk.Align.CENTER)
                self.rect_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_amp_row(self):
                self._setup_amp_switch()

                self.amp_row = Adw.ActionRow()
                self.amp_row.set_title('AMP')
                self.amp_row.set_subtitle('Analysis of asymmetric motion partitions')
                self.amp_row.add_suffix(self.amp_switch)
                self.amp_row.set_sensitive(False)

            def _setup_amp_switch(self):
                self.amp_switch = Gtk.Switch()
                self.amp_switch.set_vexpand(False)
                self.amp_switch.set_valign(Gtk.Align.CENTER)
                self.amp_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_wpp_row(self):
                self._setup_wpp_switch()

                self.wpp_row = Adw.ActionRow()
                self.wpp_row.set_title('WPP')
                self.wpp_row.set_subtitle('Wavefront parallel processing')
                self.wpp_row.add_suffix(self.wpp_switch)
                self.wpp_row.set_sensitive(False)

            def _setup_wpp_switch(self):
                self.wpp_switch = Gtk.Switch()
                self.wpp_switch.set_vexpand(False)
                self.wpp_switch.set_valign(Gtk.Align.CENTER)
                self.wpp_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_pmode_row(self):
                self._setup_pmode_switch()

                self.pmode_row = Adw.ActionRow()
                self.pmode_row.set_title('PMode')
                self.pmode_row.set_subtitle('Parallel mode decision')
                self.pmode_row.add_suffix(self.pmode_switch)
                self.pmode_row.set_sensitive(False)

            def _setup_pmode_switch(self):
                self.pmode_switch = Gtk.Switch()
                self.pmode_switch.set_vexpand(False)
                self.pmode_switch.set_valign(Gtk.Align.CENTER)
                self.pmode_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_pme_row(self):
                self._setup_pme_switch()

                self.pme_row = Adw.ActionRow()
                self.pme_row.set_title('PME')
                self.pme_row.set_subtitle('Parallel motion estimation')
                self.pme_row.add_suffix(self.pme_switch)
                self.pme_row.set_sensitive(False)

            def _setup_pme_switch(self):
                self.pme_switch = Gtk.Switch()
                self.pme_switch.set_vexpand(False)
                self.pme_switch.set_valign(Gtk.Align.CENTER)
                self.pme_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_uhd_bd_row(self):
                self._setup_uhd_bd_switch()

                self.uhd_bd_row = Adw.ActionRow()
                self.uhd_bd_row.set_title('UHD BD')
                self.uhd_bd_row.set_subtitle('Ultra HD Blu-ray format support')
                self.uhd_bd_row.add_suffix(self.uhd_bd_switch)
                self.uhd_bd_row.set_sensitive(False)

            def _setup_uhd_bd_switch(self):
                self.uhd_bd_switch = Gtk.Switch()
                self.uhd_bd_switch.set_vexpand(False)
                self.uhd_bd_switch.set_valign(Gtk.Align.CENTER)
                self.uhd_bd_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def set_widgets_setting_up(self, is_widgets_setting_up: bool):
                self.is_widgets_setting_up = is_widgets_setting_up

            def set_vbv_state(self, is_vbv_state_enabled: bool):
                if self.advanced_settings_switch.get_active():
                    self.vbv_maxrate_row.set_sensitive(is_vbv_state_enabled)
                    self.vbv_bufsize_row.set_sensitive(is_vbv_state_enabled)
                else:
                    self.vbv_maxrate_row.set_sensitive(False)
                    self.vbv_bufsize_row.set_sensitive(False)

            def apply_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.set_widgets_setting_up, True)
                self._apply_preset_setting_to_widgets(encode_task)
                self._apply_profile_setting_to_widgets(encode_task)
                self._apply_level_setting_to_widgets(encode_task)
                self._apply_tune_setting_to_widgets(encode_task)
                self._apply_rate_type_settings_to_widgets(encode_task)
                self._apply_crf_setting_to_widgets(encode_task)
                self._apply_qp_setting_to_widgets(encode_task)
                self._apply_bitrate_type_settings_to_widgets(encode_task)
                self._apply_advanced_settings_to_widgets(encode_task)
                GLib.idle_add(self.set_widgets_setting_up, False)

            def _apply_preset_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.preset_row.set_selected, encode_task.get_video_codec().preset)

            def _apply_profile_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.profile_row.set_selected, encode_task.get_video_codec().profile)

            def _apply_level_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.level_row.set_selected, encode_task.get_video_codec().level)

            def _apply_tune_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.tune_row.set_selected, encode_task.get_video_codec().tune)

            def _apply_rate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_crf_enabled:
                    GLib.idle_add(self.crf_check_button.set_active, True)
                elif encode_task.get_video_codec().is_qp_enabled:
                    GLib.idle_add(self.qp_check_button.set_active, True)
                else:
                    GLib.idle_add(self.bitrate_check_button.set_active, True)

            def _apply_crf_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.crf_scale.set_value, encode_task.get_video_codec().crf)

            def _apply_qp_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.qp_scale.set_value, encode_task.get_video_codec().qp)

            def _apply_bitrate_type_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.bitrate_spin_button.set_value, encode_task.get_video_codec().bitrate)

            def _apply_advanced_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.advanced_settings_switch.set_active,
                              encode_task.get_video_codec().is_advanced_enabled)
                self._apply_vbv_maxrate_setting_to_widgets(encode_task)
                self._apply_vbv_bufsize_setting_to_widgets(encode_task)
                self._apply_aq_mode_setting_to_widgets(encode_task)
                self._apply_aq_strength_setting_to_widgets(encode_task)
                self._apply_hevc_aq_setting_to_widgets(encode_task)
                self._apply_keyint_setting_to_widgets(encode_task)
                self._apply_min_keyint_setting_to_widgets(encode_task)
                self._apply_ref_setting_to_widgets(encode_task)
                self._apply_b_frames_setting_to_widgets(encode_task)
                self._apply_b_adapt_setting_to_widgets(encode_task)
                self._apply_no_b_pyramid_setting_to_widgets(encode_task)
                self._apply_b_intra_setting_to_widgets(encode_task)
                self._apply_no_gop_setting_to_widgets(encode_task)
                self._apply_rc_lookahead_setting_to_widgets(encode_task)
                self._apply_no_scenecut_setting_to_widgets(encode_task)
                self._apply_no_high_tier_setting_to_widgets(encode_task)
                self._apply_psy_rd_setting_to_widgets(encode_task)
                self._apply_psy_rdoq_setting_to_widgets(encode_task)
                self._apply_me_setting_to_widgets(encode_task)
                self._apply_subme_setting_to_widgets(encode_task)
                self._apply_weight_b_setting_to_widgets(encode_task)
                self._apply_no_weight_p_setting_to_widgets(encode_task)
                self._apply_deblock_settings_to_widgets(encode_task)
                self._apply_sao_settings_to_widgets(encode_task)
                self._apply_rd_setting_to_widgets(encode_task)
                self._apply_rdoq_level_setting_to_widgets(encode_task)
                self._apply_rd_refine_setting_to_widgets(encode_task)
                self._apply_max_cu_size_setting_to_widgets(encode_task)
                self._apply_min_cu_size_setting_to_widgets(encode_task)
                self._apply_rect_setting_to_widgets(encode_task)
                self._apply_amp_setting_to_widgets(encode_task)
                self._apply_wpp_setting_to_widgets(encode_task)
                self._apply_pmode_setting_to_widgets(encode_task)
                self._apply_pme_setting_to_widgets(encode_task)
                self._apply_uhd_bd_setting_to_widgets(encode_task)

            def _apply_vbv_maxrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.vbv_maxrate_spin_button.set_value, encode_task.get_video_codec().vbv_maxrate)

            def _apply_vbv_bufsize_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.vbv_bufsize_spin_button.set_value, encode_task.get_video_codec().vbv_bufsize)

            def _apply_aq_mode_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.aq_mode_row.set_selected, encode_task.get_video_codec().aq_mode)

            def _apply_aq_strength_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.aq_strength_spin_button.set_value, encode_task.get_video_codec().aq_strength)

            def _apply_hevc_aq_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.hevc_aq_switch.set_active, encode_task.get_video_codec().hevc_aq)

            def _apply_keyint_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.keyint_spin_button.set_value, encode_task.get_video_codec().keyint)

            def _apply_min_keyint_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.min_keyint_spin_button.set_value, encode_task.get_video_codec().min_keyint)

            def _apply_ref_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.ref_spin_button.set_value, encode_task.get_video_codec().ref)

            def _apply_b_frames_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_frames_spin_button.set_value, encode_task.get_video_codec().bframes)

            def _apply_b_adapt_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_adapt_row.set_selected, encode_task.get_video_codec().b_adapt)

            def _apply_no_b_pyramid_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_b_pyramid_switch.set_active, encode_task.get_video_codec().no_b_pyramid)

            def _apply_b_intra_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_intra_switch.set_active, encode_task.get_video_codec().b_intra)

            def _apply_no_gop_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_gop_switch.set_active, encode_task.get_video_codec().no_open_gop)

            def _apply_rc_lookahead_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rc_lookahead_spin_button.set_value, encode_task.get_video_codec().rc_lookahead)

            def _apply_no_scenecut_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_scenecut_switch.set_active, encode_task.get_video_codec().no_scenecut)

            def _apply_no_high_tier_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_high_tier_switch.set_active, encode_task.get_video_codec().no_high_tier)

            def _apply_psy_rd_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.psy_rd_spin_button.set_value, encode_task.get_video_codec().psy_rd)

            def _apply_psy_rdoq_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.psy_rdoq_spin_button.set_value, encode_task.get_video_codec().psy_rdoq)

            def _apply_me_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.me_row.set_selected, encode_task.get_video_codec().me)

            def _apply_subme_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.subme_spin_button.set_value, encode_task.get_video_codec().subme)

            def _apply_weight_b_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.weight_b_switch.set_active, encode_task.get_video_codec().weightb)

            def _apply_no_weight_p_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_weight_p_switch.set_active, encode_task.get_video_codec().no_weightp)

            def _apply_deblock_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_deblock_check_button.set_active, encode_task.get_video_codec().no_deblock)

                deblock_alpha, deblock_beta = encode_task.get_video_codec().deblock
                GLib.idle_add(self.deblock_alpha_spin_button.set_value, deblock_alpha)
                GLib.idle_add(self.deblock_beta_spin_button.set_value, deblock_beta)

            def _apply_sao_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_sao_switch.set_active, encode_task.get_video_codec().no_sao)
                GLib.idle_add(self.sao_non_deblock_switch.set_active, encode_task.get_video_codec().sao_non_deblock)
                GLib.idle_add(self.selective_sao_spin_button.set_value, encode_task.get_video_codec().selective_sao)
                GLib.idle_add(self.limit_sao_switch.set_active, encode_task.get_video_codec().limit_sao)

            def _apply_rd_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rd_spin_button.set_value, encode_task.get_video_codec().rd)

            def _apply_rdoq_level_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rdoq_level_row.set_selected, encode_task.get_video_codec().rdoq_level)

            def _apply_rd_refine_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rd_refine_switch.set_active, encode_task.get_video_codec().rd_refine)

            def _apply_max_cu_size_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.max_cu_size_row.set_selected, encode_task.get_video_codec().ctu)

            def _apply_min_cu_size_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.min_cu_size_row.set_selected, encode_task.get_video_codec().min_cu_size)

            def _apply_rect_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rect_switch.set_active, encode_task.get_video_codec().rect)

            def _apply_amp_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.amp_switch.set_active, encode_task.get_video_codec().amp)

            def _apply_wpp_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.wpp_switch.set_active, encode_task.get_video_codec().wpp)

            def _apply_pmode_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.pmode_switch.set_active, encode_task.get_video_codec().pmode)

            def _apply_pme_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.pme_switch.set_active, encode_task.get_video_codec().pme)

            def _apply_uhd_bd_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.uhd_bd_switch.set_active, encode_task.get_video_codec().uhd_bd)

            def apply_settings_from_widgets(self, is_delay_enabled: bool):
                if is_delay_enabled:
                    time.sleep(0.25)

                x265_settings = video_codec.X265()
                x265_settings.preset = self.preset_row.get_selected()
                x265_settings.profile = self.profile_row.get_selected()
                x265_settings.level = self.level_row.get_selected()
                x265_settings.tune = self.tune_row.get_selected()
                x265_settings.is_advanced_enabled = self.advanced_settings_switch.get_active()

                self._apply_rate_type_settings_from_widgets(x265_settings)

                if self.advanced_settings_switch.get_active():
                    x265_settings.aq_mode = self.aq_mode_row.get_selected()
                    x265_settings.aq_strength = self.aq_strength_spin_button.get_value()
                    x265_settings.hevc_aq = self.hevc_aq_switch.get_active()
                    x265_settings.keyint = self.keyint_spin_button.get_value_as_int()
                    x265_settings.min_keyint = self.min_keyint_spin_button.get_value_as_int()
                    x265_settings.ref = self.ref_spin_button.get_value_as_int()
                    x265_settings.bframes = self.b_frames_spin_button.get_value_as_int()
                    x265_settings.b_adapt = self.b_adapt_row.get_selected()
                    x265_settings.no_b_pyramid = self.no_b_pyramid_switch.get_active()
                    x265_settings.b_intra = self.b_intra_switch.get_active()
                    x265_settings.no_open_gop = self.no_gop_switch.get_active()
                    x265_settings.rc_lookahead = self.rc_lookahead_spin_button.get_value_as_int()
                    x265_settings.no_scenecut = self.no_scenecut_switch.get_active()
                    x265_settings.no_high_tier = self.no_high_tier_switch.get_active()
                    x265_settings.psy_rd = self.psy_rd_spin_button.get_value()
                    x265_settings.psy_rdoq = self.psy_rdoq_spin_button.get_value()
                    x265_settings.me = self.me_row.get_selected()
                    x265_settings.subme = self.subme_spin_button.get_value_as_int()
                    x265_settings.weightb = self.weight_b_switch.get_active()
                    x265_settings.no_weightp = self.no_weight_p_switch.get_active()
                    x265_settings.rd = self.rd_spin_button.get_value_as_int()
                    x265_settings.rdoq_level = self.rdoq_level_row.get_selected()
                    x265_settings.rd_refine = self.rd_refine_switch.get_active()
                    x265_settings.ctu = self.max_cu_size_row.get_selected()
                    x265_settings.min_cu_size = self.min_cu_size_row.get_selected()
                    x265_settings.rect = self.rect_switch.get_active()
                    x265_settings.amp = self.amp_switch.get_active()
                    x265_settings.wpp = self.wpp_switch.get_active()
                    x265_settings.pmode = self.pmode_switch.get_active()
                    x265_settings.pme = self.pme_switch.get_active()
                    x265_settings.uhd_bd = self.uhd_bd_switch.get_active()

                    self._apply_vbv_settings_from_widgets(x265_settings)
                    self._apply_sao_settings_from_widgets(x265_settings)
                    self._apply_deblock_settings_from_widgets(x265_settings)

                for input_row in self.inputs_page.get_selected_rows():
                    encode_task = input_row.encode_task
                    encode_task.set_video_codec(copy.deepcopy(x265_settings))

                    if video_codec.is_codec_2_pass(encode_task.get_video_codec()):
                        stats_file_path = os.path.join(encode_task.temp_output_file.dir,
                                                       encode_task.temp_output_file.name + '.log')
                        encode_task.video_codec.stats = stats_file_path

                    print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

                self.inputs_page.update_preview_page_encode_task()

            def _apply_rate_type_settings_from_widgets(self, x265_settings: video_codec.X265):
                if self.crf_check_button.get_active():
                    x265_settings.crf = self.crf_scale.get_value()
                elif self.qp_check_button.get_active():
                    x265_settings.qp = self.qp_scale.get_value()
                else:
                    x265_settings.bitrate = self.bitrate_spin_button.get_value_as_int()

                    if self.dual_pass_check_button.get_active():
                        x265_settings.encode_pass = 1

            def _apply_vbv_settings_from_widgets(self, x265_settings: video_codec.X265):
                x265_settings.vbv_maxrate = self.vbv_maxrate_spin_button.get_value_as_int()
                x265_settings.vbv_bufsize = self.vbv_bufsize_spin_button.get_value_as_int()

            def _apply_sao_settings_from_widgets(self, x265_settings: video_codec.X265):
                x265_settings.no_sao = self.no_sao_switch.get_active()

                if not self.no_sao_switch.get_active():
                    x265_settings.sao_non_deblock = self.sao_non_deblock_switch.get_active()
                    x265_settings.selective_sao = self.selective_sao_spin_button.get_value_as_int()
                    x265_settings.limit_sao = self.limit_sao_switch.get_active()

            def _apply_deblock_settings_from_widgets(self, x265_settings: video_codec.X265):
                x265_settings.no_deblock = self.no_deblock_check_button.get_active()

                if not self.no_deblock_check_button.get_active():
                    deblock_values = (self.deblock_alpha_spin_button.get_value_as_int(),
                                      self.deblock_beta_spin_button.get_value_as_int())
                    x265_settings.deblock = deblock_values

            def on_widget_changed_clicked_set(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                is_delay_enabled = (self.crf_event_controller_scroll in args or self.qp_event_controller_scroll in args)

                threading.Thread(target=self.apply_settings_from_widgets, args=(is_delay_enabled,)).start()

            def on_scale_gesture_stopped(self, user_data, gesture_click):
                if gesture_click.get_device():
                    return

                self.on_widget_changed_clicked_set()

            def on_crf_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('crf_page')
                    self.rate_type_settings_row.set_title('CRF')
                    self.rate_type_settings_row.set_subtitle('Constant Ratefactor')

                    self.on_widget_changed_clicked_set(check_button)

            def on_qp_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('qp_page')
                    self.rate_type_settings_row.set_title('QP')
                    self.rate_type_settings_row.set_subtitle('Constant Quantizer: P-frames')

                    self.on_widget_changed_clicked_set(check_button)

            def on_bitrate_check_button_toggled(self, check_button):
                self.set_vbv_state(check_button.get_active())

                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('bitrate_page')
                    self.rate_type_settings_row.set_title('Bitrate')
                    self.rate_type_settings_row.set_subtitle('Target video bitrate in kbps')

                    self.on_widget_changed_clicked_set(check_button)

            def on_non_deblock_check_button_toggled(self, check_button):
                self.deblock_alpha_spin_button.set_sensitive(not check_button.get_active())
                self.deblock_beta_spin_button.set_sensitive(not check_button.get_active())

                self.on_widget_changed_clicked_set(check_button)

            def on_no_sao_switch_state_set(self, switch, user_data):
                self.limit_sao_row.set_sensitive(not switch.get_active() and self.advanced_settings_switch.get_active())
                self.sao_non_deblock_row.set_sensitive(not switch.get_active()
                                                       and self.advanced_settings_switch.get_active())
                self.selective_sao_row.set_sensitive(not switch.get_active()
                                                     and self.advanced_settings_switch.get_active())

                self.on_widget_changed_clicked_set(switch)

            def on_scale_adjust_bounds(self, scale, value):
                if self.is_widgets_setting_up:
                    return

                if int(value) != int(scale.get_value()):
                    self.on_widget_changed_clicked_set(scale)

            def on_bitrate_type_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.set_vbv_state(True)

                    self.on_widget_changed_clicked_set(check_button)

            def on_advanced_settings_switch_state_set(self, switch, user_data):
                is_state_enabled = switch.get_active()
                self._set_vbv_maxrate_row_enabled(is_state_enabled)
                self._set_vbv_bufsize_row_enabled(is_state_enabled)
                self.keyint_row.set_sensitive(is_state_enabled)
                self.min_keyint_row.set_sensitive(is_state_enabled)
                self.ref_row.set_sensitive(is_state_enabled)
                self.b_frames_row.set_sensitive(is_state_enabled)
                self.b_adapt_row.set_sensitive(is_state_enabled)
                self.no_b_pyramid_row.set_sensitive(is_state_enabled)
                self.b_intra_row.set_sensitive(is_state_enabled)
                self.weight_b_row.set_sensitive(is_state_enabled)
                self.no_weight_p_row.set_sensitive(is_state_enabled)
                self.no_high_tier_row.set_sensitive(is_state_enabled)
                self.no_gop_row.set_sensitive(is_state_enabled)
                self.no_scenecut_row.set_sensitive(is_state_enabled)
                self.me_row.set_sensitive(is_state_enabled)
                self.subme_row.set_sensitive(is_state_enabled)
                self._set_deblock_row_enabled(is_state_enabled)
                self.aq_mode_row.set_sensitive(is_state_enabled)
                self.aq_strength_row.set_sensitive(is_state_enabled)
                self.hevc_aq_row.set_sensitive(is_state_enabled)
                self.rc_lookahead_row.set_sensitive(is_state_enabled)
                self.psy_rd_row.set_sensitive(is_state_enabled)
                self.psy_rdoq_row.set_sensitive(is_state_enabled)
                self.rd_row.set_sensitive(is_state_enabled)
                self.rd_refine_row.set_sensitive(is_state_enabled)
                self.rdoq_level_row.set_sensitive(is_state_enabled)
                self._set_sao_rows_enabled(is_state_enabled)
                self.min_cu_size_row.set_sensitive(is_state_enabled)
                self.max_cu_size_row.set_sensitive(is_state_enabled)
                self.rect_row.set_sensitive(is_state_enabled)
                self.amp_row.set_sensitive(is_state_enabled)
                self.wpp_row.set_sensitive(is_state_enabled)
                self.pmode_row.set_sensitive(is_state_enabled)
                self.pme_row.set_sensitive(is_state_enabled)
                self.uhd_bd_row.set_sensitive(is_state_enabled)

                self.on_widget_changed_clicked_set(switch)

            def _set_vbv_maxrate_row_enabled(self, is_enabled: bool):
                if self.bitrate_check_button.get_active():
                    self.vbv_maxrate_row.set_sensitive(is_enabled)
                else:
                    self.vbv_maxrate_row.set_sensitive(False)

            def _set_vbv_bufsize_row_enabled(self, is_enabled: bool):
                if self.bitrate_check_button.get_active():
                    self.vbv_bufsize_row.set_sensitive(is_enabled)
                else:
                    self.vbv_bufsize_row.set_sensitive(False)

            def _set_deblock_row_enabled(self, is_enabled: bool):
                self.deblock_row.set_sensitive(is_enabled)

                if not self.no_deblock_check_button.get_active():
                    self.deblock_alpha_spin_button.set_sensitive(is_enabled)
                    self.deblock_beta_spin_button.set_sensitive(is_enabled)
                else:
                    self.deblock_alpha_spin_button.set_sensitive(False)
                    self.deblock_beta_spin_button.set_sensitive(False)

            def _set_sao_rows_enabled(self, is_enabled: bool):
                self.no_sao_row.set_sensitive(is_enabled)

                if not self.no_sao_switch.get_active():
                    self.limit_sao_row.set_sensitive(is_enabled)
                    self.sao_non_deblock_row.set_sensitive(is_enabled)
                    self.selective_sao_row.set_sensitive(is_enabled)
                else:
                    self.limit_sao_row.set_sensitive(False)
                    self.sao_non_deblock_row.set_sensitive(False)
                    self.selective_sao_row.set_sensitive(False)

        class Vp9StackPage(Gtk.Box):
            def __init__(self, inputs_page):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self.inputs_page = inputs_page
                self.is_widgets_setting_up = False

                self._setup_codec_settings()

                self.append(self.codec_settings_group)

            def _setup_codec_settings(self):
                self._setup_quality_row()
                self._setup_speed_row()
                self._setup_row_multithreading_row()
                self._setup_rate_type_row()
                self._setup_2_pass_row()
                self._setup_crf_row()
                self._setup_bitrate_row()
                self._setup_max_bitrate_row()
                self._setup_min_bitrate_row()
                self._setup_bitrate_type_row()

                self.codec_settings_group = Adw.PreferencesGroup()
                self.codec_settings_group.set_title('VP9 Settings')
                self.codec_settings_group.add(self.quality_row)
                self.codec_settings_group.add(self.speed_row)
                self.codec_settings_group.add(self.row_multithreading_row)
                self.codec_settings_group.add(self.rate_type_row)
                self.codec_settings_group.add(self.crf_row)
                self.codec_settings_group.add(self.max_bitrate_row)
                self.codec_settings_group.add(self.bitrate_row)
                self.codec_settings_group.add(self.min_bitrate_row)
                self.codec_settings_group.add(self.bitrate_type_row)
                self.codec_settings_group.add(self.two_pass_row)

            def _setup_quality_row(self):
                self._setup_quality_string_list()

                self.quality_row = Adw.ComboRow()
                self.quality_row.set_title('Quality')
                self.quality_row.set_subtitle('Encoder quality')
                self.quality_row.set_model(self.quality_string_list)
                self.quality_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_quality_string_list(self):
                self.quality_string_list = Gtk.StringList.new(video_codec.VP9.QUALITY)

            def _setup_speed_row(self):
                self._setup_speed_string_list()

                self.speed_row = Adw.ComboRow()
                self.speed_row.set_title('Speed')
                self.speed_row.set_subtitle('Encoder speed')
                self.speed_row.set_model(self.speed_string_list)
                self.speed_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_speed_string_list(self):
                self.speed_string_list = Gtk.StringList.new(video_codec.VP9.SPEED)

            def _setup_row_multithreading_row(self):
                self._setup_row_multithreading_switch()

                self.row_multithreading_row = Adw.ActionRow()
                self.row_multithreading_row.set_title('Row Multithreading')
                self.row_multithreading_row.set_subtitle('Row multithreading')
                self.row_multithreading_row.add_suffix(self.row_multithreading_switch)

            def _setup_row_multithreading_switch(self):
                self.row_multithreading_switch = Gtk.Switch()
                self.row_multithreading_switch.set_vexpand(False)
                self.row_multithreading_switch.set_valign(Gtk.Align.CENTER)
                self.row_multithreading_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_rate_type_row(self):
                self._setup_rate_type_radio_buttons()

                self.rate_type_row = Adw.ActionRow()
                self.rate_type_row.set_title('Rate Type')
                self.rate_type_row.set_subtitle('Rate type method')
                self.rate_type_row.add_suffix(self.rate_type_horizontal_box)

            def _setup_rate_type_radio_buttons(self):
                self.crf_check_button = Gtk.CheckButton(label='CRF')
                self.crf_check_button.set_active(True)
                self.crf_check_button.connect('toggled', self.on_crf_check_button_toggled)

                self.bitrate_check_button = Gtk.CheckButton(label='Bitrate')
                self.bitrate_check_button.set_group(self.crf_check_button)
                self.bitrate_check_button.connect('toggled', self.on_bitrate_check_button_toggled)

                self.constrained_check_button = Gtk.CheckButton(label='Constrained')
                self.constrained_check_button.set_group(self.crf_check_button)
                self.constrained_check_button.connect('toggled', self.on_constrained_check_button_toggled)

                self.rate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.rate_type_horizontal_box.append(self.crf_check_button)
                self.rate_type_horizontal_box.append(self.bitrate_check_button)
                self.rate_type_horizontal_box.append(self.constrained_check_button)

            def _setup_2_pass_row(self):
                self._setup_2_pass_switch()

                self.two_pass_row = Adw.ActionRow()
                self.two_pass_row.set_title('2-Pass')
                self.two_pass_row.set_subtitle('2-Pass encoding')
                self.two_pass_row.add_suffix(self.two_pass_switch)

            def _setup_2_pass_switch(self):
                self.two_pass_switch = Gtk.Switch()
                self.two_pass_switch.set_vexpand(False)
                self.two_pass_switch.set_valign(Gtk.Align.CENTER)
                self.two_pass_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_crf_row(self):
                self._setup_crf_scale()

                self.crf_row = Adw.ActionRow()
                self.crf_row.set_title('CRF')
                self.crf_row.set_subtitle('Constant Ratefactor')
                self.crf_row.add_suffix(self.crf_scale)

            def _setup_crf_scale(self):
                self._setup_crf_gesture_click()
                self._setup_crf_event_controller_key()
                self._setup_crf_event_controller_scroll()

                self.crf_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                          min=video_codec.VP9.CRF_MIN,
                                                          max=video_codec.VP9.CRF_MAX,
                                                          step=1.0)
                self.crf_scale.set_value(30)
                self.crf_scale.set_digits(0)
                self.crf_scale.set_draw_value(True)
                self.crf_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.crf_scale.set_hexpand(True)
                self.crf_scale.add_controller(self.crf_gesture_click)
                self.crf_scale.add_controller(self.crf_event_controller_key)
                self.crf_scale.add_controller(self.crf_event_controller_scroll)

            def _setup_crf_gesture_click(self):
                self.crf_gesture_click = Gtk.GestureClick.new()
                self.crf_gesture_click.connect('stopped', self.on_scale_gesture_stopped, self.crf_gesture_click)
                self.crf_gesture_click.connect('unpaired-release', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_key(self):
                self.crf_event_controller_key = Gtk.EventControllerKey.new()
                self.crf_event_controller_key.connect('key-released', self.on_widget_changed_clicked_set)

            def _setup_crf_event_controller_scroll(self):
                self.crf_event_controller_scroll = Gtk.EventControllerScroll.new(
                    Gtk.EventControllerScrollFlags.BOTH_AXES)
                self.crf_event_controller_scroll.connect('scroll', self.on_widget_changed_clicked_set)

            def _setup_bitrate_row(self):
                self._setup_bitrate_spin_button()

                self.bitrate_row = Adw.ActionRow()
                self.bitrate_row.set_title('Bitrate')
                self.bitrate_row.set_subtitle('Target bitrate')
                self.bitrate_row.add_suffix(self.bitrate_spin_button)
                self.bitrate_row.set_sensitive(False)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(video_codec.VP9.BITRATE_MIN, video_codec.VP9.BITRATE_MAX)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(100, 500)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)
                self.bitrate_spin_button.set_value(2500)
                self.bitrate_spin_button.set_size_request(125, -1)
                self.bitrate_spin_button.set_vexpand(False)
                self.bitrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.bitrate_spin_button.connect('value-changed', self.on_bitrate_spin_button_value_changed)

            def _setup_max_bitrate_row(self):
                self._setup_max_bitrate_spin_button()

                self.max_bitrate_row = Adw.ActionRow()
                self.max_bitrate_row.set_title('Max Bitrate')
                self.max_bitrate_row.set_subtitle('Maximum bitrate')
                self.max_bitrate_row.add_suffix(self.max_bitrate_spin_button)
                self.max_bitrate_row.set_sensitive(False)

            def _setup_max_bitrate_spin_button(self):
                self.max_bitrate_spin_button = Gtk.SpinButton()
                self.max_bitrate_spin_button.set_range(video_codec.VP9.BITRATE_MIN, video_codec.VP9.BITRATE_MAX)
                self.max_bitrate_spin_button.set_digits(0)
                self.max_bitrate_spin_button.set_increments(100, 500)
                self.max_bitrate_spin_button.set_numeric(True)
                self.max_bitrate_spin_button.set_snap_to_ticks(True)
                self.max_bitrate_spin_button.set_value(2500)
                self.max_bitrate_spin_button.set_size_request(125, -1)
                self.max_bitrate_spin_button.set_vexpand(False)
                self.max_bitrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.max_bitrate_spin_button.connect('value-changed', self.on_max_bitrate_spin_button_value_changed)

            def _setup_min_bitrate_row(self):
                self._setup_min_bitrate_spin_button()

                self.min_bitrate_row = Adw.ActionRow()
                self.min_bitrate_row.set_title('Min Bitrate')
                self.min_bitrate_row.set_subtitle('Minimum bitrate')
                self.min_bitrate_row.add_suffix(self.min_bitrate_spin_button)
                self.min_bitrate_row.set_sensitive(False)

            def _setup_min_bitrate_spin_button(self):
                self.min_bitrate_spin_button = Gtk.SpinButton()
                self.min_bitrate_spin_button.set_range(video_codec.VP9.BITRATE_MIN, video_codec.VP9.BITRATE_MAX)
                self.min_bitrate_spin_button.set_digits(0)
                self.min_bitrate_spin_button.set_increments(100, 500)
                self.min_bitrate_spin_button.set_numeric(True)
                self.min_bitrate_spin_button.set_snap_to_ticks(True)
                self.min_bitrate_spin_button.set_value(2500)
                self.min_bitrate_spin_button.set_size_request(125, -1)
                self.min_bitrate_spin_button.set_vexpand(False)
                self.min_bitrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.min_bitrate_spin_button.connect('value-changed', self.on_min_bitrate_spin_button_value_changed)

            def _setup_bitrate_type_row(self):
                self._setup_bitrate_type_radio_buttons()

                self.bitrate_type_row = Adw.ActionRow()
                self.bitrate_type_row.set_title('Bitrate Type')
                self.bitrate_type_row.set_subtitle('Bitrate method')
                self.bitrate_type_row.add_suffix(self.bitrate_type_horizontal_box)
                self.bitrate_type_row.set_sensitive(False)

            def _setup_bitrate_type_radio_buttons(self):
                self.average_bitrate_check_button = Gtk.CheckButton(label='Average')
                self.average_bitrate_check_button.set_active(True)
                self.average_bitrate_check_button.connect('toggled', self.on_average_bitrate_check_button_toggled)

                self.vbr_bitrate_check_button = Gtk.CheckButton(label='VBR')
                self.vbr_bitrate_check_button.set_group(self.average_bitrate_check_button)
                self.vbr_bitrate_check_button.connect('toggled', self.on_vbr_bitrate_check_button_toggled)

                self.constant_bitrate_check_button = Gtk.CheckButton(label='Constant')
                self.constant_bitrate_check_button.set_group(self.average_bitrate_check_button)
                self.constant_bitrate_check_button.connect('toggled', self.on_constant_bitrate_check_button_toggled)

                self.bitrate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.bitrate_type_horizontal_box.append(self.average_bitrate_check_button)
                self.bitrate_type_horizontal_box.append(self.vbr_bitrate_check_button)
                self.bitrate_type_horizontal_box.append(self.constant_bitrate_check_button)

            def update_vbr_widgets_from_bitrate(self):
                bitrate_value = self.bitrate_spin_button.get_value()
                max_bitrate_value = self.max_bitrate_spin_button.get_value()
                min_bitrate_value = self.min_bitrate_spin_button.get_value()
                self.is_widgets_setting_up = True

                if self.constant_bitrate_check_button.get_active():
                    self.min_bitrate_spin_button.set_value(bitrate_value)
                    self.max_bitrate_spin_button.set_value(bitrate_value)
                else:
                    if bitrate_value > max_bitrate_value:
                        self.max_bitrate_spin_button.set_value(bitrate_value)

                    if bitrate_value < min_bitrate_value:
                        self.min_bitrate_spin_button.set_value(bitrate_value)

                self.is_widgets_setting_up = False

            def update_vbr_widgets_from_max_bitrate(self):
                bitrate_value = self.bitrate_spin_button.get_value()
                max_bitrate_value = self.max_bitrate_spin_button.get_value()
                min_bitrate_value = self.min_bitrate_spin_button.get_value()
                self.is_widgets_setting_up = True

                if max_bitrate_value < bitrate_value:
                    self.bitrate_spin_button.set_value(max_bitrate_value)

                    if min_bitrate_value > self.bitrate_spin_button.get_value():
                        self.min_bitrate_spin_button.set_value(max_bitrate_value)

                self.is_widgets_setting_up = False

            def update_vbr_widgets_from_min_bitrate(self):
                bitrate_value = self.bitrate_spin_button.get_value()
                max_bitrate_value = self.max_bitrate_spin_button.get_value()
                min_bitrate_value = self.min_bitrate_spin_button.get_value()
                self.is_widgets_setting_up = True

                if min_bitrate_value > bitrate_value:
                    self.bitrate_spin_button.set_value(min_bitrate_value)

                    if max_bitrate_value < self.bitrate_spin_button.get_value():
                        self.max_bitrate_spin_button.set_value(min_bitrate_value)

                self.is_widgets_setting_up = False

            def set_widgets_setting_up(self, is_widgets_setting_up: bool):
                self.is_widgets_setting_up = is_widgets_setting_up

            def apply_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.set_widgets_setting_up, True)
                self._apply_quality_setting_to_widgets(encode_task)
                self._apply_speed_setting_to_widgets(encode_task)
                self._apply_rate_type_settings_to_widgets(encode_task)
                self._apply_crf_setting_to_widgets(encode_task)
                self._apply_bitrate_setting_to_widgets(encode_task)
                self._apply_maxrate_setting_to_widgets(encode_task)
                self._apply_minrate_setting_to_widgets(encode_task)
                self._apply_bitrate_type_settings_to_widgets(encode_task)
                self._apply_row_multithreading_setting_to_widgets(encode_task)
                self._apply_encode_pass_setting_to_widgets(encode_task)
                GLib.idle_add(self.set_widgets_setting_up, False)

            def _apply_quality_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.quality_row.set_selected, encode_task.get_video_codec().quality)

            def _apply_speed_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.speed_row.set_selected, encode_task.get_video_codec().speed)

            def _apply_rate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_crf_enabled:
                    GLib.idle_add(self.crf_check_button.set_active, True)
                elif encode_task.get_video_codec().is_bitrate_enabled:
                    GLib.idle_add(self.bitrate_check_button.set_active, True)
                else:
                    GLib.idle_add(self.constrained_check_button.set_active, True)

            def _apply_crf_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.crf_scale.set_value, encode_task.get_video_codec().crf)

            def _apply_bitrate_setting_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_crf_enabled:
                    GLib.idle_add(self.bitrate_spin_button.set_value, 2500)
                else:
                    GLib.idle_add(self.bitrate_spin_button.set_value, encode_task.get_video_codec().bitrate)

            def _apply_maxrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.max_bitrate_spin_button.set_value, encode_task.get_video_codec().maxrate)

            def _apply_minrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.min_bitrate_spin_button.set_value, encode_task.get_video_codec().minrate)

            def _apply_bitrate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_average_bitrate_enabled:
                    GLib.idle_add(self.average_bitrate_check_button.set_active, True)
                elif encode_task.get_video_codec().is_vbr_bitrate_enabled:
                    GLib.idle_add(self.vbr_bitrate_check_button.set_active, True)
                else:
                    GLib.idle_add(self.constant_bitrate_check_button.set_active, True)

            def _apply_row_multithreading_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.row_multithreading_switch.set_active,
                              encode_task.get_video_codec().row_multithreading)

            def _apply_encode_pass_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.two_pass_switch.set_active, encode_task.get_video_codec().encode_pass == 1)

            def apply_settings_from_widgets(self, is_delay_enabled: bool):
                if is_delay_enabled:
                    time.sleep(0.25)

                vp9_settings = video_codec.VP9()
                vp9_settings.quality = self.quality_row.get_selected()
                vp9_settings.speed = self.speed_row.get_selected()
                vp9_settings.row_multithreading = self.row_multithreading_switch.get_active()

                self._apply_rate_type_settings_from_widgets(vp9_settings)
                self._apply_bitrate_type_settings_from_widgets(vp9_settings)
                self._apply_encode_pass_setting_from_widgets(vp9_settings)

                for input_row in self.inputs_page.get_selected_rows():
                    encode_task = input_row.encode_task
                    encode_task.set_video_codec(copy.deepcopy(vp9_settings))

                    if video_codec.is_codec_2_pass(encode_task.get_video_codec()):
                        stats_file_path = os.path.join(encode_task.temp_output_file.dir,
                                                       encode_task.temp_output_file.name + '.log')
                        encode_task.video_codec.stats = stats_file_path

                    print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

                self.inputs_page.update_preview_page_encode_task()

            def _apply_rate_type_settings_from_widgets(self, vp9_settings: video_codec.VP9):
                if self.crf_check_button.get_active():
                    vp9_settings.is_crf_enabled = True
                    vp9_settings.crf = self.crf_scale.get_value()
                elif self.bitrate_check_button.get_active():
                    vp9_settings.is_bitrate_enabled = True
                    vp9_settings.crf = None
                    vp9_settings.bitrate = self.bitrate_spin_button.get_value_as_int()
                else:
                    vp9_settings.is_constrained_enabled = True
                    vp9_settings.crf = self.crf_scale.get_value()
                    vp9_settings.bitrate = self.bitrate_spin_button.get_value_as_int()

            def _apply_bitrate_type_settings_from_widgets(self, vp9_settings: video_codec.VP9):
                if self.crf_check_button.get_active():
                    return

                if self.average_bitrate_check_button.get_active() or self.constrained_check_button.get_active():
                    vp9_settings.is_average_bitrate_enabled = True
                elif self.constant_bitrate_check_button.get_active():
                    vp9_settings.is_constant_bitrate_enabled = True
                    vp9_settings.maxrate = self.bitrate_spin_button.get_value_as_int()
                    vp9_settings.minrate = self.bitrate_spin_button.get_value_as_int()
                else:
                    vp9_settings.is_vbr_bitrate_enabled = True
                    vp9_settings.maxrate = self.max_bitrate_spin_button.get_value_as_int()
                    vp9_settings.minrate = self.min_bitrate_spin_button.get_value_as_int()

            def _apply_encode_pass_setting_from_widgets(self, vp9_settings: video_codec.VP9):
                if self.two_pass_switch.get_active():
                    vp9_settings.encode_pass = 1

            def on_widget_changed_clicked_set(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                is_delay_enabled = (self.crf_event_controller_scroll in args)

                threading.Thread(target=self.apply_settings_from_widgets, args=(is_delay_enabled,)).start()

            def on_scale_gesture_stopped(self, user_data, gesture_click):
                if gesture_click.get_device():
                    return

                self.on_widget_changed_clicked_set()

            def on_crf_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.crf_row.set_sensitive(True)
                    self.max_bitrate_row.set_sensitive(False)
                    self.bitrate_row.set_sensitive(False)
                    self.min_bitrate_row.set_sensitive(False)
                    self.bitrate_type_row.set_sensitive(False)

                    self.on_widget_changed_clicked_set(check_button)

            def on_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.crf_row.set_sensitive(False)
                    self.bitrate_row.set_sensitive(True)
                    self.bitrate_type_row.set_sensitive(True)

                    if self.vbr_bitrate_check_button.get_active():
                        self.max_bitrate_row.set_sensitive(True)
                        self.min_bitrate_row.set_sensitive(True)

                    self.on_widget_changed_clicked_set(check_button)

            def on_constrained_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.crf_row.set_sensitive(True)
                    self.max_bitrate_row.set_sensitive(False)
                    self.bitrate_row.set_sensitive(True)
                    self.min_bitrate_row.set_sensitive(False)
                    self.bitrate_type_row.set_sensitive(False)

                    self.on_widget_changed_clicked_set(check_button)

            def on_bitrate_spin_button_value_changed(self, spin_button):
                if self.is_widgets_setting_up:
                    return

                self.update_vbr_widgets_from_bitrate()

                self.on_widget_changed_clicked_set(spin_button)

            def on_max_bitrate_spin_button_value_changed(self, spin_button):
                if self.is_widgets_setting_up:
                    return

                self.update_vbr_widgets_from_max_bitrate()

                self.on_widget_changed_clicked_set(spin_button)

            def on_min_bitrate_spin_button_value_changed(self, spin_button):
                if self.is_widgets_setting_up:
                    return

                self.update_vbr_widgets_from_min_bitrate()

                self.on_widget_changed_clicked_set(spin_button)

            def on_average_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.max_bitrate_row.set_sensitive(False)
                    self.min_bitrate_row.set_sensitive(False)

                    self.on_widget_changed_clicked_set(check_button)

            def on_vbr_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.max_bitrate_row.set_sensitive(True)
                    self.min_bitrate_row.set_sensitive(True)

                    self.on_widget_changed_clicked_set(check_button)

            def on_constant_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.update_vbr_widgets_from_bitrate()
                    self.max_bitrate_row.set_sensitive(False)
                    self.min_bitrate_row.set_sensitive(False)

                    self.on_widget_changed_clicked_set(check_button)

        class NvencStackPage(Gtk.Box):
            def __init__(self, inputs_page):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self.inputs_page = inputs_page
                self.is_widgets_setting_up = False
                self._is_h264_state = True
                self._is_h265_state = False

                self._setup_codec_settings()
                self._setup_codec_advanced_settings()

                self.append(self.codec_settings_group)
                self.append(self.codec_advanced_settings_group)

            def _setup_codec_settings(self):
                self._setup_preset_row()
                self._setup_profile_row()
                self._setup_level_row()
                self._setup_tune_row()
                self._setup_rate_type_row()
                self._setup_rate_type_settings_row()
                self._setup_multi_pass_row()

                self.codec_settings_group = Adw.PreferencesGroup()
                self.codec_settings_group.set_title('Nvenc Settings')
                self.codec_settings_group.add(self.preset_row)
                self.codec_settings_group.add(self.profile_row)
                self.codec_settings_group.add(self.level_row)
                self.codec_settings_group.add(self.tune_row)
                self.codec_settings_group.add(self.rate_type_row)
                self.codec_settings_group.add(self.rate_type_settings_row)
                self.codec_settings_group.add(self.multi_pass_row)

            def _setup_preset_row(self):
                self._setup_preset_string_list()

                self.preset_row = Adw.ComboRow()
                self.preset_row.set_title('Preset')
                self.preset_row.set_subtitle('Encoder preset')
                self.preset_row.set_model(self.preset_string_list)
                self.preset_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_preset_string_list(self):
                self.preset_string_list = Gtk.StringList.new(video_codec.H264Nvenc.PRESET)

            def _setup_profile_row(self):
                self._setup_profile_string_list()

                self.profile_row = Adw.ComboRow()
                self.profile_row.set_title('Profile')
                self.profile_row.set_subtitle('Encoder profile')
                self.profile_row.set_model(self.profile_string_list)
                self.profile_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_profile_string_list(self):
                self.profile_string_list = Gtk.StringList.new(video_codec.H264Nvenc.PROFILE)

            def _setup_level_row(self):
                self._setup_level_string_list()

                self.level_row = Adw.ComboRow()
                self.level_row.set_title('Level')
                self.level_row.set_subtitle('Encoder restrictions')
                self.level_row.set_model(self.level_string_list)
                self.level_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_level_string_list(self):
                self.level_string_list = Gtk.StringList.new(video_codec.H264Nvenc.LEVEL)

            def _setup_tune_row(self):
                self._setup_tune_string_list()

                self.tune_row = Adw.ComboRow()
                self.tune_row.set_title('Tune')
                self.tune_row.set_subtitle('Encoder tune')
                self.tune_row.set_model(self.tune_string_list)
                self.tune_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)

            def _setup_tune_string_list(self):
                self.tune_string_list = Gtk.StringList.new(video_codec.H264Nvenc.TUNE)

            def _setup_rate_type_row(self):
                self._setup_rate_type_radio_buttons()

                self.rate_type_row = Adw.ActionRow()
                self.rate_type_row.set_title('Rate Type')
                self.rate_type_row.set_subtitle('Rate type method')
                self.rate_type_row.add_suffix(self.rate_type_horizontal_box)

            def _setup_rate_type_radio_buttons(self):
                self.qp_check_button = Gtk.CheckButton(label='QP')
                self.qp_check_button.set_active(True)
                self.qp_check_button.connect('toggled', self.on_qp_check_button_toggled)

                self.bitrate_check_button = Gtk.CheckButton(label='Bitrate')
                self.bitrate_check_button.set_group(self.qp_check_button)
                self.bitrate_check_button.connect('toggled', self.on_bitrate_check_button_toggled)

                self.rate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.rate_type_horizontal_box.append(self.qp_check_button)
                self.rate_type_horizontal_box.append(self.bitrate_check_button)

            def _setup_rate_type_settings_row(self):
                self._setup_rate_type_settings_stack()

                self.rate_type_settings_row = Adw.ActionRow()
                self.rate_type_settings_row.set_title('QP')
                self.rate_type_settings_row.set_subtitle('Constant Quantizer: P-frames')
                self.rate_type_settings_row.add_suffix(self.rate_type_settings_stack)

            def _setup_rate_type_settings_stack(self):
                self._setup_qp_page()
                self._setup_bitrate_page()

                self.rate_type_settings_stack = Gtk.Stack()
                self.rate_type_settings_stack.add_named(self.qp_scale, 'qp_page')
                self.rate_type_settings_stack.add_named(self.bitrate_page_vertical_box, 'bitrate_page')
                self.rate_type_settings_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

            def _setup_qp_page(self):
                self.qp_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                         min=video_codec.H264Nvenc.QP_MIN,
                                                         max=video_codec.H264Nvenc.QP_MAX,
                                                         step=1.0)
                self.qp_scale.set_value(20)
                self.qp_scale.set_digits(0)
                self.qp_scale.set_draw_value(True)
                self.qp_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_scale.set_hexpand(True)
                self.qp_scale.connect('adjust-bounds', self.on_scale_adjust_bounds)

            def _setup_bitrate_page(self):
                self._setup_bitrate_spin_button()
                self._setup_bitrate_type_widgets()

                self.bitrate_page_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.bitrate_page_vertical_box.append(self.bitrate_spin_button)
                self.bitrate_page_vertical_box.append(self.bitrate_type_horizontal_box)
                self.bitrate_page_vertical_box.set_margin_top(10)
                self.bitrate_page_vertical_box.set_margin_bottom(10)
                self.bitrate_page_vertical_box.set_hexpand(False)
                self.bitrate_page_vertical_box.set_halign(Gtk.Align.END)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(video_codec.H264Nvenc.BITRATE_MIN, video_codec.H264Nvenc.BITRATE_MAX)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(100, 500)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)
                self.bitrate_spin_button.set_value(2500)
                self.bitrate_spin_button.set_size_request(125, -1)
                self.bitrate_spin_button.set_vexpand(False)
                self.bitrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.bitrate_spin_button.set_hexpand(False)
                self.bitrate_spin_button.set_halign(Gtk.Align.CENTER)
                self.bitrate_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_bitrate_type_widgets(self):
                self.average_bitrate_check_button = Gtk.CheckButton(label='Average')
                self.average_bitrate_check_button.set_active(True)

                self.constant_bitrate_check_button = Gtk.CheckButton(label='Constant')
                self.constant_bitrate_check_button.set_group(self.average_bitrate_check_button)
                self.constant_bitrate_check_button.connect('toggled', self.on_widget_changed_clicked_set)

                self.bitrate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.bitrate_type_horizontal_box.append(self.average_bitrate_check_button)
                self.bitrate_type_horizontal_box.append(self.constant_bitrate_check_button)

            def _setup_multi_pass_row(self):
                self._setup_multi_pass_string_list()

                self.multi_pass_row = Adw.ComboRow()
                self.multi_pass_row.set_title('Multipass')
                self.multi_pass_row.set_subtitle('Encoder multipass')
                self.multi_pass_row.set_model(self.multi_pass_string_list)
                self.multi_pass_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.multi_pass_row.set_sensitive(False)

            def _setup_multi_pass_string_list(self):
                self.multi_pass_string_list = Gtk.StringList.new(video_codec.H264Nvenc.MULTI_PASS)

            def _setup_codec_advanced_settings(self):
                self._setup_custom_quantizer_row()
                self._setup_qp_i_row()
                self._setup_qp_p_row()
                self._setup_qp_b_row()
                self._setup_rc_row()
                self._setup_rc_lookahead_row()
                self._setup_surfaces_row()
                self._setup_b_frames_row()
                self._setup_refs_row()
                self._setup_no_scenecut_row()
                self._setup_forced_idr_row()
                self._setup_b_adapt_row()
                self._setup_aq_mode_row()
                self._setup_non_ref_p_row()
                self._setup_strict_gop_row()
                self._setup_aq_strength_row()
                self._setup_bluray_compat_row()
                self._setup_weighted_pred_row()
                self._setup_coder_row()
                self._setup_b_ref_mode_row()
                self._setup_tier_row()

                self.advanced_settings_switch = Gtk.Switch()
                self.advanced_settings_switch.set_vexpand(False)
                self.advanced_settings_switch.set_valign(Gtk.Align.CENTER)
                self.advanced_settings_switch.connect('state-set', self.on_advanced_settings_switch_state_set)

                self.codec_advanced_settings_group = Adw.PreferencesGroup()
                self.codec_advanced_settings_group.set_title('Advanced Settings')
                self.codec_advanced_settings_group.set_header_suffix(self.advanced_settings_switch)
                self.codec_advanced_settings_group.add(self.custom_quantizer_row)
                self.codec_advanced_settings_group.add(self.qp_i_row)
                self.codec_advanced_settings_group.add(self.qp_p_row)
                self.codec_advanced_settings_group.add(self.qp_b_row)
                self.codec_advanced_settings_group.add(self.rc_row)
                self.codec_advanced_settings_group.add(self.rc_lookahead_row)
                self.codec_advanced_settings_group.add(self.surfaces_row)
                self.codec_advanced_settings_group.add(self.tier_row)
                self.codec_advanced_settings_group.add(self.refs_row)
                self.codec_advanced_settings_group.add(self.forced_idr_row)
                self.codec_advanced_settings_group.add(self.non_ref_p_row)
                self.codec_advanced_settings_group.add(self.no_scenecut_row)
                self.codec_advanced_settings_group.add(self.strict_gop_row)
                self.codec_advanced_settings_group.add(self.b_frames_row)
                self.codec_advanced_settings_group.add(self.b_ref_mode_row)
                self.codec_advanced_settings_group.add(self.b_adapt_row)
                self.codec_advanced_settings_group.add(self.weighted_pred_row)
                self.codec_advanced_settings_group.add(self.aq_mode_row)
                self.codec_advanced_settings_group.add(self.aq_strength_row)
                self.codec_advanced_settings_group.add(self.coder_row)
                self.codec_advanced_settings_group.add(self.bluray_compat_row)

            def _setup_custom_quantizer_row(self):
                self._setup_custom_quantizer_switch()

                self.custom_quantizer_row = Adw.ActionRow()
                self.custom_quantizer_row.set_title('Custom Quantizer')
                self.custom_quantizer_row.set_subtitle('Quantizer value for each frame slice')
                self.custom_quantizer_row.add_suffix(self.custom_quantizer_switch)
                self.custom_quantizer_row.set_sensitive(False)

            def _setup_custom_quantizer_switch(self):
                self.custom_quantizer_switch = Gtk.Switch()
                self.custom_quantizer_switch.set_vexpand(False)
                self.custom_quantizer_switch.set_valign(Gtk.Align.CENTER)
                self.custom_quantizer_switch.connect('state-set', self.on_custom_quantizer_switch_state_set)

            def _setup_qp_i_row(self):
                self._setup_qp_i_scale()

                self.qp_i_row = Adw.ActionRow()
                self.qp_i_row.set_title('QP-I')
                self.qp_i_row.set_subtitle('Quantizer value for I-frames')
                self.qp_i_row.add_suffix(self.qp_i_scale)
                self.qp_i_row.set_sensitive(False)

            def _setup_qp_i_scale(self):
                self.qp_i_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                           min=video_codec.H264Nvenc.QP_MIN,
                                                           max=video_codec.H264Nvenc.QP_MAX,
                                                           step=1.0)
                self.qp_i_scale.set_value(20.0)
                self.qp_i_scale.set_digits(1)
                self.qp_i_scale.set_draw_value(True)
                self.qp_i_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_i_scale.set_hexpand(True)
                self.qp_i_scale.connect('adjust-bounds', self.on_scale_adjust_bounds)

            def _setup_qp_p_row(self):
                self._setup_qp_p_scale()

                self.qp_p_row = Adw.ActionRow()
                self.qp_p_row.set_title('QP-P')
                self.qp_p_row.set_subtitle('Quantizer value for P-frames')
                self.qp_p_row.add_suffix(self.qp_p_scale)
                self.qp_p_row.set_sensitive(False)

            def _setup_qp_p_scale(self):
                self.qp_p_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                           min=video_codec.H264Nvenc.QP_MIN,
                                                           max=video_codec.H264Nvenc.QP_MAX,
                                                           step=1.0)
                self.qp_p_scale.set_value(20.0)
                self.qp_p_scale.set_digits(1)
                self.qp_p_scale.set_draw_value(True)
                self.qp_p_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_p_scale.set_hexpand(True)
                self.qp_p_scale.connect('adjust-bounds', self.on_scale_adjust_bounds)

            def _setup_qp_b_row(self):
                self._setup_qp_b_scale()

                self.qp_b_row = Adw.ActionRow()
                self.qp_b_row.set_title('QP-B')
                self.qp_b_row.set_subtitle('Quantizer value for B-frames')
                self.qp_b_row.add_suffix(self.qp_b_scale)
                self.qp_b_row.set_sensitive(False)

            def _setup_qp_b_scale(self):
                self.qp_b_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                           min=video_codec.H264Nvenc.QP_MIN,
                                                           max=video_codec.H264Nvenc.QP_MAX,
                                                           step=1.0)
                self.qp_b_scale.set_value(20.0)
                self.qp_b_scale.set_digits(1)
                self.qp_b_scale.set_draw_value(True)
                self.qp_b_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_b_scale.set_hexpand(True)
                self.qp_b_scale.connect('adjust-bounds', self.on_scale_adjust_bounds)

            def _setup_rc_row(self):
                self._setup_rc_string_list()

                self.rc_row = Adw.ComboRow()
                self.rc_row.set_title('Rate Control')
                self.rc_row.set_subtitle('Rate control type')
                self.rc_row.set_model(self.rc_string_list)
                self.rc_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.rc_row.set_sensitive(False)

            def _setup_rc_string_list(self):
                self.rc_string_list = Gtk.StringList.new(video_codec.H264Nvenc.RATE_CONTROL)

            def _setup_rc_lookahead_row(self):
                self._setup_rc_lookahead_spin_button()

                self.rc_lookahead_row = Adw.ActionRow()
                self.rc_lookahead_row.set_title('Rate Control Lookahead')
                self.rc_lookahead_row.set_subtitle('Lookahead in frames')
                self.rc_lookahead_row.add_suffix(self.rc_lookahead_spin_button)
                self.rc_lookahead_row.set_sensitive(False)

            def _setup_rc_lookahead_spin_button(self):
                self.rc_lookahead_spin_button = Gtk.SpinButton()
                self.rc_lookahead_spin_button.set_range(video_codec.H264Nvenc.RC_LOOKAHEAD_MIN,
                                                        video_codec.H264Nvenc.RC_LOOKAHEAD_MAX)
                self.rc_lookahead_spin_button.set_digits(0)
                self.rc_lookahead_spin_button.set_increments(10, 50)
                self.rc_lookahead_spin_button.set_numeric(True)
                self.rc_lookahead_spin_button.set_snap_to_ticks(True)
                self.rc_lookahead_spin_button.set_value(0)
                self.rc_lookahead_spin_button.set_vexpand(False)
                self.rc_lookahead_spin_button.set_valign(Gtk.Align.CENTER)
                self.rc_lookahead_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_surfaces_row(self):
                self._setup_surfaces_spin_button()

                self.surfaces_row = Adw.ActionRow()
                self.surfaces_row.set_title('Surfaces')
                self.surfaces_row.set_subtitle('Surfaces')
                self.surfaces_row.add_suffix(self.surfaces_spin_button)
                self.surfaces_row.set_sensitive(False)

            def _setup_surfaces_spin_button(self):
                self.surfaces_spin_button = Gtk.SpinButton()
                self.surfaces_spin_button.set_range(video_codec.H264Nvenc.SURFACES_MIN,
                                                    video_codec.H264Nvenc.SURFACES_MAX)
                self.surfaces_spin_button.set_digits(0)
                self.surfaces_spin_button.set_increments(2, 8)
                self.surfaces_spin_button.set_numeric(True)
                self.surfaces_spin_button.set_snap_to_ticks(True)
                self.surfaces_spin_button.set_value(0)
                self.surfaces_spin_button.set_vexpand(False)
                self.surfaces_spin_button.set_valign(Gtk.Align.CENTER)
                self.surfaces_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_b_frames_row(self):
                self._setup_b_frames_spin_button()

                self.b_frames_row = Adw.ActionRow()
                self.b_frames_row.set_title('B-frames')
                self.b_frames_row.set_subtitle('Number of consecutive B-frames in GOP')
                self.b_frames_row.add_suffix(self.b_frames_spin_button)
                self.b_frames_row.set_sensitive(False)

            def _setup_b_frames_spin_button(self):
                self.b_frames_spin_button = Gtk.SpinButton()
                self.b_frames_spin_button.set_range(video_codec.H264Nvenc.B_FRAMES_MIN,
                                                    video_codec.H264Nvenc.B_FRAMES_MAX)
                self.b_frames_spin_button.set_digits(0)
                self.b_frames_spin_button.set_increments(1, 4)
                self.b_frames_spin_button.set_numeric(True)
                self.b_frames_spin_button.set_snap_to_ticks(True)
                self.b_frames_spin_button.set_value(0)
                self.b_frames_spin_button.set_vexpand(False)
                self.b_frames_spin_button.set_valign(Gtk.Align.CENTER)
                self.b_frames_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_refs_row(self):
                self._setup_refs_spin_button()

                self.refs_row = Adw.ActionRow()
                self.refs_row.set_title('Reference Frames')
                self.refs_row.set_subtitle('Consecutive number of key-frames in GOP')
                self.refs_row.add_suffix(self.refs_spin_button)
                self.refs_row.set_sensitive(False)

            def _setup_refs_spin_button(self):
                self.refs_spin_button = Gtk.SpinButton()
                self.refs_spin_button.set_range(video_codec.H264Nvenc.REFS_MIN, video_codec.H264Nvenc.REFS_MAX)
                self.refs_spin_button.set_digits(0)
                self.refs_spin_button.set_increments(1, 4)
                self.refs_spin_button.set_numeric(True)
                self.refs_spin_button.set_snap_to_ticks(True)
                self.refs_spin_button.set_value(0)
                self.refs_spin_button.set_vexpand(False)
                self.refs_spin_button.set_valign(Gtk.Align.CENTER)
                self.refs_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_no_scenecut_row(self):
                self._setup_no_scenecut_switch()

                self.no_scenecut_row = Adw.ActionRow()
                self.no_scenecut_row.set_title('No Scenecut')
                self.no_scenecut_row.set_subtitle('No Scenecut')
                self.no_scenecut_row.add_suffix(self.no_scenecut_switch)
                self.no_scenecut_row.set_sensitive(False)

            def _setup_no_scenecut_switch(self):
                self.no_scenecut_switch = Gtk.Switch()
                self.no_scenecut_switch.set_vexpand(False)
                self.no_scenecut_switch.set_valign(Gtk.Align.CENTER)
                self.no_scenecut_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_forced_idr_row(self):
                self._setup_forced_idr_switch()

                self.forced_idr_row = Adw.ActionRow()
                self.forced_idr_row.set_title('Forced IDR')
                self.forced_idr_row.set_subtitle('Forced IDR')
                self.forced_idr_row.add_suffix(self.forced_idr_switch)
                self.forced_idr_row.set_sensitive(False)

            def _setup_forced_idr_switch(self):
                self.forced_idr_switch = Gtk.Switch()
                self.forced_idr_switch.set_vexpand(False)
                self.forced_idr_switch.set_valign(Gtk.Align.CENTER)
                self.forced_idr_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_b_adapt_row(self):
                self._setup_b_adapt_switch()

                self.b_adapt_row = Adw.ActionRow()
                self.b_adapt_row.set_title('B-Adapt')
                self.b_adapt_row.set_subtitle('B-Adapt')
                self.b_adapt_row.add_suffix(self.b_adapt_switch)
                self.b_adapt_row.set_sensitive(False)

            def _setup_b_adapt_switch(self):
                self.b_adapt_switch = Gtk.Switch()
                self.b_adapt_switch.set_vexpand(False)
                self.b_adapt_switch.set_valign(Gtk.Align.CENTER)
                self.b_adapt_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_aq_mode_row(self):
                self._setup_aq_mode_radio_buttons()

                self.aq_mode_row = Adw.ActionRow()
                self.aq_mode_row.set_title('AQ Mode')
                self.aq_mode_row.set_subtitle('Adaptive quantizer mode')
                self.aq_mode_row.add_suffix(self.aq_mode_horizontal_box)
                self.aq_mode_row.set_sensitive(False)

            def _setup_aq_mode_radio_buttons(self):
                self.spatial_aq_check_button = Gtk.CheckButton(label='Spatial AQ')
                self.spatial_aq_check_button.set_active(True)
                self.spatial_aq_check_button.connect('toggled', self.on_spatial_aq_check_button_toggled)

                self.temporal_aq_check_button = Gtk.CheckButton(label='Temporal AQ')
                self.temporal_aq_check_button.set_group(self.spatial_aq_check_button)

                self.aq_mode_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.aq_mode_horizontal_box.append(self.spatial_aq_check_button)
                self.aq_mode_horizontal_box.append(self.temporal_aq_check_button)

            def _setup_non_ref_p_row(self):
                self._setup_non_ref_p_switch()

                self.non_ref_p_row = Adw.ActionRow()
                self.non_ref_p_row.set_title('Non-Ref P-frames')
                self.non_ref_p_row.set_subtitle('Allow for non-reference P-frames')
                self.non_ref_p_row.add_suffix(self.non_ref_p_switch)
                self.non_ref_p_row.set_sensitive(False)

            def _setup_non_ref_p_switch(self):
                self.non_ref_p_switch = Gtk.Switch()
                self.non_ref_p_switch.set_vexpand(False)
                self.non_ref_p_switch.set_valign(Gtk.Align.CENTER)
                self.non_ref_p_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_strict_gop_row(self):
                self._setup_strict_gop_switch()

                self.strict_gop_row = Adw.ActionRow()
                self.strict_gop_row.set_title('Strict GOP')
                self.strict_gop_row.set_subtitle('Strict GOP')
                self.strict_gop_row.add_suffix(self.strict_gop_switch)
                self.strict_gop_row.set_sensitive(False)

            def _setup_strict_gop_switch(self):
                self.strict_gop_switch = Gtk.Switch()
                self.strict_gop_switch.set_vexpand(False)
                self.strict_gop_switch.set_valign(Gtk.Align.CENTER)
                self.strict_gop_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_aq_strength_row(self):
                self._setup_aq_strength_spin_button()

                self.aq_strength_row = Adw.ActionRow()
                self.aq_strength_row.set_title('AQ Strength')
                self.aq_strength_row.set_subtitle('Adaptive quantizer strength')
                self.aq_strength_row.add_suffix(self.aq_strength_spin_button)
                self.aq_strength_row.set_sensitive(False)

            def _setup_aq_strength_spin_button(self):
                self.aq_strength_spin_button = Gtk.SpinButton()
                self.aq_strength_spin_button.set_range(video_codec.H264Nvenc.AQ_STRENGTH_MIN,
                                                       video_codec.H264Nvenc.AQ_STRENGTH_MAX)
                self.aq_strength_spin_button.set_digits(0)
                self.aq_strength_spin_button.set_increments(1, 4)
                self.aq_strength_spin_button.set_numeric(True)
                self.aq_strength_spin_button.set_snap_to_ticks(True)
                self.aq_strength_spin_button.set_value(8)
                self.aq_strength_spin_button.set_vexpand(False)
                self.aq_strength_spin_button.set_valign(Gtk.Align.CENTER)
                self.aq_strength_spin_button.connect('value-changed', self.on_widget_changed_clicked_set)

            def _setup_bluray_compat_row(self):
                self._setup_bluray_compat_switch()

                self.bluray_compat_row = Adw.ActionRow()
                self.bluray_compat_row.set_title('Blu-Ray Compatibility')
                self.bluray_compat_row.add_suffix(self.bluray_compat_switch)
                self.bluray_compat_row.set_sensitive(False)

            def _setup_bluray_compat_switch(self):
                self.bluray_compat_switch = Gtk.Switch()
                self.bluray_compat_switch.set_vexpand(False)
                self.bluray_compat_switch.set_valign(Gtk.Align.CENTER)
                self.bluray_compat_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_weighted_pred_row(self):
                self._setup_weighted_pred_switch()

                self.weighted_pred_row = Adw.ActionRow()
                self.weighted_pred_row.set_title('Weighted Predicition')
                self.weighted_pred_row.set_subtitle('Weighted predicition')
                self.weighted_pred_row.add_suffix(self.weighted_pred_switch)
                self.weighted_pred_row.set_sensitive(False)

            def _setup_weighted_pred_switch(self):
                self.weighted_pred_switch = Gtk.Switch()
                self.weighted_pred_switch.set_vexpand(False)
                self.weighted_pred_switch.set_valign(Gtk.Align.CENTER)
                self.weighted_pred_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def _setup_coder_row(self):
                self._setup_coder_string_list()

                self.coder_row = Adw.ComboRow()
                self.coder_row.set_title('Coder')
                self.coder_row.set_subtitle('Coder')
                self.coder_row.set_model(self.coder_string_list)
                self.coder_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.coder_row.set_sensitive(False)

            def _setup_coder_string_list(self):
                self.coder_string_list = Gtk.StringList.new(video_codec.H264Nvenc.CODER)

            def _setup_b_ref_mode_row(self):
                self._setup_b_ref_mode_string_list()

                self.b_ref_mode_row = Adw.ComboRow()
                self.b_ref_mode_row.set_title('B-Ref Mode')
                self.b_ref_mode_row.set_subtitle('B-Ref Mode')
                self.b_ref_mode_row.set_model(self.b_ref_mode_string_list)
                self.b_ref_mode_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
                self.b_ref_mode_row.set_sensitive(False)

            def _setup_b_ref_mode_string_list(self):
                self.b_ref_mode_string_list = Gtk.StringList.new(video_codec.H264Nvenc.BREF_MODE)

            def _setup_tier_row(self):
                self._setup_tier_switch()

                self.tier_row = Adw.ActionRow()
                self.tier_row.set_title('Tier')
                self.tier_row.set_subtitle('Tier')
                self.tier_row.add_suffix(self.tier_switch)
                self.tier_row.set_sensitive(False)

            def _setup_tier_switch(self):
                self.tier_switch = Gtk.Switch()
                self.tier_switch.set_vexpand(False)
                self.tier_switch.set_valign(Gtk.Align.CENTER)
                self.tier_switch.connect('state-set', self.on_widget_changed_clicked_set)

            def show_settings_not_compatible_message(self, is_settings_compatible: bool):
                if is_settings_compatible:
                    return

                message_text = 'Settings Not Compatible'
                secondary_message_text = 'Current codec settings may not work with this computer.'
                settings_not_compatible_message_dialog = Gtk.MessageDialog(
                    transient_for=self.inputs_page.main_window_widgets.main_window,
                    modal=True,
                    destroy_with_parent=True,
                    buttons=Gtk.ButtonsType.CLOSE,
                    text=message_text,
                    secondary_text=secondary_message_text
                )
                settings_not_compatible_message_dialog.connect('response',
                                                               self._on_settings_not_compatible_message_dialog_response)
                settings_not_compatible_message_dialog.show()

            def _on_settings_not_compatible_message_dialog_response(self, message_dialog, response):
                message_dialog.close()
                message_dialog.destroy()

            def set_h264_advanced_settings_state(self):
                self._is_h264_state = True
                self._is_h265_state = False

                self.tier_row.set_sensitive(False)
                self.b_adapt_row.set_sensitive(self.advanced_settings_switch.get_active() and True)
                self.coder_row.set_sensitive(self.advanced_settings_switch.get_active() and True)
                self._repopulate_combo_row(self.preset_row, video_codec.H264Nvenc.PRESET)
                self._repopulate_combo_row(self.profile_row, video_codec.H264Nvenc.PROFILE)
                self._repopulate_combo_row(self.level_row, video_codec.H264Nvenc.LEVEL)
                self._repopulate_combo_row(self.tune_row, video_codec.H264Nvenc.TUNE)
                self._repopulate_combo_row(self.rc_row, video_codec.H264Nvenc.RATE_CONTROL)
                self._repopulate_combo_row(self.multi_pass_row, video_codec.H264Nvenc.MULTI_PASS)
                self._repopulate_combo_row(self.b_ref_mode_row, video_codec.H264Nvenc.BREF_MODE)

            def set_h265_advanced_settings_state(self):
                self._is_h264_state = False
                self._is_h265_state = True

                self.tier_row.set_sensitive(self.advanced_settings_switch.get_active() and True)
                self.b_adapt_row.set_sensitive(False)
                self.coder_row.set_sensitive(False)
                self._repopulate_combo_row(self.preset_row, video_codec.HevcNvenc.PRESET)
                self._repopulate_combo_row(self.profile_row, video_codec.HevcNvenc.PROFILE)
                self._repopulate_combo_row(self.level_row, video_codec.HevcNvenc.LEVEL)
                self._repopulate_combo_row(self.tune_row, video_codec.HevcNvenc.TUNE)
                self._repopulate_combo_row(self.rc_row, video_codec.HevcNvenc.RATE_CONTROL)
                self._repopulate_combo_row(self.multi_pass_row, video_codec.HevcNvenc.MULTI_PASS)
                self._repopulate_combo_row(self.b_ref_mode_row, video_codec.HevcNvenc.BREF_MODE)

            def _repopulate_combo_row(self, combo_row: Adw.ComboRow, items_list: list):
                self.is_widgets_setting_up = True

                model_string_list = Gtk.StringList.new(items_list)
                combo_row.set_model(model_string_list)

                self.is_widgets_setting_up = False

            def set_widgets_setting_up(self, is_widgets_setting_up: bool):
                self.is_widgets_setting_up = is_widgets_setting_up

            def apply_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.set_widgets_setting_up, True)
                self._apply_preset_setting_to_widgets(encode_task)
                self._apply_profile_setting_to_widgets(encode_task)
                self._apply_level_setting_to_widgets(encode_task)
                self._apply_tune_setting_to_widgets(encode_task)
                self._apply_rate_type_settings_to_widgets(encode_task)
                self._apply_qp_setting_to_widgets(encode_task)
                self._apply_bitrate_type_settings_to_widgets(encode_task)
                self._apply_advanced_settings_to_widgets(encode_task)
                self._apply_advanced_settings_state_to_widgets(encode_task)
                GLib.idle_add(self.set_widgets_setting_up, False)

            def _apply_preset_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.preset_row.set_selected, encode_task.get_video_codec().preset)

            def _apply_profile_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.profile_row.set_selected, encode_task.get_video_codec().profile)

            def _apply_level_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.level_row.set_selected, encode_task.get_video_codec().level)

            def _apply_tune_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.tune_row.set_selected, encode_task.get_video_codec().tune)

            def _apply_rate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_qp_enabled:
                    GLib.idle_add(self.qp_check_button.set_active, True)
                else:
                    GLib.idle_add(self.bitrate_check_button.set_active, True)

            def _apply_qp_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.qp_scale.set_value, encode_task.get_video_codec().qp)

            def _apply_bitrate_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.bitrate_spin_button.set_value, encode_task.get_video_codec().bitrate)

            def _apply_bitrate_type_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().is_bitrate_enabled:
                    if encode_task.get_video_codec().cbr:
                        GLib.idle_add(self.constant_bitrate_check_button.set_active, True)
                else:
                    GLib.idle_add(self.average_bitrate_check_button.set_active, True)

                GLib.idle_add(self.multi_pass_row.set_selected, encode_task.get_video_codec().multi_pass)

            def _apply_advanced_settings_state_to_widgets(self, encode_task: task.Encode):
                if video_codec.is_codec_h264_nvenc(encode_task):
                    GLib.idle_add(self.set_h264_advanced_settings_state)
                else:
                    GLib.idle_add(self.set_h265_advanced_settings_state)

            def _apply_advanced_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.advanced_settings_switch.set_active,
                              encode_task.get_video_codec().is_advanced_enabled)
                self._apply_custom_qp_settings_to_widgets(encode_task)
                self._apply_rc_setting_to_widgets(encode_task)
                self._apply_rc_lookahead_setting_to_widgets(encode_task)
                self._apply_surfaces_setting_to_widgets(encode_task)
                self._apply_tier_setting_to_widgets(encode_task)
                self._apply_b_frames_setting_to_widgets(encode_task)
                self._apply_refs_setting_to_widgets(encode_task)
                self._apply_no_scenecut_setting_to_widgets(encode_task)
                self._apply_forced_idr_setting_to_widgets(encode_task)
                self._apply_b_adapt_setting_to_widgets(encode_task)
                self._apply_aq_method_settings_to_widgets(encode_task)
                self._apply_non_ref_p_setting_to_widgets(encode_task)
                self._apply_strict_gop_setting_to_widgets(encode_task)
                self._apply_aq_strength_setting_to_widgets(encode_task)
                self._apply_bluray_compat_setting_to_widgets(encode_task)
                self._apply_weighted_pred_setting_to_widgets(encode_task)
                self._apply_coder_setting_to_widgets(encode_task)
                self._apply_b_ref_mode_setting_to_widgets(encode_task)

            def _apply_custom_qp_settings_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.custom_quantizer_switch.set_active,
                              encode_task.get_video_codec().is_qp_custom_enabled)
                GLib.idle_add(self.qp_i_scale.set_value, encode_task.get_video_codec().qp_i)
                GLib.idle_add(self.qp_p_scale.set_value, encode_task.get_video_codec().qp_p)
                GLib.idle_add(self.qp_b_scale.set_value, encode_task.get_video_codec().qp_b)

            def _apply_rc_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rc_row.set_selected, encode_task.get_video_codec().rc)

            def _apply_rc_lookahead_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.rc_lookahead_spin_button.set_value, encode_task.get_video_codec().rc_lookahead)

            def _apply_surfaces_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.surfaces_spin_button.set_value, encode_task.get_video_codec().surfaces)

            def _apply_tier_setting_to_widgets(self, encode_task: task.Encode):
                if video_codec.is_codec_hevc_nvenc(encode_task):
                    GLib.idle_add(self.tier_switch.set_active, encode_task.get_video_codec().tier)

            def _apply_b_frames_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_frames_spin_button.set_value, encode_task.get_video_codec().b_frames)

            def _apply_refs_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.refs_spin_button.set_value, encode_task.get_video_codec().refs)

            def _apply_no_scenecut_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.no_scenecut_switch.set_active, encode_task.get_video_codec().no_scenecut)

            def _apply_forced_idr_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.forced_idr_switch.set_active, encode_task.get_video_codec().forced_idr)

            def _apply_b_adapt_setting_to_widgets(self, encode_task: task.Encode):
                if video_codec.is_codec_h264_nvenc(encode_task):
                    GLib.idle_add(self.b_adapt_switch.set_active, encode_task.get_video_codec().b_adapt)

            def _apply_aq_method_settings_to_widgets(self, encode_task: task.Encode):
                if encode_task.get_video_codec().spatial_aq:
                    GLib.idle_add(self.spatial_aq_check_button.set_active, True)
                else:
                    GLib.idle_add(self.temporal_aq_check_button.set_active, True)

            def _apply_non_ref_p_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.non_ref_p_switch.set_active, encode_task.get_video_codec().non_ref_p)

            def _apply_strict_gop_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.strict_gop_switch.set_active, encode_task.get_video_codec().strict_gop)

            def _apply_aq_strength_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.aq_strength_spin_button.set_value, encode_task.get_video_codec().aq_strength)

            def _apply_bluray_compat_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.bluray_compat_switch.set_active, encode_task.get_video_codec().bluray_compat)

            def _apply_weighted_pred_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.weighted_pred_switch.set_active, encode_task.get_video_codec().weighted_pred)

            def _apply_coder_setting_to_widgets(self, encode_task: task.Encode):
                if video_codec.is_codec_h264_nvenc(encode_task):
                    GLib.idle_add(self.coder_row.set_selected, encode_task.get_video_codec().coder)

            def _apply_b_ref_mode_setting_to_widgets(self, encode_task: task.Encode):
                GLib.idle_add(self.b_ref_mode_row.set_selected, encode_task.get_video_codec().b_ref_mode)

            def apply_settings_from_widgets(self, is_compatibilty_check_enabled=True):
                if self._is_h264_state:
                    nvenc_settings = video_codec.H264Nvenc()
                else:
                    nvenc_settings = video_codec.HevcNvenc()

                nvenc_settings.preset = self.preset_row.get_selected()
                nvenc_settings.profile = self.profile_row.get_selected()
                nvenc_settings.level = self.level_row.get_selected()
                nvenc_settings.tune = self.tune_row.get_selected()
                nvenc_settings.is_advanced_enabled = self.advanced_settings_switch.get_active()

                self._apply_rate_type_settings_from_widgets(nvenc_settings)

                if self.advanced_settings_switch.get_active():
                    nvenc_settings.rc = self.rc_row.get_selected()
                    nvenc_settings.rc_lookahead = self.rc_lookahead_spin_button.get_value_as_int()
                    nvenc_settings.surfaces = self.surfaces_spin_button.get_value_as_int()
                    nvenc_settings.b_frames = self.b_frames_spin_button.get_value_as_int()
                    nvenc_settings.refs = self.refs_spin_button.get_value_as_int()
                    nvenc_settings.no_scenecut = self.no_scenecut_switch.get_active()
                    nvenc_settings.forced_idr = self.forced_idr_switch.get_active()
                    nvenc_settings.non_ref_p = self.non_ref_p_switch.get_active()
                    nvenc_settings.strict_gop = self.strict_gop_switch.get_active()
                    nvenc_settings.bluray_compat = self.bluray_compat_switch.get_active()
                    nvenc_settings.weighted_pred = self.weighted_pred_switch.get_active()
                    nvenc_settings.b_ref_mode = self.b_ref_mode_row.get_selected()

                    self._apply_tier_setting_from_widgets(nvenc_settings)
                    self._apply_coder_setting_from_widgets(nvenc_settings)
                    self._apply_b_adapt_setting_from_widgets(nvenc_settings)
                    self._apply_aq_settings_from_widgets(nvenc_settings)
                    self._apply_qp_custom_settings_from_widgets(nvenc_settings)

                is_settings_compatible = None

                for input_row in self.inputs_page.get_selected_rows():
                    encode_task = input_row.encode_task
                    encode_task.set_video_codec(copy.deepcopy(nvenc_settings))

                    if is_settings_compatible is None:
                        is_settings_compatible = ffmpeg_helper.Compatibility.is_video_codec_compatible(encode_task)
                    print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

                if is_compatibilty_check_enabled:
                    GLib.idle_add(self.show_settings_not_compatible_message, is_settings_compatible)

                self.inputs_page.update_preview_page_encode_task()

            def _apply_rate_type_settings_from_widgets(self,
                                                       nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self.qp_check_button.get_active():
                    nvenc_settings.qp = self.qp_scale.get_value()
                else:
                    nvenc_settings.bitrate = self.bitrate_spin_button.get_value_as_int()
                    nvenc_settings.cbr = self.constant_bitrate_check_button.get_active()
                    nvenc_settings.multi_pass = self.multi_pass_row.get_selected()

            def _apply_tier_setting_from_widgets(self, nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self._is_h265_state:
                    nvenc_settings.tier = self.tier_switch.get_active()

            def _apply_coder_setting_from_widgets(self, nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self._is_h264_state:
                    nvenc_settings.coder = self.coder_row.get_selected()

            def _apply_b_adapt_setting_from_widgets(self,
                                                    nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self._is_h264_state:
                    nvenc_settings.b_adapt = self.b_adapt_switch.get_active()

            def _apply_aq_settings_from_widgets(self, nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self.temporal_aq_check_button.get_active():
                    nvenc_settings.temporal_aq = True
                else:
                    nvenc_settings.spatial_aq = True
                    nvenc_settings.aq_strength = self.aq_strength_spin_button.get_value_as_int()

            def _apply_qp_custom_settings_from_widgets(self,
                                                       nvenc_settings: video_codec.H264Nvenc | video_codec.HevcNvenc):
                if self.custom_quantizer_switch.get_active():
                    nvenc_settings.is_qp_custom_enabled = True
                    nvenc_settings.qp_i = self.qp_i_scale.get_value()
                    nvenc_settings.qp_p = self.qp_p_scale.get_value()
                    nvenc_settings.qp_b = self.qp_b_scale.get_value()

            def on_widget_changed_clicked_set(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                threading.Thread(target=self.apply_settings_from_widgets, args=()).start()

            def on_scale_adjust_bounds(self, scale, value):
                if self.is_widgets_setting_up:
                    return

                if int(value) != int(scale.get_value()):
                    threading.Thread(target=self.apply_settings_from_widgets,
                                     args=(),
                                     kwargs={'is_compatibilty_check_enabled': False}).start()

            def on_qp_check_button_toggled(self, check_button):
                self.custom_quantizer_row.set_sensitive(check_button.get_active())

                if check_button.get_active():
                    self.rate_type_settings_stack.set_visible_child_name('qp_page')
                    self.rate_type_settings_row.set_title('QP')
                    self.rate_type_settings_row.set_subtitle('Constant Quantizer: P-frames')
                    self.multi_pass_row.set_sensitive(False)

                    self.on_widget_changed_clicked_set(check_button)
                else:
                    self.custom_quantizer_switch.set_active(False)

            def on_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_settings_stack.set_visible_child_name('bitrate_page')
                    self.rate_type_settings_row.set_title('Bitrate')
                    self.rate_type_settings_row.set_subtitle('Encoder bitrate')
                    self.multi_pass_row.set_sensitive(True)

                self.on_widget_changed_clicked_set(check_button)

            def on_custom_quantizer_switch_state_set(self, switch, user_data):
                self.qp_i_row.set_sensitive(switch.get_active())
                self.qp_p_row.set_sensitive(switch.get_active())
                self.qp_b_row.set_sensitive(switch.get_active())

                self.on_widget_changed_clicked_set(switch)

            def on_spatial_aq_check_button_toggled(self, check_button):
                self.aq_strength_row.set_sensitive(check_button.get_active())

                self.on_widget_changed_clicked_set(check_button)

            def on_advanced_settings_switch_state_set(self, switch, user_data):
                is_state_enabled = self.advanced_settings_switch.get_active()
                self._set_qp_custom_rows_enabled(is_state_enabled)
                self.rc_row.set_sensitive(is_state_enabled)
                self.rc_lookahead_row.set_sensitive(is_state_enabled)
                self.surfaces_row.set_sensitive(is_state_enabled)
                self._set_tier_row_enabled(is_state_enabled)
                self.refs_row.set_sensitive(is_state_enabled)
                self.forced_idr_row.set_sensitive(is_state_enabled)
                self.non_ref_p_row.set_sensitive(is_state_enabled)
                self.no_scenecut_row.set_sensitive(is_state_enabled)
                self.strict_gop_row.set_sensitive(is_state_enabled)
                self.b_frames_row.set_sensitive(is_state_enabled)
                self.b_ref_mode_row.set_sensitive(is_state_enabled)
                self._set_b_adapt_row_enabled(is_state_enabled)
                self.weighted_pred_row.set_sensitive(is_state_enabled)
                self._set_aq_rows_enabled(is_state_enabled)
                self._set_coder_row_enabled(is_state_enabled)
                self.bluray_compat_row.set_sensitive(is_state_enabled)

                self.on_widget_changed_clicked_set(switch)

            def _set_qp_custom_rows_enabled(self, is_state_enabled: bool):
                self.custom_quantizer_row.set_sensitive(self.qp_check_button.get_active() and is_state_enabled)
                self.qp_i_row.set_sensitive(self.custom_quantizer_switch.get_active())
                self.qp_p_row.set_sensitive(self.custom_quantizer_switch.get_active())
                self.qp_b_row.set_sensitive(self.custom_quantizer_switch.get_active())

            def _set_tier_row_enabled(self, is_state_enabled: bool):
                self.tier_row.set_sensitive(self._is_h265_state and is_state_enabled)

            def _set_b_adapt_row_enabled(self, is_state_enabled: bool):
                self.b_adapt_row.set_sensitive(self._is_h264_state and is_state_enabled)

            def _set_aq_rows_enabled(self, is_state_enabled: bool):
                self.aq_mode_row.set_sensitive(is_state_enabled)
                self.aq_strength_row.set_sensitive(self.spatial_aq_check_button.get_active() and is_state_enabled)

            def _set_coder_row_enabled(self, is_state_enabled: bool):
                self.coder_row.set_sensitive(self._is_h264_state and is_state_enabled)

        class CodecSettingsNoAvailPage(Gtk.Box):
            def __init__(self):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self.settings_no_avail_label = Gtk.Label(label='Codec Settings Not Available')

                self.append(self.settings_no_avail_label)
                self.set_sensitive(False)

    class AudioCodecSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page
            self.is_widgets_setting_up = False

            self._setup_audio_stream_settings()

            audio_codec_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            audio_codec_settings_vertical_box.append(self.audio_stream_settings_group)
            audio_codec_settings_vertical_box.set_margin_top(20)
            audio_codec_settings_vertical_box.set_margin_bottom(20)
            audio_codec_settings_vertical_box.set_margin_start(20)
            audio_codec_settings_vertical_box.set_margin_end(20)

            self.set_child(audio_codec_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_audio_stream_settings(self):
            add_audio_stream_button_child = Adw.ButtonContent.new()
            add_audio_stream_button_child.set_label('Add Stream')
            add_audio_stream_button_child.set_icon_name('list-add-symbolic')

            add_audio_stream_button = Gtk.Button()
            add_audio_stream_button.set_child(add_audio_stream_button_child)
            add_audio_stream_button.connect('clicked', self.on_add_audio_stream_button_clicked)

            self.audio_stream_settings_group = SettingsSidebarWidgets.SettingsGroup()
            self.audio_stream_settings_group.set_title('Audio Streams')
            self.audio_stream_settings_group.set_header_suffix(add_audio_stream_button)

        def update_audio_streams_from_extension(self, general_settings_page):
            audio_codecs_list = self._get_codecs_list_from_extension(general_settings_page.get_selected_extension())

            for audio_stream_row in self.audio_stream_settings_group.children:
                audio_stream_row.is_widgets_setting_up = True
                selected_audio_codec = audio_stream_row.audio_codec_row.get_selected_item().get_string()

                audio_stream_row.repopulate_audio_codec_row(audio_codecs_list)

                if selected_audio_codec in audio_codecs_list:
                    audio_stream_row.audio_codec_row.set_selected(audio_codecs_list.index(selected_audio_codec))
                else:
                    audio_stream_row.audio_codec_row.set_selected(1)

                audio_stream_row.is_widgets_setting_up = False

                audio_stream_row.update_subtitle()
                audio_stream_row.apply_settings_from_widgets()

        @staticmethod
        def _get_codecs_list_from_extension(extension: str) -> list[str]:
            if extension == media_file.MP4_EXTENTION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_MP4_UI
            elif extension == media_file.MKV_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_MKV_UI
            elif extension == media_file.TS_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_TS_UI
            elif extension == media_file.WEBM_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_WEBM_UI
            elif extension == media_file.M4A_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_M4A_UI
            elif extension == media_file.AAC_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_AAC_UI
            elif extension == media_file.OGG_EXTENSION:
                audio_codecs_list = audio_codec.AUDIO_CODECS_OGG_UI
            else:
                audio_codecs_list = ['N/A']

            return audio_codecs_list

        def set_available_state(self):
            self.audio_stream_settings_group.set_sensitive(True)

        def set_not_available_state(self):
            self.audio_stream_settings_group.remove_children()
            self.audio_stream_settings_group.set_sensitive(False)

        def set_widgets_setting_up(self, is_widgets_setting_up: bool):
            self.is_widgets_setting_up = is_widgets_setting_up

        def apply_settings_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.set_widgets_setting_up, True)

            if self._is_encode_task_valid(encode_task):
                GLib.idle_add(self.set_available_state)
                GLib.idle_add(self.audio_stream_settings_group.remove_children)
                self._apply_audio_streams_to_widgets(encode_task)
            else:
                GLib.idle_add(self.set_not_available_state)

            GLib.idle_add(self.set_widgets_setting_up, False)

        @staticmethod
        def _is_encode_task_valid(encode_task: task.Encode) -> bool:
            return encode_task.input_file.is_audio or encode_task.input_file.is_folder

        def _apply_audio_streams_to_widgets(self, encode_task: task.Encode):
            for audio_stream, audio_stream_codec in encode_task.audio_streams.items():
                GLib.idle_add(self._create_audio_stream_row_from_task, encode_task, audio_stream, audio_stream_codec)

        def _create_audio_stream_row_from_task(self,
                                               encode_task: task.Encode,
                                               audio_stream: stream.AudioStream,
                                               audio_stream_codec):
            audio_stream_row = self.AudioStreamRow(self,
                                                   encode_task,
                                                   audio_stream,
                                                   audio_stream_codec,
                                                   self.audio_stream_settings_group.number_of_children + 1)
            self.audio_stream_settings_group.add(audio_stream_row)

        def on_add_audio_stream_button_clicked(self, button):
            if self.audio_stream_settings_group.number_of_children < 4:
                encode_task = self.inputs_page.inputs_list_box.get_selected_row().encode_task
                new_audio_stream = copy.deepcopy(encode_task.input_file.audio_streams[0])
                encode_task.add_audio_stream(new_audio_stream)
                new_audio_stream_codec = audio_codec.Aac(encode_task.get_audio_stream_index(new_audio_stream))
                encode_task.set_audio_stream_codec(new_audio_stream, new_audio_stream_codec)
                audio_stream_row = self.AudioStreamRow(self,
                                                       encode_task,
                                                       new_audio_stream,
                                                       new_audio_stream_codec,
                                                       self.audio_stream_settings_group.number_of_children + 1)
                self.audio_stream_settings_group.add(audio_stream_row)

        class AudioStreamRow(Adw.ExpanderRow):
            def __init__(self,
                         audio_codec_settings_page,
                         encode_task: task.Encode,
                         audio_stream: stream.AudioStream,
                         audio_stream_codec,
                         row_count: int):
                super().__init__()

                self.audio_codec_settings_page = audio_codec_settings_page
                self.encode_task = encode_task
                self.audio_stream = audio_stream
                self.row_count = row_count
                self.audio_stream_codec = audio_stream_codec
                self.is_widgets_setting_up = False

                self._setup_audio_stream_row()

            def _setup_audio_stream_row(self):
                self._setup_stream_row()
                self._setup_codec_row()
                self._setup_channels_setting_row()
                self._setup_bitrate_setting_row()
                self._setup_remove_button()

                self.update_title()
                self.update_subtitle()

                self.add_row(self.stream_row)
                self.add_row(self.audio_codec_row)
                self.add_row(self.channels_row)
                self.add_row(self.bitrate_setting_row)
                self.add_prefix(self.remove_button)

                if self.audio_stream_codec is None:
                    self.set_codec_copy_state()

            def _setup_stream_row(self):
                self.stream_row = Adw.ComboRow()
                self.stream_row.set_title('Selected Stream')
                self._setup_stream_combo_row()
                self.stream_row.set_use_subtitle(True)
                self.stream_row.connect('notify::selected-item', self.on_stream_combo_row_notify_selected_item)

            def _setup_stream_combo_row(self):
                stream_string_list = Gtk.StringList.new()
                selected_stream_index = 0

                for audio_stream in self.encode_task.input_file.audio_streams:
                    stream_string_list.append(audio_stream.get_info())

                    if audio_stream.index == self.audio_stream.index:
                        selected_stream_index = self.encode_task.input_file.audio_streams.index(audio_stream)

                self.stream_row.set_model(stream_string_list)
                self.stream_row.set_selected(selected_stream_index)

            def _setup_codec_row(self):
                self.audio_codec_row = Adw.ComboRow()
                self.audio_codec_row.set_title('Codec')
                self.audio_codec_row.set_subtitle('Audio codec to encode the audio stream')
                self._setup_audio_codecs_combo_row()
                self.audio_codec_row.connect('notify::selected-item', self.on_audio_codec_combo_row_notify_selected_item)

            def _setup_audio_codecs_combo_row(self):
                if self.audio_stream_codec:
                    audio_codec_name = self.audio_stream_codec.codec_name
                else:
                    audio_codec_name = 'copy'

                if self.encode_task.output_file.extension == '.mp4':
                    audio_codecs = audio_codec.AUDIO_CODECS_MP4_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_MP4.index(audio_codec_name)
                elif self.encode_task.output_file.extension == '.mkv':
                    audio_codecs = audio_codec.AUDIO_CODECS_MKV_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_MKV.index(audio_codec_name)
                elif self.encode_task.output_file.extension == '.ts':
                    audio_codecs = audio_codec.AUDIO_CODECS_TS_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_TS.index(audio_codec_name)
                elif self.encode_task.output_file.extension == '.webm':
                    audio_codecs = audio_codec.AUDIO_CODECS_WEBM_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_WEBM.index(audio_codec_name)
                elif self.encode_task.output_file.extension == '.m4a':
                    audio_codecs = audio_codec.AUDIO_CODECS_M4A_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_M4A.index(audio_codec_name)
                elif self.encode_task.output_file.extension == '.aac':
                    audio_codecs = audio_codec.AUDIO_CODECS_AAC_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_AAC.index(audio_codec_name)
                else:
                    audio_codecs = audio_codec.AUDIO_CODECS_OGG_UI
                    audio_codec_index = audio_codec.AUDIO_CODECS_OGG.index(audio_codec_name)

                audio_codecs_string_list = Gtk.StringList.new(audio_codecs)
                self.audio_codec_row.set_model(audio_codecs_string_list)
                self.audio_codec_row.set_selected(audio_codec_index)

            def _setup_channels_setting_row(self):
                self.channels_row = Adw.ComboRow()
                self.channels_row.set_title('Channels')
                self.channels_row.set_subtitle('Number of audio channels the codec should use')
                self._setup_channels_combo_row()
                self.channels_row.connect('notify::selected-item', self.on_channels_combo_row_notify_selected_item)

            def _setup_channels_combo_row(self):
                if self.audio_stream_codec:
                    channels_string_list = Gtk.StringList.new(self.audio_stream_codec.CHANNELS_UI)
                    channels_index = self.audio_stream_codec.channels
                else:
                    channels_string_list = Gtk.StringList.new(['auto'])
                    channels_index = 0

                self.channels_row.set_model(channels_string_list)
                self.channels_row.set_selected(channels_index)

            def _setup_bitrate_setting_row(self):
                self._setup_bitrate_spin_button()

                self.bitrate_setting_row = Adw.ActionRow()
                self.bitrate_setting_row.set_title('Bitrate')
                self.bitrate_setting_row.set_subtitle('Bitrate the codec should use in kbps')
                self.bitrate_setting_row.add_suffix(self.bitrate_spin_button)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(32, 996)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(32.0, 64.0)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)

                if self.audio_stream_codec:
                    self.bitrate_spin_button.set_value(self.audio_stream_codec.bitrate)
                else:
                    self.bitrate_spin_button.set_value(128)

                self.bitrate_spin_button.set_vexpand(False)
                self.bitrate_spin_button.set_valign(Gtk.Align.CENTER)
                self.bitrate_spin_button.connect('value-changed', self.on_bitrate_spin_button_value_changed)

            def _setup_remove_button(self):
                self.remove_button = Gtk.Button.new_from_icon_name('list-remove-symbolic')
                self.remove_button.set_vexpand(False)
                self.remove_button.set_valign(Gtk.Align.CENTER)
                self.remove_button.connect('clicked', self.on_remove_button_clicked)

            def update_title(self):
                self.set_title(''.join(['Audio Stream ', str(self.row_count)]))

            def update_subtitle(self):
                codec_name = self.audio_codec_row.get_selected_item().get_string()

                if self.channels_row.get_selected() < 1 or self.audio_codec_row.get_selected() < 1:
                    channels = ' '.join([str(self.audio_stream.channels), 'channels'])
                else:
                    channels = ' '.join([self.channels_row.get_selected_item().get_string(), 'channels'])

                self.set_subtitle(','.join([codec_name, channels]))

            def _update_channels_row(self):
                self.is_widgets_setting_up = True

                if self.audio_stream_codec:
                    channels_string_list = Gtk.StringList.new(self.audio_stream_codec.CHANNELS_UI)
                    channels_index = self.audio_stream_codec.channels
                else:
                    channels_string_list = Gtk.StringList.new(['auto'])
                    channels_index = 0

                self.channels_row.set_model(channels_string_list)
                self.channels_row.set_selected(channels_index)

                self.is_widgets_setting_up = False

            def set_codec_copy_state(self):
                self.channels_row.set_sensitive(False)
                self.bitrate_setting_row.set_sensitive(False)

            def repopulate_audio_codec_row(self, audio_codecs_list: list):
                audio_codecs_string_list = Gtk.StringList.new(audio_codecs_list)
                self.audio_codec_row.set_model(audio_codecs_string_list)

            def apply_settings_from_widgets(self):
                self._apply_stream_setting_from_widgets()

                if self.audio_codec_row.get_selected_item().get_string() == 'aac':
                    audio_stream_codec = audio_codec.Aac(self.encode_task.get_audio_stream_index(self.audio_stream))
                elif self.audio_codec_row.get_selected_item().get_string() == 'opus':
                    audio_stream_codec = audio_codec.Opus(self.encode_task.get_audio_stream_index(self.audio_stream))
                else:
                    self.encode_task.set_audio_stream_codec(self.audio_stream, None)

                    return

                audio_stream_codec.channels = self.channels_row.get_selected()
                audio_stream_codec.bitrate = self.bitrate_spin_button.get_value_as_int()

                self.encode_task.set_audio_stream_codec(self.audio_stream, audio_stream_codec)
                print(ffmpeg_helper.Args.get_args(self.encode_task, cli_args=True))

            def _apply_stream_setting_from_widgets(self):
                new_audio_stream = copy.deepcopy(
                    self.encode_task.input_file.audio_streams[self.stream_row.get_selected()])
                self.encode_task.audio_streams = OrderedDict(
                    (new_audio_stream if audio_stream is self.audio_stream else audio_stream, codec) for
                    audio_stream, codec in self.encode_task.audio_streams.items())
                self.audio_stream = new_audio_stream

            def on_remove_button_clicked(self, button):
                self.encode_task.remove_audio_stream(self.audio_stream)
                self.audio_codec_settings_page.audio_stream_settings_group.remove(self)

            def on_stream_combo_row_notify_selected_item(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                self.apply_settings_from_widgets()

            def on_bitrate_spin_button_value_changed(self, spin_button):
                if self.is_widgets_setting_up:
                    return

                self.apply_settings_from_widgets()

            def on_channels_combo_row_notify_selected_item(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                self.update_subtitle()
                self.apply_settings_from_widgets()

            def on_audio_codec_combo_row_notify_selected_item(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                is_codec_settings_editable = bool(self.audio_codec_row.get_selected())
                self.channels_row.set_sensitive(is_codec_settings_editable)
                self.bitrate_setting_row.set_sensitive(is_codec_settings_editable)

                self._update_channels_row()
                self.update_subtitle()
                self.apply_settings_from_widgets()

    class FilterSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page
            self.is_widgets_setting_up = False

            self._setup_deinterlace_settings()

            filter_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            filter_settings_vertical_box.append(self.deinterlace_settings_group)
            filter_settings_vertical_box.set_margin_top(20)
            filter_settings_vertical_box.set_margin_bottom(20)
            filter_settings_vertical_box.set_margin_start(20)
            filter_settings_vertical_box.set_margin_end(20)

            self.set_child(filter_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_deinterlace_settings(self):
            self._setup_deinterlace_method_setting()

            self.deinterlace_enabled_switch = Gtk.Switch()
            self.deinterlace_enabled_switch.set_vexpand(False)
            self.deinterlace_enabled_switch.set_valign(Gtk.Align.CENTER)
            self.deinterlace_enabled_switch.connect('state-set', self.on_deinterlace_enabled_switch_state_set)

            self.deinterlace_settings_group = Adw.PreferencesGroup()
            self.deinterlace_settings_group.set_title('Deinterlace')
            self.deinterlace_settings_group.set_header_suffix(self.deinterlace_enabled_switch)
            self.deinterlace_settings_group.add(self.deinterlace_method_row)

        def _setup_deinterlace_method_setting(self):
            self._setup_deinterlace_method_string_list()

            self.deinterlace_method_row = Adw.ComboRow()
            self.deinterlace_method_row.set_title('Method')
            self.deinterlace_method_row.set_subtitle('Deinterlacing method')
            self.deinterlace_method_row.set_model(self.deinterlace_method_string_list)
            self.deinterlace_method_row.connect('notify::selected-item', self.on_widget_changed_clicked_set)
            self.deinterlace_method_row.set_sensitive(False)

        def _setup_deinterlace_method_string_list(self):
            self.deinterlace_method_string_list = Gtk.StringList.new(filter.Deinterlace.DEINT_FILTERS)

        def set_filters_available_state(self):
            self.deinterlace_settings_group.set_sensitive(True)

        def set_filters_not_available_state(self):
            self.deinterlace_method_row.set_selected(0)
            self.deinterlace_enabled_switch.set_active(False)
            self.deinterlace_settings_group.set_sensitive(False)

        def set_widgets_setting_up(self, is_widgets_setting_up: bool):
            self.is_widgets_setting_up = is_widgets_setting_up

        def apply_settings_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.set_widgets_setting_up, True)

            if self.is_encode_task_valid(encode_task):
                self.set_filters_available_state()
                self._apply_deinterlace_settings_to_widgets(encode_task)
            else:
                self.set_filters_not_available_state()

            GLib.idle_add(self.set_widgets_setting_up, False)

        @staticmethod
        def is_encode_task_valid(encode_task: task.Encode) -> bool:
            if video_codec.is_codec_copy(encode_task.get_video_codec()):
                return False

            if encode_task.output_file.extension in media_file.VIDEO_OUTPUT_EXTENSIONS:
                return True
            return False

        def _apply_deinterlace_settings_to_widgets(self, encode_task: task.Encode):
            is_deinterlace_settings_enabled = encode_task.filters.deinterlace is not None
            GLib.idle_add(self.deinterlace_enabled_switch.set_active, is_deinterlace_settings_enabled)

            if is_deinterlace_settings_enabled:
                GLib.idle_add(self.deinterlace_method_row.set_selected, encode_task.filters.deinterlace.method)
            else:
                GLib.idle_add(self.deinterlace_method_row.set_selected, 0)

        def apply_settings_from_widgets(self):
            self._apply_deinterlace_settings_from_widgets()

            self.inputs_page.update_preview_page_encode_task()

        def _apply_deinterlace_settings_from_widgets(self):
            if self.deinterlace_enabled_switch.get_active():
                deinterlace_settings = filter.Deinterlace()
                deinterlace_settings.method = self.deinterlace_method_row.get_selected()
            else:
                deinterlace_settings = None

            for input_row in self.inputs_page.get_selected_rows():
                encode_task = input_row.encode_task
                encode_task.filters.deinterlace = deinterlace_settings
                print(ffmpeg_helper.Args.get_args(encode_task, cli_args=True))

        def on_deinterlace_enabled_switch_state_set(self, switch, user_data):
            self.deinterlace_method_row.set_sensitive(switch.get_active())

            self.on_widget_changed_clicked_set()

        def on_widget_changed_clicked_set(self, *args, **kwargs):
            if self.is_widgets_setting_up:
                return

            threading.Thread(target=self.apply_settings_from_widgets, args=()).start()

    class SubtitleSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page
            self.is_widgets_setting_up = False

            self._setup_subtitle_settings()

            subtitle_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            subtitle_settings_vertical_box.append(self.subtitle_stream_settings_group)
            subtitle_settings_vertical_box.set_margin_top(20)
            subtitle_settings_vertical_box.set_margin_bottom(20)
            subtitle_settings_vertical_box.set_margin_start(20)
            subtitle_settings_vertical_box.set_margin_end(20)

            self.set_child(subtitle_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_subtitle_settings(self):
            add_subtitle_stream_button_child = Adw.ButtonContent.new()
            add_subtitle_stream_button_child.set_label('Add Stream')
            add_subtitle_stream_button_child.set_icon_name('list-add-symbolic')

            add_subtitle_stream_button = Gtk.Button()
            add_subtitle_stream_button.set_child(add_subtitle_stream_button_child)
            add_subtitle_stream_button.connect('clicked', self.on_add_subtitle_stream_button_clicked)

            self.subtitle_stream_settings_group = SettingsSidebarWidgets.SettingsGroup()
            self.subtitle_stream_settings_group.set_title('Subtitle Streams')
            self.subtitle_stream_settings_group.set_header_suffix(add_subtitle_stream_button)

        def update_subtitle_stream_rows(self):
            for subtitle_stream_row in self.subtitle_stream_settings_group.children:
                subtitle_stream_row.update_available_streams()
                subtitle_stream_row.update_method()

        def set_not_available_state(self):
            self.subtitle_stream_settings_group.remove_children()
            self.subtitle_stream_settings_group.set_sensitive(False)

        def set_available_state(self):
            self.subtitle_stream_settings_group.set_sensitive(True)

        def set_video_copy_state(self):
            for subtitle_stream_row in self.subtitle_stream_settings_group.children:
                if subtitle_stream_row.is_method_burn_in():
                    subtitle_stream_row.set_method_copy()

                    break

        def set_widgets_setting_up(self, is_widgets_setting_up: bool):
            self.is_widgets_setting_up = is_widgets_setting_up

        def apply_settings_to_widgets(self, encode_task: task.Encode):
            GLib.idle_add(self.set_widgets_setting_up, True)

            if encode_task.input_file.is_video and encode_task.input_file.subtitle_streams:
                GLib.idle_add(self.set_available_state)
                GLib.idle_add(self.subtitle_stream_settings_group.remove_children)
                self._apply_subtitle_streams_to_widgets(encode_task)
            else:
                GLib.idle_add(self.set_not_available_state)

            GLib.idle_add(self.set_widgets_setting_up, False)

        def _apply_subtitle_streams_to_widgets(self, encode_task: task.Encode):
            for subtitle_stream in encode_task.filters.subtitles.streams_in_use:
                GLib.idle_add(self._create_subtitle_stream_row_from_task, encode_task, subtitle_stream)

        def _create_subtitle_stream_row_from_task(self,
                                                  encode_task: task.Encode,
                                                  subtitle_stream: stream.SubtitleStream):
            subtitle_stream_row = self.SubtitleStreamRow(self,
                                                         encode_task,
                                                         subtitle_stream,
                                                         self.subtitle_stream_settings_group.number_of_children + 1)
            self.subtitle_stream_settings_group.add(subtitle_stream_row)

        def on_add_subtitle_stream_button_clicked(self, button):
            encode_task = self.inputs_page.inputs_list_box.get_selected_row().encode_task

            if encode_task.filters.subtitles.streams_available:
                subtitle_stream = encode_task.filters.subtitles.streams_available[0]
                encode_task.filters.subtitles.use_stream(subtitle_stream)

                subtitle_stream_row = self.SubtitleStreamRow(self,
                                                             encode_task,
                                                             subtitle_stream,
                                                             self.subtitle_stream_settings_group.number_of_children + 1)
                self.subtitle_stream_settings_group.add(subtitle_stream_row)
                self.update_subtitle_stream_rows()

        class SubtitleStreamRow(Adw.ExpanderRow):
            def __init__(self, subtitle_settings_page, encode_task: task.Encode, subtitle_stream, row_count: int):
                super().__init__()

                self.subtitle_settings_page = subtitle_settings_page
                self.encode_task = encode_task
                self.subtitle_stream = subtitle_stream
                self.row_count = row_count
                self.is_widgets_setting_up = False

                self._setup_subtitle_stream_row()

            def _setup_subtitle_stream_row(self):
                self._setup_stream_row()
                self._setup_method_row()
                self._setup_remove_button()

                self.set_title(''.join(['Subtitle Stream ', str(self.row_count)]))
                self.set_subtitle(self.subtitle_stream.get_info())
                self.add_row(self.stream_row)
                self.add_row(self.method_row)
                self.add_prefix(self.remove_button)

            def _setup_stream_row(self):
                self._setup_stream_string_list()

                self.stream_row = Adw.ComboRow()
                self.stream_row.set_title('Selected Stream')
                self.stream_row.set_model(self.streams_string_list)
                self.stream_row.connect('notify::selected-item', self.on_stream_combo_row_notify_selected_item)

            def _setup_stream_string_list(self):
                streams_list = [self.subtitle_stream.get_info()]
                for subtitle_stream in self.encode_task.filters.subtitles.streams_available:
                    streams_list.append(subtitle_stream.get_info())

                self.streams_string_list = Gtk.StringList.new(streams_list)

            def _setup_method_row(self):
                self.method_row = Adw.ComboRow()
                self.method_row.set_title('Method')
                self.method_row.set_subtitle('Method to apply to the subtitle stream')
                self._setup_method_combo_row()
                self.method_row.set_model('notify::selected-item', self.on_method_combo_row_notify_selected_item)

            def _setup_method_combo_row(self):
                method_string_list = Gtk.StringList.new(['Copy', 'Burn-In'])
                self.method_row.set_model(method_string_list)

                if self.encode_task.filters.subtitles.burn_in_stream_index == self.subtitle_stream.index:
                    self.method_row.set_selected(1)
                else:
                    self.method_row.set_selected(0)

            def _setup_remove_button(self):
                self.remove_button = Gtk.Button.new_from_icon_name('list-remove-symbolic')
                self.remove_button.set_vexpand(False)
                self.remove_button.set_valign(Gtk.Align.CENTER)
                self.remove_button.connect('clicked', self.on_remove_button_clicked)

            def update_title(self):
                self.set_title(''.join(['Subtitle Stream ', str(self.row_count)]))

            def update_available_streams(self):
                self.is_widgets_setting_up = True

                streams_list = [self.subtitle_stream.get_info()]
                for subtitle_stream in self.encode_task.filters.subtitles.streams_available:
                    streams_list.append(subtitle_stream.get_info())

                streams_string_list = Gtk.StringList.new(streams_list)
                self.stream_row.set_model(streams_string_list)

                self.is_widgets_setting_up = False

            def update_method(self):
                self.is_widgets_setting_up = True

                if self.encode_task.filters.subtitles.burn_in_stream_index == self.subtitle_stream.index:
                    self.set_method_burn_in()
                else:
                    self.set_method_copy()

                self.is_widgets_setting_up = False

            def is_method_burn_in(self):
                return self.method_row.get_selected() == 1

            def set_method_burn_in(self):
                self.method_row.set_selected(1)

            def set_method_copy(self):
                self.method_row.set_selected(0)

            def on_stream_combo_row_notify_selected_item(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                self.encode_task.filters.subtitles.remove_stream(self.subtitle_stream)

                new_subtitle_stream = self.stream_row.get_selected() - 1
                self.subtitle_stream = self.encode_task.filters.subtitles.streams_available[new_subtitle_stream]
                self.encode_task.filters.subtitles.use_stream(self.subtitle_stream)
                self.encode_task.filters.update_args()

                self.set_subtitle(self.subtitle_stream.get_info())
                self.subtitle_settings_page.update_subtitle_stream_rows()

            def on_method_combo_row_notify_selected_item(self, *args, **kwargs):
                if self.is_widgets_setting_up:
                    return

                if self.method_row.get_selected():
                    self.encode_task.filters.subtitles.set_stream_method_burn_in(self.subtitle_stream)
                else:
                    self.encode_task.filters.subtitles.burn_in_stream_index = None

                self.encode_task.filters.update_args()

                self.subtitle_settings_page.update_subtitle_stream_rows()

            def on_remove_button_clicked(self, button):
                self.encode_task.filters.subtitles.remove_stream(self.subtitle_stream)
                self.encode_task.filters.update_args()

                self.subtitle_settings_page.subtitle_stream_settings_group.remove(self)
                self.subtitle_settings_page.update_subtitle_stream_rows()
