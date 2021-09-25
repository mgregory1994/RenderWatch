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

import logging

from render_watch.app_handlers.main_window_handlers import MainWindowHandlers
from render_watch.app_handlers.prefs_handlers import PrefsHandlers


class HandlersManager(object):
    """Supplies all signals from the handlers for Gtk.Builder.get_signals()"""

    def __init__(self, gtk_builder, gtk_settings, encoder_queue, preferences):
        main_window_handlers = MainWindowHandlers(gtk_builder, encoder_queue, preferences)
        prefs_handlers = PrefsHandlers(gtk_builder, gtk_settings, main_window_handlers, preferences)
        self.__handlers_list = (main_window_handlers, prefs_handlers)

    def __getattr__(self, signal_name):  # Needed for builder.connect_signals() in handlers_manager.py
        """Returns the list of signals this class uses.

                Used for Gtk.Builder.get_signals().

                :param signal_name:
                    The signal function name being looked for.
                """
        for handler in self.__handlers_list:
            if hasattr(handler, signal_name):
                return getattr(handler, signal_name)
        logging.critical('--- FAILED TO GET NEEDED SIGNAL FROM HANDLERS CLASSES ---')
        raise AttributeError('%r not found on any of %r' % (signal_name, self.__handlers_list))
