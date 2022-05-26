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


import threading
import os

from pathlib import Path

from render_watch.ui import Gtk, Gdk, Gio, GLib, Adw
from render_watch.ui import inputs_page
from render_watch.ui import active_page
from render_watch.ui import completed_page
from render_watch.encode import encoder_queue, preview
from render_watch.ffmpeg import encoding
from render_watch import app_preferences


class RenderWatch(Adw.Application):
    def __init__(self, app_settings: app_preferences.Settings):
        super().__init__(application_id='test.demo', flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.app_settings = app_settings
        # self.task_queue = encoder_queue.TaskQueue(self.app_settings)
        self.preview_generator = preview.PreviewGenerator(self.app_settings)

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        self.main_window = Adw.ApplicationWindow(application=self, destroy_with_parent=True, title='Render Watch')
        self.main_window.set_size_request(1000, 600)
        self.main_window.set_default_size(1280, 720)
        self._setup_window_contents()
        self.about_dialog = self.AboutDialog(self, self.main_window)
        self.preferences_window = self.PreferencesWindow(self, self.main_window, self.app_settings)
        self.main_window.connect('close-request', lambda user_data: self.quit())
        self.main_window.present()

    def do_shutdown(self):
        self.preview_generator.kill()
        self.app_settings.save()
        app_preferences.clear_temp_directory(self.app_settings)

        Adw.Application.do_shutdown(self)

    def _setup_window_contents(self):
        self._setup_task_states_stack()
        self._setup_task_states_view_switcher()
        self._setup_add_inputs_widgets()
        self._setup_options_menu()
        self._setup_settings_sidebar_button()
        self._setup_header_bar()

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vertical_box.append(self.header_bar)
        vertical_box.append(self.inputs_toast_overlay)
        self.main_window.set_content(vertical_box)

    def _setup_task_states_stack(self):
        self._setup_inputs_page_widgets()
        self._setup_active_page_widgets()
        self._setup_completed_page_widgets()
        self.task_states_stack = Adw.ViewStack()
        self.task_states_stack.add_titled(self.inputs_page_widgets.main_widget, 'inputs_page', 'Inputs')
        self.task_states_stack.add_titled(self.active_page_widgets.main_widget, 'active_page', 'Active')
        self.task_states_stack.add_titled(self.completed_page_widgets.main_widget, 'completed_page', 'Completed')
        self.task_states_stack.get_page(self.inputs_page_widgets.main_widget).set_icon_name('list-add-symbolic')
        self.task_states_stack.get_page(self.active_page_widgets.main_widget).set_icon_name('view-list-symbolic')
        self.task_states_stack.get_page(self.completed_page_widgets.main_widget).set_icon_name('computer-symbolic')
        self.task_states_stack.connect('notify', self.switch_page_popover_options)

        self.inputs_toast_overlay = Adw.ToastOverlay()
        self.inputs_toast_overlay.set_child(self.task_states_stack)

    def _setup_inputs_page_widgets(self):
        self.inputs_page_widgets = inputs_page.InputsPageWidgets(self, self.preview_generator, self.app_settings)

    def _setup_active_page_widgets(self):
        self.active_page_widgets = active_page.ActivePageWidgets()

    def _setup_completed_page_widgets(self):
        self.completed_page_widgets = completed_page.CompletedPageWidgets()

    def _setup_task_states_view_switcher(self):
        self.task_states_view_switcher = Adw.ViewSwitcher()
        self.task_states_view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self.task_states_view_switcher.set_stack(self.task_states_stack)

    def _setup_add_inputs_widgets(self):
        self.add_button = Gtk.Button(label='Add')
        self.add_button.connect('clicked', self.show_input_file_chooser)
        self.add_button.add_css_class('suggested-action')
        self.input_type_combobox = Gtk.ComboBoxText()
        self.input_type_combobox.append_text('Files')
        self.input_type_combobox.append_text('Folders')
        self.input_type_combobox.set_active(0)
        self.input_type_combobox.connect('changed', self.set_input_type_state)

        self.add_inputs_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add_inputs_horizontal_box.append(self.add_button)
        self.add_inputs_horizontal_box.append(self.input_type_combobox)
        self.add_inputs_horizontal_box.add_css_class('linked')

    def _show_add_button_clicked_toast(self, add_button):
        button_clicked_toast = Adw.Toast(title='Add Button Clicked!')
        self.inputs_toast_overlay.add_toast(button_clicked_toast)
        action_row = Adw.ActionRow()
        action_row.set_title('New Input')
        action_row.set_subtitle('Video')
        action_row.add_suffix(Gtk.Switch())
        self.inputs_page_widgets.inputs_list_box.append(action_row)

    def _setup_options_menu(self):
        self.options_menu_button = Gtk.MenuButton()
        self.options_menu_button.set_icon_name('open-menu-symbolic')
        self.settings_button = Gtk.Button(label='Settings')
        self.settings_button.connect('clicked', self.show_preferences_window)
        self.about_button = Gtk.Button(label='About Render Watch')
        self.about_button.connect('clicked', self.show_about_dialog)

        self.page_popover_options_stack = Adw.ViewStack()
        self.page_popover_options_stack.add_named(self.inputs_page_widgets.popover_options_vertical_box, 'inputs_page')
        self.page_popover_options_stack.add_named(self.active_page_widgets.popover_options_vertical_box, 'active_page')
        self.page_popover_options_stack.add_named(self.completed_page_widgets.popover_options_vertical_box,
                                                  'completed_page')
        self.page_popover_options_stack.set_vhomogeneous(False)

        options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        options_vertical_box.append(self.page_popover_options_stack)
        options_vertical_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        options_vertical_box.append(self.settings_button)
        options_vertical_box.append(self.about_button)
        options_vertical_box.set_margin_start(5)
        options_vertical_box.set_margin_end(5)
        options_vertical_box.set_margin_top(5)
        options_vertical_box.set_margin_bottom(5)

        self.options_popover = Gtk.Popover()
        self.options_popover.set_child(options_vertical_box)
        self.options_menu_button.set_popover(self.options_popover)

    def _setup_settings_sidebar_button(self):
        self.toggle_settings_sidebar_button = Gtk.Button()
        self.toggle_settings_sidebar_button.set_icon_name('sidebar-show-rtl-symbolic')
        self.toggle_settings_sidebar_button.connect('clicked', self.inputs_page_widgets.toggle_settings_sidebar)

    def _setup_header_bar(self):
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_title_widget(self.task_states_view_switcher)
        self.header_bar.pack_start(self.add_inputs_horizontal_box)
        self.header_bar.pack_end(self.options_menu_button)
        self.header_bar.pack_end(self.toggle_settings_sidebar_button)

    def switch_page_popover_options(self, property, user_data):
        try:
            if self.task_states_stack.get_visible_child_name() != self.page_popover_options_stack.get_visible_child_name():
                self.page_popover_options_stack.set_visible_child_name(self.task_states_stack.get_visible_child_name())
        except AttributeError:
            pass

    def set_input_type_state(self, combobox):
        if combobox.get_active_text() == 'Files':
            self.inputs_page_widgets.set_input_type_state(is_file_state_enabled=True)
        else:
            self.inputs_page_widgets.set_input_type_state()

    def show_input_file_chooser(self, button):
        if self.input_type_combobox.get_active_text() == 'Files':
            title = 'Open Media File'
            action = Gtk.FileChooserAction.OPEN
        else:
            title = 'Open Folder'
            action = Gtk.FileChooserAction.SELECT_FOLDER

        input_file_chooser = Gtk.FileChooserDialog(title=title,
                                                   action=action,
                                                   transient_for=self.main_window,
                                                   modal=True,
                                                   destroy_with_parent=True,
                                                   resizable=False)
        input_file_chooser.add_buttons('Open', Gtk.ResponseType.ACCEPT, 'Cancel', Gtk.ResponseType.CANCEL)
        input_file_chooser.set_size_request(1000, 700)
        input_file_chooser.set_select_multiple(True)
        input_file_chooser.connect('response', self._add_new_input)
        input_file_chooser.show()

    def _add_new_input(self, file_chooser_dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            threading.Thread(target=self.inputs_page_widgets.add_inputs,
                             args=(file_chooser_dialog.get_files(),),
                             daemon=True).start()

        file_chooser_dialog.close()
        file_chooser_dialog.destroy()

    def show_output_file_chooser(self, output_file_link_button, input_row):
        output_file_chooser = Gtk.FileChooserDialog(title='Save Output File Location',
                                                    action=Gtk.FileChooserAction.SAVE,
                                                    transient_for=self.main_window,
                                                    modal=True,
                                                    destroy_with_parent=True,
                                                    resizable=False)
        output_file_chooser.add_buttons('Save', Gtk.ResponseType.ACCEPT, 'Cancel', Gtk.ResponseType.CANCEL)
        output_file_chooser.set_size_request(1000, 700)
        output_file_chooser.set_current_folder(Gio.File.new_for_path(input_row.encoding_task.output_file.dir))
        output_file_chooser.set_current_name(input_row.encoding_task.output_file.get_name_and_extension())
        output_file_chooser.connect('response', self._set_new_output_file, input_row)
        output_file_chooser.show()

        return True

    def _set_new_output_file(self, file_chooser_dialog, response, input_row):
        if response == Gtk.ResponseType.ACCEPT:
            output_dir = file_chooser_dialog.get_current_folder().get_path()
            output_file_name = file_chooser_dialog.get_current_name()
            input_row.set_output_file_path_link(output_dir, output_file_name)

        file_chooser_dialog.close()
        file_chooser_dialog.destroy()

    def show_about_dialog(self, about_render_watch_button):
        self.options_popover.popdown()
        self.about_dialog.show()

    def show_preferences_window(self, settings_button):
        self.options_popover.popdown()
        self.preferences_window.show()

    class AboutDialog(Gtk.AboutDialog):
        def __init__(self, application: Gtk.Application, parent_window: Adw.ApplicationWindow):
            super().__init__(application=application,
                             transient_for=parent_window,
                             modal=True,
                             destroy_with_parent=True,
                             resizable=False,
                             hide_on_close=True,
                             title='About Render Watch')

            self.set_program_name('Render Watch')
            self.set_artists(['Laura Pluckhan: Render Watch Logo'])
            self.set_authors(['Michael Gregory: Founder, Lead Developer'])
            self.set_comments('Render Watch is an open source video transcoder for Linux.')
            self.set_copyright('Copyright 2020 - 2022')
            self.set_license_type(Gtk.License.GPL_3_0)
            self.set_version('v0.3.0-beta')
            self.set_website('https://github.com/mgregory1994/RenderWatch')
            self.set_website_label('GitHub')
            app_logo = Gdk.Texture.new_from_file(Gio.File.new_for_path('../src/render_watch/data/RenderWatch.png'))
            self.set_logo(app_logo)
            self.set_default_size(480, 380)

    class PreferencesWindow(Adw.PreferencesWindow):
        def __init__(self,
                     application: Gtk.Application,
                     parent_window: Adw.ApplicationWindow,
                     app_settings: app_preferences.Settings):
            super().__init__(application=application,
                             transient_for=parent_window,
                             modal=True,
                             destroy_with_parent=True,
                             resizable=False,
                             hide_on_close=True)

            self.app_settings = app_settings

            self._setup_general_settings_page()
            self._setup_encoder_settings_page()
            self._setup_watch_folder_settings_page()
            self.add(self.general_settings_page)
            self.add(self.encoder_settings_page)
            self.add(self.watch_folder_settings_page)

        def _setup_general_settings_page(self):
            self._setup_directories_group()

            self.general_settings_page = Adw.PreferencesPage()
            self.general_settings_page.set_name('general_settings')
            self.general_settings_page.set_title('General')
            self.general_settings_page.set_icon_name('preferences-system-symbolic')
            self.general_settings_page.add(self.directories_group)

        def _setup_directories_group(self):
            self._setup_output_directory_preferences_row()
            self._setup_temp_directory_preferences_row()
            self._setup_overwrite_outputs_widgets()

            self.directories_group = Adw.PreferencesGroup()
            self.directories_group.set_title('Directories')
            self.directories_group.set_description('Directories used by Render Watch')
            self.directories_group.set_header_suffix(self.overwrite_outputs_horizontal_box)
            self.directories_group.add(self.output_directory_row)
            self.directories_group.add(self.temp_directory_row)

        def _setup_output_directory_preferences_row(self):
            self.output_directory_title_label = Gtk.Label(label='Output Directory')
            self.output_directory_title_label.set_hexpand(True)
            self.output_directory_title_label.set_halign(Gtk.Align.START)
            self.output_directory_label = Gtk.Label(label=self.app_settings.output_directory)
            self.output_directory_label.set_sensitive(False)
            self.output_directory_file_chooser_button = Gtk.Button(icon_name='document-open-symbolic')
            self.output_directory_file_chooser_button.connect('clicked', self._show_output_directory_file_chooser)

            self.output_directory_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.output_directory_horizontal_box.append(self.output_directory_title_label)
            self.output_directory_horizontal_box.append(self.output_directory_label)
            self.output_directory_horizontal_box.append(self.output_directory_file_chooser_button)
            self.output_directory_horizontal_box.set_margin_top(10)
            self.output_directory_horizontal_box.set_margin_bottom(10)
            self.output_directory_horizontal_box.set_margin_end(10)
            self.output_directory_horizontal_box.set_margin_start(10)

            self.output_directory_row = Adw.PreferencesRow()
            self.output_directory_row.set_title('Output Directory')
            self.output_directory_row.set_child(self.output_directory_horizontal_box)

        def _setup_temp_directory_preferences_row(self):
            self.temp_directory_title_label = Gtk.Label(label='Temp Directory')
            self.temp_directory_title_label.set_hexpand(True)
            self.temp_directory_title_label.set_halign(Gtk.Align.START)
            self.temp_directory_label = Gtk.Label(label=self.app_settings.get_new_temp_directory())
            self.temp_directory_label.set_sensitive(False)
            self.temp_directory_file_chooser_button = Gtk.Button(icon_name='document-open-symbolic')
            self.temp_directory_file_chooser_button.connect('clicked', self._show_temp_directory_file_chooser)

            self.temp_directory_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.temp_directory_horizontal_box.append(self.temp_directory_title_label)
            self.temp_directory_horizontal_box.append(self.temp_directory_label)
            self.temp_directory_horizontal_box.append(self.temp_directory_file_chooser_button)
            self.temp_directory_horizontal_box.set_margin_top(10)
            self.temp_directory_horizontal_box.set_margin_bottom(10)
            self.temp_directory_horizontal_box.set_margin_end(10)
            self.temp_directory_horizontal_box.set_margin_start(10)

            self.temp_directory_row = Adw.PreferencesRow()
            self.temp_directory_row.set_title('Temp Directory')
            self.temp_directory_row.set_child(self.temp_directory_horizontal_box)

        def _setup_overwrite_outputs_widgets(self):
            self.overwrite_outputs_label = Gtk.Label(label='Overwrite Outputs')
            self.overwrite_outputs_switch = Gtk.Switch()
            self.overwrite_outputs_switch.set_vexpand(False)
            self.overwrite_outputs_switch.set_valign(Gtk.Align.CENTER)
            self.overwrite_outputs_switch.set_active(self.app_settings.is_overwriting_output_files)
            self.overwrite_outputs_switch.connect('state-set', self._save_overwrite_outputs_setting)

            self.overwrite_outputs_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.overwrite_outputs_horizontal_box.append(self.overwrite_outputs_label)
            self.overwrite_outputs_horizontal_box.append(self.overwrite_outputs_switch)

        def _setup_encoder_settings_page(self):
            self._setup_parallel_group()
            self._setup_parallel_nvenc_group()

            self.encoder_settings_page = Adw.PreferencesPage()
            self.encoder_settings_page.set_name('encoder_settings')
            self.encoder_settings_page.set_title('Encoder')
            self.encoder_settings_page.set_icon_name('view-list-symbolic')
            self.encoder_settings_page.add(self.parallel_group)
            self.encoder_settings_page.add(self.parallel_nvenc_group)

        def _setup_parallel_group(self):
            self._setup_x264_row()
            self._setup_x265_row()
            self._setup_vp9_row()

            self.parallel_group = Adw.PreferencesGroup()
            self.parallel_group.set_title('Parallel Tasks')
            self.parallel_group.set_description('Set the number of parallel tasks for each codec')
            self.parallel_group.add(self.x264_row)
            self.parallel_group.add(self.x265_row)
            self.parallel_group.add(self.vp9_row)

        def _setup_x264_row(self):
            x264_label = Gtk.Label(label='X264')
            x264_label.set_hexpand(True)
            x264_label.set_halign(Gtk.Align.START)
            self.x264_tasks_spinbutton = Gtk.SpinButton()
            self.x264_tasks_spinbutton.set_range(2, 8)
            self.x264_tasks_spinbutton.set_digits(0)
            self.x264_tasks_spinbutton.set_increments(1.0, 1.0)
            self.x264_tasks_spinbutton.set_value(self.app_settings.per_codec_x264)
            self.x264_tasks_spinbutton.set_numeric(True)
            self.x264_tasks_spinbutton.set_snap_to_ticks(True)
            self.x264_tasks_spinbutton.connect('value-changed', self._save_x264_per_codec_setting)

            x264_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            x264_horizontal_box.append(x264_label)
            x264_horizontal_box.append(self.x264_tasks_spinbutton)
            x264_horizontal_box.set_margin_top(10)
            x264_horizontal_box.set_margin_bottom(10)
            x264_horizontal_box.set_margin_start(10)
            x264_horizontal_box.set_margin_end(10)

            self.x264_row = Adw.PreferencesRow()
            self.x264_row.set_title('X264 Parallel Tasks')
            self.x264_row.set_child(x264_horizontal_box)

        def _setup_x265_row(self):
            x265_label = Gtk.Label(label='X265')
            x265_label.set_hexpand(True)
            x265_label.set_halign(Gtk.Align.START)
            self.x265_tasks_spinbutton = Gtk.SpinButton()
            self.x265_tasks_spinbutton.set_range(2, 8)
            self.x265_tasks_spinbutton.set_digits(0)
            self.x265_tasks_spinbutton.set_increments(1.0, 1.0)
            self.x265_tasks_spinbutton.set_value(self.app_settings.per_codec_x265)
            self.x265_tasks_spinbutton.set_numeric(True)
            self.x265_tasks_spinbutton.set_snap_to_ticks(True)
            self.x265_tasks_spinbutton.connect('value-changed', self._save_x265_per_codec_setting)

            x265_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            x265_horizontal_box.append(x265_label)
            x265_horizontal_box.append(self.x265_tasks_spinbutton)
            x265_horizontal_box.set_margin_top(10)
            x265_horizontal_box.set_margin_bottom(10)
            x265_horizontal_box.set_margin_start(10)
            x265_horizontal_box.set_margin_end(10)

            self.x265_row = Adw.PreferencesRow()
            self.x265_row.set_title('X265 Parallel Tasks')
            self.x265_row.set_child(x265_horizontal_box)

        def _setup_vp9_row(self):
            vp9_label = Gtk.Label(label='VP9')
            vp9_label.set_hexpand(True)
            vp9_label.set_halign(Gtk.Align.START)
            self.vp9_tasks_spinbutton = Gtk.SpinButton()
            self.vp9_tasks_spinbutton.set_range(2, 8)
            self.vp9_tasks_spinbutton.set_digits(0)
            self.vp9_tasks_spinbutton.set_increments(1.0, 1.0)
            self.vp9_tasks_spinbutton.set_value(self.app_settings.per_codec_vp9)
            self.vp9_tasks_spinbutton.set_numeric(True)
            self.vp9_tasks_spinbutton.set_snap_to_ticks(True)
            self.vp9_tasks_spinbutton.connect('value-changed', self._save_vp9_per_codec_setting)

            vp9_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            vp9_horizontal_box.append(vp9_label)
            vp9_horizontal_box.append(self.vp9_tasks_spinbutton)
            vp9_horizontal_box.set_margin_top(10)
            vp9_horizontal_box.set_margin_bottom(10)
            vp9_horizontal_box.set_margin_start(10)
            vp9_horizontal_box.set_margin_end(10)

            self.vp9_row = Adw.PreferencesRow()
            self.vp9_row.set_title('VP9 Parallel Tasks')
            self.vp9_row.set_child(vp9_horizontal_box)

        def _setup_parallel_nvenc_group(self):
            self._setup_parallel_nvenc_row()

            self.parallel_nvenc_switch = Gtk.Switch()
            self.parallel_nvenc_switch.set_vexpand(False)
            self.parallel_nvenc_switch.set_valign(Gtk.Align.CENTER)
            self.parallel_nvenc_switch.set_active(self.app_settings.is_nvenc_tasks_parallel)
            self.parallel_nvenc_switch.connect('state-set', self._save_parallel_nvenc_setting)

            self.parallel_nvenc_group = Adw.PreferencesGroup()
            self.parallel_nvenc_group.set_title('Parallel NVENC')
            self.parallel_nvenc_group.set_description('Set the number of parallel tasks for NVENC')
            self.parallel_nvenc_group.set_header_suffix(self.parallel_nvenc_switch)
            self.parallel_nvenc_group.add(self.nvenc_tasks_row)

        def _setup_parallel_nvenc_row(self):
            nvenc_tasks_label = Gtk.Label(label='NVENC Tasks')
            nvenc_tasks_label.set_hexpand(True)
            nvenc_tasks_label.set_halign(Gtk.Align.START)
            self.nvenc_tasks_spinbutton = Gtk.SpinButton()
            self.nvenc_tasks_spinbutton.set_range(2, 12)
            self.nvenc_tasks_spinbutton.set_digits(0)
            self.nvenc_tasks_spinbutton.set_increments(1.0, 1.0)
            self.nvenc_tasks_spinbutton.set_value(self.app_settings.parallel_nvenc_workers)
            self.nvenc_tasks_spinbutton.set_numeric(True)
            self.nvenc_tasks_spinbutton.set_snap_to_ticks(True)
            self.nvenc_tasks_spinbutton.connect('value-changed', self._save_parallel_nvenc_tasks_setting)

            nvenc_tasks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            nvenc_tasks_horizontal_box.append(nvenc_tasks_label)
            nvenc_tasks_horizontal_box.append(self.nvenc_tasks_spinbutton)
            nvenc_tasks_horizontal_box.set_margin_top(10)
            nvenc_tasks_horizontal_box.set_margin_bottom(10)
            nvenc_tasks_horizontal_box.set_margin_start(10)
            nvenc_tasks_horizontal_box.set_margin_end(10)

            self.nvenc_tasks_row = Adw.PreferencesRow()
            self.nvenc_tasks_row.set_title('NVENC Tasks')
            self.nvenc_tasks_row.set_child(nvenc_tasks_horizontal_box)
            self.nvenc_tasks_row.set_sensitive(self.app_settings.is_nvenc_tasks_parallel)

        def _setup_watch_folder_settings_page(self):
            self._setup_parallel_watch_folder_group()
            self._setup_watch_folder_tasks_group()

            self.watch_folder_settings_page = Adw.PreferencesPage()
            self.watch_folder_settings_page.set_name('watch_folder_settings')
            self.watch_folder_settings_page.set_title("Watch Folder")
            self.watch_folder_settings_page.set_icon_name('folder-symbolic')
            self.watch_folder_settings_page.add(self.watch_folder_tasks_group)
            self.watch_folder_settings_page.add(self.parallel_watch_folder_group)

        def _setup_parallel_watch_folder_group(self):
            self._setup_parallel_watch_folders_row()
            self._setup_wait_for_tasks_row()

            self.parallel_watch_folder_group = Adw.PreferencesGroup()
            self.parallel_watch_folder_group.set_title('Parallel Watch Folder')
            self.parallel_watch_folder_group.set_description('Parallel settings for watch folder tasks')
            self.parallel_watch_folder_group.add(self.parallel_watch_folders_row)
            self.parallel_watch_folder_group.add(self.wait_for_tasks_row)

        def _setup_parallel_watch_folders_row(self):
            parallel_watch_folders_title_label = Gtk.Label(label='Parallel Watch Folder Tasks')
            parallel_watch_folders_title_label.set_hexpand(True)
            parallel_watch_folders_title_label.set_halign(Gtk.Align.START)
            self.parallel_watch_folders_switch = Gtk.Switch()
            self.parallel_watch_folders_switch.set_vexpand(False)
            self.parallel_watch_folders_switch.set_valign(Gtk.Align.CENTER)
            self.parallel_watch_folders_switch.set_active(self.app_settings.is_encoding_parallel_watch_folders)
            self.parallel_watch_folders_switch.connect('state-set', self._save_parallel_watch_folders_setting)

            parallel_watch_folders_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            parallel_watch_folders_horizontal_box.append(parallel_watch_folders_title_label)
            parallel_watch_folders_horizontal_box.append(self.parallel_watch_folders_switch)
            parallel_watch_folders_horizontal_box.set_margin_top(10)
            parallel_watch_folders_horizontal_box.set_margin_bottom(10)
            parallel_watch_folders_horizontal_box.set_margin_start(10)
            parallel_watch_folders_horizontal_box.set_margin_end(10)

            self.parallel_watch_folders_row = Adw.PreferencesRow()
            self.parallel_watch_folders_row.set_title('Parallel Watch Folder')
            self.parallel_watch_folders_row.set_child(parallel_watch_folders_horizontal_box)

        def _setup_wait_for_tasks_row(self):
            wait_for_tasks_label = Gtk.Label(label='Wait For Other Running Tasks')
            wait_for_tasks_label.set_hexpand(True)
            wait_for_tasks_label.set_halign(Gtk.Align.START)
            self.wait_for_tasks_switch = Gtk.Switch()
            self.wait_for_tasks_switch.set_vexpand(False)
            self.wait_for_tasks_switch.set_valign(Gtk.Align.CENTER)
            self.wait_for_tasks_switch.set_active(self.app_settings.is_watch_folders_waiting_for_tasks)
            self.wait_for_tasks_switch.connect('state-set', self._save_watch_folders_wait_for_tasks_setting)

            wait_for_tasks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            wait_for_tasks_horizontal_box.append(wait_for_tasks_label)
            wait_for_tasks_horizontal_box.append(self.wait_for_tasks_switch)
            wait_for_tasks_horizontal_box.set_margin_top(10)
            wait_for_tasks_horizontal_box.set_margin_bottom(10)
            wait_for_tasks_horizontal_box.set_margin_start(10)
            wait_for_tasks_horizontal_box.set_margin_end(10)

            self.wait_for_tasks_row = Adw.PreferencesRow()
            self.wait_for_tasks_row.set_title('Watch Folder Wait For Tasks')
            self.wait_for_tasks_row.set_child(wait_for_tasks_horizontal_box)

        def _setup_watch_folder_tasks_group(self):
            self._setup_move_to_done_row()

            self.watch_folder_tasks_group = Adw.PreferencesGroup()
            self.watch_folder_tasks_group.set_title('Watch Folder Tasks')
            self.watch_folder_tasks_group.set_description('Watch folder task settings')
            self.watch_folder_tasks_group.add(self.move_to_done_row)

        def _setup_move_to_done_row(self):
            move_to_done_label = Gtk.Label(label='Move Completed Input Files to a Done Folder')
            move_to_done_label.set_hexpand(True)
            move_to_done_label.set_halign(Gtk.Align.START)
            self.move_to_done_switch = Gtk.Switch()
            self.move_to_done_switch.set_vexpand(False)
            self.move_to_done_switch.set_valign(Gtk.Align.CENTER)
            self.move_to_done_switch.set_active(self.app_settings.is_watch_folders_moving_to_done)
            self.move_to_done_switch.connect('state-set', self._save_watch_folders_move_to_done_setting)

            move_to_done_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            move_to_done_horizontal_box.append(move_to_done_label)
            move_to_done_horizontal_box.append(self.move_to_done_switch)
            move_to_done_horizontal_box.set_margin_top(10)
            move_to_done_horizontal_box.set_margin_bottom(10)
            move_to_done_horizontal_box.set_margin_start(10)
            move_to_done_horizontal_box.set_margin_end(10)

            self.move_to_done_row = Adw.PreferencesRow()
            self.move_to_done_row.set_title('Move Completed Input Files to a Done Folder')
            self.move_to_done_row.set_child(move_to_done_horizontal_box)

        def _set_parallel_nvenc_state(self, is_state_enabled: bool):
            self.nvenc_tasks_row.set_sensitive(is_state_enabled)

        def _show_output_directory_file_chooser(self, button):
            output_directory_file_chooser = Gtk.FileChooserDialog(title='Open Default Output Directory',
                                                                  action=Gtk.FileChooserAction.SELECT_FOLDER,
                                                                  transient_for=self,
                                                                  modal=True,
                                                                  destroy_with_parent=True,
                                                                  resizable=False)
            output_directory_file_chooser.add_buttons('Cancel', Gtk.ResponseType.REJECT)
            output_directory_file_chooser.add_buttons('Open', Gtk.ResponseType.ACCEPT)
            output_directory_file_chooser.set_file(Gio.File.new_for_path(self.app_settings.output_directory))
            output_directory_file_chooser.set_size_request(1000, 700)
            output_directory_file_chooser.connect('response', self._save_output_directory_setting)
            output_directory_file_chooser.show()

        def _show_temp_directory_file_chooser(self, button):
            temp_directory_file_chooser = Gtk.FileChooserDialog(title='Open Temp Directory',
                                                                action=Gtk.FileChooserAction.SELECT_FOLDER,
                                                                transient_for=self,
                                                                modal=True,
                                                                destroy_with_parent=True,
                                                                resizable=False)
            temp_directory_file_chooser.add_buttons('Cancel', Gtk.ResponseType.REJECT)
            temp_directory_file_chooser.add_buttons('Open', Gtk.ResponseType.ACCEPT)
            temp_directory_file_chooser.set_file(Gio.File.new_for_path(self.app_settings.temp_directory))
            temp_directory_file_chooser.set_size_request(1000, 700)
            temp_directory_file_chooser.connect('response', self._save_temp_directory_setting)
            temp_directory_file_chooser.show()

        def _save_output_directory_setting(self, file_chooser_dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                output_directory_path = file_chooser_dialog.get_file().get_path()
                self.output_directory_label.set_label(output_directory_path)
                self.app_settings.output_directory = output_directory_path

            file_chooser_dialog.close()
            file_chooser_dialog.destroy()

        def _save_overwrite_outputs_setting(self, switch, user_data):
            self.app_settings.is_overwriting_output_files = self.overwrite_outputs_switch.get_active()

        def _save_temp_directory_setting(self, file_chooser_dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                temp_directory_path = file_chooser_dialog.get_file().get_path()
                self.temp_directory_label.set_label(temp_directory_path)
                self.app_settings.temp_directory = temp_directory_path

            file_chooser_dialog.close()
            file_chooser_dialog.destroy()

        def _save_x264_per_codec_setting(self, spin_button):
            self.app_settings.per_codec_x264 = self.x264_tasks_spinbutton.get_value()

        def _save_x265_per_codec_setting(self, spin_button):
            self.app_settings.per_codec_x265 = self.x265_tasks_spinbutton.get_value()

        def _save_vp9_per_codec_setting(self, spin_button):
            self.app_settings.per_codec_vp9 = self.vp9_tasks_spinbutton.get_value()

        def _save_parallel_nvenc_setting(self, switch, user_data):
            self._set_parallel_nvenc_state(switch.get_active())
            self.app_settings.is_nvenc_tasks_parallel = self.parallel_nvenc_switch.get_active()

        def _save_parallel_nvenc_tasks_setting(self, spin_button):
            self.app_settings.parallel_nvenc_workers = self.nvenc_tasks_spinbutton.get_value()

        def _save_parallel_watch_folders_setting(self, switch, user_data):
            self.app_settings.is_encoding_parallel_watch_folders = self.parallel_watch_folders_switch.get_active()

        def _save_watch_folders_wait_for_tasks_setting(self, switch, user_data):
            self.app_settings.is_watch_folders_waiting_for_tasks = self.wait_for_tasks_switch.get_active()

        def _save_watch_folders_move_to_done_setting(self, switch, user_data):
            self.app_settings.is_watch_folders_moving_to_done = self.move_to_done_switch.get_active()
