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


from render_watch.ffmpeg.aac import Aac
from render_watch.signals.aac.aac_bitrate_signal import AacBitrateSignal
from render_watch.signals.aac.aac_channels_signal import AacChannelsSignal


class AacHandlers:
    def __init__(self, gtk_builder, inputs_page_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.is_widgets_setting_up = False
        self.aac_bitrate_signal = AacBitrateSignal(self, inputs_page_handlers)
        self.aac_channels_signal = AacChannelsSignal(self, inputs_page_handlers)
        self.signals_list = (self.aac_bitrate_signal, self.aac_channels_signal)
        self.aac_channels_combobox = gtk_builder.get_object('aac_channels_combobox')
        self.aac_bitrate_spinbutton = gtk_builder.get_object('aac_bitrate_spinbutton')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)

        raise AttributeError

    def get_settings(self, ffmpeg):
        audio_settings = Aac()
        audio_settings.bitrate = self.aac_bitrate_spinbutton.get_value_as_int()
        audio_settings.channels = self.aac_channels_combobox.get_active()
        ffmpeg.audio_settings = audio_settings

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_aac_settings_widgets(ffmpeg)

    def __setup_aac_settings_widgets(self, ffmpeg):
        audio_settings = ffmpeg.audio_settings

        if audio_settings is not None and audio_settings.codec_name == 'aac':
            self.is_widgets_setting_up = True

            self.aac_bitrate_spinbutton.set_value(audio_settings.bitrate)
            self.aac_channels_combobox.set_active(audio_settings.channels)

            self.is_widgets_setting_up = False
        else:
            self.reset_settings()

    def reset_settings(self):
        self.is_widgets_setting_up = True
        self.aac_channels_combobox.set_active(0)
        self.aac_bitrate_spinbutton.set_value(128)
        self.is_widgets_setting_up = False
