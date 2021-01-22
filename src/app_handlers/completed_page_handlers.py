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


from startup import Gtk


class CompletedPageHandlers:
    def __init__(self, gtk_builder):
        self.main_window_handlers = None
        self.completed_page_listbox = gtk_builder.get_object('completed_list')
        self.clear_all_completed_button = gtk_builder.get_object("clear_all_completed_button")

        self.completed_page_listbox.set_header_func(self.__completed_list_update_header_func, None)

    @staticmethod
    def __completed_list_update_header_func(completed_page_listbox_row, previous_completed_page_listbox_row, data):
        if previous_completed_page_listbox_row is None:
            completed_page_listbox_row.set_header(None)
        else:
            completed_page_listbox_row_header = completed_page_listbox_row.get_header()

            if completed_page_listbox_row_header is None:
                completed_page_listbox_row_header = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

                completed_page_listbox_row_header.show()
                completed_page_listbox_row.set_header(completed_page_listbox_row_header)

    def get_rows(self):
        return self.completed_page_listbox.get_children()

    def remove_duplicate_row(self, completed_page_listbox_row):
        for listbox_row in self.get_rows():
            if listbox_row.file_path_link.get_uri() == completed_page_listbox_row.file_path_link.get_uri():
                listbox_row.on_remove_button_clicked(None)

                break

    def add_completed_page_listbox_row(self, completed_page_listbox_row):
        self.completed_page_listbox.add(completed_page_listbox_row)
        self.completed_page_listbox.show_all()

    def on_completed_list_add(self, completed_page_listbox, row):
        self.clear_all_completed_button.set_sensitive(True)

    def on_completed_list_remove(self, completed_page_listbox, completed_page_listbox_row):
        if not completed_page_listbox.get_children():
            self.clear_all_completed_button.set_sensitive(False)

        completed_page_listbox_row.destroy()

    def on_clear_all_completed_button_clicked(self, clear_all_completed_button):
        for row in self.completed_page_listbox.get_children():
            row.on_remove_button_clicked(None)

        clear_all_completed_button.set_sensitive(False)
        self.main_window_handlers.popdown_app_preferences_popover()
