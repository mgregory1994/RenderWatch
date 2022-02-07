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

from render_watch.helpers.ui_helper import UIHelper
from render_watch.signals.subtitles.subtitle_streams_signal import RemoveSubtitleStreamSignal, \
    ChangedSubtitleStreamSignal, ChangeStreamMethodSignal
from render_watch.startup import Gtk


class StreamRow(Gtk.ListBoxRow):
    """
    Creates a subtitle stream row for the subtitles list in the settings sidebar.
    """

    def __init__(self, subtitle_handlers, inputs_page_handlers, starting_stream=None):
        Gtk.ListBoxRow.__init__(self)
        self.subtitle_handlers = subtitle_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.previously_selected_stream = None
        self._starting_stream = starting_stream
        self.is_widgets_changing = False
        self.is_restricted_mode_enabled = False

        self._setup_signals()
        self._setup_widgets()

    def _setup_signals(self):
        self.changed_subtitle_stream_signal = ChangedSubtitleStreamSignal(self, self.subtitle_handlers)
        self.change_stream_method_signal = ChangeStreamMethodSignal(self, self.subtitle_handlers)
        self.remove_subtitle_stream_signal = RemoveSubtitleStreamSignal(self, self.subtitle_handlers)

    def _setup_widgets(self):
        this_modules_file_path = os.path.dirname(os.path.abspath(__file__))
        rows_ui_file_path = os.path.join(this_modules_file_path, '../render_watch_data/rows_ui.glade')

        gtk_builder = Gtk.Builder()
        gtk_builder.add_from_file(rows_ui_file_path)

        self.subtitle_stream_row_box = gtk_builder.get_object('subtitle_stream_row_box')
        self.subtitle_stream_combobox = gtk_builder.get_object('subtitle_stream_combobox')
        self._build_stream_combobox()
        self.subtitle_stream_method_combobox = gtk_builder.get_object('subtitle_stream_method_combobox')
        self.remove_subtitle_stream_button = gtk_builder.get_object('remove_subtitle_stream_button')

        self.add(self.subtitle_stream_row_box)

        self.subtitle_stream_combobox.connect('changed',
                                              self.changed_subtitle_stream_signal.on_subtitle_stream_combobox_changed)
        self.subtitle_stream_method_combobox.connect('changed',
                                                     self.change_stream_method_signal.on_subtitle_stream_method_combobox_changed)
        self.remove_subtitle_stream_button.connect('clicked',
                                                   self.remove_subtitle_stream_signal.on_remove_subtitle_stream_button_clicked)

    def _build_stream_combobox(self):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        if self._starting_stream:
            available_streams = [self._starting_stream]
        else:
            available_streams = []
        available_streams.extend(list(ffmpeg.subtitles_settings.streams_available.values()))

        UIHelper.setup_combobox(self.subtitle_stream_combobox, available_streams)
        self.previously_selected_stream = self.get_selected_stream()

    def get_selected_stream(self):
        return self.subtitle_stream_combobox.get_active_text()

    def is_burn_in_method_enabled(self):
        return self.subtitle_stream_method_combobox.get_active_text() == 'Burn In'

    def set_burn_in_method(self):
        self.subtitle_stream_method_combobox.set_active(1)

    def update_available_streams(self):
        ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()
        available_streams = [self.get_selected_stream()]
        available_streams.extend(list(ffmpeg.subtitles_settings.streams_available.values()))

        self.is_widgets_changing = True
        UIHelper.rebuild_combobox(self.subtitle_stream_combobox, available_streams)
        self.is_widgets_changing = False

        self.previously_selected_stream = self.get_selected_stream()

    def remove_burn_in_method(self):
        self.is_widgets_changing = True
        self.subtitle_stream_method_combobox.set_active(0)
        self.is_widgets_changing = False
