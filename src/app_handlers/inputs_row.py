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
import os

from ffmpeg import general_settings
from encoding import preview
from encoding import encoder_helper
from app_formatting import format_converter
from app_handlers.active_row import ActiveRow
from app_handlers.chunk_row import ChunkRow
from startup import Gtk, GLib


class InputsRow(Gtk.ListBoxRow):
    def __init__(self, ffmpeg, inputs_page_handlers, active_page_handlers, main_window_handlers, encoder, preferences):
        Gtk.ListBoxRow.__init__(self)

        self.ffmpeg = ffmpeg
        self.preferences = preferences
        self.inputs_page_handlers = inputs_page_handlers
        self.active_page_handlers = active_page_handlers
        self.encoder = encoder
        self.main_window_handlers = main_window_handlers
        self.gtk_builder = Gtk.Builder()

        self.gtk_builder.add_from_file('../data/rows_ui.glade')

        self.__listbox_row_widget_container = self.gtk_builder.get_object('inputs_row_container')
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

        self.__setup_row_state()
        self.__setup_streams()
        self.setup_labels()
        self.add(self.__listbox_row_widget_container)
        self.remove_button.connect('clicked', self.on_remove_button_clicked)
        self.start_button.connect('clicked', self.on_start_button_clicked)
        self.video_stream_combobox.connect('changed', self.on_video_stream_combobox_changed)
        self.audio_stream_combobox.connect('changed', self.on_audio_stream_combobox_changed)
        self.inputs_folder_recursive_radiobutton.connect('toggled', self.on_inputs_folder_recursive_radiobutton_toggled)
        self.inputs_folder_watch_radiobutton.connect('toggled', self.on_inputs_folder_watch_radiobutton_toggled)

    def __setup_row_state(self):
        if not self.ffmpeg.folder_state:
            threading.Thread(target=self.setup_preview_thumbnail, args=()).start()
        else:
            self.__setup_folder_state()

    def __setup_folder_state(self):
        self.inputs_type_operations_stack.set_visible_child(self.inputs_folder_operations_buttonsbox)
        self.preview_thumbnail.set_from_icon_name('folder-symbolic', 96)

    def setup_preview_thumbnail(self):
        output_file = preview.get_crop_preview_file(self.ffmpeg, self.preferences, 96)

        GLib.idle_add(self.preview_thumbnail.set_from_file, output_file)

    def setup_labels(self):
        self.file_name_label.set_text(self.ffmpeg.filename)
        self.__setup_info_popover()
        self.__setup_inputs_row_info()

    def __setup_info_popover(self):
        self.__setup_info_popover_output_labels()
        self.__setup_info_popover_channels_label()
        self.__setup_info_popover_output_container_label()
        self.__setup_info_popover_frame_rate_label()
        self.__setup_info_popover_input_labels()
        self.__setup_info_popover_ffmpeg_params()

    def __setup_info_popover_output_labels(self):
        self.info_output_vcodec_label.set_text('Video Codec: ' + self.video_codec_label.get_text())
        self.info_output_acodec_label.set_text('Audio Codec: ' + self.audio_codec_label.get_text())
        self.info_output_resolution_label.set_text('Resolution: ' + self.resolution_label.get_text())
        self.info_output_duration_label.set_text('Duration: ' + self.duration_label.get_text())

    def __setup_info_popover_channels_label(self):
        if self.ffmpeg.audio_settings is not None:

            if self.ffmpeg.audio_settings.channels != 0:
                self.info_output_channels_label.set_text('Channels: ' + self.ffmpeg.audio_settings.channels_str)
            else:
                self.info_output_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)
        else:
            self.info_output_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)

    def __setup_info_popover_output_container_label(self):
        if self.ffmpeg.output_container is not None:
            self.info_output_container_label.set_text('Container: ' + self.ffmpeg.output_container)
        else:
            self.info_output_container_label.set_text('Container: ' + self.ffmpeg.input_container)

    def __setup_info_popover_frame_rate_label(self):
        if self.ffmpeg.general_settings.frame_rate is not None:
            frame_rate_index = self.ffmpeg.general_settings.frame_rate
            frame_rate_text = general_settings.GeneralSettings.frame_rate_ffmpeg_args_list[frame_rate_index]

            self.info_output_framerate_label.set_text('Frame Rate: ' + frame_rate_text)
        else:
            self.info_output_framerate_label.set_text('Frame Rate: ' + self.ffmpeg.framerate_origin)

    def __setup_info_popover_input_labels(self):
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
            self.info_input_vcodec_label.set_text('Video Codec: ' + self.ffmpeg.codec_video_origin)
            self.info_input_acodec_label.set_text('Audio Codec: ' + self.ffmpeg.codec_audio_origin)
            self.info_input_container_label.set_text('Container: ' + self.ffmpeg.input_container)
            self.info_input_framerate_label.set_text('Frame Rate: ' + str(self.ffmpeg.framerate_origin))
            self.info_input_channels_label.set_text('Channels: ' + self.ffmpeg.audio_channels_origin)
            self.info_input_filesize_label.set_text('File Size: ' + self.ffmpeg.file_size)
            self.info_input_duration_label.set_text('Duration: ' +
                                                    format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin))
            self.info_input_resolution_label.set_text('Resolution: ' + self.ffmpeg.resolution_origin)

    def __setup_info_popover_ffmpeg_params(self):
        args = self.ffmpeg.get_args(cmd_args_enabled=True)
        params = ''

        for index, arg in enumerate(args):
            params += arg

            if (index + 1) != len(args):
                params += ' '

        self.info_params_label.set_text(params)

    def __setup_inputs_row_info(self):
        self.__setup_inputs_row_video_codec_label()
        self.__setup_inputs_row_audio_codec_label()
        self.__setup_inputs_row_resolution_label()
        self.__setup_inputs_row_duration_label()
        self.__setup_info_popover()

    def __setup_inputs_row_video_codec_label(self):
        if self.ffmpeg.video_settings is not None:
            self.video_codec_label.set_text(self.ffmpeg.video_settings.codec_name)
        else:
            self.video_codec_label.set_text('copy')

    def __setup_inputs_row_audio_codec_label(self):
        if self.ffmpeg.audio_settings is not None:
            self.audio_codec_label.set_text(self.ffmpeg.audio_settings.codec_name)
        else:
            self.audio_codec_label.set_text('copy')

    def __setup_inputs_row_resolution_label(self):
        if self.ffmpeg.folder_state:
            self.resolution_label.set_text('N/A')
        else:

            if self.ffmpeg.picture_settings.scale is not None:
                scale_width, scale_height = self.ffmpeg.picture_settings.scale

                self.resolution_label.set_text(str(scale_width) + 'x' + str(scale_height))
            elif self.ffmpeg.picture_settings.crop is not None:
                width, height, *rest = self.ffmpeg.picture_settings.crop

                self.resolution_label.set_text(str(width) + 'x' + str(height))
            else:
                self.resolution_label.set_text(self.ffmpeg.resolution_origin)

    def __setup_inputs_row_duration_label(self):
        if self.ffmpeg.folder_state:
            self.duration_label.set_text('N/A')
        else:

            if self.ffmpeg.trim_settings is not None:
                timecode = format_converter.get_timecode_from_seconds(float(self.ffmpeg.trim_settings.trim_duration))

                self.duration_label.set_text(timecode)
            else:
                timecode = format_converter.get_timecode_from_seconds(self.ffmpeg.duration_origin)

                self.duration_label.set_text(timecode)

    def __setup_streams(self):
        if self.ffmpeg.folder_state:
            return

        self.__setup_video_stream_combobox()
        self.__setup_audio_stream_combobox()

    def __setup_video_stream_combobox(self):
        self.video_stream_combobox.remove_all()

        for index, items in enumerate(self.ffmpeg.input_file_info['video_streams'].items()):
            self.video_stream_combobox.append_text('[' + str(index) + ']' + items[1])
            self.video_stream_combobox.set_entry_text_column(0)
            self.video_stream_combobox.set_active(0)

            if index == 0:
                self.ffmpeg.video_stream_index = items[0]

    def __setup_audio_stream_combobox(self):
        self.audio_stream_combobox.remove_all()

        for index, items in enumerate(self.ffmpeg.input_file_info['audio_streams'].items()):
            self.audio_stream_combobox.append_text('[' + str(index) + ']' + items[1])
            self.audio_stream_combobox.set_entry_text_column(0)
            self.audio_stream_combobox.set_active(0)

            if index == 0:
                self.ffmpeg.audio_stream_index = items[0]

    def on_remove_button_clicked(self, remove_button):
        self.inputs_page_handlers.remove_inputs_page_listbox_row(self)

    def on_start_button_clicked(self, start_button):
        threading.Thread(target=self.__process_input_for_active_row, args=()).start()

    def __process_input_for_active_row(self):
        self.__fix_same_name_occurrences()
        GLib.idle_add(self.__create_and_add_active_listbox_row)

    def __fix_same_name_occurrences(self):
        file_name = self.ffmpeg.filename
        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container
        counter = 0

        while True:
            if self.ffmpeg.input_file == output_file_path:
                output_file_path = self.__fix_output_file_path_from_same_input_file_path(file_name, counter)
            elif not self.preferences.overwrite_outputs and os.path.exists(output_file_path):
                output_file_path = self.__fix_output_file_path_from_file_already_exists(file_name, counter)
            else:
                output_file_path_found = False

                for active_listbox_row in self.active_page_handlers.get_active_page_listbox_rows():
                    row_file_name = active_listbox_row.ffmpeg.filename
                    row_output_directory = active_listbox_row.ffmpeg.output_directory
                    row_output_container = active_listbox_row.ffmpeg.output_container
                    row_output_file_path = row_output_directory + row_file_name + row_output_container

                    if output_file_path == row_output_file_path:
                        self.ffmpeg.filename = file_name + '_' + str(counter)
                        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename \
                                           + self.ffmpeg.output_container
                        output_file_path_found = True

                if not output_file_path_found:
                    break

            counter += 1

    def __fix_output_file_path_from_same_input_file_path(self, file_name, counter):
        self.ffmpeg.filename = file_name + '_' + str(counter)
        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

        return output_file_path

    def __fix_output_file_path_from_file_already_exists(self, file_name, counter):
        self.ffmpeg.filename = file_name + '_' + str(counter)
        output_file_path = self.ffmpeg.output_directory + self.ffmpeg.filename + self.ffmpeg.output_container

        return output_file_path

    def __create_and_add_active_listbox_row(self):
        input_information_popover = self.input_information_button.get_popover()
        preview_thumbnail_file_path = self.preview_thumbnail.get_property('file')
        active_page_listbox_row = ActiveRow(self.ffmpeg, input_information_popover, self.gtk_builder,
                                            preview_thumbnail_file_path, self.active_page_handlers.active_page_listbox,
                                            self.preferences)

        self.active_page_handlers.add_active_page_listbox_row(active_page_listbox_row)
        self.inputs_page_handlers.remove_inputs_page_listbox_row(self)
        threading.Thread(target=self.__add_active_row_to_encoder, args=(active_page_listbox_row,)).start()

    def __add_active_row_to_encoder(self, active_page_listbox_row):
        if self.main_window_handlers.is_chunk_processing_selected() and not self.ffmpeg.folder_state:
            self.__add_active_row_chunks_to_encoder(active_page_listbox_row)
        else:
            self.encoder.add_active_listbox_row(active_page_listbox_row)

    def __add_active_row_chunks_to_encoder(self, active_page_listbox_row):
        chunks = encoder_helper.get_chunks(self.ffmpeg, self.preferences)

        if chunks is None:
            self.encoder.add_active_listbox_row(active_page_listbox_row)
        else:
            for index, ffmpeg in enumerate(chunks):
                chunk_row = ChunkRow(ffmpeg, (index + 1), active_page_listbox_row)

                if (index + 1) == len(chunks):
                    GLib.idle_add(active_page_listbox_row.add_audio_chunk_row, chunk_row)
                else:
                    GLib.idle_add(active_page_listbox_row.add_chunk_row, chunk_row)

                self.encoder.add_active_listbox_row(chunk_row)

    def on_video_stream_combobox_changed(self, video_stream_combobox):
        combobox_index = video_stream_combobox.get_active()
        video_streams = list(self.ffmpeg.input_file_info['video_streams'].items())
        video_stream_index = (video_streams[combobox_index])[0]

        self.ffmpeg.video_stream_index = video_stream_index
        self.setup_labels()

    def on_audio_stream_combobox_changed(self, audio_stream_combobox):
        combobox_index = audio_stream_combobox.get_active()
        audio_streams = list(self.ffmpeg.input_file_info['audio_streams'].items())
        audio_stream_index = (audio_streams[combobox_index])[0]

        self.ffmpeg.audio_stream_index = audio_stream_index
        self.setup_labels()

    def on_inputs_folder_recursive_radiobutton_toggled(self, folder_recursive_radiobutton):
        self.ffmpeg.recursive_folder = folder_recursive_radiobutton.get_active()

    def on_inputs_folder_watch_radiobutton_toggled(self, folder_watch_radiobutton):
        self.ffmpeg.watch_folder = folder_watch_radiobutton.get_active()
