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


from render_watch.signals.application_preferences.watch_folder_wait_for_tasks_signal import WatchFolderWaitForTasksSignal
from render_watch.startup import Gtk


class WaitForTasksRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the overwrite outputs option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences):
        self.watch_folder_wait_for_tasks_signal = WatchFolderWaitForTasksSignal(application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.wait_for_tasks_row_box = gtk_builder.get_object('wait_for_tasks_row_box')
        self.wait_for_tasks_switch = gtk_builder.get_object('wait_for_tasks_switch')
        self.wait_for_tasks_switch.set_active(application_preferences.is_watch_folder_wait_for_tasks_enabled)

        self.add(self.wait_for_tasks_row_box)

        self.wait_for_tasks_switch.connect('state-set',
                                           self.watch_folder_wait_for_tasks_signal.on_wait_for_tasks_switch_state_set)
