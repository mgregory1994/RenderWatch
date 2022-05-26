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

    def _setup_settings_pages(self):
        self._setup_general_settings_page()
        self._setup_video_codec_settings_page()
        self._setup_audio_codec_settings_page()
        self._setup_filter_settings_page()
        self._setup_subtitle_settings_page()
        self._setup_benchmark_page()

    def _setup_general_settings_page(self):
        self.general_settings_label = Gtk.Label(label='General Settings Page')

    def _setup_video_codec_settings_page(self):
        self.video_codec_settings_label = Gtk.Label(label='Video Codec Settings Page')

    def _setup_audio_codec_settings_page(self):
        self.audio_codec_settings_label = Gtk.Label(label='Audio Codec Settings Page')

    def _setup_filter_settings_page(self):
        self.filter_settings_label = Gtk.Label(label='Filter Settings Page')

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
        self.settings_page_stack.add_titled(self.general_settings_label, 'general_settings_page', 'General')
        self.settings_page_stack.add_titled(self.video_codec_settings_label, 'video_codec_settings_page', 'Video Codec')
        self.settings_page_stack.add_titled(self.audio_codec_settings_label, 'audio_codec_settings_page', 'Audio Codec')
        self.settings_page_stack.add_titled(self.filter_settings_label, 'filter_settings_page', 'Filters')
        self.settings_page_stack.add_titled(self.subtitle_settings_label, 'subtitle_settings_page', 'Subtitles')
        self.settings_page_stack.get_page(self.general_settings_label).set_icon_name('preferences-system-symbolic')
        self.settings_page_stack.get_page(self.video_codec_settings_label).set_icon_name('video-x-generic-symbolic')
        self.settings_page_stack.get_page(self.audio_codec_settings_label).set_icon_name('audio-x-generic-symbolic')
        self.settings_page_stack.get_page(self.filter_settings_label).set_icon_name('insert-image-symbolic')
        self.settings_page_stack.get_page(self.subtitle_settings_label).set_icon_name('insert-text-symbolic')

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
