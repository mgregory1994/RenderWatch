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


from render_watch.ffmpeg.settings import Settings
from render_watch.app_handlers.completed_page_handlers import CompletedPageHandlers
from render_watch.app_handlers.active_page_handlers import ActivePageHandlers
from render_watch.app_handlers.inputs_page_handlers import InputsPageHandlers
from render_watch.signals.main_window.about_signal import AboutSignal
from render_watch.signals.main_window.add_input_signal import AddInputSignal
from render_watch.signals.main_window.apply_settings_all_signal import ApplySettingsAllSignal
from render_watch.signals.main_window.auto_crop_signal import AutoCropSignal
from render_watch.signals.main_window.output_chooser_signal import OutputChooserSignal
from render_watch.signals.main_window.page_switch_signal import PageSwitchSignal
from render_watch.signals.main_window.parallel_tasks_signal import ParallelTasksSignal
from render_watch.signals.main_window.preferences_signal import PreferencesSignal
from render_watch.signals.main_window.settings_sidebar_signal import SettingsSidebarSignal


class MainWindowHandlers:
    """Handles all widget changes for the main window."""

    def __init__(self, gtk_builder, encoder_queue, preferences):
        self.encoder_queue = encoder_queue
        self.preferences = preferences
        self.completed_page_handlers = CompletedPageHandlers(gtk_builder, self)
        self.active_page_handlers = ActivePageHandlers(gtk_builder, self.completed_page_handlers, self, preferences)
        self.inputs_page_handlers = InputsPageHandlers(gtk_builder, self.active_page_handlers, self, preferences)
        self.settings_sidebar_handlers = self.inputs_page_handlers.settings_sidebar_handlers
        self.ffmpeg_template = None
        self.about_signal = AboutSignal(self)
        self.add_input_signal = AddInputSignal(self,
                                               self.inputs_page_handlers,
                                               self.active_page_handlers,
                                               self.settings_sidebar_handlers,
                                               self.encoder_queue,
                                               self.preferences)
        self.apply_settings_all_signal = ApplySettingsAllSignal(self,
                                                                self.inputs_page_handlers,
                                                                self.settings_sidebar_handlers,
                                                                self.preferences)
        self.auto_crop_signal = AutoCropSignal(self.inputs_page_handlers)
        self.output_chooser_signal = OutputChooserSignal(self, self.inputs_page_handlers, self.preferences)
        self.page_switch_signal = PageSwitchSignal(self, self.inputs_page_handlers)
        self.parallel_tasks_signal = ParallelTasksSignal(self, self.encoder_queue)
        self.preferences_signal = PreferencesSignal(self)
        self.settings_sidebar_signal = SettingsSidebarSignal(self)
        self.signals_list = (
            self.about_signal, self.add_input_signal, self.apply_settings_all_signal,
            self.auto_crop_signal, self.output_chooser_signal, self.page_switch_signal,
            self.parallel_tasks_signal, self.preferences_signal, self.settings_sidebar_signal,
            self.completed_page_handlers, self.active_page_handlers, self.inputs_page_handlers,
            self.settings_sidebar_handlers
        )
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

    def get_output_chooser_dir(self):
        return self.output_file_chooser_button.get_filename()

    def is_chunk_processing_selected(self):
        parallel_tasks_enabled = self.parallel_tasks_radiobutton.get_active()
        parallel_tasks_chunks_enabled = self.parallel_tasks_chunks_radiobutton.get_active()
        return parallel_tasks_enabled and parallel_tasks_chunks_enabled

    def is_file_inputs_enabled(self):
        return self.add_combobox.get_active() == 0

    def is_folder_inputs_enabled(self):
        return self.add_combobox.get_active() == 1

    def set_processing_inputs_state(self, enabled, first_input_file_path):
        """Toggles the inputs page to show importing new inputs."""
        if enabled:
            self.inputs_page_handlers.set_processing_inputs_state(first_input_file_path)
            self.add_button.set_sensitive(not enabled)
            self.add_combobox.set_sensitive(not enabled)
            self.input_settings_stack.set_sensitive(not enabled)
            self.output_file_chooser_button.set_sensitive(not enabled)
            self.app_preferences_menubutton.set_sensitive(not enabled)
        else:
            self.inputs_page_handlers.setup_inputs_settings_widgets()
            self.inputs_page_handlers.setup_page_options()
            self.add_button.set_sensitive(not enabled)
            self.add_combobox.set_sensitive(not enabled)
            self.output_file_chooser_button.set_sensitive(not enabled)
            self.app_preferences_menubutton.set_sensitive(not enabled)
            self.inputs_page_handlers.set_inputs_state()

    def set_inputs_page_state(self):
        """Sets up main window widgets when the inputs page is showing."""
        self.app_preferences_stack.set_visible_child(self.app_preferences_inputs_page_box)
        self.output_file_chooser_button.set_sensitive(True)
        self.add_button.set_sensitive(True)
        self.add_combobox.set_sensitive(True)
        self.inputs_page_handlers.setup_inputs_settings_widgets()

    def set_active_page_state(self):
        """Sets up the main window widgets when the active page is showing."""
        self.app_preferences_stack.set_visible_child(self.app_preferences_active_page_box)
        self.input_settings_stack.set_sensitive(False)
        self.output_file_chooser_button.set_sensitive(False)
        self.add_button.set_sensitive(False)
        self.add_combobox.set_sensitive(False)

    def set_completed_page_state(self):
        """Sets up the main window widgets when the completed page is showing."""
        self.app_preferences_stack.set_visible_child(self.completed_page_handlers.clear_all_completed_button)
        self.input_settings_stack.set_sensitive(False)
        self.output_file_chooser_button.set_sensitive(False)
        self.add_button.set_sensitive(False)
        self.add_combobox.set_sensitive(False)

    def set_input_selected_state(self, enabled):
        """Toggles the settings sidebar when an input is selected."""
        if enabled:
            self.input_settings_stack.set_sensitive(True)
        else:
            self.input_settings_stack.set_sensitive(False)
            self.input_settings_revealer.set_reveal_child(False)
            self.input_settings_stack.set_visible_child(self.show_input_settings_button)

    def set_parallel_tasks_state(self, enabled):
        """Toggles the parallel task type widgets."""
        self.parallel_tasks_type_buttonbox.set_sensitive(enabled)

    def update_ffmpeg_template(self):
        """Configures the ffmpeg template settings object to match the selected inputs row."""
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            self.ffmpeg_template = inputs_row.ffmpeg.get_copy()
        else:
            self.ffmpeg_template = Settings()

    def switch_to_active_page(self):
        self.pages_stack.set_visible_child(self.active_page_scroller)

    def show_about_dialog(self):
        self.app_preferences_popover.popdown()
        self.about_dialog.run()
        self.about_dialog.hide()

    def show_preferences_dialog(self):
        self.app_preferences_popover.popdown()
        self.preferences_dialog.run()
        self.preferences_dialog.hide()

    def show_settings_sidebar(self, enabled):
        if enabled:
            self.input_settings_stack.set_visible_child(self.hide_input_settings_button)
        else:
            self.input_settings_stack.set_visible_child(self.show_input_settings_button)
        self.input_settings_revealer.set_reveal_child(enabled)

    def popdown_app_preferences_popover(self):
        self.app_preferences_popover.popdown()
