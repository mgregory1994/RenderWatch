"""
Copyright 2021 Michael Gregory

This file is part of Render Watch.

Render Watch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Render Watch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.
"""


from render_watch.app_formatting import format_converter


class TrimEndSignal:
    def __init__(self, trim_page_handlers, inputs_page_handlers):
        self.trim_page_handlers = trim_page_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_trim_end_scale_value_changed(self, trim_end_scale):
        end_time_in_seconds = round(trim_end_scale.get_value(), 1)

        if end_time_in_seconds <= self.trim_page_handlers.get_trim_start_value():
            self.trim_page_handlers.set_trim_start_value(end_time_in_seconds - 1)

        if end_time_in_seconds == 0:
            trim_end_scale.set_value(1)

        end_timecode = format_converter.get_timecode_from_seconds(end_time_in_seconds)

        self.trim_page_handlers.set_trim_end_text(end_timecode, True)

    def on_trim_end_scale_button_release_event(self, event, data):  # Unused parameters needed for this signal
        if self.trim_page_handlers.is_widgets_setting_up:
            return

        self.trim_page_handlers.run_trim_thumbnail_thread(True)
        self.trim_page_handlers.update_trim_settings()

    def on_trim_end_scale_key_release_event(self, event, data):  # Unused parameters needed for this signal
        if self.trim_page_handlers.is_widgets_setting_up:
            return

        self.trim_page_handlers.run_trim_thumbnail_thread(True)
        self.trim_page_handlers.update_trim_settings()
