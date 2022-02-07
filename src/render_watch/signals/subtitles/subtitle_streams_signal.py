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


class AddSubtitleStreamSignal:
    """
    Handles the signal emitted when the user adds a subtitle stream.
    """

    def __init__(self, subtitles_handlers):
        self.subtitles_handlers = subtitles_handlers

    def on_subtitle_streams_list_add_button_clicked(self, subtitle_streams_list_add_button):
        self.subtitles_handlers.add_available_stream()


class RemoveSubtitleStreamSignal:
    """
    Handles the signal emitted when the user removes a subtitle stream.
    """

    def __init__(self, subtitle_stream_row, subtitle_handlers):
        self.subtitle_stream_row = subtitle_stream_row
        self.subtitle_handlers = subtitle_handlers

    def on_remove_subtitle_stream_button_clicked(self, remove_subtitle_stream_button):
        self.subtitle_handlers.remove_stream(self.subtitle_stream_row)


class ChangedSubtitleStreamSignal:
    """
    Handles the signal emitted when the user changed a subtitle stream.
    """

    def __init__(self, subtitle_stream_row, subtitle_handlers):
        self.subtitle_stream_row = subtitle_stream_row
        self.subtitle_handlers = subtitle_handlers

    def on_subtitle_stream_combobox_changed(self, subtitle_stream_combobox):
        if self.subtitle_stream_row.is_widgets_changing:
            return

        self.subtitle_handlers.change_stream(self.subtitle_stream_row)


class ChangeStreamMethodSignal:
    """
    Handles the signale emitted when the user changed a subtitle stream's method.
    """

    def __init__(self, subtitle_stream_row, subtitle_handlers):
        self.subtitle_stream_row = subtitle_stream_row
        self.subtitle_handlers = subtitle_handlers

    def on_subtitle_stream_method_combobox_changed(self, subtitle_stream_method_combobox):
        if self.subtitle_stream_row.is_widgets_changing:
            return
        if self.subtitle_stream_row.is_restricted_mode_enabled:
            self.subtitle_stream_row.set_burn_in_method()
            return

        if self.subtitle_stream_row.is_burn_in_method_enabled():
            self.subtitle_handlers.set_burn_in_for_stream(self.subtitle_stream_row)
        else:
            self.subtitle_handlers.remove_burn_in_method()
