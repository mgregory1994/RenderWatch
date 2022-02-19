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


class ConcurrentTasksSignal:
    """
    Handles the signals emitted when Concurrency related options are changed in the preferences dialog.
    """

    def __init__(self, application_preferences_handlers, application_preferences):
        self.application_preferences_handlers = application_preferences_handlers
        self.application_preferences = application_preferences

    def on_concurrent_tasks_combobox_changed(self, concurrent_tasks_combobox):
        """
        Applies the Concurrent Tasks option to the application's preferences.

        :param concurrent_tasks_combobox: Combobox that emitted the signal.
        """
        parallel_tasks_value = ApplicationPreferences.PARALLEL_TASKS_VALUES[concurrent_tasks_combobox.get_active()]
        self.application_preferences.parallel_tasks = parallel_tasks_value

        self.application_preferences_handlers.update_concurrent_tasks_restart_state()
        self.application_preferences_handlers.update_concurrent_message(parallel_tasks_value)

    def on_concurrent_nvenc_tasks_combobox_changed(self, concurrent_nvenc_tasks_combobox):
        """
        Applies the NVENC Concurrent Tasks option to the application's preferences.

        :param concurrent_nvenc_tasks_combobox: Combobox that emitted the signal.
        """
        concurrent_nvenc_text = ApplicationPreferences.CONCURRENT_NVENC_VALUES[
            concurrent_nvenc_tasks_combobox.get_active()
        ]
        self.application_preferences.set_concurrent_nvenc_value(concurrent_nvenc_text)

        self.application_preferences_handlers.update_nvenc_concurrent_tasks_restart_state(concurrent_nvenc_text)

    def on_simultaneous_concurrent_nvenc_tasks_switch_state_set(self,
                                                                simultaneous_concurrent_nvenc_tasks_switch,
                                                                user_data=None):
        """
        Toggles the NVENC Concurrent Tasks option in the application's preferences.

        :param simultaneous_concurrent_nvenc_tasks_switch: Switch that emitted the signal.
        """
        self.application_preferences.is_concurrent_nvenc_enabled = simultaneous_concurrent_nvenc_tasks_switch.get_active()

    def on_run_watch_folders_concurrently_switch_state_set(self, run_watch_folders_concurrently_switch, user_data=None):
        """
        Toggles the Run Watch Folder Tasks Concurrently option in the application's preferences.

        :param run_watch_folders_concurrently_switch: Switch that emitted the signal.
        """
        self.application_preferences.is_concurrent_watch_folder_enabled = run_watch_folders_concurrently_switch.get_active()
