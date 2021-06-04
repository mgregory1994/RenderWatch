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

from render_watch.encoding import preview
from render_watch.signals.crop.autocrop_signal import AutocropSignal
from render_watch.signals.crop.crop_dimensions_signal import CropDimensionsSignal
from render_watch.signals.crop.crop_padding_signal import CropPaddingSignal
from render_watch.signals.crop.crop_signal import CropSignal
from render_watch.signals.crop.preview_size_signal import PreviewSizeSignal
from render_watch.signals.crop.scale_dimensions_signal import ScaleDimensionsSignal
from render_watch.signals.crop.scale_signal import ScaleSignal
from render_watch.startup import GLib, GdkPixbuf


class CropPageHandlers:
    def __init__(self, gtk_builder, inputs_page_handlers, preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.preferences = preferences
        self.ffmpeg = None
        self.image_buffer = None
        self.image_scale_buffer = None
        self.resize_thumbnail_thread = None
        self.crop_preview_viewport_width = 0
        self.crop_preview_viewport_height = 0
        self.is_widgets_setting_up = False
        self.auto_crop_signal = AutocropSignal(self)
        self.padding_signal = CropPaddingSignal(self)
        self.crop_dimensions_signal = CropDimensionsSignal(self)
        self.crop_signal = CropSignal(self)
        self.preview_size_signal = PreviewSizeSignal(self)
        self.scale_dimensions = ScaleDimensionsSignal(self)
        self.scale_signal = ScaleSignal(self)
        self.signals_list = (self.auto_crop_signal, self.padding_signal, self.crop_dimensions_signal, self.crop_signal,
                             self.preview_size_signal, self.scale_dimensions, self.scale_signal)
        self.crop_preview = gtk_builder.get_object('crop_preview')
        self.crop_autocrop_enabled_button = gtk_builder.get_object('crop_autocrop_enabled_button')
        self.crop_enabled_button = gtk_builder.get_object('crop_enabled_button')
        self.crop_width_spinbutton = gtk_builder.get_object('crop_width_spinbutton')
        self.crop_height_spinbutton = gtk_builder.get_object('crop_height_spinbutton')
        self.crop_x_scale = gtk_builder.get_object('crop_x_scale')
        self.crop_y_scale = gtk_builder.get_object('crop_y_scale')
        self.scale_enabled_button = gtk_builder.get_object('scale_enabled_button')
        self.scale_width_spinbutton = gtk_builder.get_object('scale_width_spinbutton')
        self.scale_height_spinbutton = gtk_builder.get_object('scale_height_spinbutton')
        self.crop_width_adjustment = gtk_builder.get_object('crop_width_adjustment')
        self.crop_height_adjustment = gtk_builder.get_object('crop_height_adjustment')
        self.crop_x_adjustment = gtk_builder.get_object('crop_x_adjustment')
        self.crop_y_adjustment = gtk_builder.get_object('crop_y_adjustment')
        self.scale_width_adjustment = gtk_builder.get_object('scale_width_adjustment')
        self.scale_height_adjustment = gtk_builder.get_object('scale_height_adjustment')
        self.crop_controls_box = gtk_builder.get_object('crop_controls_box')
        self.scale_controls_box = gtk_builder.get_object('scale_controls_box')
        self.crop_preview_stack = gtk_builder.get_object('crop_preview_stack')
        self.crop_preview_viewport = gtk_builder.get_object('crop_preview_viewport')
        self.crop_reset = gtk_builder.get_object('crop_reset')

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)

        raise AttributeError

    def setup_crop_page(self):
        if not self.__setup_ffmpeg():
            return

        self.is_widgets_setting_up = True
        origin_width, origin_height = self.ffmpeg.width_origin, self.ffmpeg.height_origin

        self.crop_width_adjustment.set_upper(origin_width)
        self.crop_height_adjustment.set_upper(origin_height)
        self.__setup_crop_page_scale_widgets(origin_width, origin_height)
        self.__setup_crop_page_crop_widgets(origin_width, origin_height)

        self.is_widgets_setting_up = False

        threading.Thread(target=self.set_crop_thumbnail, args=()).start()

    def __setup_ffmpeg(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()

        if inputs_row is not None:
            self.ffmpeg = inputs_row.ffmpeg

            return True

        return False

    def __setup_crop_page_scale_widgets(self, origin_width, origin_height):
        if self.ffmpeg.picture_settings.scale is None:
            self.scale_enabled_button.set_active(False)
            self.scale_width_spinbutton.set_value(origin_width)
            self.scale_height_spinbutton.set_value(origin_height)
        else:
            scale_width, scale_height = self.ffmpeg.picture_settings.scale

            self.scale_enabled_button.set_active(True)
            self.scale_width_spinbutton.set_value(scale_width)
            self.scale_height_spinbutton.set_value(scale_height)

    def __setup_crop_page_crop_widgets(self, origin_width, origin_height):
        if self.ffmpeg.picture_settings.crop is None:
            self.crop_autocrop_enabled_button.set_active(False)
            self.crop_enabled_button.set_active(False)
            self.crop_enabled_button.set_sensitive(True)
            self.crop_width_spinbutton.set_value(origin_width)
            self.crop_height_spinbutton.set_value(origin_height)
            self.crop_x_adjustment.set_upper(0)
            self.crop_y_adjustment.set_upper(0)
        else:
            width, height, x_pad, y_pad = self.ffmpeg.picture_settings.crop

            if self.ffmpeg.picture_settings.auto_crop:
                self.set_auto_crop_state(True)
                self.crop_enabled_button.set_active(True)
            else:
                self.set_auto_crop_state(False)
                self.crop_enabled_button.set_active(True)

            self.crop_width_spinbutton.set_value(width)
            self.crop_height_spinbutton.set_value(height)
            self.crop_x_adjustment.set_upper(origin_width - width)
            self.crop_y_adjustment.set_upper(origin_height - height)
            self.crop_x_scale.set_value(x_pad)
            self.crop_y_scale.set_value(y_pad)

    def set_auto_crop_state(self, state):
        self.crop_autocrop_enabled_button.set_active(state)
        self.crop_enabled_button.set_sensitive(not state)

    def set_crop_thumbnail(self):
        output_file = preview.get_crop_preview_file(self.ffmpeg, self.preferences)
        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)
        widget_width = self.crop_preview_viewport.get_allocated_width()
        widget_height = self.crop_preview_viewport.get_allocated_height()

        self.set_thumbnail_size(widget_width, widget_height)

    def set_thumbnail_size(self, widget_width, widget_height):
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

        GLib.idle_add(self.crop_preview.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.crop_preview_stack.set_visible_child, self.crop_preview)
        GLib.idle_add(self.crop_preview.set_opacity, 1)

    def reset_crop_page(self):
        self.is_widgets_setting_up = True

        self.crop_autocrop_enabled_button.set_active(True)
        self.scale_enabled_button.set_active(False)
        self.crop_y_scale.set_value(0)
        self.crop_x_scale.set_value(0)
        self.crop_width_spinbutton.set_value(0)
        self.crop_height_spinbutton.set_value(0)
        self.scale_width_spinbutton.set_value(0)
        self.scale_height_spinbutton.set_value(0)
        self.crop_preview_stack.set_visible_child(self.crop_reset)
        self.crop_preview.set_opacity(0.5)

        self.is_widgets_setting_up = False

    def get_crop_x_value(self):
        return self.crop_x_scale.get_value()

    def get_crop_y_value(self):
        return self.crop_y_scale.get_value()

    def set_crop_x_value(self, crop_x_value):
        self.crop_x_scale.set_value(crop_x_value)

    def set_crop_x_upper_limit(self, upper_limit):
        self.crop_x_adjustment.set_upper(upper_limit)

    def set_crop_y_upper_limit(self, upper_limit):
        self.crop_y_adjustment.set_upper(upper_limit)

    def set_crop_y_value(self, crop_y_value):
        self.crop_y_scale.set_value(crop_y_value)

    def set_preview_viewport_width(self, width):
        self.crop_preview_viewport_width = width

    def set_preview_viewport_height(self, height):
        self.crop_preview_viewport_height = height

    def setup_crop_settings(self):
        self.__setup_crop_settings_from_crop_page_widgets()
        self.__setup_scale_settings_from_crop_page_widgets()
        self.inputs_page_handlers.get_selected_row().setup_labels()

    def __setup_crop_settings_from_crop_page_widgets(self):
        if self.crop_enabled_button.get_active():
            width = self.crop_width_spinbutton.get_value_as_int()
            height = self.crop_height_spinbutton.get_value_as_int()
            x = round(self.crop_x_scale.get_value())
            y = round(self.crop_y_scale.get_value())

            self.ffmpeg.picture_settings.crop = width, height, x, y
        else:
            self.ffmpeg.picture_settings.crop = None

    def __setup_scale_settings_from_crop_page_widgets(self):
        if self.scale_enabled_button.get_active():
            width = self.scale_width_spinbutton.get_value_as_int()
            height = self.scale_height_spinbutton.get_value_as_int()

            self.ffmpeg.picture_settings.scale = width, height
        else:
            self.ffmpeg.picture_settings.scale = None

    def set_crop_state(self, enabled):
        self.crop_controls_box.set_sensitive(enabled)

    def set_scale_state(self, enabled):
        self.scale_controls_box.set_sensitive(enabled)

    def update_autocrop_state(self):
        auto_crop_enabled = self.crop_autocrop_enabled_button.get_active()

        if auto_crop_enabled:
            self.crop_enabled_button.set_active(True)
            self.crop_enabled_button.set_sensitive(False)
            self.crop_controls_box.set_sensitive(False)
        else:
            self.crop_enabled_button.set_sensitive(True)

            if self.crop_enabled_button.get_active():
                self.crop_controls_box.set_sensitive(True)
