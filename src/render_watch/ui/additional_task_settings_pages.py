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


from render_watch.ui import Gtk, Gio, Gdk, GLib, Adw
from render_watch.encode import preview
from render_watch.ffmpeg import encoding
from render_watch import app_preferences


class PreviewPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        preview_page_label = Gtk.Label(label='Preview Page')
        preview_page_label.set_vexpand(True)
        preview_page_label.set_valign(Gtk.Align.CENTER)
        preview_page_label.set_hexpand(True)
        preview_page_label.set_halign(Gtk.Align.CENTER)

        self.append(preview_page_label)


class CropPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        crop_page_label = Gtk.Label(label='Crop Page')
        crop_page_label.set_vexpand(True)
        crop_page_label.set_valign(Gtk.Align.CENTER)
        crop_page_label.set_hexpand(True)
        crop_page_label.set_halign(Gtk.Align.CENTER)

        self.append(crop_page_label)


class TrimPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        trim_page_label = Gtk.Label(label='Trim Page')
        trim_page_label.set_vexpand(True)
        trim_page_label.set_valign(Gtk.Align.CENTER)
        trim_page_label.set_hexpand(True)
        trim_page_label.set_halign(Gtk.Align.CENTER)

        self.append(trim_page_label)


class BenchmarkPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        benchmark_page_label = Gtk.Label(label='Benchmark Page')
        benchmark_page_label.set_vexpand(True)
        benchmark_page_label.set_valign(Gtk.Align.CENTER)
        benchmark_page_label.set_hexpand(True)
        benchmark_page_label.set_halign(Gtk.Align.CENTER)

        self.append(benchmark_page_label)
