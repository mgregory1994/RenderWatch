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


class CropPaddingSignal:
    """
    Handles the signals emitted when crop padding settings are changed.
    """

    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    # Unused parameters needed for this signal
    def _on_crop_pad_changed(self, crop_scale_widget, event=None, user_data=None):
        """
        Applies the padding settings and updates the crop preview.

        :param crop_scale_widget: Crop scale widget that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal Data
        """
        if self.crop_page_handlers.is_widgets_setting_up:
            return

        self.crop_page_handlers.apply_crop_settings()

        threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()

    def on_crop_x_padding_scale_button_release_event(self, crop_x_padding_scale, event=None, user_data=None):
        """
        Applies the x padding settings and updates the crop preview.

        :param crop_x_padding_scale: Crop scale widget that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal Data
        """
        self._on_crop_pad_changed(crop_x_padding_scale, event, user_data)

    def on_crop_x_padding_scale_key_release_event(self, crop_x_padding_scale, event=None, user_data=None):
        """
        Applies the x padding settings and updates the crop preview.

        :param crop_x_padding_scale: Crop scale widget that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal Data
        """
        self._on_crop_pad_changed(crop_x_padding_scale, event, user_data)

    def on_crop_y_padding_scale_button_release_event(self, crop_y_padding_scale, event=None, user_data=None):
        """
        Applies the x padding settings and updates the crop preview.

        :param crop_y_padding_scale: Crop scale widget that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal Data
        """
        self._on_crop_pad_changed(crop_y_padding_scale, event, user_data)

    def on_crop_y_padding_scale_key_release_event(self, crop_y_padding_scale, event=None, user_data=None):
        """
        Applies the x padding settings and updates the crop preview.

        :param crop_y_padding_scale: Crop scale widget that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal Data
        """
        self._on_crop_pad_changed(crop_y_padding_scale, event, user_data)
