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


class X264PartitionsSignal:
    def __init__(self, x264_handlers, inputs_page_handlers):
        self.x264_handlers = x264_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_x264_partitions_auto_radiobutton_toggled(self, partitions_auto_radiobutton):
        if not partitions_auto_radiobutton.get_active():
            return

        if self.x264_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = None

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_x264_partitions_custom_radiobutton_toggled(self, partitions_custom_radiobutton):
        self.x264_handlers.set_partitions_custom_state(partitions_custom_radiobutton.get_active())

        if not partitions_custom_radiobutton.get_active():
            return

        if self.x264_handlers.is_widgets_setting_up:
            return

        partitions_setting = self.x264_handlers.get_partitions_settings()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = partitions_setting

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    # Unused parameters needed for this signal
    def on_x264_partitions_type_checkbox_toggled(self, partitions_type_checkbox):
        if self.x264_handlers.is_widgets_setting_up:
            return

        partitions_setting = self.x264_handlers.get_partitions_settings()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings.partitions = partitions_setting

            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
