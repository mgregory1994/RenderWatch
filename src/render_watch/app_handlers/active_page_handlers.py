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


from render_watch.signals.active_page.add_row_signal import AddRowSignal
from render_watch.signals.active_page.live_thumbnails_signal import LiveThumbnailsSignal
from render_watch.signals.active_page.pause_all_signal import PauseAllSignal
from render_watch.signals.active_page.remove_row_signal import RemoveRowSignal
from render_watch.signals.active_page.resume_all_signal import ResumeAllSignal
from render_watch.signals.active_page.stop_all_signal import StopAllSignal
from render_watch.startup import Gtk


class ActivePageHandlers:
    """Handles all widget changes on the active page."""

    def __init__(self, gtk_builder, completed_page_handlers, main_window_handlers, preferences):
        self.preferences = preferences
        self.main_window_handlers = None
        self.completed_page_handlers = None
        self.add_row_signal = AddRowSignal(self)
        self.live_thumbnails_signal = LiveThumbnailsSignal(self)
        self.pause_all_signal = PauseAllSignal(self, main_window_handlers)
        self.remove_row_signal = RemoveRowSignal(self, completed_page_handlers, preferences)
        self.resume_all_signal = ResumeAllSignal(self, main_window_handlers)
        self.stop_all_signal = StopAllSignal(self, main_window_handlers, preferences)
        self.signals_list = (
            self.add_row_signal, self.live_thumbnails_signal, self.pause_all_signal,
            self.remove_row_signal, self.resume_all_signal, self.stop_all_signal
        )
        self.active_page_listbox = gtk_builder.get_object('active_list')
        self.stop_all_processing_button = gtk_builder.get_object('stop_all_proc_button')
        self.pause_all_processing_button = gtk_builder.get_object('pause_all_proc_button')
        self.resume_all_processing_button = gtk_builder.get_object('resume_all_proc_button')
        self.live_thumbnails_switch = gtk_builder.get_object('live_thumbnails_switch')
        self.active_page_listbox.set_header_func(self._active_list_update_header_func, None)

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

    # Unused parameters needed for this function.
    @staticmethod
    def _active_list_update_header_func(active_page_listbox_row, previous_active_page_listbox_row, data):
        # Adds a separator between Gtk.Listbox rows.
        if previous_active_page_listbox_row is None:
            active_page_listbox_row.set_header(None)
        else:
            active_page_listbox_row_header = active_page_listbox_row.get_header()
            if active_page_listbox_row_header is None:
                active_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                active_page_listbox_row_header.show()
                active_page_listbox_row.set_header(active_page_listbox_row_header)

    def get_rows(self):
        return self.active_page_listbox.get_children()

    def is_live_thumbnails_enabled(self):
        return self.live_thumbnails_switch.get_active()

    def add_row(self, active_row):
        self.active_page_listbox.add(active_row)
        self.active_page_listbox.show_all()

    def remove_row(self, active_row):
        self.active_page_listbox.remove(active_row)

    def set_page_options_state(self, enabled):
        """Allows access to this page's options in the preferences menu.

        :param enabled:
            Toggles the state of this page's options in the preferences menu.
        """
        self.pause_all_processing_button.set_sensitive(enabled)
        self.resume_all_processing_button.set_sensitive(enabled)
        self.stop_all_processing_button.set_sensitive(enabled)

    def signal_remove_row(self):
        self.remove_row_signal.on_active_list_remove(self.active_page_listbox, None)
