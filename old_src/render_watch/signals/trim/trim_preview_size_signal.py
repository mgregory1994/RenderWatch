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


class TrimPreviewSizeSignal:
    """
    Handles the signal emitted when the Trim Preview Viewport's dimensions change.
    """

    def __init__(self, trim_page_handlers):
        self.trim_page_handlers = trim_page_handlers

    # Unused parameters needed for this signal
    def on_trim_preview_viewport_size_allocate(self, trim_preview_viewport, viewport_allocation=None):
        """
        Resized the Trim Preview based on the Viewport's dimensions.
        Maintains the preview's aspect ratio.

        :param trim_preview_viewport: Viewport that emitted the signal.
        :param viewport_allocation: Viewport's allocation data.
        """
        widget_width = trim_preview_viewport.get_allocated_width()
        widget_height = trim_preview_viewport.get_allocated_height()
        has_viewport_width_changed = not self.trim_page_handlers.get_preview_viewport_width() == widget_width
        has_viewport_height_changed = not self.trim_page_handlers.get_preview_viewport_height() == widget_height
        if has_viewport_width_changed or has_viewport_height_changed:
            self.trim_page_handlers.resize_trim_preview(widget_width, widget_height)
            self.trim_page_handlers.set_preview_viewport_width(widget_width)
            self.trim_page_handlers.set_preview_viewport_height(widget_height)
