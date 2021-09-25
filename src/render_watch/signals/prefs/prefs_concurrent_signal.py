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


from render_watch.startup.preferences import Preferences


class PrefsConcurrentSignal:
    """Handles the signals emitted when the Concurrency related options are changed in the preferences dialog."""

    def __init__(self, prefs_handlers, preferences):
        self.prefs_handlers = prefs_handlers
        self.preferences = preferences

    def on_prefs_concurrent_combobox_changed(self, concurrent_combobox):
        """Applies the Concurrent Tasks value option to the application's preferences.

        :param concurrent_combobox:
            Combobox that emitted the signal.
        """
        parallel_tasks_value = Preferences.parallel_tasks_values_list[concurrent_combobox.get_active()]
        self.preferences.parallel_tasks = parallel_tasks_value
        self.prefs_handlers.update_concurrent_restart_state()
        self.prefs_handlers.update_concurrent_message(parallel_tasks_value)

    def on_prefs_nvenc_concurrent_combobox_changed(self, nvenc_concurrent_combobox):
        """Applies the NVENC Concurrent Tasks value option to the application's preferences.

        :param nvenc_concurrent_combobox:
            Combobox that emitted the signal.
        """
        concurrent_nvenc_text = Preferences.concurrent_nvenc_values_list[nvenc_concurrent_combobox.get_active()]
        self.preferences.concurrent_nvenc_value = concurrent_nvenc_text
        self.prefs_handlers.update_nvenc_concurrent_restart_state(concurrent_nvenc_text)

    def on_prefs_nvenc_concurrent_checkbox_toggled(self, nvenc_concurrent_checkbox):
        """Toggles the NVENC Concurrent Tasks option in the application's preferences.

        :param nvenc_concurrent_checkbox:
            Checkbox that emitted the signal.
        """
        self.preferences.concurrent_nvenc = nvenc_concurrent_checkbox.get_active()

    def on_prefs_watch_concurrent_checkbox_toggled(self, watch_folder_concurrent_checkbox):
        """Toggles the Concurrent Watch Folder Tasks option in the application's preferences.

        :param watch_folder_concurrent_checkbox:
            Checkbox that emitted the signal.
        """
        self.preferences.concurrent_watch_folder = watch_folder_concurrent_checkbox.get_active()
