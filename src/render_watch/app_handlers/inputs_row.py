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
import os

from render_watch.ffmpeg import general_settings
from render_watch.encoding import preview
from render_watch.helpers import encoder_helper
from render_watch.app_formatting import format_converter
from render_watch.app_handlers.active_row import ActiveRow
from render_watch.app_handlers.chunk_row import ChunkRow
from render_watch.signals.inputs_row.audio_stream_signal import AudioStreamSignal
from render_watch.signals.inputs_row.recursive_folder_task_signal import RecursiveFolderTaskSignal
from render_watch.signals.inputs_row.watch_folder_task_signal import WatchFolderTaskSignal
from render_watch.signals.inputs_row.remove_task_signal import RemoveTaskSignal
from render_watch.signals.inputs_row.start_signal import StartSignal
from render_watch.signals.inputs_row.video_stream_signal import VideoStreamSignal
from render_watch.startup import Gtk, GLib


class InputsRow(Gtk.ListBoxRow):
    """
    Handles the functionality for an individual input task on the inputs page.
    """

    def __init__(self,
                 ffmpeg,
                 inputs_page_handlers,
                 active_page_handlers,
                 main_window_handlers,
                 encoder_queue,
                 application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self.ffmpeg = ffmpeg
        self.application_preferences = application_preferences
        self.inputs_page_handlers = inputs_page_handlers
        self.active_page_handlers = active_page_handlers
        self.encoder_queue = encoder_queue
        self.main_window_handlers = main_window_handlers

        self._setup_signals(inputs_page_handlers)
        self._setup_widgets()

    def _setup_signals(self, inputs_page_handlers):
        self.audio_stream_signal = AudioStreamSignal(self)
        self.recursive_folder_task_signal = RecursiveFolderTaskSignal(self)
        self.watch_folder_task_signal = WatchFolderTaskSignal(self)
        self.remove_task_signal = RemoveTaskSignal(self, inputs_page_handlers)
        self.start_signal = StartSignal(self)
        self.video_stream_signal = VideoStreamSignal(self)

    def _setup_widgets(self):
        this_modules_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_modules_file_path, '../render_watch_data/rows_ui.glade')

        self.gtk_builder = Gtk.Builder()
        self.gtk_builder.add_from_file(rows_ui_file_path)

        self.inputs_listbox_row_box = self.gtk_builder.get_object('inputs_listbox_row_box')
        self.inputs_listbox_row_preview_icon = self.gtk_builder.get_object('inputs_listbox_row_preview_icon')
        self.inputs_listbox_row_start_button = self.gtk_builder.get_object('inputs_listbox_row_start_button')
        self.inputs_listbox_row_task_info_button = self.gtk_builder.get_object('inputs_listbox_row_task_info_button')
        self.inputs_listbox_row_file_name_label = self.gtk_builder.get_object('inputs_listbox_row_file_name_label')
        self.inputs_listbox_row_remove_button = self.gtk_builder.get_object('inputs_listbox_row_remove_button')
        self.inputs_listbox_row_video_codec_value_label = self.gtk_builder.get_object('inputs_listbox_row_video_codec_value_label')
        self.inputs_listbox_row_audio_codec_value_label = self.gtk_builder.get_object('inputs_listbox_row_audio_codec_value_label')
        self.inputs_listbox_row_resolution_value_label = self.gtk_builder.get_object('inputs_listbox_row_resolution_value_label')
        self.inputs_listbox_row_duration_value_label = self.gtk_builder.get_object('inputs_listbox_row_duration_value_label')
        self.streams_stack = self.gtk_builder.get_object('streams_stack')
        self.folder_type_buttonbox = self.gtk_builder.get_object('folder_type_buttonbox')
        self.standard_folder_task_radiobutton = self.gtk_builder.get_object('standard_folder_task_radiobutton')
        self.recursive_folder_task_radiobutton = self.gtk_builder.get_object('recursive_folder_task_radiobutton')
        self.watch_folder_task_radiobutton = self.gtk_builder.get_object('watch_folder_task_radiobutton')
        self.video_stream_combobox = self.gtk_builder.get_object('video_stream_combobox')
        self.audio_stream_combobox = self.gtk_builder.get_object('audio_stream_combobox')
        self.ffmpeg_parameters_value_label = self.gtk_builder.get_object('ffmpeg_parameters_value_label')
        self.input_info_video_codec_label = self.gtk_builder.get_object('input_info_video_codec_label')
        self.input_info_audio_codec_label = self.gtk_builder.get_object('input_info_audio_codec_label')
        self.input_info_container_label = self.gtk_builder.get_object('input_info_container_label')
        self.input_info_resolution_label = self.gtk_builder.get_object('input_info_resolution_label')
        self.input_info_duration_label = self.gtk_builder.get_object('input_info_duration_label')
        self.input_info_frame_rate_label = self.gtk_builder.get_object('input_info_frame_rate_label')
        self.input_info_channels_label = self.gtk_builder.get_object('input_info_channels_label')
        self.input_info_file_size_label = self.gtk_builder.get_object('input_info_file_size_label')
        self.output_info_video_codec_label = self.gtk_builder.get_object('output_info_video_codec_label')
        self.output_info_audio_codec_label = self.gtk_builder.get_object('output_info_audio_codec_label')
        self.output_info_container_label = self.gtk_builder.get_object('output_info_container_label')
        self.output_info_resolution_label = self.gtk_builder.get_object('output_info_resolution_label')
        self.output_info_duration_label = self.gtk_builder.get_object('output_info_duration_label')
        self.output_info_frame_rate_label = self.gtk_builder.get_object('output_info_frame_rate_label')
        self.output_info_channels_label = self.gtk_builder.get_object('output_info_channels_label')

        self._setup_row_state()
        self._setup_streams()
        self.setup_labels()
        self.add(self.inputs_listbox_row_box)

        self.inputs_listbox_row_remove_button.connect('clicked',
                                                      self.remove_task_signal.on_remove_input_task_button_clicked)
        self.inputs_listbox_row_start_button.connect('clicked', self.start_signal.on_start_button_clicked)
        self.video_stream_combobox.connect('changed', self.video_stream_signal.on_video_stream_combobox_changed)
        self.audio_stream_combobox.connect('changed', self.audio_stream_signal.on_audio_stream_combobox_changed)
        self.recursive_folder_task_radiobutton.connect('toggled',
                                                       self.recursive_folder_task_signal.on_recursive_folder_task_radiobutton_toggled)
        self.watch_folder_task_radiobutton.connect('toggled',
                                                   self.watch_folder_task_signal.on_watch_folder_task_radiobutton_toggled)

    def _setup_row_state(self):
        if self.ffmpeg.folder_state:
            self._setup_folder_state()
        else:
            threading.Thread(target=self.setup_preview_thumbnail, args=()).start()

    def _setup_folder_state(self):
        self.streams_stack.set_visible_child(self.folder_type_buttonbox)
        self.inputs_listbox_row_preview_icon.set_from_icon_name('folder-symbolic', 96)

    def setup_preview_thumbnail(self):
        """
        Generates and applies a preview thumbnail.
        """
        output_file = preview.generate_crop_preview_file(self.ffmpeg, self.application_preferences, 96)
        GLib.idle_add(self.inputs_listbox_row_preview_icon.set_from_file, output_file)

    def _setup_streams(self):
        if self.ffmpeg.folder_state:
            return

        self._setup_video_stream_combobox()
        self._setup_audio_stream_combobox()

    def _setup_video_stream_combobox(self):
        self.video_stream_combobox.remove_all()

        for index, items in enumerate(self.ffmpeg.input_file_info['video_streams'].items()):
            self.video_stream_combobox.append_text('[' + str(index) + ']' + items[1]['info'])

        self.video_stream_combobox.set_entry_text_column(0)
        self.video_stream_combobox.set_active(0)
        self.signal_video_stream_combobox()

    def _setup_audio_stream_combobox(self):
        self.audio_stream_combobox.remove_all()

        if not self.ffmpeg.input_file_info['audio_streams']:
            self.audio_stream_combobox.set_sensitive(False)
            return

        for index, items in enumerate(self.ffmpeg.input_file_info['audio_streams'].items()):
            self.audio_stream_combobox.append_text('[' + str(index) + ']' + items[1]['info'])

        self.audio_stream_combobox.set_entry_text_column(0)
        self.audio_stream_combobox.set_active(0)
        self.signal_audio_stream_combobox()

    def setup_labels(self):
        """
        Sets up labels for task's title, input info., and info. popover labels.
        """
        self.inputs_listbox_row_file_name_label.set_text(self.ffmpeg.filename)
        self._setup_info_popover()
        self._setup_inputs_row_info()

    def _setup_info_popover(self):
        self._setup_info_popover_output_labels()
        self._setup_info_popover_channels_label()
        self._setup_info_popover_output_container_label()
        self._setup_info_popover_frame_rate_label()
        self._setup_info_popover_input_labels()
        self._setup_info_popover_ffmpeg_params()

    def _setup_info_popover_output_labels(self):
        self.output_info_video_codec_label.set_text('Video Codec: '
                                                    + self.inputs_listbox_row_video_codec_value_label.get_text())
        self.output_info_audio_codec_label.set_text('Audio Codec: '
                                                    + self.inputs_listbox_row_audio_codec_value_label.get_text())
        self.output_info_resolution_label.set_text('Resolution: '
                                                   + self.inputs_listbox_row_resolution_value_label.get_text())
        self.output_info_duration_label.set_text('Duration: '
                                                 + self.inputs_listbox_row_duration_value_label.get_text())

    def _setup_info_popover_channels_label(self):
        if self.ffmpeg.audio_settings:
            if self.ffmpeg.audio_settings.channels != 0:
                self.output_info_channels_label.set_text('Channels: ' + self.ffmpeg.audio_settings.channels_str)
        else:
            self.output_info_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)

    def _setup_info_popover_output_container_label(self):
        if self.ffmpeg.output_container:
            self.output_info_container_label.set_text('Container: ' + self.ffmpeg.output_container)
        else:
            self.output_info_container_label.set_text('Container: ' + self.ffmpeg.input_container)

    def _setup_info_popover_frame_rate_label(self):
        if self.ffmpeg.general_settings.frame_rate:
            frame_rate_index = self.ffmpeg.general_settings.frame_rate
            frame_rate_text = general_settings.GeneralSettings.FRAME_RATE_ARGS_LIST[frame_rate_index]

            self.output_info_frame_rate_label.set_text('Frame Rate: ' + frame_rate_text)
        else:
            self.output_info_frame_rate_label.set_text('Frame Rate: ' + self.ffmpeg.framerate_origin)

    def _setup_info_popover_input_labels(self):
        if self.ffmpeg.folder_state:
            self._setup_info_popover_folder_state()
        else:
            self._setup_info_popover_file_state()

    def _setup_info_popover_folder_state(self):
        self.input_info_video_codec_label.set_text('Video Codec: N/A')
        self.input_info_audio_codec_label.set_text('Audio Codec: N/A')
        self.input_info_container_label.set_text('Container: N/A')
        self.input_info_frame_rate_label.set_text('Frame Rate: N/A')
        self.input_info_channels_label.set_text('Channels: N/A')
        self.input_info_file_size_label.set_text('File Size: N/A')
        self.input_info_duration_label.set_text('Duration: N/A')
        self.input_info_resolution_label.set_text('Resolution: N/A')

    def _setup_info_popover_file_state(self):
        duration_timecode = format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin)
        self.input_info_video_codec_label.set_text('Video Codec: ' + self.ffmpeg.codec_video_origin)
        self.input_info_audio_codec_label.set_text('Audio Codec: ' + self.ffmpeg.codec_audio_origin)
        self.input_info_container_label.set_text('Container: ' + self.ffmpeg.input_container)
        self.input_info_frame_rate_label.set_text('Frame Rate: ' + str(self.ffmpeg.framerate_origin))
        self.input_info_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)
        self.input_info_file_size_label.set_text('File Size: ' + self.ffmpeg.file_size)
        self.input_info_duration_label.set_text('Duration: ' + duration_timecode)
        self.input_info_resolution_label.set_text('Resolution: ' + self.ffmpeg.resolution_origin)

    def _setup_info_popover_ffmpeg_params(self):
        args = self.ffmpeg.get_args(cmd_args_enabled=True)
        params = ''

        for index, arg in enumerate(args):
            params += arg

            if (index + 1) != len(args):
                params += ' '

        self.ffmpeg_parameters_value_label.set_text(params)

    def _setup_inputs_row_info(self):
        self._setup_inputs_row_video_codec_label()
        self._setup_inputs_row_audio_codec_label()
        self._setup_inputs_row_resolution_label()
        self._setup_inputs_row_duration_label()
        self._setup_info_popover()

    def _setup_inputs_row_video_codec_label(self):
        if self.ffmpeg.video_settings:
            self.inputs_listbox_row_video_codec_value_label.set_text(self.ffmpeg.video_settings.codec_name)
        else:
            self.inputs_listbox_row_video_codec_value_label.set_text('copy')

    def _setup_inputs_row_audio_codec_label(self):
        if self.ffmpeg.audio_settings:
            self.inputs_listbox_row_audio_codec_value_label.set_text(self.ffmpeg.audio_settings.codec_name)
        else:
            self.inputs_listbox_row_audio_codec_value_label.set_text('copy')

    def _setup_inputs_row_resolution_label(self):
        if self.ffmpeg.folder_state:
            self.inputs_listbox_row_resolution_value_label.set_text('N/A')
        else:
            if self.ffmpeg.picture_settings.scale:
                scale_width, scale_height = self.ffmpeg.picture_settings.scale
                self.inputs_listbox_row_resolution_value_label.set_text(str(scale_width) + 'x' + str(scale_height))
            elif self.ffmpeg.picture_settings.crop:
                width, height, *rest = self.ffmpeg.picture_settings.crop
                self.inputs_listbox_row_resolution_value_label.set_text(str(width) + 'x' + str(height))
            else:
                self.inputs_listbox_row_resolution_value_label.set_text(self.ffmpeg.resolution_origin)

    def _setup_inputs_row_duration_label(self):
        if self.ffmpeg.folder_state:
            self.inputs_listbox_row_duration_value_label.set_text('N/A')
        else:
            if self.ffmpeg.trim_settings:
                timecode = format_converter.get_timecode_from_seconds(float(self.ffmpeg.trim_settings.trim_duration))
                self.inputs_listbox_row_duration_value_label.set_text(timecode)
            else:
                timecode = format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin)
                self.inputs_listbox_row_duration_value_label.set_text(timecode)

    def process_row_input(self):
        """
        Sends task to the active page for encoding.
        """
        self._fix_same_name_occurrences()
        GLib.idle_add(self._add_task_to_active_page)

    def _fix_same_name_occurrences(self):
        file_name = self.ffmpeg.filename
        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container
        counter = 0

        while True:
            if self.ffmpeg.input_file == output_file_path:
                output_file_path = self._fix_same_output_and_input_file_paths(file_name, counter)
            elif not self.application_preferences.is_overwrite_outputs_enabled and os.path.exists(output_file_path):
                output_file_path = self._fix_output_file_already_exists(file_name, counter)
            else:
                output_file_path_found = False

                for active_task in self.active_page_handlers.get_rows():
                    task_file_name = active_task.ffmpeg.filename
                    task_output_directory = active_task.ffmpeg.output_directory
                    task_output_container = active_task.ffmpeg.output_container
                    task_output_file_path = task_output_directory + task_file_name + task_output_container

                    if output_file_path == task_output_file_path:
                        self.ffmpeg.filename = file_name + '_' + str(counter)
                        output_file_path = self.ffmpeg.output_directory \
                                           + self.ffmpeg.filename \
                                           + self.ffmpeg.output_container
                        output_file_path_found = True
                if not output_file_path_found:
                    break

            counter += 1

    def _fix_same_output_and_input_file_paths(self, file_name, counter):
        self.ffmpeg.filename = file_name + '_' + str(counter)
        return self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

    def _fix_output_file_already_exists(self, file_name, counter):
        self.ffmpeg.filename = file_name + '_' + str(counter)
        return self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

    def _add_task_to_active_page(self):
        input_information_popover = self.inputs_listbox_row_task_info_button.get_popover()
        preview_thumbnail_file_path = self.inputs_listbox_row_preview_icon.get_property('file')
        active_page_task = ActiveRow(self.ffmpeg,
                                     input_information_popover,
                                     self.gtk_builder,
                                     preview_thumbnail_file_path,
                                     self.active_page_handlers,
                                     self.application_preferences)

        self.active_page_handlers.add_row(active_page_task)
        self.inputs_page_handlers.remove_row(self)
        threading.Thread(target=self._add_active_page_task_to_encoder, args=(active_page_task,)).start()

    def _add_active_page_task_to_encoder(self, active_page_task):
        if self.main_window_handlers.is_chunk_processing_selected() and not self.ffmpeg.folder_state:
            self._add_active_page_task_chunks_to_encoder(active_page_task)
        else:
            self.encoder_queue.add_active_row(active_page_task)

    def _add_active_page_task_chunks_to_encoder(self, active_page_task):
        chunks = encoder_helper.get_chunks(self.ffmpeg, self.application_preferences)

        if chunks:
            for index, ffmpeg in enumerate(chunks):
                chunk_row = ChunkRow(ffmpeg, (index + 1), active_page_task)

                if (index + 1) == len(chunks):
                    GLib.idle_add(active_page_task.add_audio_chunk_row, chunk_row)
                else:
                    GLib.idle_add(active_page_task.add_chunk_row, chunk_row)

                self.encoder_queue.add_active_row(chunk_row)
        else:
            self.encoder_queue.add_active_row(active_page_task)

    def signal_start_button(self):
        self.start_signal.on_start_button_clicked(self.inputs_listbox_row_start_button)

    def signal_video_stream_combobox(self):
        self.video_stream_signal.on_video_stream_combobox_changed(self.video_stream_combobox)

    def signal_audio_stream_combobox(self):
        self.audio_stream_signal.on_audio_stream_combobox_changed(self.audio_stream_combobox)
