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


import logging
import queue
import threading
import time

from render_watch.ui import Gtk, Gio, Gdk, GLib, Adw
from render_watch.encode import preview, benchmark
from render_watch.ffmpeg import encoding, trim, filters
from render_watch.helpers import format_converter
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
    """Class that contains the widgets that make up the application's crop page."""

    RESOLUTION_MIN = 240
    RESOLUTION_MAX = 7680

    def __init__(self, preview_generator: preview.PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the CropPage widgets class with the necessary variables for creating the application's crop page.

        Parameters:
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
            app_settings: Application settings.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.app_settings = app_settings
        self.encoding_task = None
        self.video_duration = None
        self.is_widgets_setting_up = False

        self._setup_crop_page_contents()

        self.crop_previewer = self.CropPreviewer(self, preview_generator)

        self.set_margin_top(10)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

    def _setup_crop_page_contents(self):
        # Instantiates all the widgets needed for the crop page.
        self._setup_preview_widgets()
        self._setup_crop_settings_widgets()
        self._setup_scale_settings_widgets()

        crop_page_settings_contents_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        crop_page_settings_contents_horizontal_box.append(self.crop_settings_group)
        crop_page_settings_contents_horizontal_box.append(self.scale_settings_group)

        self.append(self.preview_vertical_box)
        self.append(crop_page_settings_contents_horizontal_box)

    def _setup_preview_widgets(self):
        # Instantiates the preview widgets.
        self._setup_preview_picture()
        self._setup_preview_not_available_label()
        self._setup_preview_stack()
        self._setup_time_position_settings()

        self.preview_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.preview_vertical_box.append(self.preview_stack)
        self.preview_vertical_box.append(self.time_position_settings_group)

    def _setup_preview_picture(self):
        # Instantiates the preview picture widget.
        self.preview_picture = Gtk.Picture()
        self.preview_picture.content_fit = True
        self.preview_picture.set_can_shrink(True)
        self.preview_picture.set_keep_aspect_ratio(True)

    def _setup_preview_not_available_label(self):
        # Instantiates the preview not available label widget.
        self.preview_not_available_label = Gtk.Label(label='Preview Not Available')
        self.preview_not_available_label.add_css_class('dim-label')
        self.preview_not_available_label.set_vexpand(True)
        self.preview_not_available_label.set_valign(Gtk.Align.CENTER)
        self.preview_not_available_label.set_hexpand(True)
        self.preview_not_available_label.set_halign(Gtk.Align.CENTER)

    def _setup_preview_stack(self):
        # Instantiates the preview stack widget.
        self.preview_stack = Gtk.Stack()
        self.preview_stack.add_named(self.preview_not_available_label, 'not_available')
        self.preview_stack.add_named(self.preview_picture, 'preview')
        self.preview_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_time_position_settings(self):
        # Instantiates the preview time position widgets.
        self._setup_preview_time_position_row()

        self.time_position_settings_group = Adw.PreferencesGroup()
        self.time_position_settings_group.add(self.preview_time_position_row)

    def _setup_preview_time_position_row(self):
        # Instantiates the preview time position setting widgets.
        self._setup_preview_time_position_title_label()
        self._setup_preview_time_position_value_label()
        self._setup_preview_time_position_scale()

        titles_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        titles_vertical_box.append(self.preview_time_position_title_label)
        titles_vertical_box.append(self.preview_time_position_value_label)

        contents_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        contents_horizontal_box.append(titles_vertical_box)
        contents_horizontal_box.append(self.preview_time_position_scale)
        contents_horizontal_box.set_margin_top(10)
        contents_horizontal_box.set_margin_bottom(10)
        contents_horizontal_box.set_margin_start(10)
        contents_horizontal_box.set_margin_end(10)

        self.preview_time_position_row = Adw.ActionRow()
        self.preview_time_position_row.set_child(contents_horizontal_box)

    def _setup_preview_time_position_title_label(self):
        # Instantiates the preview time position title label widget.
        self.preview_time_position_title_label = Gtk.Label(label='Video Position')
        self.preview_time_position_title_label.set_vexpand(True)
        self.preview_time_position_title_label.set_valign(Gtk.Align.END)
        self.preview_time_position_title_label.set_hexpand(False)
        self.preview_time_position_title_label.set_halign(Gtk.Align.START)

    def _setup_preview_time_position_value_label(self):
        # Instantiates the preview time position value label widget.
        self.preview_time_position_value_label = Gtk.Label(label='##:##:##')
        self.preview_time_position_value_label.add_css_class('dim-label')
        self.preview_time_position_value_label.add_css_class('caption')
        self.preview_time_position_value_label.set_vexpand(True)
        self.preview_time_position_value_label.set_valign(Gtk.Align.START)
        self.preview_time_position_value_label.set_hexpand(False)
        self.preview_time_position_value_label.set_halign(Gtk.Align.START)

    def _setup_preview_time_position_scale(self):
        # Instantiates the preview time position scale widget.
        self.preview_time_position_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.1)
        self.preview_time_position_scale.set_value(0.0)
        self.preview_time_position_scale.set_digits(1)
        self.preview_time_position_scale.set_draw_value(False)
        self.preview_time_position_scale.set_hexpand(True)
        self.preview_time_position_scale.connect('value-changed', self.on_preview_time_position_scale_value_changed)

    def _setup_crop_settings_widgets(self):
        # Instantiates the crop settings widgets.
        self._setup_auto_crop_row()
        self._setup_crop_size_row()
        self._setup_crop_padding_row()
        self._setup_crop_settings_switch()

        self.crop_settings_group = Adw.PreferencesGroup()
        self.crop_settings_group.set_title('Crop Settings')
        self.crop_settings_group.set_header_suffix(self.crop_settings_switch)
        self.crop_settings_group.add(self.auto_crop_row)
        self.crop_settings_group.add(self.crop_size_row)
        self.crop_settings_group.add(self.crop_padding_row)

    def _setup_auto_crop_row(self):
        # Instantiates the auto crop setting widgets.
        self._setup_auto_crop_switch()

        self.auto_crop_row = Adw.ActionRow()
        self.auto_crop_row.set_title('Auto Crop')
        self.auto_crop_row.add_suffix(self.auto_crop_switch)
        self.auto_crop_row.set_sensitive(False)

    def _setup_auto_crop_switch(self):
        # Instantiates the auto crop switch widget.
        self.auto_crop_switch = Gtk.Switch()
        self.auto_crop_switch.set_vexpand(False)
        self.auto_crop_switch.set_valign(Gtk.Align.CENTER)
        self.auto_crop_switch.connect('state-set', self.on_auto_crop_switch_state_set)

    def _setup_crop_size_row(self):
        # Instantiates the crop size setting widgets.
        self._setup_crop_width_label()
        self._setup_crop_width_spin_button()
        self._setup_crop_height_label()
        self._setup_crop_height_spin_button()
        self._setup_crop_size_title_label()

        crop_width_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        crop_width_horizontal_box.append(self.crop_width_label)
        crop_width_horizontal_box.append(self.crop_width_spin_button)

        crop_height_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        crop_height_horizontal_box.append(self.crop_height_label)
        crop_height_horizontal_box.append(self.crop_height_spin_button)

        crop_settings_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        crop_settings_horizontal_box.append(crop_width_horizontal_box)
        crop_settings_horizontal_box.append(crop_height_horizontal_box)
        crop_settings_horizontal_box.set_hexpand(True)
        crop_settings_horizontal_box.set_halign(Gtk.Align.END)

        crop_size_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        crop_size_horizontal_box.append(self.crop_size_title_label)
        crop_size_horizontal_box.append(crop_settings_horizontal_box)
        crop_size_horizontal_box.set_margin_top(10)
        crop_size_horizontal_box.set_margin_bottom(10)
        crop_size_horizontal_box.set_margin_start(10)
        crop_size_horizontal_box.set_margin_end(10)

        self.crop_size_row = Adw.ActionRow()
        self.crop_size_row.set_child(crop_size_horizontal_box)
        self.crop_size_row.set_sensitive(False)

    def _setup_crop_width_label(self):
        # Instantiates the crop width label widget.
        self.crop_width_label = Gtk.Label(label='Width')
        self.crop_width_label.set_vexpand(True)
        self.crop_width_label.set_valign(Gtk.Align.CENTER)
        self.crop_width_label.set_hexpand(False)
        self.crop_width_label.set_halign(Gtk.Align.START)

    def _setup_crop_width_spin_button(self):
        # Instantiates the crop width spin button widget.
        self.crop_width_spin_button = Gtk.SpinButton()
        self.crop_width_spin_button.set_range(self.RESOLUTION_MIN, self.RESOLUTION_MAX)
        self.crop_width_spin_button.set_digits(0)
        self.crop_width_spin_button.set_increments(120, 1024)
        self.crop_width_spin_button.set_numeric(True)
        self.crop_width_spin_button.set_value(240)
        self.crop_width_spin_button.set_size_request(125, -1)
        self.crop_width_spin_button.set_vexpand(False)
        self.crop_width_spin_button.set_valign(Gtk.Align.CENTER)
        self.crop_width_spin_button.connect('value-changed', self.on_crop_width_spin_button_value_changed)

    def _setup_crop_height_label(self):
        # Instantiates the crop height label widget.
        self.crop_height_label = Gtk.Label(label='Height')
        self.crop_height_label.set_vexpand(True)
        self.crop_height_label.set_valign(Gtk.Align.CENTER)
        self.crop_height_label.set_hexpand(False)
        self.crop_height_label.set_halign(Gtk.Align.START)

    def _setup_crop_height_spin_button(self):
        # Instantiates the crop height spin button widget.
        self.crop_height_spin_button = Gtk.SpinButton()
        self.crop_height_spin_button.set_range(self.RESOLUTION_MIN, self.RESOLUTION_MAX)
        self.crop_height_spin_button.set_digits(0)
        self.crop_height_spin_button.set_increments(120, 1024)
        self.crop_height_spin_button.set_numeric(True)
        self.crop_height_spin_button.set_value(240)
        self.crop_height_spin_button.set_size_request(125, -1)
        self.crop_height_spin_button.set_vexpand(False)
        self.crop_height_spin_button.set_valign(Gtk.Align.CENTER)
        self.crop_height_spin_button.connect('value-changed', self.on_crop_height_spin_button_value_changed)

    def _setup_crop_size_title_label(self):
        # Instantiates the crop size title label widget.
        self.crop_size_title_label = Gtk.Label(label='Size')
        self.crop_size_title_label.set_vexpand(True)
        self.crop_size_title_label.set_valign(Gtk.Align.CENTER)

    def _setup_crop_padding_row(self):
        # Instantiates the crop padding setting widgets.
        self._setup_crop_x_padding_title_label()
        self._setup_crop_x_padding_spin_button()
        self._setup_crop_y_padding_title_label()
        self._setup_crop_y_padding_spin_button()
        self._setup_crop_padding_title_label()

        crop_x_padding_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        crop_x_padding_horizontal_box.append(self.crop_x_padding_title_label)
        crop_x_padding_horizontal_box.append(self.crop_x_padding_spin_button)

        crop_y_padding_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        crop_y_padding_horizontal_box.append(self.crop_y_padding_title_label)
        crop_y_padding_horizontal_box.append(self.crop_y_padding_spin_button)

        crop_padding_settings_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        crop_padding_settings_horizontal_box.append(crop_x_padding_horizontal_box)
        crop_padding_settings_horizontal_box.append(crop_y_padding_horizontal_box)
        crop_padding_settings_horizontal_box.set_hexpand(True)
        crop_padding_settings_horizontal_box.set_halign(Gtk.Align.END)

        crop_padding_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        crop_padding_horizontal_box.append(self.crop_padding_title_label)
        crop_padding_horizontal_box.append(crop_padding_settings_horizontal_box)
        crop_padding_horizontal_box.set_margin_top(10)
        crop_padding_horizontal_box.set_margin_bottom(10)
        crop_padding_horizontal_box.set_margin_start(10)
        crop_padding_horizontal_box.set_margin_end(10)

        self.crop_padding_row = Adw.ActionRow()
        self.crop_padding_row.set_child(crop_padding_horizontal_box)
        self.crop_padding_row.set_sensitive(False)

    def _setup_crop_x_padding_title_label(self):
        # Instantiates the crop x padding title label widget.
        self.crop_x_padding_title_label = Gtk.Label(label='X')
        self.crop_x_padding_title_label.set_vexpand(True)
        self.crop_x_padding_title_label.set_valign(Gtk.Align.CENTER)
        self.crop_x_padding_title_label.set_hexpand(False)
        self.crop_x_padding_title_label.set_halign(Gtk.Align.END)

    def _setup_crop_x_padding_spin_button(self):
        # Instantiates the crop x padding spin button widget.
        self.crop_x_padding_spin_button = Gtk.SpinButton()
        self.crop_x_padding_spin_button.set_digits(0)
        self.crop_x_padding_spin_button.set_increments(1, 10)
        self.crop_x_padding_spin_button.set_numeric(True)
        self.crop_x_padding_spin_button.set_value(0)
        self.crop_x_padding_spin_button.set_size_request(125, -1)
        self.crop_x_padding_spin_button.set_vexpand(False)
        self.crop_x_padding_spin_button.set_valign(Gtk.Align.CENTER)
        self.crop_x_padding_spin_button.connect('value-changed', self.on_crop_x_padding_spin_button_value_changed)

    def _setup_crop_y_padding_title_label(self):
        # Instantiates the crop y padding title label widget.
        self.crop_y_padding_title_label = Gtk.Label(label='Y')
        self.crop_y_padding_title_label.set_vexpand(True)
        self.crop_y_padding_title_label.set_valign(Gtk.Align.CENTER)
        self.crop_y_padding_title_label.set_hexpand(False)
        self.crop_y_padding_title_label.set_halign(Gtk.Align.END)

    def _setup_crop_y_padding_spin_button(self):
        # Instantiates the crop y padding spin button widget.
        self.crop_y_padding_spin_button = Gtk.SpinButton()
        self.crop_y_padding_spin_button.set_digits(0)
        self.crop_y_padding_spin_button.set_increments(1, 10)
        self.crop_y_padding_spin_button.set_numeric(True)
        self.crop_y_padding_spin_button.set_value(0)
        self.crop_y_padding_spin_button.set_size_request(125, -1)
        self.crop_y_padding_spin_button.set_vexpand(False)
        self.crop_y_padding_spin_button.set_valign(Gtk.Align.CENTER)
        self.crop_y_padding_spin_button.connect('value-changed', self.on_crop_y_padding_spin_button_value_changed)

    def _setup_crop_padding_title_label(self):
        # Instantiates the crop padding title label widget.
        self.crop_padding_title_label = Gtk.Label(label='Padding')
        self.crop_padding_title_label.set_vexpand(True)
        self.crop_padding_title_label.set_valign(Gtk.Align.CENTER)

    def _setup_crop_settings_switch(self):
        # Instantiates the crop settings switch widget.
        self.crop_settings_switch = Gtk.Switch()
        self.crop_settings_switch.set_vexpand(False)
        self.crop_settings_switch.set_valign(Gtk.Align.CENTER)
        self.crop_settings_switch.connect('state-set', self.on_crop_settings_switch_state_set)

    def _setup_scale_settings_widgets(self):
        # Instantiates the scale settings widgets.
        self._setup_scale_size_row()
        self._setup_scale_settings_switch()

        self.scale_settings_group = Adw.PreferencesGroup()
        self.scale_settings_group.set_title('Scale Settings')
        self.scale_settings_group.set_header_suffix(self.scale_settings_switch)
        self.scale_settings_group.add(self.scale_size_row)

    def _setup_scale_size_row(self):
        # Instantiates the scale size setting widgets.
        self._setup_scale_width_label()
        self._setup_scale_width_spin_button()
        self._setup_scale_height_label()
        self._setup_scale_height_spin_button()
        self._setup_scale_size_title_label()

        scale_width_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        scale_width_horizontal_box.append(self.scale_width_label)
        scale_width_horizontal_box.append(self.scale_width_spin_button)

        scale_height_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        scale_height_horizontal_box.append(self.scale_height_label)
        scale_height_horizontal_box.append(self.scale_height_spin_button)

        scale_settings_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        scale_settings_horizontal_box.append(scale_width_horizontal_box)
        scale_settings_horizontal_box.append(scale_height_horizontal_box)
        scale_settings_horizontal_box.set_hexpand(True)
        scale_settings_horizontal_box.set_halign(Gtk.Align.END)

        scale_size_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        scale_size_horizontal_box.append(self.scale_size_title_label)
        scale_size_horizontal_box.append(scale_settings_horizontal_box)
        scale_size_horizontal_box.set_margin_top(10)
        scale_size_horizontal_box.set_margin_bottom(10)
        scale_size_horizontal_box.set_margin_start(10)
        scale_size_horizontal_box.set_margin_end(10)

        self.scale_size_row = Adw.ActionRow()
        self.scale_size_row.set_child(scale_size_horizontal_box)
        self.scale_size_row.set_sensitive(False)

    def _setup_scale_width_label(self):
        # Instantiates the scale width label widget.
        self.scale_width_label = Gtk.Label(label='Width')
        self.scale_width_label.set_vexpand(True)
        self.scale_width_label.set_valign(Gtk.Align.CENTER)
        self.scale_width_label.set_hexpand(False)
        self.scale_width_label.set_halign(Gtk.Align.START)

    def _setup_scale_width_spin_button(self):
        # Instantiates the scale width spin button widget.
        self.scale_width_spin_button = Gtk.SpinButton()
        self.scale_width_spin_button.set_range(self.RESOLUTION_MIN, self.RESOLUTION_MAX)
        self.scale_width_spin_button.set_digits(0)
        self.scale_width_spin_button.set_increments(120, 1024)
        self.scale_width_spin_button.set_numeric(True)
        self.scale_width_spin_button.set_value(240)
        self.scale_width_spin_button.set_size_request(125, -1)
        self.scale_width_spin_button.set_vexpand(False)
        self.scale_width_spin_button.set_valign(Gtk.Align.CENTER)
        self.scale_width_spin_button.connect('value-changed', self.on_scale_width_spin_button_value_changed)

    def _setup_scale_height_label(self):
        # Instantiates the scale height label widget.
        self.scale_height_label = Gtk.Label(label='Height')
        self.scale_height_label.set_vexpand(True)
        self.scale_height_label.set_valign(Gtk.Align.CENTER)
        self.scale_height_label.set_hexpand(False)
        self.scale_height_label.set_halign(Gtk.Align.START)

    def _setup_scale_height_spin_button(self):
        # Instantiates the scale height spin button widget.
        self.scale_height_spin_button = Gtk.SpinButton()
        self.scale_height_spin_button.set_range(self.RESOLUTION_MIN, self.RESOLUTION_MAX)
        self.scale_height_spin_button.set_digits(0)
        self.scale_height_spin_button.set_increments(120, 1024)
        self.scale_height_spin_button.set_numeric(True)
        self.scale_height_spin_button.set_value(240)
        self.scale_height_spin_button.set_size_request(125, -1)
        self.scale_height_spin_button.set_vexpand(False)
        self.scale_height_spin_button.set_valign(Gtk.Align.CENTER)
        self.scale_height_spin_button.connect('value-changed', self.on_scale_height_spin_button_value_changed)

    def _setup_scale_size_title_label(self):
        # Instantiates the scale size title label widget.
        self.scale_size_title_label = Gtk.Label(label='Size')
        self.scale_size_title_label.set_vexpand(True)
        self.scale_size_title_label.set_valign(Gtk.Align.CENTER)
        self.scale_size_title_label.set_hexpand(False)
        self.scale_size_title_label.set_halign(Gtk.Align.CENTER)

    def _setup_scale_settings_switch(self):
        # Instantiates the scale settings switch widget.
        self.scale_settings_switch = Gtk.Switch()
        self.scale_settings_switch.set_vexpand(False)
        self.scale_settings_switch.set_valign(Gtk.Align.CENTER)
        self.scale_settings_switch.connect('state-set', self.on_scale_settings_switch_state_set)

    def set_crop_state_enabled(self, is_state_enabled: bool):
        """
        Sets the state of the crop widgets to reflect whether the crop settings are enabled.

        Parameters:
             is_state_enabled: Boolean that represents whether the crop settings are enabled.
        """
        self.auto_crop_row.set_sensitive(is_state_enabled)
        self.crop_size_row.set_sensitive(is_state_enabled and not self.auto_crop_switch.get_active())
        self.crop_padding_row.set_sensitive(is_state_enabled and not self.auto_crop_switch.get_active())

    def set_auto_crop_state_enabled(self, is_state_enabled: bool):
        """
        Sets the state of the auto crop widgets to reflect whether the auto crop setting is enabled.

        Parameters:
            is_state_enabled: Boolean that represents whether the auto crop setting is enabled.
        """
        self.crop_size_row.set_sensitive(not is_state_enabled)
        self.crop_padding_row.set_sensitive(not is_state_enabled)

    def set_scale_state_enabled(self, is_state_enabled: bool):
        """
        Sets the state of the scale widgets to reflect whether the scale settings are enabled.

        Parameters:
            is_state_enabled: Boolean that represents whether the scale settings are enabled.
        """
        self.scale_size_row.set_sensitive(is_state_enabled)

    def set_widgets_setting_up(self, is_widgets_setting_up: bool):
        """
        Sets whether the widgets are being set up for a new encoding task.

        Parameters:
            is_widgets_setting_up: Boolean that represents whether the widgets are being set up for a new encoding task.
        """
        self.is_widgets_setting_up = is_widgets_setting_up

    def update_crop_size_range(self):
        """
        Uses the encoding task's selected video stream's dimensions to set the range for the
        crop width and height spin buttons.
        """
        origin_width = self.encoding_task.video_stream.width
        origin_height = self.encoding_task.video_stream.height

        self.crop_width_spin_button.set_range(self.RESOLUTION_MIN, origin_width)
        self.crop_height_spin_button.set_range(self.RESOLUTION_MIN, origin_height)

    def update_crop_padding_range(self):
        """
        Uses the encoding task's selected video stream's dimensions to set the range for the
        crop x and y padding spin buttons.
        """
        origin_width = self.encoding_task.video_stream.width
        origin_height = self.encoding_task.video_stream.height
        x_pad = self.crop_x_padding_spin_button.get_value_as_int()
        y_pad = self.crop_y_padding_spin_button.get_value_as_int()
        x_padding_max = origin_width - self.crop_width_spin_button.get_value_as_int()
        y_padding_max = origin_height - self.crop_height_spin_button.get_value_as_int()

        self.crop_x_padding_spin_button.set_range(0, x_padding_max)
        self.crop_y_padding_spin_button.set_range(0, y_padding_max)

        if x_pad > x_padding_max:
            self.crop_x_padding_spin_button.set_value(x_padding_max)

        if y_pad > y_padding_max:
            self.crop_y_padding_spin_button.set_value(y_padding_max)

    def update_preview_position_range(self):
        """
        Uses the encoding task's selected video stream's duration to set the range for the preview time position scale.
        """
        video_duration = self.encoding_task.input_file.duration

        self.preview_time_position_scale.set_range(min=0.0, max=video_duration)
        self.preview_time_position_scale.set_value(round(video_duration / 2.0, 1))
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(video_duration / 2.0))

    def apply_settings_to_widgets(self, encoding_task: encoding.Task):
        """
        Applies the given encoding task's settings to the crop page's widgets.

        Parameters:
            encoding_task: Encoding task to apply to the crop page's widgets.
        """
        if self.encoding_task is encoding_task:
            return

        self.encoding_task = encoding_task

        GLib.idle_add(self.set_widgets_setting_up, True)
        GLib.idle_add(self.update_crop_size_range)
        GLib.idle_add(self.update_preview_position_range)
        self._apply_crop_preview_to_widgets()
        self._apply_crop_enabled_setting_to_widgets()
        self._apply_crop_settings_to_widgets()
        self._apply_scale_enabled_setting_to_widgets()
        self._apply_scale_settings_to_widgets()
        GLib.idle_add(self.set_widgets_setting_up, False)

    def _apply_crop_preview_to_widgets(self):
        # Applies the encoding task's settings to the preview picture widget.
        GLib.idle_add(self.preview_picture.set_filename, self.encoding_task.temp_output_file.crop_preview_file_path)
        GLib.idle_add(self.preview_stack.set_visible_child_name, 'preview')

    def _apply_crop_enabled_setting_to_widgets(self):
        # Applies the encoding task's settings to the crop enabled settings widgets.
        GLib.idle_add(self.crop_settings_switch.set_active, self.encoding_task.filter.crop is not None)
        GLib.idle_add(self.auto_crop_switch.set_active, self.encoding_task.filter.crop.auto_crop_enabled)

    def _apply_crop_settings_to_widgets(self):
        # Applies the encoding task's settings to the crop settings widgets.
        if self.encoding_task.filter.is_crop_enabled():
            width, height, x_pad, y_pad = self.encoding_task.filter.crop.dimensions

            GLib.idle_add(self.crop_width_spin_button.set_value, width)
            GLib.idle_add(self.crop_height_spin_button.set_value, height)
            GLib.idle_add(self.update_crop_padding_range)
            GLib.idle_add(self.crop_x_padding_spin_button.set_value, x_pad)
            GLib.idle_add(self.crop_y_padding_spin_button.set_value, y_pad)
        else:
            origin_width = self.encoding_task.video_stream.width
            origin_height = self.encoding_task.video_stream.height

            GLib.idle_add(self.crop_width_spin_button.set_value, origin_width)
            GLib.idle_add(self.crop_height_spin_button.set_value, origin_height)
            GLib.idle_add(self.update_crop_padding_range)
            GLib.idle_add(self.crop_x_padding_spin_button.set_value, 0)
            GLib.idle_add(self.crop_y_padding_spin_button.set_value, 0)

    def _apply_scale_enabled_setting_to_widgets(self):
        # Applies the encoding task's settings to the scale enabled settings widget.
        GLib.idle_add(self.scale_settings_switch.set_active, (self.encoding_task.filter.scale is not None))

    def _apply_scale_settings_to_widgets(self):
        # Applies the encoding task's settings to the scale settings widgets.
        if self.encoding_task.filter.is_scale_enabled():
            width, height = self.encoding_task.filter.scale.dimensions

            GLib.idle_add(self.scale_width_spin_button.set_value, width)
            GLib.idle_add(self.scale_height_spin_button.set_value, height)
        else:
            origin_width = self.encoding_task.video_stream.width
            origin_height = self.encoding_task.video_stream.height

            GLib.idle_add(self.scale_width_spin_button.set_value, origin_width)
            GLib.idle_add(self.scale_height_spin_button.set_value, origin_height)

    def apply_settings_from_widgets(self):
        """Applies the state of the crop page's widgets to the encoding task."""
        self._apply_crop_settings_from_widgets()
        self._apply_scale_settings_from_widgets()

    def _apply_crop_settings_from_widgets(self):
        # Applies the state of the crop settings widgets to the encoding task.
        if self.crop_settings_switch.get_active():
            if self.auto_crop_switch.get_active():
                crop_settings = filters.Crop(self.encoding_task, self.app_settings)
            else:
                width = self.crop_width_spin_button.get_value_as_int()
                height = self.crop_height_spin_button.get_value_as_int()
                x_pad = self.crop_x_padding_spin_button.get_value_as_int()
                y_pad = self.crop_y_padding_spin_button.get_value_as_int()

                crop_settings = filters.Crop(self.encoding_task, self.app_settings, autocrop=False)
                crop_settings.dimensions = (width, height, x_pad, y_pad)

            self.encoding_task.filter.crop = crop_settings
        else:
            self.encoding_task.filter.crop = None

        GLib.idle_add(self.update_crop_padding_range)

    def _apply_scale_settings_from_widgets(self):
        # Applies the state of the scale widgets to the encoding task.
        if self.scale_settings_switch.get_active():
            width = self.scale_width_spin_button.get_value_as_int()
            height = self.scale_height_spin_button.get_value_as_int()

            scale_settings = filters.Scale()
            scale_settings.dimensions = (width, height)
            self.encoding_task.filter.scale = scale_settings
        else:
            self.encoding_task.filter.scale = None

    def on_preview_time_position_scale_value_changed(self, scale):
        """
        Signal callback function for the preview time position scale's 'value-changed' signal.
        Updates the preview time position value label to reflect what time position is set and generates a new preview.

        Parameters:
            scale: Gtk.Scale that emitted the signal.
        """
        scale_value = scale.get_value()
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(scale_value))

        self.crop_previewer.add_preview_task(self.encoding_task, scale_value)

    def on_crop_settings_switch_state_set(self, switch, user_data=None):
        """
        Signal callback function for the crop settings switch's 'state-set' signal.
        Sets the state of the crop settings widgets and generates a new preview.

        Parameters:
            switch: Gtk.Switch that emitted the signal.
            user_data: Additional data passed from the signal.
        """
        self.set_crop_state_enabled(switch.get_active())

        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_auto_crop_switch_state_set(self, switch, user_data=None):
        """
        Signal callback function for the auto crop switch's 'state-set' signal.
        Sets the state of the crop settings and generates a new preview.

        Parameters:
            switch: Gtk.Switch that emitted the signal.
            user_data: Additional data passed from the signal.
        """
        self.set_auto_crop_state_enabled(switch.get_active())

        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_crop_width_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop width spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_crop_height_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop height spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_crop_x_padding_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop x padding spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_crop_y_padding_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop y padding spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_scale_settings_switch_state_set(self, switch, user_data=None):
        """
        Signal callback function for the scale settings switch's 'state-set' signal.
        Sets the state of the scale settings widgets and generates a new preview.

        Parameters:
            switch: Gtk.Switch that emitted the signal.
            user_data: Additional data passed from the signal.
        """
        self.set_scale_state_enabled(switch.get_active())

        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_scale_width_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the scale width spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    def on_scale_height_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the scale height spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.crop_previewer.add_preview_task(self.encoding_task, self.preview_time_position_scale.get_value())

    class CropPreviewer:
        """Class that manages the preview queue and generates a new preview for each request."""

        def __init__(self, crop_page, preview_generator: preview.PreviewGenerator):
            """
            Initializes the CropPreviewer class with the necessary variables for managing the crop previewer.

            Parameters:
                crop_page: The crop page to manage previews for.
                preview_generator: preview.PreviewGenerator to send preview requests to.
            """
            self._crop_page = crop_page
            self._preview_generator = preview_generator
            self._preview_queue = queue.Queue()

            threading.Thread(target=self._preview_queue_loop, args=()).start()

        def _preview_queue_loop(self):
            # The loop that consumes the preview queue in order to process crop preview requests.
            while True:
                encoding_task, time_position = self._preview_queue.get()

                GLib.idle_add(self._crop_page.preview_picture.set_opacity, 0.5)

                if not encoding_task:
                    return

                time.sleep(0.1)

                while not self._preview_queue.empty():
                    with self._preview_queue.mutex:
                        encoding_task, time_position = self._preview_queue.queue[-1]

                        self._preview_queue.queue.clear()

                    time.sleep(0.1)

                self._crop_page.apply_settings_from_widgets()
                self._generate_preview(encoding_task, time_position)

                GLib.idle_add(self._crop_page.preview_picture.set_opacity, 1.0)

        def _generate_preview(self, encoding_task: encoding.Task, time_position: float):
            # Uses the preview generator to generate a new crop preview.
            self._preview_generator.generate_crop_preview(encoding_task, time_position)
            self._wait_for_preview_generation(encoding_task)

            GLib.idle_add(self._crop_page.preview_picture.set_filename,
                          encoding_task.temp_output_file.crop_preview_file_path)

        @staticmethod
        def _wait_for_preview_generation( encoding_task: encoding.Task):
            # Waits for the preview generator to finish creating the crop preview file.
            if encoding_task.temp_output_file.crop_preview_threading_event.is_set():
                encoding_task.temp_output_file.crop_preview_threading_event.clear()

            encoding_task.temp_output_file.crop_preview_threading_event.wait()

        def add_preview_task(self, encoding_task: encoding.Task, time_position: int | float):
            """
            Adds the given encoding task and time position to the preview queue in order to request a new crop preview.

            Parameters:
                encoding_task: Encoding task to send to the preview queue.
                time_position: Time position (in seconds) to use for the crop preview.
            """
            self._preview_queue.put((encoding_task, time_position))

        def kill(self):
            """Empties the preview queue and stops the preview queue loop."""
            while not self._preview_queue.empty():
                self._preview_queue.get()

            self._preview_queue.put((False, False))


class TrimPage(Gtk.Box):
    """Class that contains the widgets that make up the application's trim page."""

    TRIM_DURATION_LABEL = 'Duration: '

    def __init__(self, preview_generator: preview.PreviewGenerator):
        """
        Initializes the TrimPage widgets class with the necessary variables for creating the application's trim page.

        Parameters:
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.encoding_task = None
        self.video_duration = None
        self.is_widgets_setting_up = False

        self._setup_trim_page_contents()

        self.trim_previewer = self.TrimPreviewer(self, preview_generator)

        self.set_margin_top(10)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

    def _setup_trim_page_contents(self):
        # Instantiates all of the widgets needed for the trim page.
        self._setup_preview_widgets()
        self._setup_trim_settings_widgets()

        self.append(self.preview_stack)
        self.append(self.trim_settings_group)

    def _setup_preview_widgets(self):
        # Instantiates the widgets for the previewer on the trim page.
        self._setup_preview_picture()
        self._setup_preview_placeholder_icon()
        self._setup_preview_not_available_label()

        self.preview_stack = Gtk.Stack()
        self.preview_stack.add_named(self.audio_icon, 'audio')
        self.preview_stack.add_named(self.preview_not_available_label, 'not_available')
        self.preview_stack.add_named(self.preview_picture, 'preview')
        self.preview_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_preview_picture(self):
        # Instantiates the preview picture widget.
        self.preview_picture = Gtk.Picture()
        self.preview_picture.content_fit = True
        self.preview_picture.set_can_shrink(True)
        self.preview_picture.set_keep_aspect_ratio(True)

    def _setup_preview_placeholder_icon(self):
        # Instantiates the preview placeholder widget.
        self.audio_icon = Gtk.Image.new_from_icon_name('audio-x-generic-symbolic')
        self.audio_icon.set_pixel_size(128)
        self.audio_icon.add_css_class('dim-label')
        self.audio_icon.set_vexpand(True)
        self.audio_icon.set_valign(Gtk.Align.CENTER)
        self.audio_icon.set_hexpand(True)
        self.audio_icon.set_halign(Gtk.Align.CENTER)

    def _setup_preview_not_available_label(self):
        # Instantiates the preview not available widget.
        self.preview_not_available_label = Gtk.Label(label='Preview Not Available')
        self.preview_not_available_label.add_css_class('dim-label')
        self.preview_not_available_label.set_vexpand(True)
        self.preview_not_available_label.set_valign(Gtk.Align.CENTER)
        self.preview_not_available_label.set_hexpand(True)
        self.preview_not_available_label.set_halign(Gtk.Align.CENTER)

    def _setup_trim_settings_widgets(self):
        # Instantiates the trim widgets on the trim page.
        self._setup_trim_start_row()
        self._setup_trim_end_row()
        self._setup_trim_settings_suffix_content()

        self.trim_settings_group = Adw.PreferencesGroup()
        self.trim_settings_group.set_title('Trim Settings')
        self.trim_settings_group.set_header_suffix(self.trim_settings_suffix_content_horizontal_box)
        self.trim_settings_group.add(self.trim_start_row)
        self.trim_settings_group.add(self.trim_end_row)

    def _setup_trim_start_row(self):
        # Instantiates the trim start time widgets.
        self._setup_trim_start_title_label()
        self._setup_trim_start_subtitle_label()
        self._setup_trim_start_scale()

        titles_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        titles_vertical_box.append(self.trim_start_title_label)
        titles_vertical_box.append(self.trim_start_timecode_label)

        contents_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        contents_horizontal_box.append(titles_vertical_box)
        contents_horizontal_box.append(self.trim_start_scale)
        contents_horizontal_box.set_margin_top(10)
        contents_horizontal_box.set_margin_bottom(10)
        contents_horizontal_box.set_margin_start(10)
        contents_horizontal_box.set_margin_end(10)

        self.trim_start_row = Adw.ActionRow()
        self.trim_start_row.set_child(contents_horizontal_box)
        self.trim_start_row.set_sensitive(False)

    def _setup_trim_start_title_label(self):
        # Instantiates the trim start time label widget.
        self.trim_start_title_label = Gtk.Label(label='Trim Start')
        self.trim_start_title_label.set_vexpand(True)
        self.trim_start_title_label.set_valign(Gtk.Align.END)
        self.trim_start_title_label.set_hexpand(False)
        self.trim_start_title_label.set_halign(Gtk.Align.START)

    def _setup_trim_start_subtitle_label(self):
        # Instantiates the trim start timecode label widget.
        self.trim_start_timecode_label = Gtk.Label(label='00:00:00')
        self.trim_start_timecode_label.add_css_class('dim-label')
        self.trim_start_timecode_label.add_css_class('caption')
        self.trim_start_timecode_label.set_vexpand(True)
        self.trim_start_timecode_label.set_valign(Gtk.Align.START)
        self.trim_start_timecode_label.set_hexpand(False)
        self.trim_start_timecode_label.set_halign(Gtk.Align.START)

    def _setup_trim_start_scale(self):
        # Instantiates the trim start scale widget.
        self.trim_start_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                         min=0.0,
                                                         max=1.0,
                                                         step=0.1)
        self.trim_start_scale.set_value(0.0)
        self.trim_start_scale.set_digits(1)
        self.trim_start_scale.set_draw_value(False)
        self.trim_start_scale.set_hexpand(True)
        self.trim_start_scale.connect('adjust-bounds', self.on_trim_start_scale_adjust_bounds)

    def _setup_trim_end_row(self):
        # Instantiates the trim end time widgets.
        self._setup_trim_end_title_label()
        self._setup_trim_end_subtitle_label()
        self._setup_trim_end_scale()

        titles_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        titles_vertical_box.append(self.trim_end_title_label)
        titles_vertical_box.append(self.trim_end_timecode_label)

        contents_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        contents_horizontal_box.append(titles_vertical_box)
        contents_horizontal_box.append(self.trim_end_scale)
        contents_horizontal_box.set_margin_top(10)
        contents_horizontal_box.set_margin_bottom(10)
        contents_horizontal_box.set_margin_start(10)
        contents_horizontal_box.set_margin_end(10)

        self.trim_end_row = Adw.ActionRow()
        self.trim_end_row.set_child(contents_horizontal_box)
        self.trim_end_row.set_sensitive(False)

    def _setup_trim_end_title_label(self):
        # Instantiates the trim end time label widget.
        self.trim_end_title_label = Gtk.Label(label='Trim End')
        self.trim_end_title_label.set_vexpand(True)
        self.trim_end_title_label.set_valign(Gtk.Align.END)
        self.trim_end_title_label.set_hexpand(False)
        self.trim_end_title_label.set_halign(Gtk.Align.START)

    def _setup_trim_end_subtitle_label(self):
        # Instantiates the trim end timecode label widget.
        self.trim_end_timecode_label = Gtk.Label(label='##:##:##')
        self.trim_end_timecode_label.add_css_class('dim-label')
        self.trim_end_timecode_label.add_css_class('caption')
        self.trim_end_timecode_label.set_vexpand(True)
        self.trim_end_timecode_label.set_valign(Gtk.Align.START)
        self.trim_end_timecode_label.set_hexpand(False)
        self.trim_end_timecode_label.set_halign(Gtk.Align.START)

    def _setup_trim_end_scale(self):
        # Instantiates the trim end scale widget.
        self.trim_end_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                       min=0.0,
                                                       max=1.0,
                                                       step=0.1)
        self.trim_end_scale.set_value(0.0)
        self.trim_end_scale.set_digits(1)
        self.trim_end_scale.set_draw_value(False)
        self.trim_end_scale.set_inverted(True)
        self.trim_end_scale.set_hexpand(True)
        self.trim_end_scale.connect('adjust-bounds', self.on_trim_end_scale_adjust_bounds)

    def _setup_trim_settings_suffix_content(self):
        # Instantiates the trim settings group's suffix widgets.
        self.trim_duration_label = Gtk.Label()

        self.trim_settings_switch = Gtk.Switch()
        self.trim_settings_switch.set_vexpand(False)
        self.trim_settings_switch.set_valign(Gtk.Align.CENTER)
        self.trim_settings_switch.connect('state-set', self.on_trim_settings_switch_state_set)

        self.trim_settings_suffix_content_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.trim_settings_suffix_content_horizontal_box.append(self.trim_duration_label)
        self.trim_settings_suffix_content_horizontal_box.append(self.trim_settings_switch)

    def is_trim_scale_bad_value(self, value: float) -> bool:
        """
        Returns whether the given trim scale value exceeds the total input video's duration or is below zero.

        Parameters:
            value: The value of the scale widget.

        Returns:
            Boolean that represents whether the given scale value is a bad value.
        """
        return value < 0 or value > self.video_duration

    def set_trim_state_enabled(self, is_state_enabled: bool):
        """
        Sets the state of the trim page by toggling the trim settings widgets.

        Parameters:
            is_state_enabled: Boolean that represents whether to enable the trim page's trim settings widgets.
        """
        self.trim_start_row.set_sensitive(is_state_enabled)
        self.trim_end_row.set_sensitive(is_state_enabled)

    def set_trim_start_value(self, trim_start_value: float):
        """
        Sets the trim start time value for the trim start widgets.

        Parameters:
            trim_start_value: The given trim start value in seconds.
        """
        self.trim_start_scale.set_value(trim_start_value)
        self.trim_start_timecode_label.set_label(format_converter.get_timecode_from_seconds(trim_start_value))

    def set_trim_end_value(self, trim_end_value: float):
        """
        Sets the trim end time value for the trim end widgets.

        Parameters:
            trim_end_value: The given trim end value in seconds.
        """
        self.trim_end_scale.set_value(trim_end_value)
        self.trim_end_timecode_label.set_label(
            format_converter.get_timecode_from_seconds(self.video_duration - trim_end_value)
        )

    def set_range_for_trim_scales(self, range_min: float, range_max: float):
        """
        Sets the given range values for the trim start/end scale widgets.

        Parameters:
            range_min: Minimum range in seconds.
            range_max: Maximum range in seconds.
        """
        self.trim_start_scale.set_range(min=range_min, max=range_max)
        self.trim_end_scale.set_range(min=range_min, max=range_max)

    def set_widgets_setting_up(self, is_widgets_setting_up: bool):
        """
        Sets whether the trim page's widgets are being set up.

        Parameters:
            is_widgets_setting_up: Boolean that represents whether the trim page's widgets are being set up.
        """
        self.is_widgets_setting_up = is_widgets_setting_up

    def update_trim_duration(self):
        """Sets the trim duration label widget based on the state of the trim scale widgets."""
        if self.trim_settings_switch.get_active():
            trim_start_time = self.trim_start_scale.get_value()
            trim_duration = (self.video_duration - self.trim_end_scale.get_value()) - trim_start_time
            trim_settings_label = ''.join([self.TRIM_DURATION_LABEL,
                                           format_converter.get_timecode_from_seconds(trim_duration)])
            self.trim_duration_label.set_label(trim_settings_label)
        else:
            trim_settings_label = ''.join([self.TRIM_DURATION_LABEL,
                                           format_converter.get_timecode_from_seconds(self.video_duration)])
            self.trim_duration_label.set_label(trim_settings_label)

    def fix_trim_scale_bad_value(self, scale, value: float):
        """
        Sets the given scale to a valid value if the given scale value is bad.

        Parameters:
            scale: Gtk.Scale to fix.
            value: Scale value in seconds.
        """
        if value < 0:
            scale.set_value(0)
        elif value > self.video_duration:
            scale.set_value(self.video_duration)

    def apply_settings_to_widgets(self, encoding_task: encoding.Task):
        """
        Applies the given encoding task's settings to the trim page's widgets.

        Parameters:
            encoding_task: Encoding task to apply to the trim page's widgets.
        """
        self.encoding_task = encoding_task
        self.video_duration = encoding_task.input_file.duration

        GLib.idle_add(self.set_widgets_setting_up, True)
        GLib.idle_add(self.set_range_for_trim_scales, 0.0, self.video_duration)
        self._apply_trim_enabled_setting_to_widgets(encoding_task)
        self._apply_trim_preview_to_widgets(encoding_task)
        self._apply_trim_start_setting_to_widgets(encoding_task)
        self._apply_trim_end_setting_to_widgets(encoding_task)
        GLib.idle_add(self.set_widgets_setting_up, False)

    def _apply_trim_enabled_setting_to_widgets(self, encoding_task: encoding.Task):
        # Applies the encoding task's settings to the trim settings group's suffix widgets.
        if encoding_task.trim:
            GLib.idle_add(self.trim_settings_switch.set_active, True)

            trim_settings_label = ''.join([self.TRIM_DURATION_LABEL,
                                           format_converter.get_timecode_from_seconds(encoding_task.trim.trim_duration)])
        else:
            GLib.idle_add(self.trim_settings_switch.set_active, False)

            trim_settings_label = ''.join([self.TRIM_DURATION_LABEL,
                                           format_converter.get_timecode_from_seconds(self.video_duration)])

        GLib.idle_add(self.trim_duration_label.set_label, trim_settings_label)

    def _apply_trim_preview_to_widgets(self, encoding_task: encoding.Task):
        # Applies the encoding task's trim preview file to the preview picture.
        if encoding_task.input_file.is_video:
            GLib.idle_add(self.preview_picture.set_filename, encoding_task.temp_output_file.trim_preview_file_path)
            GLib.idle_add(self.preview_stack.set_visible_child_name, 'preview')
        else:
            GLib.idle_add(self.preview_stack.set_visible_child_name, 'audio')

    def _apply_trim_start_setting_to_widgets(self, encoding_task: encoding.Task):
        # Applies the encoding task's trim start time setting to the trim start widgets.
        if encoding_task.trim:
            GLib.idle_add(self.set_trim_start_value, encoding_task.trim.start_time)
        else:
            GLib.idle_add(self.set_trim_start_value, 0.0)

    def _apply_trim_end_setting_to_widgets(self, encoding_task: encoding.Task):
        # Applies the encoding task's trim end time setting to the trim end widgets.
        if encoding_task.trim:
            start_time = encoding_task.trim.start_time
            trim_duration = encoding_task.trim.trim_duration
            GLib.idle_add(self.set_trim_end_value, self.video_duration - (start_time + trim_duration))
        else:
            GLib.idle_add(self.set_trim_end_value, 0.0)

    def apply_settings_from_widgets(self):
        """Applies the state of the trim page's widgets to the encoding task."""
        if self.trim_settings_switch.get_active():
            start_time = self.trim_start_scale.get_value()
            seconds_from_end = self.trim_end_scale.get_value()
            trim_duration = (self.video_duration - seconds_from_end) - start_time

            trim_settings = trim.TrimSettings()
            trim_settings.start_time = start_time
            trim_settings.trim_duration = trim_duration

            self.encoding_task.trim = trim_settings
        else:
            self.encoding_task.trim = None

    def on_trim_settings_switch_state_set(self, switch, user_data=None):
        """
        Signal callback function for the trim settings switch's 'state-set' signal.
        Sets the trim page's state, updates the trim duration, and generates a new preview.

        Parameters:
            switch: Gtk.Switch that emitted the signal.
            user_data: Additional data passed from the signal.
        """
        self.set_trim_state_enabled(switch.get_active())
        self.update_trim_duration()

        if self.is_widgets_setting_up:
            return

        self.trim_previewer.add_preview_task(self.encoding_task, self.trim_start_scale.get_value())

    def on_trim_start_scale_adjust_bounds(self, scale, value):
        """
        Signal callback function for the trim start scale's 'adjust-bounds' signal.
        Sets the trim start timecode label, updates the trim duration, and generates a new preview.

        Parameters:
            scale: Gtk.Scale that emitted the signal.
            value: The value of the scale that emitted the signal.
        """
        if self.is_trim_scale_bad_value(value):
            self.fix_trim_scale_bad_value(scale, value)

            return

        self.trim_start_timecode_label.set_label(format_converter.get_timecode_from_seconds(value))
        self.update_trim_duration()

        if self.is_widgets_setting_up or round(value, 1) == round(scale.get_value(), 1):
            return

        self._adjust_trim_start_scale_overshoot(value)

        self.trim_previewer.add_preview_task(self.encoding_task, self.trim_start_scale.get_value())

    def _adjust_trim_start_scale_overshoot(self, scale_value: float):
        # Moves the trim end scale with the trim start scale if they were to start overlapping.
        trim_end_value = self.trim_end_scale.get_value()

        if scale_value > (self.video_duration - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_start_value(self.video_duration - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS)
        elif scale_value > ((self.video_duration - trim_end_value) - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_end_value(self.video_duration - (scale_value + trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS))

    def on_trim_end_scale_adjust_bounds(self, scale, value):
        """
        Signal callback function for the trim end scale's 'adjust-bounds' signal.
        Sets the trim end timecode label, updates the trim duration, and generates a new preview.

        Parameters:
            scale: Gtk.Scale that emitted the signal.
            value: The value of the scale that emitted the signal.
        """
        if self.is_trim_scale_bad_value(value):
            self.fix_trim_scale_bad_value(scale, value)

            return

        self.trim_end_timecode_label.set_label(format_converter.get_timecode_from_seconds(self.video_duration - value))
        self.update_trim_duration()

        if self.is_widgets_setting_up:
            return

        self._adjust_trim_end_scale_overshoot(value)

        self.trim_previewer.add_preview_task(self.encoding_task, (self.video_duration - value))

    def _adjust_trim_end_scale_overshoot(self, scale_value: float):
        # Moves the trim start scale with the trim end scale if they were to start overlapping.
        trim_start_value = self.trim_start_scale.get_value()

        if scale_value > (self.video_duration - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_end_value(self.video_duration - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS)
        elif scale_value > ((self.video_duration - trim_start_value) - trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_start_value(self.video_duration - (scale_value + trim.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS))

    class TrimPreviewer:
        """Class that manages the preview queue and generates a new preview for each request."""

        def __init__(self, trim_page, preview_generator: preview.PreviewGenerator):
            """
            Initializes the TrimPreviewer class with the necessary variables for managing the trim previewer.

            Parameters:
                trim_page: The trim page to manage previews for.
                preview_generator: preview.PreviewGenerator to send preview requests to.
            """
            self._trim_page = trim_page
            self._preview_generator = preview_generator
            self._preview_queue = queue.Queue()

            threading.Thread(target=self._preview_queue_loop, args=()).start()

        def _preview_queue_loop(self):
            # The loop that consumes the preview queue in order to process trim preview requests.
            while True:
                encoding_task, time_position = self._preview_queue.get()

                GLib.idle_add(self._trim_page.preview_picture.set_opacity, 0.5)

                if not encoding_task:
                    return

                time.sleep(0.1)

                while not self._preview_queue.empty():
                    with self._preview_queue.mutex:
                        encoding_task, time_position = self._preview_queue.queue[-1]

                        self._preview_queue.queue.clear()

                    time.sleep(0.1)

                self._trim_page.apply_settings_from_widgets()

                if encoding_task.input_file.is_video:
                    self._generate_preview(encoding_task, time_position)

                GLib.idle_add(self._trim_page.preview_picture.set_opacity, 1.0)

        def _generate_preview(self, encoding_task: encoding.Task, time_position: float):
            # Uses the preview generator to generate a new trim preview.
            self._preview_generator.generate_trim_preview(encoding_task, time_position)
            self._wait_for_preview_generation(encoding_task)

            GLib.idle_add(self._trim_page.preview_picture.set_filename,
                          encoding_task.temp_output_file.trim_preview_file_path)

        @staticmethod
        def _wait_for_preview_generation(encoding_task: encoding.Task):
            # Waits for the preview generator to finish creating the trim preview file.
            if encoding_task.temp_output_file.trim_preview_threading_event.is_set():
                encoding_task.temp_output_file.trim_preview_threading_event.clear()

            encoding_task.temp_output_file.trim_preview_threading_event.wait()

        def add_preview_task(self, encoding_task: encoding.Task, time_position: int | float):
            """
            Adds the given encoding task and time position to the preview queue in order to request a new trim preview.

            Parameters:
                encoding_task: Encoding task to send to the preview queue.
                time_position: Time position (in seconds) to use for the trim preview.
            """
            self._preview_queue.put((encoding_task, time_position))

        def kill(self):
            """Empties the preview queue and stops the preview queue loop."""
            while not self._preview_queue.empty():
                self._preview_queue.get()

            self._preview_queue.put((False, False))


class BenchmarkPage(Gtk.Box):
    """Class that contains the widgets that make up the application's benchmark page."""

    BENCHMARK_TYPE_OPTIONS = ('Short', 'Long')

    def __init__(self, benchmark_generator: benchmark.BenchmarkGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the BenchmarkPage class with the necessary variables for creating the application's benchmark page.

        Parameters:
            benchmark_generator: The benchmark.BenchmarkGenerator for running benchmarks for encoding tasks.
            app_settings: Application's settings.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.benchmark_generator = benchmark_generator
        self.app_settings = app_settings
        self.encoding_task = None
        self._is_stop_button_clicked = False
        self._stop_button_thread_lock = threading.Lock()

        self._setup_benchmark_page_contents()

        self.set_vexpand(True)
        self.set_valign(Gtk.Align.CENTER)

        self.set_margin_top(10)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

    @property
    def is_stop_button_clicked(self) -> bool:
        """
        Returns whether the stop button has been clicked. This property is thread safe.

        Returns:
            Boolean that represents whether the stop button has been clicked.
        """
        with self._stop_button_thread_lock:
            return self._is_stop_button_clicked

    @is_stop_button_clicked.setter
    def is_stop_button_clicked(self, is_clicked: bool):
        """
        Sets whether the stop button has been clicked. This property is thread safe.

        Parameters:
            is_clicked: Boolean that represents whether the stop button has been clicked.
        """
        with self._stop_button_thread_lock:
            self._is_stop_button_clicked = is_clicked

    def _setup_benchmark_page_contents(self):
        # Instantiates all the widgets needed for the benchmark page.
        self._setup_benchmark_results_widgets()
        self._setup_benchmark_settings_widgets()

        self.append(self.results_group)
        self.append(self.benchmark_settings_vertical_box)

    def _setup_benchmark_results_widgets(self):
        # Instantiates the benchmark results widgets.
        self._setup_results_grid()
        self._setup_results_row()
        self._setup_progress_row()

        self.results_group = Adw.PreferencesGroup()
        self.results_group.set_title('Results')
        self.results_group.add(self.results_row)
        self.results_group.add(self.progress_row)

    def _setup_results_grid(self):
        # Instantiates the grid widget that contains the results.
        self._setup_bitrate_results()
        self._setup_speed_results()
        self._setup_file_size_results()
        self._setup_encode_time_results()

        self.results_grid = Gtk.Grid()
        self.results_grid.attach(self.bitrate_results_horizontal_box, column=0, row=0, width=1, height=1)
        self.results_grid.attach(self.speed_result_horizontal_box, column=1, row=0, width=1, height=1)
        self.results_grid.attach(self.file_size_result_horizontal_box, column=0, row=1, width=1, height=1)
        self.results_grid.attach(self.encode_time_result_horizontal_box, column=1, row=1, width=1, height=1)
        self.results_grid.set_column_homogeneous(True)
        self.results_grid.set_column_spacing(10)
        self.results_grid.set_row_homogeneous(True)
        self.results_grid.set_row_spacing(10)
        self.results_grid.set_hexpand(True)
        self.results_grid.set_margin_top(10)
        self.results_grid.set_margin_bottom(10)
        self.results_grid.set_margin_start(10)
        self.results_grid.set_margin_end(10)

    def _setup_bitrate_results(self):
        # Instantiates the bitrate results widgets.
        bitrate_title_label = Gtk.Label(label='Bitrate:')
        bitrate_title_label.set_hexpand(False)
        bitrate_title_label.set_halign(Gtk.Align.START)

        self.bitrate_results_label = Gtk.Label(label='--')
        self.bitrate_results_label.set_hexpand(False)
        self.bitrate_results_label.set_halign(Gtk.Align.START)

        self.bitrate_results_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.bitrate_results_horizontal_box.append(bitrate_title_label)
        self.bitrate_results_horizontal_box.append(self.bitrate_results_label)

    def _setup_speed_results(self):
        # Instantiates the speed results widgets.
        speed_title_label = Gtk.Label(label='Speed:')
        speed_title_label.set_hexpand(False)
        speed_title_label.set_halign(Gtk.Align.START)

        self.speed_result_label = Gtk.Label(label='--')
        self.speed_result_label.set_hexpand(False)
        self.speed_result_label.set_halign(Gtk.Align.START)

        self.speed_result_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.speed_result_horizontal_box.append(speed_title_label)
        self.speed_result_horizontal_box.append(self.speed_result_label)

    def _setup_file_size_results(self):
        # Instantiates the file size results widgets.
        file_size_title_label = Gtk.Label(label='Est. File Size:')
        file_size_title_label.set_hexpand(False)
        file_size_title_label.set_halign(Gtk.Align.START)

        self.file_size_result_label = Gtk.Label(label='--')
        self.file_size_result_label.set_hexpand(False)
        self.file_size_result_label.set_halign(Gtk.Align.START)

        self.file_size_result_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.file_size_result_horizontal_box.append(file_size_title_label)
        self.file_size_result_horizontal_box.append(self.file_size_result_label)

    def _setup_encode_time_results(self):
        # Instantiates the encode time results widgets.
        encode_time_title_label = Gtk.Label(label='Est. Encode Time:')
        encode_time_title_label.set_hexpand(False)
        encode_time_title_label.set_halign(Gtk.Align.START)

        self.encode_time_result_label = Gtk.Label(label='--')
        self.encode_time_result_label.set_hexpand(False)
        self.encode_time_result_label.set_halign(Gtk.Align.START)

        self.encode_time_result_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.encode_time_result_horizontal_box.append(encode_time_title_label)
        self.encode_time_result_horizontal_box.append(self.encode_time_result_label)

    def _setup_results_row(self):
        # Instantiates the results row widget.
        self.results_row = Adw.ActionRow()
        self.results_row.set_child(self.results_grid)

    def _setup_progress_row(self):
        # Instantiates the progress row widgets.
        self.benchmark_progress_bar = Gtk.ProgressBar()
        self.benchmark_progress_bar.set_hexpand(True)
        self.benchmark_progress_bar.set_margin_top(20)
        self.benchmark_progress_bar.set_margin_bottom(20)
        self.benchmark_progress_bar.set_margin_start(40)
        self.benchmark_progress_bar.set_margin_end(40)

        self.progress_row = Adw.ActionRow()
        self.progress_row.set_child(self.benchmark_progress_bar)

    def _setup_benchmark_settings_widgets(self):
        # Instantiates the benchmark settings widgets.
        self._setup_benchmark_type_row()
        self._setup_start_stop_button()

        self.benchmark_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.benchmark_settings_vertical_box.append(self.benchmark_type_group)
        self.benchmark_settings_vertical_box.append(self.start_stop_button_stack)

    def _setup_benchmark_type_row(self):
        # Instantiates the benchmark type row widgets.
        self._setup_benchmark_type_string_list()

        self.benchmark_type_combo_row = Adw.ComboRow()
        self.benchmark_type_combo_row.set_title('Type')
        self.benchmark_type_combo_row.set_subtitle('Choose how long the benchmark should be')
        self.benchmark_type_combo_row.set_model(self.benchmark_type_string_list)

        self.benchmark_type_group = Adw.PreferencesGroup()
        self.benchmark_type_group.set_title('Settings')
        self.benchmark_type_group.add(self.benchmark_type_combo_row)

    def _setup_benchmark_type_string_list(self):
        # Instantiates the benchmark types as a string list.
        self.benchmark_type_string_list = Gtk.StringList.new(self.BENCHMARK_TYPE_OPTIONS)

    def _setup_start_stop_button(self):
        # Instantiates the start/stop button widgets.
        self._setup_start_button()
        self._setup_stop_button()

        self.start_stop_button_stack = Gtk.Stack()
        self.start_stop_button_stack.add_named(self.start_button, 'start')
        self.start_stop_button_stack.add_named(self.stop_button, 'stop')
        self.start_stop_button_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_start_button(self):
        # Instantiates the start button.
        self.start_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        self.start_button.set_hexpand(True)
        self.start_button.set_halign(Gtk.Align.CENTER)
        self.start_button.add_css_class('suggested-action')
        self.start_button.set_size_request(100, -1)
        self.start_button.connect('clicked', self.on_start_button_clicked)

    def _setup_stop_button(self):
        # Instantiates the stop button.
        self.stop_button = Gtk.Button.new_from_icon_name('media-playback-stop-symbolic')
        self.stop_button.set_hexpand(True)
        self.stop_button.set_halign(Gtk.Align.CENTER)
        self.stop_button.add_css_class('destructive-action')
        self.stop_button.set_size_request(100, -1)
        self.stop_button.connect('clicked', self.on_stop_button_clicked)

    def setup_encode_task(self, encoding_task: encoding.Task):
        """
        Sets a new encoding task to use for the benchmark and resets the state of the benchmark widgets.

        Parameters:
            encoding_task: The new encoding task to use for the benchmark.
        """
        if encoding_task is self.encoding_task:
            return

        self.encoding_task = encoding_task
        self.reset_state()

    def reset_state(self):
        """Resets the state of the benchmark widgets."""
        self.reset_results()
        self.start_stop_button_stack.set_visible_child_name('start')

    def reset_results(self):
        """Resets the state of the results widgets."""
        self.bitrate_results_label.set_label('--')
        self.speed_result_label.set_label('--')
        self.file_size_result_label.set_label('--')
        self.encode_time_result_label.set_label('--')
        self.benchmark_progress_bar.set_fraction(0.0)

    def stop_benchmark(self):
        """Sets the encoding task's stop benchmark state."""
        if self.encoding_task:
            self.encoding_task.is_benchmark_stopped = True

    def start_benchmark(self):
        """
        Starts a benchmark for the encoding task. Adds the encoding task to the benchmark generator
        and waits for the benchmark to complete. This needs to be run in a thread otherwise it will block.
        """
        GLib.idle_add(self.reset_results)

        if self.encoding_task:
            self.benchmark_generator.add_benchmark_task(self.encoding_task,
                                                        long_benchmark=bool(self.benchmark_type_combo_row.get_selected()))
            self._wait_until_benchmark_is_done()

        GLib.idle_add(self.start_stop_button_stack.set_visible_child_name, 'start')

    def _wait_until_benchmark_is_done(self):
        # Waits for the benchmark to start and then waits for the benchmark to finish.
        while not self.encoding_task.has_benchmark_started and not self.encoding_task.is_benchmark_stopped:
            time.sleep(0.25)

        while self.encoding_task.has_benchmark_started and not self.encoding_task.is_benchmark_stopped:
            self._update_results()

            time.sleep(1)

        if self.is_stop_button_clicked:
            self.reset_results()
        else:
            self._update_final_results()

    def _update_results(self):
        # Updates the running benchmark widgets with the encoding task's benchmark values.
        try:
            self._update_bitrate_results()
            self._update_speed_results()
            self._update_benchmark_progress()
        except TypeError:
            pass

    def _update_bitrate_results(self):
        # Updates the bitrate results widget using the encoding task's benchmark bitrate value.
        if self.encoding_task.benchmark_bitrate:
            GLib.idle_add(self.bitrate_results_label.set_label, str(self.encoding_task.benchmark_bitrate) + 'Kbps')

    def _update_speed_results(self):
        # Updates the speed results widget using the encoding task's benchmark speed value.
        if self.encoding_task.benchmark_speed:
            GLib.idle_add(self.speed_result_label.set_label, str(self.encoding_task.benchmark_speed) + 'x')

    def _update_benchmark_progress(self):
        # Updates the benchmark progress widget using the encoding task's benchmark progress value.
        if self.encoding_task.benchmark_progress is not None:
            GLib.idle_add(self.benchmark_progress_bar.set_fraction, self.encoding_task.benchmark_progress)

    def _update_final_results(self):
        # Updates all the benchmark results widgets using the encoding task's benchmark values.
        self._update_results()
        self._update_file_size_results()
        self._update_encode_time_results()

    def _update_file_size_results(self):
        # Updates the file size results widget using the encoding task's benchmark file size value.
        try:
            GLib.idle_add(self.file_size_result_label.set_label,
                          format_converter.get_file_size_from_bytes(self.encoding_task.benchmark_file_size))
        except TypeError as e:
            GLib.idle_add(self.file_size_result_label.set_label, 'Error')

            logging.exception(e)

    def _update_encode_time_results(self):
        # Updates the encode time results widget using the encoding task's benchmark time estimate value.
        try:
            GLib.idle_add(self.encode_time_result_label.set_label,
                          format_converter.get_timecode_from_seconds(self.encoding_task.benchmark_time_estimate))
        except TypeError as e:
            GLib.idle_add(self.encode_time_result_label.set_label, 'Error')

            logging.exception(e)

    def on_start_button_clicked(self, button):
        """
        Signal callback function for the start button's 'clicked' signal.
        Shows the stop button and starts the benchmark process.

        Parameters:
            button: Gtk.Button that emitted the signal.
        """
        self.start_stop_button_stack.set_visible_child_name('stop')

        self.is_stop_button_clicked = False
        threading.Thread(target=self.start_benchmark, args=()).start()

    def on_stop_button_clicked(self, button):
        """
        Signal callback function for the stop button's 'clicked' signal.
        Shows the start button and stops the benchmark process.

        Parameters:
            button: Gtk.Button that emitted the signal.
        """
        self.start_stop_button_stack.set_visible_child_name('start')

        self.is_stop_button_clicked = True
        self.stop_benchmark()
