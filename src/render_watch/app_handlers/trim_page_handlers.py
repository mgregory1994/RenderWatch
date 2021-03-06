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

from render_watch.app_formatting import format_converter
from render_watch.encoding import preview
from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.startup import GLib, GdkPixbuf


class TrimPageHandlers:
    def __init__(self, gtk_builder, preferences):
        self.inputs_page_handlers = None
        self.ffmpeg = None
        self.image_buffer = None
        self.image_scaled_buffer = None
        self.resize_thumbnail_thread = None
        self.trim_preview_viewport_width = 0
        self.trim_preview_viewport_height = 0
        self.__is_widgets_setting_up = False
        self.preferences = preferences
        self.trim_popover = gtk_builder.get_object('trim_popover')
        self.trim_time_box = gtk_builder.get_object('trim_time_box')
        self.trim_start_scale = gtk_builder.get_object('trim_start_scale')
        self.trim_end_scale = gtk_builder.get_object('trim_end_scale')
        self.trim_preview = gtk_builder.get_object('trim_preview')
        self.trim_reset = gtk_builder.get_object('trim_reset')
        self.trim_preview_stack = gtk_builder.get_object('trim_preview_stack')
        self.trim_enabled_checkbox = gtk_builder.get_object('trim_enabled_checkbox')
        self.trim_start_adjustment = gtk_builder.get_object('trim_start_adjustment')
        self.trim_end_adjustment = gtk_builder.get_object('trim_end_adjustment')
        self.trim_start_label = gtk_builder.get_object('trim_start_label')
        self.trim_start_value_label = gtk_builder.get_object('trim_start_value_label')
        self.trim_end_label = gtk_builder.get_object('trim_end_label')
        self.trim_end_value_label = gtk_builder.get_object('trim_end_value_label')
        self.trim_preview_viewport = gtk_builder.get_object('trim_preview_viewport')

    def __set_trim_start_label_value_text(self, trim_start_value_text, bold_text_enabled=False):
        if bold_text_enabled:
            self.trim_start_label.set_markup('<b>Trim Start:</b>')
            self.trim_start_value_label.set_markup('<b>' + trim_start_value_text + '</b>')
            self.__disable_trim_end_label_bold_text()
        else:
            self.trim_start_label.set_text('Trim Start:')
            self.trim_start_value_label.set_text(trim_start_value_text)

    def __set_trim_end_label_value_text(self, trim_end_value_text, bold_text_enabled=False):
        if bold_text_enabled:
            self.trim_end_label.set_markup('<b>Trim End:</b>')
            self.trim_end_value_label.set_markup('<b>' + trim_end_value_text + '</b>')
            self.__disable_trim_start_label_bold_text()
        else:
            self.trim_end_label.set_text('Trim End:')
            self.trim_end_value_label.set_text(trim_end_value_text)

    def __disable_trim_start_label_bold_text(self):
        start_time_in_seconds = round(self.trim_start_scale.get_value(), 1)
        start_timecode = format_converter.get_timecode_from_seconds(start_time_in_seconds)

        self.trim_start_label.set_text('Trim Start:')
        self.trim_start_value_label.set_text(start_timecode)

    def __disable_trim_end_label_bold_text(self):
        end_time_in_seconds = round(self.trim_end_scale.get_value(), 1)
        end_timecode = format_converter.get_timecode_from_seconds(end_time_in_seconds)

        self.trim_end_label.set_text('Trim End:')
        self.trim_end_value_label.set_text(end_timecode)

    def setup_trim_page(self):
        if not self.__setup_ffmpeg():
            return

        self.__is_widgets_setting_up = True

        self.__setup_trim_page_scales()
        self.__setup_trim_page_labels()

        self.__is_widgets_setting_up = False

        self.__run_set_trim_thumbnail_thread()

    def __setup_ffmpeg(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()

        if inputs_row is not None:
            self.ffmpeg = inputs_row.ffmpeg

            return True

        return False

    def __setup_trim_page_scales(self):
        self.trim_start_adjustment.set_upper(self.ffmpeg.duration_origin)
        self.trim_end_adjustment.set_upper(self.ffmpeg.duration_origin)

        if self.ffmpeg.trim_settings is None:
            self.trim_start_scale.set_value(0)
            self.trim_end_scale.set_value(self.trim_end_adjustment.get_upper())
            self.trim_enabled_checkbox.set_active(False)
        else:
            start_time = self.ffmpeg.trim_settings.start_time
            trim_duration = self.ffmpeg.trim_settings.trim_duration

            self.trim_start_scale.set_value(start_time)
            self.trim_end_scale.set_value(start_time + trim_duration)
            self.trim_enabled_checkbox.set_active(True)

    def __setup_trim_page_labels(self):
        start_timecode = format_converter.get_timecode_from_seconds(self.trim_start_scale.get_value())
        end_timecode = format_converter.get_timecode_from_seconds(self.trim_end_scale.get_value())

        self.__set_trim_start_label_value_text(start_timecode, True)
        self.__set_trim_end_label_value_text(end_timecode)

    def __run_set_trim_thumbnail_thread(self, use_end_time=False):
        if use_end_time:
            time = round(self.trim_end_scale.get_value(), 1)
        else:
            time = round(self.trim_start_scale.get_value(), 1)

        threading.Thread(target=self.__set_trim_thumbnail, args=(time,)).start()

    def __set_trim_thumbnail(self, time):
        output_file = preview.get_trim_preview_file(self.ffmpeg, time, self.preferences)
        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)
        widget_width = self.trim_preview_viewport.get_allocated_width()
        widget_height = self.trim_preview_viewport.get_allocated_height()

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

        self.__run_resize_thumbnail_thread(scaled_width, scaled_height)

    def __run_resize_thumbnail_thread(self, scaled_width, scaled_height):
        if self.resize_thumbnail_thread is None or not self.resize_thumbnail_thread.is_alive():
            self.resize_thumbnail_thread = threading.Thread(target=self.__resize_thumbnail,
                                                            args=(scaled_width, scaled_height))

            self.resize_thumbnail_thread.start()

    def __resize_thumbnail(self, width, height):
        self.image_scaled_buffer = self.image_buffer.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

        GLib.idle_add(self.trim_preview.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.trim_preview_stack.set_visible_child, self.trim_preview)
        GLib.idle_add(self.trim_preview.set_opacity, 1)

    def reset_trim_page(self):
        self.__is_widgets_setting_up = True

        self.trim_start_scale.set_value(0)
        self.trim_end_scale.set_value(self.trim_end_adjustment.get_upper())
        self.trim_preview_stack.set_visible_child(self.trim_reset)
        self.trim_preview.set_opacity(0.5)
        self.trim_enabled_checkbox.set_active(False)

        self.__is_widgets_setting_up = False

    def on_trim_enabled_checkbox_toggled(self, trim_enabled_checkbox):
        self.trim_time_box.set_sensitive(trim_enabled_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        self.__setup_trim_settings()

    def __setup_trim_settings(self):
        if self.trim_enabled_checkbox.get_active():
            start_time = round(self.trim_start_scale.get_value(), 1)
            duration = round(self.trim_end_scale.get_value() - start_time, 1)

            trim_settings = TrimSettings()
            trim_settings.start_time = start_time
            trim_settings.trim_duration = duration
            self.ffmpeg.trim_settings = trim_settings
        else:
            self.ffmpeg.trim_settings = None

        self.inputs_page_handlers.get_selected_row().setup_labels()

    def on_trim_start_scale_value_changed(self, trim_start_scale):
        start_time_in_seconds = round(trim_start_scale.get_value(), 1)

        if start_time_in_seconds >= self.trim_end_scale.get_value():
            self.trim_end_scale.set_value(start_time_in_seconds + 1)

        if start_time_in_seconds == self.ffmpeg.duration_origin:
            trim_start_scale.set_value(start_time_in_seconds - 1)

        start_timecode = format_converter.get_timecode_from_seconds(start_time_in_seconds)

        self.__set_trim_start_label_value_text(start_timecode, True)

    def on_trim_start_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return
        
        self.__run_set_trim_thumbnail_thread()
        self.__setup_trim_settings()

    def on_trim_start_scale_key_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return
        
        self.__run_set_trim_thumbnail_thread()
        self.__setup_trim_settings()

    def on_trim_end_scale_value_changed(self, trim_end_scale):
        end_time_in_seconds = round(trim_end_scale.get_value(), 1)

        if end_time_in_seconds <= self.trim_start_scale.get_value():
            self.trim_start_scale.set_value(end_time_in_seconds - 1)

        if end_time_in_seconds == 0:
            trim_end_scale.set_value(1)

        end_timecode = format_converter.get_timecode_from_seconds(end_time_in_seconds)

        self.__set_trim_end_label_value_text(end_timecode, True)

    def on_trim_end_scale_button_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return
        
        self.__run_set_trim_thumbnail_thread(True)
        self.__setup_trim_settings()

    def on_trim_end_scale_key_release_event(self, event, data):
        if self.__is_widgets_setting_up:
            return
        
        self.__run_set_trim_thumbnail_thread(True)
        self.__setup_trim_settings()

    def on_trim_preview_viewport_size_allocate(self, trim_preview_viewport, allocation):
        widget_width = trim_preview_viewport.get_allocated_width()
        widget_height = trim_preview_viewport.get_allocated_height()

        if not self.trim_preview_viewport_width == widget_width \
                or not self.trim_preview_viewport_height == widget_height:
            self.__set_thumbnail_resize(widget_width, widget_height)
            self.trim_preview_viewport_width = widget_width
            self.trim_preview_viewport_height = widget_height
