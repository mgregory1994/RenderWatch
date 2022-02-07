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


class AudioCodecSignal:
    """
    Handles the signal emitted when the Audio Codec option is changed.
    """

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_audio_codec_combobox_changed(self, audio_codec_combobox):
        """
        Applies the new audio audio codec to the task's ffmpeg settings.

        :param audio_codec_combobox: Combobox that emitted the signal.
        """
        if audio_codec_combobox.get_active_text() is None \
                or self.settings_sidebar_handlers.is_audio_codec_transitioning:
            return

        audio_settings = self.settings_sidebar_handlers.update_audio_settings()

        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg

            if not (ffmpeg.folder_state or ffmpeg.input_file_info['audio_streams']):
                continue

            ffmpeg.audio_settings = audio_settings

            row.setup_labels()

        if self.inputs_page_handlers.is_preview_page_failed_state():
            self.inputs_page_handlers.update_preview_page()
