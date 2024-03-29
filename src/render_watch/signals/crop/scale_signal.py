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


class ScaleSignal:
    """
    Handles the signal emitted when scale settings are toggled.
    """

    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    def on_scale_enabled_checkbutton_toggled(self, scale_enabled_checkbutton):
        """
        Applies scale settings, updates the crop page's widgets, and updates the crop preview.

        :param scale_enabled_checkbutton: Checkbutton that emitted the signal.
        """
        self.crop_page_handlers.set_scale_state(scale_enabled_checkbutton.get_active())

        if self.crop_page_handlers.is_widgets_setting_up:
            return

        self.crop_page_handlers.apply_crop_settings()

        threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()
