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
from render_watch.signals.preview.duration_signal import DurationSignal
from render_watch.signals.preview.live_preview_signal import LivePreviewSignal
from render_watch.signals.preview.viewport_size_signal import ViewportSizeSignal
from render_watch.signals.preview.preview_location_signal import PreviewLocationSignal
from render_watch.startup import GLib, GdkPixbuf


class PreviewPageHandlers:
    """
    Handles all widget changes on the preview page.
    """

    def __init__(self, gtk_builder, inputs_page_handlers, application_preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.application_preferences = application_preferences
        self.ffmpeg = None
        self.preview_thumbnail_thread = None
        self.resize_thumbnail_thread = None
        self.is_preview_thread_stopping = False
        self.preview_preview_viewport_width = 0
        self.preview_preview_viewport_height = 0
        self.image_buffer = None
        self.image_scaled_buffer = None
        self._preview_thread = None
        self._preview_queue = queue.Queue()

        self.duration_signal = DurationSignal(self)
        self.live_preview_signal = LivePreviewSignal(self)
        self.viewport_size_signal = ViewportSizeSignal(self)
        self.preview_location_signal = PreviewLocationSignal(self)
        self.signals_list = (
            self.duration_signal, self.live_preview_signal,
            self.viewport_size_signal, self.preview_location_signal
        )

        self.preview_icon = gtk_builder.get_object('preview_icon')
        self.preview_time_selection_label = gtk_builder.get_object('preview_time_selection_label')
        self.preview_position_scale = gtk_builder.get_object('preview_position_scale')
        self.preview_live_radiobutton = gtk_builder.get_object('preview_live_radiobutton')
        self.preview_5s_radio_button = gtk_builder.get_object('preview_5s_radiobutton')
        self.preview_10s_radio_button = gtk_builder.get_object('preview_10s_radiobutton')
        self.preview_20s_radio_button = gtk_builder.get_object('preview_20s_radiobutton')
        self.preview_30s_radio_button = gtk_builder.get_object('preview_30s_radiobutton')
        self.preview_stack = gtk_builder.get_object('preview_stack')
        self.preview_progressbar = gtk_builder.get_object('preview_progressbar')
        self.preview_type_buttonbox = gtk_builder.get_object('preview_type_buttonbox')
        self.preview_time_selection_box = gtk_builder.get_object('preview_time_selection_box')
        self.preview_time_adjustment = gtk_builder.get_object('preview_time_adjustment')
        self.preview_not_available_label = gtk_builder.get_object('preview_not_available_label')
        self.preview_progress_box = gtk_builder.get_object('preview_progress_box')
        self.preview_viewport = gtk_builder.get_object('preview_viewport')
        self.preview_selection_box = gtk_builder.get_object('preview_selection_box')
        self.preview_wrong_codec_label = gtk_builder.get_object('preview_wrong_codec_label')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def setup_preview_page(self):
        """
        Configures the preview page widgets to match the selected task's ffmpeg settings.
        """
        if self.get_preview_encode_state():
            return

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
        self.preview_position_scale.set_value(duration / 4)
        self.preview_time_selection_label.set_text(current_timecode + ' / ' + duration_timecode)
        self._preview_queue.put(self.preview_position_scale.get_value())
        self._run_set_preview_thumbnail_thread()

    def _setup_ffmpeg(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            self.ffmpeg = inputs_row.ffmpeg

            return True
        return False

    def _set_not_available_state(self, state):
        self.preview_selection_box.set_sensitive(not state)

        if state:
            self.preview_stack.set_visible_child(self.preview_not_available_label)
        else:
            self.preview_stack.set_visible_child(self.preview_icon)

    def _run_set_preview_thumbnail_thread(self):
        self._preview_thread = threading.Thread(target=self._set_preview_thumbnail, args=())
        self._preview_thread.start()

    def _set_preview_thumbnail(self):
        output_file = preview.generate_preview_file(self.ffmpeg,
                                                    self._preview_queue.get(),
                                                    self.application_preferences)

        if not self._preview_queue.empty():
            return

        if output_file is None:
            self.preview_stack.set_visible_child(self.preview_wrong_codec_label)

            return

        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)

        viewport_width = self.preview_viewport.get_allocated_width()
        viewport_height = self.preview_viewport.get_allocated_height()
        GLib.idle_add(self.set_thumbnail_size, viewport_width, viewport_height)

    def set_thumbnail_size(self, viewport_width, viewport_height):
        """
        Resizes the preview icon to fit the preview viewport.
        """
        if self.image_buffer is None:
            return

        image_width = self.image_buffer.get_width()
        image_height = self.image_buffer.get_height()
        width_ratio = viewport_width / image_width
        height_ratio = viewport_height / image_height
        aspect_ratio = min(width_ratio, height_ratio)
        scaled_width = image_width * aspect_ratio
        scaled_height = image_height * aspect_ratio

        if self.resize_thumbnail_thread is None or not self.resize_thumbnail_thread.is_alive():
            self.resize_thumbnail_thread = threading.Thread(target=self._resize_thumbnail,
                                                            args=(scaled_width, scaled_height))
            self.resize_thumbnail_thread.start()

    def _resize_thumbnail(self, width, height):
        self.image_scaled_buffer = self.image_buffer.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

        GLib.idle_add(self.preview_icon.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.preview_stack.set_visible_child, self.preview_icon)
        GLib.idle_add(self.preview_icon.set_opacity, 1)

    def reset_preview_page(self):
        self.preview_icon.set_from_icon_name('camera-video-symbolic', 192)
        self.preview_icon.set_opacity(0.5)

    def reset_preview_buttons(self):
        self.preview_live_radiobutton.set_active(True)
        self.preview_progressbar.set_fraction(0.0)

    def get_current_time_value(self):
        return self.preview_position_scale.get_value()

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

    def get_preview_encode_state(self):
        return self.preview_stack.get_visible_child() == self.preview_progress_box

    def is_preview_failed_state(self):
        return self.preview_stack.get_visible_child() == self.preview_wrong_codec_label

    def set_progress_fraction(self, progress_bar_fraction_value):
        self.preview_progressbar.set_fraction(progress_bar_fraction_value)

    def set_time_label_text(self, time_text):
        self.preview_time_selection_label.set_text(time_text)

    def set_preview_opacity(self, opacity_fraction):
        self.preview_icon.set_opacity(opacity_fraction)

    def set_preview_viewport_width(self, width):
        self.preview_preview_viewport_width = width

    def set_preview_viewport_height(self, height):
        self.preview_preview_viewport_height = height

    def set_preview_duration_state(self):
        self.preview_stack.set_visible_child(self.preview_progress_box)
        self.preview_time_selection_box.set_sensitive(False)
        self.preview_type_buttonbox.set_sensitive(False)
        self.inputs_page_handlers.set_preview_encoding_state(True)

    def set_preview_live_state(self):
        self.preview_stack.set_visible_child(self.preview_icon)
        self.preview_time_selection_box.set_sensitive(True)
        self.preview_type_buttonbox.set_sensitive(True)
        self.inputs_page_handlers.set_preview_encoding_state(False)

    def queue_preview_time_position(self, time_position):
        self._preview_queue.put(time_position)

    def update_preview(self):
        if self.ffmpeg.video_settings is None:
            self._set_not_available_state(True)
        else:
            self._set_not_available_state(False)
            self.preview_location_signal.on_preview_position_scale_button_release_event(self.preview_position_scale)

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
            self.is_preview_thread_stopping = True
            self.preview_thumbnail_thread.join()
            self.is_preview_thread_stopping = False

    def run_preview_thumbnail_thread(self, start_time, preview_duration):
        self.preview_thumbnail_thread = threading.Thread(target=preview.start_vid_preview,
                                                         args=(self.ffmpeg,
                                                               start_time,
                                                               preview_duration,
                                                               self,
                                                               lambda: self.is_preview_thread_stopping,
                                                               self.application_preferences),
                                                         daemon=True)
        self.preview_thumbnail_thread.start()
