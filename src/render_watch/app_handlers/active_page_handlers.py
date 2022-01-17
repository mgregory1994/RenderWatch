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


from render_watch.signals.active_page.add_task_signal import AddTaskSignal
from render_watch.signals.active_page.preview_encode_signal import PreviewEncodeSignal
from render_watch.signals.active_page.pause_all_tasks_signal import PauseAllTasksSignal
from render_watch.signals.active_page.task_removed_signal import TaskRemovedSignal
from render_watch.signals.active_page.resume_all_tasks_signal import ResumeAllTasksSignal
from render_watch.signals.active_page.stop_all_tasks_signal import StopAllTasksSignal
from render_watch.startup import Gtk


class ActivePageHandlers:
    """
    Handles all widget changes on the active page.
    """

    def __init__(self, gtk_builder, completed_page_handlers, main_window_handlers, application_preferences):
        self.application_preferences = application_preferences
        self.main_window_handlers = None
        self.completed_page_handlers = None

        self._setup_signals(main_window_handlers, completed_page_handlers, application_preferences)
        self._setup_widgets(gtk_builder)

    def _setup_signals(self, main_window_handlers, completed_page_handlers, application_preferences):
        self.add_row_signal = AddTaskSignal(self)
        self.live_thumbnails_signal = PreviewEncodeSignal(self, application_preferences)
        self.pause_all_signal = PauseAllTasksSignal(self, main_window_handlers)
        self.remove_row_signal = TaskRemovedSignal(self, completed_page_handlers, application_preferences)
        self.resume_all_signal = ResumeAllTasksSignal(self, main_window_handlers)
        self.stop_all_signal = StopAllTasksSignal(self, main_window_handlers)
        self.signals_list = (
            self.add_row_signal, self.live_thumbnails_signal, self.pause_all_signal,
            self.remove_row_signal, self.resume_all_signal, self.stop_all_signal
        )

    def _setup_widgets(self, gtk_builder):
        self.active_list = gtk_builder.get_object('active_list')
        self.stop_all_tasks_button = gtk_builder.get_object('stop_all_tasks_button')
        self.pause_all_tasks_button = gtk_builder.get_object('pause_all_tasks_button')
        self.resume_all_tasks_button = gtk_builder.get_object('resume_all_tasks_button')
        self.preview_encode_switch = gtk_builder.get_object('preview_encode_switch')

        self.active_list.set_header_func(self._active_list_update_header_func, None)

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    # Unused parameters needed for this function.
    @staticmethod
    def _active_list_update_header_func(active_page_listbox_row, previous_active_page_listbox_row, data=None):
        if previous_active_page_listbox_row is None:
            active_page_listbox_row.set_header(None)
        else:
            active_page_listbox_row_header = active_page_listbox_row.get_header()

            if active_page_listbox_row_header is None:
                active_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                active_page_listbox_row_header.show()

                active_page_listbox_row.set_header(active_page_listbox_row_header)

    def get_rows(self):
        return self.active_list.get_children()

    def is_live_thumbnails_enabled(self):
        return self.preview_encode_switch.get_active()

    def add_row(self, active_row):
        self.active_list.add(active_row)
        self.active_list.show_all()
        active_row.hide_chunks_menubutton()

    def remove_row(self, active_row):
        self.active_list.remove(active_row)

    def set_page_options_state(self, is_state_enabled):
        """
        Allows access to this page's options in the options menu.

        :param is_state_enabled: Toggles the state of this page's options in the preferences menu.
        """
        self.pause_all_tasks_button.set_sensitive(is_state_enabled)
        self.resume_all_tasks_button.set_sensitive(is_state_enabled)
        self.stop_all_tasks_button.set_sensitive(is_state_enabled)

    def signal_remove_row(self):
        self.remove_row_signal.on_active_list_remove(self.active_list, None)
