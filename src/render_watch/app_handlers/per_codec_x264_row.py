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

from render_watch.startup.application_preferences import ApplicationPreferences
from render_watch.signals.application_preferences.per_codec_parallel_tasks_signal import PerCodecParallelTasksSignal
from render_watch.helpers.ui_helper import UIHelper
from render_watch.startup import Gtk


class PerCodecX264Row(Gtk.ListBoxRow):
    """
    Creates a Gtk.ListboxRow for the per codec x264 option in the Application Preferences Dialog.
    """

    def __init__(self, application_preferences_handlers, application_preferences):
        Gtk.ListBoxRow.__init__(self)
        self._setup_signals(application_preferences_handlers, application_preferences)
        self._setup_widgets(application_preferences)

    def _setup_signals(self, application_preferences_handlers, application_preferences):
        self.per_codec_parallel_tasks_signal = PerCodecParallelTasksSignal(application_preferences_handlers,
                                                                           application_preferences)

    def _setup_widgets(self, application_preferences):
        this_modules_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_modules_file_path, '../render_watch_data/rows_ui.glade')

        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(rows_ui_file_path)

        self.per_codec_listbox_row_box = gtk_builder.get_object('per_codec_listbox_row_box')
        self.per_codec_label = gtk_builder.get_object('per_codec_label')
        self.per_codec_label.set_text('x264')
        self.per_codec_subtext_label = gtk_builder.get_object('per_codec_subtext_label')
        self.per_codec_subtext_label.set_text('Number of tasks to run for the x264 codec')
        self.per_codec_combobox = gtk_builder.get_object('per_codec_combobox')
        UIHelper.setup_combobox(self.per_codec_combobox, ApplicationPreferences.PER_CODEC_TASKS_VALUES)
        self.per_codec_combobox.set_active(ApplicationPreferences.PER_CODEC_TASKS_VALUES.index(
            str(application_preferences.per_codec_parallel_tasks['x264'])))

        self.add(self.per_codec_listbox_row_box)

        self.per_codec_combobox.connect('changed',
                                        self.per_codec_parallel_tasks_signal.on_per_codec_x264_combobox_changed)
