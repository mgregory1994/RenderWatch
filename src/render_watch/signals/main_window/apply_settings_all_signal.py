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
import copy

from render_watch.startup import GLib


class ApplySettingsAllSignal:
    """
    Handles the signal emitted from the apply settings to all in the options menu.
    """

    def __init__(self, main_window_handlers, inputs_page_handlers, settings_sidebar_handlers, application_preferences):
        self.main_window_handlers = main_window_handlers
        self.inputs_page_handlers = inputs_page_handlers
        self.settings_sidebar_handlers = settings_sidebar_handlers
        self.application_preferences = application_preferences

    # Unused parameters needed for this signal
    def on_apply_settings_to_all_switch_state_set(self, apply_settings_to_all_switch, user_data=None):
        if apply_settings_to_all_switch.get_active():
            self._apply_settings_to_all_inputs()
        else:
            if self.inputs_page_handlers.get_selected_row() is None:
                self.main_window_handlers.set_input_selected_state(False)

    def _apply_settings_to_all_inputs(self):
        self.main_window_handlers.update_ffmpeg_template()
        threading.Thread(target=self._set_settings_sidebar_to_ffmpeg_template, args=()).start()
        self._apply_ffmpeg_template_to_all_inputs()

        self.main_window_handlers.set_input_selected_state(True)

    def _set_settings_sidebar_to_ffmpeg_template(self):
        ffmpeg_template = self.main_window_handlers.ffmpeg_template
        general_settings = ffmpeg_template.general_settings
        video_settings = ffmpeg_template.video_settings
        audio_settings = ffmpeg_template.audio_settings
        is_general_settings_custom = general_settings.frame_rate or general_settings.fast_start

        if video_settings or audio_settings or is_general_settings_custom:
            self._setup_settings_sidebar(ffmpeg_template)
        else:
            self._reset_settings_sidebar()

    def _reset_settings_sidebar(self):
        GLib.idle_add(self.settings_sidebar_handlers.reset_settings)

    def _setup_settings_sidebar(self, ffmpeg):
        GLib.idle_add(self.settings_sidebar_handlers.set_settings, ffmpeg)

    def _apply_ffmpeg_template_to_all_inputs(self):
        ffmpeg_template = self.main_window_handlers.ffmpeg_template

        for row in self.inputs_page_handlers.get_rows():
            row_ffmpeg = row.ffmpeg
            row_ffmpeg.output_container = ffmpeg_template.output_container
            row_ffmpeg.general_settings.ffmpeg_args = ffmpeg_template.general_settings.ffmpeg_args.copy()

            if ffmpeg_template.video_settings:
                row_ffmpeg.video_settings = copy.deepcopy(ffmpeg_template.video_settings)
            else:
                row_ffmpeg.video_settings = None

            if ffmpeg_template.audio_settings:
                row_ffmpeg.audio_settings = copy.deepcopy(ffmpeg_template.audio_settings)
            else:
                row.ffmpeg.audio_settings = None

            if row_ffmpeg.is_video_settings_2_pass():
                row_ffmpeg.video_settings.stats = self.application_preferences.temp_directory \
                                                  + '/' \
                                                  + row_ffmpeg.temp_file_name \
                                                  + '.log'

            GLib.idle_add(row.setup_labels)
