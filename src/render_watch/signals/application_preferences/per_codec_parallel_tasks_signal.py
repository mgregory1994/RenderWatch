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


from render_watch.startup.application_preferences import ApplicationPreferences


class PerCodecParallelTasksSignal:
    """
    Handles the signals emitted when per codec related options are change in the application preferences dialog.
    """

    def __init__(self, application_preferences_handlers, application_preferences):
        self.application_preferences_handlers = application_preferences_handlers
        self.application_preferences = application_preferences

    def on_per_codec_switch_state_set(self, per_codec_switch, user_data=None):
        self.application_preferences.is_per_codec_parallel_tasks_enabled = per_codec_switch.get_active()

        if per_codec_switch.get_active():
            self.application_preferences_handlers.show_per_codec_options()
        else:
            self.application_preferences_handlers.show_parallel_tasks_options()

        self.application_preferences_handlers.update_per_codec_tasks_restart_state()

    def on_per_codec_x264_combobox_changed(self, per_codec_x264_combobox):
        per_codec_x264_index = per_codec_x264_combobox.get_active()
        per_codec_x264_value = ApplicationPreferences.PER_CODEC_TASKS_VALUES[per_codec_x264_index]
        self.application_preferences.per_codec_parallel_tasks['x264'] = per_codec_x264_value

        self.application_preferences_handlers.update_per_codec_value_restart_state()

    def on_per_codec_x265_combobox_changed(self, per_codec_x265_combobox):
        per_codec_x265_index = per_codec_x265_combobox.get_active()
        per_codec_x265_value = ApplicationPreferences.PER_CODEC_TASKS_VALUES[per_codec_x265_index]
        self.application_preferences.per_codec_parallel_tasks['x265'] = per_codec_x265_value

        self.application_preferences_handlers.update_per_codec_value_restart_state()

    def on_per_codec_vp9_combobox_changed(self, per_codec_vp9_combobox):
        per_codec_vp9_index = per_codec_vp9_combobox.get_active()
        per_codec_vp9_value = ApplicationPreferences.PER_CODEC_TASKS_VALUES[per_codec_vp9_index]
        self.application_preferences.per_codec_parallel_tasks['vp9'] = per_codec_vp9_value

        self.application_preferences_handlers.update_per_codec_value_restart_state()
