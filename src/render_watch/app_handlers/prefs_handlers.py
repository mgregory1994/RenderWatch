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

import logging

from render_watch.startup.preferences import Preferences
from render_watch.helpers import directory_helper
from render_watch.startup import Gtk


class PrefsHandlers:
    def __init__(self, gtk_builder, gtk_settings, preferences):
        self.gtk_settings = gtk_settings
        self.main_window_handlers = None
        self.preferences = preferences
        self.original_temp_directory = preferences.temp_directory
        self.original_parallel_tasks_index = Preferences.parallel_tasks_values_list.index(
            preferences.parallel_tasks_as_string)
        self.prefs_dialog = gtk_builder.get_object("prefs_dialog")
        self.prefs_concurrent_combobox = gtk_builder.get_object('prefs_concurrent_combobox')
        self.prefs_concurrent_message_stack = gtk_builder.get_object('prefs_concurrent_message_stack')
        self.prefs_concurrent_message_8 = gtk_builder.get_object('prefs_concurrent_message_8')
        self.prefs_concurrent_message_12 = gtk_builder.get_object('prefs_concurrent_message_12')
        self.prefs_concurrent_message_24 = gtk_builder.get_object('prefs_concurrent_message_24')
        self.prefs_concurrent_message_32 = gtk_builder.get_object('prefs_concurrent_message_32')
        self.prefs_concurrent_message_final = gtk_builder.get_object('prefs_concurrent_message_final')
        self.prefs_concurrent_restart_stack = gtk_builder.get_object('prefs_concurrent_restart_stack')
        self.prefs_concurrent_restart_image = gtk_builder.get_object('prefs_concurrent_restart_image')
        self.prefs_concurrent_empty_label = gtk_builder.get_object('prefs_concurrent_empty_label')
        self.prefs_nvenc_concurrent_warning_stack = gtk_builder.get_object('prefs_nvenc_concurrent_warning_stack')
        self.prefs_nvenc_concurrent_empty_label = gtk_builder.get_object('prefs_nvenc_concurrent_empty_label')
        self.prefs_nvenc_concurrent_warning_image = gtk_builder.get_object('prefs_nvenc_concurrent_warning_image')
        self.prefs_temp_restart_stack = gtk_builder.get_object('prefs_temp_restart_stack')
        self.prefs_temp_restart_image = gtk_builder.get_object('prefs_temp_restart_image')
        self.prefs_temp_empty_label = gtk_builder.get_object('prefs_temp_empty_label')
        self.prefs_dark_theme_checkbox = gtk_builder.get_object("prefs_dark_theme_checkbox")
        self.prefs_temp_chooserbutton = gtk_builder.get_object('prefs_temp_chooserbutton')

    def on_prefs_concurrent_combobox_changed(self, concurrent_combobox):
        parallel_tasks_value = Preferences.parallel_tasks_values_list[concurrent_combobox.get_active()]
        self.preferences.parallel_tasks = parallel_tasks_value

        self.__setup_concurrent_setting_restart_required_widgets(concurrent_combobox)
        self.__setup_concurrent_message_widgets(parallel_tasks_value)

    def __setup_concurrent_setting_restart_required_widgets(self, concurrent_combobox):
        if concurrent_combobox.get_active() == self.original_parallel_tasks_index:
            self.prefs_concurrent_restart_stack.set_visible_child(self.prefs_concurrent_empty_label)
        else:
            self.prefs_concurrent_restart_stack.set_visible_child(self.prefs_concurrent_restart_image)

    def __setup_concurrent_message_widgets(self, parallel_tasks_value):
        if parallel_tasks_value == '2':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_8)
        elif parallel_tasks_value == '3':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_12)
        elif parallel_tasks_value == '4':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_24)
        elif parallel_tasks_value == '6':
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_32)
        else:
            self.prefs_concurrent_message_stack.set_visible_child(self.prefs_concurrent_message_final)

    def on_prefs_nvenc_concurrent_combobox_changed(self, nvenc_concurrent_combobox):
        concurrent_nvenc_text = Preferences.concurrent_nvenc_values_list[nvenc_concurrent_combobox.get_active()]
        self.preferences.concurrent_nvenc_value = concurrent_nvenc_text

        self.__setup_nvenc_concurrent_setting_restart_required_widgets(concurrent_nvenc_text)

    def __setup_nvenc_concurrent_setting_restart_required_widgets(self, concurrent_nvenc_text):
        if concurrent_nvenc_text != 'auto':
            self.prefs_nvenc_concurrent_warning_stack.set_visible_child(self.prefs_nvenc_concurrent_warning_image)
        else:
            self.prefs_nvenc_concurrent_warning_stack.set_visible_child(self.prefs_nvenc_concurrent_empty_label)

    def on_prefs_temp_chooserbutton_file_set(self, temp_file_chooser):
        temp_file_path = temp_file_chooser.get_filename()

        try:
            self.__check_temp_directory_accessible(temp_file_chooser, temp_file_path)
            self.__check_temp_directory_empty(temp_file_chooser, temp_file_path)
        except ImportError:
            logging.warning('--- NOT SETTING TEMP FOLDER DIRECTORY: ' + temp_file_path + ' ---')
        else:
            self.__setup_temp_setting_restart_required_widgets(temp_file_path)

            self.preferences.temp_directory = temp_file_path

    def __check_temp_directory_accessible(self, temp_file_chooser, temp_file_path):
        if not directory_helper.is_directory_accessible(temp_file_path):
            self.__show_directory_not_accessible_dialog(temp_file_path)
            temp_file_chooser.set_filename(self.original_temp_directory)

            raise ImportError

    def __show_directory_not_accessible_dialog(self, directory):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Directory \"' + directory + '\" is not accessible'
        )

        message_dialog.format_secondary_text('Check permissions or select a different directory.')
        message_dialog.run()
        message_dialog.destroy()

    def __check_temp_directory_empty(self, temp_file_chooser, temp_file_path):
        if not directory_helper.is_directory_empty(temp_file_path):
            message_response = self.__show_directory_not_empty_message_dialog(temp_file_path)

            if message_response == Gtk.ResponseType.NO:
                temp_file_chooser.set_filename(self.original_temp_directory)

                raise ImportError

    def __show_directory_not_empty_message_dialog(self, directory):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            'Directory \"' + directory + '\" is not empty'
        )

        message_dialog.format_secondary_text('It is highly recommended that you choose an empty directory due to '
                                             'potential DATA LOSS.\n\n'
                                             'This is especially dangerous when using the \"Clear Temp Folder'
                                             ' on Exit\" option.\n\n'
                                             'Are you sure you want to use this directory?')

        response = message_dialog.run()

        message_dialog.destroy()

        return response

    def __setup_temp_setting_restart_required_widgets(self, temp_file_path):
        if temp_file_path == self.original_temp_directory:
            self.prefs_temp_restart_stack.set_visible_child(self.prefs_temp_empty_label)
        else:
            self.prefs_temp_restart_stack.set_visible_child(self.prefs_temp_restart_image)

    def on_prefs_clear_checkbox_toggled(self, clear_temp_directory_checkbox):
        clear_temp_directory_enabled = clear_temp_directory_checkbox.get_active()

        if clear_temp_directory_enabled:
            self.__show_clear_temp_warning_dialog()

        self.preferences.clear_temp_directory_on_exit = clear_temp_directory_enabled

    def __show_clear_temp_warning_dialog(self):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Possible data loss'
        )

        message_dialog.format_secondary_text('This option deletes the chosen temp directory when closing '
                                             'Render Watch.\n\nThis can lead to possible DATA LOSS.\n\n'
                                             'USE WITH CAUTION!')
        message_dialog.run()
        message_dialog.destroy()

    def on_prefs_overwrite_outputs_checkbox_toggled(self, overwrite_outputs_checkbox):
        self.preferences.overwrite_outputs = overwrite_outputs_checkbox.get_active()

    def on_prefs_nvenc_concurrent_checkbox_toggled(self, nvenc_concurrent_checkbox):
        self.preferences.concurrent_nvenc = nvenc_concurrent_checkbox.get_active()

    def on_prefs_move_to_done_checkbox_toggled(self, watch_folder_move_finished_to_done_checkbox):
        self.preferences.watch_folder_move_finished_to_done = watch_folder_move_finished_to_done_checkbox.get_active()

    def on_prefs_watch_concurrent_checkbox_toggled(self, watch_folder_concurrent_checkbox):
        self.preferences.concurrent_watch_folder = watch_folder_concurrent_checkbox.get_active()

    def on_prefs_wait_for_tasks_checkbox_toggled(self, watch_folder_wait_for_other_tasks_checkbox):
        self.preferences.watch_folder_wait_for_other_tasks = watch_folder_wait_for_other_tasks_checkbox.get_active()

    def on_prefs_dark_theme_switch_state_set(self, dark_theme_switch, user_data):
        dark_mode = dark_theme_switch.get_active()
        self.preferences.use_dark_mode = dark_mode

        self.gtk_settings.set_property('gtk-application-prefer-dark-theme', dark_mode)
