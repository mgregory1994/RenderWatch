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


class FramerateSignal:
    """Handles the signals emitted when the Frame Rate type options are changed in the settings sidebar."""

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_framerate_auto_radiobutton_clicked(self, frame_rate_auto_radiobutton):
        """Removes the Frame Rate option and uses the input's frame rate instead.

        :param frame_rate_auto_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not frame_rate_auto_radiobutton.get_active():
            return

        self.settings_sidebar_handlers.set_framerate_state(False)

        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = None
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_framerate_custom_radiobutton_clicked(self, frame_rate_custom_radiobutton):
        """Applies the custom Frame Rate option.

        :param frame_rate_custom_radiobutton:
            Radiobutton that emitted the signal.
        """
        if not frame_rate_custom_radiobutton.get_active():
            return

        self.settings_sidebar_handlers.set_framerate_state(True)

        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        frame_rate_index = self.settings_sidebar_handlers.get_framerate_value()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = frame_rate_index
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()

    def on_fps_combobox_changed(self, frame_rate_combobox):
        """Applies the selected Frame Rate value option.

        :param frame_rate_combobox:
            Combobox that emitted the signal.
        """
        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        frame_rate_index = frame_rate_combobox.get_active()
        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            ffmpeg.general_settings.frame_rate = frame_rate_index
            row.setup_labels()

        self.inputs_page_handlers.update_preview_page()
