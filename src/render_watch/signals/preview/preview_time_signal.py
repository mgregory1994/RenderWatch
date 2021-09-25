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


import threading

from render_watch.app_formatting import format_converter


class PreviewTimeSignal:
    """Handles the signal emitted when the Current Preview Time is changed on the preview page."""

    def __init__(self, preview_page_handlers):
        self.preview_page_handlers = preview_page_handlers

    def on_preview_time_scale_value_changed(self, preview_time_scale):
        """Sets up and shows the new current preview time.

        :param preview_time_scale:
            Scale that emitted the signal.
        """
        ffmpeg = self.preview_page_handlers.ffmpeg
        input_duration_in_seconds = ffmpeg.input_file_info['duration']
        current_time_in_seconds = round(preview_time_scale.get_value(), 1)
        end_time_difference = input_duration_in_seconds - current_time_in_seconds
        current_timecode = format_converter.get_timecode_from_seconds(current_time_in_seconds)
        duration_timecode = format_converter.get_timecode_from_seconds(input_duration_in_seconds)
        self.preview_page_handlers.set_time_label_text(current_timecode + ' / ' + duration_timecode)
        self.preview_page_handlers.set_preview_opacity(0.5)
        self.preview_page_handlers.update_duration_radiobuttons(end_time_difference)

    def on_preview_scale_released(self, event, data):  # Unused parameters needed for this signal
        """Generates a new preview at the new current time.

        :param event:
            Unused parameter.
        :param data:
            Unused parameter.
        """
        self.preview_page_handlers.set_preview_opacity(0.5)
        time = self.preview_page_handlers.get_current_time_value()
        self.preview_page_handlers.queue_add_time(time)
        threading.Thread(target=self.preview_page_handlers.process_preview, args=()).start()
