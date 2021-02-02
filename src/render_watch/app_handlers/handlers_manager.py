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

import logging

from render_watch.app_handlers.main_window_handlers import MainWindowHandlers
from render_watch.app_handlers.inputs_page_handlers import InputsPageHandlers
from render_watch.app_handlers.preview_page_handlers import PreviewPageHandlers
from render_watch.app_handlers.crop_page_handlers import CropPageHandlers
from render_watch.app_handlers.trim_page_handlers import TrimPageHandlers
from render_watch.app_handlers.active_page_handlers import ActivePageHandlers
from render_watch.app_handlers.completed_page_handlers import CompletedPageHandlers
from render_watch.app_handlers.settings_sidebar_handlers import SettingsSidebarHandlers
from render_watch.app_handlers.prefs_handlers import PrefsHandlers


class HandlersManager(object):
    def __init__(self, gtk_builder, gtk_settings, encoder, preferences):
        main_window_handlers = MainWindowHandlers(gtk_builder, encoder, preferences)
        inputs_page_handlers = InputsPageHandlers(gtk_builder)
        preview_page_handlers = PreviewPageHandlers(gtk_builder, preferences)
        crop_page_handlers = CropPageHandlers(gtk_builder, preferences)
        trim_page_handlers = TrimPageHandlers(gtk_builder, preferences)
        active_page_handlers = ActivePageHandlers(gtk_builder, preferences)
        completed_page_handlers = CompletedPageHandlers(gtk_builder)
        settings_sidebar_handlers = SettingsSidebarHandlers(gtk_builder, preferences)
        prefs_handlers = PrefsHandlers(gtk_builder, gtk_settings, preferences)
        self.__handlers_list = (main_window_handlers, inputs_page_handlers, crop_page_handlers, trim_page_handlers,
                                preview_page_handlers, active_page_handlers, completed_page_handlers, prefs_handlers,
                                settings_sidebar_handlers)
        # settings_sidebar_handlers must come last in this list: Gtk.connect_signals() bug

        main_window_handlers.inputs_page_handlers = inputs_page_handlers
        main_window_handlers.active_page_handlers = active_page_handlers
        main_window_handlers.completed_page_handlers = completed_page_handlers
        main_window_handlers.settings_sidebar_handlers = settings_sidebar_handlers
        inputs_page_handlers.settings_sidebar_handlers = settings_sidebar_handlers
        inputs_page_handlers.main_window_handlers = main_window_handlers
        inputs_page_handlers.active_page_handlers = active_page_handlers
        inputs_page_handlers.crop_page_handlers = crop_page_handlers
        inputs_page_handlers.preview_page_handlers = preview_page_handlers
        inputs_page_handlers.trim_page_handlers = trim_page_handlers
        preview_page_handlers.inputs_page_handlers = inputs_page_handlers
        crop_page_handlers.main_window_handlers = main_window_handlers
        crop_page_handlers.inputs_page_handlers = inputs_page_handlers
        trim_page_handlers.inputs_page_handlers = inputs_page_handlers
        active_page_handlers.main_window_handlers = main_window_handlers
        active_page_handlers.completed_page_handlers = completed_page_handlers
        completed_page_handlers.main_window_handlers = main_window_handlers
        settings_sidebar_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.crop_page_handlers = crop_page_handlers
        settings_sidebar_handlers.trim_page_handlers = trim_page_handlers
        settings_sidebar_handlers.preview_page_handlers = preview_page_handlers
        settings_sidebar_handlers.x264_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.x265_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.nvenc_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.vp9_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.aac_handlers.inputs_page_handlers = inputs_page_handlers
        settings_sidebar_handlers.opus_handlers.inputs_page_handlers = inputs_page_handlers
        prefs_handlers.main_window_handlers = main_window_handlers

    def __getattr__(self, signal_name):
        for handler in self.__handlers_list:
            if hasattr(handler, signal_name):
                return getattr(handler, signal_name)
        else:
            logging.critical('--- FAILED TO GET NEEDED SIGNAL FROM HANDLERS CLASSES ---')
            raise AttributeError('%r not found on any of %r' % (signal_name, self.__handlers_list))
