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


import threading


class CropDimensionsSignal:
    """
    Handles the signals emitted when crop dimensions are changed.
    """

    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    # Unused parameters needed for this signal
    def on_crop_width_spinbutton_activate(self, crop_width_spinbutton, event=None, user_data=None):
        """
        Applies crop width settings and updates the crop page's widgets.

        :param crop_width_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        ffmpeg = self.crop_page_handlers.ffmpeg
        width, original_width = crop_width_spinbutton.get_value_as_int(), ffmpeg.width_origin
        upper_limit = original_width - width

        if self.crop_page_handlers.get_crop_x_value() > upper_limit:
            self.crop_page_handlers.set_crop_x_value(upper_limit)
        self.crop_page_handlers.set_crop_x_upper_limit(upper_limit)

        if self.crop_page_handlers.is_widgets_setting_up:
            return

        self.crop_page_handlers.apply_crop_settings()

        threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()

    def on_crop_width_spinbutton_button_release_event(self, crop_width_spinbutton, event=None, user_data=None):
        """
        Applies crop width settings and updates the crop page's widgets.

        :param crop_width_spinbutton: Spinbutton that emitted the signal
        :param event: Signal event.
        :param user_data: Signal user_data
        """
        self.on_crop_width_spinbutton_activate(crop_width_spinbutton, event)

    # Unused parameters needed for this signal
    def on_crop_height_spinbutton_activate(self, crop_height_spinbutton, event=None, user_data=None):
        """
        Applies crop height settings and updates the crop page's widgets.

        :param crop_height_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        ffmpeg = self.crop_page_handlers.ffmpeg
        height, original_height = crop_height_spinbutton.get_value_as_int(), ffmpeg.height_origin
        upper_limit = original_height - height

        if self.crop_page_handlers.get_crop_y_value() > upper_limit:
            self.crop_page_handlers.set_crop_y_value(upper_limit)
        self.crop_page_handlers.set_crop_y_upper_limit(upper_limit)

        if self.crop_page_handlers.is_widgets_setting_up:
            return

        self.crop_page_handlers.apply_crop_settings()

        threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()

    def on_crop_height_spinbutton_button_release_event(self, crop_height_spinbutton, event=None, user_data=None):
        """
        Applies crop height settings and updates the crop page's widgets.

        :param crop_height_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self.on_crop_height_spinbutton_activate(crop_height_spinbutton, event)
