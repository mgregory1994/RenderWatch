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


from render_watch.signals.application_preferences.dark_mode_signal import DarkModeSignal
from render_watch.startup import Gtk


class DarkModeRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the dark mode option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, gtk_settings, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(gtk_settings, application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, gtk_settings, application_preferences):
        self.dark_mode_signal = DarkModeSignal(gtk_settings, application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.dark_mode_row_box = gtk_builder.get_object('dark_mode_row_box')
        self.dark_mode_switch = gtk_builder.get_object('dark_mode_switch')
        self.dark_mode_switch.set_active(application_preferences.is_dark_mode_enabled)

        self.add(self.dark_mode_row_box)

        self.dark_mode_switch.connect('state-set', self.dark_mode_signal.on_dark_mode_switch_state_set)
