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


from render_watch.ui import Gtk, Adw
from render_watch.ffmpeg import encoding, general_settings, filters, x264
from render_watch import app_preferences


class SettingsSidebarWidgets:

    SIDEBAR_WIDTH = 450

    def __init__(self, inputs_page, app_settings: app_preferences.Settings):
        self.inputs_page = inputs_page
        self.app_settings = app_settings
        self.main_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self._setup_settings_sidebar_widgets()

    def _setup_settings_sidebar_widgets(self):
        self._setup_settings_pages()
        self._setup_settings_view_switcher()
        self._setup_preview_buttons()

        self.main_widget.append(self.settings_view_switcher)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.settings_page_stack)
        self.main_widget.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.main_widget.append(self.preview_buttons_horizontal_box)
        self.main_widget.set_size_request(self.SIDEBAR_WIDTH, -1)
        self.main_widget.set_hexpand(False)

    def _setup_settings_pages(self):
        self._setup_general_settings_page()
        self._setup_video_codec_settings_page()
        self._setup_audio_codec_settings_page()
        self._setup_filter_settings_page()
        self._setup_subtitle_settings_page()

    def _setup_general_settings_page(self):
        self.general_settings_page = self.GeneralSettingsPage()

    def _setup_video_codec_settings_page(self):
        self.video_codec_settings_page = self.VideoCodecSettingsPage(self.inputs_page)

    def _setup_audio_codec_settings_page(self):
        self.audio_codec_settings_page = self.AudioCodecSettingsPage(self.inputs_page)

    def _setup_filter_settings_page(self):
        self.filter_settings_page = self.FilterSettingsPage()

    def _setup_subtitle_settings_page(self):
        self.subtitle_settings_page = self.SubtitleSettingsPage(self.inputs_page)

    def _setup_settings_view_switcher(self):
        self._setup_settings_page_stack()

        self.settings_view_switcher = Adw.ViewSwitcher()
        self.settings_view_switcher.set_policy(Adw.ViewSwitcherPolicy.NARROW)
        self.settings_view_switcher.set_stack(self.settings_page_stack)

    def _setup_settings_page_stack(self):
        self.settings_page_stack = Adw.ViewStack()
        self.settings_page_stack.add_titled(self.general_settings_page, 'general_settings_page', 'General')
        self.settings_page_stack.add_titled(self.video_codec_settings_page, 'video_codec_settings_page', 'Video Codec')
        self.settings_page_stack.add_titled(self.audio_codec_settings_page, 'audio_codec_settings_page', 'Audio Codec')
        self.settings_page_stack.add_titled(self.filter_settings_page, 'filter_settings_page', 'Filters')
        self.settings_page_stack.add_titled(self.subtitle_settings_page, 'subtitle_settings_page', 'Subtitles')
        self.settings_page_stack.get_page(self.general_settings_page).set_icon_name('preferences-system-symbolic')
        self.settings_page_stack.get_page(self.video_codec_settings_page).set_icon_name('video-x-generic-symbolic')
        self.settings_page_stack.get_page(self.audio_codec_settings_page).set_icon_name('audio-x-generic-symbolic')
        self.settings_page_stack.get_page(self.filter_settings_page).set_icon_name('insert-image-symbolic')
        self.settings_page_stack.get_page(self.subtitle_settings_page).set_icon_name('insert-text-symbolic')

    def _setup_preview_buttons(self):
        settings_preview_button = Gtk.Button.new_from_icon_name('video-display-symbolic')
        crop_preview_button = Gtk.Button.new_from_icon_name('zoom-fit-best-symbolic')
        trim_preview_button = Gtk.Button.new_from_icon_name('edit-cut-symbolic')
        benchmark_button = Gtk.Button.new_from_icon_name('system-run-symbolic')

        self.preview_buttons_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.preview_buttons_horizontal_box.append(settings_preview_button)
        self.preview_buttons_horizontal_box.append(crop_preview_button)
        self.preview_buttons_horizontal_box.append(trim_preview_button)
        self.preview_buttons_horizontal_box.append(benchmark_button)
        self.preview_buttons_horizontal_box.set_hexpand(False)
        self.preview_buttons_horizontal_box.set_halign(Gtk.Align.CENTER)
        self.preview_buttons_horizontal_box.set_margin_top(10)
        self.preview_buttons_horizontal_box.set_margin_bottom(10)

    class SettingsGroup(Adw.PreferencesGroup):
        def __init__(self):
            super().__init__()

            self.children = []
            self.number_of_children = 0

        def add(self, preferences_row: Adw.PreferencesRow):
            super().add(preferences_row)

            if preferences_row not in self.children:
                self.children.append(preferences_row)
                self.number_of_children += 1

        def remove(self, preferences_row: Adw.PreferencesRow):
            if preferences_row in self.children:
                super().remove(preferences_row)
                self.children.remove(preferences_row)
                self.number_of_children -= 1

                self.update_children()

        def remove_children(self):
            for child in self.children:
                super().remove(child)

        def update_children(self):
            for index, child in enumerate(self.children):
                child.row_count = index + 1
                child.update_title()

    class GeneralSettingsPage(Gtk.ScrolledWindow):
        def __init__(self):
            super().__init__()

            self._setup_preset_settings()
            self._setup_output_file_settings()
            self._setup_frame_rate_settings()

            general_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            general_settings_vertical_box.append(self.preset_settings_group)
            general_settings_vertical_box.append(self.output_settings_group)
            general_settings_vertical_box.append(self.frame_rate_settings_group)
            general_settings_vertical_box.set_margin_top(20)
            general_settings_vertical_box.set_margin_bottom(20)
            general_settings_vertical_box.set_margin_start(20)
            general_settings_vertical_box.set_margin_end(20)

            self.set_child(general_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_preset_settings(self):
            self.preset_settings_group = Adw.PreferencesGroup()
            self.preset_settings_group.set_title('Preset')

        def _setup_output_file_settings(self):
            self._setup_extension_setting()
            self._setup_fast_start_setting()

            self.output_settings_group = Adw.PreferencesGroup()
            self.output_settings_group.set_title('Output File')
            self.output_settings_group.add(self.extension_row)
            self.output_settings_group.add(self.fast_start_row)

        def _setup_extension_setting(self):
            extension_combobox = Gtk.ComboBoxText()
            extension_combobox.set_vexpand(False)
            extension_combobox.set_valign(Gtk.Align.CENTER)

            for extension in encoding.output.CONTAINERS:
                extension_combobox.append_text(extension)

            extension_combobox.set_active(0)

            self.extension_row = Adw.ActionRow()
            self.extension_row.set_title('Extension')
            self.extension_row.set_subtitle('Output file extension type')
            self.extension_row.add_suffix(extension_combobox)

        def _setup_fast_start_setting(self):
            fast_start_switch = Gtk.Switch()
            fast_start_switch.set_vexpand(False)
            fast_start_switch.set_valign(Gtk.Align.CENTER)

            self.fast_start_row = Adw.ActionRow()
            self.fast_start_row.set_title('Fast Start')
            self.fast_start_row.set_subtitle('Move MOV atom to the beginning of the file')
            self.fast_start_row.add_suffix(fast_start_switch)

        def _setup_frame_rate_settings(self):
            self._setup_custom_frame_rate_setting()

            auto_frame_rate_switch = Gtk.Switch()
            auto_frame_rate_switch.set_vexpand(False)
            auto_frame_rate_switch.set_valign(Gtk.Align.CENTER)

            self.frame_rate_settings_group = Adw.PreferencesGroup()
            self.frame_rate_settings_group.set_title('Frame Rate')
            self.frame_rate_settings_group.set_header_suffix(auto_frame_rate_switch)
            self.frame_rate_settings_group.add(self.custom_frame_rate_row)

        def _setup_custom_frame_rate_setting(self):
            custom_frame_rate_combobox = Gtk.ComboBoxText()
            custom_frame_rate_combobox.set_vexpand(False)
            custom_frame_rate_combobox.set_valign(Gtk.Align.CENTER)

            for frame_rate in general_settings.GeneralSettings.FRAME_RATE:
                custom_frame_rate_combobox.append_text(frame_rate)

            custom_frame_rate_combobox.set_active(0)

            self.custom_frame_rate_row = Adw.ActionRow()
            self.custom_frame_rate_row.set_title('Frames Per Second')
            self.custom_frame_rate_row.set_subtitle('Output\'s frame rate')
            self.custom_frame_rate_row.add_suffix(custom_frame_rate_combobox)
            self.custom_frame_rate_row.set_sensitive(False)

    class VideoCodecSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page

            self._setup_video_stream_settings()
            self._setup_video_codec_settings_pages()

            video_codec_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            video_codec_settings_vertical_box.append(self.video_stream_settings_group)
            video_codec_settings_vertical_box.append(self.video_codec_settings_stack)
            video_codec_settings_vertical_box.set_margin_top(20)
            video_codec_settings_vertical_box.set_margin_bottom(20)
            video_codec_settings_vertical_box.set_margin_start(20)
            video_codec_settings_vertical_box.set_margin_end(20)

            self.set_child(video_codec_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_video_stream_settings(self):
            self._setup_video_stream_row()
            self._setup_video_codec_row()

            self.video_stream_settings_group = Adw.PreferencesGroup()
            self.video_stream_settings_group.set_title('Video Stream')
            self.video_stream_settings_group.add(self.video_stream_row)
            self.video_stream_settings_group.add(self.video_codec_row)

        def _setup_video_stream_row(self):
            self._setup_video_stream_combobox()

            self.video_stream_row = Adw.ActionRow()
            self.video_stream_row.set_title('Selected Stream')
            self.video_stream_row.set_subtitle('Video stream to use for the codec settings')
            self.video_stream_row.add_suffix(self.video_stream_combobox)

        def _setup_video_stream_combobox(self):
            self.video_stream_combobox = Gtk.ComboBoxText()
            self.video_stream_combobox.set_vexpand(False)
            self.video_stream_combobox.set_valign(Gtk.Align.CENTER)

        def _setup_video_codec_row(self):
            self._setup_video_codec_combobox()

            self.video_codec_row = Adw.ActionRow()
            self.video_codec_row.set_title('Video Codec')
            self.video_codec_row.set_subtitle('Codec to encode the video stream')
            self.video_codec_row.add_suffix(self.video_codec_combobox)

        def _setup_video_codec_combobox(self):
            self.video_codec_combobox = Gtk.ComboBoxText()
            self.video_codec_combobox.set_vexpand(False)
            self.video_codec_combobox.set_valign(Gtk.Align.CENTER)

        def _setup_video_codec_settings_pages(self):
            x264_page = self.X264StackPage()

            self.video_codec_settings_stack = Gtk.Stack()
            self.video_codec_settings_stack.add_named(x264_page, 'x264_page')
            self.video_codec_settings_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        class X264StackPage(Gtk.Box):
            def __init__(self):
                super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)

                self._setup_codec_settings()
                self._setup_codec_advanced_settings()

                self.append(self.codec_settings_group)
                self.append(self.advanced_codec_settings_group)

            def _setup_codec_settings(self):
                self._setup_preset_row()
                self._setup_profile_row()
                self._setup_level_row()
                self._setup_tune_row()
                self._setup_rate_type_row()
                self._setup_rate_type_settings_row()

                self.codec_settings_group = Adw.PreferencesGroup()
                self.codec_settings_group.set_title('X264 Settings')
                self.codec_settings_group.add(self.preset_row)
                self.codec_settings_group.add(self.profile_row)
                self.codec_settings_group.add(self.level_row)
                self.codec_settings_group.add(self.tune_row)
                self.codec_settings_group.add(self.rate_type_row)
                self.codec_settings_group.add(self.rate_type_settings_row)

            def _setup_preset_row(self):
                self._setup_preset_combobox()

                self.preset_row = Adw.ActionRow()
                self.preset_row.set_title('Preset')
                self.preset_row.set_subtitle('Encoding preset')
                self.preset_row.add_suffix(self.preset_combobox)

            def _setup_preset_combobox(self):
                self.preset_combobox = Gtk.ComboBoxText()
                self.preset_combobox.set_vexpand(False)
                self.preset_combobox.set_valign(Gtk.Align.CENTER)

                for preset_setting in x264.X264.PRESET:
                    self.preset_combobox.append_text(preset_setting)

                self.preset_combobox.set_active(0)

            def _setup_profile_row(self):
                self._setup_profile_combobox()

                self.profile_row = Adw.ActionRow()
                self.profile_row.set_title('Profile')
                self.profile_row.set_subtitle('Profile restrictions')
                self.profile_row.add_suffix(self.profile_combobox)

            def _setup_profile_combobox(self):
                self.profile_combobox = Gtk.ComboBoxText()
                self.profile_combobox.set_vexpand(False)
                self.profile_combobox.set_valign(Gtk.Align.CENTER)

                for profile_setting in x264.X264.PROFILE:
                    self.profile_combobox.append_text(profile_setting)

                self.profile_combobox.set_active(0)

            def _setup_level_row(self):
                self._setup_level_combobox()

                self.level_row = Adw.ActionRow()
                self.level_row.set_title('Level')
                self.level_row.set_subtitle('Specified level')
                self.level_row.add_suffix(self.level_combobox)

            def _setup_level_combobox(self):
                self.level_combobox = Gtk.ComboBoxText()
                self.level_combobox.set_vexpand(False)
                self.level_combobox.set_valign(Gtk.Align.CENTER)

                for level_setting in x264.X264.LEVEL:
                    self.level_combobox.append_text(level_setting)

                self.level_combobox.set_active(0)

            def _setup_tune_row(self):
                self._setup_tune_combobox()

                self.tune_row = Adw.ActionRow()
                self.tune_row.set_title('Tune')
                self.tune_row.set_subtitle('Tune encoder parameters')
                self.tune_row.add_suffix(self.tune_combobox)

            def _setup_tune_combobox(self):
                self.tune_combobox = Gtk.ComboBoxText()
                self.tune_combobox.set_vexpand(False)
                self.tune_combobox.set_valign(Gtk.Align.CENTER)

                for tune_setting in x264.X264.TUNE:
                    self.tune_combobox.append_text(tune_setting)

                self.tune_combobox.set_active(0)

            def _setup_rate_type_row(self):
                self._setup_rate_type_radio_buttons()

                self.rate_type_row = Adw.ActionRow()
                self.rate_type_row.set_title('Rate Type')
                self.rate_type_row.set_subtitle('Codec rate type method')
                self.rate_type_row.add_suffix(self.rate_type_horizontal_box)

            def _setup_rate_type_radio_buttons(self):
                crf_check_button = Gtk.CheckButton(label='CRF')
                crf_check_button.set_active(True)
                crf_check_button.connect('toggled', self.on_crf_check_button_toggled)

                qp_check_button = Gtk.CheckButton(label='QP')
                qp_check_button.set_group(crf_check_button)
                qp_check_button.connect('toggled', self.on_qp_check_button_toggled)

                self.bitrate_check_button = Gtk.CheckButton(label='Bitrate')
                self.bitrate_check_button.set_group(crf_check_button)
                self.bitrate_check_button.connect('toggled', self.on_bitrate_check_button_toggled)

                self.rate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.rate_type_horizontal_box.append(crf_check_button)
                self.rate_type_horizontal_box.append(qp_check_button)
                self.rate_type_horizontal_box.append(self.bitrate_check_button)

            def _setup_rate_type_settings_row(self):
                self._setup_rate_type_settings_stack()

                self.rate_type_settings_row = Adw.ActionRow()
                self.rate_type_settings_row.set_title('CRF')
                self.rate_type_settings_row.set_subtitle('Constant Ratefactor')
                self.rate_type_settings_row.add_suffix(self.rate_type_stack)

            def _setup_rate_type_settings_stack(self):
                self._setup_crf_page()
                self._setup_qp_page()
                self._setup_bitrate_page()

                self.rate_type_stack = Gtk.Stack()
                self.rate_type_stack.add_named(self.crf_scale, 'crf_page')
                self.rate_type_stack.add_named(self.qp_scale, 'qp_page')
                self.rate_type_stack.add_named(self.bitrate_page_vertical_box, 'bitrate_page')
                self.rate_type_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

            def _setup_crf_page(self):
                self.crf_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                          min=x264.X264.CRF_MIN,
                                                          max=x264.X264.CRF_MAX,
                                                          step=1.0)
                self.crf_scale.set_value(20.0)
                self.crf_scale.set_digits(1)
                self.crf_scale.set_draw_value(True)
                self.crf_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.crf_scale.set_hexpand(True)

            def _setup_qp_page(self):
                self.qp_scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL,
                                                         min=x264.X264.QP_MIN,
                                                         max=x264.X264.QP_MAX,
                                                         step=1.0)
                self.qp_scale.set_value(20.0)
                self.qp_scale.set_digits(1)
                self.qp_scale.set_draw_value(True)
                self.qp_scale.set_value_pos(Gtk.PositionType.BOTTOM)
                self.qp_scale.set_hexpand(True)

            def _setup_bitrate_page(self):
                self._setup_bitrate_spin_button()
                self._setup_bitrate_type_widgets()

                self.bitrate_page_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.bitrate_page_vertical_box.append(self.bitrate_spin_button)
                self.bitrate_page_vertical_box.append(self.bitrate_type_horizontal_box)
                self.bitrate_page_vertical_box.set_margin_top(10)
                self.bitrate_page_vertical_box.set_margin_bottom(10)
                self.bitrate_page_vertical_box.set_hexpand(False)
                self.bitrate_page_vertical_box.set_halign(Gtk.Align.END)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(x264.X264.BITRATE_MIN, x264.X264.BITRATE_MAX)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(100, 500)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)
                self.bitrate_spin_button.set_value(2500)
                self.bitrate_spin_button.set_size_request(125, -1)
                self.bitrate_spin_button.set_vexpand(True)
                self.bitrate_spin_button.set_valign(Gtk.Align.END)
                self.bitrate_spin_button.set_hexpand(True)
                self.bitrate_spin_button.set_halign(Gtk.Align.CENTER)

            def _setup_bitrate_type_widgets(self):
                self.average_check_button = Gtk.CheckButton(label='Average')
                self.average_check_button.set_active(True)

                self.constant_check_button = Gtk.CheckButton(label='Constant')
                self.constant_check_button.set_group(self.average_check_button)

                self.dual_pass_check_button = Gtk.CheckButton(label='2-Pass')
                self.dual_pass_check_button.set_group(self.average_check_button)

                self.bitrate_type_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.bitrate_type_horizontal_box.append(self.average_check_button)
                self.bitrate_type_horizontal_box.append(self.constant_check_button)
                self.bitrate_type_horizontal_box.append(self.dual_pass_check_button)
                self.bitrate_type_horizontal_box.set_vexpand(True)
                self.bitrate_type_horizontal_box.set_valign(Gtk.Align.START)

            def _setup_codec_advanced_settings(self):
                self._setup_keyint_row()
                self._setup_min_keyint_row()
                self._setup_scenecut_row()
                self._setup_b_frames_row()
                self._setup_b_adapt_row()
                self._setup_b_pyramid_row()
                self._setup_no_cabac_row()
                self._setup_ref_row()
                self._setup_deblock_row()
                self._setup_vbv_maxrate_row()
                self._setup_vbv_bufsize_row()
                self._setup_aq_mode_row()
                self._setup_aq_strength_row()
                self._setup_partitions_row()
                self._setup_direct_row()
                self._setup_weight_b_row()
                self._setup_me_row()
                self._setup_me_range_row()
                self._setup_subme_row()
                self._setup_psy_rd_row()
                self._setup_mixed_refs_row()
                self._setup_dct8x8_row()
                self._setup_trellis_row()
                self._setup_no_fast_pskip_row()
                self._setup_no_dct_decimate_row()
                self._setup_weight_p_row()

                advanced_settings_switch = Gtk.Switch()
                advanced_settings_switch.set_vexpand(False)
                advanced_settings_switch.set_valign(Gtk.Align.CENTER)
                advanced_settings_switch.connect('state-set', self._on_advanced_settings_switch_state_set)

                self.advanced_codec_settings_group = Adw.PreferencesGroup()
                self.advanced_codec_settings_group.set_title('Advanced Settings')
                self.advanced_codec_settings_group.set_header_suffix(advanced_settings_switch)
                self.advanced_codec_settings_group.add(self.vbv_maxrate_row)
                self.advanced_codec_settings_group.add(self.vbv_bufsize_row)
                self.advanced_codec_settings_group.add(self.keyint_row)
                self.advanced_codec_settings_group.add(self.min_keyint_row)
                self.advanced_codec_settings_group.add(self.scenecut_row)
                self.advanced_codec_settings_group.add(self.b_frames_row)
                self.advanced_codec_settings_group.add(self.b_adapt_row)
                self.advanced_codec_settings_group.add(self.b_pyramid_row)
                self.advanced_codec_settings_group.add(self.weight_b_row)
                self.advanced_codec_settings_group.add(self.weight_p_row)
                self.advanced_codec_settings_group.add(self.no_fast_pskip_row)
                self.advanced_codec_settings_group.add(self.ref_row)
                self.advanced_codec_settings_group.add(self.mixed_refs_row)
                self.advanced_codec_settings_group.add(self.no_cabac_row)
                self.advanced_codec_settings_group.add(self.deblock_row)
                self.advanced_codec_settings_group.add(self.aq_mode_row)
                self.advanced_codec_settings_group.add(self.aq_strength_row)
                self.advanced_codec_settings_group.add(self.partitions_row)
                self.advanced_codec_settings_group.add(self.dct8x8_row)
                self.advanced_codec_settings_group.add(self.direct_row)
                self.advanced_codec_settings_group.add(self.me_row)
                self.advanced_codec_settings_group.add(self.me_range_row)
                self.advanced_codec_settings_group.add(self.subme_row)
                self.advanced_codec_settings_group.add(self.psyrd_row)
                self.advanced_codec_settings_group.add(self.trellis_row)
                self.advanced_codec_settings_group.add(self.no_dct_decimate_row)

            def _setup_keyint_row(self):
                self._setup_keyint_spin_button()

                self.keyint_row = Adw.ActionRow()
                self.keyint_row.set_title('Keyint')
                self.keyint_row.set_subtitle('Maximum interval between keyframes')
                self.keyint_row.add_suffix(self.keyint_spin_button)
                self.keyint_row.set_sensitive(False)

            def _setup_keyint_spin_button(self):
                self.keyint_spin_button = Gtk.SpinButton()
                self.keyint_spin_button.set_range(x264.X264.KEYINT_MIN, x264.X264.KEYINT_MAX)
                self.keyint_spin_button.set_digits(0)
                self.keyint_spin_button.set_increments(10, 100)
                self.keyint_spin_button.set_numeric(True)
                self.keyint_spin_button.set_snap_to_ticks(True)
                self.keyint_spin_button.set_value(250)
                self.keyint_spin_button.set_vexpand(False)
                self.keyint_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_min_keyint_row(self):
                self._setup_min_keyint_spin_button()

                self.min_keyint_row = Adw.ActionRow()
                self.min_keyint_row.set_title('Min Keyint')
                self.min_keyint_row.set_subtitle('Minimum interval between keyframes')
                self.min_keyint_row.add_suffix(self.min_keyint_spin_button)
                self.min_keyint_row.set_sensitive(False)

            def _setup_min_keyint_spin_button(self):
                self.min_keyint_spin_button = Gtk.SpinButton()
                self.min_keyint_spin_button.set_range(x264.X264.KEYINT_MIN, x264.X264.KEYINT_MAX)
                self.min_keyint_spin_button.set_digits(0)
                self.min_keyint_spin_button.set_increments(10, 100)
                self.min_keyint_spin_button.set_numeric(True)
                self.min_keyint_spin_button.set_snap_to_ticks(True)
                self.min_keyint_spin_button.set_value(25)
                self.min_keyint_spin_button.set_vexpand(False)
                self.min_keyint_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_scenecut_row(self):
                self._setup_scenecut_spin_button()

                self.scenecut_row = Adw.ActionRow()
                self.scenecut_row.set_title('Scenecut')
                self.scenecut_row.set_subtitle('Threshold for keyframe placement')
                self.scenecut_row.add_suffix(self.scenecut_spin_button)
                self.scenecut_row.set_sensitive(False)

            def _setup_scenecut_spin_button(self):
                self.scenecut_spin_button = Gtk.SpinButton()
                self.scenecut_spin_button.set_range(x264.X264.SCENECUT_MIN, x264.X264.SCENECUT_MAX)
                self.scenecut_spin_button.set_digits(0)
                self.scenecut_spin_button.set_increments(10, 100)
                self.scenecut_spin_button.set_numeric(True)
                self.scenecut_spin_button.set_snap_to_ticks(True)
                self.scenecut_spin_button.set_value(40)
                self.scenecut_spin_button.set_vexpand(False)
                self.scenecut_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_b_frames_row(self):
                self._setup_b_frames_spin_button()

                self.b_frames_row = Adw.ActionRow()
                self.b_frames_row.set_title('B-Frames')
                self.b_frames_row.set_subtitle('Maximum concurrent B-frames that can be used')
                self.b_frames_row.add_suffix(self.b_frames_spin_button)
                self.b_frames_row.set_sensitive(False)

            def _setup_b_frames_spin_button(self):
                self.b_frames_spin_button = Gtk.SpinButton()
                self.b_frames_spin_button.set_range(x264.X264.B_FRAMES_MIN, x264.X264.B_FRAMES_MAX)
                self.b_frames_spin_button.set_digits(0)
                self.b_frames_spin_button.set_increments(1, 5)
                self.b_frames_spin_button.set_numeric(True)
                self.b_frames_spin_button.set_snap_to_ticks(True)
                self.b_frames_spin_button.set_value(3)
                self.b_frames_spin_button.set_vexpand(False)
                self.b_frames_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_b_adapt_row(self):
                self._setup_b_adapt_combobox()

                self.b_adapt_row = Adw.ActionRow()
                self.b_adapt_row.set_title('B-Adapt')
                self.b_adapt_row.set_subtitle('B-frame placement method')
                self.b_adapt_row.add_suffix(self.b_adapt_combobox)
                self.b_adapt_row.set_sensitive(False)

            def _setup_b_adapt_combobox(self):
                self.b_adapt_combobox = Gtk.ComboBoxText()
                self.b_adapt_combobox.set_vexpand(False)
                self.b_adapt_combobox.set_valign(Gtk.Align.CENTER)

                for b_adapt_setting in x264.X264.B_ADAPT:
                    self.b_adapt_combobox.append_text(b_adapt_setting)

                self.b_adapt_combobox.set_active(0)

            def _setup_b_pyramid_row(self):
                self._setup_b_pyramid_combobox()

                self.b_pyramid_row = Adw.ActionRow()
                self.b_pyramid_row.set_title('B-Pyramid')
                self.b_pyramid_row.set_subtitle('Allows B-frames to be referenced by other frames')
                self.b_pyramid_row.add_suffix(self.b_pyramid_combobox)
                self.b_pyramid_row.set_sensitive(False)

            def _setup_b_pyramid_combobox(self):
                self.b_pyramid_combobox = Gtk.ComboBoxText()
                self.b_pyramid_combobox.set_vexpand(False)
                self.b_pyramid_combobox.set_valign(Gtk.Align.CENTER)

                for b_pyramid_setting in x264.X264.B_PYRAMID_UI:
                    self.b_pyramid_combobox.append_text(b_pyramid_setting)

                self.b_pyramid_combobox.set_active(0)

            def _setup_no_cabac_row(self):
                self._setup_no_cabac_switch()

                self.no_cabac_row = Adw.ActionRow()
                self.no_cabac_row.set_title('No CABAC')
                self.no_cabac_row.set_subtitle('Disables the Context Adaptive Binary Arithmetic Coder')
                self.no_cabac_row.add_suffix(self.no_cabac_switch)
                self.no_cabac_row.set_sensitive(False)

            def _setup_no_cabac_switch(self):
                self.no_cabac_switch = Gtk.Switch()
                self.no_cabac_switch.set_vexpand(False)
                self.no_cabac_switch.set_valign(Gtk.Align.CENTER)

            def _setup_ref_row(self):
                self._setup_ref_spin_button()

                self.ref_row = Adw.ActionRow()
                self.ref_row.set_title('Reference Frames')
                self.ref_row.set_subtitle('Number of previous frames each P-frame can reference')
                self.ref_row.add_suffix(self.ref_spin_button)
                self.ref_row.set_sensitive(False)

            def _setup_ref_spin_button(self):
                self.ref_spin_button = Gtk.SpinButton()
                self.ref_spin_button.set_range(x264.X264.REF_MIN, x264.X264.REF_MAX)
                self.ref_spin_button.set_digits(0)
                self.ref_spin_button.set_increments(1, 5)
                self.ref_spin_button.set_numeric(True)
                self.ref_spin_button.set_snap_to_ticks(True)
                self.ref_spin_button.set_value(3)
                self.ref_spin_button.set_vexpand(False)
                self.ref_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_deblock_row(self):
                self._setup_no_deblock_check_button()
                self._setup_deblock_alpha_spin_button()
                self._setup_deblock_beta_spin_button()

                self.deblock_values_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                self.deblock_values_vertical_box.append(self.deblock_alpha_horizontal_box)
                self.deblock_values_vertical_box.append(self.deblock_beta_horizontal_box)
                self.deblock_values_vertical_box.set_margin_top(10)
                self.deblock_values_vertical_box.set_margin_bottom(10)

                deblock_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                deblock_horizontal_box.append(self.no_deblock_check_button)
                deblock_horizontal_box.append(self.deblock_values_vertical_box)

                self.deblock_row = Adw.ActionRow()
                self.deblock_row.set_title('Deblocker')
                self.deblock_row.set_subtitle('Controls the state of the inloop deblocker')
                self.deblock_row.add_suffix(deblock_horizontal_box)
                self.deblock_row.set_sensitive(False)

            def _setup_no_deblock_check_button(self):
                self.no_deblock_check_button = Gtk.CheckButton(label='No Deblock')

            def _setup_deblock_alpha_spin_button(self):
                deblock_alpha_label = Gtk.Label(label='Alpha')

                deblock_alpha_spin_button = Gtk.SpinButton()
                deblock_alpha_spin_button.set_range(x264.X264.DEBLOCK_MIN, x264.X264.DEBLOCK_MAX)
                deblock_alpha_spin_button.set_digits(0)
                deblock_alpha_spin_button.set_increments(1, 5)
                deblock_alpha_spin_button.set_numeric(True)
                deblock_alpha_spin_button.set_snap_to_ticks(True)
                deblock_alpha_spin_button.set_value(0)
                deblock_alpha_spin_button.set_vexpand(False)
                deblock_alpha_spin_button.set_valign(Gtk.Align.CENTER)

                self.deblock_alpha_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.deblock_alpha_horizontal_box.append(deblock_alpha_label)
                self.deblock_alpha_horizontal_box.append(deblock_alpha_spin_button)
                self.deblock_alpha_horizontal_box.set_hexpand(False)
                self.deblock_alpha_horizontal_box.set_halign(Gtk.Align.END)

            def _setup_deblock_beta_spin_button(self):
                deblock_beta_label = Gtk.Label(label='Beta')

                deblock_beta_spin_button = Gtk.SpinButton()
                deblock_beta_spin_button.set_range(x264.X264.DEBLOCK_MIN, x264.X264.DEBLOCK_MAX)
                deblock_beta_spin_button.set_digits(0)
                deblock_beta_spin_button.set_increments(1, 5)
                deblock_beta_spin_button.set_numeric(True)
                deblock_beta_spin_button.set_snap_to_ticks(True)
                deblock_beta_spin_button.set_value(0)
                deblock_beta_spin_button.set_vexpand(False)
                deblock_beta_spin_button.set_valign(Gtk.Align.CENTER)

                self.deblock_beta_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.deblock_beta_horizontal_box.append(deblock_beta_label)
                self.deblock_beta_horizontal_box.append(deblock_beta_spin_button)
                self.deblock_beta_horizontal_box.set_hexpand(False)
                self.deblock_beta_horizontal_box.set_halign(Gtk.Align.END)

            def _setup_vbv_maxrate_row(self):
                self._setup_vbv_maxrate_spin_button()

                self.vbv_maxrate_row = Adw.ActionRow()
                self.vbv_maxrate_row.set_title('VBV Max Rate')
                self.vbv_maxrate_row.set_subtitle('VBV maximum bitrate in kbps')
                self.vbv_maxrate_row.add_suffix(self.vbv_maxrate_spin_button)
                self.vbv_maxrate_row.set_sensitive(False)

            def _setup_vbv_maxrate_spin_button(self):
                self.vbv_maxrate_spin_button = Gtk.SpinButton()
                self.vbv_maxrate_spin_button.set_range(x264.X264.BITRATE_MIN, x264.X264.BITRATE_MAX)
                self.vbv_maxrate_spin_button.set_digits(0)
                self.vbv_maxrate_spin_button.set_increments(100, 500)
                self.vbv_maxrate_spin_button.set_numeric(True)
                self.vbv_maxrate_spin_button.set_snap_to_ticks(True)
                self.vbv_maxrate_spin_button.set_value(2500)
                self.vbv_maxrate_spin_button.set_size_request(125, -1)
                self.vbv_maxrate_spin_button.set_vexpand(False)
                self.vbv_maxrate_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_vbv_bufsize_row(self):
                self._setup_vbv_bufsize_spin_button()

                self.vbv_bufsize_row = Adw.ActionRow()
                self.vbv_bufsize_row.set_title('VBV Buffer Size')
                self.vbv_bufsize_row.set_subtitle('VBV buffer size in kbps')
                self.vbv_bufsize_row.add_suffix(self.vbv_bufsize_spin_button)
                self.vbv_bufsize_row.set_sensitive(False)

            def _setup_vbv_bufsize_spin_button(self):
                self.vbv_bufsize_spin_button = Gtk.SpinButton()
                self.vbv_bufsize_spin_button.set_range(x264.X264.BITRATE_MIN, x264.X264.BITRATE_MAX)
                self.vbv_bufsize_spin_button.set_digits(0)
                self.vbv_bufsize_spin_button.set_increments(100, 500)
                self.vbv_bufsize_spin_button.set_numeric(True)
                self.vbv_bufsize_spin_button.set_snap_to_ticks(True)
                self.vbv_bufsize_spin_button.set_value(2500)
                self.vbv_bufsize_spin_button.set_size_request(125, -1)
                self.vbv_bufsize_spin_button.set_vexpand(False)
                self.vbv_bufsize_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_aq_mode_row(self):
                self._setup_aq_mode_combobox()

                self.aq_mode_row = Adw.ActionRow()
                self.aq_mode_row.set_title('AQ Mode')
                self.aq_mode_row.set_subtitle('Mode to distribute available bits across all macroblocks')
                self.aq_mode_row.add_suffix(self.aq_mode_combobox)
                self.aq_mode_row.set_sensitive(False)

            def _setup_aq_mode_combobox(self):
                self.aq_mode_combobox = Gtk.ComboBoxText()
                self.aq_mode_combobox.set_vexpand(False)
                self.aq_mode_combobox.set_valign(Gtk.Align.CENTER)

                for aq_mode_setting in x264.X264.AQ_MODE_UI:
                    self.aq_mode_combobox.append_text(aq_mode_setting)

                self.aq_mode_combobox.set_active(0)

            def _setup_aq_strength_row(self):
                self._setup_aq_strength_spin_button()

                self.aq_strength_row = Adw.ActionRow()
                self.aq_strength_row.set_title('AQ Strength')
                self.aq_strength_row.set_subtitle('Strength of AQ bias towards low detail macroblocks')
                self.aq_strength_row.add_suffix(self.aq_strength_spin_button)
                self.aq_strength_row.set_sensitive(False)

            def _setup_aq_strength_spin_button(self):
                self.aq_strength_spin_button = Gtk.SpinButton()
                self.aq_strength_spin_button.set_range(x264.X264.AQ_STRENGTH_MIN, x264.X264.AQ_STRENGTH_MAX)
                self.aq_strength_spin_button.set_digits(1)
                self.aq_strength_spin_button.set_increments(0.1, 0.5)
                self.aq_strength_spin_button.set_numeric(True)
                self.aq_strength_spin_button.set_snap_to_ticks(True)
                self.aq_strength_spin_button.set_value(1.0)
                self.aq_strength_spin_button.set_vexpand(False)
                self.aq_strength_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_partitions_row(self):
                self._setup_partitions_enabled_radio_buttons()
                self._setup_partitions_check_buttons()

                partitions_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                partitions_horizontal_box.append(self.partitions_enabled_horizontal_box)
                partitions_horizontal_box.append(self.partitions_options_vertical_box)
                partitions_horizontal_box.set_margin_top(10)
                partitions_horizontal_box.set_margin_bottom(10)

                self.partitions_row = Adw.ActionRow()
                self.partitions_row.set_title('Partitions')
                self.partitions_row.set_subtitle('Per-frametype macroblock partitions')
                self.partitions_row.add_suffix(partitions_horizontal_box)
                self.partitions_row.set_sensitive(False)

            def _setup_partitions_enabled_radio_buttons(self):
                auto_radio_button = Gtk.CheckButton(label='Auto')
                auto_radio_button.set_active(True)

                custom_radio_button = Gtk.CheckButton(label='Custom')
                custom_radio_button.set_group(auto_radio_button)

                self.partitions_enabled_horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                self.partitions_enabled_horizontal_box.append(auto_radio_button)
                self.partitions_enabled_horizontal_box.append(custom_radio_button)

            def _setup_partitions_check_buttons(self):
                i4x4_check_button = Gtk.CheckButton(label='i4x4')
                i4x4_check_button.set_hexpand(False)
                i4x4_check_button.set_halign(Gtk.Align.START)
                i8x8_check_button = Gtk.CheckButton(label='i8x8')
                i8x8_check_button.set_hexpand(False)
                i8x8_check_button.set_halign(Gtk.Align.START)
                p4x4_check_button = Gtk.CheckButton(label='p4x4')
                p4x4_check_button.set_hexpand(False)
                p4x4_check_button.set_halign(Gtk.Align.START)
                p8x8_check_button = Gtk.CheckButton(label='p8x8')
                p8x8_check_button.set_hexpand(False)
                p8x8_check_button.set_halign(Gtk.Align.START)
                b8x8_check_button = Gtk.CheckButton(label='b8x8')
                b8x8_check_button.set_hexpand(False)
                b8x8_check_button.set_halign(Gtk.Align.START)

                i_partitions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                i_partitions_box.append(i4x4_check_button)
                i_partitions_box.append(i8x8_check_button)

                p_partitions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                p_partitions_box.append(p4x4_check_button)
                p_partitions_box.append(p8x8_check_button)

                self.partitions_options_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                self.partitions_options_vertical_box.append(i_partitions_box)
                self.partitions_options_vertical_box.append(p_partitions_box)
                self.partitions_options_vertical_box.append(b8x8_check_button)

            def _setup_direct_row(self):
                self._setup_direct_combobox()

                self.direct_row = Adw.ActionRow()
                self.direct_row.set_title('Direct')
                self.direct_row.set_subtitle('Sets prediction mode for direct motion vectors')
                self.direct_row.add_suffix(self.direct_combobox)
                self.direct_row.set_sensitive(False)

            def _setup_direct_combobox(self):
                self.direct_combobox = Gtk.ComboBoxText()
                self.direct_combobox.set_vexpand(False)
                self.direct_combobox.set_valign(Gtk.Align.CENTER)

                for direct_setting in x264.X264.DIRECT_UI:
                    self.direct_combobox.append_text(direct_setting)

                self.direct_combobox.set_active(0)

            def _setup_weight_b_row(self):
                self._setup_weight_b_switch()

                self.weight_b_row = Adw.ActionRow()
                self.weight_b_row.set_title('Weight B')
                self.weight_b_row.set_subtitle('Allow non-symmetric weighting between references in B-frames')
                self.weight_b_row.add_suffix(self.weight_b_switch)
                self.weight_b_row.set_sensitive(False)

            def _setup_weight_b_switch(self):
                self.weight_b_switch = Gtk.Switch()
                self.weight_b_switch.set_vexpand(False)
                self.weight_b_switch.set_valign(Gtk.Align.CENTER)

            def _setup_me_row(self):
                self._setup_me_combobox()

                self.me_row = Adw.ActionRow()
                self.me_row.set_title('Motion Estimation')
                self.me_row.set_subtitle('Sets full-pixel motion estimation method')
                self.me_row.add_suffix(self.me_combobox)
                self.me_row.set_sensitive(False)

            def _setup_me_combobox(self):
                self.me_combobox = Gtk.ComboBoxText()
                self.me_combobox.set_vexpand(False)
                self.me_combobox.set_valign(Gtk.Align.CENTER)

                for me_setting in x264.X264.ME:
                    self.me_combobox.append_text(me_setting)

                self.me_combobox.set_active(0)

            def _setup_me_range_row(self):
                self._setup_me_range_spin_button()

                self.me_range_row = Adw.ActionRow()
                self.me_range_row.set_title('ME Range')
                self.me_range_row.set_subtitle('Controls the max range of the motion search')
                self.me_range_row.add_suffix(self.me_range_spin_button)
                self.me_range_row.set_sensitive(False)

            def _setup_me_range_spin_button(self):
                self.me_range_spin_button = Gtk.SpinButton()
                self.me_range_spin_button.set_range(x264.X264.ME_RANGE_MIN, x264.X264.ME_RANGE_MAX)
                self.me_range_spin_button.set_digits(0)
                self.me_range_spin_button.set_increments(4, 8)
                self.me_range_spin_button.set_numeric(True)
                self.me_range_spin_button.set_snap_to_ticks(True)
                self.me_range_spin_button.set_value(16)
                self.me_range_spin_button.set_vexpand(False)
                self.me_range_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_subme_row(self):
                self._setup_subme_combobox()

                self.subme_row = Adw.ActionRow()
                self.subme_row.set_title('SubME')
                self.subme_row.set_subtitle('Sets sub-pixel estimation complexity')
                self.subme_row.add_suffix(self.subme_combobox)
                self.subme_row.set_sensitive(False)

            def _setup_subme_combobox(self):
                self.subme_combobox = Gtk.ComboBoxText()
                self.subme_combobox.set_vexpand(False)
                self.subme_combobox.set_valign(Gtk.Align.CENTER)

                for subme_setting in x264.X264.SUB_ME_UI:
                    self.subme_combobox.append_text(subme_setting)

                self.subme_combobox.set_active(0)

            def _setup_psy_rd_row(self):
                self._setup_psyrd_spin_button()
                self._setup_psyrd_trellis_spin_button()

                psyrd_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                psyrd_vertical_box.append(self.psyrd_spin_button)
                psyrd_vertical_box.append(self.psyrd_trellis_spin_button)
                psyrd_vertical_box.set_margin_top(10)
                psyrd_vertical_box.set_margin_bottom(10)

                self.psyrd_row = Adw.ActionRow()
                self.psyrd_row.set_title('PsyRD')
                self.psyrd_row.set_subtitle('Psychovisual rate distortion strength')
                self.psyrd_row.add_suffix(psyrd_vertical_box)
                self.psyrd_row.set_sensitive(False)

            def _setup_psyrd_spin_button(self):
                self.psyrd_spin_button = Gtk.SpinButton()
                self.psyrd_spin_button.set_range(x264.X264.PSYRD_MIN, x264.X264.PSYRD_MAX)
                self.psyrd_spin_button.set_digits(1)
                self.psyrd_spin_button.set_increments(0.1, 0.5)
                self.psyrd_spin_button.set_numeric(True)
                self.psyrd_spin_button.set_snap_to_ticks(True)
                self.psyrd_spin_button.set_value(1.0)
                self.psyrd_spin_button.set_vexpand(False)
                self.psyrd_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_psyrd_trellis_spin_button(self):
                self.psyrd_trellis_spin_button = Gtk.SpinButton()
                self.psyrd_trellis_spin_button.set_range(x264.X264.PSYRD_TRELLIS_MIN, x264.X264.PSYRD_TRELLIS_MAX)
                self.psyrd_trellis_spin_button.set_digits(2)
                self.psyrd_trellis_spin_button.set_increments(0.05, 0.1)
                self.psyrd_trellis_spin_button.set_numeric(True)
                self.psyrd_trellis_spin_button.set_snap_to_ticks(True)
                self.psyrd_trellis_spin_button.set_value(0.0)
                self.psyrd_trellis_spin_button.set_vexpand(False)
                self.psyrd_trellis_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_mixed_refs_row(self):
                self._setup_mixed_refs_switch()

                self.mixed_refs_row = Adw.ActionRow()
                self.mixed_refs_row.set_title('Mixed Refs')
                self.mixed_refs_row.set_subtitle('Allows reference selection on a per-8x8 partition basis')
                self.mixed_refs_row.add_suffix(self.mixed_refs_switch)
                self.mixed_refs_row.set_sensitive(False)

            def _setup_mixed_refs_switch(self):
                self.mixed_refs_switch = Gtk.Switch()
                self.mixed_refs_switch.set_vexpand(False)
                self.mixed_refs_switch.set_valign(Gtk.Align.CENTER)

            def _setup_dct8x8_row(self):
                self._setup_dct8x8_switch()

                self.dct8x8_row = Adw.ActionRow()
                self.dct8x8_row.set_title('dct8x8')
                self.dct8x8_row.set_subtitle('Adaptive use of 8x8 transforms in I-frames')
                self.dct8x8_row.add_suffix(self.dct8x8_switch)
                self.dct8x8_row.set_sensitive(False)

            def _setup_dct8x8_switch(self):
                self.dct8x8_switch = Gtk.Switch()
                self.dct8x8_switch.set_vexpand(False)
                self.dct8x8_switch.set_valign(Gtk.Align.CENTER)

            def _setup_trellis_row(self):
                self._setup_trellis_combobox()

                self.trellis_row = Adw.ActionRow()
                self.trellis_row.set_title('Trellis')
                self.trellis_row.set_subtitle('Trellis quantization to increase efficiency')
                self.trellis_row.add_suffix(self.trellis_combobox)
                self.trellis_row.set_sensitive(False)

            def _setup_trellis_combobox(self):
                self.trellis_combobox = Gtk.ComboBoxText()
                self.trellis_combobox.set_vexpand(False)
                self.trellis_combobox.set_valign(Gtk.Align.CENTER)

                for trellis_setting in x264.X264.TRELLIS_UI:
                    self.trellis_combobox.append_text(trellis_setting)

                self.trellis_combobox.set_active(0)

            def _setup_no_fast_pskip_row(self):
                self._setup_no_fast_pskip_switch()

                self.no_fast_pskip_row = Adw.ActionRow()
                self.no_fast_pskip_row.set_title('No Fast PSkip')
                self.no_fast_pskip_row.set_subtitle('Disables early skip detection on P-frames')
                self.no_fast_pskip_row.add_suffix(self.no_fast_pskip_switch)
                self.no_fast_pskip_row.set_sensitive(False)

            def _setup_no_fast_pskip_switch(self):
                self.no_fast_pskip_switch = Gtk.Switch()
                self.no_fast_pskip_switch.set_vexpand(False)
                self.no_fast_pskip_switch.set_valign(Gtk.Align.CENTER)

            def _setup_no_dct_decimate_row(self):
                self._setup_no_dct_decimate_switch()

                self.no_dct_decimate_row = Adw.ActionRow()
                self.no_dct_decimate_row.set_title('No DCT Decimate')
                self.no_dct_decimate_row.set_subtitle('Disables coefficient thresholding on P-frames')
                self.no_dct_decimate_row.add_suffix(self.no_dct_decimate_switch)
                self.no_dct_decimate_row.set_sensitive(False)

            def _setup_no_dct_decimate_switch(self):
                self.no_dct_decimate_switch = Gtk.Switch()
                self.no_dct_decimate_switch.set_vexpand(False)
                self.no_dct_decimate_switch.set_valign(Gtk.Align.CENTER)

            def _setup_weight_p_row(self):
                self._setup_weight_p_switch()

                self.weight_p_row = Adw.ActionRow()
                self.weight_p_row.set_title('Weight P')
                self.weight_p_row.set_subtitle('Allow non-symmetric weighting between references in P-frames')
                self.weight_p_row.add_suffix(self.weight_p_switch)
                self.weight_p_row.set_sensitive(False)

            def _setup_weight_p_switch(self):
                self.weight_p_switch = Gtk.Switch()
                self.weight_p_switch.set_vexpand(False)
                self.weight_p_switch.set_valign(Gtk.Align.CENTER)

            def on_crf_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('crf_page')
                    self.rate_type_settings_row.set_title('CRF')
                    self.rate_type_settings_row.set_subtitle('Constant Ratefactor')

            def on_qp_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('qp_page')
                    self.rate_type_settings_row.set_title('QP')
                    self.rate_type_settings_row.set_subtitle('Constant quantizer: P-frames')

            def on_bitrate_check_button_toggled(self, check_button):
                if check_button.get_active():
                    self.rate_type_stack.set_visible_child_name('bitrate_page')
                    self.rate_type_settings_row.set_title('Bitrate')
                    self.rate_type_settings_row.set_subtitle('Target video bitrate in kbps')

            def _on_advanced_settings_switch_state_set(self, switch, user_data):
                is_state_enabled = switch.get_active()
                self._set_vbv_maxrate_row_enabled(is_state_enabled)
                self._set_vbv_bufsize_row_enabled(is_state_enabled)
                self.keyint_row.set_sensitive(is_state_enabled)
                self.min_keyint_row.set_sensitive(is_state_enabled)
                self.scenecut_row.set_sensitive(is_state_enabled)
                self.b_frames_row.set_sensitive(is_state_enabled)
                self.b_adapt_row.set_sensitive(is_state_enabled)
                self.b_pyramid_row.set_sensitive(is_state_enabled)
                self.weight_b_row.set_sensitive(is_state_enabled)
                self.weight_p_row.set_sensitive(is_state_enabled)
                self.no_fast_pskip_row.set_sensitive(is_state_enabled)
                self.ref_row.set_sensitive(is_state_enabled)
                self.mixed_refs_row.set_sensitive(is_state_enabled)
                self.no_cabac_row.set_sensitive(is_state_enabled)
                self._set_deblock_row_enabled(is_state_enabled)
                self.aq_mode_row.set_sensitive(is_state_enabled)
                self.aq_strength_row.set_sensitive(is_state_enabled)
                self.partitions_row.set_sensitive(is_state_enabled)
                self.dct8x8_row.set_sensitive(is_state_enabled)
                self.direct_row.set_sensitive(is_state_enabled)
                self.me_row.set_sensitive(is_state_enabled)
                self.me_range_row.set_sensitive(is_state_enabled)
                self.subme_row.set_sensitive(is_state_enabled)
                self.psyrd_row.set_sensitive(is_state_enabled)
                self.trellis_row.set_sensitive(is_state_enabled)
                self.no_dct_decimate_row.set_sensitive(is_state_enabled)

            def _set_vbv_maxrate_row_enabled(self, is_enabled: bool):
                if self.bitrate_check_button.get_active() \
                        and (self.average_check_button.get_active() or self.dual_pass_check_button.get_active()):
                    self.vbv_maxrate_row.set_sensitive(is_enabled)
                self.vbv_maxrate_row.set_sensitive(False)

            def _set_vbv_bufsize_row_enabled(self, is_enabled: bool):
                if self.bitrate_check_button.get_active() \
                        and (self.average_check_button.get_active() or self.dual_pass_check_button.get_active()):
                    self.vbv_bufsize_row.set_sensitive(is_enabled)
                self.vbv_bufsize_row.set_sensitive(False)

            def _set_deblock_row_enabled(self, is_enabled: bool):
                self.deblock_row.set_sensitive(is_enabled)
                self.deblock_values_vertical_box.set_sensitive(not self.no_deblock_check_button.get_active())



    class AudioCodecSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page

            self._setup_audio_stream_settings()

            audio_codec_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            audio_codec_settings_vertical_box.append(self.audio_stream_settings_group)
            audio_codec_settings_vertical_box.set_margin_top(20)
            audio_codec_settings_vertical_box.set_margin_bottom(20)
            audio_codec_settings_vertical_box.set_margin_start(20)
            audio_codec_settings_vertical_box.set_margin_end(20)

            self.set_child(audio_codec_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_audio_stream_settings(self):
            add_audio_stream_button_child = Adw.ButtonContent.new()
            add_audio_stream_button_child.set_label('Add Stream')
            add_audio_stream_button_child.set_icon_name('list-add-symbolic')

            add_audio_stream_button = Gtk.Button()
            add_audio_stream_button.set_child(add_audio_stream_button_child)
            add_audio_stream_button.connect('clicked', self.on_add_audio_stream_button_clicked)

            self.audio_stream_settings_group = SettingsSidebarWidgets.SettingsGroup()
            self.audio_stream_settings_group.set_title('Audio Streams')
            self.audio_stream_settings_group.set_header_suffix(add_audio_stream_button)

        def on_add_audio_stream_button_clicked(self, button):
            if self.audio_stream_settings_group.number_of_children < 4:
                encoding_task = self.inputs_page.inputs_list_box.get_selected_row().encoding_task
                audio_stream_row = self.AudioStreamRow(self,
                                                       encoding_task,
                                                       encoding_task.input_file.audio_streams[0],
                                                       self.audio_stream_settings_group.number_of_children + 1)
                self.audio_stream_settings_group.add(audio_stream_row)

        class AudioStreamRow(Adw.ExpanderRow):
            def __init__(self, audio_codec_settings_page, encoding_task: encoding.Task, audio_stream, row_count: int):
                super().__init__()

                self.audio_codec_settings_page = audio_codec_settings_page
                self.encoding_task = encoding_task
                self.audio_stream = audio_stream
                self.row_count = row_count
                self.audio_stream_codec = self.encoding_task.get_audio_stream_codec(self.audio_stream)

                self._setup_audio_stream_row()

            def _setup_audio_stream_row(self):
                self._setup_stream_row()
                self._setup_codec_row()
                self._setup_channels_setting_row()
                self._setup_bitrate_setting_row()
                self._setup_remove_button()

                self.update_title()
                self.update_subtitle()

                self.add_row(self.stream_row)
                self.add_row(self.audio_codec_row)
                self.add_row(self.channels_setting_row)
                self.add_row(self.bitrate_setting_row)
                self.add_prefix(self.remove_button)

                if self.audio_stream_codec is None:
                    self.set_codec_copy_state()

            def _setup_stream_row(self):
                self._setup_stream_combobox()

                self.stream_row = Adw.ActionRow()
                self.stream_row.set_title('Selected Stream')
                self.stream_row.set_subtitle('Audio stream to use')
                self.stream_row.add_suffix(self.stream_combobox)

            def _setup_stream_combobox(self):
                self.stream_combobox = Gtk.ComboBoxText()
                self.stream_combobox.set_vexpand(False)
                self.stream_combobox.set_valign(Gtk.Align.CENTER)

                for stream in self.encoding_task.input_file.audio_streams:
                    self.stream_combobox.append_text(stream.get_info())

                self.stream_combobox.set_active(0)

            def _setup_codec_row(self):
                self._setup_audio_codecs_combobox()

                self.audio_codec_row = Adw.ActionRow()
                self.audio_codec_row.set_title('Codec')
                self.audio_codec_row.set_subtitle('Audio codec to encode the audio stream')
                self.audio_codec_row.add_suffix(self.audio_codecs_combobox)

            def _setup_audio_codecs_combobox(self):
                self.audio_codecs_combobox = Gtk.ComboBoxText()
                self.audio_codecs_combobox.set_vexpand(False)
                self.audio_codecs_combobox.set_valign(Gtk.Align.CENTER)

                audio_codec_name = self.audio_stream_codec.codec_name

                if self.encoding_task.output_file.extension == '.mp4':
                    audio_codecs = self.encoding_task.AUDIO_CODECS_MP4_UI
                    audio_codec_index = self.encoding_task.AUDIO_CODECS_MP4_UI.index(audio_codec_name)
                elif self.encoding_task.output_file.extension == '.mkv':
                    audio_codecs = self.encoding_task.AUDIO_CODECS_MKV_UI
                    audio_codec_index = self.encoding_task.AUDIO_CODECS_MKV_UI.index(audio_codec_name)
                elif self.encoding_task.output_file.extension == '.ts':
                    audio_codecs = self.encoding_task.AUDIO_CODECS_TS_UI
                    audio_codec_index = self.encoding_task.AUDIO_CODECS_TS_UI.index(audio_codec_name)
                else:
                    audio_codecs = self.encoding_task.AUDIO_CODECS_WEBM_UI
                    audio_codec_index = self.encoding_task.AUDIO_CODECS_WEBM_UI.index(audio_codec_name)

                for audio_codec in audio_codecs:
                    self.audio_codecs_combobox.append_text(audio_codec)

                self.audio_codecs_combobox.set_active(audio_codec_index)
                self.audio_codecs_combobox.connect('changed', self.on_audio_codec_combobox_changed)

            def _setup_channels_setting_row(self):
                self._setup_channels_combobox()

                self.channels_setting_row = Adw.ActionRow()
                self.channels_setting_row.set_title('Channels')
                self.channels_setting_row.set_subtitle('Number of audio channels the codec should use')
                self.channels_setting_row.add_suffix(self.channels_combobox)

            def _setup_channels_combobox(self):
                self.channels_combobox = Gtk.ComboBoxText()

                for channel_setting in self.audio_stream_codec.CHANNELS_UI:
                    self.channels_combobox.append_text(channel_setting)

                self.channels_combobox.set_active(self.audio_stream_codec.channels)
                self.channels_combobox.set_vexpand(False)
                self.channels_combobox.set_valign(Gtk.Align.CENTER)
                self.channels_combobox.connect('changed', self.on_channels_combobox_changed)

            def _setup_bitrate_setting_row(self):
                self._setup_bitrate_spin_button()

                self.bitrate_setting_row = Adw.ActionRow()
                self.bitrate_setting_row.set_title('Bitrate')
                self.bitrate_setting_row.set_subtitle('Bitrate the codec should use in kbps')
                self.bitrate_setting_row.add_suffix(self.bitrate_spin_button)

            def _setup_bitrate_spin_button(self):
                self.bitrate_spin_button = Gtk.SpinButton()
                self.bitrate_spin_button.set_range(32, 996)
                self.bitrate_spin_button.set_digits(0)
                self.bitrate_spin_button.set_increments(32.0, 64.0)
                self.bitrate_spin_button.set_numeric(True)
                self.bitrate_spin_button.set_snap_to_ticks(True)

                if self.audio_stream_codec:
                    self.bitrate_spin_button.set_value(self.audio_stream_codec.bitrate)
                else:
                    self.bitrate_spin_button.set_value(128)

                self.bitrate_spin_button.set_vexpand(False)
                self.bitrate_spin_button.set_valign(Gtk.Align.CENTER)

            def _setup_remove_button(self):
                self.remove_button = Gtk.Button.new_from_icon_name('list-remove-symbolic')
                self.remove_button.set_vexpand(False)
                self.remove_button.set_valign(Gtk.Align.CENTER)
                self.remove_button.connect('clicked', self.on_remove_button_clicked)

            def update_title(self):
                self.set_title(''.join(['Audio Stream ', str(self.row_count)]))

            def update_subtitle(self):
                codec_name = self.audio_codecs_combobox.get_active_text()

                if self.channels_combobox.get_active() < 1 or self.audio_codecs_combobox.get_active() < 1:
                    channels = ' '.join([str(self.audio_stream.channels), 'channels'])
                else:
                    channels = ' '.join([self.channels_combobox.get_active_text(), 'channels'])

                self.set_subtitle(','.join([codec_name, channels]))

            def set_codec_copy_state(self):
                self.channels_setting_row.set_sensitive(False)
                self.bitrate_setting_row.set_sensitive(False)

            def on_remove_button_clicked(self, button):
                self.audio_codec_settings_page.audio_stream_settings_group.remove(self)

            def on_channels_combobox_changed(self, combobox):
                self.update_subtitle()

            def on_audio_codec_combobox_changed(self, combobox):
                is_codec_settings_editable = bool(combobox.get_active())
                self.channels_setting_row.set_sensitive(is_codec_settings_editable)
                self.bitrate_setting_row.set_sensitive(is_codec_settings_editable)

                self.update_subtitle()

    class FilterSettingsPage(Gtk.ScrolledWindow):
        def __init__(self):
            super().__init__()

            self._setup_deinterlace_settings()

            filter_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            filter_settings_vertical_box.append(self.deinterlace_settings_group)
            filter_settings_vertical_box.set_margin_top(20)
            filter_settings_vertical_box.set_margin_bottom(20)
            filter_settings_vertical_box.set_margin_start(20)
            filter_settings_vertical_box.set_margin_end(20)

            self.set_child(filter_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_deinterlace_settings(self):
            self._setup_deinterlace_method_setting()

            deinterlace_enabled_switch = Gtk.Switch()
            deinterlace_enabled_switch.set_vexpand(False)
            deinterlace_enabled_switch.set_valign(Gtk.Align.CENTER)

            self.deinterlace_settings_group = Adw.PreferencesGroup()
            self.deinterlace_settings_group.set_title('Deinterlace')
            self.deinterlace_settings_group.set_header_suffix(deinterlace_enabled_switch)
            self.deinterlace_settings_group.add(self.deinterlace_method_row)

        def _setup_deinterlace_method_setting(self):
            deinterlace_method_combobox = Gtk.ComboBoxText()
            deinterlace_method_combobox.set_vexpand(False)
            deinterlace_method_combobox.set_valign(Gtk.Align.CENTER)

            for deinterlace_method in filters.Deinterlace.DEINT_FILTERS:
                deinterlace_method_combobox.append_text(deinterlace_method)

            deinterlace_method_combobox.set_active(0)

            self.deinterlace_method_row = Adw.ActionRow()
            self.deinterlace_method_row.set_title('Method')
            self.deinterlace_method_row.set_subtitle('Deinterlacing method')
            self.deinterlace_method_row.add_suffix(deinterlace_method_combobox)
            self.deinterlace_method_row.set_sensitive(False)

    class SubtitleSettingsPage(Gtk.ScrolledWindow):
        def __init__(self, inputs_page):
            super().__init__()

            self.inputs_page = inputs_page

            self._setup_subtitle_settings()

            subtitle_settings_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
            subtitle_settings_vertical_box.append(self.subtitle_stream_settings_group)
            subtitle_settings_vertical_box.set_margin_top(20)
            subtitle_settings_vertical_box.set_margin_bottom(20)
            subtitle_settings_vertical_box.set_margin_start(20)
            subtitle_settings_vertical_box.set_margin_end(20)

            self.set_child(subtitle_settings_vertical_box)
            self.set_vexpand(True)

        def _setup_subtitle_settings(self):
            add_subtitle_stream_button_child = Adw.ButtonContent.new()
            add_subtitle_stream_button_child.set_label('Add Stream')
            add_subtitle_stream_button_child.set_icon_name('list-add-symbolic')

            add_subtitle_stream_button = Gtk.Button()
            add_subtitle_stream_button.set_child(add_subtitle_stream_button_child)
            add_subtitle_stream_button.connect('clicked', self.on_add_subtitle_stream_button_clicked)

            self.subtitle_stream_settings_group = SettingsSidebarWidgets.SettingsGroup()
            self.subtitle_stream_settings_group.set_title('Subtitle Streams')
            self.subtitle_stream_settings_group.set_header_suffix(add_subtitle_stream_button)

        def on_add_subtitle_stream_button_clicked(self, button):
            encoding_task = self.inputs_page.inputs_list_box.get_selected_row().encoding_task

            if encoding_task.filter.subtitles.streams_available:
                subtitle_stream = encoding_task.filter.subtitles.streams_available[0]
                encoding_task.filter.subtitles.use_stream(subtitle_stream)

                subtitle_stream_row = self.SubtitleStreamRow(self,
                                                             encoding_task,
                                                             subtitle_stream,
                                                             self.subtitle_stream_settings_group.number_of_children + 1)
                self.subtitle_stream_settings_group.add(subtitle_stream_row)

        class SubtitleStreamRow(Adw.ExpanderRow):
            def __init__(self, subtitle_settings_page, encoding_task: encoding.Task, subtitle_stream, row_count: int):
                super().__init__()

                self.subtitle_settings_page = subtitle_settings_page
                self.encoding_task = encoding_task
                self.subtitle_stream = subtitle_stream
                self.row_count = row_count

                self._setup_subtitle_stream_row()

            def _setup_subtitle_stream_row(self):
                self._setup_stream_row()
                self._setup_method_row()
                self._setup_remove_button()

                self.set_title(''.join(['Subtitle Stream ', str(self.row_count)]))
                self.set_subtitle(self.subtitle_stream.get_info())
                self.add_row(self.stream_row)
                self.add_row(self.method_row)
                self.add_prefix(self.remove_button)

            def _setup_stream_row(self):
                self._setup_stream_combobox()

                self.stream_row = Adw.ActionRow()
                self.stream_row.set_title('Selected Stream')
                self.stream_row.add_suffix(self.stream_combobox)

            def _setup_stream_combobox(self):
                self.stream_combobox = Gtk.ComboBoxText()
                self.stream_combobox.set_vexpand(False)
                self.stream_combobox.set_valign(Gtk.Align.CENTER)
                self.stream_combobox.append_text(self.subtitle_stream.get_info())

                for stream in self.encoding_task.filter.subtitles.streams_available:
                    self.stream_combobox.append_text(stream.get_info())

                self.stream_combobox.set_active(0)

            def _setup_method_row(self):
                self._setup_method_combobox()

                self.method_row = Adw.ActionRow()
                self.method_row.set_title('Method')
                self.method_row.set_subtitle('Method to apply to the subtitle stream')
                self.method_row.add_suffix(self.method_combobox)

            def _setup_method_combobox(self):
                self.method_combobox = Gtk.ComboBoxText()
                self.method_combobox.append_text('Copy')
                self.method_combobox.append_text('Burn-In')
                self.method_combobox.set_active(0)
                self.method_combobox.set_vexpand(False)
                self.method_combobox.set_valign(Gtk.Align.CENTER)

            def _setup_remove_button(self):
                self.remove_button = Gtk.Button.new_from_icon_name('list-remove-symbolic')
                self.remove_button.set_vexpand(False)
                self.remove_button.set_valign(Gtk.Align.CENTER)
                self.remove_button.connect('clicked', self.on_remove_button_clicked)

            def update_title(self):
                self.set_title(''.join(['Subtitle Stream ', str(self.row_count)]))

            def on_remove_button_clicked(self, button):
                self.subtitle_settings_page.subtitle_stream_settings_group.remove(self)
