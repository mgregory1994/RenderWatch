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


class PreviewLocationSignal:
    """
    Handles the signal emitted when the Current Preview Location is changed.
    """

    def __init__(self, preview_page_handlers):
        self.preview_page_handlers = preview_page_handlers

    def on_preview_position_scale_value_changed(self, preview_position_scale):
        """
        Sets up and shows the new current preview location.

        :param preview_position_scale: Scale that emitted the signal.
        """
        end_time_difference = self._get_input_end_time_difference(preview_position_scale)
        current_timecode = self._get_current_location_timecode(preview_position_scale)
        duration_timecode = self._get_input_duration_timecode()
        self.preview_page_handlers.set_time_label_text(current_timecode + ' / ' + duration_timecode)
        self.preview_page_handlers.set_preview_opacity(0.5)
        self.preview_page_handlers.update_duration_radiobuttons(end_time_difference)

    @staticmethod
    def _get_current_location_timecode(preview_position_scale):
        current_time_in_seconds = round(preview_position_scale.get_value(), 1)
        return format_converter.get_timecode_from_seconds(current_time_in_seconds)

    def _get_input_duration_timecode(self):
        ffmpeg = self.preview_page_handlers.ffmpeg
        input_duration_in_seconds = ffmpeg.input_file_info['duration']
        return format_converter.get_timecode_from_seconds(input_duration_in_seconds)

    def _get_input_end_time_difference(self, preview_position_scale):
        ffmpeg = self.preview_page_handlers.ffmpeg
        input_duration_in_seconds = ffmpeg.input_file_info['duration']
        current_time_in_seconds = round(preview_position_scale.get_value(), 1)
        return input_duration_in_seconds - current_time_in_seconds

    # Unused parameters needed for this signal
    def on_preview_position_scale_button_release_event(self, preview_position_scale, event=None, user_data=None):
        """
        Generates a new preview image at the new current time.

        :param preview_position_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self.preview_page_handlers.set_preview_opacity(0.5)

        time = self.preview_page_handlers.get_current_time_value()
        self.preview_page_handlers.queue_add_time(time)

        threading.Thread(target=self.preview_page_handlers.process_preview, args=()).start()

    def on_preview_position_scale_key_release_event(self, preview_position_scale, event=None, user_data=None):
        """
        Generates a new preview image at the new current time.

        :param preview_position_scale: Scale that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self.on_preview_position_scale_button_release_event(preview_position_scale, event, user_data)
