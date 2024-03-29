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


class PreviewSizeSignal:
    """
    Handles the signal emitted when the crop preview's viewport size changes.
    """

    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    # Unused parameters needed for this signal
    def on_crop_preview_viewport_size_allocate(self, crop_preview_viewport, allocation=None):
        """
        Resizes the crop preview to match the size of the viewport.

        :param crop_preview_viewport: Viewport that emitted the signal.
        :param allocation: Viewport allocation.
        """
        widget_width = crop_preview_viewport.get_allocated_width()
        widget_height = crop_preview_viewport.get_allocated_height()

        has_viewport_width_changed = not self.crop_page_handlers.crop_preview_viewport_width == widget_width
        has_viewport_height_changed = not self.crop_page_handlers.crop_preview_viewport_height == widget_height
        if has_viewport_width_changed or has_viewport_height_changed:
            self.crop_page_handlers.set_thumbnail_size(widget_width, widget_height)
            self.crop_page_handlers.set_preview_viewport_width(widget_width)
            self.crop_page_handlers.set_preview_viewport_height(widget_height)
