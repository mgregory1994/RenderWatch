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


from render_watch.app_handlers.completed_row import CompletedRow
from render_watch.startup import Gtk


class ActivePageHandlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.main_window_handlers = None
        self.completed_page_handlers = None
        self.active_page_listbox = gtk_builder.get_object('active_list')
        self.stop_all_processing_button = gtk_builder.get_object('stop_all_proc_button')
        self.pause_all_processing_button = gtk_builder.get_object('pause_all_proc_button')
        self.resume_all_processing_button = gtk_builder.get_object('resume_all_proc_button')
        self.live_thumbnails_switch = gtk_builder.get_object('live_thumbnails_switch')

        self.active_page_listbox.set_header_func(self.__active_list_update_header_func, None)

    @staticmethod
    def __active_list_update_header_func(active_page_listbox_row, previous_active_page_listbox_row, data):
        if previous_active_page_listbox_row is None:
            active_page_listbox_row.set_header(None)
        else:
            active_page_listbox_row_header = active_page_listbox_row.get_header()

            if active_page_listbox_row_header is None:
                active_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

                active_page_listbox_row_header.show()
                active_page_listbox_row.set_header(active_page_listbox_row_header)

    def get_active_page_listbox_rows(self):
        return self.active_page_listbox.get_children()

    def add_active_page_listbox_row(self, active_page_listbox_row):
        self.active_page_listbox.add(active_page_listbox_row)
        self.active_page_listbox.show_all()

    def on_pause_all_proc_button_clicked(self, pause_all_tasks_button):
        self.main_window_handlers.popdown_app_preferences_popover()

        for row in self.get_active_page_listbox_rows():
            row.on_pause_button_clicked(None)

    def on_resume_all_proc_button_clicked(self, resume_all_tasks_button):
        self.main_window_handlers.popdown_app_preferences_popover()

        for row in self.get_active_page_listbox_rows():
            row.on_start_button_clicked(None)

    def on_stop_all_proc_button_clicked(self, stop_all_tasks_button):
        self.main_window_handlers.app_preferences_popover.popdown()

        stop_all_tasks_message_response = self.__show_stop_all_tasks_message_dialog()

        if stop_all_tasks_message_response == Gtk.ResponseType.YES:
            for row in self.get_active_page_listbox_rows():
                row.on_stop_button_clicked(None)

            self.on_active_list_remove(self.active_page_listbox, None)

    def __show_stop_all_tasks_message_dialog(self):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            'Stop all tasks?',
        )

        message_dialog.format_secondary_text('This will stop and remove all queued and running tasks')

        response = message_dialog.run()

        message_dialog.destroy()

        return response

    def on_live_thumbnails_switch_state_set(self, live_thumbnails_switch, user_data):
        for row in self.get_active_page_listbox_rows():
            row.live_thumbnail = live_thumbnails_switch.get_active()

    def on_active_list_add(self, active_page_listbox, active_page_listbox_row):
        active_page_listbox_row.live_thumbnail = self.live_thumbnails_switch.get_active()

        self.__set_sensitive_for_active_page_preferences_widgets(True)

    def __set_sensitive_for_active_page_preferences_widgets(self, is_sensitive):
        self.pause_all_processing_button.set_sensitive(is_sensitive)
        self.resume_all_processing_button.set_sensitive(is_sensitive)
        self.stop_all_processing_button.set_sensitive(is_sensitive)

    def on_active_list_remove(self, active_page_listbox, active_page_listbox_row):
        self.__add_active_page_listbox_row_to_completed_page(active_page_listbox_row)

        if not active_page_listbox.get_children():
            self.__set_sensitive_for_active_page_preferences_widgets(False)

    def __add_active_page_listbox_row_to_completed_page(self, active_page_listbox_row):
        if self.__is_active_page_listbox_row_finished(active_page_listbox_row):
            completed_row = CompletedRow(active_page_listbox_row, self.completed_page_handlers.completed_page_listbox,
                                         self.preferences)

            self.completed_page_handlers.remove_duplicate_row(completed_row)
            self.completed_page_handlers.add_completed_page_listbox_row(completed_row)

    @staticmethod
    def __is_active_page_listbox_row_finished(active_page_listbox_row):
        return active_page_listbox_row is not None and active_page_listbox_row.finished \
               and not active_page_listbox_row.failed
