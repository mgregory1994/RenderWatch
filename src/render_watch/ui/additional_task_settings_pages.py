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


import queue
import threading
import time

from render_watch.ui import Gtk, Gio, Gdk, GLib, Adw, GdkPixbuf
from render_watch.encode import preview
from render_watch.ffmpeg import encoding, trim
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
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        crop_page_label = Gtk.Label(label='Crop Page')
        crop_page_label.set_vexpand(True)
        crop_page_label.set_valign(Gtk.Align.CENTER)
        crop_page_label.set_hexpand(True)
        crop_page_label.set_halign(Gtk.Align.CENTER)

        self.append(crop_page_label)


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

        self.trim_previewer = self.TrimPreviewer(self, preview_generator, self.preview_picture)

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

        def __init__(self, trim_page, preview_generator: preview.PreviewGenerator, preview_picture):
            """
            Initializes the TrimPreviewer class with the necessary variables for managing the trim previewer.

            Parameters:
                trim_page: The trim page to manage previews for.
                preview_generator: preview.PreviewGenerator to send preview requests to.
                preview_picture: The Gtk.Picture to use for showing the trim preview image.
            """
            self._trim_page = trim_page
            self._preview_generator = preview_generator
            self._preview_picture = preview_picture
            self._preview_queue = queue.Queue()

            threading.Thread(target=self._preview_queue_loop, args=()).start()

        def _preview_queue_loop(self):
            # The loop that consumes the preview queue in order to process trim preview requests.
            while True:
                encoding_task, time_position = self._preview_queue.get()

                GLib.idle_add(self._preview_picture.set_opacity, 0.5)

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

                GLib.idle_add(self._preview_picture.set_opacity, 1.0)

        def _generate_preview(self, encoding_task: encoding.Task, time_position: float):
            # Uses the preview generator to generate a new trim preview.
            self._preview_generator.generate_trim_preview(encoding_task, time_position)
            self._wait_for_preview_generation(encoding_task)

            GLib.idle_add(self._preview_picture.set_filename,
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
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        benchmark_page_label = Gtk.Label(label='Benchmark Page')
        benchmark_page_label.set_vexpand(True)
        benchmark_page_label.set_valign(Gtk.Align.CENTER)
        benchmark_page_label.set_hexpand(True)
        benchmark_page_label.set_halign(Gtk.Align.CENTER)

        self.append(benchmark_page_label)
