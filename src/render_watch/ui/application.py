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
from render_watch.encode import encoder_queue, preview, benchmark
from render_watch import app_preferences


class RenderWatch(Adw.Application):
    """Class that is the Adwaita application for Render Watch"""

    def __init__(self,
                 app_settings: app_preferences.Settings,
                 task_queue: encoder_queue.TaskQueue,
                 preview_generator: preview.PreviewGenerator,
                 benchmark_generator: benchmark.BenchmarkGenerator):
        """
        Initializes the RenderWatch class with the necessary variables for starting the UI.

        Parameters:
            app_settings: Application settings.
            task_queue: Encoding task queue.
            preview_generator: Generates previews for encoding tasks.
            benchmark_generator: Generates a benchmark for encoding tasks.
        """
        super().__init__(application_id=app_preferences.APP_NAME, flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.app_settings = app_settings
        self.task_queue = task_queue
        self.preview_generator = preview_generator
        self.benchmark_generator = benchmark_generator

    def do_startup(self):
        """
        Performs the startup for the application. This runs before the Adw.ApplicationWindow is instantiated and shown.

        Returns:
             None
        """
        Adw.Application.do_startup(self)

        self.get_style_manager().set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def do_activate(self):
        """
        Instantiates the Adw.ApplicationWindow and shows it.

        Returns:
            None
        """
        main_window_widgets = main_window.MainWindowWidgets(self,
                                                            self.task_queue,
                                                            self.preview_generator,
                                                            self.app_settings)
        main_window_widgets.main_window.present()

    def do_shutdown(self):
        """
        Performs the shutdown process for the application. This stops all queues and generators, saves the
        application's settings, and then stops the UI loop.

        Returns:
            None
        """
        self._kill_queues_and_generators()
        self._save_application_settings()

        Adw.Application.do_shutdown(self)

    def _kill_queues_and_generators(self):
        # Stops all queues and generators.
        self.task_queue.kill()
        self.preview_generator.kill()
        self.benchmark_generator.kill()

    def _save_application_settings(self):
        # Saves the application's settings and clears the temp directory.
        self.app_settings.save()
        app_preferences.clear_temp_directory(self.app_settings)
