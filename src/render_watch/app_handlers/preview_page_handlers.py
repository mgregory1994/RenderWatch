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


import threading
import queue

from render_watch.encoding import preview
from render_watch.app_formatting import format_converter
from render_watch.startup import GLib, GdkPixbuf


class PreviewPageHandlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.ffmpeg = None
        self.inputs_page_handlers = None
        self.preview_thumbnail_thread = None
        self.resize_thumbnail_thread = None
        self.stop_preview_thread = False
        self.preview_preview_viewport_width = 0
        self.preview_preview_viewport_height = 0
        self.image_buffer = None
        self.image_scaled_buffer = None
        self.__preview_thread = None
        self.__preview_queue = queue.Queue()
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

    def setup_preview_page(self):
        if not self.__setup_ffmpeg():
            return

        if self.ffmpeg.video_settings is None:
            self.__set_not_available_state(True)

            return
        else:
            self.__set_not_available_state(False)

        duration = self.ffmpeg.duration_origin
        duration_timecode = format_converter.get_timecode_from_seconds(duration)
        current_timecode = format_converter.get_timecode_from_seconds(duration / 4)

        self.preview_time_adjustment.set_upper(duration)
        self.preview_time_scale.set_value(duration / 4)
        self.preview_time_label.set_text(current_timecode + ' / ' + duration_timecode)

        time = self.preview_time_scale.get_value()

        self.__preview_queue.put(time)
        self.__run_set_preview_thumbnail_thread()

    def __setup_ffmpeg(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()

        if inputs_row is not None:
            self.ffmpeg = inputs_row.ffmpeg

            return True

        return False

    def __set_not_available_state(self, state):
        self.preview_settings_box.set_sensitive(not state)

        if state:
            self.preview_stack.set_visible_child(self.preview_noavail)
        else:
            self.preview_stack.set_visible_child(self.preview_preview)

    def __run_set_preview_thumbnail_thread(self):
        self.__preview_thread = threading.Thread(target=self.__set_preview_thumbnail, args=())

        self.__preview_thread.start()

    def __set_preview_thumbnail(self):
        time = self.__preview_queue.get()

        if not self.__preview_queue.empty():
            return

        output_file = preview.get_preview_file(self.ffmpeg, time, self.preferences)

        if not self.__preview_queue.empty():
            return

        if output_file is None:
            self.preview_stack.set_visible_child(self.preview_wrong_codec)

            return

        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)
        widget_width = self.preview_preview_viewport.get_allocated_width()
        widget_height = self.preview_preview_viewport.get_allocated_height()

        GLib.idle_add(self.__set_thumbnail_resize, widget_width, widget_height)

    def __set_thumbnail_resize(self, widget_width, widget_height):
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
            self.resize_thumbnail_thread = threading.Thread(target=self.__resize_thumbnail,
                                                            args=(scaled_width, scaled_height))

            self.resize_thumbnail_thread.start()

    def __resize_thumbnail(self, width, height):
        self.image_scaled_buffer = self.image_buffer.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

        GLib.idle_add(self.preview_preview.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.preview_stack.set_visible_child, self.preview_preview)
        GLib.idle_add(self.preview_preview.set_opacity, 1)

    def update_preview(self):
        if self.ffmpeg.video_settings is None:
            self.__set_not_available_state(True)
        else:
            self.__set_not_available_state(False)
            self.on_preview_scale_released(None, None)

    def reset_preview_page(self):
        self.preview_preview.set_from_icon_name('camera-video-symbolic', 192)
        self.preview_preview.set_opacity(0.5)

    def reset_preview_buttons(self):
        self.preview_still_radio_button.set_active(True)
        self.preview_progressbar.set_fraction(0.0)

    def set_preview_progress_bar_fraction(self, progress_bar_fraction_value):
        self.preview_progressbar.set_fraction(progress_bar_fraction_value)

    def on_preview_time_scale_value_changed(self, preview_time_scale):
        current_time_in_seconds = round(preview_time_scale.get_value(), 1)
        input_duration_in_seconds = self.ffmpeg.input_file_info['duration']
        difference_in_time = input_duration_in_seconds - current_time_in_seconds
        current_timecode = format_converter.get_timecode_from_seconds(current_time_in_seconds)
        duration_timecode = format_converter.get_timecode_from_seconds(input_duration_in_seconds)

        self.preview_time_label.set_text(current_timecode + ' / ' + duration_timecode)
        self.preview_preview.set_opacity(0.5)
        self.__setup_preview_duration_radiobuttons(difference_in_time)

    def __setup_preview_duration_radiobuttons(self, difference_in_time):
        if difference_in_time < 5:
            self.preview_5s_radio_button.set_sensitive(False)
            self.preview_10s_radio_button.set_sensitive(False)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif difference_in_time < 10:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(False)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif difference_in_time < 20:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(False)
            self.preview_30s_radio_button.set_sensitive(False)
        elif difference_in_time < 30:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(True)
            self.preview_30s_radio_button.set_sensitive(False)
        else:
            self.preview_5s_radio_button.set_sensitive(True)
            self.preview_10s_radio_button.set_sensitive(True)
            self.preview_20s_radio_button.set_sensitive(True)
            self.preview_30s_radio_button.set_sensitive(True)

    def on_preview_scale_released(self, event, data):
        time = self.preview_time_scale.get_value()

        self.preview_preview.set_opacity(0.5)
        self.__preview_queue.put(time)
        threading.Thread(target=self.__process_preview, args=()).start()

    def __process_preview(self):
        if self.__preview_thread is not None and self.__preview_thread.is_alive():
            self.__preview_thread.join()

        self.__run_set_preview_thumbnail_thread()

    def on_preview_duration_toggled(self, preview_duration_radiobutton):
        if not preview_duration_radiobutton.get_active():
            return

        self.__stop_preview_thumbnail_thread()

        start_time = round(self.preview_time_scale.get_value(), 1)
        preview_duration = self.__get_preview_duration_from_preview_duration_radiobutton(preview_duration_radiobutton)

        self.__set_preview_duration_state()
        self.__run_preview_thumbnail_thread(start_time, preview_duration)

    def __stop_preview_thumbnail_thread(self):
        if self.preview_thumbnail_thread is not None and self.preview_thumbnail_thread.is_alive():
            self.stop_preview_thread = True
            self.preview_thumbnail_thread.join()
            self.stop_preview_thread = False

    def __get_preview_duration_from_preview_duration_radiobutton(self, preview_duration_radiobutton):
        if preview_duration_radiobutton is self.preview_5s_radio_button:
            preview_duration = 5
        elif preview_duration_radiobutton is self.preview_10s_radio_button:
            preview_duration = 10
        elif preview_duration_radiobutton is self.preview_20s_radio_button:
            preview_duration = 20
        else:
            preview_duration = 30

        return preview_duration

    def __set_preview_duration_state(self):
        self.preview_stack.set_visible_child(self.preview_progress_box)
        self.preview_time_box.set_sensitive(False)
        self.preview_type_buttons_box.set_sensitive(False)

    def __run_preview_thumbnail_thread(self, start_time, preview_duration):
        self.preview_thumbnail_thread = threading.Thread(target=preview.start_vid_preview,
                                                         args=(self.ffmpeg, start_time, preview_duration,
                                                               self, lambda: self.stop_preview_thread,
                                                               self.preferences),
                                                         daemon=True)
        self.preview_thumbnail_thread.start()

    def on_preview_still_button_toggled(self, preview_still_radiobutton):
        if not preview_still_radiobutton.get_active():
            return

        self.__set_preview_still_state()

    def __set_preview_still_state(self):
        self.preview_stack.set_visible_child(self.preview_preview)
        self.preview_time_box.set_sensitive(True)
        self.preview_type_buttons_box.set_sensitive(True)

    def on_preview_preview_viewport_size_allocate(self, preview_preview_viewport, allocation):
        widget_width = preview_preview_viewport.get_allocated_width()
        widget_height = preview_preview_viewport.get_allocated_height()

        if not self.preview_preview_viewport_width == widget_width \
                or not self.preview_preview_viewport_height == widget_height:
            self.__set_thumbnail_resize(widget_width, widget_height)
            self.preview_preview_viewport_width = widget_width
            self.preview_preview_viewport_height = widget_height
