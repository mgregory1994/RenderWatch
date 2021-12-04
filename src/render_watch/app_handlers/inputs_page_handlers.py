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


from render_watch.app_handlers.preview_page_handlers import PreviewPageHandlers
from render_watch.app_handlers.crop_page_handlers import CropPageHandlers
from render_watch.app_handlers.trim_page_handlers import TrimPageHandlers
from render_watch.app_handlers.settings_sidebar_handlers import SettingsSidebarHandlers
from render_watch.signals.inputs_page.drag_and_drop_signal import DragAndDropSignal
from render_watch.signals.inputs_page.page_return_signal import PageReturnSignal
from render_watch.signals.inputs_page.remove_all_signal import RemoveAllSignal
from render_watch.signals.inputs_page.remove_signal import RemoveSignal
from render_watch.signals.inputs_page.select_row_signal import SelectRowSignal
from render_watch.signals.inputs_page.start_all_signal import StartAllSignal
from render_watch.startup import Gtk, Gdk


class InputsPageHandlers:
    """
    Handles all widget changes on the active page.
    """

    def __init__(self, gtk_builder, active_page_handlers, main_window_handlers, application_preferences):
        preview_page_handlers = PreviewPageHandlers(gtk_builder, self, application_preferences)
        crop_page_handlers = CropPageHandlers(gtk_builder, self, main_window_handlers, application_preferences)
        trim_page_handlers = TrimPageHandlers(gtk_builder, self, application_preferences)
        self.settings_sidebar_handlers = SettingsSidebarHandlers(gtk_builder,
                                                                 crop_page_handlers,
                                                                 trim_page_handlers,
                                                                 preview_page_handlers,
                                                                 self,
                                                                 main_window_handlers,
                                                                 application_preferences)
        self.preview_page_handlers = preview_page_handlers

        self._setup_signals(main_window_handlers,
                            active_page_handlers,
                            trim_page_handlers,
                            crop_page_handlers,
                            preview_page_handlers)
        self._setup_widgets(gtk_builder)

    def _setup_signals(self,
                       main_window_handlers,
                       active_page_handlers,
                       trim_page_handlers,
                       crop_page_handlers,
                       preview_page_handlers):
        self.drag_and_drop_signal = DragAndDropSignal(main_window_handlers)
        self.page_return_signal = PageReturnSignal(self, trim_page_handlers, crop_page_handlers, preview_page_handlers)
        self.remove_all_signal = RemoveAllSignal(self, main_window_handlers)
        self.remove_signal = RemoveSignal(self, active_page_handlers, main_window_handlers)
        self.select_row_signal = SelectRowSignal(self, self.settings_sidebar_handlers, main_window_handlers)
        self.start_all_signal = StartAllSignal(self, main_window_handlers)
        self.signals_list = (
            self.drag_and_drop_signal, self.page_return_signal, self.remove_all_signal,
            self.remove_signal, self.select_row_signal, self.start_all_signal, preview_page_handlers,
            crop_page_handlers, trim_page_handlers, self.settings_sidebar_handlers
        )

    def _setup_widgets(self, gtk_builder):
        self.inputs_list = gtk_builder.get_object('inputs_list')
        self.remove_all_button = gtk_builder.get_object('remove_all_button')
        self.inputs_page_stack = gtk_builder.get_object('inputs_page_stack')
        self.toggle_settings_sidebar_button = gtk_builder.get_object("toggle_settings_sidebar_button")
        self.start_all_button = gtk_builder.get_object('start_all_button')
        self.remove_all_button = gtk_builder.get_object('remove_all_button')
        self.apply_settings_to_all_switch = gtk_builder.get_object('apply_settings_to_all_switch')
        self.auto_crop_inputs_checkbutton = gtk_builder.get_object('auto_crop_inputs_checkbutton')
        self.adding_inputs_file_path_label = gtk_builder.get_object('adding_inputs_file_path_label')
        self.adding_inputs_progressbar = gtk_builder.get_object('adding_inputs_progressbar')
        self.adding_inputs_box = gtk_builder.get_object('adding_inputs_box')
        self.extra_settings_box = gtk_builder.get_object('extra_settings_box')
        self.return_to_inputs_list_button = gtk_builder.get_object('return_to_inputs_list_button')
        self.extra_settings_stack = gtk_builder.get_object('extra_settings_stack')
        self.trim_page_box = gtk_builder.get_object('trim_page_box')
        self.picture_settings_page_box = gtk_builder.get_object('picture_settings_page_box')
        self.preview_page_box = gtk_builder.get_object('preview_page_box')

        self.inputs_list.set_header_func(self._inputs_list_update_header_func, None)
        self.inputs_list.drag_dest_set(Gtk.DestDefaults.MOTION
                                       | Gtk.DestDefaults.HIGHLIGHT
                                       | Gtk.DestDefaults.DROP,
                                       [Gtk.TargetEntry.new("text/uri-list", 0, 80)],
                                       Gdk.DragAction.COPY)

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    # Unused parameters needed for this function
    @staticmethod
    def _inputs_list_update_header_func(inputs_page_listbox_row, previous_inputs_page_listbox_row, data=None):
        if previous_inputs_page_listbox_row is None:
            inputs_page_listbox_row.set_header(None)
        else:
            inputs_page_listbox_row_header = inputs_page_listbox_row.get_header()

            if inputs_page_listbox_row_header is None:
                inputs_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                inputs_page_listbox_row_header.show()
                inputs_page_listbox_row.set_header(inputs_page_listbox_row_header)

    def set_processing_inputs_state(self, first_input_file_path):
        """
        Shows/hides widgets that show the progress of importing files.
        """
        self.inputs_page_stack.set_visible_child(self.adding_inputs_box)
        self.adding_inputs_file_path_label.set_text(first_input_file_path)
        self.adding_inputs_progressbar.set_fraction(0.0)

    def set_inputs_state(self):
        """
        Shows the tasks list for imported inputs.
        """
        self.inputs_page_stack.set_visible_child(self.inputs_list)
        self.inputs_list.show_all()

    def set_trim_state(self):
        """
        Shows the trim page
        """
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.trim_page_box)

    def set_crop_state(self):
        """
        Shows the crop page.
        """
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.picture_settings_page_box)

    def set_preview_state(self):
        """
        Shows the preview page.
        """
        self.inputs_page_stack.set_visible_child(self.extra_settings_box)
        self.extra_settings_stack.set_visible_child(self.preview_page_box)

    def is_crop_state(self):
        main_page = self.inputs_page_stack.get_visible_child()
        extra_page = self.extra_settings_stack.get_visible_child()

        return main_page is self.extra_settings_box and extra_page is self.picture_settings_page_box

    def is_trim_state(self):
        main_page = self.inputs_page_stack.get_visible_child()
        extra_page = self.extra_settings_stack.get_visible_child()

        return main_page is self.extra_settings_box and extra_page is self.trim_page_box

    def is_preview_state(self):
        main_page = self.inputs_page_stack.get_visible_child()
        extra_page = self.extra_settings_stack.get_visible_child()

        return main_page is self.extra_settings_box and extra_page is self.preview_page_box

    def setup_page_options(self):
        """
        Toggles the options available to the inputs page from the options popover.
        """
        settings_enabled = self.inputs_list.get_children() is not None
        self.start_all_button.set_sensitive(settings_enabled)
        self.remove_all_button.set_sensitive(settings_enabled)

    def setup_inputs_settings_widgets(self):
        """
        Toggles accessibility to the settings sidebar if there's a task in the inputs list.
        """
        is_apply_all_selected = self.apply_settings_to_all_switch.get_active()
        inputs_settings_enabled = is_apply_all_selected or self.get_selected_row()
        self.toggle_settings_sidebar_button.set_sensitive(inputs_settings_enabled)

    def get_rows(self):
        return self.inputs_list.get_children()

    def get_selected_row(self):
        return self.inputs_list.get_selected_row()

    def get_selected_row_ffmpeg(self):
        return self.inputs_list.get_selected_row().ffmpeg

    def get_selected_rows(self):
        selected_row = self.inputs_list.get_selected_row()

        if self.apply_settings_to_all_switch.get_active() or selected_row is None:
            return self.inputs_list.get_children()
        return [selected_row]

    def set_importing_file_path_text(self, importing_inputs_file_path_text):
        self.adding_inputs_file_path_label.set_text(importing_inputs_file_path_text)

    def set_importing_progress_fraction(self, progress_fraction):
        self.adding_inputs_progressbar.set_fraction(progress_fraction)

    def is_apply_all_selected(self):
        return self.apply_settings_to_all_switch.get_active()

    def is_auto_crop_selected(self):
        return self.auto_crop_inputs_checkbutton.get_active()

    def add_row(self, inputs_page_listbox_row):
        self.inputs_list.add(inputs_page_listbox_row)
        self.start_all_button.set_sensitive(True)
        self.remove_all_button.set_sensitive(True)

    def remove_row(self, inputs_page_listbox_row):
        self.inputs_list.remove(inputs_page_listbox_row)

    def remove_all_rows(self):
        for row in self.get_rows():
            self.remove_row(row)

    def set_input_settings_state(self, enabled):
        self.toggle_settings_sidebar_button.set_sensitive(enabled)

    def set_remove_all_state(self):
        self.remove_all_button.set_sensitive(False)
        self.start_all_button.set_sensitive(False)

    def set_preview_encoding_state(self, is_preview_encoding):
        self.return_to_inputs_list_button.set_sensitive(not is_preview_encoding)

    def update_preview_page(self):
        if self.is_preview_state():
            self.preview_page_handlers.update_preview()
