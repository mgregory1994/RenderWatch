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
from render_watch.signals.inputs_row.folder_recursive_signal import FolderRecursiveSignal
from render_watch.signals.inputs_row.folder_watch_signal import FolderWatchSignal
from render_watch.signals.inputs_row.remove_signal import RemoveSignal
from render_watch.signals.inputs_row.start_signal import StartSignal
from render_watch.signals.inputs_row.video_stream_signal import VideoStreamSignal
from render_watch.startup import Gtk, GLib


class InputsRow(Gtk.ListBoxRow):
    """Handles all functionality for each Gtk.ListboxRow inputs row on the inputs page."""

    def __init__(self,
                 ffmpeg,
                 inputs_page_handlers,
                 active_page_handlers,
                 main_window_handlers,
                 encoder_queue,
                 preferences):
        Gtk.ListBoxRow.__init__(self)
        self.ffmpeg = ffmpeg
        self.preferences = preferences
        self.inputs_page_handlers = inputs_page_handlers
        self.active_page_handlers = active_page_handlers
        self.encoder_queue = encoder_queue
        self.main_window_handlers = main_window_handlers
        self.audio_stream_signal = AudioStreamSignal(self)
        self.folder_recursive_signal = FolderRecursiveSignal(self)
        self.folder_watch_signal = FolderWatchSignal(self)
        self.remove_signal = RemoveSignal(self, inputs_page_handlers)
        self.start_signal = StartSignal(self)
        self.video_stream_signal = VideoStreamSignal(self)
        self.signals_list = (
            self.audio_stream_signal, self.folder_recursive_signal, self.folder_watch_signal,
            self.remove_signal, self.start_signal, self.video_stream_signal
        )

        self.gtk_builder = Gtk.Builder()
        this_file_directory_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_file_directory_file_path, '../render_watch_data/rows_ui.glade')
        self.gtk_builder.add_from_file(rows_ui_file_path)
        self.listbox_row_widget_container = self.gtk_builder.get_object('inputs_row_container')
        self.preview_thumbnail = self.gtk_builder.get_object('input_thumbnail')
        self.start_button = self.gtk_builder.get_object('inputs_row_start_button')
        self.trim_button = self.gtk_builder.get_object('inputs_row_trim_button')
        self.crop_button = self.gtk_builder.get_object('inputs_row_crop_button')
        self.preview_button = self.gtk_builder.get_object('inputs_row_preview_button')
        self.benchmark_button = self.gtk_builder.get_object('inputs_row_benchmark_button')
        self.input_information_button = self.gtk_builder.get_object('inputs_row_info_button')
        self.file_name_label = self.gtk_builder.get_object('inputs_row_filename_label')
        self.remove_button = self.gtk_builder.get_object('inputs_row_remove_button')
        self.video_codec_label = self.gtk_builder.get_object('inputs_row_vcodec_label')
        self.audio_codec_label = self.gtk_builder.get_object('inputs_row_acodec_label')
        self.resolution_label = self.gtk_builder.get_object('inputs_row_resolution_label')
        self.duration_label = self.gtk_builder.get_object('inputs_row_duration_label')
        self.inputs_type_operations_stack = self.gtk_builder.get_object('inputs_type_operations_stack')
        self.inputs_folder_operations_buttonsbox = self.gtk_builder.get_object('inputs_folder_operations_buttonsbox')
        self.inputs_folder_standard_radiobutton = self.gtk_builder.get_object('inputs_folder_standard_radiobutton')
        self.inputs_folder_recursive_radiobutton = self.gtk_builder.get_object('inputs_folder_recursive_radiobutton')
        self.inputs_folder_watch_radiobutton = self.gtk_builder.get_object('inputs_folder_watch_radiobutton')
        self.video_stream_combobox = self.gtk_builder.get_object('video_stream_combobox')
        self.audio_stream_combobox = self.gtk_builder.get_object('audio_stream_combobox')
        self.info_params_label = self.gtk_builder.get_object('info_params_label')
        self.info_input_vcodec_label = self.gtk_builder.get_object('info_input_vcodec_label')
        self.info_input_acodec_label = self.gtk_builder.get_object('info_input_acodec_label')
        self.info_input_container_label = self.gtk_builder.get_object('info_input_container_label')
        self.info_input_resolution_label = self.gtk_builder.get_object('info_input_resolution_label')
        self.info_input_duration_label = self.gtk_builder.get_object('info_input_duration_label')
        self.info_input_framerate_label = self.gtk_builder.get_object('info_input_framerate_label')
        self.info_input_channels_label = self.gtk_builder.get_object('info_input_channels_label')
        self.info_input_filesize_label = self.gtk_builder.get_object('info_input_filesize_label')
        self.info_output_vcodec_label = self.gtk_builder.get_object('info_output_vcodec_label')
        self.info_output_acodec_label = self.gtk_builder.get_object('info_output_acodec_label')
        self.info_output_container_label = self.gtk_builder.get_object('info_output_container_label')
        self.info_output_resolution_label = self.gtk_builder.get_object('info_output_resolution_label')
        self.info_output_duration_label = self.gtk_builder.get_object('info_output_duration_label')
        self.info_output_framerate_label = self.gtk_builder.get_object('info_output_framerate_label')
        self.info_output_channels_label = self.gtk_builder.get_object('info_output_channels_label')
        self._setup_row_state()
        self._setup_streams()
        self.setup_labels()
        self.add(self.listbox_row_widget_container)
        self.remove_button.connect('clicked', self.on_remove_button_clicked)
        self.start_button.connect('clicked', self.on_start_button_clicked)
        self.video_stream_combobox.connect('changed', self.on_video_stream_combobox_changed)
        self.audio_stream_combobox.connect('changed', self.on_audio_stream_combobox_changed)
        self.inputs_folder_recursive_radiobutton.connect('toggled', self.on_inputs_folder_recursive_radiobutton_toggled)
        self.inputs_folder_watch_radiobutton.connect('toggled', self.on_inputs_folder_watch_radiobutton_toggled)

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def _setup_row_state(self):
        # Sets up the inputs row widgets to show the type of imported input.
        if not self.ffmpeg.folder_state:
            threading.Thread(target=self.setup_preview_thumbnail, args=()).start()
        else:
            self._setup_folder_state()

    def _setup_folder_state(self):
        # Sets the input row widgets to show a folder input.
        self.inputs_type_operations_stack.set_visible_child(self.inputs_folder_operations_buttonsbox)
        self.preview_thumbnail.set_from_icon_name('folder-symbolic', 96)

    def setup_preview_thumbnail(self):
        """Generates and applies a preview thumbnail."""
        output_file = preview.generate_crop_preview_file(self.ffmpeg, self.preferences, 96)
        GLib.idle_add(self.preview_thumbnail.set_from_file, output_file)

    def _setup_streams(self):
        # Populates the video and audio stream combobox widgets.
        if self.ffmpeg.folder_state:
            return
        self._setup_video_stream_combobox()
        self._setup_audio_stream_combobox()

    def _setup_video_stream_combobox(self):
        # Populates the video stream combobox widget.
        self.video_stream_combobox.remove_all()

        for index, items in enumerate(self.ffmpeg.input_file_info['video_streams'].items()):
            self.video_stream_combobox.append_text('[' + str(index) + ']' + items[1]['info'])
        self.video_stream_combobox.set_entry_text_column(0)
        self.video_stream_combobox.set_active(0)
        self.signal_video_stream_combobox()

    def _setup_audio_stream_combobox(self):
        # Populates the audio stream combobox widget.
        self.audio_stream_combobox.remove_all()

        for index, items in enumerate(self.ffmpeg.input_file_info['audio_streams'].items()):
            self.audio_stream_combobox.append_text('[' + str(index) + ']' + items[1]['info'])
        self.audio_stream_combobox.set_entry_text_column(0)
        self.audio_stream_combobox.set_active(0)
        self.signal_audio_stream_combobox()

    def setup_labels(self):
        """Sets up labels for inputs row title, input info., and popover labels."""
        self.file_name_label.set_text(self.ffmpeg.filename)
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
        self.info_output_vcodec_label.set_text('Video Codec: ' + self.video_codec_label.get_text())
        self.info_output_acodec_label.set_text('Audio Codec: ' + self.audio_codec_label.get_text())
        self.info_output_resolution_label.set_text('Resolution: ' + self.resolution_label.get_text())
        self.info_output_duration_label.set_text('Duration: ' + self.duration_label.get_text())

    def _setup_info_popover_channels_label(self):
        if self.ffmpeg.audio_settings is not None:
            if self.ffmpeg.audio_settings.channels != 0:
                self.info_output_channels_label.set_text('Channels: ' + self.ffmpeg.audio_settings.channels_str)
        else:
            self.info_output_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)

    def _setup_info_popover_output_container_label(self):
        if self.ffmpeg.output_container:
            self.info_output_container_label.set_text('Container: ' + self.ffmpeg.output_container)
        else:
            self.info_output_container_label.set_text('Container: ' + self.ffmpeg.input_container)

    def _setup_info_popover_frame_rate_label(self):
        if self.ffmpeg.general_settings.frame_rate:
            frame_rate_index = self.ffmpeg.general_settings.frame_rate
            frame_rate_text = general_settings.GeneralSettings.FRAME_RATE_ARGS_LIST[frame_rate_index]
            self.info_output_framerate_label.set_text('Frame Rate: ' + frame_rate_text)
        else:
            self.info_output_framerate_label.set_text('Frame Rate: ' + self.ffmpeg.framerate_origin)

    def _setup_info_popover_input_labels(self):
        if self.ffmpeg.folder_state:
            self.info_input_vcodec_label.set_text('Video Codec: N/A')
            self.info_input_acodec_label.set_text('Audio Codec: N/A')
            self.info_input_container_label.set_text('Container: N/A')
            self.info_input_framerate_label.set_text('Frame Rate: N/A')
            self.info_input_channels_label.set_text('Channels: N/A')
            self.info_input_filesize_label.set_text('File Size: N/A')
            self.info_input_duration_label.set_text('Duration: N/A')
            self.info_input_resolution_label.set_text('Resolution: N/A')
        else:
            duration_timecode = format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin)
            self.info_input_vcodec_label.set_text('Video Codec: ' + self.ffmpeg.codec_video_origin)
            self.info_input_acodec_label.set_text('Audio Codec: ' + self.ffmpeg.codec_audio_origin)
            self.info_input_container_label.set_text('Container: ' + self.ffmpeg.input_container)
            self.info_input_framerate_label.set_text('Frame Rate: ' + str(self.ffmpeg.framerate_origin))
            self.info_input_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)
            self.info_input_filesize_label.set_text('File Size: ' + self.ffmpeg.file_size)
            self.info_input_duration_label.set_text('Duration: ' + duration_timecode)
            self.info_input_resolution_label.set_text('Resolution: ' + self.ffmpeg.resolution_origin)

    def _setup_info_popover_ffmpeg_params(self):
        # Generates terminal arguments that can run ffmpeg with the currently applied settings.
        args = self.ffmpeg.get_args(cmd_args_enabled=True)
        params = ''
        for index, arg in enumerate(args):
            params += arg
            if (index + 1) != len(args):
                params += ' '
        self.info_params_label.set_text(params)

    def _setup_inputs_row_info(self):
        # Sets up imported input info. for inputs row.
        self._setup_inputs_row_video_codec_label()
        self._setup_inputs_row_audio_codec_label()
        self._setup_inputs_row_resolution_label()
        self._setup_inputs_row_duration_label()
        self._setup_info_popover()

    def _setup_inputs_row_video_codec_label(self):
        if self.ffmpeg.video_settings:
            self.video_codec_label.set_text(self.ffmpeg.video_settings.codec_name)
        else:
            self.video_codec_label.set_text('copy')

    def _setup_inputs_row_audio_codec_label(self):
        if self.ffmpeg.audio_settings:
            self.audio_codec_label.set_text(self.ffmpeg.audio_settings.codec_name)
        else:
            self.audio_codec_label.set_text('copy')

    def _setup_inputs_row_resolution_label(self):
        if self.ffmpeg.folder_state:
            self.resolution_label.set_text('N/A')
        else:
            if self.ffmpeg.picture_settings.scale:
                scale_width, scale_height = self.ffmpeg.picture_settings.scale
                self.resolution_label.set_text(str(scale_width) + 'x' + str(scale_height))
            elif self.ffmpeg.picture_settings.crop:
                width, height, *rest = self.ffmpeg.picture_settings.crop
                self.resolution_label.set_text(str(width) + 'x' + str(height))
            else:
                self.resolution_label.set_text(self.ffmpeg.resolution_origin)

    def _setup_inputs_row_duration_label(self):
        if self.ffmpeg.folder_state:
            self.duration_label.set_text('N/A')
        else:
            if self.ffmpeg.trim_settings:
                timecode = format_converter.get_timecode_from_seconds(float(self.ffmpeg.trim_settings.trim_duration))
                self.duration_label.set_text(timecode)
            else:
                timecode = format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin)
                self.duration_label.set_text(timecode)

    def process_row_input(self):
        """Sends inputs row to the active page for encoding."""
        self._fix_same_name_occurrences()
        GLib.idle_add(self._create_and_add_active_listbox_row)

    def _fix_same_name_occurrences(self):
        # Fixes output and input being the same file, or overwriting an existing output file.
        file_name = self.ffmpeg.filename
        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container
        counter = 0
        while True:
            if self.ffmpeg.input_file == output_file_path:
                output_file_path = self._fix_same_output_and_input_file_paths(file_name, counter)
            elif not self.preferences.overwrite_outputs and os.path.exists(output_file_path):
                output_file_path = self._fix_output_file_already_exists(file_name, counter)
            else:
                output_file_path_found = False
                for active_listbox_row in self.active_page_handlers.get_rows():
                    row_file_name = active_listbox_row.ffmpeg.filename
                    row_output_directory = active_listbox_row.ffmpeg.output_directory
                    row_output_container = active_listbox_row.ffmpeg.output_container
                    row_output_file_path = row_output_directory + row_file_name + row_output_container
                    if output_file_path == row_output_file_path:
                        self.ffmpeg.filename = file_name + '_' + str(counter)
                        output_file_path = self.ffmpeg.output_directory \
                                           + self.ffmpeg.filename \
                                           + self.ffmpeg.output_container
                        output_file_path_found = True
                if not output_file_path_found:
                    break

            counter += 1

    def _fix_same_output_and_input_file_paths(self, file_name, counter):
        # Fixes matching input and output files for the ffmpeg settings object.
        self.ffmpeg.filename = file_name + '_' + str(counter)
        return self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

    def _fix_output_file_already_exists(self, file_name, counter):
        # Fixes output file already existing for the ffmpeg settings object.
        self.ffmpeg.filename = file_name + '_' + str(counter)
        return self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

    def _create_and_add_active_listbox_row(self):
        # Creates a Gtk.ListboxRow active row from this inputs row.
        input_information_popover = self.input_information_button.get_popover()
        preview_thumbnail_file_path = self.preview_thumbnail.get_property('file')
        active_page_listbox_row = ActiveRow(self.ffmpeg,
                                            input_information_popover,
                                            self.gtk_builder,
                                            preview_thumbnail_file_path,
                                            self.active_page_handlers,
                                            self.preferences)
        self.active_page_handlers.add_row(active_page_listbox_row)
        self.inputs_page_handlers.remove_row(self)
        threading.Thread(target=self._add_active_row_to_encoder, args=(active_page_listbox_row,)).start()

    def _add_active_row_to_encoder(self, active_page_listbox_row):
        # Uses active row to send ffmpeg settings object to the encoder queue.
        if self.main_window_handlers.is_chunk_processing_selected() and not self.ffmpeg.folder_state:
            self._add_active_row_chunks_to_encoder(active_page_listbox_row)
        else:
            self.encoder_queue.add_active_row(active_page_listbox_row)

    def _add_active_row_chunks_to_encoder(self, active_page_listbox_row):
        # Chunks active row's ffmpeg settings object and sends those chunks to the encoder queue.
        chunks = encoder_helper.get_chunks(self.ffmpeg, self.preferences)
        if chunks is None:
            self.encoder_queue.add_active_row(active_page_listbox_row)
        else:
            for index, ffmpeg in enumerate(chunks):
                chunk_row = ChunkRow(ffmpeg, (index + 1), active_page_listbox_row)
                if (index + 1) == len(chunks):
                    GLib.idle_add(active_page_listbox_row.add_audio_chunk_row, chunk_row)
                else:
                    GLib.idle_add(active_page_listbox_row.add_chunk_row, chunk_row)
                self.encoder_queue.add_active_row(chunk_row)

    def signal_start_button(self):
        self.start_signal.on_start_button_clicked(self.start_button)

    def signal_video_stream_combobox(self):
        self.video_stream_signal.on_video_stream_combobox_changed(self.video_stream_combobox)

    def signal_audio_stream_combobox(self):
        self.audio_stream_signal.on_audio_stream_combobox_changed(self.audio_stream_combobox)
