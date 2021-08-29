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


class OpusBitrateSignal:
    """Handles the signal emitted when the Opus Bitrate option is changed."""

    def __init__(self, opus_handlers, inputs_page_handlers):
        self.opus_handlers = opus_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_opus_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        """Applies the Bitrate value option.

        :param bitrate_spinbutton:
            Spinbutton that emitted the signal.
        """
        if self.opus_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings.bitrate = bitrate_spinbutton.get_value_as_int()
            row.setup_labels()
