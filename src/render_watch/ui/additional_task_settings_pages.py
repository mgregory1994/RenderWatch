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
from render_watch.ffmpeg import task, filter
from render_watch.helpers import format_converter
from render_watch import app_preferences


class PreviewPage(Gtk.Box):
    """Class that contains the widgets that make up the application's preview page."""

    PREVIEW_DURATIONS = (5, 10, 20, 30)
    PREVIEW_DURATIONS_UI = ('5 Seconds', '10 Seconds', '20 Seconds', '30 Seconds')

    NOT_AVAILABLE_PAGE = 'not_available'
    GENERATING_PREVIEW_PAGE = 'generating'
    LIVE_PREVIEW_PAGE = 'preview'
    AUDIO_PREVIEW_PAGE = 'audio'

    def __init__(self, preview_generator: preview.PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the PreviewPage widgets class with the necessary variables for creating
        the application's preview page.

        Parameters:
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
            app_settings: Application's settings.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self._encode_task = None
        self._encode_task_thread_lock = threading.Lock()
        self._settings_preview_task = None
        self.is_widgets_setting_up = False

        self._setup_preview_page_contents()

        self.preview_previewer = self.PreviewPreviewer(self, preview_generator)

        self.set_margin_top(10)
        self.set_margin_bottom(20)
        self.set_margin_start(20)
        self.set_margin_end(20)

    @property
    def encode_task(self) -> task.Encode:
        """
        Returns the encoding task that's currently loaded for the preview page. This property is thread safe.

        Returns:
            Encoding task that's currently loaded for the preview page.
        """
        with self._encode_task_thread_lock:
            return self._encode_task

    @encode_task.setter
    def encode_task(self, new_encode_task: task.Encode):
        """
        Sets the encoding task to be loaded for the preview page. This property is thread safe.

        Parameters:
            new_encode_task: Encoding task to be loaded for the preview page.
        """
        with self._encode_task_thread_lock:
            self._encode_task = new_encode_task

    def _setup_preview_page_contents(self):
        # Instantiates all the widgets needed for the preview page.
        self._setup_preview_widgets()
        self._setup_preview_type_widgets()

        self.append(self.preview_stack)
        self.append(self.preview_type_group)

    def _setup_preview_widgets(self):
        # Instantiates the preview widgets.
        self._setup_preview_picture()
        self._setup_preview_not_available_status_page()
        self._setup_generating_preview_status_page()
        self._setup_audio_preview_status_page()
        self._setup_preview_stack()

    def _setup_preview_picture(self):
        # Instantiates the preview picture widget.
        self.preview_picture = Gtk.Picture()
        self.preview_picture.content_fit = True
        self.preview_picture.set_can_shrink(True)
        self.preview_picture.set_keep_aspect_ratio(True)

    def _setup_preview_not_available_status_page(self):
        # Instantiates the preview not available status page widget.
        self.preview_not_available_status_page = Adw.StatusPage.new()
        self.preview_not_available_status_page.set_title('Preview Not Available')
        self.preview_not_available_status_page.set_description('Current settings can\'t be used for previews')
        self.preview_not_available_status_page.set_icon_name('action-unavailable-symbolic')
        self.preview_not_available_status_page.set_sensitive(False)

    def _setup_generating_preview_status_page(self):
        # Instantiates the generating preview status page widget.
        self._setup_preview_progress_bar()

        self.generating_preview_status_page = Adw.StatusPage.new()
        self.generating_preview_status_page.set_title('Generating Preview')
        self.generating_preview_status_page.set_description('Take a sip of coffee...')
        self.generating_preview_status_page.set_icon_name('image-loading-symbolic')
        self.generating_preview_status_page.set_child(self.preview_progress_bar)

    def _setup_preview_progress_bar(self):
        # Instantiates the preview progress bar widget.
        self.preview_progress_bar = Gtk.ProgressBar.new()
        self.preview_progress_bar.set_hexpand(True)
        self.preview_progress_bar.set_margin_start(40)
        self.preview_progress_bar.set_margin_end(40)

    def _setup_audio_preview_status_page(self):
        # Instantiates the audio preview status page widget.
        self.audio_preview_status_page = Adw.StatusPage.new()
        self.audio_preview_status_page.set_title('Audio Only')
        self.audio_preview_status_page.set_description('Only audio can be previewed for this input')
        self.audio_preview_status_page.set_icon_name('audio-speakers-symbolic')
        self.audio_preview_status_page.set_sensitive(False)

    def _setup_preview_stack(self):
        # Instantiates the preview stack widget.
        spacing_label = Gtk.Label()
        spacing_label.set_vexpand(True)
        spacing_label.set_valign(Gtk.Align.CENTER)
        spacing_label.set_hexpand(True)
        spacing_label.set_halign(Gtk.Align.CENTER)

        self.preview_stack = Gtk.Stack()
        self.preview_stack.add_named(self.preview_not_available_status_page, self.NOT_AVAILABLE_PAGE)
        self.preview_stack.add_named(self.generating_preview_status_page, self.GENERATING_PREVIEW_PAGE)
        self.preview_stack.add_named(self.audio_preview_status_page, self.AUDIO_PREVIEW_PAGE)
        self.preview_stack.add_named(self.preview_picture, self.LIVE_PREVIEW_PAGE)
        self.preview_stack.add_named(spacing_label, 'spacing')
        self.preview_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_preview_type_widgets(self):
        # Instantiates the preview type and controls widgets.
        self._setup_preview_time_position_row()
        self._setup_preview_type_row()

        self.preview_type_group = Adw.PreferencesGroup()
        self.preview_type_group.set_title('Preview Settings')
        self.preview_type_group.add(self.preview_time_position_row)
        self.preview_type_group.add(self.preview_type_combo_row)

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
        self._setup_preview_time_position_gesture_click()
        self._setup_preview_time_position_event_controller_key()
        self._setup_preview_time_position_event_controller_scroll()

        self.preview_time_position_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.1)
        self.preview_time_position_scale.set_value(0.0)
        self.preview_time_position_scale.set_digits(1)
        self.preview_time_position_scale.set_draw_value(False)
        self.preview_time_position_scale.set_hexpand(True)
        self.preview_time_position_scale.connect('value-changed', self.on_preview_time_position_scale_value_changed)
        self.preview_time_position_scale.add_controller(self.preview_time_position_gesture_click)
        self.preview_time_position_scale.add_controller(self.preview_time_position_event_controller_key)
        self.preview_time_position_scale.add_controller(self.preview_time_position_event_controller_scroll)

    def _setup_preview_time_position_gesture_click(self):
        # Instantiates the preview time position gesture click event controller.
        self.preview_time_position_gesture_click = Gtk.GestureClick.new()
        self.preview_time_position_gesture_click.connect('stopped',
                                                         self.on_scale_gesture_stopped,
                                                         self.preview_time_position_gesture_click)
        self.preview_time_position_gesture_click.connect('unpaired-release', self.generate_new_preview)

    def _setup_preview_time_position_event_controller_key(self):
        # Instantiates the preview time position event controller key.
        self.preview_time_position_event_controller_key = Gtk.EventControllerKey.new()
        self.preview_time_position_event_controller_key.connect('key-released', self.generate_new_preview)

    def _setup_preview_time_position_event_controller_scroll(self):
        # Instantiates the preview time position event controller scroll.
        self.preview_time_position_event_controller_scroll = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        self.preview_time_position_event_controller_scroll.connect('scroll', self.on_event_controller_scroll)

    def _setup_preview_type_row(self):
        # Instantiates the preview controls and preview type widgets.
        self._setup_start_stop_stack()

        self.preview_durations_string_list = Gtk.StringList.new(self.PREVIEW_DURATIONS_UI)

        self.preview_type_combo_row = Adw.ComboRow()
        self.preview_type_combo_row.set_title('Preview Duration')
        self.preview_type_combo_row.set_subtitle('Duration to use at the current video position')
        self.preview_type_combo_row.set_model(self.preview_durations_string_list)
        self.preview_type_combo_row.add_suffix(self.start_stop_stack)

    def _setup_start_stop_stack(self):
        # Instantiates the start/stop button stack widget.
        self._setup_start_button()
        self._setup_stop_button()

        self.start_stop_stack = Gtk.Stack()
        self.start_stop_stack.add_named(self.start_button, 'start')
        self.start_stop_stack.add_named(self.stop_button, 'stop')
        self.start_stop_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_start_button(self):
        # Instantiates the start button widget.
        self.start_button = Gtk.Button.new_from_icon_name('media-playback-start-symbolic')
        self.start_button.add_css_class('suggested-action')
        self.start_button.set_vexpand(False)
        self.start_button.set_valign(Gtk.Align.CENTER)
        self.start_button.connect('clicked', self.on_start_button_clicked)

    def _setup_stop_button(self):
        # Instantiates the stop button widget.
        self.stop_button = Gtk.Button.new_from_icon_name('media-playback-stop-symbolic')
        self.stop_button.add_css_class('destructive-action')
        self.stop_button.set_vexpand(False)
        self.stop_button.set_valign(Gtk.Align.CENTER)
        self.stop_button.connect('clicked', self.on_stop_button_clicked)

    def set_live_preview_state(self):
        """Sets the preview page's widgets for the live preview state."""
        if self.encode_task.input_file.is_video:
            self.preview_stack.set_visible_child_name(self.LIVE_PREVIEW_PAGE)
            self.preview_picture.set_opacity(1.0)
            self.start_stop_stack.set_visible_child_name('start')
            self.preview_type_group.set_sensitive(True)
            self.preview_time_position_row.set_sensitive(True)
        else:
            self.set_audio_preview_state()

    def set_updating_live_preview_state(self):
        """Sets the preview page's widgets for the updating live preview state."""
        self.preview_picture.set_opacity(0.5)

    def set_audio_preview_state(self):
        """Sets the preview page's widgets for the audio preview state."""
        self.preview_stack.set_visible_child_name(self.AUDIO_PREVIEW_PAGE)
        self.start_stop_stack.set_visible_child_name('start')
        self.preview_type_group.set_sensitive(True)
        self.preview_time_position_row.set_sensitive(True)

    def set_generating_preview_state(self):
        """Sets the preview page's widgets for the generating preview state."""
        self.preview_stack.set_visible_child_name(self.GENERATING_PREVIEW_PAGE)
        self.start_stop_stack.set_visible_child_name('stop')
        self.preview_time_position_row.set_sensitive(False)

    def set_preview_not_available_state(self):
        """Sets the preview page's widgets for the preview not available state."""
        self.preview_stack.set_visible_child_name(self.NOT_AVAILABLE_PAGE)
        self.preview_type_group.set_sensitive(False)

    def set_preview_progress_bar_fraction(self, progress_fraction: float):
        """
        Sets the preview progress bar's percent complete using a decimal (0.0 - 1.0).

        Parameters:
            progress_fraction: Float the represents the percent complete as a decimal (0.0 - 1.0).
        """
        if progress_fraction is not None:
            self.preview_progress_bar.set_fraction(progress_fraction)

    def update_preview(self):
        """Re-sets the preview picture widget's file to the encoding task's settings preview file."""
        self.preview_picture.set_filename(self._settings_preview_task.preview_file_path)

    def generate_new_preview(self, *args, **kwargs):
        """For updating the preview when the encoding task's settings have changed."""
        if self.preview_time_position_event_controller_scroll in args:
            time.sleep(0.25)

        for kw, arg in kwargs.items():
            if 'duration' in kw:
                preview_duration = arg
                self._settings_preview_task = task.VideoPreview(self.encode_task,
                                                                preview_duration,
                                                                self.preview_time_position_scale.get_value())
                break
        else:
            self._settings_preview_task = task.SettingsPreview(self.encode_task,
                                                               self.preview_time_position_scale.get_value())

        self.preview_previewer.add_preview_task(self._settings_preview_task)

    def setup_encode_task(self, encode_task: task.Encode):
        """
        Sets a new encoding task to be used for the preview page.
        The preview page is then updated to show the new encoding task.

        Parameters:
            encode_task: New encoding task to use for the preview page.
        """
        if encode_task.input_file.is_folder:
            GLib.idle_add(self.set_preview_not_available_state)

            return

        if encode_task is self.encode_task:
            return

        self.encode_task = encode_task

        GLib.idle_add(self._set_widgets_setting_up, True)
        GLib.idle_add(self._update_preview_position_range)
        GLib.idle_add(self.generate_new_preview)
        GLib.idle_add(self.set_live_preview_state)
        GLib.idle_add(self._set_widgets_setting_up, False)

    def _set_widgets_setting_up(self, is_widgets_setting_up: bool):
        # Sets whether the preview page's widgets are being set up.
        self.is_widgets_setting_up = is_widgets_setting_up

    def _update_preview_position_range(self):
        # Updates the preview time position scale for a new encoding task.
        input_duration = self.encode_task.input_file.duration
        input_duration_half = input_duration / 2.0

        self.preview_time_position_scale.set_range(min=0.0, max=input_duration)
        self.preview_time_position_scale.set_value(input_duration_half)
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(input_duration_half))

    def on_scale_gesture_stopped(self, user_data, gesture_click):
        """
        Signal callback function for the scale gesture click's 'stopped' signal.
        Checks if there's still a device associated with the gesture (click and hold) and then generates a new preview.

        Parameters:
            user_data: Extra data passed in from the signal.
            gesture_click: Gtk.GestureClick that emitted the signal.
        """
        if gesture_click.get_device():
            return

        self.generate_new_preview()

    def on_event_controller_scroll(self, event_controller, dx, dy):
        """
        Signal callback function for the event controller scroll's 'scroll' signal.
        Generates a new preview.

        Parameters:
            event_controller: Gtk.EventControllerScroll that emitted the signal.
            dx: Direction of the scroll on the X-axis.
            dy: Direction of the scroll on the Y-axis.
        """
        threading.Thread(target=self.generate_new_preview, args=(event_controller,)).start()

    def on_preview_time_position_scale_value_changed(self, scale):
        """
        Signal callback function for the preview time position scale's 'value-changed' signal.
        Sets the preview time position value label and generates a new preview.

        Parameters:
            scale: Gtk.Scale that emitted the signal.
        """
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(scale.get_value()))

    def on_start_button_clicked(self, button):
        """
        Signal callback function for the start button's 'clicked' signal.
        Sets the encoding task's preview duration based on the preview type combo row's selection
        and generates a new preview.

        Parameters:
            button: Gtk.Button that emitted the signal.
        """
        preview_duration = self.PREVIEW_DURATIONS[self.preview_type_combo_row.get_selected()]

        self.generate_new_preview(duration=preview_duration)

    def on_stop_button_clicked(self, button):
        """
        Signal callback function for the stop button's 'clicked' signal.
        Sets the encoding task's stop video preview state in order to stop the currently running preview generation.

        Parameters:
            button: Gtk.Button that emitted the signal.
        """
        self.encode_task.is_video_preview_stopped = True

    class PreviewPreviewer:
        """Class that manages the preview queue and generates a new preview for each request."""

        PROGRESS_UPDATE_INTERVAL_IN_SECONDS = 1.0

        def __init__(self, preview_page, preview_generator: preview.PreviewGenerator):
            """
            Initializes the PreviewPreviewer class with the necessary variables for managing the preview previewer.

            Parameters:
                preview_page: The preview page to manage previews for.
                preview_generator: preview.PreviewGenerator to send preview requests to.
            """
            self._preview_page = preview_page
            self._preview_generator = preview_generator
            self._preview_queue = queue.Queue()

            threading.Thread(target=self._preview_queue_loop, args=()).start()

        def _preview_queue_loop(self):
            # The loop that consumes the preview queue in order to process preview requests.
            while True:
                preview_task = self._preview_queue.get()

                if not preview_task:
                    break

                preview_task = self._wait_for_empty_queue(preview_task)

                self._generate_preview(preview_task)

        def _wait_for_empty_queue(self,
                                  preview_task: task.SettingsPreview | task.VideoPreview) -> task.SettingsPreview | task.VideoPreview:
            # Consumes the queue until it's empty and stays empty for some time.
            time.sleep(0.1)

            while not self._preview_queue.empty():
                with self._preview_queue.mutex:
                    preview_task = self._preview_queue.queue[-1]

                    self._preview_queue.queue.clear()

                time.sleep(0.1)

            return preview_task

        def _generate_preview(self, preview_task: task.SettingsPreview | task.VideoPreview):
            # Uses the preview generator to generate a new preview.
            if isinstance(preview_task, task.VideoPreview):
                self._generate_video_preview(preview_task)
            else:
                self._generate_settings_preview(preview_task)

            GLib.idle_add(self._preview_page.update_preview)

        def _generate_video_preview(self, video_preview_task: task.VideoPreview):
            # Uses the preview generator to generate a new video preview.
            GLib.idle_add(self._preview_page.set_generating_preview_state)

            threading.Thread(target=self._update_video_preview_progress_loop, args=(video_preview_task,)).start()

            self._preview_generator.generate_video_preview(video_preview_task)
            self._wait_for_video_preview_generator(video_preview_task)

            if video_preview_task.preview_file_path or video_preview_task.is_preview_stopped:
                GLib.idle_add(self._preview_page.set_live_preview_state)
            else:
                GLib.idle_add(self._preview_page.set_preview_not_available_state)

        def _update_video_preview_progress_loop(self, video_preview_task: task.VideoPreview):
            # Loop that updates the progress of generating a video preview.
            video_preview_task.reset()

            while not (video_preview_task.is_preview_done or video_preview_task.is_preview_stopped):
                GLib.idle_add(self._preview_page.set_preview_progress_bar_fraction,
                              video_preview_task.progress)

                time.sleep(self.PROGRESS_UPDATE_INTERVAL_IN_SECONDS)

            GLib.idle_add(self._preview_page.set_preview_progress_bar_fraction, 1.0)

        @staticmethod
        def _wait_for_video_preview_generator(video_preview_task: task.VideoPreview):
            # Suspends the thread until the video preview generator is done.
            if video_preview_task.preview_threading_event.is_set():
                video_preview_task.preview_threading_event.clear()

            video_preview_task.preview_threading_event.wait()
            video_preview_task.is_preview_done = True

        def _generate_settings_preview(self, settings_preview_task: task.SettingsPreview):
            # Uses the preview generator to generate a new static preview of the encoding task's settings.
            GLib.idle_add(self._preview_page.set_updating_live_preview_state)

            self._preview_generator.generate_settings_preview(settings_preview_task)
            self._wait_for_settings_preview_generator(settings_preview_task)

            if settings_preview_task.preview_file_path:
                GLib.idle_add(self._preview_page.set_live_preview_state)
            else:
                GLib.idle_add(self._preview_page.set_preview_not_available_state)

        @staticmethod
        def _wait_for_settings_preview_generator(settings_preview_task: task.SettingsPreview):
            # Suspends the thread until the preview generator is done.
            if settings_preview_task.preview_threading_event.is_set():
                settings_preview_task.preview_threading_event.clear()

            settings_preview_task.preview_threading_event.wait()

        def add_preview_task(self, preview_task: task.SettingsPreview | task.VideoPreview):
            """
            Adds a new encoding task and the preview time position to the preview queue.

            Parameters:
                preview_task: Preview task to generate a preview for.
            """
            self._preview_queue.put(preview_task)

        def kill(self):
            """Empties the preview queue and stops the preview queue loop."""
            while not self._preview_queue.empty():
                self._preview_queue.get()

            self._preview_queue.put(False)


class CropPage(Gtk.Box):
    """Class that contains the widgets that make up the application's crop page."""

    RESOLUTION_MIN = 240
    RESOLUTION_MAX = 7680

    NOT_AVAILABLE_PAGE = 'not_available'
    PREVIEW_PAGE = 'preview'

    def __init__(self, preview_generator: preview.PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the CropPage widgets class with the necessary variables for creating the application's crop page.

        Parameters:
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
            app_settings: Application settings.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.app_settings = app_settings
        self.encode_task = None
        self.video_duration = None
        self.is_widgets_setting_up = False
        self.crop_preview_task = None

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
        self._setup_preview_not_available_status_page()
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

    def _setup_preview_not_available_status_page(self):
        # Instantiates the preview not available status page widget.
        self.preview_not_available_status_page = Adw.StatusPage.new()
        self.preview_not_available_status_page.set_title('Preview Not Available')
        self.preview_not_available_status_page.set_description('Current settings can\'t be used for previews')
        self.preview_not_available_status_page.set_icon_name('action-unavailable-symbolic')
        self.preview_not_available_status_page.set_sensitive(False)

    def _setup_preview_stack(self):
        # Instantiates the preview stack widget.
        spacing_label = Gtk.Label.new()
        spacing_label.set_vexpand(True)
        spacing_label.set_hexpand(True)

        self.preview_stack = Gtk.Stack()
        self.preview_stack.add_named(self.preview_not_available_status_page, 'not_available')
        self.preview_stack.add_named(self.preview_picture, 'preview')
        self.preview_stack.add_named(spacing_label, 'spacing')
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
        self._setup_preview_time_position_gesture_click()
        self._setup_preview_time_position_event_controller_key()
        self._setup_preview_time_position_event_controller_scroll()

        self.preview_time_position_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    step=0.1)
        self.preview_time_position_scale.set_value(0.0)
        self.preview_time_position_scale.set_digits(1)
        self.preview_time_position_scale.set_draw_value(False)
        self.preview_time_position_scale.set_hexpand(True)
        self.preview_time_position_scale.connect('value-changed', self.on_preview_time_position_scale_value_changed)
        self.preview_time_position_scale.add_controller(self.preview_time_position_gesture_click)
        self.preview_time_position_scale.add_controller(self.preview_time_position_event_controller_key)
        self.preview_time_position_scale.add_controller(self.preview_time_position_event_controller_scroll)

    def _setup_preview_time_position_gesture_click(self):
        # Instantiates the preview time position gesture click controller.
        self.preview_time_position_gesture_click = Gtk.GestureClick.new()
        self.preview_time_position_gesture_click.connect('stopped',
                                                         self.on_scale_gesture_stopped,
                                                         self.preview_time_position_gesture_click)
        self.preview_time_position_gesture_click.connect('unpaired-release', self.generate_crop_preview)

    def _setup_preview_time_position_event_controller_key(self):
        # Instantiates the preview time position event controller key.
        self.preview_time_position_event_controller_key = Gtk.EventControllerKey.new()
        self.preview_time_position_event_controller_key.connect('key-released', self.generate_crop_preview)

    def _setup_preview_time_position_event_controller_scroll(self):
        # Instantiates the preview time position event controller scroll.
        self.preview_time_position_event_controller_scroll = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        self.preview_time_position_event_controller_scroll.connect('scroll', self.on_event_controller_scroll)

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

    def set_preview_available_state(self):
        """Sets the crop page's widgets for the crop available state."""
        self.preview_stack.set_visible_child_name(self.PREVIEW_PAGE)
        self.crop_settings_group.set_sensitive(True)
        self.scale_settings_group.set_sensitive(True)
        self.time_position_settings_group.set_sensitive(True)
        self.preview_picture.set_opacity(1.0)

    def set_updating_preview_state(self):
        """Sets the preview page's widgets for the updating preview state."""
        self.preview_picture.set_opacity(0.5)

    def set_preview_not_available_state(self):
        """Sets the crop page's widgets for the crop not available state."""
        self.preview_stack.set_visible_child_name(self.NOT_AVAILABLE_PAGE)
        self.crop_settings_group.set_sensitive(False)
        self.scale_settings_group.set_sensitive(False)
        self.time_position_settings_group.set_sensitive(False)

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

    def generate_crop_preview(self, *args, **kwargs):
        """Adds a preview task to the crop previewer."""
        if self.preview_time_position_event_controller_scroll in args:
            time.sleep(0.25)

        self.crop_preview_task = task.CropPreview(self.encode_task, self.preview_time_position_scale.get_value())
        self.crop_previewer.add_preview_task(self.crop_preview_task)

    def update_preview(self):
        """Re-sets the preview picture widget's file to the encoding task's crop preview file."""
        self.preview_picture.set_filename(self.crop_preview_task.preview_file_path)

    def update_crop_size_range(self):
        """
        Uses the encoding task's selected video stream's dimensions to set the range for the
        crop width and height spin buttons.
        """
        origin_width = self.encode_task.get_video_stream().width
        origin_height = self.encode_task.get_video_stream().height

        self.crop_width_spin_button.set_range(self.RESOLUTION_MIN, origin_width)
        self.crop_height_spin_button.set_range(self.RESOLUTION_MIN, origin_height)

    def update_crop_padding_range(self):
        """
        Uses the encoding task's selected video stream's dimensions to set the range for the
        crop x and y padding spin buttons.
        """
        origin_width = self.encode_task.get_video_stream().width
        origin_height = self.encode_task.get_video_stream().height
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
        video_duration = self.encode_task.input_file.duration

        self.preview_time_position_scale.set_range(min=0.0, max=video_duration)
        self.preview_time_position_scale.set_value(round(video_duration / 2.0, 1))
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(video_duration / 2.0))

    def apply_settings_to_widgets(self, encode_task: task.Encode):
        """
        Applies the given encoding task's settings to the crop page's widgets.

        Parameters:
            encode_task: Encoding task to apply to the crop page's widgets.
        """
        if not encode_task.input_file.is_video or encode_task.input_file.is_folder:
            self.set_preview_not_available_state()

            return

        if self.encode_task is encode_task:
            return

        self.encode_task = encode_task
        self.generate_crop_preview()

        GLib.idle_add(self.set_widgets_setting_up, True)
        GLib.idle_add(self.update_crop_size_range)
        GLib.idle_add(self.update_preview_position_range)
        self._apply_crop_enabled_setting_to_widgets()
        self._apply_crop_settings_to_widgets()
        self._apply_scale_enabled_setting_to_widgets()
        self._apply_scale_settings_to_widgets()
        # GLib.idle_add(self.update_preview)
        GLib.idle_add(self.set_preview_available_state)
        GLib.idle_add(self.set_widgets_setting_up, False)

    def _apply_crop_enabled_setting_to_widgets(self):
        # Applies the encoding task's settings to the crop enabled settings widgets.
        GLib.idle_add(self.crop_settings_switch.set_active, self.encode_task.filters.crop is not None)
        GLib.idle_add(self.auto_crop_switch.set_active, self.encode_task.filters.crop.auto_crop_enabled)

    def _apply_crop_settings_to_widgets(self):
        # Applies the encoding task's settings to the crop settings widgets.
        if self.encode_task.filters.is_crop_enabled():
            width, height, x_pad, y_pad = self.encode_task.filters.crop.dimensions

            GLib.idle_add(self.crop_width_spin_button.set_value, width)
            GLib.idle_add(self.crop_height_spin_button.set_value, height)
            GLib.idle_add(self.update_crop_padding_range)
            GLib.idle_add(self.crop_x_padding_spin_button.set_value, x_pad)
            GLib.idle_add(self.crop_y_padding_spin_button.set_value, y_pad)
        else:
            origin_width = self.encode_task.get_video_stream().width
            origin_height = self.encode_task.get_video_stream().height

            GLib.idle_add(self.crop_width_spin_button.set_value, origin_width)
            GLib.idle_add(self.crop_height_spin_button.set_value, origin_height)
            GLib.idle_add(self.update_crop_padding_range)
            GLib.idle_add(self.crop_x_padding_spin_button.set_value, 0)
            GLib.idle_add(self.crop_y_padding_spin_button.set_value, 0)

    def _apply_scale_enabled_setting_to_widgets(self):
        # Applies the encoding task's settings to the scale enabled settings widget.
        GLib.idle_add(self.scale_settings_switch.set_active, (self.encode_task.filters.scale is not None))

    def _apply_scale_settings_to_widgets(self):
        # Applies the encoding task's settings to the scale settings widgets.
        if self.encode_task.filters.is_scale_enabled():
            width, height = self.encode_task.filters.scale.dimensions

            GLib.idle_add(self.scale_width_spin_button.set_value, width)
            GLib.idle_add(self.scale_height_spin_button.set_value, height)
        else:
            origin_width = self.encode_task.get_video_stream().width
            origin_height = self.encode_task.get_video_stream().height

            GLib.idle_add(self.scale_width_spin_button.set_value, origin_width)
            GLib.idle_add(self.scale_height_spin_button.set_value, origin_height)

    def apply_settings_from_widgets(self):
        """Applies the state of the crop page's widgets to the encoding task."""
        self._apply_crop_settings_from_widgets()
        self._apply_scale_settings_from_widgets()

        self.crop_preview_task.update_encode_task()

    def _apply_crop_settings_from_widgets(self):
        # Applies the state of the crop settings widgets to the encoding task.
        if self.crop_settings_switch.get_active():
            if self.auto_crop_switch.get_active():
                crop_settings = filter.Crop(self.encode_task, self.app_settings)
            else:
                width = self.crop_width_spin_button.get_value_as_int()
                height = self.crop_height_spin_button.get_value_as_int()
                x_pad = self.crop_x_padding_spin_button.get_value_as_int()
                y_pad = self.crop_y_padding_spin_button.get_value_as_int()

                crop_settings = filter.Crop(self.encode_task, self.app_settings, autocrop=False)
                crop_settings.dimensions = (width, height, x_pad, y_pad)

            self.encode_task.filters.crop = crop_settings
        else:
            self.encode_task.filters.crop = None

        GLib.idle_add(self.update_crop_padding_range)

    def _apply_scale_settings_from_widgets(self):
        # Applies the state of the scale widgets to the encoding task.
        if self.scale_settings_switch.get_active():
            width = self.scale_width_spin_button.get_value_as_int()
            height = self.scale_height_spin_button.get_value_as_int()

            scale_settings = filter.Scale()
            scale_settings.dimensions = (width, height)
            self.encode_task.filters.scale = scale_settings
        else:
            self.encode_task.filters.scale = None

    def on_scale_gesture_stopped(self, user_data, gesture_click):
        if gesture_click.get_device():
            return

        self.generate_crop_preview()

    def on_event_controller_scroll(self, event_controller, dx, dy):
        threading.Thread(target=self.generate_crop_preview, args=(event_controller,)).start()

    def on_preview_time_position_scale_value_changed(self, scale):
        """
        Signal callback function for the preview time position scale's 'value-changed' signal.
        Updates the preview time position value label to reflect what time position is set and generates a new preview.

        Parameters:
            scale: Gtk.Scale that emitted the signal.
        """
        scale_value = scale.get_value()
        self.preview_time_position_value_label.set_label(format_converter.get_timecode_from_seconds(scale_value))

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

        self.generate_crop_preview()

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

        self.generate_crop_preview()

    def on_crop_width_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop width spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

    def on_crop_height_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop height spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

    def on_crop_x_padding_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop x padding spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

    def on_crop_y_padding_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the crop y padding spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

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

        self.generate_crop_preview()

    def on_scale_width_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the scale width spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

    def on_scale_height_spin_button_value_changed(self, spin_button):
        """
        Signal callback function for the scale height spin button's 'value-changed' signal.
        Generates a new preview.

        Parameters:
            spin_button: Gtk.SpinButton that emitted the signal.
        """
        if self.is_widgets_setting_up:
            return

        self.generate_crop_preview()

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
                crop_preview_task = self._preview_queue.get()

                if not crop_preview_task:
                    return

                crop_preview_task = self._wait_for_empty_queue(crop_preview_task)

                self._crop_page.apply_settings_from_widgets()
                self._generate_preview(crop_preview_task)

        def _wait_for_empty_queue(self, crop_preview_task: task.CropPreview) -> task.CropPreview:
            # Consumes the queue until it's empty and stays empty for some time.
            time.sleep(0.1)

            while not self._preview_queue.empty():
                with self._preview_queue.mutex:
                    crop_preview_task = self._preview_queue.queue[-1]

                    self._preview_queue.queue.clear()

                time.sleep(0.1)

            return crop_preview_task

        def _generate_preview(self, crop_preview_task: task.CropPreview):
            # Uses the preview generator to generate a new crop preview.
            GLib.idle_add(self._crop_page.set_updating_preview_state)

            self._preview_generator.generate_crop_preview(crop_preview_task)
            self._wait_for_preview_generation(crop_preview_task)

            if crop_preview_task.preview_file_path:
                GLib.idle_add(self._crop_page.update_preview)
                GLib.idle_add(self._crop_page.set_preview_available_state)
            else:
                GLib.idle_add(self._crop_page.set_preview_not_available_state)

        @staticmethod
        def _wait_for_preview_generation(crop_preview_task: task.CropPreview):
            # Waits for the preview generator to finish creating the crop preview file.
            if crop_preview_task.preview_threading_event.is_set():
                crop_preview_task.preview_threading_event.clear()

            crop_preview_task.preview_threading_event.wait()

        def add_preview_task(self, crop_preview_task: task.CropPreview):
            """
            Adds the given encoding task and time position to the preview queue in order to request a new crop preview.

            Parameters:
                crop_preview_task: Crop preview task to send to the preview queue.
            """
            self._preview_queue.put(crop_preview_task)

        def kill(self):
            """Empties the preview queue and stops the preview queue loop."""
            while not self._preview_queue.empty():
                self._preview_queue.get()

            self._preview_queue.put(False)


class TrimPage(Gtk.Box):
    """Class that contains the widgets that make up the application's trim page."""

    TRIM_DURATION_LABEL = 'Duration: '

    NOT_AVAILABLE_PAGE = 'not_available'
    AUDIO_PAGE = 'audio'
    PREVIEW_PAGE = 'preview'

    def __init__(self, preview_generator: preview.PreviewGenerator):
        """
        Initializes the TrimPage widgets class with the necessary variables for creating the application's trim page.

        Parameters:
            preview_generator: The preview.PreviewGenerator for creating previews for encoding tasks.
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

        self.encode_task = None
        self.video_duration = None
        self.is_widgets_setting_up = False
        self.trim_preview_task = None

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
        self._setup_audio_preview_status_page()
        self._setup_preview_not_available_status_page()
        self._setup_preview_stack()

    def _setup_preview_picture(self):
        # Instantiates the preview picture widget.
        self.preview_picture = Gtk.Picture()
        self.preview_picture.content_fit = True
        self.preview_picture.set_can_shrink(True)
        self.preview_picture.set_keep_aspect_ratio(True)

    def _setup_audio_preview_status_page(self):
        # Instantiates the audio preview status page widget.
        self.audio_preview_status_page = Adw.StatusPage.new()
        self.audio_preview_status_page.set_title('Audio Only')
        self.audio_preview_status_page.set_description('Preview not available for audio inputs')
        self.audio_preview_status_page.set_icon_name('audio-x-generic-symbolic')

    def _setup_preview_not_available_status_page(self):
        # Instantiates the preview not available status page widget.
        self.preview_not_available_status_page = Adw.StatusPage.new()
        self.preview_not_available_status_page.set_title('Preview Not Available')
        self.preview_not_available_status_page.set_description('Current settings can\'t be used for previews')
        self.preview_not_available_status_page.set_icon_name('action-unavailable-symbolic')
        self.preview_not_available_status_page.set_sensitive(False)

    def _setup_preview_stack(self):
        # Instantiates the preview stack widget.
        spacing_label = Gtk.Label.new()
        spacing_label.set_vexpand(True)
        spacing_label.set_hexpand(True)

        self.preview_stack = Gtk.Stack()
        self.preview_stack.add_named(self.preview_not_available_status_page, self.NOT_AVAILABLE_PAGE)
        self.preview_stack.add_named(self.audio_preview_status_page, self.AUDIO_PAGE)
        self.preview_stack.add_named(self.preview_picture, self.PREVIEW_PAGE)
        self.preview_stack.add_named(spacing_label, 'spacing')
        self.preview_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

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

        self._setup_trim_start_time_position_gesture_click()
        self._setup_trim_start_time_position_event_controller_key()
        self._setup_trim_start_time_position_event_controller_scroll()
        self.trim_start_scale.add_controller(self.trim_start_time_position_gesture_click)
        self.trim_start_scale.add_controller(self.trim_start_time_position_event_controller_key)
        self.trim_start_scale.add_controller(self.trim_start_time_position_event_controller_scroll)

    def _setup_trim_start_time_position_gesture_click(self):
        # Instantiates the start time position gesture click event controller.
        self.trim_start_time_position_gesture_click = Gtk.GestureClick.new()
        self.trim_start_time_position_gesture_click.connect('stopped',
                                                            self.on_scale_gesture_stopped,
                                                            self.trim_start_time_position_gesture_click)
        self.trim_start_time_position_gesture_click.connect('unpaired-release',
                                                            self.generate_new_preview,
                                                            self.trim_start_scale)

    def _setup_trim_start_time_position_event_controller_key(self):
        # Instantiates the trim start time position event controller key.
        self.trim_start_time_position_event_controller_key = Gtk.EventControllerKey.new()
        self.trim_start_time_position_event_controller_key.connect('key-released',
                                                                   self.generate_new_preview,
                                                                   self.trim_start_scale)

    def _setup_trim_start_time_position_event_controller_scroll(self):
        # Instantiates the trim start time position event controller scroll.
        self.trim_start_time_position_event_controller_scroll = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        self.trim_start_time_position_event_controller_scroll.connect('scroll', self.on_event_controller_scroll)

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

        self._setup_trim_end_time_position_gesture_click()
        self._setup_trim_end_time_position_event_controller_key()
        self._setup_trim_end_time_position_event_controller_scroll()
        self.trim_end_scale.add_controller(self.trim_end_time_position_gesture_click)
        self.trim_end_scale.add_controller(self.trim_end_time_position_event_controller_key)
        self.trim_end_scale.add_controller(self.trim_end_time_position_event_controller_scroll)

    def _setup_trim_end_time_position_gesture_click(self):
        # Instantiates the trim end time position gesture click event controller.
        self.trim_end_time_position_gesture_click = Gtk.GestureClick.new()
        self.trim_end_time_position_gesture_click.connect('stopped',
                                                          self.on_scale_gesture_stopped,
                                                          self.trim_end_time_position_gesture_click)
        self.trim_end_time_position_gesture_click.connect('unpaired-release',
                                                          self.generate_new_preview,
                                                          self.trim_end_scale)

    def _setup_trim_end_time_position_event_controller_key(self):
        # Instantiates the trim end time position event controller key.
        self.trim_end_time_position_event_controller_key = Gtk.EventControllerKey.new()
        self.trim_end_time_position_event_controller_key.connect('key-released',
                                                                 self.generate_new_preview,
                                                                 self.trim_end_scale)

    def _setup_trim_end_time_position_event_controller_scroll(self):
        # Instantiates the trim end time position event controller scroll.
        self.trim_end_time_position_event_controller_scroll = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.BOTH_AXES
        )
        self.trim_end_time_position_event_controller_scroll.connect('scroll', self.on_event_controller_scroll)

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

    def get_trim_end_time_position(self):
        """
        Returns the time position relative to the value of the trim end scale's value.

        Returns:
            Float that represents the time position relative to the value of the trim end scale's value.
        """
        end_time_position = self.video_duration - self.trim_end_scale.get_value()

        if end_time_position >= self.video_duration:
            end_time_position -= 1.0

        return end_time_position

    def is_trim_scale_bad_value(self, value: float) -> bool:
        """
        Returns whether the given trim scale value exceeds the total input video's duration or is below zero.

        Parameters:
            value: The value of the scale widget.

        Returns:
            Boolean that represents whether the given scale value is a bad value.
        """
        return value < 0 or value > self.video_duration

    def set_preview_state(self):
        """Sets the trim preview page's widgets for the preview state."""
        self.preview_stack.set_visible_child_name(self.PREVIEW_PAGE)
        self.preview_picture.set_opacity(1.0)
        self.trim_settings_group.set_sensitive(True)

    def set_updating_preview_state(self):
        """Sets the preview page's widgets for the updating preview state."""
        self.preview_picture.set_opacity(0.5)

    def set_audio_preview_state(self):
        """Sets the trim preview page's widgets for the audio preview state."""
        self.preview_stack.set_visible_child_name(self.AUDIO_PAGE)
        self.trim_settings_group.set_sensitive(True)

    def set_preview_not_available_state(self):
        """Sets the trim preview page's widgets for the preview not available state."""
        self.preview_stack.set_visible_child_name(self.NOT_AVAILABLE_PAGE)
        self.trim_settings_group.set_sensitive(False)

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

    def update_preview(self):
        """Re-sets the preview picture widget's file to the encoding task's trim preview file."""
        self.preview_picture.set_filename(self.trim_preview_task.preview_file_path)

    def generate_new_preview(self, *args, **kwargs):
        """For updating the preview when the encoding task's settings have changed."""
        if self.trim_start_time_position_event_controller_scroll in args \
                or self.trim_end_time_position_event_controller_scroll in args:
            time.sleep(0.25)

        if self.trim_start_scale in args:
            time_position = self.trim_start_scale.get_value()
        else:
            time_position = self.get_trim_end_time_position()

        self.trim_preview_task = task.TrimPreview(self.encode_task, time_position)
        self.trim_previewer.add_preview_task(self.trim_preview_task)

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

    def apply_settings_to_widgets(self, encode_task: task.Encode):
        """
        Applies the given encoding task's settings to the trim page's widgets.

        Parameters:
            encode_task: Encoding task to apply to the trim page's widgets.
        """
        if encode_task.input_file.is_folder:
            self.set_preview_not_available_state()

            return

        if encode_task is self.encode_task:
            return

        self.encode_task = encode_task
        self.video_duration = encode_task.input_file.duration
        self.generate_new_preview()

        GLib.idle_add(self.set_widgets_setting_up, True)
        GLib.idle_add(self.set_range_for_trim_scales, 0.0, self.video_duration)
        self._apply_trim_enabled_setting_to_widgets(encode_task)
        self._apply_trim_preview_to_widgets(encode_task)
        self._apply_trim_start_setting_to_widgets(encode_task)
        self._apply_trim_end_setting_to_widgets(encode_task)
        GLib.idle_add(self.set_widgets_setting_up, False)

    def _apply_trim_enabled_setting_to_widgets(self, encode_task: task.Encode):
        # Applies the encoding task's settings to the trim settings group's suffix widgets.
        if encode_task.trim_settings:
            GLib.idle_add(self.trim_settings_switch.set_active, True)

            trim_settings_label = ''.join([
                self.TRIM_DURATION_LABEL,
                format_converter.get_timecode_from_seconds(encode_task.trim_settings.trim_duration)
            ])
        else:
            GLib.idle_add(self.trim_settings_switch.set_active, False)

            trim_settings_label = ''.join([self.TRIM_DURATION_LABEL,
                                           format_converter.get_timecode_from_seconds(self.video_duration)])

        GLib.idle_add(self.trim_duration_label.set_label, trim_settings_label)

    def _apply_trim_preview_to_widgets(self, encode_task: task.Encode):
        # Applies the encoding task's trim preview file to the preview picture.
        if encode_task.input_file.is_video:
            # GLib.idle_add(self.preview_picture.set_filename, self.trim_preview_task.preview_file_path)
            GLib.idle_add(self.set_preview_state)
        else:
            GLib.idle_add(self.set_audio_preview_state)

    def _apply_trim_start_setting_to_widgets(self, encode_task: task.Encode):
        # Applies the encoding task's trim start time setting to the trim start widgets.
        if encode_task.trim_settings:
            GLib.idle_add(self.set_trim_start_value, encode_task.trim_settings.start_time)
        else:
            GLib.idle_add(self.set_trim_start_value, 0.0)

    def _apply_trim_end_setting_to_widgets(self, encode_task: task.Encode):
        # Applies the encoding task's trim end time setting to the trim end widgets.
        if encode_task.trim_settings:
            start_time = encode_task.trim_settings.start_time
            trim_duration = encode_task.trim_settings.trim_duration
            GLib.idle_add(self.set_trim_end_value, self.video_duration - (start_time + trim_duration))
        else:
            GLib.idle_add(self.set_trim_end_value, 0.0)

    def apply_settings_from_widgets(self):
        """Applies the state of the trim page's widgets to the encoding task."""
        if self.trim_settings_switch.get_active():
            start_time = self.trim_start_scale.get_value()
            seconds_from_end = self.trim_end_scale.get_value()
            trim_duration = (self.video_duration - seconds_from_end) - start_time

            trim_settings = task.TrimSettings()
            trim_settings.start_time = start_time
            trim_settings.trim_duration = trim_duration

            self.encode_task.trim_settings = trim_settings
        else:
            self.encode_task.trim_settings = None

        self.trim_preview_task.update_encode_task()

    def on_scale_gesture_stopped(self, user_data, gesture_click):
        """
        Signal callback function for the scale gesture click's 'stopped' signal.
        Checks if there's still a device associated with the gesture (click and hold) and then generates a new preview.

        Parameters:
            user_data: Extra data passed in from the signal.
            gesture_click: Gtk.GestureClick that emitted the signal.
        """
        if gesture_click.get_device():
            return

        if gesture_click is self.trim_start_time_position_gesture_click:
            scale = self.trim_start_scale
        else:
            scale = self.trim_end_scale

        self.generate_new_preview(scale)

    def on_event_controller_scroll(self, event_controller, dx, dy):
        """
        Signal callback function for the event controller scroll's 'scroll' signal.
        Generates a new preview.

        Parameters:
            event_controller: Gtk.EventControllerScroll that emitted the signal.
            dx: Direction of the scroll on the X-axis.
            dy: Direction of the scroll on the Y-axis.
        """
        if event_controller is self.trim_start_time_position_event_controller_scroll:
            scale = self.trim_start_scale
        else:
            scale = self.trim_end_scale

        threading.Thread(target=self.generate_new_preview, args=(scale, event_controller)).start()

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

        self.trim_preview_task = task.TrimPreview(self.encode_task, self.trim_start_scale.get_value())
        self.trim_previewer.add_preview_task(self.trim_preview_task)

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

        if self.is_widgets_setting_up:
            return

        self._adjust_trim_start_scale_overshoot(value)

    def _adjust_trim_start_scale_overshoot(self, scale_value: float):
        # Moves the trim end scale with the trim start scale if they were to start overlapping.
        trim_end_value = self.trim_end_scale.get_value()

        if scale_value > (self.video_duration - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_start_value(self.video_duration - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS)
        elif scale_value > ((self.video_duration - trim_end_value) - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_end_value(self.video_duration - (scale_value + task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS))

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

    def _adjust_trim_end_scale_overshoot(self, scale_value: float):
        # Moves the trim start scale with the trim end scale if they were to start overlapping.
        trim_start_value = self.trim_start_scale.get_value()

        if scale_value > (self.video_duration - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_end_value(self.video_duration - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS)
        elif scale_value > ((self.video_duration - trim_start_value) - task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS):
            self.set_trim_start_value(self.video_duration - (scale_value + task.TrimSettings.MIN_TRIM_DURATION_IN_SECONDS))

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
                trim_preview_task = self._preview_queue.get()

                if not trim_preview_task:
                    return

                trim_preview_task = self._wait_for_empty_queue(trim_preview_task)

                self._trim_page.apply_settings_from_widgets()

                if trim_preview_task.encode_task.input_file.is_video:
                    self._generate_preview(trim_preview_task)

        def _wait_for_empty_queue(self, trim_preview_task: task.TrimPreview) -> task.TrimPreview:
            # Consumes the queue until it's empty and stays empty for some time.
            time.sleep(0.1)

            while not self._preview_queue.empty():
                with self._preview_queue.mutex:
                    trim_preview_task, time_position = self._preview_queue.queue[-1]

                    self._preview_queue.queue.clear()

                time.sleep(0.1)

            return trim_preview_task

        def _generate_preview(self, trim_preview_task: task.TrimPreview):
            # Uses the preview generator to generate a new trim preview.
            GLib.idle_add(self._trim_page.set_updating_preview_state)

            self._preview_generator.generate_trim_preview(trim_preview_task)
            self._wait_for_preview_generation(trim_preview_task)

            if trim_preview_task.preview_file_path:
                GLib.idle_add(self._trim_page.set_preview_state)
            else:
                GLib.idle_add(self._trim_page.set_preview_not_available_state)

            GLib.idle_add(self._trim_page.update_preview)

        @staticmethod
        def _wait_for_preview_generation(trim_preview_task: task.TrimPreview):
            # Waits for the preview generator to finish creating the trim preview file.
            if trim_preview_task.preview_threading_event.is_set():
                trim_preview_task.preview_threading_event.clear()

            trim_preview_task.preview_threading_event.wait()

        def add_preview_task(self, trim_preview_task: task.TrimPreview):
            """
            Adds a new encoding task and the preview time position to the preview queue.

            Parameters:
                trim_preview_task: Trim preview task to generate a preview for.
            """
            self._preview_queue.put(trim_preview_task)

        def kill(self):
            """Empties the preview queue and stops the preview queue loop."""
            while not self._preview_queue.empty():
                self._preview_queue.get()

            self._preview_queue.put(False)


class BenchmarkPage(Gtk.Box):
    """Class that contains the widgets that make up the application's benchmark page."""

    BENCHMARK_TYPE_OPTIONS = ('Short', 'Long')

    NOT_AVAILABLE_PAGE = 'not_available'
    RUNNING_PAGE = 'running'
    IDLE_PAGE = 'idle'
    COMPLETE_PAGE = 'complete'

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
        self.encode_task = None
        self._benchmark_task = None
        self._is_stop_button_clicked = False
        self._stop_button_thread_lock = threading.Lock()

        self._setup_benchmark_page_contents()

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
        self._setup_benchmark_status_widgets()
        self._setup_benchmark_settings_widgets()

        self.append(self.benchmark_status_stack)
        self.append(self.benchmark_settings_vertical_box)

    def _setup_benchmark_status_widgets(self):
        # Instantiates the benchmark status pages widgets.
        self._setup_benchmark_not_available_page()
        self._setup_benchmark_idle_status_page()
        self._setup_benchmark_complete_status_page()
        self._setup_benchmark_running_status_page()
        self._setup_benchmark_status_stack()

    def _setup_benchmark_not_available_page(self):
        # Instantiates the benchmark not available page widget.
        self.benchmark_not_available_status_page = Adw.StatusPage.new()
        self.benchmark_not_available_status_page.set_title('Benchmark Not Available')
        self.benchmark_not_available_status_page.set_description('Cannot run a benchmark for folder inputs')
        self.benchmark_not_available_status_page.set_icon_name('action-unavailable-symbolic')
        self.benchmark_not_available_status_page.set_sensitive(False)

    def _setup_benchmark_idle_status_page(self):
        # Instantiates the benchmark idle status page widget.
        self.benchmark_idle_status_page = Adw.StatusPage.new()
        self.benchmark_idle_status_page.set_title('Benchmark Idle')
        self.benchmark_idle_status_page.set_description('Waiting to start a benchmark')
        self.benchmark_idle_status_page.set_icon_name('content-loading-symbolic')

    def _setup_benchmark_complete_status_page(self):
        # Instantiates the benchmark complete status page widget.
        self.benchmark_complete_status_page = Adw.StatusPage.new()
        self.benchmark_complete_status_page.set_title('Benchmark Complete')
        self.benchmark_complete_status_page.set_description('Check out the results')
        self.benchmark_complete_status_page.set_icon_name('emblem-ok-symbolic')

    def _setup_benchmark_running_status_page(self):
        # Instantiates the benchmark running status page widget.
        self._setup_benchmark_progress_bar()

        self.benchmark_running_status_page = Adw.StatusPage.new()
        self.benchmark_running_status_page.set_title('Running Benchmark')
        self.benchmark_running_status_page.set_description('Take a sip of tea...')
        self.benchmark_running_status_page.set_icon_name('system-run-symbolic')
        self.benchmark_running_status_page.set_child(self.benchmark_progress_bar)

    def _setup_benchmark_progress_bar(self):
        # Instantiates the benchmark progress bar widget.
        self.benchmark_progress_bar = Gtk.ProgressBar()
        self.benchmark_progress_bar.set_hexpand(True)
        self.benchmark_progress_bar.set_margin_start(40)
        self.benchmark_progress_bar.set_margin_end(40)

    def _setup_benchmark_status_stack(self):
        # Instantiates the benchmark status stack widget.
        spacing_label = Gtk.Label.new()
        spacing_label.set_vexpand(True)
        spacing_label.set_hexpand(True)

        self.benchmark_status_stack = Gtk.Stack.new()
        self.benchmark_status_stack.add_named(self.benchmark_not_available_status_page, self.NOT_AVAILABLE_PAGE)
        self.benchmark_status_stack.add_named(self.benchmark_idle_status_page, self.IDLE_PAGE)
        self.benchmark_status_stack.add_named(self.benchmark_running_status_page, self.RUNNING_PAGE)
        self.benchmark_status_stack.add_named(self.benchmark_complete_status_page, self.COMPLETE_PAGE)
        self.benchmark_status_stack.add_named(spacing_label, 'spacing')
        self.benchmark_status_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

    def _setup_benchmark_results_widgets(self):
        # Instantiates the benchmark results widgets.
        self._setup_results_grid()
        self._setup_results_row()

        self.results_group = Adw.PreferencesGroup()
        self.results_group.set_title('Results')
        self.results_group.add(self.results_row)

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

    def _setup_benchmark_settings_widgets(self):
        # Instantiates the benchmark settings widgets.
        self._setup_results_grid()
        self._setup_results_row()
        self._setup_benchmark_type_row()
        self._setup_start_stop_button()

        self.benchmark_type_group = Adw.PreferencesGroup()
        self.benchmark_type_group.set_title('Settings')
        self.benchmark_type_group.add(self.results_row)
        self.benchmark_type_group.add(self.benchmark_type_combo_row)

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

    def set_benchmark_idle_state(self):
        """Sets the benchmark page's widgets for the idle state."""
        self.benchmark_status_stack.set_visible_child_name(self.IDLE_PAGE)
        self.reset_results()
        self.start_stop_button_stack.set_visible_child_name('start')
        self.start_stop_button_stack.set_sensitive(True)

    def set_benchmark_running_state(self):
        """Sets the benchmark page's widgets for the running state."""
        self.benchmark_status_stack.set_visible_child_name(self.RUNNING_PAGE)
        self.reset_results()
        self.start_stop_button_stack.set_visible_child_name('stop')

    def set_benchmark_complete_state(self):
        """Sets the benchmark page's widgets for the completed state."""
        self.benchmark_status_stack.set_visible_child_name(self.COMPLETE_PAGE)
        self.start_stop_button_stack.set_visible_child_name('start')

    def set_benchmark_not_available_state(self):
        """Sets the benchmark page's widgets for the not available state."""
        self.benchmark_status_stack.set_visible_child_name(self.NOT_AVAILABLE_PAGE)
        self.start_stop_button_stack.set_sensitive(False)

    def reset_results(self):
        """Resets the state of the results widgets."""
        self.bitrate_results_label.set_label('--')
        self.speed_result_label.set_label('--')
        self.file_size_result_label.set_label('--')
        self.encode_time_result_label.set_label('--')
        self.benchmark_progress_bar.set_fraction(0.0)

    def setup_encode_task(self, encode_task: task.Encode):
        """
        Sets a new encoding task to use for the benchmark and resets the state of the benchmark widgets.

        Parameters:
            encode_task: The new encoding task to use for the benchmark.
        """
        if encode_task.input_file.is_folder:
            self.set_benchmark_not_available_state()

            return

        if encode_task is self.encode_task:
            return

        self.encode_task = encode_task
        self.set_benchmark_idle_state()

    def stop_benchmark(self):
        """Sets the encoding task's stop benchmark state."""
        if self._benchmark_task:
            self._benchmark_task.is_stopped = True

    def start_benchmark(self):
        """
        Starts a benchmark for the encoding task. Adds the encoding task to the benchmark generator
        and waits for the benchmark to complete. This needs to be run in a thread otherwise it will block.
        """
        GLib.idle_add(self.set_benchmark_running_state)

        if self.encode_task:
            self._benchmark_task = task.Benchmark(self.encode_task, bool(self.benchmark_type_combo_row.get_selected))
            self.benchmark_generator.add_benchmark_task(self._benchmark_task)
            self._wait_until_benchmark_is_done()

        if self.is_stop_button_clicked:
            GLib.idle_add(self.set_benchmark_idle_state)
        else:
            GLib.idle_add(self.set_benchmark_complete_state)

    def _wait_until_benchmark_is_done(self):
        # Waits for the benchmark to start and then waits for the benchmark to finish.
        while not self._benchmark_task.has_started and not self._benchmark_task.is_stopped:
            time.sleep(0.25)

        while self._benchmark_task.has_started and not self._benchmark_task.is_stopped:
            self._update_results()

            time.sleep(1)

        if not self.is_stop_button_clicked:
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
        if self._benchmark_task.bitrate is not None:
            GLib.idle_add(self.bitrate_results_label.set_label, str(self._benchmark_task.bitrate) + 'Kbps')

    def _update_speed_results(self):
        # Updates the speed results widget using the encoding task's benchmark speed value.
        if self._benchmark_task.speed is not None:
            GLib.idle_add(self.speed_result_label.set_label, str(self._benchmark_task.speed) + 'x')

    def _update_benchmark_progress(self):
        # Updates the benchmark progress widget using the encoding task's benchmark progress value.
        if self._benchmark_task.progress is not None:
            GLib.idle_add(self.benchmark_progress_bar.set_fraction, self._benchmark_task.progress)

    def _update_final_results(self):
        # Updates all the benchmark results widgets using the encoding task's benchmark values.
        self._update_results()
        self._update_file_size_results()
        self._update_encode_time_results()

    def _update_file_size_results(self):
        # Updates the file size results widget using the encoding task's benchmark file size value.
        try:
            GLib.idle_add(self.file_size_result_label.set_label,
                          format_converter.get_file_size_from_bytes(self._benchmark_task.file_size))
        except TypeError as e:
            GLib.idle_add(self.file_size_result_label.set_label, 'Error')

            logging.exception(e)

    def _update_encode_time_results(self):
        # Updates the encode time results widget using the encoding task's benchmark time estimate value.
        try:
            GLib.idle_add(self.encode_time_result_label.set_label,
                          format_converter.get_timecode_from_seconds(self._benchmark_task.encode_time_estimate))
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
        self.is_stop_button_clicked = False
        threading.Thread(target=self.start_benchmark, args=()).start()

    def on_stop_button_clicked(self, button):
        """
        Signal callback function for the stop button's 'clicked' signal.
        Shows the start button and stops the benchmark process.

        Parameters:
            button: Gtk.Button that emitted the signal.
        """
        self.is_stop_button_clicked = True
        self.stop_benchmark()
