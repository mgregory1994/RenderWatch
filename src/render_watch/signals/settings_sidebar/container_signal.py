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


from render_watch.ffmpeg.general_settings import GeneralSettings


class ContainerSignal:
    """Handles the signal emitted when the Container option is changed in the settings sidebar."""

    def __init__(self, settings_sidebar_handlers, inputs_page_handlers):
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.inputs_page_handlers = inputs_page_handlers

    def on_container_combobox_changed(self, container_combobox):
        """Configures the settings sidebar for the new container and applies the container option.

        :param container_combobox:
            Combobox that emitted the signal.
        """
        container_text = GeneralSettings.CONTAINERS_UI_LIST[container_combobox.get_active()]
        if container_text == '.mp4':
            self.settings_sidebar_handlers.set_mp4_state()
        elif container_text == '.mkv':
            self.settings_sidebar_handlers.set_mkv_state()
        elif container_text == '.ts':
            self.settings_sidebar_handlers.set_ts_state()
        elif container_text == '.webm':
            self.settings_sidebar_handlers.set_webm_state()

        if self.settings_sidebar_handlers.is_widgets_setting_up:
            return

        for row in self.inputs_page_handlers.get_selected_rows():
            ffmpeg = row.ffmpeg
            if container_text == 'copy':
                ffmpeg.output_container = None
            else:
                ffmpeg.output_container = container_text
            row.setup_labels()
