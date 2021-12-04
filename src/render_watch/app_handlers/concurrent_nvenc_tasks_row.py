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


from render_watch.helpers.ui_helper import UIHelper
from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.signals.application_preferences.concurrent_tasks_signal import ConcurrentTasksSignal
from render_watch.startup import Gtk


class ConcurrentNvencTasksRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the nvenc concurrent tasks option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences_handlers, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences_handlers, application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences_handlers, application_preferences):
        self.concurrent_tasks_signal = ConcurrentTasksSignal(application_preferences_handlers, application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        concurrent_nvenc_tasks_row_box = gtk_builder.get_object('concurrent_nvenc_tasks_row_box')
        self.concurrent_nvenc_tasks_combobox = gtk_builder.get_object('concurrent_nvenc_tasks_combobox')
        UIHelper.setup_combobox(self.concurrent_nvenc_tasks_combobox, ApplicationPreferences.CONCURRENT_NVENC_VALUES)
        concurrent_nvenc_value = application_preferences.get_concurrent_nvenc_value(string=True)
        self.concurrent_nvenc_tasks_combobox.set_active(ApplicationPreferences.CONCURRENT_NVENC_VALUES.index(
            concurrent_nvenc_value))
        concurrent_nvenc_tasks_warning_stack = gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_stack')
        concurrent_nvenc_tasks_warning_blank_label = gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_blank_label')
        concurrent_nvenc_tasks_warning_icon = gtk_builder.get_object(
            'concurrent_nvenc_tasks_warning_icon')

        if concurrent_nvenc_value != 'auto':
            concurrent_nvenc_tasks_warning_stack.set_visible_child(concurrent_nvenc_tasks_warning_icon)
        else:
            concurrent_nvenc_tasks_warning_stack.set_visible_child(concurrent_nvenc_tasks_warning_blank_label)

        self.add(concurrent_nvenc_tasks_row_box)

        self.concurrent_nvenc_tasks_combobox.connect('changed',
                                                     self.concurrent_tasks_signal.on_concurrent_nvenc_tasks_combobox_changed)
