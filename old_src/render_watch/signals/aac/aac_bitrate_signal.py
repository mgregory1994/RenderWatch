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


class AacBitrateSignal:
    """
    Handles the signals emitted from the AAC bitrate widget.
    """

    def __init__(self, aac_handlers, inputs_page_handlers):
        self.aac_handlers = aac_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_aac_bitrate_spinbutton_value_changed(self, aac_bitrate_spinbutton):
        """
        Updates all selected rows on the inputs page with the new audio bitrate.

        :param aac_bitrate_spinbutton: Spinbutton that emitted the signal.
        """
        if self.aac_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings.bitrate = aac_bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

        if self.inputs_page_handlers.is_preview_page_failed_state():
            self.inputs_page_handlers.update_preview_page()