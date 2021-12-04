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


class OpusChannelsSignal:
    """
    Handles the signal emitted when the Opus Channels option is changed.
    """

    def __init__(self, opus_handlers, inputs_page_handlers):
        self.opus_handlers = opus_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_opus_channels_combobox_changed(self, opus_channels_combobox):
        """
        Applies the Channels option.

        :param opus_channels_combobox: Combobox that emitted the signal.
        """
        if self.opus_handlers.is_widgets_setting_up:
            return

        channels_index = opus_channels_combobox.get_active()

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings.channels = channels_index

            row.setup_labels()

        if self.inputs_page_handlers.is_preview_page_failed_state():
            self.inputs_page_handlers.update_preview_page()
