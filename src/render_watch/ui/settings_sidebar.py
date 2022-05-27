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
from render_watch.ffmpeg import encoding, general_settings, filters
from render_watch import app_preferences


class SettingsSidebarWidgets:

    SIDEBAR_WIDTH = 450

    def __init__(self, app_settings: app_preferences.Settings):
        self.app_settings = app_settings
        self.main_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._setup_settings_pages()
        self._setup_settings_view_switcher()
        self._setup_preview_buttons()

        self.main_widget.append(self.settings_view_switcher)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.settings_page_scrolled_window)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.preview_buttons_horizontal_box)
        self.main_widget.set_size_request(self.SIDEBAR_WIDTH, -1)
        self.main_widget.set_hexpand(False)

    def _setup_settings_pages(self):
        self._setup_general_settings_page()
        self._setup_video_codec_settings_page()
        self._setup_audio_codec_settings_page()
        self._setup_filter_settings_page()
        self._setup_subtitle_settings_page()
        self._setup_benchmark_page()

    def _setup_general_settings_page(self):
        self._setup_preset_settings()
        self._setup_output_file_settings()
        self._setup_frame_rate_settings()

        self.general_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.general_settings_vertical_box.append(self.preset_settings_group)
        self.general_settings_vertical_box.append(self.output_settings_group)
        self.general_settings_vertical_box.append(self.frame_rate_settings_group)

    def _setup_preset_settings(self):
        self.preset_settings_group = Adw.PreferencesGroup()
        self.preset_settings_group.set_title('Preset')

    def _setup_output_file_settings(self):
        self._setup_extension_setting()
        self._setup_fast_start_setting()

        extension_row = Adw.ActionRow()
        extension_row.set_title('Extension')
        extension_row.set_subtitle('Output file extension type')
        extension_row.add_suffix(self.extension_combobox)

        fast_start_row = Adw.ActionRow()
        fast_start_row.set_title('Fast Start')
        fast_start_row.set_subtitle('Move MOV atom to the beginning of the file')
        fast_start_row.add_suffix(self.fast_start_switch)

        self.output_settings_group = Adw.PreferencesGroup()
        self.output_settings_group.set_title('Output File')
        self.output_settings_group.add(extension_row)
        self.output_settings_group.add(fast_start_row)

    def _setup_extension_setting(self):
        self.extension_combobox = Gtk.ComboBoxText()
        self.extension_combobox.set_vexpand(False)
        self.extension_combobox.set_valign(Gtk.Align.CENTER)

        for extension in encoding.output.CONTAINERS:
            self.extension_combobox.append_text(extension)

        self.extension_combobox.set_active(0)

    def _setup_fast_start_setting(self):
        self.fast_start_switch = Gtk.Switch()
        self.fast_start_switch.set_vexpand(False)
        self.fast_start_switch.set_valign(Gtk.Align.CENTER)

    def _setup_frame_rate_settings(self):
        self._setup_custom_frame_rate_setting()

        auto_frame_rate_switch = Gtk.Switch()
        auto_frame_rate_switch.set_vexpand(False)
        auto_frame_rate_switch.set_valign(Gtk.Align.CENTER)

        self.frame_rate_settings_group = Adw.PreferencesGroup()
        self.frame_rate_settings_group.set_title('Frame Rate')
        self.frame_rate_settings_group.set_header_suffix(auto_frame_rate_switch)
        self.frame_rate_settings_group.add(self.custom_frame_rate_row)

    def _setup_custom_frame_rate_setting(self):
        custom_frame_rate_combobox = Gtk.ComboBoxText()
        custom_frame_rate_combobox.set_vexpand(False)
        custom_frame_rate_combobox.set_valign(Gtk.Align.CENTER)

        for frame_rate in general_settings.GeneralSettings.FRAME_RATE:
            custom_frame_rate_combobox.append_text(frame_rate)

        custom_frame_rate_combobox.set_active(0)

        self.custom_frame_rate_row = Adw.ActionRow()
        self.custom_frame_rate_row.set_title('Frames Per Second')
        self.custom_frame_rate_row.set_subtitle('Output\'s frame rate')
        self.custom_frame_rate_row.add_suffix(custom_frame_rate_combobox)
        self.custom_frame_rate_row.set_sensitive(False)

    def _setup_video_codec_settings_page(self):
        self.video_codec_settings_label = Gtk.Label(label='Video Codec Settings Page')

    def _setup_audio_codec_settings_page(self):
        self.audio_codec_settings_label = Gtk.Label(label='Audio Codec Settings Page')

    def _setup_filter_settings_page(self):
        self._setup_deinterlace_settings()

        self.filter_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.filter_settings_vertical_box.append(self.deinterlace_settings_group)

    def _setup_deinterlace_settings(self):
        self._setup_deinterlace_method_setting()

        deinterlace_enabled_switch = Gtk.Switch()
        deinterlace_enabled_switch.set_vexpand(False)
        deinterlace_enabled_switch.set_valign(Gtk.Align.CENTER)

        self.deinterlace_settings_group = Adw.PreferencesGroup()
        self.deinterlace_settings_group.set_title('Deinterlace')
        self.deinterlace_settings_group.set_header_suffix(deinterlace_enabled_switch)
        self.deinterlace_settings_group.add(self.deinterlace_method_row)

    def _setup_deinterlace_method_setting(self):
        deinterlace_method_combobox = Gtk.ComboBoxText()
        deinterlace_method_combobox.set_vexpand(False)
        deinterlace_method_combobox.set_valign(Gtk.Align.CENTER)

        for deinterlace_method in filters.Deinterlace.DEINT_FILTERS:
            deinterlace_method_combobox.append_text(deinterlace_method)

        deinterlace_method_combobox.set_active(0)

        self.deinterlace_method_row = Adw.ActionRow()
        self.deinterlace_method_row.set_title('Method')
        self.deinterlace_method_row.set_subtitle('Deinterlacing method')
        self.deinterlace_method_row.add_suffix(deinterlace_method_combobox)
        self.deinterlace_method_row.set_sensitive(False)

    def _setup_subtitle_settings_page(self):
        self.subtitle_settings_label = Gtk.Label(label='Subtitle Settings Page')

    def _setup_benchmark_page(self):
        self.benchmark_label = Gtk.Label(label='Benchmark Page')

    def _setup_settings_view_switcher(self):
        self._setup_settings_page_stack()

        self.settings_view_switcher = Adw.ViewSwitcher()
        self.settings_view_switcher.set_policy(Adw.ViewSwitcherPolicy.NARROW)
        self.settings_view_switcher.set_stack(self.settings_page_stack)

    def _setup_settings_page_stack(self):
        self.settings_page_stack = Adw.ViewStack()
        self.settings_page_stack.add_titled(self.general_settings_vertical_box, 'general_settings_page', 'General')
        self.settings_page_stack.add_titled(self.video_codec_settings_label, 'video_codec_settings_page', 'Video Codec')
        self.settings_page_stack.add_titled(self.audio_codec_settings_label, 'audio_codec_settings_page', 'Audio Codec')
        self.settings_page_stack.add_titled(self.filter_settings_vertical_box, 'filter_settings_page', 'Filters')
        self.settings_page_stack.add_titled(self.subtitle_settings_label, 'subtitle_settings_page', 'Subtitles')
        self.settings_page_stack.get_page(self.general_settings_vertical_box).set_icon_name('preferences-system-symbolic')
        self.settings_page_stack.get_page(self.video_codec_settings_label).set_icon_name('video-x-generic-symbolic')
        self.settings_page_stack.get_page(self.audio_codec_settings_label).set_icon_name('audio-x-generic-symbolic')
        self.settings_page_stack.get_page(self.filter_settings_vertical_box).set_icon_name('insert-image-symbolic')
        self.settings_page_stack.get_page(self.subtitle_settings_label).set_icon_name('insert-text-symbolic')
        self.settings_page_stack.set_margin_top(20)
        self.settings_page_stack.set_margin_bottom(20)
        self.settings_page_stack.set_margin_start(20)
        self.settings_page_stack.set_margin_end(20)

        self.settings_page_scrolled_window = Gtk.ScrolledWindow()
        self.settings_page_scrolled_window.set_child(self.settings_page_stack)
        self.settings_page_scrolled_window.set_vexpand(True)

    def _setup_preview_buttons(self):
        self.settings_preview_button = Gtk.Button.new_from_icon_name('video-display-symbolic')
        self.crop_preview_button = Gtk.Button.new_from_icon_name('zoom-fit-best-symbolic')
        self.trim_preview_button = Gtk.Button.new_from_icon_name('edit-cut-symbolic')

        self.preview_buttons_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.preview_buttons_horizontal_box.append(self.settings_preview_button)
        self.preview_buttons_horizontal_box.append(self.crop_preview_button)
        self.preview_buttons_horizontal_box.append(self.trim_preview_button)
        self.preview_buttons_horizontal_box.set_hexpand(False)
        self.preview_buttons_horizontal_box.set_halign(Gtk.Align.CENTER)
        self.preview_buttons_horizontal_box.set_margin_top(10)
        self.preview_buttons_horizontal_box.set_margin_bottom(10)
