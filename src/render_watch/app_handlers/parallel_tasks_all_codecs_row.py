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


from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.signals.application_preferences.concurrent_tasks_signal import ConcurrentTasksSignal
from render_watch.helpers.ui_helper import UIHelper
from render_watch.startup import Gtk


class ParallelTasksAllCodecsRow(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the concurrent tasks option in the application preferences dialog.
    """

    def __init__(self, gtk_builder, application_preferences_handlers, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences_handlers, application_preferences)
        self._setup_widgets(gtk_builder, application_preferences)

    def _setup_signals(self, application_preferences_handlers, application_preferences):
        self.concurrent_tasks_signal = ConcurrentTasksSignal(application_preferences_handlers, application_preferences)

    def _setup_widgets(self, gtk_builder, application_preferences):
        parallel_tasks_all_codecs_row_box = gtk_builder.get_object('parallel_tasks_all_codecs_row_box')
        self.concurrent_tasks_combobox = gtk_builder.get_object('concurrent_tasks_combobox')
        parallel_tasks_value = application_preferences.parallel_tasks
        UIHelper.setup_combobox(self.concurrent_tasks_combobox, ApplicationPreferences.PARALLEL_TASKS_VALUES)
        self.concurrent_tasks_combobox.set_active(ApplicationPreferences.PARALLEL_TASKS_VALUES.index(
            str(parallel_tasks_value)))
        concurrent_tasks_message_stack = gtk_builder.get_object('concurrent_tasks_message_stack')
        concurrent_tasks_message_8 = gtk_builder.get_object('concurrent_tasks_message_8')
        concurrent_tasks_message_12 = gtk_builder.get_object('concurrent_tasks_message_12')
        concurrent_tasks_message_24 = gtk_builder.get_object('concurrent_tasks_message_24')
        concurrent_tasks_message_32 = gtk_builder.get_object('concurrent_tasks_message_32')
        concurrent_tasks_message_max = gtk_builder.get_object('concurrent_tasks_message_max')

        if parallel_tasks_value == 2:
            concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_8)
        elif parallel_tasks_value == 3:
            concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_12)
        elif parallel_tasks_value == 4:
            concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_24)
        elif parallel_tasks_value == 6:
            concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_32)
        else:
            concurrent_tasks_message_stack.set_visible_child(concurrent_tasks_message_max)

        self.add(parallel_tasks_all_codecs_row_box)

        self.concurrent_tasks_combobox.connect('changed',
                                               self.concurrent_tasks_signal.on_concurrent_tasks_combobox_changed)
