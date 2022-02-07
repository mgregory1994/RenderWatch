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


from render_watch.signals.application_preferences.move_watch_folder_tasks_to_done_signal import MoveWatchFolderTasksToDoneSignal
from render_watch.startup import Gtk


class MoveWatchFolderTasksToDoneRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the move watch folder tasks to done option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences):
        self.move_watch_folder_tasks_to_done_signal = MoveWatchFolderTasksToDoneSignal(application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.move_watch_folder_tasks_to_done_row_box = gtk_builder.get_object('move_watch_folder_tasks_to_done_row_box')
        self.move_watch_folder_tasks_to_done_switch = gtk_builder.get_object('move_watch_folder_tasks_to_done_switch')
        self.move_watch_folder_tasks_to_done_switch.set_active(
            application_preferences.is_watch_folder_move_tasks_to_done_enabled)

        self.add(self.move_watch_folder_tasks_to_done_row_box)

        self.move_watch_folder_tasks_to_done_switch.connect('state-set',
                                                            self.move_watch_folder_tasks_to_done_signal.on_move_watch_folder_tasks_to_done_switch_state_set)
