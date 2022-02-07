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


class RemoveAllSignal:
    """
    Handles the signal emitted from the remove all button on the inputs page's options menu.
    """

    def __init__(self, inputs_page_handlers, main_window_handlers):
        self.inputs_page_handlers = inputs_page_handlers
        self.main_window_handlers = main_window_handlers

    def on_remove_all_button_clicked(self, remove_all_button):  # Unused parameters needed for this signal
        """
        On user confirmation, removes all inputs from the inputs page.

        :param remove_all_button: Button that emitted the signal.
        """
        message_dialog = Gtk.MessageDialog(self.main_window_handlers.main_window,
                                           Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                           Gtk.MessageType.WARNING,
                                           Gtk.ButtonsType.YES_NO,
                                           'Remove all inputs?')
        message_dialog.format_secondary_text('This will remove all of your imports along with any settings applied')

        response = message_dialog.run()
        if response == Gtk.ResponseType.YES:
            self.inputs_page_handlers.remove_all_rows()

        message_dialog.destroy()

        self.main_window_handlers.popdown_app_preferences_popover()
