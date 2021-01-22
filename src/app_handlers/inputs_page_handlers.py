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
import time
import os

from urllib.parse import unquote, urlparse
from startup import Gtk, Gdk, GLib
from encoding import directory_helper

TARGET_TYPE_URI_LIST = 80


class InputsPageHandlers:
    def __init__(self, gtk_builder):
        self.settings_sidebar_handlers = None
        self.main_window_handlers = None
        self.active_page_handlers = None
        self.trim_page_handlers = None
        self.crop_page_handlers = None
        self.preview_page_handlers = None
        self.inputs_page_box = gtk_builder.get_object("inputs_box")
        self.inputs_page_listbox = gtk_builder.get_object('inputs_list')
        self.remove_all_inputs_button = gtk_builder.get_object('remove_all_button')
        self.inputs_page_stack = gtk_builder.get_object('inputs_stack')
        self.input_settings_stack = gtk_builder.get_object("settings_stack")
        self.inputs_page_listbox = gtk_builder.get_object('inputs_list')
        self.inputs_page_stack = gtk_builder.get_object('inputs_stack')
        self.start_all_button = gtk_builder.get_object('start_all_button')
        self.remove_all_inputs_button = gtk_builder.get_object('remove_all_button')
        self.apply_to_all_button = gtk_builder.get_object('apply_to_all_button')
        self.auto_crop_button = gtk_builder.get_object('auto_crop_button')
        self.apply_to_all_button = gtk_builder.get_object('apply_to_all_button')
        self.importing_inputs_filepath_label = gtk_builder.get_object('inputs_filepath_label')
        self.importing_inputs_progressbar = gtk_builder.get_object('inputs_progressbar')
        self.importing_inputs_box = gtk_builder.get_object('inputs_proc_box')
        self.extra_settings_box = gtk_builder.get_object('extra_settings_box')
        self.return_to_inputs_button = gtk_builder.get_object('return_to_inputs_button')
        self.extra_settings_stack = gtk_builder.get_object('extra_settings_stack')
        self.trim_page_box = gtk_builder.get_object('trim_page_box')
        self.crop_page_box = gtk_builder.get_object('crop_page_box')
        self.preview_page_box = gtk_builder.get_object('preview_page_box')

        self.inputs_page_listbox.set_header_func(self.__inputs_list_update_header_func, None)
        self.inputs_page_listbox.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.HIGHLIGHT |
                                               Gtk.DestDefaults.DROP, [Gtk.TargetEntry.new("text/uri-list", 0, 80)],
                                               Gdk.DragAction.COPY)

    @staticmethod
    def __inputs_list_update_header_func(inputs_page_listbox_row, previous_inputs_page_listbox_row, data):
        if previous_inputs_page_listbox_row is None:
            inputs_page_listbox_row.set_header(None)
        else:
            inputs_page_listbox_row_header = inputs_page_listbox_row.get_header()

            if inputs_page_listbox_row_header is None:
                inputs_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

                inputs_page_listbox_row_header.show()
                inputs_page_listbox_row.set_header(inputs_page_listbox_row_header)

    def set_processing_inputs_state(self, first_input_file_path):
        self.inputs_page_stack.set_visible_child(self.importing_inputs_box)
        self.importing_inputs_filepath_label.set_text(first_input_file_path)
        self.importing_inputs_progressbar.set_fraction(0.0)

    def set_inputs_state(self):
        self.inputs_page_stack.set_visible_child(self.inputs_page_listbox)
        self.inputs_page_listbox.show_all()

    def set_trim_state(self):
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.trim_page_box)

    def set_crop_state(self):
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.crop_page_box)

    def set_preview_state(self):
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.preview_page_box)

    def is_crop_state(self):
        if self.inputs_page_stack.get_visible_child() == self.extra_settings_box:
            return self.extra_settings_stack.get_visible_child() == self.crop_page_box

        return False

    def is_trim_state(self):
        if self.inputs_page_stack.get_visible_child() == self.extra_settings_box:
            return self.extra_settings_stack.get_visible_child() == self.trim_page_box

        return False

    def is_preview_state(self):
        if self.inputs_page_stack.get_visible_child() == self.extra_settings_box:
            return self.extra_settings_stack.get_visible_child() == self.preview_page_box

        return False

    def setup_add_remove_all_settings_widgets(self):
        settings_enabled = self.inputs_page_listbox.get_children() is not None

        self.start_all_button.set_sensitive(settings_enabled)
        self.remove_all_inputs_button.set_sensitive(settings_enabled)

    def setup_inputs_settings_widgets(self):
        is_apply_all_selected = self.apply_to_all_button.get_active()
        inputs_settings_enabled = is_apply_all_selected or self.get_selected_row()

        self.input_settings_stack.set_sensitive(inputs_settings_enabled)

    def get_rows(self):
        return self.inputs_page_listbox.get_children()

    def get_selected_row(self):
        return self.inputs_page_listbox.get_selected_row()

    def get_selected_row_ffmpeg(self):
        return self.inputs_page_listbox.get_selected_row().ffmpeg

    def get_selected_rows(self):
        selected_row = self.inputs_page_listbox.get_selected_row()

        if self.apply_to_all_button.get_active() or selected_row is None:
            rows = self.inputs_page_listbox.get_children()
        else:
            rows = [selected_row]

        return rows

    def set_text_for_importing_inputs_file_path_label(self, importing_inputs_file_path_text):
        self.importing_inputs_filepath_label.set_text(importing_inputs_file_path_text)

    def set_fraction_for_importing_inputs_progress_bar(self, progress_fraction):
        self.importing_inputs_progressbar.set_fraction(progress_fraction)

    def is_apply_all_selected(self):
        return self.apply_to_all_button.get_active()

    def is_auto_crop_selected(self):
        return self.auto_crop_button.get_active()

    def add_inputs_page_listbox_row(self, inputs_page_listbox_row):
        self.inputs_page_listbox.add(inputs_page_listbox_row)
        self.start_all_button.set_sensitive(True)
        self.remove_all_inputs_button.set_sensitive(True)

    def remove_inputs_page_listbox_row(self, inputs_page_listbox_row):
        self.inputs_page_listbox.remove(inputs_page_listbox_row)

    def update_preview_page(self):
        if self.preview_state:
            self.preview_page_handlers.update_preview()

    @property
    def preview_state(self):
        main_page = self.inputs_page_stack.get_visible_child()
        extra_page = self.extra_settings_stack.get_visible_child()

        return main_page is self.extra_settings_box and extra_page is self.preview_page_box

    def on_remove_all_button_clicked(self, remove_all_button):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            'Remove all inputs?'
        )

        message_dialog.format_secondary_text('This will remove all of your imports along with any settings applied')

        response = message_dialog.run()

        if response == Gtk.ResponseType.YES:
            for row in self.inputs_page_listbox.get_children():
                self.inputs_page_listbox.remove(row)

        message_dialog.destroy()
        self.main_window_handlers.popdown_app_preferences_popover()

    def on_start_all_button_clicked(self, start_all_button):
        self.main_window_handlers.popdown_app_preferences_popover()
        threading.Thread(target=self.__start_all, args=()).start()

    def __start_all(self):
        time.sleep(.2)

        for row in self.inputs_page_listbox.get_children():
            row.on_start_button_clicked(None)

    def on_inputs_list_row_selected(self, inputs_page_listbox, inputs_page_listbox_row):
        if inputs_page_listbox_row is not None:
            self.input_settings_stack.set_sensitive(True)
            self.settings_sidebar_handlers.set_extra_settings_state(not inputs_page_listbox_row.ffmpeg.folder_state)
            threading.Thread(target=self.__set_settings_for_settings_sidebar_handlers, args=()).start()
        else:
            self.settings_sidebar_handlers.set_extra_settings_state(False)

            if self.apply_to_all_button.get_active():
                return

            self.input_settings_stack.set_sensitive(False)
            self.main_window_handlers.show_settings_sidebar(False)

    def __set_settings_for_settings_sidebar_handlers(self):
        GLib.idle_add(self.settings_sidebar_handlers.set_settings)

    def on_inputs_list_remove(self, inputs_page_listbox, inputs_page_listbox_row):
        if not self.inputs_page_listbox.get_children():
            self.remove_all_inputs_button.set_sensitive(False)
            self.start_all_button.set_sensitive(False)

            if self.active_page_handlers.active_page_listbox.get_children():
                self.main_window_handlers.switch_to_active_page()

    def on_inputs_list_drag_data_received(self, inputs_page_listbox, drag_context, x, y, data, target_type,
                                          timestamp):
        if target_type == TARGET_TYPE_URI_LIST:
            inputs = []
            inputs_uri = data.get_data().decode()
            inputs_uri_list = inputs_uri.split()

            for file_path_uri in inputs_uri_list:
                input_path = unquote(urlparse(file_path_uri).path)

                if self.main_window_handlers.get_add_type_combobox_index() == 0:

                    if os.path.isfile(input_path):
                        inputs.append(input_path)
                    else:
                        inputs.extend(directory_helper.get_files_in_directory(input_path, recursive=True))
                else:
                    if os.path.isdir(input_path):
                        inputs.append(input_path)

            if inputs:
                self.main_window_handlers.on_add_button_clicked(self.main_window_handlers.add_button, inputs=inputs)

    def on_return_to_inputs_button_clicked(self, return_to_inputs_button):
        self.set_inputs_state()
        self.trim_page_handlers.reset_trim_page()
        self.crop_page_handlers.reset_crop_page()
        self.preview_page_handlers.reset_preview_page()
        threading.Thread(target=self.__update_selected_row, args=()).start()

    def __update_selected_row(self):
        GLib.idle_add(self.inputs_page_listbox.get_selected_row().setup_labels)
        self.inputs_page_listbox.get_selected_row().setup_preview_thumbnail()
