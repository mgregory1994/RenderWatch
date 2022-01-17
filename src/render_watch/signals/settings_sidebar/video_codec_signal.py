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
    """
    Handles the signal emitted when the Video Codec option is changed.
    """

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_video_codec_combobox_changed(self, video_codec_combobox):
        """
        Sets up the settings sidebar and applies the new Video Codec option.

        :param video_codec_combobox: Combobox that emitted the signal.
        """
        if not self._is_video_combobox_state_valid(video_codec_combobox):
            return

        video_settings = self.settings_sidebar_handlers.get_changed_video_codec_settings()

        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        self._set_copy_video_codec_state(video_codec_combobox)

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.video_settings = video_settings

            row.setup_labels()

        self.settings_sidebar_handlers.set_benchmark_state()
        self.inputs_page_handlers.update_preview_page()

    def _is_video_combobox_state_valid(self, video_codec_combobox):
        return video_codec_combobox.get_active_text() \
               and not self.settings_sidebar_handlers.is_video_codec_transitioning

    def _set_copy_video_codec_state(self, video_codec_combobox):
        is_copy_video_codec_enabled = video_codec_combobox.get_active() == 0
        if is_copy_video_codec_enabled:
            self.settings_sidebar_handlers.signal_framerate_auto_radiobutton()
            self.settings_sidebar_handlers.subtitles_handlers.remove_burn_in_for_all_streams()
        self.settings_sidebar_handlers.set_framerate_locked_state(is_copy_video_codec_enabled)
