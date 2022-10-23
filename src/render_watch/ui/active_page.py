# Copyright 2022 Michael Gregory
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


from render_watch.ui import Gtk, Adw


class ActivePageWidgets:
    def __init__(self):
        self.main_widget = Gtk.ListBox()

        self._setup_active_page_widgets()

    def _setup_active_page_widgets(self):
        self._setup_no_active_tasks_status_page()
        self._setup_options_popover_widgets()

        self.main_widget.set_placeholder(self.no_active_tasks_status_page)
        self.main_widget.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.main_widget.set_show_separators(True)
        self.main_widget.set_vexpand(True)
        self.main_widget.set_hexpand(True)

    def _setup_no_active_tasks_status_page(self):
        self.no_active_tasks_status_page = Adw.StatusPage.new()
        self.no_active_tasks_status_page.set_title('No Active Tasks')
        self.no_active_tasks_status_page.set_description('Use the inputs page to start a new task')
        self.no_active_tasks_status_page.set_icon_name('action-unavailable-symbolic')
        self.no_active_tasks_status_page.set_sensitive(False)

    def _setup_options_popover_widgets(self):
        self._setup_task_preview_widgets()

        pause_all_button = Gtk.Button(label='Pause All')

        stop_all_button = Gtk.Button(label='Stop All')
        stop_all_button.add_css_class('destructive-action')

        self.popover_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.popover_options_vertical_box.append(pause_all_button)
        self.popover_options_vertical_box.append(stop_all_button)
        self.popover_options_vertical_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.popover_options_vertical_box.append(self.task_preview_horizontal_box)

    def _setup_task_preview_widgets(self):
        task_preview_label = Gtk.Label(label='Preview Running Tasks')

        task_preview_switch = Gtk.Switch()
        task_preview_switch.set_hexpand(True)
        task_preview_switch.set_halign(Gtk.Align.END)

        self.task_preview_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.task_preview_horizontal_box.append(task_preview_label)
        self.task_preview_horizontal_box.append(task_preview_switch)
