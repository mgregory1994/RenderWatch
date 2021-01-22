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

from encoding import preview
from startup import GLib, Gtk, GdkPixbuf


class CropPageHandlers:
    def __init__(self, gtk_builder, preferences):
        self.preferences = preferences
        self.ffmpeg = None
        self.inputs_page_handlers = None
        self.main_window_handlers = None
        self.image_buffer = None
        self.image_scale_buffer = None
        self.resize_thumbnail_thread = None
        self.crop_preview_viewport_width = 0
        self.crop_preview_viewport_height = 0
        self.__is_widgets_setting_up = False
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

    def setup_crop_page(self):
        if not self.__setup_ffmpeg():
            return

        self.__is_widgets_setting_up = True
        origin_width, origin_height = self.ffmpeg.width_origin, self.ffmpeg.height_origin

        self.crop_width_adjustment.set_upper(origin_width)
        self.crop_height_adjustment.set_upper(origin_height)
        self.__setup_crop_page_scale_widgets(origin_width, origin_height)
        self.__setup_crop_page_crop_widgets(origin_width, origin_height)

        self.__is_widgets_setting_up = False

        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

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
                self.__set_auto_crop_state(True)
                self.crop_enabled_button.set_active(True)
            else:
                self.__set_auto_crop_state(False)
                self.crop_enabled_button.set_active(True)

            self.crop_width_spinbutton.set_value(width)
            self.crop_height_spinbutton.set_value(height)
            self.crop_x_adjustment.set_upper(origin_width - width)
            self.crop_y_adjustment.set_upper(origin_height - height)
            self.crop_x_scale.set_value(x_pad)
            self.crop_y_scale.set_value(y_pad)

    def __set_auto_crop_state(self, state):
        self.crop_autocrop_enabled_button.set_active(state)
        self.crop_enabled_button.set_sensitive(not state)

    def __set_crop_thumbnail(self):
        output_file = preview.get_crop_preview_file(self.ffmpeg, self.preferences)
        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)
        widget_width = self.crop_preview_viewport.get_allocated_width()
        widget_height = self.crop_preview_viewport.get_allocated_height()

        self.__set_thumbnail_resize(widget_width, widget_height)

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

        GLib.idle_add(self.crop_preview.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.crop_preview_stack.set_visible_child, self.crop_preview)
        GLib.idle_add(self.crop_preview.set_opacity, 1)

    def reset_crop_page(self):
        self.__is_widgets_setting_up = True

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

        self.__is_widgets_setting_up = False

    def on_crop_autocrop_enabled_button_toggled(self, auto_crop_enabled_checkbox):
        auto_crop_enabled = auto_crop_enabled_checkbox.get_active()

        self.__setup_crop_page_widgets_for_auto_crop(auto_crop_enabled)

        if self.__is_widgets_setting_up:
            return

        if auto_crop_enabled:
            threading.Thread(target=self.__setup_autocrop, args=()).start()
        else:
            self.__setup_crop_settings()
            threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def __setup_crop_page_widgets_for_auto_crop(self, auto_crop_enabled):
        if auto_crop_enabled:
            self.crop_enabled_button.set_active(True)
            self.crop_enabled_button.set_sensitive(False)
            self.crop_controls_box.set_sensitive(False)
        else:
            self.crop_enabled_button.set_sensitive(True)

            if self.crop_enabled_button.get_active():
                self.crop_controls_box.set_sensitive(True)

    def __setup_autocrop(self):
        auto_crop_enabled = preview.process_auto_crop(self.ffmpeg)

        if auto_crop_enabled:
            self.ffmpeg.picture_settings.auto_crop = auto_crop_enabled

            self.__set_crop_thumbnail()
        else:
            GLib.idle_add(self.__show_auto_crop_not_needed_dialog)
            GLib.idle_add(self.__set_auto_crop_state, False)

    def __show_auto_crop_not_needed_dialog(self):
        message_dialog = Gtk.MessageDialog(
            self.main_window_handlers.main_window,
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            'Auto crop not needed'
        )

        message_dialog.format_secondary_text('Could not detect any \"black bars\" within the picture.')
        message_dialog.run()
        message_dialog.destroy()

    def on_crop_enabled_button_toggled(self, crop_enabled_checkbox):
        self.crop_controls_box.set_sensitive(crop_enabled_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        self.__setup_crop_settings()
        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def __setup_crop_settings(self):
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

    def on_crop_width_spinbutton_value_changed(self, crop_width_spinbutton):
        width, original_width = crop_width_spinbutton.get_value_as_int(), self.ffmpeg.width_origin
        upper_limit = original_width - width

        if self.crop_x_scale.get_value() > upper_limit:
            self.crop_x_scale.set_value(upper_limit)

        self.crop_x_adjustment.set_upper(upper_limit)

        if self.__is_widgets_setting_up:
            return

        self.__setup_crop_settings()
        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def on_crop_height_spinbutton_value_changed(self, crop_height_spinbutton):
        height, original_height = crop_height_spinbutton.get_value_as_int(), self.ffmpeg.height_origin
        upper_limit = original_height - height

        if self.crop_y_scale.get_value() > upper_limit:
            self.crop_y_scale.set_value(upper_limit)

        self.crop_y_adjustment.set_upper(upper_limit)

        if self.__is_widgets_setting_up:
            return

        self.__setup_crop_settings()
        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def on_crop_pad_changed(self, event, data):
        if not self.__is_widgets_setting_up:
            self.__setup_crop_settings()
            threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def on_scale_enabled_button_toggled(self, scale_enabled_checkbox):
        self.scale_controls_box.set_sensitive(scale_enabled_checkbox.get_active())

        if self.__is_widgets_setting_up:
            return

        self.__setup_crop_settings()
        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def on_scale_spinbutton_value_changed(self, scale_spinbutton):
        if self.__is_widgets_setting_up:
            return

        self.__setup_crop_settings()
        threading.Thread(target=self.__set_crop_thumbnail, args=()).start()

    def on_crop_preview_viewport_size_allocate(self, crop_preview_viewport, allocation):
        widget_width = crop_preview_viewport.get_allocated_width()
        widget_height = crop_preview_viewport.get_allocated_height()

        if not self.crop_preview_viewport_width == widget_width \
                or not self.crop_preview_viewport_height == widget_height:
            self.__set_thumbnail_resize(widget_width, widget_height)
            self.crop_preview_viewport_width = widget_width
            self.crop_preview_viewport_height = widget_height
