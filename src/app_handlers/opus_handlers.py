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


from ffmpeg.opus import Opus


class OpusHandlers:
    def __init__(self, gtk_builder):
        self.__is_widgets_setting_up = False
        self.inputs_page_handlers = None
        self.opus_channels_combobox = gtk_builder.get_object('opus_channels_combobox')
        self.opus_bitrate_spinbutton = gtk_builder.get_object('opus_bitrate_spinbutton')

    def reset_settings(self):
        self.__is_widgets_setting_up = True
        self.opus_bitrate_spinbutton.set_value(128)
        self.opus_channels_combobox.set_active(0)
        self.__is_widgets_setting_up = False

    def set_settings(self, ffmpeg_param=None):
        if ffmpeg_param is not None:
            ffmpeg = ffmpeg_param
        else:
            ffmpeg = self.inputs_page_handlers.get_selected_row_ffmpeg()

        self.__setup_opus_settings_widgets(ffmpeg)

    def __setup_opus_settings_widgets(self, ffmpeg):
        audio_settings = ffmpeg.audio_settings

        if audio_settings is not None and audio_settings.codec_name == 'libopus':
            self.__is_widgets_setting_up = True

            self.opus_bitrate_spinbutton.set_value(audio_settings.bitrate)
            self.opus_channels_combobox.set_active(audio_settings.channels)

            self.__is_widgets_setting_up = False
        else:
            self.reset_settings()

    def get_settings(self, ffmpeg):
        audio_settings = Opus()
        audio_settings.channels = self.opus_channels_combobox.get_active()
        audio_settings.bitrate = self.opus_bitrate_spinbutton.get_value_as_int()
        ffmpeg.audio_settings = audio_settings

    def __get_selected_inputs_rows(self):
        return self.inputs_page_handlers.get_selected_rows()

    def on_opus_bitrate_spinbutton_value_changed(self, bitrate_spinbutton):
        if self.__is_widgets_setting_up:
            return

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings.bitrate = bitrate_spinbutton.get_value_as_int()

            row.setup_labels()

    def on_opus_channels_combobox_changed(self, channels_combobox):
        if self.__is_widgets_setting_up:
            return

        channels_index = channels_combobox.get_active()

        for row in self.__get_selected_inputs_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.audio_settings.channels = channels_index

            row.setup_labels()
