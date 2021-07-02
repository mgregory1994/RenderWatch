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


from render_watch.startup import Gtk


class StopAllSignal:
    """Handles the signal emitted from the stop all button on the active page's options menu."""

    def __init__(self, active_page_handlers, main_window_handlers, remove_signal):
        self.active_page_handlers = active_page_handlers
        self.main_window_handlers = main_window_handlers
        self.remove_signal = remove_signal

    def on_stop_all_proc_button_clicked(self, stop_all_tasks_button):  # Unused parameters needed for this signal
        """Stops all tasks on the active page.

        :param stop_all_tasks_button:
            Button that emitted the signal.
        """
        self.main_window_handlers.app_preferences_popover.popdown()

        stop_all_tasks_message_response = self._show_stop_all_tasks_message_dialog()
        if stop_all_tasks_message_response == Gtk.ResponseType.YES:
            for row in self.active_page_handlers.get_rows():
                row.on_stop_button_clicked(None)
            self.active_page_handlers.signal_remove_row()

    def _show_stop_all_tasks_message_dialog(self):
        # Confirms if the user wants to stop all tasks.
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.YES_NO,
                                           'Stop all tasks?')
        message_dialog.format_secondary_text('This will stop and remove all queued and running tasks')
        response = message_dialog.run()
        message_dialog.destroy()
        return response
