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


from render_watch.ui import Gio, Adw
from render_watch.ui import main_window
from render_watch.encode import encoder_queue, preview
from render_watch import app_preferences


class RenderWatch(Adw.Application):
    def __init__(self, app_settings: app_preferences.Settings):
        super().__init__(application_id=app_preferences.APP_NAME, flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.app_settings = app_settings
        # self.task_queue = encoder_queue.TaskQueue(self.app_settings)
        self.preview_generator = preview.PreviewGenerator(self.app_settings)

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        main_window_widgets = main_window.MainWindowWidgets(self, None, self.preview_generator, self.app_settings)
        main_window_widgets.main_window.present()

    def do_shutdown(self):
        self.preview_generator.kill()
        self.app_settings.save()
        app_preferences.clear_temp_directory(self.app_settings)

        Adw.Application.do_shutdown(self)
