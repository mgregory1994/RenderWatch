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
import copy
import os

from render_watch.app_handlers.inputs_row import InputsRow
from render_watch.ffmpeg.settings import Settings
from render_watch.encoding import directory_helper
from render_watch.encoding import preview
from render_watch.encoding import encoder_helper
from render_watch.app_formatting.alias import AliasGenerator
from render_watch.startup import Gtk, GLib


class MainWindowHandlers:
    def __init__(self, gtk_builder, encoder, preferences):
        self.ffmpeg_template = None
        self.encoder = encoder
        self.preferences = preferences
        self.inputs_page_handlers = None
        self.settings_sidebar_handlers = None
        self.active_page_handlers = None
        self.completed_page_handlers = None
        self.pages_stack = gtk_builder.get_object('page_stack')
        self.active_page_scroller = gtk_builder.get_object("active_scroller")
        self.app_preferences_popover = gtk_builder.get_object('prefs_popover')
        self.app_preferences_stack = gtk_builder.get_object("prefs_pages_stack")
        self.app_preferences_inputs_page_box = gtk_builder.get_object("prefs_inputs_box")
        self.app_preferences_active_page_box = gtk_builder.get_object("prefs_active_box")
        self.app_preferences_menubutton = gtk_builder.get_object('prefs_menu_button')
        self.about_dialog = gtk_builder.get_object("about_dialog")
        self.input_settings_revealer = gtk_builder.get_object("settings_revealer")
        self.input_settings_stack = gtk_builder.get_object("settings_stack")
        self.show_input_settings_button = gtk_builder.get_object("show_settings_button")
        self.hide_input_settings_button = gtk_builder.get_object("hide_settings_button")
        self.preferences_button = gtk_builder.get_object("prefs_button")
        self.preferences_dialog = gtk_builder.get_object("prefs_dialog")
        self.output_file_chooser_button = gtk_builder.get_object("output_chooserbutton")
        self.add_button = gtk_builder.get_object("add_button")
        self.add_combobox = gtk_builder.get_object('add_combobox')
        self.parallel_tasks_type_buttonbox = gtk_builder.get_object('dist_proc_type_buttonbox')
        self.parallel_tasks_radiobutton = gtk_builder.get_object('dist_proc_button')
        self.parallel_tasks_chunks_radiobutton = gtk_builder.get_object('chunks_radio_button')
        self.main_window = gtk_builder.get_object('main_window')

    def is_chunk_processing_selected(self):
        parallel_tasks_enabled = self.parallel_tasks_radiobutton.get_active()
        parallel_tasks_chunks_enabled = self.parallel_tasks_chunks_radiobutton.get_active()

        return parallel_tasks_enabled and parallel_tasks_chunks_enabled

    def switch_to_active_page(self):
        self.pages_stack.set_visible_child(self.active_page_scroller)

    def get_add_type_combobox_index(self):
        return self.add_combobox.get_active()

    def popdown_app_preferences_popover(self):
        self.app_preferences_popover.popdown()

    def on_about_button_clicked(self, about_button):
        self.app_preferences_popover.popdown()
        self.about_dialog.run()
        self.about_dialog.hide()

    def on_show_settings_button_clicked(self, show_settings_button):
        self.show_settings_sidebar(True)

    def on_hide_settings_button_clicked(self, hide_settings_button):
        self.show_settings_sidebar(False)

    def show_settings_sidebar(self, is_show_enabled):
        if is_show_enabled:
            self.input_settings_stack.set_visible_child(self.hide_input_settings_button)
        else:
            self.input_settings_stack.set_visible_child(self.show_input_settings_button)

        self.input_settings_revealer.set_reveal_child(is_show_enabled)

    def on_add_button_clicked(self, add_button, inputs=None):
        file_inputs_enabled = self.add_combobox.get_active() == 0

        if inputs is None:

            if file_inputs_enabled:
                file_chooser_response, inputs = self.__create_and_show_file_chooser()
            else:
                file_chooser_response, inputs = self.__create_and_show_folder_chooser()
        else:
            file_chooser_response = Gtk.ResponseType.OK

        threading.Thread(target=self.__setup_and_process_inputs_state,
                         args=(inputs, file_chooser_response, file_inputs_enabled), daemon=True).start()

    def __create_and_show_file_chooser(self):
        file_chooser = Gtk.FileChooserDialog('Choose a file', self.main_window, Gtk.FileChooserAction.OPEN,
                                             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                                              Gtk.ResponseType.OK))

        file_chooser.set_select_multiple(True)

        response = file_chooser.run()
        files = file_chooser.get_filenames()

        file_chooser.destroy()

        return response, files

    def __create_and_show_folder_chooser(self):
        file_chooser = Gtk.FileChooserDialog('Choose a folder', self.main_window, Gtk.FileChooserAction.SELECT_FOLDER,
                                             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                                              Gtk.ResponseType.OK))

        file_chooser.set_select_multiple(True)

        response = file_chooser.run()
        folders = file_chooser.get_filenames()

        file_chooser.destroy()

        return response, folders

    def __setup_and_process_inputs_state(self, inputs, file_chooser_response, file_inputs_enabled):
        if file_inputs_enabled:
            inputs = [value for value in inputs if encoder_helper.is_input_valid(value)]
        else:
            inputs = [value for value in inputs if os.path.isdir(value)]

        output_dir = self.output_file_chooser_button.get_filename()

        if file_chooser_response == Gtk.ResponseType.OK and inputs:
            GLib.idle_add(self.__set_processing_inputs_state, False, inputs[0])
            threading.Thread(target=self.__process_inputs, args=(inputs, output_dir, file_inputs_enabled),
                             daemon=True).start()

    def __set_processing_inputs_state(self, is_state_disabled, first_input_file_path):
        if not is_state_disabled:
            self.inputs_page_handlers.set_processing_inputs_state(first_input_file_path)
            self.add_button.set_sensitive(is_state_disabled)
            self.add_combobox.set_sensitive(is_state_disabled)
            self.input_settings_stack.set_sensitive(is_state_disabled)
            self.output_file_chooser_button.set_sensitive(is_state_disabled)
            self.app_preferences_menubutton.set_sensitive(is_state_disabled)
        else:
            self.inputs_page_handlers.setup_inputs_settings_widgets()
            self.inputs_page_handlers.setup_add_remove_all_settings_widgets()
            self.add_button.set_sensitive(is_state_disabled)
            self.add_combobox.set_sensitive(is_state_disabled)
            self.output_file_chooser_button.set_sensitive(is_state_disabled)
            self.app_preferences_menubutton.set_sensitive(is_state_disabled)
            self.inputs_page_handlers.set_inputs_state()

    def __process_inputs(self, inputs, output_dir, file_inputs_enabled):
        self.__setup_ffmpeg_template_for_settings_sidebar_handlers()

        length_of_input_files = len(inputs)

        for index, file_path in enumerate(inputs):
            self.__setup_importing_files_widgets_for_inputs_page_handlers(file_path, index, length_of_input_files)

            ffmpeg = Settings()

            self.__setup_input_file_path_settings(ffmpeg, file_path, output_dir, file_inputs_enabled)

            if self.__check_input_exists(ffmpeg):
                GLib.idle_add(self.__show_input_exists_dialog, ffmpeg)

                continue

            if self.inputs_page_handlers.is_apply_all_selected():
                self.__apply_ffmpeg_template_settings(ffmpeg)

            if not preview.set_info(ffmpeg):
                continue

            self.__setup_input_picture_settings(ffmpeg, file_inputs_enabled)

            GLib.idle_add(self.__create_and_add_new_inputs_row, ffmpeg)

        GLib.idle_add(self.__set_processing_inputs_state, True, None)

    def __setup_ffmpeg_template_for_settings_sidebar_handlers(self):
        if self.inputs_page_handlers.is_apply_all_selected():
            self.settings_sidebar_handlers.get_settings(self.ffmpeg_template)

    def __setup_importing_files_widgets_for_inputs_page_handlers(self, file_path, index, length_of_input_files):
        GLib.idle_add(self.inputs_page_handlers.set_text_for_importing_inputs_file_path_label, file_path)
        GLib.idle_add(self.inputs_page_handlers.set_fraction_for_importing_inputs_progress_bar,
                      (index / length_of_input_files))

    @staticmethod
    def __setup_input_file_path_settings(ffmpeg, file_path, output_dir, file_inputs_enabled):
        if file_inputs_enabled:
            ffmpeg.input_file = file_path
            ffmpeg.temp_file_name = AliasGenerator.generate_alias_from_name(ffmpeg.filename)
            ffmpeg.output_directory = output_dir + '/'
        else:
            ffmpeg.input_folder = file_path
            ffmpeg.output_directory = output_dir + '/'

    def __check_input_exists(self, ffmpeg):
        for listbox_row in self.inputs_page_handlers.get_rows():
            if ffmpeg.input_file == listbox_row.ffmpeg.input_file:
                return True

        return False

    def __show_input_exists_dialog(self, ffmpeg):
        message_dialog = Gtk.MessageDialog(
            self.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'File \"' + ffmpeg.input_file + '\" is already imported'
        )

        message_dialog.run()
        message_dialog.destroy()

    def __apply_ffmpeg_template_settings(self, ffmpeg):
        if self.ffmpeg_template.video_settings is not None:
            ffmpeg.video_settings = copy.deepcopy(self.ffmpeg_template.video_settings)
        else:
            ffmpeg.video_settings = None

        if self.ffmpeg_template.audio_settings is not None:
            ffmpeg.audio_settings = copy.deepcopy(self.ffmpeg_template.audio_settings)
        else:
            ffmpeg.audio_settings = None

        ffmpeg.general_settings.ffmpeg_args = self.ffmpeg_template.general_settings.ffmpeg_args.copy()

        if ffmpeg.is_video_settings_2_pass():
            ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + ffmpeg.temp_file_name + '.log'

    def __setup_input_picture_settings(self, ffmpeg, file_inputs_enabled):
        if self.inputs_page_handlers.is_auto_crop_selected():

            if file_inputs_enabled:
                ffmpeg.picture_settings.auto_crop = preview.process_auto_crop(ffmpeg)
            else:
                ffmpeg.folder_auto_crop = True

    def __create_and_add_new_inputs_row(self, ffmpeg):
        inputs_page_listbox_row = InputsRow(ffmpeg, self.inputs_page_handlers, self.active_page_handlers, self,
                                            self.encoder, self.preferences)

        self.inputs_page_handlers.add_inputs_page_listbox_row(inputs_page_listbox_row)

    def on_page_stack_visible_child_notify(self, page_stack, string):
        self.show_settings_sidebar(False)

        if page_stack.get_visible_child() == self.inputs_page_handlers.inputs_page_box:
            self.__set_inputs_page_state()
        elif page_stack.get_visible_child() == self.active_page_scroller:
            self.__set_active_page_state()
        else:
            self.__set_completed_page_state()

    def __set_inputs_page_state(self):
        self.app_preferences_stack.set_visible_child(self.app_preferences_inputs_page_box)
        self.output_file_chooser_button.set_sensitive(True)
        self.add_button.set_sensitive(True)
        self.add_combobox.set_sensitive(True)
        self.inputs_page_handlers.setup_inputs_settings_widgets()

    def __set_active_page_state(self):
        self.app_preferences_stack.set_visible_child(self.app_preferences_active_page_box)
        self.input_settings_stack.set_sensitive(False)
        self.output_file_chooser_button.set_sensitive(False)
        self.add_button.set_sensitive(False)
        self.add_combobox.set_sensitive(False)

    def __set_completed_page_state(self):
        self.app_preferences_stack.set_visible_child(self.completed_page_handlers.clear_all_completed_button)
        self.input_settings_stack.set_sensitive(False)
        self.output_file_chooser_button.set_sensitive(False)
        self.add_button.set_sensitive(False)
        self.add_combobox.set_sensitive(False)

    def on_prefs_button_clicked(self, prefs_button):
        self.app_preferences_popover.popdown()
        self.preferences_dialog.run()
        self.preferences_dialog.hide()

    def on_apply_to_all_button_toggled(self, apply_to_all_checkbox):
        inputs_page_listbox_row = self.inputs_page_handlers.get_selected_row()

        if apply_to_all_checkbox.get_active():

            if inputs_page_listbox_row is not None:
                self.ffmpeg_template = inputs_page_listbox_row.ffmpeg.get_copy()

                #threading.Thread(target=self.__set_settings_for_settings_sidebar_handlers,
                                 #args=(self.ffmpeg_template,)).start()
            else:
                self.ffmpeg_template = Settings()

            #threading.Thread(target=self.__apply_settings_to_all, args=(self.ffmpeg_template,)).start()
            threading.Thread(target=self.__set_settings_and_apply_to_all, args=()).start()
            self.input_settings_stack.set_sensitive(True)
        else:

            if inputs_page_listbox_row is None:
                self.input_settings_stack.set_sensitive(False)
                self.input_settings_revealer.set_reveal_child(False)
                self.input_settings_stack.set_visible_child(self.show_input_settings_button)

    def __set_settings_and_apply_to_all(self):
        video_settings = self.ffmpeg_template.video_settings

        if video_settings is None:
            self.__reset_settings_for_settings_sidebar_handlers()
        else:
            self.__set_settings_for_settings_sidebar_handlers(self.ffmpeg_template)

        self.__apply_settings_to_all(self.ffmpeg_template)

    def __reset_settings_for_settings_sidebar_handlers(self):
        GLib.idle_add(self.settings_sidebar_handlers.reset_settings)

    def __set_settings_for_settings_sidebar_handlers(self, ffmpeg):
        GLib.idle_add(self.settings_sidebar_handlers.set_settings, ffmpeg)

    def __apply_settings_to_all(self, ffmpeg):
        for row in self.inputs_page_handlers.get_rows():
            row_ffmpeg = row.ffmpeg

            if ffmpeg.video_settings is not None:
                row_ffmpeg.video_settings = copy.deepcopy(ffmpeg.video_settings)
            else:
                row_ffmpeg.video_settings = None

            if ffmpeg.audio_settings is not None:
                row_ffmpeg.audio_settings = copy.deepcopy(ffmpeg.audio_settings)
            else:
                row.ffmpeg.audio_settings = None

            row_ffmpeg.general_settings.ffmpeg_args = ffmpeg.general_settings.ffmpeg_args.copy()

            if row_ffmpeg.is_video_settings_2_pass():
                row_ffmpeg.video_settings.stats = self.preferences.temp_directory + '/' + row_ffmpeg.temp_file_name + '.log'

            GLib.idle_add(row.setup_labels)

    def on_auto_crop_button_toggled(self, auto_crop_checkbox):
        for inputs_page_listbox_row in self.inputs_page_handlers.get_rows():
            if inputs_page_listbox_row.ffmpeg.folder_state:
                inputs_page_listbox_row.ffmpeg.folder_auto_crop = auto_crop_checkbox.get_active()

    def on_dist_proc_button_toggled(self, parallel_tasks_radiobutton):
        self.encoder.parallel_tasks_enabled = parallel_tasks_radiobutton.get_active()
        self.parallel_tasks_type_buttonbox.set_sensitive(parallel_tasks_radiobutton.get_active())

    def on_output_chooserbutton_file_set(self, file_chooser_button):
        folder_path = file_chooser_button.get_filename()

        if not directory_helper.is_directory_accessible(folder_path):
            message_dialog = Gtk.MessageDialog(
                self.main_window,
                Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                'Directory \"' + folder_path + '\" is not accessable'
            )

            message_dialog.format_secondary_text('Check permissions or select a different directory.')
            message_dialog.run()
            message_dialog.destroy()
            file_chooser_button.set_filename(self.preferences.output_directory)

            return

        self.__setup_new_output_directory(folder_path)

    def __setup_new_output_directory(self, folder_path):
        self.preferences.output_directory = folder_path
        output_dir = folder_path + '/'

        for row in self.inputs_page_handlers.get_rows():
            row.ffmpeg.output_directory = output_dir

            row.setup_labels()
