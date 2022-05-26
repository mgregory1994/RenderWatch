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


import os
import threading
import time

from pathlib import Path

from render_watch.ui import Gtk, Gio, Gdk, GLib, Adw, GdkPixbuf, Pango
from render_watch.ui import settings_sidebar
from render_watch.encode import preview
from render_watch.ffmpeg import encoding, input
from render_watch import app_preferences


class InputActionRow(Adw.ActionRow):
    def __init__(self,
                 inputs_page_widgets,
                 encoding_task: encoding.Task,
                 preview_generator: preview.PreviewGenerator,
                 app_settings: app_preferences.Settings):
        super().__init__()

        self.inputs_page_widgets = inputs_page_widgets
        self.encoding_task = encoding_task
        self.preview_generator = preview_generator
        self.app_settings = app_settings

        self._setup_action_row()

    def _setup_action_row(self):
        self.set_title(self.encoding_task.input_file.name)
        self.set_title_lines(3)

        self._setup_subtitle()
        self._setup_contents()
        self._setup_remove_button()

    def _setup_subtitle(self):
        if self.encoding_task.input_file.is_folder:
            self.set_subtitle('Folder')
        elif self.encoding_task.input_file.is_video:
            self.set_subtitle('Video')
        else:
            self.set_subtitle('Audio')

        self.set_subtitle_lines(1)

    def _setup_contents(self):
        self._setup_controls()
        self._setup_output_path_link_button()

        if self.encoding_task.input_file.is_folder:
            pass  # Setup Folder Contents
        elif self.encoding_task.input_file.is_video:
            self._setup_video_contents()
        else:
            pass  # Setup audio contents

    def _setup_video_contents(self):
        self._setup_preview()

        self.video_contents_centered_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.video_contents_centered_box.append(self.controls_horizontal_box)
        self.video_contents_centered_box.append(self.output_path_link_button)
        self.video_contents_centered_box.append(self.preview_horizontal_box)
        self.video_contents_centered_box.set_hexpand(True)
        self.video_contents_centered_box.set_vexpand(True)

        self.add_suffix(self.video_contents_centered_box)

    def _setup_controls(self):
        self.task_info_button = Gtk.MenuButton()
        self.task_info_button.set_icon_name('view-more-symbolic')
        self._setup_task_info_popover()
        self.task_info_button.set_popover(self.task_info_popover)

        start_task_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        start_task_button.set_size_request(50, -1)

        self.controls_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.controls_horizontal_box.append(self.task_info_button)
        self.controls_horizontal_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.controls_horizontal_box.append(start_task_button)
        self.controls_horizontal_box.set_vexpand(False)
        self.controls_horizontal_box.set_valign(Gtk.Align.CENTER)
        self.controls_horizontal_box.set_hexpand(False)
        self.controls_horizontal_box.set_halign(Gtk.Align.START)

    def _setup_task_info_popover(self):
        self._setup_task_info_popover_contents()

        self.task_info_popover = Gtk.Popover()
        self.task_info_popover.set_child(self.task_info_popover_scrolled_window)
        self.task_info_popover.set_size_request(400, 300)

    def _setup_task_info_popover_contents(self):
        self._setup_task_info_popover_input_contents()
        self._setup_task_info_popover_output_contents()

        task_info_contents_separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)

        task_info_popover_contents_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        task_info_popover_contents_horizontal_box.append(self.input_contents_vertical_box)
        task_info_popover_contents_horizontal_box.append(task_info_contents_separator)
        task_info_popover_contents_horizontal_box.append(self.output_contents_vertical_box)
        task_info_popover_contents_horizontal_box.set_margin_start(10)
        task_info_popover_contents_horizontal_box.set_margin_end(10)

        self.task_info_popover_scrolled_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                                                    vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self.task_info_popover_scrolled_window.set_child(task_info_popover_contents_horizontal_box)
        self.task_info_popover_scrolled_window.set_margin_top(10)
        self.task_info_popover_scrolled_window.set_margin_bottom(10)

    def _setup_task_info_popover_input_contents(self):
        input_label = Gtk.Label(label='Input')
        input_label.set_hexpand(True)
        input_label.set_halign(Gtk.Align.CENTER)

        if self.encoding_task.input_file.is_folder:
            input_type_label = Gtk.Label(label='Type: Folder')
        elif self.encoding_task.input_file.is_video:
            input_type_label = Gtk.Label(label='Type: Video')
        else:
            input_type_label = Gtk.Label(label='Type: Audio')

        input_type_label.set_hexpand(True)
        input_type_label.set_halign(Gtk.Align.START)

        input_file_label = Gtk.Label(label=''.join(['File: ',
                                                    self.encoding_task.input_file.name,
                                                    self.encoding_task.input_file.extension]))
        input_file_label.set_hexpand(True)
        input_file_label.set_halign(Gtk.Align.START)

        self.input_contents_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.input_contents_vertical_box.append(input_label)
        self.input_contents_vertical_box.append(input_type_label)
        self.input_contents_vertical_box.append(input_file_label)

        self._setup_task_info_popover_input_video_streams()
        self._setup_task_info_popover_input_audio_streams()

    def _setup_task_info_popover_input_video_streams(self):
        for video_stream in self.encoding_task.input_file.video_streams:
            video_stream_label = Gtk.Label(label=''.join(['Video Stream[', str(video_stream.index), ']']))
            video_stream_label.set_hexpand(True)
            video_stream_label.set_halign(Gtk.Align.START)
            video_stream_language_label = Gtk.Label(label=''.join(['Language: ', video_stream.language]))
            video_stream_language_label.set_hexpand(True)
            video_stream_language_label.set_halign(Gtk.Align.START)
            video_stream_language_label.set_margin_start(20)
            video_stream_codec_label = Gtk.Label(label=''.join(['Codec: ', video_stream.codec_name]))
            video_stream_codec_label.set_hexpand(True)
            video_stream_codec_label.set_halign(Gtk.Align.START)
            video_stream_codec_label.set_margin_start(20)
            video_stream_dimensions_label = Gtk.Label(label=''.join(['Dimensions: ',
                                                                     str(video_stream.width),
                                                                     'x',
                                                                     str(video_stream.height)]))
            video_stream_dimensions_label.set_hexpand(True)
            video_stream_dimensions_label.set_halign(Gtk.Align.START)
            video_stream_dimensions_label.set_margin_start(20)
            video_stream_bitrate_label = Gtk.Label(label=''.join(['Bitrate: ', str(video_stream.bitrate)]))
            video_stream_bitrate_label.set_hexpand(True)
            video_stream_bitrate_label.set_halign(Gtk.Align.START)
            video_stream_bitrate_label.set_margin_start(20)
            video_stream_frame_rate_label = Gtk.Label(label=''.join(['Frame Rate: ', str(video_stream.frame_rate)]))
            video_stream_frame_rate_label.set_hexpand(True)
            video_stream_frame_rate_label.set_halign(Gtk.Align.START)
            video_stream_frame_rate_label.set_margin_start(20)

            self.input_contents_vertical_box.append(video_stream_label)
            self.input_contents_vertical_box.append(video_stream_language_label)
            self.input_contents_vertical_box.append(video_stream_codec_label)
            self.input_contents_vertical_box.append(video_stream_dimensions_label)
            self.input_contents_vertical_box.append(video_stream_bitrate_label)
            self.input_contents_vertical_box.append(video_stream_frame_rate_label)

    def _setup_task_info_popover_input_audio_streams(self):
        for audio_stream in self.encoding_task.input_file.audio_streams:
            audio_stream_label = Gtk.Label(label=''.join(['Audio Stream[', str(audio_stream.index), ']']))
            audio_stream_label.set_hexpand(True)
            audio_stream_label.set_halign(Gtk.Align.START)
            audio_stream_language_label = Gtk.Label(label=''.join(['Language: ', audio_stream.language]))
            audio_stream_language_label.set_hexpand(True)
            audio_stream_language_label.set_halign(Gtk.Align.START)
            audio_stream_language_label.set_margin_start(20)
            audio_stream_codec_label = Gtk.Label(label=''.join(['Codec: ', audio_stream.codec_name]))
            audio_stream_codec_label.set_hexpand(True)
            audio_stream_codec_label.set_halign(Gtk.Align.START)
            audio_stream_codec_label.set_margin_start(20)
            audio_stream_dimensions_label = Gtk.Label(label=''.join(['Channels: ', str(audio_stream.channels)]))
            audio_stream_dimensions_label.set_hexpand(True)
            audio_stream_dimensions_label.set_halign(Gtk.Align.START)
            audio_stream_dimensions_label.set_margin_start(20)
            audio_stream_bitrate_label = Gtk.Label(label=''.join(['Bitrate: ', str(audio_stream.bitrate)]))
            audio_stream_bitrate_label.set_hexpand(True)
            audio_stream_bitrate_label.set_halign(Gtk.Align.START)
            audio_stream_bitrate_label.set_margin_start(20)
            audio_stream_frame_rate_label = Gtk.Label(label=''.join(['Sample Rate: ', str(audio_stream.sample_rate)]))
            audio_stream_frame_rate_label.set_hexpand(True)
            audio_stream_frame_rate_label.set_halign(Gtk.Align.START)
            audio_stream_frame_rate_label.set_margin_start(20)

            self.input_contents_vertical_box.append(audio_stream_label)
            self.input_contents_vertical_box.append(audio_stream_language_label)
            self.input_contents_vertical_box.append(audio_stream_codec_label)
            self.input_contents_vertical_box.append(audio_stream_dimensions_label)
            self.input_contents_vertical_box.append(audio_stream_bitrate_label)
            self.input_contents_vertical_box.append(audio_stream_frame_rate_label)

    def _setup_task_info_popover_output_contents(self):
        output_label = Gtk.Label(label='Output')
        output_label.set_hexpand(True)
        output_label.set_halign(Gtk.Align.CENTER)

        self.output_contents_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.output_contents_vertical_box.append(output_label)

        if self.encoding_task.input_file.is_video or self.encoding_task.input_file.is_folder:
            video_codec_label = Gtk.Label(label=''.join(['Video Codec: ', self.encoding_task.video_codec.codec_name]))
            video_codec_label.set_hexpand(True)
            video_codec_label.set_halign(Gtk.Align.START)

            self.output_contents_vertical_box.append(video_codec_label)

        if self.encoding_task.input_file.is_audio or self.encoding_task.input_file.is_folder:
            for audio_stream in self.encoding_task.audio_streams:
                audio_stream_index = self.encoding_task.get_audio_stream_index(audio_stream)
                audio_stream_codec = self.encoding_task.get_audio_stream_codec(audio_stream)
                audio_stream_label = Gtk.Label(label=''.join(['Audio Stream [', str(audio_stream_index), ']']))
                audio_stream_label.set_hexpand(True)
                audio_stream_label.set_halign(Gtk.Align.START)
                audio_stream_language_label = Gtk.Label(label=''.join(['Language: ', audio_stream.language]))
                audio_stream_language_label.set_hexpand(True)
                audio_stream_language_label.set_halign(Gtk.Align.START)
                audio_stream_language_label.set_margin_start(20)
                audio_stream_codec_label = Gtk.Label(label=''.join(['Codec: ', audio_stream_codec.codec_name]))
                audio_stream_codec_label.set_hexpand(True)
                audio_stream_codec_label.set_halign(Gtk.Align.START)
                audio_stream_codec_label.set_margin_start(20)

                self.output_contents_vertical_box.append(audio_stream_label)
                self.output_contents_vertical_box.append(audio_stream_language_label)
                self.output_contents_vertical_box.append(audio_stream_codec_label)

    def _setup_output_path_link_button(self):
        output_path_uri = ''.join(['file:/', self.encoding_task.output_file.file_path])
        self.output_path_link_button = Gtk.LinkButton.new_with_label(output_path_uri,
                                                                     self.encoding_task.output_file.file_path)
        self.output_path_link_button.set_hexpand(False)
        self.output_path_link_button.set_halign(Gtk.Align.START)

    def _setup_preview(self):
        preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            self.encoding_task.temp_output_file.crop_preview_file_path,
            width=-1,
            height=72,
            preserve_aspect_ratio=True
        )
        self.preview_image = Gtk.Picture.new_for_pixbuf(preview_pixbuf)
        self.preview_image.set_can_shrink(False)
        self.preview_image.set_hexpand(True)
        self.preview_image.set_halign(Gtk.Align.CENTER)
        self.preview_image.set_margin_top(5)
        self.preview_image.set_margin_bottom(5)
        self.preview_image.set_margin_start(5)
        self.preview_image.set_margin_end(5)

        self.preview_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.preview_horizontal_box.append(self.preview_image)
        self.preview_horizontal_box.set_hexpand(True)

    def _setup_remove_button(self):
        remove_button = Gtk.Button.new_from_icon_name('list-remove-symbolic')
        remove_button.set_vexpand(False)
        remove_button.set_valign(Gtk.Align.CENTER)
        remove_button.connect('clicked', self.remove_from_inputs)
        remove_button.set_margin_end(5)

        self.add_suffix(remove_button)

    def set_output_file_path_link(self, output_dir, output_file_name):
        self.encoding_task.output_file.dir = output_dir
        self.encoding_task.output_file.name = Path(output_file_name).resolve().stem

        output_file_path = os.path.join(output_dir, output_file_name)
        output_path_uri = ''.join(['file:/', output_file_path])
        self.output_path_link_button.set_uri(output_path_uri)
        self.output_path_link_button.set_label(output_file_path)

    def remove_from_inputs(self, remove_button):
        self.inputs_page_widgets.remove_input_row(self)


class InputsPageWidgets:
    def __init__(self, application, preview_generator: preview.PreviewGenerator, app_settings: app_preferences.Settings):
        self.application = application
        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self.main_widget = Gtk.Stack()

        self._setup_inputs_widgets()

    def _setup_inputs_widgets(self):
        self._setup_inputs_list()
        self._setup_adding_inputs_widgets()
        self._setup_settings_sidebar_widgets()
        self._setup_flap()
        self._setup_options_popover_widgets()

        self.main_widget.add_named(self.inputs_page_flap, 'edit_inputs')
        self.main_widget.add_named(self.adding_inputs_vertical_box, 'adding_inputs')
        self.main_widget.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_inputs_list(self):
        self._setup_inputs_list_placeholder_widget()

        self.inputs_list_box = Gtk.ListBox()
        self.inputs_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.inputs_list_box.set_show_separators(True)
        self.inputs_list_box.set_placeholder(self.placeholder_vertical_box)
        self.inputs_list_box.set_vexpand(True)
        self.inputs_list_box.set_hexpand(True)

        inputs_list_drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        inputs_list_drop_target.connect('drop', self.import_inputs_list_drop)
        inputs_list_drop_target.connect('accept', self.accept_inputs_list_drop)
        self.inputs_list_box.add_controller(inputs_list_drop_target)

        self.inputs_scrolled_window = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER,
                                                         vscrollbar_policy=Gtk.PolicyType.AUTOMATIC)
        self.inputs_scrolled_window.set_child(self.inputs_list_box)

    def _setup_inputs_list_placeholder_widget(self):
        placeholder_add_file_icon = Gtk.Image.new_from_icon_name('document-new-symbolic')
        placeholder_add_file_icon.set_pixel_size(128)
        placeholder_add_file_icon.set_vexpand(True)
        placeholder_add_file_icon.set_valign(Gtk.Align.END)
        placeholder_add_file_icon.set_hexpand(True)
        placeholder_add_file_icon.set_halign(Gtk.Align.CENTER)
        placeholder_add_file_icon.set_opacity(0.5)
        placeholder_add_folder_icon = Gtk.Image.new_from_icon_name('folder-new-symbolic')
        placeholder_add_folder_icon.set_pixel_size(128)
        placeholder_add_folder_icon.set_vexpand(True)
        placeholder_add_folder_icon.set_valign(Gtk.Align.END)
        placeholder_add_folder_icon.set_hexpand(True)
        placeholder_add_folder_icon.set_halign(Gtk.Align.CENTER)
        placeholder_add_folder_icon.set_opacity(0.5)
        self.placeholder_icon_stack = Gtk.Stack()
        self.placeholder_icon_stack.add_named(placeholder_add_file_icon, 'files')
        self.placeholder_icon_stack.add_named(placeholder_add_folder_icon, 'folders')
        self.placeholder_icon_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        placeholder_label = Gtk.Label(label='Add or Drop a New Input')
        placeholder_label.set_vexpand(True)
        placeholder_label.set_valign(Gtk.Align.START)
        placeholder_label.set_sensitive(False)

        self.placeholder_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
        self.placeholder_vertical_box.append(self.placeholder_icon_stack)
        self.placeholder_vertical_box.append(placeholder_label)

    def _setup_adding_inputs_widgets(self):
        adding_inputs_label = Gtk.Label(label='Adding Inputs...')
        adding_inputs_label.set_vexpand(True)
        adding_inputs_label.set_valign(Gtk.Align.END)
        attr_size = Pango.AttrSize.new(32 * Pango.SCALE)
        attr_list = Pango.AttrList.new()
        attr_list.insert(attr_size)
        adding_inputs_label.set_attributes(attr_list)
        self.adding_inputs_current_file_path = Gtk.Label()
        self.adding_inputs_progress_bar = Gtk.ProgressBar()
        self.adding_inputs_progress_bar.set_vexpand(True)
        self.adding_inputs_progress_bar.set_margin_top(20)
        self.adding_inputs_progress_bar.set_margin_start(80)
        self.adding_inputs_progress_bar.set_margin_end(80)

        self.adding_inputs_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.adding_inputs_vertical_box.append(adding_inputs_label)
        self.adding_inputs_vertical_box.append(self.adding_inputs_current_file_path)
        self.adding_inputs_vertical_box.append(self.adding_inputs_progress_bar)

    def _setup_settings_sidebar_widgets(self):
        self.settings_sidebar_widgets = settings_sidebar.SettingsSidebarWidgets(self.app_settings)

    def _setup_flap(self):
        self.inputs_page_flap = Adw.Flap()
        self.inputs_page_flap.set_content(self.inputs_scrolled_window)
        self.inputs_page_flap.set_flap(self.settings_sidebar_widgets.main_widget)
        self.inputs_page_flap.set_separator(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.inputs_page_flap.set_flap_position(Gtk.PackType.END)
        self.inputs_page_flap.set_reveal_flap(False)
        self.inputs_page_flap.set_locked(True)
        self.inputs_page_flap.get_flap().add_css_class('background')

    def _setup_options_popover_widgets(self):
        self._setup_input_options_widgets()
        self._setup_encoder_options_widgets()

        self.start_all_button = Gtk.Button(label='Start All')
        self.remove_all_button = Gtk.Button(label='Remove All')
        self.remove_all_button.add_css_class('destructive-action')

        self.popover_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.popover_options_vertical_box.append(self.start_all_button)
        self.popover_options_vertical_box.append(self.remove_all_button)
        self.popover_options_vertical_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.popover_options_vertical_box.append(self.input_options_vertical_box)
        self.popover_options_vertical_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.popover_options_vertical_box.append(self.encoder_options_vertical_box)

    def _setup_input_options_widgets(self):
        auto_crop_tasks_label = Gtk.Label(label='Auto-Crop New Tasks:')
        auto_crop_tasks_label.set_halign(Gtk.Align.START)
        self.auto_crop_tasks_switch = Gtk.Switch()
        self.auto_crop_tasks_switch.set_hexpand(True)
        self.auto_crop_tasks_switch.set_halign(Gtk.Align.END)
        self.auto_crop_tasks_switch.set_active(self.app_settings.is_auto_cropping_inputs)
        auto_crop_tasks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        auto_crop_tasks_horizontal_box.append(auto_crop_tasks_label)
        auto_crop_tasks_horizontal_box.append(self.auto_crop_tasks_switch)

        apply_settings_to_all_tasks_label = Gtk.Label(label='Apply Settings To All Tasks:')
        apply_settings_to_all_tasks_label.set_halign(Gtk.Align.START)
        self.apply_settings_to_all_tasks_switch = Gtk.Switch()
        self.apply_settings_to_all_tasks_switch.set_hexpand(True)
        self.apply_settings_to_all_tasks_switch.set_halign(Gtk.Align.END)
        apply_settings_to_all_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        apply_settings_to_all_horizontal_box.append(apply_settings_to_all_tasks_label)
        apply_settings_to_all_horizontal_box.append(self.apply_settings_to_all_tasks_switch)

        self.input_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.input_options_vertical_box.append(auto_crop_tasks_horizontal_box)
        self.input_options_vertical_box.append(apply_settings_to_all_horizontal_box)

    def _setup_encoder_options_widgets(self):
        self.standard_tasks_check_button = Gtk.CheckButton(label='Standard Tasks')
        self.standard_tasks_check_button.set_active(True)
        self.parallel_tasks_check_button = Gtk.CheckButton(label='Parallel Tasks')
        self.parallel_tasks_check_button.set_group(self.standard_tasks_check_button)
        self.parallel_tasks_check_button.set_active(self.app_settings.is_encoding_parallel_tasks)
        self.parallel_tasks_check_button.connect('toggled', self._save_encoder_type_setting)
        encoder_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        encoder_type_horizontal_box.append(self.standard_tasks_check_button)
        encoder_type_horizontal_box.append(self.parallel_tasks_check_button)

        task_chunks_label = Gtk.Label(label='Task Chunks:')
        task_chunks_label.set_halign(Gtk.Align.START)
        task_chunks_label.set_hexpand(True)
        task_chunks_label.set_margin_start(40)
        self.task_chunks_switch = Gtk.Switch()
        self.task_chunks_switch.set_halign(Gtk.Align.END)
        self.task_chunks_switch.set_active(self.app_settings.is_encoding_parallel_method_chunking)
        self.task_chunks_switch.connect('state-set', self._save_encoder_chunking_setting)
        self.task_chunks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.task_chunks_horizontal_box.append(task_chunks_label)
        self.task_chunks_horizontal_box.append(self.task_chunks_switch)

        self.encoder_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.encoder_options_vertical_box.append(encoder_type_horizontal_box)
        self.encoder_options_vertical_box.append(self.task_chunks_horizontal_box)

    def import_inputs_list_drop(self, drop_target, files_list, x_pos, y_pos):
        threading.Thread(target=self._add_drop_inputs, args=(files_list.get_files(),)).start()

    def _add_drop_inputs(self, input_files: list):
        acceptable_files = filter(lambda file: Path(file.get_path()).resolve().suffix.lower() in input.VALID_EXTENSIONS,
                                  input_files)
        self.add_inputs(list(acceptable_files))

    def accept_inputs_list_drop(self, drop, user_data):  # Unused parameters needed for drop accept function.
        return True

    def add_inputs(self, input_files: list):
        GLib.idle_add(self.main_widget.set_visible_child_name, 'adding_inputs')

        for index, file in enumerate(input_files):
            GLib.idle_add(self.adding_inputs_current_file_path.set_label, file.get_path())
            self._set_adding_inputs_progress(index, len(input_files))
            encoding_task = self._create_encoding_task(file)

            if encoding_task:
                GLib.idle_add(self._create_input_row, encoding_task)

        GLib.idle_add(self.main_widget.set_visible_child_name, 'edit_inputs')

    def _create_encoding_task(self, input_file: Gio.File):
        import traceback
        try:
            encoding_task = encoding.Task(input_file.get_path(), self.app_settings)

            if encoding_task.input_file.is_video:
                encoding_task.filter.crop = encoding.filters.Crop(encoding_task, self.app_settings)
                self.preview_generator.generate_previews(encoding_task)

                while not self._are_task_previews_generated(encoding_task):
                    time.sleep(0.5)
        except:
            traceback.print_exc()
            return None
        else:
            return encoding_task

    @staticmethod
    def _are_task_previews_generated(encoding_task):
        if encoding_task.temp_output_file.crop_preview_file_path is None:
            return False

        if encoding_task.temp_output_file.trim_preview_file_path is None:
            return False

        if encoding_task.temp_output_file.settings_preview_file_path is None:
            return False
        return True

    def _create_input_row(self, encoding_task: encoding.Task):
        input_row = InputActionRow(self, encoding_task, self.preview_generator, self.app_settings)
        input_row.output_path_link_button.connect('activate-link', self.application.show_output_file_chooser, input_row)
        GLib.idle_add(self.inputs_list_box.append, input_row)

    def _set_adding_inputs_progress(self, index: int, list_length: int):
        progress_fraction = round(float(index + 1) / float(list_length), 3)

        GLib.idle_add(self.adding_inputs_progress_bar.set_fraction, progress_fraction)

    def remove_input_row(self, input_row: Adw.ActionRow):
        self.inputs_list_box.remove(input_row)

    def set_input_type_state(self, is_file_state_enabled=False):
        if is_file_state_enabled:
            self.placeholder_icon_stack.set_visible_child_name('files')
        else:
            self.placeholder_icon_stack.set_visible_child_name('folders')

    def set_parallel_encoder_option_state(self, is_state_enabled: bool):
        self.task_chunks_horizontal_box.set_sensitive(is_state_enabled)

    def toggle_settings_sidebar(self, toggle_settings_sidebar_button):
        self.inputs_page_flap.set_reveal_flap(not self.inputs_page_flap.get_reveal_flap())

    def _save_auto_crop_setting(self, switch, user_data):
        self.app_settings.is_auto_cropping_inputs = self.auto_crop_tasks_switch.get_active()

    def _save_encoder_type_setting(self, checkbutton):
        self.set_parallel_encoder_option_state(checkbutton.get_active())
        self.app_settings.is_encoding_parallel_tasks = checkbutton.get_active()

        if not checkbutton.get_active():
            self.task_chunks_switch.set_active(False)

    def _save_encoder_chunking_setting(self, switch, user_data):
        self.app_settings.is_encoding_parallel_method_chunking = switch.get_active()
