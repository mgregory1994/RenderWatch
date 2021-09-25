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
import copy
import os

from render_watch.ffmpeg.settings import Settings
from render_watch.encoding import preview
from render_watch.helpers import encoder_helper
from render_watch.app_formatting.alias import AliasGenerator
from render_watch.app_handlers.inputs_row import InputsRow
from render_watch.startup import Gtk, GLib


class AddInputSignal:
    """Handles the signal emitted when an input is selected and added."""

    def __init__(self,
                 main_window_handlers,
                 inputs_page_handlers,
                 active_page_handlers,
                 settings_sidebar_handlers,
                 encoder_queue,
                 preferences):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.active_page_handlers = active_page_handlers
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.encoder_queue = encoder_queue
        self.preferences = preferences

    def on_add_button_clicked(self, add_button, inputs=None):  # Unused parameters needed for this signal
        """Adds files or folders from a file chooser dialog. Then filter and process those inputs.

        :param add_button:
            Button that emitted the signal.
        :param inputs:
            (Default=None) Pass in a list of inputs instead of using the file chooser.
        """
        file_inputs_enabled = self.main_window_handlers.is_file_inputs_enabled()
        if inputs is None:
            if file_inputs_enabled:
                file_chooser_response, inputs = self._create_and_show_file_chooser()
            else:
                file_chooser_response, inputs = self._create_and_show_folder_chooser()
        else:
            file_chooser_response = Gtk.ResponseType.OK

        threading.Thread(target=self._filter_inputs,
                         args=(inputs, file_chooser_response, file_inputs_enabled),
                         daemon=True).start()

    def _create_and_show_file_chooser(self):
        # Shows a file chooser for selecting files.
        file_chooser = Gtk.FileChooserDialog('Choose a file',
                                             self.main_window_handlers.main_window,
                                             Gtk.FileChooserAction.OPEN,
                                             (Gtk.STOCK_CANCEL,
                                              Gtk.ResponseType.CANCEL,
                                              Gtk.STOCK_OPEN,
                                              Gtk.ResponseType.OK))
        file_chooser.set_select_multiple(True)
        response = file_chooser.run()
        files = file_chooser.get_filenames()
        file_chooser.destroy()
        return response, files

    def _create_and_show_folder_chooser(self):
        # Shows a file chooser for selecting folders.
        file_chooser = Gtk.FileChooserDialog('Choose a folder',
                                             self.main_window_handlers.main_window,
                                             Gtk.FileChooserAction.SELECT_FOLDER,
                                             (Gtk.STOCK_CANCEL,
                                              Gtk.ResponseType.CANCEL,
                                              Gtk.STOCK_OPEN,
                                              Gtk.ResponseType.OK))
        file_chooser.set_select_multiple(True)
        response = file_chooser.run()
        folders = file_chooser.get_filenames()
        file_chooser.destroy()
        return response, folders

    def _filter_inputs(self, inputs, file_chooser_response, file_inputs_enabled):
        # Chooses valid inputs based on file extensions or if the inputs are folders.
        if file_inputs_enabled:
            inputs = [value for value in inputs if encoder_helper.is_extension_valid(value)]
        else:
            inputs = [value for value in inputs if os.path.isdir(value)]

        output_dir = self.main_window_handlers.get_output_chooser_dir()

        if file_chooser_response == Gtk.ResponseType.OK and inputs:
            GLib.idle_add(self.main_window_handlers.set_processing_inputs_state, True, inputs[0])
            threading.Thread(target=self._process_inputs,
                             args=(inputs, output_dir, file_inputs_enabled),
                             daemon=True).start()

    def _process_inputs(self, inputs, output_dir, file_inputs_enabled):
        # Setup an ffmpeg settings object for each input and add them to the inputs page.
        self._setup_settings_sidebar_ffmpeg_template()

        length_of_input_files = len(inputs)
        for index, file_path in enumerate(inputs):
            self._setup_importing_files_widgets(file_path, index, length_of_input_files)

            ffmpeg = Settings()
            self._setup_input_file_paths(ffmpeg, file_path, output_dir, file_inputs_enabled)
            if self._input_exists(ffmpeg):
                GLib.idle_add(self._show_input_exists_dialog, ffmpeg)
                continue
            if self.inputs_page_handlers.is_apply_all_selected():
                self._apply_ffmpeg_template_settings(ffmpeg)

            if not preview.set_info(ffmpeg):
                continue
            self._setup_picture_settings(ffmpeg, file_inputs_enabled)

            GLib.idle_add(self._add_to_inputs_page, ffmpeg)

        GLib.idle_add(self.main_window_handlers.set_processing_inputs_state, False, None)

    def _setup_settings_sidebar_ffmpeg_template(self):
        # Configures the ffmpeg template to match the settings sidebar.
        if self.inputs_page_handlers.is_apply_all_selected():
            ffmpeg_template = self.main_window_handlers.ffmpeg_template
            self.settings_sidebar_handlers.get_settings(ffmpeg_template)

    def _setup_importing_files_widgets(self, file_path, index, length_of_input_files):
        # Shows widgets to display progress on the import process.
        GLib.idle_add(self.inputs_page_handlers.set_importing_file_path_text, file_path)
        GLib.idle_add(self.inputs_page_handlers.set_importing_progress_fraction,
                      (index / length_of_input_files))

    @staticmethod
    def _setup_input_file_paths(ffmpeg, file_path, output_dir, file_inputs_enabled):
        # Sets the input and output file paths for the ffmpeg settings object.
        if file_inputs_enabled:
            ffmpeg.input_file = file_path
            ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(ffmpeg.filename)
        else:
            ffmpeg.input_folder(file_path)
        ffmpeg.output_directory = output_dir + '/'

    def _input_exists(self, ffmpeg):
        for listbox_row in self.inputs_page_handlers.get_rows():
            if ffmpeg.input_file == listbox_row.ffmpeg.input_file:
                return True
        return False

    def _show_input_exists_dialog(self, ffmpeg):
        # Notifies the user that an input has already been added to the inputs page.
        message_dialog = Gtk.MessageDialog(self.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.OK,
                                           'File \"' + ffmpeg.input_file + '\" is already imported')
        message_dialog.run()
        message_dialog.destroy()

    def _apply_ffmpeg_template_settings(self, ffmpeg):
        # Applies the ffmpeg template settings to the ffmepg settings object.
        ffmpeg_template = self.main_window_handlers.ffmpeg_template
        if ffmpeg_template.video_settings:
            ffmpeg.video_settings = copy.deepcopy(ffmpeg_template.video_settings)
        else:
            ffmpeg.video_settings = None
        if ffmpeg_template.audio_settings:
            ffmpeg.audio_settings = copy.deepcopy(ffmpeg_template.audio_settings)
        else:
            ffmpeg.audio_settings = None
        ffmpeg.output_container = ffmpeg_template.output_container
        ffmpeg.general_settings.ffmpeg_args = ffmpeg_template.general_settings.ffmpeg_args.copy()
        if ffmpeg.is_video_settings_2_pass():
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'

    def _setup_picture_settings(self, ffmpeg, file_inputs_enabled):
        # Generates the auto crop settings for the ffmpeg settings object.
        if self.inputs_page_handlers.is_auto_crop_selected():
            if file_inputs_enabled:
                ffmpeg.picture_settings.auto_crop_enabled = preview.process_auto_crop(ffmpeg)
            else:
                ffmpeg.folder_auto_crop = True

    def _add_to_inputs_page(self, ffmpeg):
        # Creates an inputs row for the ffmpeg settings object and adds it to the inputs page.
        inputs_page_listbox_row = InputsRow(ffmpeg,
                                            self.inputs_page_handlers,
                                            self.active_page_handlers,
                                            self.main_window_handlers,
                                            self.encoder_queue,
                                            self.preferences)
        self.inputs_page_handlers.add_row(inputs_page_listbox_row)
