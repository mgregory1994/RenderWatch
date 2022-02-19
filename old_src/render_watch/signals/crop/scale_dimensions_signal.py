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


class ScaleDimensionsSignal:
    """
    Handles the signals emitted when scale dimensions are changed.
    """

    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    # Unused parameters needed for this signal
    def _apply_scale(self, scale_spinbutton, event=None, user_data=None):
        """
        Applies the scale settings and updates the crop preview.

        :param scale_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        if self.crop_page_handlers.is_widgets_setting_up:
            return

        self.crop_page_handlers.apply_crop_settings()

        threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()

    def on_scale_width_spinbutton_activate(self, scale_width_spinbutton, event=None):
        """
        Applies scale settings and updates the crop preview.

        :param scale_width_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        """
        self._apply_scale(scale_width_spinbutton, event)

    def on_scale_width_spinbutton_button_release_event(self, scale_width_spinbutton, event=None, user_data=None):
        """
        Applies scale settings and updates the crop preview.

        :param scale_width_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self._apply_scale(scale_width_spinbutton, event, user_data)

    def on_scale_height_spinbutton_activate(self, scale_height_spinbutton, event=None):
        """
        Applies scale settings and updates the crop preview.

        :param scale_height_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        """
        self._apply_scale(scale_height_spinbutton, event)

    def on_scale_height_spinbutton_button_release_event(self, scale_height_spinbutton, event=None, user_data=None):
        """
        Applies scale settings and updates the crop preview.

        :param scale_height_spinbutton: Spinbutton that emitted the signal.
        :param event: Signal event.
        :param user_data: Signal user data.
        """
        self._apply_scale(scale_height_spinbutton, event, user_data)
