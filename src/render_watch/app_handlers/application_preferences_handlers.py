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


import os


from render_watch.app_handlers.temporary_files_row import TemporaryFilesRow
from render_watch.app_handlers.clear_temporary_files_row import ClearTemporaryFilesRow
from render_watch.app_handlers.dark_mode_row import DarkModeRow
from render_watch.app_handlers.parallel_tasks_all_codecs_row import ParallelTasksAllCodecsRow
from render_watch.app_handlers.per_codec_x264_row import PerCodecX264Row
from render_watch.app_handlers.per_codec_x265_row import PerCodecX265Row
from render_watch.app_handlers.per_codec_vp9_row import PerCodecVp9Row
from render_watch.app_handlers.concurrent_nvenc_tasks_row import ConcurrentNvencTasksRow
from render_watch.app_handlers.simultaneous_nvenc_tasks_row import SimultaneousNvencTasksRow
from render_watch.app_handlers.overwrite_outputs_row import OverwriteOutputsRow
from render_watch.app_handlers.run_watch_folders_concurrently_row import RunWatchFoldersConcurrentlyRow
from render_watch.app_handlers.wait_for_tasks_row import WaitForTasksRow
from render_watch.app_handlers.move_watch_folder_tasks_to_done_row import MoveWatchFolderTasksToDoneRow
from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.signals.application_preferences.per_codec_parallel_tasks_signal import PerCodecParallelTasksSignal
from render_watch.startup import Gtk


class ApplicationPreferencesHandlers:
    """
    Handles all widget changes for the preferences dialog.
    """

    def __init__(self, gtk_builder, gtk_settings, main_window_handlers, application_preferences):
        self.original_temp_directory = application_preferences.temp_directory
        self.original_concurrent_tasks_index = ApplicationPreferences.PARALLEL_TASKS_VALUES.index(
            str(application_preferences.parallel_tasks))
        self.original_per_codec_enabled = application_preferences.is_per_codec_parallel_tasks_enabled
        self.original_per_codec_x264_value = application_preferences.per_codec_parallel_tasks['x264']
        self.original_per_codec_x265_value = application_preferences.per_codec_parallel_tasks['x265']
        self.original_per_codec_vp9_value = application_preferences.per_codec_parallel_tasks['vp9']

        self._setup_signals(application_preferences)
        self._setup_widgets(gtk_builder, gtk_settings, main_window_handlers, application_preferences)

    def _setup_signals(self, application_preferences):
        self.per_codec_parallel_tasks_signal = PerCodecParallelTasksSignal(self, application_preferences)

        self.signals_list = [
            self.per_codec_parallel_tasks_signal
        ]

    def _setup_widgets(self, gtk_builder, gtk_settings, main_window_handlers, application_preferences):
        this_modules_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_modules_file_path, '../render_watch_data/rows_ui.glade')

        options_rows_gtk_builder = Gtk.Builder()
        options_rows_gtk_builder.add_from_file(rows_ui_file_path)

        self.temporary_files_list = gtk_builder.get_object('temporary_files_list')
        self.temporary_files_restart_stack = options_rows_gtk_builder.get_object('temporary_files_restart_stack')
        self.temporary_files_restart_blank_label = options_rows_gtk_builder.get_object(
            'temporary_files_restart_blank_label')
        self.temporary_files_restart_icon = options_rows_gtk_builder.get_object('temporary_files_restart_icon')
        self.misc_preferences_list = gtk_builder.get_object('misc_preferences_list')
        self.parallel_tasks_stack = gtk_builder.get_object('parallel_tasks_stack')
        self.concurrent_tasks_frame = gtk_builder.get_object('concurrent_tasks_frame')
        self.concurrent_tasks_list = gtk_builder.get_object('concurrent_tasks_list')
        self.concurrent_tasks_combobox = options_rows_gtk_builder.get_object('concurrent_tasks_combobox')
        self.concurrent_tasks_restart_stack = options_rows_gtk_builder.get_object('concurrent_tasks_restart_stack')
        self.concurrent_tasks_restart_blank_label = options_rows_gtk_builder.get_object(
            'concurrent_tasks_restart_blank_label')
        self.concurrent_tasks_restart_icon = options_rows_gtk_builder.get_object('concurrent_tasks_restart_icon')
        self.concurrent_tasks_message_stack = options_rows_gtk_builder.get_object('concurrent_tasks_message_stack')
        self.concurrent_tasks_message_8 = options_rows_gtk_builder.get_object('concurrent_tasks_message_8')
        self.concurrent_tasks_message_12 = options_rows_gtk_builder.get_object('concurrent_tasks_message_12')
        self.concurrent_tasks_message_24 = options_rows_gtk_builder.get_object('concurrent_tasks_message_24')
        self.concurrent_tasks_message_32 = options_rows_gtk_builder.get_object('concurrent_tasks_message_32')
        self.concurrent_tasks_message_max = options_rows_gtk_builder.get_object('concurrent_tasks_message_max')
        self.per_codec_warning_stack = gtk_builder.get_object('per_codec_warning_stack')
        self.per_codec_restart_blank_label = gtk_builder.get_object('per_codec_restart_blank_label')
        self.per_codec_restart_icon = gtk_builder.get_object('per_codec_restart_icon')
        self.per_codec_switch = gtk_builder.get_object('per_codec_switch')
        self.per_codec_list = gtk_builder.get_object('per_codec_list')
        self.per_codec_frame = gtk_builder.get_object('per_codec_frame')
        self.parallel_nvenc_tasks_list = gtk_builder.get_object('parallel_nvenc_tasks_list')
        self.concurrent_nvenc_tasks_warning_stack = options_rows_gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_stack')
        self.concurrent_nvenc_tasks_warning_blank_label = options_rows_gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_blank_label')
        self.concurrent_nvenc_tasks_warning_icon = options_rows_gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_icon')
        self.encoder_outputs_list = gtk_builder.get_object('encoder_outputs_list')
        self.queue_list = gtk_builder.get_object('queue_list')
        self.watch_folder_outputs_list = gtk_builder.get_object('watch_folder_outputs_list')

        self.temporary_files_list.set_header_func(self._options_list_update_header_func, None)
        self.misc_preferences_list.set_header_func(self._options_list_update_header_func, None)
        self.concurrent_tasks_list.set_header_func(self._options_list_update_header_func, None)
        self.per_codec_list.set_header_func(self._options_list_update_header_func, None)
        self.parallel_nvenc_tasks_list.set_header_func(self._options_list_update_header_func, None)
        self.encoder_outputs_list.set_header_func(self._options_list_update_header_func, None)
        self.queue_list.set_header_func(self._options_list_update_header_func, None)
        self.watch_folder_outputs_list.set_header_func(self._options_list_update_header_func, None)

        self._add_general_page_options_rows(options_rows_gtk_builder,
                                            gtk_settings,
                                            main_window_handlers,
                                            application_preferences)
        self._add_encoder_page_options_rows(options_rows_gtk_builder, application_preferences)
        self._add_watch_folder_page_options_rows(options_rows_gtk_builder, application_preferences)

    # Unused parameters needed for this function
    @staticmethod
    def _options_list_update_header_func(inputs_page_listbox_row, previous_inputs_page_listbox_row, data=None):
        if previous_inputs_page_listbox_row is None:
            inputs_page_listbox_row.set_header(None)
        else:
            inputs_page_listbox_row_header = inputs_page_listbox_row.get_header()

            if inputs_page_listbox_row_header is None:
                inputs_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                inputs_page_listbox_row_header.show()
                inputs_page_listbox_row.set_header(inputs_page_listbox_row_header)

    def _add_general_page_options_rows(self, gtk_builder, gtk_settings, main_window_handlers, application_preferences):
        self._add_temporary_files_options_rows(gtk_builder, main_window_handlers, application_preferences)
        self._add_misc_options_rows(gtk_builder, gtk_settings, application_preferences)

    def _add_temporary_files_options_rows(self, gtk_builder, main_window_handlers, application_preferences):
        self.temporary_files_row = TemporaryFilesRow(gtk_builder, main_window_handlers, self, application_preferences)
        self.clear_temporary_files_row = ClearTemporaryFilesRow(gtk_builder,
                                                                main_window_handlers,
                                                                application_preferences)

        self.temporary_files_list.add(self.temporary_files_row)
        self.temporary_files_list.add(self.clear_temporary_files_row)
        self.temporary_files_list.show_all()

    def _add_misc_options_rows(self, gtk_builder, gtk_settings, application_preferences):
        self.dark_mode_row = DarkModeRow(gtk_builder, gtk_settings, application_preferences)

        self.misc_preferences_list.add(self.dark_mode_row)
        self.misc_preferences_list.show_all()

    def _add_encoder_page_options_rows(self, gtk_builder, application_preferences):
        self._add_concurrent_tasks_options_rows(gtk_builder, application_preferences)
        self._add_per_codec_options_rows(application_preferences)
        self._add_concurrent_nvenc_tasks_options_rows(gtk_builder, application_preferences)
        self._add_overwrite_outputs_options_rows(gtk_builder, application_preferences)

    def _add_concurrent_tasks_options_rows(self,
                                           gtk_builder, application_preferences):
        self.parallel_tasks_all_codecs_row = ParallelTasksAllCodecsRow(gtk_builder, self, application_preferences)

        self.concurrent_tasks_list.add(self.parallel_tasks_all_codecs_row)
        self.concurrent_tasks_list.show_all()

    def _add_per_codec_options_rows(self, application_preferences):
        self.per_codec_x264_row = PerCodecX264Row(self, application_preferences)
        self.per_codec_x265_row = PerCodecX265Row(self, application_preferences)
        self.per_codec_vp9_row = PerCodecVp9Row(self, application_preferences)

        self.per_codec_list.add(self.per_codec_x264_row)
        self.per_codec_list.add(self.per_codec_x265_row)
        self.per_codec_list.add(self.per_codec_vp9_row)
        self.per_codec_list.show_all()

    def _add_concurrent_nvenc_tasks_options_rows(self, gtk_builder, application_preferences):
        self.concurrent_nvenc_tasks_row = ConcurrentNvencTasksRow(gtk_builder, self, application_preferences)
        self.simultaneous_nvenc_tasks_row = SimultaneousNvencTasksRow(gtk_builder, application_preferences)

        self.parallel_nvenc_tasks_list.add(self.concurrent_nvenc_tasks_row)
        self.parallel_nvenc_tasks_list.add(self.simultaneous_nvenc_tasks_row)
        self.parallel_nvenc_tasks_list.show_all()

    def _add_overwrite_outputs_options_rows(self, gtk_builder, application_preferences):
        self.overwrite_outputs_row = OverwriteOutputsRow(gtk_builder, application_preferences)

        self.encoder_outputs_list.add(self.overwrite_outputs_row)
        self.encoder_outputs_list.show_all()

    def _add_watch_folder_page_options_rows(self, gtk_builder, application_preferences):
        self._add_queue_options_rows(gtk_builder, application_preferences)
        self._add_watch_folder_outputs_options_rows(gtk_builder, application_preferences)

    def _add_queue_options_rows(self, gtk_builder, application_preferences):
        self.run_watch_folders_concurrently_row = RunWatchFoldersConcurrentlyRow(gtk_builder, application_preferences)
        self.wait_for_tasks_row = WaitForTasksRow(gtk_builder, application_preferences)

        self.queue_list.add(self.run_watch_folders_concurrently_row)
        self.queue_list.add(self.wait_for_tasks_row)
        self.queue_list.show_all()

    def _add_watch_folder_outputs_options_rows(self, gtk_builder, application_preferences):
        self.move_watch_folder_tasks_to_done_row = MoveWatchFolderTasksToDoneRow(gtk_builder, application_preferences)

        self.watch_folder_outputs_list.add(self.move_watch_folder_tasks_to_done_row)
        self.watch_folder_outputs_list.show_all()

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def update_concurrent_tasks_restart_state(self):
        """
        Shows the "restart required" icon when the concurrent tasks settings are changed.
        """
        if self.concurrent_tasks_combobox.get_active() == self.original_concurrent_tasks_index:
            self.concurrent_tasks_restart_stack.set_visible_child(self.concurrent_tasks_restart_blank_label)
        else:
            self.concurrent_tasks_restart_stack.set_visible_child(self.concurrent_tasks_restart_icon)

    def update_concurrent_message(self, concurrent_tasks_value):
        """
        Shows the recommended amount of cores for the selected amount of concurrent tasks.
        """
        if concurrent_tasks_value == '2':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_8)
        elif concurrent_tasks_value == '3':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_12)
        elif concurrent_tasks_value == '4':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_24)
        elif concurrent_tasks_value == '6':
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_32)
        else:
            self.concurrent_tasks_message_stack.set_visible_child(self.concurrent_tasks_message_max)

    def update_per_codec_tasks_restart_state(self):
        """
        Shows the restart required image when the per codec option is toggled.
        """
        if self.per_codec_switch.get_active() == self.original_per_codec_enabled:
            self.per_codec_warning_stack.set_visible_child(self.per_codec_restart_blank_label)
        else:
            self.per_codec_warning_stack.set_visible_child(self.per_codec_restart_icon)

    def update_per_codec_value_restart_state(self):
        """
        Shows the restart required image when the per codec values are changed.
        """
        if self._has_per_codec_x264_value_changed() \
                or self._has_per_codec_x265_value_changed() \
                or self._has_per_codec_vp9_value_changed():
            self.per_codec_warning_stack.set_visible_child(self.per_codec_restart_icon)
        else:
            self.per_codec_warning_stack.set_visible_child(self.per_codec_restart_blank_label)

    def _has_per_codec_x264_value_changed(self):
        per_codec_x264_index = self.per_codec_x264_row.per_codec_combobox.get_active()
        original_per_codec_x264_index = ApplicationPreferences.PER_CODEC_TASKS_VALUES.index(
            str(self.original_per_codec_x264_value))

        return per_codec_x264_index != original_per_codec_x264_index

    def _has_per_codec_x265_value_changed(self):
        per_codec_x265_index = self.per_codec_x265_row.per_codec_combobox.get_active()
        original_per_codec_x265_index = ApplicationPreferences.PER_CODEC_TASKS_VALUES.index(
            str(self.original_per_codec_x265_value))

        return per_codec_x265_index != original_per_codec_x265_index

    def _has_per_codec_vp9_value_changed(self):
        per_codec_vp9_index = self.per_codec_vp9_row.per_codec_combobox.get_active()
        original_per_codec_vp9_index = ApplicationPreferences.PER_CODEC_TASKS_VALUES.index(
            str(self.original_per_codec_vp9_value))

        return per_codec_vp9_index != original_per_codec_vp9_index

    def update_nvenc_concurrent_tasks_restart_state(self, concurrent_nvenc_tasks_text):
        """
        Shows the restart required image when the NVENC concurrent settings are changed.
        """
        if concurrent_nvenc_tasks_text != 'auto':
            self.concurrent_nvenc_tasks_warning_stack.set_visible_child(self.concurrent_nvenc_tasks_warning_icon)
        else:
            self.concurrent_nvenc_tasks_warning_stack.set_visible_child(self.concurrent_nvenc_tasks_warning_blank_label)

    def update_temp_restart_state(self, temp_files_directory):
        """
        Shows the "restart required" icon when the temp directory is changed.
        """
        if temp_files_directory == self.original_temp_directory:
            self.temporary_files_restart_stack.set_visible_child(self.temporary_files_restart_blank_label)
        else:
            self.temporary_files_restart_stack.set_visible_child(self.temporary_files_restart_icon)

    def show_per_codec_options(self):
        self.parallel_tasks_stack.set_visible_child(self.per_codec_frame)

    def show_parallel_tasks_options(self):
        self.parallel_tasks_stack.set_visible_child(self.concurrent_tasks_frame)
