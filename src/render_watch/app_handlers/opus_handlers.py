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


from render_watch.ffmpeg.opus import Opus
from render_watch.signals.opus.opus_bitrate_signal import OpusBitrateSignal
from render_watch.signals.opus.opus_channels_signal import OpusChannelsSignal


class OpusHandlers:
    """
    Handles all widget changes for the Opus codec.
    """

    def __init__(self, gtk_builder, inputs_page_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.is_widgets_setting_up = False

        self.opus_bitrate_signal = OpusBitrateSignal(self, inputs_page_handlers)
        self.opus_channels_signal = OpusChannelsSignal(self, inputs_page_handlers)
        self.signals_list = (self.opus_bitrate_signal, self.opus_channels_signal)

        self.opus_channels_combobox = gtk_builder.get_object('opus_channels_combobox')
        self.opus_bitrate_spinbutton = gtk_builder.get_object('opus_bitrate_spinbutton')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def get_settings(self, ffmpeg):
        """
        Applies settings from the opus widgets to ffmpeg settings.
        """
        audio_settings = Opus()
        audio_settings.channels = self.opus_channels_combobox.get_active()
        audio_settings.bitrate = self.opus_bitrate_spinbutton.get_value_as_int()

        ffmpeg.audio_settings = audio_settings

    def set_settings(self, ffmpeg_param=None):
        """
        Configures the opus widgets to match the selected task's ffmpeg settings.

        :param ffmpeg_param: (Default None) Use custom ffmpeg settings.
        """
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self._setup_opus_settings_widgets(ffmpeg)

    def _setup_opus_settings_widgets(self, ffmpeg):
        audio_settings = ffmpeg.audio_settings

        if ffmpeg.is_audio_settings_opus():
            self.is_widgets_setting_up = True
            self.opus_bitrate_spinbutton.set_value(audio_settings.bitrate)
            self.opus_channels_combobox.set_active(audio_settings.channels)
            self.is_widgets_setting_up = False
        else:
            self.reset_settings()

    def reset_settings(self):
        """
        Resets the opus widgets to their default values.
        """
        self.is_widgets_setting_up = True
        self.opus_bitrate_spinbutton.set_value(128)
        self.opus_channels_combobox.set_active(0)
        self.is_widgets_setting_up = False
