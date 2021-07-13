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


class VideoCodecSignal:
    """Handles the signal emitted when the Video Codec option is changed in the settings sidebar."""

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_video_codec_combobox_changed(self, video_codec_combobox):
        """Sets up the settings sidebar and applies the new Video Codec option.

        :param video_codec_combobox:
            Combobox that emitted the signal.
        """
        if video_codec_combobox.get_active_text() is None \
                or self.settings_sidebar_handlers.is_video_codec_transitioning:
            return
        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        video_settings = self.settings_sidebar_handlers.update_video_settings()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings = video_settings
            row.setup_labels()

        self.settings_sidebar_handlers.set_benchmark_state()
        self.inputs_page_handlers.update_preview_page()
