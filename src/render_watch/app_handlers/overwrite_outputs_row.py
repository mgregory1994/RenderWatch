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


from render_watch.signals.application_preferences.overwrite_outputs_signal import OverwriteOutputsSignal
from render_watch.startup import Gtk


class OverwriteOutputsRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the overwrite outputs option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences):
        self.overwrite_outputs_signal = OverwriteOutputsSignal(application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        self.overwrite_outputs_row_box = gtk_builder.get_object('overwrite_outputs_row_box')
        self.overwrite_outputs_switch = gtk_builder.get_object('overwrite_outputs_switch')
        self.overwrite_outputs_switch.set_active(application_preferences.is_overwrite_outputs_enabled)

        self.add(self.overwrite_outputs_row_box)

        self.overwrite_outputs_switch.connect('state-set',
                                              self.overwrite_outputs_signal.on_overwrite_outputs_switch_state_set)
