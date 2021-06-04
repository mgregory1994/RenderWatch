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

from render_watch.encoding import preview
from render_watch.startup import Gtk, GLib


class AutocropSignal:
    def __init__(self, crop_page_handlers):
        self.crop_page_handlers = crop_page_handlers

    def on_crop_autocrop_enabled_button_toggled(self, auto_crop_enabled_checkbox):
        auto_crop_enabled = auto_crop_enabled_checkbox.get_active()

        self.crop_page_handlers.update_autocrop_state()

        if self.crop_page_handlers.is_widgets_setting_up:
            return

        if auto_crop_enabled:
            threading.Thread(target=self.setup_autocrop, args=()).start()
        else:
            ffmpeg = self.crop_page_handlers.ffmpeg
            ffmpeg.picture_settings.auto_crop = False

            self.crop_page_handlers.setup_crop_settings()
            threading.Thread(target=self.crop_page_handlers.set_crop_thumbnail, args=()).start()

    def setup_autocrop(self):
        ffmpeg = self.crop_page_handlers.ffmpeg
        auto_crop_enabled = preview.process_auto_crop(ffmpeg)

        if auto_crop_enabled:
            ffmpeg.picture_settings.auto_crop = auto_crop_enabled

            self.crop_page_handlers.set_crop_thumbnail()
        else:
            GLib.idle_add(self.__show_auto_crop_not_needed_dialog)
            GLib.idle_add(self.crop_page_handlers.set_auto_crop_state, False)

    def __show_auto_crop_not_needed_dialog(self):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Auto crop not needed'
        )

        message_dialog.format_secondary_text('Could not detect any \"black bars\" within the picture.')
        message_dialog.run()
        message_dialog.destroy()
