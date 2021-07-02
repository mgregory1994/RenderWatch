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


import threading
import queue

from render_watch.encoding import preview
from render_watch.app_formatting import format_converter
from render_watch.signals.preview.preview_duration_signal import PreviewDurationSignal
from render_watch.signals.preview.preview_live_signal import PreviewLiveSignal
from render_watch.signals.preview.preview_size_signal import PreviewSizeSignal
from render_watch.signals.preview.preview_time_signal import PreviewTimeSignal
from render_watch.startup import GLib, GdkPixbuf


class PreviewPageHandlers:
    """Handles all widget changes on the preview page."""

    def __init__(self, gtk_builder, inputs_page_handlers, preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences
        self.ffmpeg = None
        self.preview_thumbnail_thread = None
        self.resize_thumbnail_thread = None
        self.stop_preview_thread = False
        self.preview_preview_viewport_width = 0
        self.preview_preview_viewport_height = 0
        self.image_buffer = None
        self.image_scaled_buffer = None
        self._preview_thread = None
        self._preview_queue = queue.Queue()
        self.preview_duration_signal = PreviewDurationSignal(self)
        self.preview_live_signal = PreviewLiveSignal(self)
        self.preview_size_signal = PreviewSizeSignal(self)
        self.preview_time_signal = PreviewTimeSignal(self)
        self.signals_list = (
            self.preview_duration_signal, self.preview_live_signal,
            self.preview_size_signal, self.preview_time_signal
        )
        self.preview_preview = gtk_builder.get_object('preview_preview')
        self.preview_time_label = gtk_builder.get_object('preview_time_label')
        self.preview_time_scale = gtk_builder.get_object('preview_time_scale')
        self.preview_still_radio_button = gtk_builder.get_object('preview_still_radio_button')
        self.preview_5s_radio_button = gtk_builder.get_object('preview_5s_radio_button')
        self.preview_10s_radio_button = gtk_builder.get_object('preview_10s_radio_button')
        self.preview_20s_radio_button = gtk_builder.get_object('preview_20s_radio_button')
        self.preview_30s_radio_button = gtk_builder.get_object('preview_30s_radio_button')
        self.preview_stack = gtk_builder.get_object('preview_stack')
        self.preview_progressbar = gtk_builder.get_object('preview_progressbar')
        self.preview_type_buttons_box = gtk_builder.get_object('preview_type_buttons_box')
        self.preview_time_box = gtk_builder.get_object('preview_time_box')
        self.preview_time_adjustment = gtk_builder.get_object('preview_time_adjustment')
        self.preview_noavail = gtk_builder.get_object('preview_noavail')
        self.preview_progress_box = gtk_builder.get_object('preview_progress_box')
        self.preview_preview_viewport = gtk_builder.get_object('preview_preview_viewport')
        self.preview_settings_box = gtk_builder.get_object('preview_settings_box')
        self.preview_wrong_codec = gtk_builder.get_object('preview_wrong_codec')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

        Used for Gtk.Builder.get_signals().

        :param signal_name:
            The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def setup_preview_page(self):
        """Sets up the preview page for the currently selected inputs row."""
        if not self._setup_ffmpeg():
            return
        if self.ffmpeg.video_settings is None:
            self._set_not_available_state(True)
            return
        else:
            self._set_not_available_state(False)

        duration = self.ffmpeg.duration_origin
        duration_timecode = format_converter.get_timecode_from_seconds(duration)
        current_timecode = format_converter.get_timecode_from_seconds(duration / 4)
        self.preview_time_adjustment.set_upper(duration)
        self.preview_time_scale.set_value(duration / 4)
        self.preview_time_label.set_text(current_timecode + ' / ' + duration_timecode)
        self._preview_queue.put(self.preview_time_scale.get_value())
        self._run_set_preview_thumbnail_thread()

    def _setup_ffmpeg(self):
        # Gets the ffmpeg settings object from the currently selected inputs row.
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            self.ffmpeg = inputs_row.ffmpeg
            return True
        return False

    def _set_not_available_state(self, state):
        # Shows that the previewer is unavailable.
        self.preview_settings_box.set_sensitive(not state)
        if state:
            self.preview_stack.set_visible_child(self.preview_noavail)
        else:
            self.preview_stack.set_visible_child(self.preview_preview)

    def _run_set_preview_thumbnail_thread(self):
        # Runs the thread that sets up the previewer's image.
        self._preview_thread = threading.Thread(target=self._set_preview_thumbnail, args=())
        self._preview_thread.start()

    def _set_preview_thumbnail(self):
        # Generates the previewer's image and sizes it accordingly.
        if not self._preview_queue.empty():
            return

        output_file = preview.generate_preview_file(self.ffmpeg, self._preview_queue.get(), self.preferences)

        if not self._preview_queue.empty():
            return

        if output_file is None:
            self.preview_stack.set_visible_child(self.preview_wrong_codec)
            return

        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)
        widget_width = self.preview_preview_viewport.get_allocated_width()
        widget_height = self.preview_preview_viewport.get_allocated_height()
        GLib.idle_add(self.set_thumbnail_size, widget_width, widget_height)

    def set_thumbnail_size(self, widget_width, widget_height):
        """Resizes the previewer's image."""
        if self.image_buffer is None:
            return
        image_width = self.image_buffer.get_width()
        image_height = self.image_buffer.get_height()
        width_ratio = widget_width / image_width
        height_ratio = widget_height / image_height
        aspect_ratio = min(width_ratio, height_ratio)
        scaled_width = image_width * aspect_ratio
        scaled_height = image_height * aspect_ratio
        if self.resize_thumbnail_thread is None or not self.resize_thumbnail_thread.is_alive():
            self.resize_thumbnail_thread = threading.Thread(target=self._resize_thumbnail,
                                                            args=(scaled_width, scaled_height))
            self.resize_thumbnail_thread.start()

    def _resize_thumbnail(self, width, height):
        # Resizes the previewer's image.
        self.image_scaled_buffer = self.image_buffer.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        GLib.idle_add(self.preview_preview.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.preview_stack.set_visible_child, self.preview_preview)
        GLib.idle_add(self.preview_preview.set_opacity, 1)

    def reset_preview_page(self):
        self.preview_preview.set_from_icon_name('camera-video-symbolic', 192)
        self.preview_preview.set_opacity(0.5)

    def reset_preview_buttons(self):
        self.preview_still_radio_button.set_active(True)
        self.preview_progressbar.set_fraction(0.0)

    def get_current_time_value(self):
        return self.preview_time_scale.get_value()

    def get_preview_duration(self):
        if self.preview_5s_radio_button.get_active():
            preview_duration = 5
        elif self.preview_10s_radio_button.get_active():
            preview_duration = 10
        elif self.preview_20s_radio_button.get_active():
            preview_duration = 20
        elif self.preview_30s_radio_button.get_active():
            preview_duration = 30
        else:
            preview_duration = None
        return preview_duration

    def get_preview_viewport_width(self):
        return self.preview_preview_viewport_width

    def get_preview_viewport_height(self):
        return self.preview_preview_viewport_height

    def set_progress_fraction(self, progress_bar_fraction_value):
        self.preview_progressbar.set_fraction(progress_bar_fraction_value)

    def set_time_label_text(self, time_text):
        self.preview_time_label.set_text(time_text)

    def set_preview_opacity(self, opacity_fraction):
        self.preview_preview.set_opacity(opacity_fraction)

    def set_preview_viewport_width(self, width):
        self.preview_preview_viewport_width = width

    def set_preview_viewport_height(self, height):
        self.preview_preview_viewport_height = height

    def set_preview_duration_state(self):
        self.preview_stack.set_visible_child(self.preview_progress_box)
        self.preview_time_box.set_sensitive(False)
        self.preview_type_buttons_box.set_sensitive(False)

    def set_preview_live_state(self):
        self.preview_stack.set_visible_child(self.preview_preview)
        self.preview_time_box.set_sensitive(True)
        self.preview_type_buttons_box.set_sensitive(True)

    def queue_add_time(self, time):
        self._preview_queue.put(time)

    def update_preview(self):
        if self.ffmpeg.video_settings is None:
            self._set_not_available_state(True)
        else:
            self._set_not_available_state(False)
            self.preview_time_signal.on_preview_scale_released(None, None)

    def update_duration_radiobuttons(self, end_time_difference):
        if end_time_difference < 5:
            self.preview_5s_radio_button.set_sensitive(False)
            self.preview_10s_radio_button.set_sensitive(False)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif end_time_difference < 10:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(False)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif end_time_difference < 20:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif end_time_difference < 30:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(True)
            self.preview_30s_radio_button.set_sensitive(False)
        else:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(True)
            self.preview_30s_radio_button.set_sensitive(True)

    def process_preview(self):
        if self._preview_thread is not None and self._preview_thread.is_alive():
            self._preview_thread.join()
        self._run_set_preview_thumbnail_thread()

    def stop_preview_thumbnail_thread(self):
        if self.preview_thumbnail_thread is not None and self.preview_thumbnail_thread.is_alive():
            self.stop_preview_thread = True
            self.preview_thumbnail_thread.join()
            self.stop_preview_thread = False

    def run_preview_thumbnail_thread(self, start_time, preview_duration):
        self.preview_thumbnail_thread = threading.Thread(target=preview.start_vid_preview,
                                                         args=(self.ffmpeg,
                                                               start_time,
                                                               preview_duration,
                                                               self,
                                                               lambda: self.stop_preview_thread,
                                                               self.preferences),
                                                         daemon=True)
        self.preview_thumbnail_thread.start()
