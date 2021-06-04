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


import threading


class CropPaddingSignal:
    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    def on_crop_pad_changed(self, event, data):  # Unused parameters needed for this signal
        if not self.crop_page_handlers.is_widgets_setting_up:
            self.crop_page_handlers.setup_crop_settings()
            threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()
