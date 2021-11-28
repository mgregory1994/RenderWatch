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
from render_watch.ffmpeg.settings import GeneralSettings
from render_watch.app_handlers.completed_page_handlers import CompletedPageHandlers
from render_watch.app_handlers.active_page_handlers import ActivePageHandlers
from render_watch.app_handlers.inputs_page_handlers import InputsPageHandlers
from render_watch.signals.main_window.about_application_signal import AboutApplicationSignal
from render_watch.signals.main_window.add_inputs_signal import AddInputsSignal
from render_watch.signals.main_window.apply_settings_all_signal import ApplySettingsAllSignal
from render_watch.signals.main_window.auto_crop_signal import AutoCropSignal
from render_watch.signals.main_window.output_chooser_signal import OutputChooserSignal
from render_watch.signals.main_window.page_switch_signal import PageSwitchSignal
from render_watch.signals.main_window.parallel_tasks_signal import ParallelTasksSignal
from render_watch.signals.main_window.parallel_chunks_signal import ParallelChunksSignal
from render_watch.signals.main_window.application_preferences_signal import ApplicationPreferencesSignal
from render_watch.signals.main_window.settings_sidebar_signal import SettingsSidebarSignal
from render_watch.startup import GLib


class MainWindowHandlers:
    """
    Handles all widget changes for the main window.
    """

    def __init__(self, gtk_builder, encoder_queue, application_preferences):
        self.encoder_queue = encoder_queue
        self.application_preferences = application_preferences
        self.completed_page_handlers = CompletedPageHandlers(gtk_builder, self)
        self.active_page_handlers = ActivePageHandlers(gtk_builder,
                                                       self.completed_page_handlers,
                                                       self,
                                                       application_preferences)
        self.inputs_page_handlers = InputsPageHandlers(gtk_builder,
                                                       self.active_page_handlers,
                                                       self,
                                                       application_preferences)
        self.settings_sidebar_handlers = self.inputs_page_handlers.settings_sidebar_handlers
        self.ffmpeg_template = None
        self.inputs_page_paned_position = self.application_preferences.settings_sidebar_position
        self.is_sidebar_pane_resizing = False
        self._setup_signals()
        self._setup_widgets(gtk_builder)

    def _setup_signals(self):
        self.about_application_signal = AboutApplicationSignal(self)
        self.add_input_signal = AddInputsSignal(self,
                                                self.inputs_page_handlers,
                                                self.active_page_handlers,
                                                self.settings_sidebar_handlers,
                                                self.encoder_queue,
                                                self.application_preferences)
        self.apply_settings_all_signal = ApplySettingsAllSignal(self,
                                                                self.inputs_page_handlers,
                                                                self.settings_sidebar_handlers,
                                                                self.application_preferences)
        self.auto_crop_signal = AutoCropSignal(self.inputs_page_handlers, self.application_preferences)
        self.output_chooser_signal = OutputChooserSignal(self, self.inputs_page_handlers, self.application_preferences)
        self.page_switch_signal = PageSwitchSignal(self, self.inputs_page_handlers)
        self.parallel_tasks_signal = ParallelTasksSignal(self, self.encoder_queue, self.application_preferences)
        self.parallel_chunks_signal = ParallelChunksSignal(self.application_preferences)
        self.preferences_signal = ApplicationPreferencesSignal(self)
        self.settings_sidebar_signal = SettingsSidebarSignal(self)
        self.signals_list = (
            self.about_application_signal, self.add_input_signal, self.apply_settings_all_signal,
            self.auto_crop_signal, self.output_chooser_signal, self.page_switch_signal,
            self.parallel_tasks_signal, self.parallel_chunks_signal, self.preferences_signal,
            self.settings_sidebar_signal, self.completed_page_handlers, self.active_page_handlers,
            self.inputs_page_handlers, self.settings_sidebar_handlers
        )

    def _setup_widgets(self, gtk_builder):
        self.page_stack = gtk_builder.get_object('page_stack')
        self.active_page_scroller = gtk_builder.get_object("active_page_scroller")
        self.application_options_popover = gtk_builder.get_object('application_options_popover')
        self.page_options_stack = gtk_builder.get_object("page_options_stack")
        self.inputs_page_options_box = gtk_builder.get_object("inputs_page_options_box")
        self.active_page_options_box = gtk_builder.get_object("active_page_options_box")
        self.application_options_menubutton = gtk_builder.get_object('application_options_menubutton')
        self.about_application_dialog = gtk_builder.get_object("about_application_dialog")
        self.inputs_page_paned = gtk_builder.get_object('inputs_page_paned')
        self.settings_sidebar_box = gtk_builder.get_object('settings_sidebar_box')
        self.settings_sidebar_box.set_visible(False)
        self.toggle_settings_sidebar_button = gtk_builder.get_object("toggle_settings_sidebar_button")
        self.application_preferences_button = gtk_builder.get_object("application_preferences_button")
        self.application_preferences_dialog = gtk_builder.get_object("application_preferences_dialog")
        self.output_directory_chooserbutton = gtk_builder.get_object("output_directory_chooserbutton")
        self.add_inputs_button = gtk_builder.get_object("add_inputs_button")
        self.add_inputs_type_combobox = gtk_builder.get_object('add_inputs_type_combobox')
        self.parallel_tasks_type_options_box = gtk_builder.get_object('parallel_tasks_type_options_box')
        self.toggle_parallel_tasks_radiobutton = gtk_builder.get_object('toggle_parallel_tasks_radiobutton')
        self.parallel_tasks_chunks_radiobutton = gtk_builder.get_object('parallel_tasks_chunks_radiobutton')
        self.main_window = gtk_builder.get_object('main_window')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def get_output_chooser_dir(self):
        return self.output_directory_chooserbutton.get_filename()

    def is_chunk_processing_selected(self):
        parallel_tasks_enabled = self.toggle_parallel_tasks_radiobutton.get_active()
        parallel_tasks_chunks_enabled = self.parallel_tasks_chunks_radiobutton.get_active()
        return parallel_tasks_enabled and parallel_tasks_chunks_enabled

    def is_file_inputs_enabled(self):
        return self.add_inputs_type_combobox.get_active() == 0

    def is_folder_inputs_enabled(self):
        return self.add_inputs_type_combobox.get_active() == 1

    def set_processing_inputs_state(self, is_state_enabled, first_input_file_path):
        """
        Shows/hides the progress of importing inputs.
        """
        if is_state_enabled:
            self.inputs_page_handlers.set_processing_inputs_state(first_input_file_path)
            self.add_inputs_button.set_sensitive(not is_state_enabled)
            self.add_inputs_type_combobox.set_sensitive(not is_state_enabled)
            self.toggle_settings_sidebar_button.set_sensitive(not is_state_enabled)
            self.output_directory_chooserbutton.set_sensitive(not is_state_enabled)
            self.application_options_menubutton.set_sensitive(not is_state_enabled)
        else:
            self.inputs_page_handlers.setup_inputs_settings_widgets()
            self.inputs_page_handlers.setup_page_options()
            self.add_inputs_button.set_sensitive(not is_state_enabled)
            self.add_inputs_type_combobox.set_sensitive(not is_state_enabled)
            self.output_directory_chooserbutton.set_sensitive(not is_state_enabled)
            self.application_options_menubutton.set_sensitive(not is_state_enabled)
            self.inputs_page_handlers.set_inputs_state()

    def _show_processing_inputs_state(self, first_input_file_path):
        self.inputs_page_handlers.set_processing_inputs_state(first_input_file_path)
        self.add_inputs_button.set_sensitive(False)
        self.add_inputs_type_combobox.set_sensitive(False)
        self.toggle_settings_sidebar_button.set_sensitive(False)
        self.output_directory_chooserbutton.set_sensitive(False)
        self.application_options_menubutton.set_sensitive(False)

    def _hide_processing_inputs_state(self):
        self.inputs_page_handlers.setup_inputs_settings_widgets()
        self.inputs_page_handlers.setup_page_options()
        self.add_inputs_button.set_sensitive(True)
        self.add_inputs_type_combobox.set_sensitive(True)
        self.output_directory_chooserbutton.set_sensitive(True)
        self.application_options_menubutton.set_sensitive(True)
        self.inputs_page_handlers.set_inputs_state()

    def set_inputs_page_state(self):
        """
        Sets up the main window widgets for when the inputs page is showing.
        """
        self.page_options_stack.set_visible_child(self.inputs_page_options_box)
        self.output_directory_chooserbutton.set_sensitive(True)
        self.add_inputs_button.set_sensitive(True)
        self.add_inputs_type_combobox.set_sensitive(True)
        self.inputs_page_handlers.setup_inputs_settings_widgets()

    def set_active_page_state(self):
        """
        Sets up the main window widgets for when the active page is showing.
        """
        self.page_options_stack.set_visible_child(self.active_page_options_box)
        self.toggle_settings_sidebar_button.set_sensitive(False)
        self.output_directory_chooserbutton.set_sensitive(False)
        self.add_inputs_button.set_sensitive(False)
        self.add_inputs_type_combobox.set_sensitive(False)

    def set_completed_page_state(self):
        """
        Sets up the main window widgets for when the completed page is showing.
        """
        self.page_options_stack.set_visible_child(self.completed_page_handlers.clear_all_completed_tasks_button)
        self.toggle_settings_sidebar_button.set_sensitive(False)
        self.output_directory_chooserbutton.set_sensitive(False)
        self.add_inputs_button.set_sensitive(False)
        self.add_inputs_type_combobox.set_sensitive(False)

    def set_input_selected_state(self, is_state_enabled):
        """
        Toggles the settings sidebar when an input is selected/deselected.
        """
        if is_state_enabled:
            self.toggle_settings_sidebar_button.set_sensitive(True)
        else:
            self.toggle_settings_sidebar_button.set_sensitive(False)
            self.settings_sidebar_box.set_visible(False)

    def set_parallel_tasks_state(self, is_state_enabled):
        """
        Toggles the parallel task type widgets.
        """
        self.parallel_tasks_type_options_box.set_sensitive(is_state_enabled)

    def update_ffmpeg_template(self):
        """
        Configures the ffmpeg template settings to match the selected task.
        """
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            self.ffmpeg_template = inputs_row.ffmpeg.get_copy()
        else:
            self.ffmpeg_template = Settings()
            self.ffmpeg_template.output_container = GeneralSettings.CONTAINERS_UI_LIST[0]

    def switch_to_active_page(self):
        self.page_stack.set_visible_child(self.active_page_scroller)

    def show_about_dialog(self):
        self.application_options_popover.popdown()
        self.about_application_dialog.run()
        self.about_application_dialog.hide()

    def show_preferences_dialog(self):
        self.application_options_popover.popdown()
        self.application_preferences_dialog.run()
        self.application_preferences_dialog.hide()

    def toggle_settings_sidebar(self, is_closing_settings_sidebar=False):
        if is_closing_settings_sidebar:
            is_toggled_settings_sidebar_visible = False
        else:
            is_toggled_settings_sidebar_visible = not self.settings_sidebar_box.get_visible()

        if is_toggled_settings_sidebar_visible:
            self.inputs_page_paned.set_position(self.inputs_page_paned_position)
        else:
            self.inputs_page_paned.set_position(-1)

        GLib.idle_add(self.settings_sidebar_box.set_visible, is_toggled_settings_sidebar_visible)

    def popdown_app_preferences_popover(self):
        self.application_options_popover.popdown()

    def update_settings_sidebar_paned_position(self):
        self.inputs_page_paned_position = self.main_window.get_size().width - self.inputs_page_paned.get_position()
        self.application_preferences.settings_sidebar_position = self.inputs_page_paned_position

    def update_settings_sidebar_paned_allocation(self):
        if self.is_sidebar_pane_resizing or self.inputs_page_paned_position < 0:
            return

        self.inputs_page_paned.set_position(self.main_window.get_size().width - self.inputs_page_paned_position)
