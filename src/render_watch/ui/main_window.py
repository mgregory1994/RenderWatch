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


from render_watch.ui import Gtk, Gdk, Gio, GLib, Adw
from render_watch.ui import inputs_page, active_page, completed_page
from render_watch.encode import encoder_queue, preview, benchmark
from render_watch import app_preferences


class MainWindowWidgets:
    """Class that contains the widgets that make up the application's main window."""

    WINDOW_MIN_WIDTH = 1000
    WINDOW_MIN_HEIGHT = 690

    def __init__(self,
                 application: Adw.Application,
                 task_queue: encoder_queue.TaskQueue,
                 preview_generator: preview.PreviewGenerator,
                 benchmark_generator: benchmark.BenchmarkGenerator,
                 app_settings: app_preferences.Settings):
        """
        Initializes the MainWindowWidgets class with the necessary variables for creating the application's main window.

        Parameters:
            application: Adwaita application for Render Watch.
            task_queue: The encoder_queue.TaskQueue for sending encoding tasks to.
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
            app_settings: Application's settings.
        """
        self.application = application
        self.task_queue = task_queue
        self.preview_generator = preview_generator
        self.benchmark_generator = benchmark_generator
        self.app_settings = app_settings
        self.main_window = Adw.ApplicationWindow(application=application,
                                                 destroy_with_parent=True,
                                                 title='Render Watch')
        self.about_dialog = self.AboutDialog(self.application, self.main_window)
        self.preferences_window = self.PreferencesWindow(self.application, self.main_window, self.app_settings)

        self._setup_main_window()

        self.preview_generator.main_window = self.main_window

    def _setup_main_window(self):
        # Initializes all widgets for the main window and sets the state of the main window.
        self._setup_main_window_contents()

        self.main_window.set_size_request(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT)
        self.main_window.set_default_size(self.app_settings.window_width, self.app_settings.window_height)

        if self.app_settings.is_window_maximized:
            self.main_window.maximize()

        self.main_window.connect('close-request', self.on_main_window_close_request)

    def _setup_main_window_contents(self):
        # Initializes all main window widgets and sets them as the contents of the main window.
        self._setup_task_states_stack()
        self._setup_task_states_view_switcher()
        self._setup_add_inputs_widgets()
        self._setup_options_menu_button()
        self._setup_settings_sidebar_button()
        self._setup_header_bar()

        main_window_contents_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_window_contents_vertical_box.append(self.header_bar)
        main_window_contents_vertical_box.append(self.task_states_stack)

        self.main_window.set_content(main_window_contents_vertical_box)

    def _setup_task_states_stack(self):
        # Setup task state pages using an view stack.
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
        self.task_states_stack.connect('notify', self.on_task_states_stack_notify)

    def _setup_inputs_page_widgets(self):
        # Initializes the inputs page's widgets.
        self.inputs_page_widgets = inputs_page.InputsPageWidgets(self,
                                                                 self.preview_generator,
                                                                 self.benchmark_generator,
                                                                 self.app_settings)

    def _setup_active_page_widgets(self):
        # Initializes the active page's widgets.
        self.active_page_widgets = active_page.ActivePageWidgets()

    def _setup_completed_page_widgets(self):
        # Initializes the completed page's widgets.
        self.completed_page_widgets = completed_page.CompletedPageWidgets()

    def _setup_task_states_view_switcher(self):
        # Initializes the task states view switcher for the header bar.
        self.task_states_view_switcher = Adw.ViewSwitcher()
        self.task_states_view_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        self.task_states_view_switcher.set_stack(self.task_states_stack)

    def _setup_add_inputs_widgets(self):
        # Initializes the widgets related to adding an input for the header bar.
        self._setup_add_inputs_button()
        self._setup_input_type_combobox()

        self.add_inputs_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add_inputs_horizontal_box.append(self.add_button)
        self.add_inputs_horizontal_box.append(self.input_type_combobox)
        self.add_inputs_horizontal_box.add_css_class('linked')

    def _setup_add_inputs_button(self):
        # Initializes the add inputs button.
        self.add_button = Gtk.Button(label='Add')
        self.add_button.connect('clicked', self.on_add_button_clicked)
        self.add_button.add_css_class('suggested-action')

    def _setup_input_type_combobox(self):
        # Initializes the input type combobox.
        self.input_type_combobox = Gtk.ComboBoxText()
        self.input_type_combobox.append_text('Files')
        self.input_type_combobox.append_text('Folders')
        self.input_type_combobox.set_active(0)
        self.input_type_combobox.connect('changed', self.on_input_type_combobox_changed)

    def _setup_options_menu_button(self):
        # Initializes the options menu button and the popover tied to the menu button.
        self._setup_page_popover_options()
        self._setup_options_menu_popover_contents()
        self._setup_options_popover()

        self.options_menu_button = Gtk.MenuButton()
        self.options_menu_button.set_icon_name('open-menu-symbolic')
        self.options_menu_button.set_popover(self.options_popover)

    def _setup_page_popover_options(self):
        # Initializes the options menu's popover contents for each task states page.
        self.page_popover_options_stack = Adw.ViewStack()
        self.page_popover_options_stack.add_named(self.inputs_page_widgets.popover_options_vertical_box, 'inputs_page')
        self.page_popover_options_stack.add_named(self.active_page_widgets.popover_options_vertical_box, 'active_page')
        self.page_popover_options_stack.add_named(self.completed_page_widgets.popover_options_vertical_box,
                                                  'completed_page')
        self.page_popover_options_stack.set_vhomogeneous(False)

    def _setup_options_menu_popover_contents(self):
        # Initializes the options menu's popover contents.
        self._setup_application_settings_button()
        self._setup_about_button()

        self.options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.options_vertical_box.append(self.page_popover_options_stack)
        self.options_vertical_box.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.options_vertical_box.append(self.settings_button)
        self.options_vertical_box.append(self.about_button)
        self.options_vertical_box.set_margin_start(5)
        self.options_vertical_box.set_margin_end(5)
        self.options_vertical_box.set_margin_top(5)
        self.options_vertical_box.set_margin_bottom(5)

    def _setup_application_settings_button(self):
        # Initializes the application settings button for the options menu popover.
        self.settings_button = Gtk.Button(label='Settings')
        self.settings_button.connect('clicked', self.on_settings_button_clicked)

    def _setup_about_button(self):
        # Initializes the about button for the options menu popover.
        self.about_button = Gtk.Button(label='About Render Watch')
        self.about_button.connect('clicked', self.on_about_button_clicked)

    def _setup_options_popover(self):
        # Initializes the options menu's popover.
        self.options_popover = Gtk.Popover()
        self.options_popover.set_child(self.options_vertical_box)

    def _setup_settings_sidebar_button(self):
        # Initializes the settings sidebar button for the header bar.
        self.toggle_settings_sidebar_button = Gtk.Button()
        self.toggle_settings_sidebar_button.set_icon_name('view-dual-symbolic')
        self.toggle_settings_sidebar_button.set_sensitive(False)
        self.toggle_settings_sidebar_button.connect('clicked', self.inputs_page_widgets.toggle_settings_sidebar)

    def _setup_header_bar(self):
        # Initializes the header bar for the application window.
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_title_widget(self.task_states_view_switcher)
        self.header_bar.pack_start(self.add_inputs_horizontal_box)
        self.header_bar.pack_end(self.options_menu_button)
        self.header_bar.pack_end(self.toggle_settings_sidebar_button)

    def is_folder_input_type(self):
        """
        Returns whether the input type is set to 'Folders' for adding inputs.

        Returns:
            Boolean that represents whether the input type is set to 'Folders'.
        """
        return self.input_type_combobox.get_active_text() == 'Folders'

    def set_adding_inputs_state(self, is_state_enabled: bool):
        """
        Sets the state of the main window's widgets to show when the user is importing new inputs.

        Parameters:
            is_state_enabled: Boolean that represents whether we are enabling this state.
        """
        self.add_button.set_sensitive(not is_state_enabled)
        self.input_type_combobox.set_sensitive(not is_state_enabled)
        self.options_menu_button.set_sensitive(not is_state_enabled)

    def on_main_window_close_request(self, user_data):
        """
        Signal callback function for the main window's 'close-request' signal. Saves the state of the application window
        and quits the application.

        Parameters:
            user_data: Additional data passed by the signal (not used).
        """
        window_width, window_height = self.main_window.get_default_size()
        self.app_settings.window_width = window_width
        self.app_settings.window_height = window_height
        self.app_settings.is_window_maximized = self.main_window.is_maximized()

        self.application.quit()

    def on_task_states_stack_notify(self, property, user_data):
        """
        Signal callback function for the task state stack's 'notify' signal. Changes the options menu's popover's
        contents to match the visible page of the task states stack.

        Parameters:
            property: Property that emitted the notify signal (not used).
            user_data: Additional data passed by the signal (not used).
        """
        try:
            if self.task_states_stack.get_visible_child_name() != self.page_popover_options_stack.get_visible_child_name():
                self.page_popover_options_stack.set_visible_child_name(self.task_states_stack.get_visible_child_name())
        except AttributeError:
            pass

    def on_add_button_clicked(self, button):
        """
        Signal callback function for the add button's 'clicked' signal.
        Opens a file chooser so that the user can choose new inputs to add.

        Parameters:
            button: Gtk.Button that emitted the signal (not used).
        """
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
        # Imports the files selected with the file chooser if the response is accepted.
        if response == Gtk.ResponseType.ACCEPT:
            threading.Thread(target=self.inputs_page_widgets.add_inputs,
                             args=(file_chooser_dialog.get_files(),),
                             daemon=True).start()

        file_chooser_dialog.close()
        file_chooser_dialog.destroy()

    def on_output_path_link_button_activate_link(self, link_button, input_row):
        """
        Signal callback function for the input row's output path link button's 'activate-link' signal.
        Opens a file chooser that allows the user to change the output directory for the input row.

        Parameters:
            link_button: Gtk.LinkButton that emitted the 'activate-link' signal (not used).
            input_row: Input row that the link button belongs to.
        """
        if input_row.encoding_task.input_file.is_folder:
            action = Gtk.FileChooserAction.SELECT_FOLDER
        else:
            action = Gtk.FileChooserAction.SAVE

        output_file_chooser = Gtk.FileChooserDialog(title='Save Output File Location',
                                                    action=action,
                                                    transient_for=self.main_window,
                                                    modal=True,
                                                    destroy_with_parent=True,
                                                    resizable=False)
        output_file_chooser.add_buttons('Save', Gtk.ResponseType.ACCEPT, 'Cancel', Gtk.ResponseType.CANCEL)
        output_file_chooser.set_size_request(1000, 700)
        output_file_chooser.set_current_folder(Gio.File.new_for_path(input_row.encoding_task.output_file.dir))

        if not input_row.encoding_task.input_file.is_folder:
            output_file_chooser.set_current_name(input_row.encoding_task.output_file.get_name_and_extension())

        output_file_chooser.connect('response', self._set_new_output_file, input_row)
        output_file_chooser.show()

        return True  # Overrides link button's default signal callback and uses this one instead.

    @staticmethod
    def _set_new_output_file(file_chooser_dialog, response, input_row):
        # Sets the output directory of the input row using the file chooser's directory if the response is accepted.
        if response == Gtk.ResponseType.ACCEPT:
            output_dir = file_chooser_dialog.get_current_folder().get_path()
            output_file_name = file_chooser_dialog.get_current_name()
            input_row.set_output_file_path_link(output_dir, output_file_name)

        file_chooser_dialog.close()
        file_chooser_dialog.destroy()

    def show_remove_all_confirmation_message(self):
        """Shows a message dialog confirming with the user to remove all inputs."""
        message_text = 'Remove All Inputs'
        message_secondary_text = 'Do you want to remove all inputs?'
        remove_all_confirmation_message_dialog = Gtk.MessageDialog(transient_for=self.main_window,
                                                                   modal=True,
                                                                   destroy_with_parent=True,
                                                                   buttons=Gtk.ButtonsType.YES_NO,
                                                                   text=message_text,
                                                                   secondary_text=message_secondary_text)
        remove_all_confirmation_message_dialog.connect(
            'response',
            self.inputs_page_widgets.on_remove_all_confirmation_message_response
        )
        remove_all_confirmation_message_dialog.show()

    def on_input_type_combobox_changed(self, combobox):
        """
        Signal callback function for the input type combobox' 'changed' signal.
        Sets the state of the inputs page's widgets to reflect if files or folders are going to be imported.

        Parameters:
            combobox: Gtk.Combobox that emitted the 'changed' signal.
        """
        if combobox.get_active_text() == 'Files':
            self.inputs_page_widgets.set_input_type_state(is_file_state_enabled=True)
        else:
            self.inputs_page_widgets.set_input_type_state()

    def on_settings_button_clicked(self, button):
        """
        Signal callback function for the settings button's 'clicked' signal.
        Shows the application's preferences window.

        Parameters:
            button: Gtk.Button that emitted the 'clicked' signal.
        """
        self.options_popover.popdown()
        self.preferences_window.show()

    def on_about_button_clicked(self, button):
        """
        Signal callback function for the about button's 'clicked' signal.
        Shows the application's about dialog.

        Parameters:
            button: Gtk.Button that emitted the 'clicked' signal.
        """
        self.options_popover.popdown()
        self.about_dialog.show()

    def on_inputs_list_box_row_selected(self, input_row, user_data=None):
        """
        Signal callback function for the inputs list box row's 'selected' signal.
        Toggles the sensitivity of the toggle settings sidebar button.

        Parameters:
            input_row: Gtk.ListboxRow that emitted the 'selected' signal.
            user_data: Additional data passed by the signal (not used).
        """
        self.toggle_settings_sidebar_button.set_sensitive(input_row is not None)

    class AboutDialog(Gtk.AboutDialog):
        """Class that contains the widgets that make up the application's about dialog."""

        def __init__(self, application: Adw.Application, parent_window: Adw.ApplicationWindow):
            """
            Initializes the AboutDialog class with the necessary variables for creating the application's about dialog.

            Parameters:
                application: Adwaita application for Render Watch.
                parent_window: Application's main window.
            """
            super().__init__(application=application,
                             transient_for=parent_window,
                             modal=True,
                             destroy_with_parent=True,
                             resizable=False,
                             hide_on_close=True,
                             title='About Render Watch')

            self._setup_application_name()
            self._setup_artists()
            self._setup_authors()
            self._setup_comments()
            self._setup_copyright()
            self._setup_version()
            self._setup_website()
            self._setup_logo()

            self.set_default_size(480, 380)

        def _setup_application_name(self):
            # Sets the program name
            self.set_program_name('Render Watch')

        def _setup_artists(self):
            # Sets the credits for the artists.
            self.set_artists(['Laura Pluckhan: Render Watch Logo'])

        def _setup_authors(self):
            # Sets the credits for the authors.
            self.set_authors(['Michael Gregory: Founder, Lead Developer'])

        def _setup_comments(self):
            # Sets the application's description summary.
            self.set_comments('Render Watch is an open source video transcoder for Linux.')

        def _setup_copyright(self):
            # Sets the copyright information.
            self.set_copyright('Copyright 2020 - 2022')
            self.set_license_type(Gtk.License.GPL_3_0)

        def _setup_version(self):
            # Sets the version.
            self.set_version('v0.3.0-beta')

        def _setup_website(self):
            # Sets the website link.
            self.set_website('https://github.com/mgregory1994/RenderWatch')
            self.set_website_label('GitHub')

        def _setup_logo(self):
            # Sets the application's logo.
            app_logo = Gdk.Texture.new_from_file(Gio.File.new_for_path('../src/render_watch/data/RenderWatch.png'))
            self.set_logo(app_logo)

    class PreferencesWindow(Adw.PreferencesWindow):
        """Class that contains the widgets that make up the application's preferences window."""

        def __init__(self,
                     application: Gtk.Application,
                     parent_window: Adw.ApplicationWindow,
                     app_settings: app_preferences.Settings):
            """
            Initializes the PreferencesWindow class with the necessary variables for creating the
            application's preferences window.

            Parameters:
                application: Adwaita application for Render Watch.
                parent_window: Adwaita ApplicationWindow to use as the parent window.
                app_settings: Application's settings.
            """
            super().__init__(application=application,
                             transient_for=parent_window,
                             modal=True,
                             destroy_with_parent=True,
                             resizable=False,
                             hide_on_close=True,
                             title='Render Watch Settings')

            self.app_settings = app_settings

            self._setup_preferences_window()

        def _setup_preferences_window(self):
            # Initializes all widgets for the preferences window and adds them to the preferences window.
            self._setup_general_settings_page()
            self._setup_encoder_settings_page()
            self._setup_watch_folder_settings_page()
            self.add(self.general_settings_page)
            self.add(self.encoder_settings_page)
            self.add(self.watch_folder_settings_page)

        def _setup_general_settings_page(self):
            # Initializes the general settings page widgets.
            self._setup_directories_group()

            self.general_settings_page = Adw.PreferencesPage()
            self.general_settings_page.set_name('general_settings')
            self.general_settings_page.set_title('General')
            self.general_settings_page.set_icon_name('preferences-system-symbolic')
            self.general_settings_page.add(self.directories_group)

        def _setup_directories_group(self):
            # Initializes the directory settings widgets.
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
            # Initializes the output directory setting widgets.
            self._setup_output_directory_title_label()
            self._setup_output_directory_label()
            self._setup_output_directory_file_chooser_button()

            output_directory_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            output_directory_horizontal_box.append(self.output_directory_title_label)
            output_directory_horizontal_box.append(self.output_directory_label)
            output_directory_horizontal_box.append(self.output_directory_file_chooser_button)
            output_directory_horizontal_box.set_margin_top(10)
            output_directory_horizontal_box.set_margin_bottom(10)
            output_directory_horizontal_box.set_margin_end(10)
            output_directory_horizontal_box.set_margin_start(10)

            self.output_directory_row = Adw.PreferencesRow()
            self.output_directory_row.set_title('Output Directory')
            self.output_directory_row.set_child(output_directory_horizontal_box)

        def _setup_output_directory_title_label(self):
            # Initializes the output directory title label.
            self.output_directory_title_label = Gtk.Label(label='Output Directory')
            self.output_directory_title_label.set_hexpand(True)
            self.output_directory_title_label.set_halign(Gtk.Align.START)

        def _setup_output_directory_label(self):
            # Initializes the output directory label.
            self.output_directory_label = Gtk.Label(label=self.app_settings.output_directory)
            self.output_directory_label.set_sensitive(False)

        def _setup_output_directory_file_chooser_button(self):
            # Initializes the output directory file chooser button.
            self.output_directory_file_chooser_button = Gtk.Button(icon_name='document-open-symbolic')
            self.output_directory_file_chooser_button.connect('clicked',
                                                              self.on_output_directory_file_chooser_button_clicked)

        def _setup_temp_directory_preferences_row(self):
            # Initializes the temp directory setting widgets.
            self._setup_temp_directory_title_label()
            self._setup_temp_directory_label()
            self._setup_temp_directory_file_chooser_button()

            temp_directory_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            temp_directory_horizontal_box.append(self.temp_directory_title_label)
            temp_directory_horizontal_box.append(self.temp_directory_label)
            temp_directory_horizontal_box.append(self.temp_directory_file_chooser_button)
            temp_directory_horizontal_box.set_margin_top(10)
            temp_directory_horizontal_box.set_margin_bottom(10)
            temp_directory_horizontal_box.set_margin_end(10)
            temp_directory_horizontal_box.set_margin_start(10)

            self.temp_directory_row = Adw.PreferencesRow()
            self.temp_directory_row.set_title('Temp Directory')
            self.temp_directory_row.set_child(temp_directory_horizontal_box)

        def _setup_temp_directory_title_label(self):
            # Initializes the temp directory title label.
            self.temp_directory_title_label = Gtk.Label(label='Temp Directory')
            self.temp_directory_title_label.set_hexpand(True)
            self.temp_directory_title_label.set_halign(Gtk.Align.START)

        def _setup_temp_directory_label(self):
            # Initializes the temp directory label.
            self.temp_directory_label = Gtk.Label(label=self.app_settings.get_new_temp_directory())
            self.temp_directory_label.set_sensitive(False)

        def _setup_temp_directory_file_chooser_button(self):
            # Initializes the temp directory file chooser button.
            self.temp_directory_file_chooser_button = Gtk.Button(icon_name='document-open-symbolic')
            self.temp_directory_file_chooser_button.connect('clicked',
                                                            self.on_temp_directory_file_chooser_button_clicked)

        def _setup_overwrite_outputs_widgets(self):
            # Initializes the overwrite outputs setting widgets.
            self._setup_overwrite_outputs_switch()

            overwrite_outputs_label = Gtk.Label(label='Overwrite Outputs')

            self.overwrite_outputs_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.overwrite_outputs_horizontal_box.append(overwrite_outputs_label)
            self.overwrite_outputs_horizontal_box.append(self.overwrite_outputs_switch)

        def _setup_overwrite_outputs_switch(self):
            # Initializes the overwrite outputs switch.
            self.overwrite_outputs_switch = Gtk.Switch()
            self.overwrite_outputs_switch.set_vexpand(False)
            self.overwrite_outputs_switch.set_valign(Gtk.Align.CENTER)
            self.overwrite_outputs_switch.set_active(self.app_settings.is_overwriting_output_files)
            self.overwrite_outputs_switch.connect('state-set', self.on_overwrite_outputs_switch_state_set)

        def _setup_encoder_settings_page(self):
            # Initializes the encoder settings page widgets.
            self._setup_parallel_group()
            self._setup_parallel_nvenc_group()

            self.encoder_settings_page = Adw.PreferencesPage()
            self.encoder_settings_page.set_name('encoder_settings')
            self.encoder_settings_page.set_title('Encoder')
            self.encoder_settings_page.set_icon_name('view-list-symbolic')
            self.encoder_settings_page.add(self.parallel_group)
            self.encoder_settings_page.add(self.parallel_nvenc_group)

        def _setup_parallel_group(self):
            # Initializes the parallel encoding setting widgets.
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
            # Initializes the parallel encoding setting widgets for x264.
            self._setup_x264_label()
            self._setup_x264_tasks_spin_button()

            x264_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            x264_horizontal_box.append(self.x264_label)
            x264_horizontal_box.append(self.x264_tasks_spin_button)
            x264_horizontal_box.set_margin_top(10)
            x264_horizontal_box.set_margin_bottom(10)
            x264_horizontal_box.set_margin_start(10)
            x264_horizontal_box.set_margin_end(10)

            self.x264_row = Adw.PreferencesRow()
            self.x264_row.set_title('X264 Parallel Tasks')
            self.x264_row.set_child(x264_horizontal_box)

        def _setup_x264_label(self):
            # Initializes the x264 label.
            self.x264_label = Gtk.Label(label='X264')
            self.x264_label.set_hexpand(True)
            self.x264_label.set_halign(Gtk.Align.START)

        def _setup_x264_tasks_spin_button(self):
            # Initializes the x264 tasks spin button.
            self.x264_tasks_spin_button = Gtk.SpinButton()
            self.x264_tasks_spin_button.set_value(self.app_settings.per_codec_x264)
            self.x264_tasks_spin_button.set_range(self.app_settings.TASK_MIN, self.app_settings.TASK_MAX)
            self.x264_tasks_spin_button.set_digits(0)
            self.x264_tasks_spin_button.set_increments(1.0, 1.0)
            self.x264_tasks_spin_button.set_numeric(True)
            self.x264_tasks_spin_button.set_snap_to_ticks(True)
            self.x264_tasks_spin_button.connect('value-changed', self.on_x264_tasks_spin_button_value_changed)

        def _setup_x265_row(self):
            # Initializes the parallel encoding setting widgets for x265.
            self._setup_x265_label()
            self._setup_x265_tasks_spin_button()

            x265_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            x265_horizontal_box.append(self.x265_label)
            x265_horizontal_box.append(self.x265_tasks_spin_button)
            x265_horizontal_box.set_margin_top(10)
            x265_horizontal_box.set_margin_bottom(10)
            x265_horizontal_box.set_margin_start(10)
            x265_horizontal_box.set_margin_end(10)

            self.x265_row = Adw.PreferencesRow()
            self.x265_row.set_title('X265 Parallel Tasks')
            self.x265_row.set_child(x265_horizontal_box)

        def _setup_x265_label(self):
            # Initializes the x265 label.
            self.x265_label = Gtk.Label(label='X265')
            self.x265_label.set_hexpand(True)
            self.x265_label.set_halign(Gtk.Align.START)

        def _setup_x265_tasks_spin_button(self):
            # Initializes the x265 tasks spin button.
            self.x265_tasks_spin_button = Gtk.SpinButton()
            self.x265_tasks_spin_button.set_value(self.app_settings.per_codec_x265)
            self.x265_tasks_spin_button.set_range(self.app_settings.TASK_MIN, self.app_settings.TASK_MAX)
            self.x265_tasks_spin_button.set_digits(0)
            self.x265_tasks_spin_button.set_increments(1.0, 1.0)
            self.x265_tasks_spin_button.set_numeric(True)
            self.x265_tasks_spin_button.set_snap_to_ticks(True)
            self.x265_tasks_spin_button.connect('value-changed', self.on_x265_tasks_spin_button_value_changed)

        def _setup_vp9_row(self):
            # Initializes the parallel encoding setting widgets for VP9.
            self._setup_vp9_label()
            self._setup_vp9_tasks_spin_button()

            vp9_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            vp9_horizontal_box.append(self.vp9_label)
            vp9_horizontal_box.append(self.vp9_tasks_spin_button)
            vp9_horizontal_box.set_margin_top(10)
            vp9_horizontal_box.set_margin_bottom(10)
            vp9_horizontal_box.set_margin_start(10)
            vp9_horizontal_box.set_margin_end(10)

            self.vp9_row = Adw.PreferencesRow()
            self.vp9_row.set_title('VP9 Parallel Tasks')
            self.vp9_row.set_child(vp9_horizontal_box)

        def _setup_vp9_label(self):
            # Initializes the VP9 label.
            self.vp9_label = Gtk.Label(label='VP9')
            self.vp9_label.set_hexpand(True)
            self.vp9_label.set_halign(Gtk.Align.START)

        def _setup_vp9_tasks_spin_button(self):
            # Initializes the VP9 tasks spin button.
            self.vp9_tasks_spin_button = Gtk.SpinButton()
            self.vp9_tasks_spin_button.set_value(self.app_settings.per_codec_vp9)
            self.vp9_tasks_spin_button.set_range(self.app_settings.TASK_MIN, self.app_settings.TASK_MAX)
            self.vp9_tasks_spin_button.set_digits(0)
            self.vp9_tasks_spin_button.set_increments(1.0, 1.0)
            self.vp9_tasks_spin_button.set_numeric(True)
            self.vp9_tasks_spin_button.set_snap_to_ticks(True)
            self.vp9_tasks_spin_button.connect('value-changed', self.on_vp9_tasks_spin_button_value_changed)

        def _setup_parallel_nvenc_group(self):
            # Initializes the parallel nvenc settings widgets.
            self._setup_parallel_nvenc_row()
            self._setup_parallel_nvenc_switch()

            self.parallel_nvenc_group = Adw.PreferencesGroup()
            self.parallel_nvenc_group.set_title('Parallel NVENC')
            self.parallel_nvenc_group.set_description('Set the number of parallel tasks for NVENC')
            self.parallel_nvenc_group.set_header_suffix(self.parallel_nvenc_switch)
            self.parallel_nvenc_group.add(self.nvenc_tasks_row)

        def _setup_parallel_nvenc_row(self):
            # Initializes the parallel nvenc tasks setting widgets.
            self._setup_nvenc_tasks_label()
            self._setup_nvenc_tasks_spin_button()

            nvenc_tasks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            nvenc_tasks_horizontal_box.append(self.nvenc_tasks_label)
            nvenc_tasks_horizontal_box.append(self.nvenc_tasks_spin_button)
            nvenc_tasks_horizontal_box.set_margin_top(10)
            nvenc_tasks_horizontal_box.set_margin_bottom(10)
            nvenc_tasks_horizontal_box.set_margin_start(10)
            nvenc_tasks_horizontal_box.set_margin_end(10)

            self.nvenc_tasks_row = Adw.PreferencesRow()
            self.nvenc_tasks_row.set_title('NVENC Tasks')
            self.nvenc_tasks_row.set_child(nvenc_tasks_horizontal_box)
            self.nvenc_tasks_row.set_sensitive(self.app_settings.is_nvenc_tasks_parallel)

        def _setup_nvenc_tasks_label(self):
            # Initializes the nvenc tasks label.
            self.nvenc_tasks_label = Gtk.Label(label='NVENC Tasks')
            self.nvenc_tasks_label.set_hexpand(True)
            self.nvenc_tasks_label.set_halign(Gtk.Align.START)

        def _setup_nvenc_tasks_spin_button(self):
            # Initializes the nvenc tasks spin button.
            self.nvenc_tasks_spin_button = Gtk.SpinButton()
            self.nvenc_tasks_spin_button.set_value(self.app_settings.parallel_nvenc_workers)
            self.nvenc_tasks_spin_button.set_range(self.app_settings.NVENC_TASK_MIN, self.app_settings.NVENC_TASK_MAX)
            self.nvenc_tasks_spin_button.set_digits(0)
            self.nvenc_tasks_spin_button.set_increments(1.0, 1.0)
            self.nvenc_tasks_spin_button.set_numeric(True)
            self.nvenc_tasks_spin_button.set_snap_to_ticks(True)
            self.nvenc_tasks_spin_button.connect('value-changed', self.on_nvenc_tasks_spin_button_value_changed)

        def _setup_parallel_nvenc_switch(self):
            # Initializes the parallel nvenc switch.
            self.parallel_nvenc_switch = Gtk.Switch()
            self.parallel_nvenc_switch.set_active(self.app_settings.is_nvenc_tasks_parallel)
            self.parallel_nvenc_switch.set_vexpand(False)
            self.parallel_nvenc_switch.set_valign(Gtk.Align.CENTER)
            self.parallel_nvenc_switch.connect('state-set', self.on_parallel_nvenc_switch_state_set)

        def _setup_watch_folder_settings_page(self):
            # Initializes the watch folder settings widgets.
            self._setup_parallel_watch_folder_group()
            self._setup_watch_folder_tasks_group()

            self.watch_folder_settings_page = Adw.PreferencesPage()
            self.watch_folder_settings_page.set_name('watch_folder_settings')
            self.watch_folder_settings_page.set_title("Watch Folder")
            self.watch_folder_settings_page.set_icon_name('folder-symbolic')
            self.watch_folder_settings_page.add(self.watch_folder_tasks_group)
            self.watch_folder_settings_page.add(self.parallel_watch_folder_group)

        def _setup_parallel_watch_folder_group(self):
            # Initializes the parallel watch folders settings widgets.
            self._setup_parallel_watch_folders_row()
            self._setup_wait_for_tasks_row()

            self.parallel_watch_folder_group = Adw.PreferencesGroup()
            self.parallel_watch_folder_group.set_title('Parallel Watch Folder')
            self.parallel_watch_folder_group.set_description('Parallel settings for watch folder tasks')
            self.parallel_watch_folder_group.add(self.parallel_watch_folders_row)
            self.parallel_watch_folder_group.add(self.wait_for_tasks_row)

        def _setup_parallel_watch_folders_row(self):
            # Initializes the parallel watch folders setting widgets.
            self._setup_parallel_watch_folders_title_label()
            self._setup_parallel_watch_folders_switch()

            parallel_watch_folders_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            parallel_watch_folders_horizontal_box.append(self.parallel_watch_folders_title_label)
            parallel_watch_folders_horizontal_box.append(self.parallel_watch_folders_switch)
            parallel_watch_folders_horizontal_box.set_margin_top(10)
            parallel_watch_folders_horizontal_box.set_margin_bottom(10)
            parallel_watch_folders_horizontal_box.set_margin_start(10)
            parallel_watch_folders_horizontal_box.set_margin_end(10)

            self.parallel_watch_folders_row = Adw.PreferencesRow()
            self.parallel_watch_folders_row.set_title('Parallel Watch Folder')
            self.parallel_watch_folders_row.set_child(parallel_watch_folders_horizontal_box)

        def _setup_parallel_watch_folders_title_label(self):
            # Initializes the parallel watch folders title label.
            self.parallel_watch_folders_title_label = Gtk.Label(label='Parallel Watch Folder Tasks')
            self.parallel_watch_folders_title_label.set_hexpand(True)
            self.parallel_watch_folders_title_label.set_halign(Gtk.Align.START)

        def _setup_parallel_watch_folders_switch(self):
            # Initializes the parallel watch folders switch.
            self.parallel_watch_folders_switch = Gtk.Switch()
            self.parallel_watch_folders_switch.set_active(self.app_settings.is_encoding_parallel_watch_folders)
            self.parallel_watch_folders_switch.set_vexpand(False)
            self.parallel_watch_folders_switch.set_valign(Gtk.Align.CENTER)
            self.parallel_watch_folders_switch.connect('state-set', self.on_parallel_watch_folders_switch_state_set)

        def _setup_wait_for_tasks_row(self):
            # Initializes the watch folders wait for tasks setting widgets.
            self._setup_wait_for_tasks_label()
            self._setup_wait_for_tasks_switch()

            wait_for_tasks_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            wait_for_tasks_horizontal_box.append(self.wait_for_tasks_label)
            wait_for_tasks_horizontal_box.append(self.wait_for_tasks_switch)
            wait_for_tasks_horizontal_box.set_margin_top(10)
            wait_for_tasks_horizontal_box.set_margin_bottom(10)
            wait_for_tasks_horizontal_box.set_margin_start(10)
            wait_for_tasks_horizontal_box.set_margin_end(10)

            self.wait_for_tasks_row = Adw.PreferencesRow()
            self.wait_for_tasks_row.set_title('Watch Folder Wait For Tasks')
            self.wait_for_tasks_row.set_child(wait_for_tasks_horizontal_box)

        def _setup_wait_for_tasks_label(self):
            # Initializes the wait for tasks label.
            self.wait_for_tasks_label = Gtk.Label(label='Wait For Other Running Tasks')
            self.wait_for_tasks_label.set_hexpand(True)
            self.wait_for_tasks_label.set_halign(Gtk.Align.START)

        def _setup_wait_for_tasks_switch(self):
            # Initializes the wait for tasks switch.
            self.wait_for_tasks_switch = Gtk.Switch()
            self.wait_for_tasks_switch.set_active(self.app_settings.is_watch_folders_waiting_for_tasks)
            self.wait_for_tasks_switch.set_vexpand(False)
            self.wait_for_tasks_switch.set_valign(Gtk.Align.CENTER)
            self.wait_for_tasks_switch.connect('state-set', self.on_wait_for_tasks_switch_state_set)

        def _setup_watch_folder_tasks_group(self):
            # Initializes the watch folder task settings widgets.
            self._setup_move_to_done_row()

            self.watch_folder_tasks_group = Adw.PreferencesGroup()
            self.watch_folder_tasks_group.set_title('Watch Folder Tasks')
            self.watch_folder_tasks_group.set_description('Watch folder task settings')
            self.watch_folder_tasks_group.add(self.move_to_done_row)

        def _setup_move_to_done_row(self):
            # Initializes the move finished tasks to done folder setting widgets.
            self._setup_move_to_done_label()
            self._setup_move_to_done_switch()

            move_to_done_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            move_to_done_horizontal_box.append(self.move_to_done_label)
            move_to_done_horizontal_box.append(self.move_to_done_switch)
            move_to_done_horizontal_box.set_margin_top(10)
            move_to_done_horizontal_box.set_margin_bottom(10)
            move_to_done_horizontal_box.set_margin_start(10)
            move_to_done_horizontal_box.set_margin_end(10)

            self.move_to_done_row = Adw.PreferencesRow()
            self.move_to_done_row.set_title('Move Completed Input Files to a Done Folder')
            self.move_to_done_row.set_child(move_to_done_horizontal_box)

        def _setup_move_to_done_label(self):
            # Initializes the move to done label.
            self.move_to_done_label = Gtk.Label(label='Move Completed Input Files to a Done Folder')
            self.move_to_done_label.set_hexpand(True)
            self.move_to_done_label.set_halign(Gtk.Align.START)

        def _setup_move_to_done_switch(self):
            # Initializes the move to done switch.
            self.move_to_done_switch = Gtk.Switch()
            self.move_to_done_switch.set_active(self.app_settings.is_watch_folders_moving_to_done)
            self.move_to_done_switch.set_vexpand(False)
            self.move_to_done_switch.set_valign(Gtk.Align.CENTER)
            self.move_to_done_switch.connect('state-set', self.on_move_to_done_switch_state_set)

        def set_parallel_nvenc_state(self, is_state_enabled: bool):
            """
            Sets the parallel nvenc settings widgets to reflect whether the parallel nvenc state is enabled.

            Parameters:
                is_state_enabled: Boolean that represents whether the parallel nvenc state is enabled.
            """
            self.nvenc_tasks_row.set_sensitive(is_state_enabled)

        def on_output_directory_file_chooser_button_clicked(self, button):
            """
            Signal callback function for the output directory file chooser button's 'clicked' signal.
            Shows a file chooser dialog that allows the user to choose a new folder for the application's
            default output directory.

            Parameters:
                button: Gtk.Button that emitted the signal.
            """
            output_directory_file_chooser = Gtk.FileChooserDialog(title='Open Default Output Directory',
                                                                  action=Gtk.FileChooserAction.SELECT_FOLDER,
                                                                  transient_for=self,
                                                                  modal=True,
                                                                  destroy_with_parent=True,
                                                                  resizable=False)
            output_directory_file_chooser.add_buttons('Cancel', Gtk.ResponseType.CANCEL)
            output_directory_file_chooser.add_buttons('Open', Gtk.ResponseType.ACCEPT)
            output_directory_file_chooser.set_file(Gio.File.new_for_path(self.app_settings.output_directory))
            output_directory_file_chooser.set_size_request(1000, 700)
            output_directory_file_chooser.connect('response', self._save_output_directory_setting)
            output_directory_file_chooser.show()

        def _save_output_directory_setting(self, file_chooser_dialog, response):
            # Sets the file chooser's selected directory as the application's default output directory.
            if response == Gtk.ResponseType.ACCEPT:
                output_directory_path = file_chooser_dialog.get_file().get_path()
                self.output_directory_label.set_label(output_directory_path)
                self.app_settings.output_directory = output_directory_path

            file_chooser_dialog.close()
            file_chooser_dialog.destroy()

        def on_temp_directory_file_chooser_button_clicked(self, button):
            """
            Signal callback function for the temp directory file chooser button's 'clicked' signal.
            Shows a file chooser dialog that allows the user to choose a new folder for the
            application's temp directory.

            Parameters:
                button: Gtk.Button that emitted the signal.
            """
            temp_directory_file_chooser = Gtk.FileChooserDialog(title='Open Temp Directory',
                                                                action=Gtk.FileChooserAction.SELECT_FOLDER,
                                                                transient_for=self,
                                                                modal=True,
                                                                destroy_with_parent=True,
                                                                resizable=False)
            temp_directory_file_chooser.add_buttons('Cancel', Gtk.ResponseType.CANCEL)
            temp_directory_file_chooser.add_buttons('Open', Gtk.ResponseType.ACCEPT)
            temp_directory_file_chooser.set_file(Gio.File.new_for_path(self.app_settings.temp_directory))
            temp_directory_file_chooser.set_size_request(1000, 700)
            temp_directory_file_chooser.connect('response', self._save_temp_directory_setting)
            temp_directory_file_chooser.show()

        def _save_temp_directory_setting(self, file_chooser_dialog, response):
            # Sets the file chooser's selected directory as the application's temp directory.
            if response == Gtk.ResponseType.ACCEPT:
                temp_directory_path = file_chooser_dialog.get_file().get_path()
                self.temp_directory_label.set_label(temp_directory_path)
                self.app_settings.temp_directory = temp_directory_path

            file_chooser_dialog.close()
            file_chooser_dialog.destroy()

        def on_overwrite_outputs_switch_state_set(self, switch, user_data):
            """
            Signal callback function for the overwrite outputs switch's 'state-set' signal.
            Uses the switch's state to set the application's overwriting output files setting.

            Parameters:
                switch: Gtk.Switch that emitted the signal.
                user_data: Additional data passed from the signal.
            """
            self.app_settings.is_overwriting_output_files = switch.get_active()

        def on_x264_tasks_spin_button_value_changed(self, spin_button):
            """
            Signal callback function for the x264 tasks spin button's 'value-changed' signal.
            Uses the spin button's value to set the application's per codec x264 setting.

            Parameters:
                spin_button: Gtk.SpinButton that emitted the signal.
            """
            self.app_settings.per_codec_x264 = spin_button.get_value()

        def on_x265_tasks_spin_button_value_changed(self, spin_button):
            """
            Signal callback function for the x265 tasks spin button's 'value-changed' signal.
            Uses the spin button's value to set the application's per codec x265 setting.

            Parameters:
                spin_button: Gtk.SpinButton that emitted the signal.
            """
            self.app_settings.per_codec_x265 = spin_button.get_value()

        def on_vp9_tasks_spin_button_value_changed(self, spin_button):
            """
            Signal callback function for the vp9 tasks spin button's 'value-changed' signal.
            Uses the spin button's value to set the application's per codec vp9 setting.

            Parameters:
                spin_button: Gtk.SpinButton that emitted the signal.
            """
            self.app_settings.per_codec_vp9 = spin_button.get_value()

        def on_parallel_nvenc_switch_state_set(self, switch, user_data):
            """
            Signal callback function for the parallel nvenc switch's 'state-set' signal.
            Sets the parallel nvenc state for the preferences window and uses the switch's state to set the
            application's parallel nvenc tasks setting.

            Parameters:
                switch: Gtk.Switch that emitted the signal.
                user_data: Additional data passed from the signal.
            """
            self.set_parallel_nvenc_state(switch.get_active())
            self.app_settings.is_nvenc_tasks_parallel = self.parallel_nvenc_switch.get_active()

        def on_nvenc_tasks_spin_button_value_changed(self, spin_button):
            """
            Signal callback function for the nvenc tasks spin button's 'value-changed' signal.
            Uses the spin button's value to set the application's parallel nvenc workers setting.

            Parameters:
                spin_button: Gtk.SpinButton that emitted the signal.
            """
            self.app_settings.parallel_nvenc_workers = spin_button.get_value()

        def on_parallel_watch_folders_switch_state_set(self, switch, user_data):
            """
            Signal callback function for the parallel watch folders switch's 'state-set' signal.
            Uses the switch's state to set the application's encode watch folders in parallel setting.

            Parameters:
                switch: Gtk.Switch that emitted the signal.
                user_data: Additional data passed from the signal.
            """
            self.app_settings.is_encoding_parallel_watch_folders = switch.get_active()

        def on_wait_for_tasks_switch_state_set(self, switch, user_data):
            """
            Signal callback function for the wait for tasks switch's 'state-set' signal.
            Uses the switch's state to set the application's watch folders wait for other tasks setting.

            Parameters:
                switch: Gtk.Switch that emitted the signal.
                user_data: Additional data passed from the signal.
            """
            self.app_settings.is_watch_folders_waiting_for_tasks = switch.get_active()

        def on_move_to_done_switch_state_set(self, switch, user_data):
            """
            Signal callback function for the move to done switch's 'state-set' signal.
            Uses the switch's state to set the application's move finished watch folder tasks to a done folder setting.

            Parameters:
                switch: Gtk.Switch that emitted the signal.
                user_data: Additional data passed from the signal.
            """
            self.app_settings.is_watch_folders_moving_to_done = switch.get_active()
