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

from render_watch.app_formatting import format_converter
from render_watch.encoding import preview
from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.signals.trim.trim_enabled_signal import TrimEnabledSignal
from render_watch.signals.trim.trim_start_signal import TrimStartSignal
from render_watch.signals.trim.trim_end_signal import TrimEndSignal
from render_watch.signals.trim.trim_preview_size_signal import TrimPreviewSizeSignal
from render_watch.startup import GLib, GdkPixbuf


class TrimPageHandlers:
    """
    Handles all widget changes on the trim page.
    """

    def __init__(self, gtk_builder, inputs_page_handlers, application_preferences):
        self.inputs_page_handlers = inputs_page_handlers
        self.application_preferences = application_preferences
        self.ffmpeg = None
        self.image_buffer = None
        self.image_scaled_buffer = None
        self.resize_thumbnail_thread = None
        self.trim_preview_viewport_width = 0
        self.trim_preview_viewport_height = 0
        self.is_widgets_setting_up = False

        self.trim_enabled_signal = TrimEnabledSignal(self)
        self.trim_start_signal = TrimStartSignal(self)
        self.trim_end_signal = TrimEndSignal(self)
        self.trim_preview_size_signal = TrimPreviewSizeSignal(self)
        self.signals_list = (
            self.trim_enabled_signal, self.trim_start_signal,
            self.trim_end_signal, self.trim_preview_size_signal
        )

        self.trim_selection_box = gtk_builder.get_object('trim_selection_box')
        self.trim_start_time_scale = gtk_builder.get_object('trim_start_time_scale')
        self.trim_end_time_scale = gtk_builder.get_object('trim_end_time_scale')
        self.trim_preview_icon = gtk_builder.get_object('trim_preview_icon')
        self.trim_no_preview_icon = gtk_builder.get_object('trim_no_preview_icon')
        self.trim_preview_stack = gtk_builder.get_object('trim_preview_stack')
        self.trim_enabled_checkbutton = gtk_builder.get_object('trim_enabled_checkbutton')
        self.trim_start_adjustment = gtk_builder.get_object('trim_start_adjustment')
        self.trim_end_adjustment = gtk_builder.get_object('trim_end_adjustment')
        self.trim_start_label = gtk_builder.get_object('trim_start_label')
        self.trim_start_time_label = gtk_builder.get_object('trim_start_time_label')
        self.trim_end_label = gtk_builder.get_object('trim_end_label')
        self.trim_end_time_label = gtk_builder.get_object('trim_end_time_label')
        self.trim_preview_viewport = gtk_builder.get_object('trim_preview_viewport')

    def __getattr__(self, signal_name):
        """
        If found, return the signal name's function from the list of signals.

        :param signal_name: The signal function name being looked for.
        """
        for signal in self.signals_list:
            if hasattr(signal, signal_name):
                return getattr(signal, signal_name)
        raise AttributeError

    def setup_trim_page(self):
        """
        Configures the trim page widgets to match the selected task's ffmpeg settings.
        """
        if self._setup_ffmpeg():
            self.is_widgets_setting_up = True
            self._setup_trim_page_scales()
            self._setup_trim_page_labels()
            self.is_widgets_setting_up = False
            self.run_trim_preview_thread()

    def _setup_ffmpeg(self):
        inputs_row = self.inputs_page_handlers.get_selected_row()
        if inputs_row:
            self.ffmpeg = inputs_row.ffmpeg

            return True
        return False

    def _setup_trim_page_scales(self):
        self.trim_start_adjustment.set_upper(self.ffmpeg.duration_origin)
        self.trim_end_adjustment.set_upper(self.ffmpeg.duration_origin)

        if self.ffmpeg.trim_settings:
            start_time = self.ffmpeg.trim_settings.start_time
            trim_duration = self.ffmpeg.trim_settings.trim_duration
            self.trim_start_time_scale.set_value(start_time)
            self.trim_end_time_scale.set_value(start_time + trim_duration)

            self.trim_enabled_checkbutton.set_active(True)
        else:
            self.trim_start_time_scale.set_value(0)
            self.trim_end_time_scale.set_value(self.trim_end_adjustment.get_upper())

            self.trim_enabled_checkbutton.set_active(False)

    def _setup_trim_page_labels(self):
        start_timecode = format_converter.get_timecode_from_seconds(self.trim_start_time_scale.get_value())
        end_timecode = format_converter.get_timecode_from_seconds(self.trim_end_time_scale.get_value())
        self.set_trim_start_text(start_timecode, is_bold_text_enabled=True)
        self.set_trim_end_text(end_timecode)

    def set_trim_start_text(self, trim_start_value_text, is_bold_text_enabled=False):
        if is_bold_text_enabled:
            self.trim_start_label.set_markup('<b>Trim Start:</b>')
            self.trim_start_time_label.set_markup('<b>' + trim_start_value_text + '</b>')

            self._disable_trim_end_label_bold_text()
        else:
            self.trim_start_label.set_text('Trim Start:')
            self.trim_start_time_label.set_text(trim_start_value_text)

    def _disable_trim_end_label_bold_text(self):
        end_time_in_seconds = round(self.trim_end_time_scale.get_value(), 1)
        end_timecode = format_converter.get_timecode_from_seconds(end_time_in_seconds)
        self.trim_end_label.set_text('Trim End:')
        self.trim_end_time_label.set_text(end_timecode)

    def set_trim_end_text(self, trim_end_value_text, is_bold_text_enabled=False):
        if is_bold_text_enabled:
            self.trim_end_label.set_markup('<b>Trim End:</b>')
            self.trim_end_time_label.set_markup('<b>' + trim_end_value_text + '</b>')

            self._disable_trim_start_label_bold_text()
        else:
            self.trim_end_label.set_text('Trim End:')
            self.trim_end_time_label.set_text(trim_end_value_text)

    def _disable_trim_start_label_bold_text(self):
        start_time_in_seconds = round(self.trim_start_time_scale.get_value(), 1)
        start_timecode = format_converter.get_timecode_from_seconds(start_time_in_seconds)
        self.trim_start_label.set_text('Trim Start:')
        self.trim_start_time_label.set_text(start_timecode)

    def run_trim_preview_thread(self, is_using_trim_end_time=False):
        """
        Generates a new trim preview image.
        """
        if is_using_trim_end_time:
            time = round(self.trim_end_time_scale.get_value(), 1)
        else:
            time = round(self.trim_start_time_scale.get_value(), 1)

        threading.Thread(target=self._set_preview_image, args=(time,)).start()

    def _set_preview_image(self, preview_position):
        output_file = preview.generate_trim_preview_file(self.ffmpeg, preview_position, self.application_preferences)
        self.image_buffer = GdkPixbuf.Pixbuf.new_from_file(output_file)

        widget_width = self.trim_preview_viewport.get_allocated_width()
        widget_height = self.trim_preview_viewport.get_allocated_height()
        GLib.idle_add(self.resize_trim_preview, widget_width, widget_height)

    def resize_trim_preview(self, widget_width, widget_height):
        """
        Resizes the trim preview image.
        """
        if self.image_buffer:
            image_width = self.image_buffer.get_width()
            image_height = self.image_buffer.get_height()
            width_ratio = widget_width / image_width
            height_ratio = widget_height / image_height
            aspect_ratio = min(width_ratio, height_ratio)
            scaled_width = image_width * aspect_ratio
            scaled_height = image_height * aspect_ratio

            self._run_resize_preview_thread(scaled_width, scaled_height)

    def _run_resize_preview_thread(self, scaled_width, scaled_height):
        if self.resize_thumbnail_thread is None or not self.resize_thumbnail_thread.is_alive():
            self.resize_thumbnail_thread = threading.Thread(target=self._resize_preview,
                                                            args=(scaled_width, scaled_height))
            self.resize_thumbnail_thread.start()

    def _resize_preview(self, scale_width, scale_height):
        self.image_scaled_buffer = self.image_buffer.scale_simple(scale_width,
                                                                  scale_height,
                                                                  GdkPixbuf.InterpType.BILINEAR)
        GLib.idle_add(self.trim_preview_icon.set_from_pixbuf, self.image_scaled_buffer)
        GLib.idle_add(self.trim_preview_stack.set_visible_child, self.trim_preview_icon)
        GLib.idle_add(self.trim_preview_icon.set_opacity, 1)

    def reset_trim_page(self):
        """
        Resets the trim page widgets to their default values.
        """
        self.is_widgets_setting_up = True
        self.trim_start_time_scale.set_value(0)
        self.trim_end_time_scale.set_value(self.trim_end_adjustment.get_upper())
        self.trim_preview_stack.set_visible_child(self.trim_no_preview_icon)
        self.trim_preview_icon.set_opacity(0.5)
        self.trim_enabled_checkbutton.set_active(False)
        self.is_widgets_setting_up = False

    def get_trim_start_value(self):
        return self.trim_start_time_scale.get_value()

    def get_trim_end_value(self):
        return self.trim_end_time_scale.get_value()

    def get_preview_viewport_width(self):
        return self.trim_preview_viewport_width

    def get_preview_viewport_height(self):
        return self.trim_preview_viewport_height

    def set_trim_start_value(self, trim_start_value):
        self.trim_start_time_scale.set_value(trim_start_value)

    def set_trim_end_value(self, trim_end_value):
        self.trim_end_time_scale.set_value(trim_end_value)

    def set_trim_state(self, enabled):
        self.trim_selection_box.set_sensitive(enabled)

    def set_preview_viewport_width(self, viewport_width):
        self.trim_preview_viewport_width = viewport_width

    def set_preview_viewport_height(self, viewport_height):
        self.trim_preview_viewport_height = viewport_height

    def apply_trim_settings(self):
        """
        Applies the trim settings to the selected task's ffmpeg settings.
        """
        if self.trim_enabled_checkbutton.get_active():
            start_time = round(self.trim_start_time_scale.get_value(), 1)
            duration = round(self.trim_end_time_scale.get_value() - start_time, 1)

            trim_settings = TrimSettings()
            trim_settings.start_time = start_time
            trim_settings.trim_duration = duration
            self.ffmpeg.trim_settings = trim_settings
        else:
            self.ffmpeg.trim_settings = None

        self.inputs_page_handlers.get_selected_row().setup_labels()
