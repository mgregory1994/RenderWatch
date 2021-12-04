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


from render_watch.signals.application_preferences.concurrent_tasks_signal import ConcurrentTasksSignal
from render_watch.startup import Gtk


class SimultaneousNvencTasksRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the run nvenc alongside other tasks option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences):
        self.concurrent_tasks_signal = ConcurrentTasksSignal(self, application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.simultaneous_nvenc_tasks_row_box = gtk_builder.get_object('simultaneous_nvenc_tasks_row_box')
        self.simultaneous_nvenc_tasks_switch = gtk_builder.get_object('simultaneous_nvenc_tasks_switch')
        self.simultaneous_nvenc_tasks_switch.set_active(application_preferences.is_concurrent_nvenc_enabled)

        self.add(self.simultaneous_nvenc_tasks_row_box)

        self.simultaneous_nvenc_tasks_switch.connect('state-set',
                                                     self.concurrent_tasks_signal.on_simultaneous_concurrent_nvenc_tasks_switch_state_set)
