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


import os
import queue
import signal
import subprocess
import threading
import re

from render_watch.ui import Gtk, GLib, Gdk
from render_watch.ffmpeg import task, video_codec
from render_watch.helpers import ffmpeg_helper, format_converter
from render_watch import app_preferences, logger


class PreviewGenerator:
    """Class that queues tasks and generates previews for them."""

    def __init__(self, app_settings: app_preferences.Settings):
        """
        Initializes the PreviewGenerator class with the necessary variables for queueing encoding tasks and
        sending them to the preview queues.

        Parameters:
            app_settings: Application settings.
        """
        self._new_tasks_queue = queue.Queue()
        self._crop_preview = _CropPreview(self, app_settings)
        self._trim_preview = _TrimPreview(self, app_settings)
        self._settings_preview = _SettingsPreview(self, app_settings)
        self._video_preview = _VideoPreview(self, app_settings)
        self.main_window = None

    def generate_crop_preview(self, crop_preview_task: task.CropPreview):
        """
        Adds the given encoding task to the crop preview queue and creates the preview at the given time position.

        Parameters:
            crop_preview_task: Crop preview task to send to the crop preview queue.

        Returns:
            None
        """
        self._crop_preview.add_crop_task(crop_preview_task)

    def generate_trim_preview(self, trim_preview_task: task.TrimPreview):
        """
        Adds the given encoding task to the trim preview queue and creates the preview at the given time position.

        Parameters:
            trim_preview_task: Trim preview task to send to the trim preview queue.

        Returns:
            None
        """
        self._trim_preview.add_trim_preview_task(trim_preview_task)

    def generate_settings_preview(self, settings_preview_task: task.SettingsPreview):
        """
        Adds the given encoding task to the settings preview queue and creates the preview at the given time position.

        Parameters:
            settings_preview_task: Settings preview task to send to the settings preview queue.

        Returns:
            None
        """
        self._settings_preview.add_settings_task(settings_preview_task)

    def generate_video_preview(self, video_preview_task: task.VideoPreview):
        """
        Adds the given encoding task to the video preview queue and creates the preview at the given time position.

        Parameters:
            video_preview_task: Video preview task to send to the settings preview queue.

        Returns:
            None
        """
        self._video_preview.add_video_task(video_preview_task)

    def open_preview_file(self, file_path: str):
        file_uri = ''.join(['file://', file_path])
        Gtk.show_uri(self.main_window, file_uri, Gdk.CURRENT_TIME)

    def kill(self):
        """
        Empties all preview queues and then adds a stop task to each preview queue.

        Returns:
            None
        """
        self._empty_queues()
        self._stop_queues()

    def _empty_queues(self):
        # Empties all preview queues.
        self._crop_preview.empty_queue()
        self._trim_preview.empty_queue()
        self._settings_preview.empty_queue()
        self._video_preview.empty_queue()

    def _stop_queues(self):
        # Adds a stop task to all preview queues.
        self._crop_preview.add_stop_task()
        self._trim_preview.add_stop_task()
        self._settings_preview.add_stop_task()
        self._video_preview.add_stop_task()

    @staticmethod
    def run_preview_subprocess(preview_task: task.TrimPreview | task.CropPreview | task.SettingsPreview | task.VideoPreview,
                               subprocess_args_list: list):
        """
        Runs a subprocess for each args list contained in subprocess_args_list.

        Parameters:
            preview_task: Preview task that's being used to make a preview.
            subprocess_args_list: List that contains lists of subprocess args.

        Returns:
            Subprocess' return code as an integer.
        """
        for encode_pass, args_list in enumerate(subprocess_args_list):
            with subprocess.Popen(args_list,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as preview_process:
                if isinstance(preview_task, task.VideoPreview):
                    PreviewGenerator.process_video_preview_subprocess(preview_process, preview_task, encode_pass)

                process_return_code = preview_process.wait()

            if process_return_code:
                logger.log_preview_subprocess_failed(preview_task.encode_task.temp_file.file_path, subprocess_args_list)

                break

        return process_return_code

    @staticmethod
    def process_video_preview_subprocess(video_preview_process: subprocess.Popen,
                                         video_preview_task: task.VideoPreview,
                                         encode_pass: int):
        stdout_last_line = ''

        while True:
            if video_preview_task.is_preview_stopped and video_preview_process.poll() is None:
                os.kill(video_preview_process.pid, signal.SIGKILL)

                break

            stdout = video_preview_process.stdout.readline().strip()
            if stdout == '' and video_preview_process.poll() is not None:
                break

            stdout_last_line = stdout

            PreviewGenerator._update_video_preview_current_position(video_preview_task, stdout)
            PreviewGenerator._update_video_preview_progress(video_preview_task, encode_pass)

        PreviewGenerator._log_video_preview_process_state(video_preview_process, video_preview_task, stdout_last_line)

    @staticmethod
    def _update_video_preview_current_position(video_preview_task: task.VideoPreview, stdout: str):
        try:
            current_position_timecode = re.search(r'time=\d+:\d+:\d+\.\d+|time=\s+\d+:\d+:\d+\.\d+',
                                                  stdout).group().split('=')[1]
            current_position_in_seconds = format_converter.get_seconds_from_timecode(current_position_timecode)
            video_preview_task.current_time_position = current_position_in_seconds
        except (AttributeError, TypeError):
            pass

    @staticmethod
    def _update_video_preview_progress(video_preview_task: task.VideoPreview, encode_pass: int):
        try:
            if video_codec.is_codec_2_pass(video_preview_task.encode_task):
                encode_passes = 2
            else:
                encode_passes = 1

            if encode_pass == 0:
                progress = (video_preview_task.current_time_position / video_preview_task.preview_duration) / encode_passes
            else:
                progress = 0.5 + ((video_preview_task.current_time_position / video_preview_task.preview_duration) / encode_passes)

            video_preview_task.progress = round(progress, 4)
        except (AttributeError, TypeError, ZeroDivisionError):
            pass

    @staticmethod
    def _log_video_preview_process_state(video_preview_process: subprocess.Popen,
                                         video_preview_task: task.VideoPreview,
                                         stdout_last_line: str):
        if video_preview_task.is_preview_stopped:
            logger.log_video_preview_process_stopped(video_preview_task.encode_task.output_file.file_path)
        elif video_preview_process.wait():
            logger.log_video_preview_process_failed(video_preview_task.encode_task.output_file.file_path,
                                                    stdout_last_line)


class _CropPreview:
    """Class that queues crop preview tasks and generates a preview file for them."""

    def __init__(self, preview_generator: PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the _CropPreview class with all necessary variables for queuing crop preview tasks and
        generating a preview file for them.

        Parameters:
            preview_generator: Preview generator that initialized this class.
            app_settings: Application settings.
        """
        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self._crop_tasks_queue = queue.Queue()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Loop that creates a preview file for each queued crop preview task.
        try:
            while True:
                crop_preview_task = self._crop_tasks_queue.get()

                if not crop_preview_task:
                    logger.log_stopping_crop_preview_queue_loop()

                    break

                try:
                    self._process_crop_preview_task(crop_preview_task)
                except:
                    logger.log_crop_preview_task_failed(crop_preview_task.encode_task.input_file.file_path)
                finally:
                    crop_preview_task.preview_threading_event.set()
        except:
            logger.log_crop_preview_queue_loop_failed()

    def _process_crop_preview_task(self, crop_preview_task: task.CropPreview):
        # Creates a preview file for the crop preview task.
        crop_preview_args = _get_preview_subprocess_args(crop_preview_task)

        if self.preview_generator.run_preview_subprocess(crop_preview_task, [crop_preview_args]):
            raise Exception
        else:
            crop_preview_task.apply_trim_preview_file_path()

    def add_crop_task(self, crop_preview_task: task.CropPreview):
        """
        Adds the given encoding task to the crop preview queue.

        Parameters:
            crop_preview_task: Crop preview task to add to the crop tasks queue.

        Returns:
            None
        """
        self._crop_tasks_queue.put(crop_preview_task)

    def add_stop_task(self):
        """
        Adds a False boolean to the crop preview queue to stop the queue loop.

        Returns:
            None
        """
        self._crop_tasks_queue.put(False)

    def empty_queue(self):
        """
        Empties the crop preview queue.

        Returns:
            None
        """
        while not self._crop_tasks_queue.empty():
            self._crop_tasks_queue.get()


class _TrimPreview:
    """Class that queues temp preview tasks and generates a preview file for them."""

    def __init__(self, preview_generator: PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the _TrimPreview class with all necessary variables for queueing trim preview tasks and
        generating a preview file for them.

        Parameters:
            preview_generator: Preview generator that initialized this class.
            app_settings: Application settings.
        """
        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self._trim_tasks_queue = queue.Queue()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Loop that creates a preview file for each queued trim preview task.
        try:
            while True:
                trim_preview_task = self._trim_tasks_queue.get()

                if not trim_preview_task:
                    logger.log_stopping_trim_preview_queue_loop()

                    break

                try:
                    self._process_trim_preview_task(trim_preview_task)
                except:
                    logger.log_trim_preview_task_failed(trim_preview_task.encode_task.input_file.file_path)
                finally:
                    trim_preview_task.preview_threading_event.set()
        except:
            logger.log_trim_preview_queue_loop_failed()

    def _process_trim_preview_task(self, trim_preview_task: task.TrimPreview):
        # Creates a preview file for the trim preview task.
        trim_preview_args = _get_preview_subprocess_args(trim_preview_task)

        if self.preview_generator.run_preview_subprocess(trim_preview_task, [trim_preview_args]):
            raise Exception
        else:
            trim_preview_task.apply_trim_preview_file_path()

    def add_trim_preview_task(self, trim_preview_task: task.TrimPreview):
        """
        Adds the given encoding task to the trim preview queue.

        Parameters:
            trim_preview_task: Encoding task to add to the trim tasks queue.

        Returns:
            None
        """
        self._trim_tasks_queue.put(trim_preview_task)

    def add_stop_task(self):
        """
        Adds a False boolean to the trim preview queue to stop the queue loop.

        Returns:
            None
        """
        self._trim_tasks_queue.put(False)

    def empty_queue(self):
        """
        Empties the trim preview queue.

        Returns:
            None
        """
        while not self._trim_tasks_queue.empty():
            self._trim_tasks_queue.get()


class _SettingsPreview:
    """Class that queues settings preview tasks and generates a preview file for them."""

    ENCODE_DURATION = 1

    def __init__(self, preview_generator: PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the _SettingsPreview class with all necessary variables for queueing settings preview tasks and
        generating a preview file for them.

        Parameters:
            preview_generator: Preview generator that initialized this class.
            app_settings: Application settings.
        """
        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self._settings_tasks_queue = queue.Queue()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Loop that creates a preview file for each queued settings preview task.
        try:
            while True:
                settings_preview_task = self._settings_tasks_queue.get()

                if not settings_preview_task:
                    logger.log_stopping_settings_preview_queue_loop()

                    break

                try:
                    self._process_settings_preview_task(settings_preview_task)
                except:
                    logger.log_settings_preview_task_failed(settings_preview_task.encode_task.input_file.file_path)
                finally:
                    settings_preview_task.preview_threading_event.set()
        except:
            logger.log_settings_preview_queue_loop_failed()

    def _process_settings_preview_task(self, settings_preview_task: task.SettingsPreview):
        # Creates a preview file for the settings preview task.
        settings_preview_args_list = self._get_preview_subprocess_args(settings_preview_task)

        if self.preview_generator.run_preview_subprocess(settings_preview_task, settings_preview_args_list):
            raise Exception
        else:
            settings_preview_task.apply_settings_preview_file_path()

    def _get_preview_subprocess_args(self, settings_preview_task: task.SettingsPreview) -> list:
        # Returns a list that contains lists of subprocess args for the settings preview task.
        settings_preview_args = ffmpeg_helper.Args.get_args(settings_preview_task.encode_task)
        settings_preview_args.append(self._get_single_image_preview_subprocess_args(settings_preview_task))

        return settings_preview_args

    @staticmethod
    def _get_single_image_preview_subprocess_args(settings_preview_task: task.SettingsPreview) -> list:
        # Returns a list that contains the subprocess args for generating a single image of the settings preview file.
        single_image_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        single_image_args.append('-i')
        single_image_args.append(settings_preview_task.encode_task.temp_file.file_path)
        settings_preview_task.encode_task.temp_file.extension = '.png'
        single_image_args.append('-f')
        single_image_args.append('image2')
        single_image_args.append('-an')
        single_image_args.append('-update')
        single_image_args.append('1')
        single_image_args.append(settings_preview_task.encode_task.temp_file.file_path)

        return single_image_args

    def add_settings_task(self, settings_preview_task: task.SettingsPreview):
        """
        Adds the given encoding task to the settings preview queue.

        Parameters:
            settings_preview_task: Settings preview task to add to the settings tasks queue.

        Returns:
            None
        """
        self._settings_tasks_queue.put(settings_preview_task)

    def add_stop_task(self):
        """
        Adds a False boolean to the settings preview queue to stop the queue loop.

        Returns:
            None
        """
        self._settings_tasks_queue.put(False)

    def empty_queue(self):
        """
        Empties the settings preview queue.

        Returns:
            None
        """
        while not self._settings_tasks_queue.empty():
            self._settings_tasks_queue.get()


class _VideoPreview:
    """Class that queues video preview tasks and generates a preview file for them."""

    def __init__(self, preview_generator: PreviewGenerator, app_settings: app_preferences.Settings):
        """
        Initializes the _VideoPreview class with all necessary variables for queueing video preview tasks and
        generating a preview file for them.

        Parameters:
            preview_generator: Preview generator that initialized this class.
            app_settings: Application settings.
        """
        self.preview_generator = preview_generator
        self.app_settings = app_settings
        self._video_preview_queue = queue.Queue()

        threading.Thread(target=self._run_queue_loop_instance, args=()).start()

    def _run_queue_loop_instance(self):
        # Loop that creates a preview file for each queued video preview task.
        try:
            while True:
                video_preview_task = self._video_preview_queue.get()

                if not video_preview_task:
                    logger.log_stopping_video_preview_queue_loop()

                    break

                try:
                    self._process_video_preview_task(video_preview_task)
                    self.preview_generator.open_preview_file(video_preview_task.preview_file_path)
                except:
                    logger.log_video_preview_task_failed(video_preview_task.encode_task.input_file.file_path)
                finally:
                    video_preview_task.preview_threading_event.set()
        except:
            logger.log_video_preview_queue_loop_failed()

    def _process_video_preview_task(self, video_preview_task: task.VideoPreview):
        # Creates a preview file for the video preview task.
        video_preview_args = ffmpeg_helper.Args.get_args(video_preview_task.encode_task)

        if self.preview_generator.run_preview_subprocess(video_preview_task, video_preview_args):
            raise Exception
        else:
            video_preview_task.apply_video_preview_file_path()

    def add_video_task(self, video_preview_task: task.VideoPreview):
        """
        Adds the given encoding task to the video preview queue.

        Parameters:
            video_preview_task: Video preview task to add to the video tasks queue.

        Returns:
            None
        """
        self._video_preview_queue.put(video_preview_task)

    def add_stop_task(self):
        """
        Adds a False boolean to the video preview queue to stop the queue loop.

        Returns:
            None
        """
        self._video_preview_queue.put(False)

    def empty_queue(self):
        """
        Empties the video preview queue.

        Returns:
            None
        """
        while not self._video_preview_queue.empty():
            self._video_preview_queue.get()


def _get_preview_subprocess_args(preview_task: task.TrimPreview | task.CropPreview) -> list[str]:
    # Returns a list of subprocess args for generating a single image with crop for the preview task.
    subprocess_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
    subprocess_args.append('-ss')
    subprocess_args.append(str(preview_task.time_position))
    subprocess_args.append('-i')
    subprocess_args.append(preview_task.encode_task.input_file.file_path)
    subprocess_args.append('-vframes')
    subprocess_args.append('1')

    if preview_task.encode_task.filters.ffmpeg_args['-filter_complex'] is not None:
        subprocess_args.append('-filter_complex')
        subprocess_args.append(preview_task.encode_task.filters.ffmpeg_args['-filter_complex'])

    subprocess_args.append('-an')
    subprocess_args.append(preview_task.encode_task.temp_file.file_path)

    return subprocess_args
