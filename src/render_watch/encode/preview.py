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
import subprocess
import threading

from render_watch.ffmpeg import encoding, trim
from render_watch.helpers import ffmpeg_helper
from render_watch import app_preferences


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

    def generate_previews(self, encoding_task: encoding.Task):
        """
        Adds the given encoding task to the crop preview, trim preview, and settings preview queues.

        Parameters:
            encoding_task: Encoding task to send to the preview queues.

        Returns:
            None
        """
        if not encoding_task.input_file.is_video:
            return

        self._crop_preview.add_crop_task(encoding_task)
        self._trim_preview.add_trim_task(encoding_task)

        if encoding_task.video_codec:
            self._settings_preview.add_settings_task(encoding_task)

    def generate_crop_preview(self, encoding_task: encoding.Task, time_position: int | float):
        """
        Adds the given encoding task to the crop preview queue and creates the preview at the given time position.

        Parameters:
            encoding_task: Encoding task to send to the crop preview queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._crop_preview.add_crop_task(encoding_task, time_position)

    def generate_trim_preview(self, encoding_task: encoding.Task, time_position: int | float):
        """
        Adds the given encoding task to the trim preview queue and creates the preview at the given time position.

        Parameters:
            encoding_task: Encoding task to send to the trim preview queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._trim_preview.add_trim_task(encoding_task, time_position)

    def generate_settings_preview(self, encoding_task: encoding.Task, time_position: int | float):
        """
        Adds the given encoding task to the settings preview queue and creates the preview at the given time position.

        Parameters:
            encoding_task: Encoding task to send to the settings preview queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        if encoding_task.video_codec:
            self._settings_preview.add_settings_task(encoding_task, time_position)

    def generate_video_preview(self, encoding_task: encoding.Task, time_position: int | float):
        """
        Adds the given encoding task to the video preview queue and creates the preview at the given time position.

        Parameters:
            encoding_task: Encoding task to send to the settings preview queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        if encoding_task.video_codec:
            self._video_preview.add_video_task(encoding_task, time_position)

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
    def run_preview_subprocess(encoding_task: encoding.Task, subprocess_args_list: list):
        """
        Runs a subprocess for each args list contained in subprocess_args_list.

        Parameters:
            encoding_task: Encoding task that's being used to make a preview.
            subprocess_args_list: List that contains lists of subprocess args.

        Returns:
            Subprocess' return code as an integer.
        """
        for args_list in subprocess_args_list:
            with subprocess.Popen(args_list,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  bufsize=1) as preview_process:
                process_return_code = preview_process.wait()

            if process_return_code:
                logging.exception(''.join(['--- PREVIEW SUBPROCESS FAILED:',
                                           encoding_task.temp_output_file.file_path,
                                           ' ---\n',
                                           str(args_list)]))

                break

        return process_return_code


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
                encoding_task, time_position = self._crop_tasks_queue.get()

                if encoding_task:
                    encoding_task_copy = encoding_task.get_copy()
                else:
                    logging.info('--- STOPPING CROP PREVIEW QUEUE LOOP ---')

                    break

                try:
                    if time_position is None:
                        time_position = round(encoding_task_copy.input_file.duration / 2, 2)

                    encoding_task_copy.temp_output_file.name = ''.join([encoding_task_copy.temp_output_file.name,
                                                                        '_crop_preview'])
                    encoding_task_copy.temp_output_file.extension = '.png'
                    encoding_task_copy.is_using_temp_output_file = True

                    self._process_crop_preview_task(encoding_task, encoding_task_copy, time_position)
                except:
                    logging.exception(''.join(['--- CROP PREVIEW TASK FAILED ---\n',
                                               encoding_task_copy.input_file.file_path]))
                finally:
                    encoding_task.temp_output_file.crop_preview_threading_event.set()
        except:
            logging.exception('--- CROP PREVIEW QUEUE LOOP FAILED ---')

    def _process_crop_preview_task(self,
                                   encoding_task: encoding.Task,
                                   encoding_task_copy: encoding.Task,
                                   time_position: int | float):
        # Creates a preview file for the crop preview task.
        crop_preview_args = _get_preview_subprocess_args(encoding_task_copy, time_position)

        if self.preview_generator.run_preview_subprocess(encoding_task_copy, [crop_preview_args]):
            encoding_task.temp_output_file.crop_preview_file_path = None

            raise Exception
        else:
            encoding_task.temp_output_file.crop_preview_file_path = encoding_task_copy.temp_output_file.file_path

    def add_crop_task(self, encoding_task: encoding.Task, time_position=None):
        """
        Adds the given encoding task to the crop preview queue.

        Parameters:
            encoding_task: Encoding task to add to the crop tasks queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._crop_tasks_queue.put((encoding_task, time_position))

    def add_stop_task(self):
        """
        Adds a False boolean to the crop preview queue to stop the queue loop.

        Returns:
            None
        """
        self._crop_tasks_queue.put((False, None))

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
                encoding_task, time_position = self._trim_tasks_queue.get()

                if encoding_task:
                    encoding_task_copy = encoding_task.get_copy()
                else:
                    logging.info('--- STOPPING TRIM PREVIEW QUEUE LOOP ---')

                    break

                try:
                    if time_position is None:
                        time_position = 0

                    encoding_task_copy.temp_output_file.name = ''.join([encoding_task_copy.temp_output_file.name,
                                                                        '_trim_preview'])
                    encoding_task_copy.temp_output_file.extension = '.png'
                    encoding_task_copy.is_using_temp_output_file = True

                    self._process_trim_preview_task(encoding_task, encoding_task_copy, time_position)
                except:
                    logging.exception(''.join(['--- TRIM PREVIEW TASK FAILED ---\n',
                                               encoding_task_copy.input_file.file_path]))
                finally:
                    encoding_task.temp_output_file.trim_preview_threading_event.set()
        except:
            logging.exception('--- TRIM PREVIEW QUEUE LOOP FAILED ---')

    def _process_trim_preview_task(self,
                                   encoding_task: encoding.Task,
                                   encoding_task_copy: encoding.Task,
                                   time_position: int | float):
        # Creates a preview file for the trim preview task.
        trim_preview_args = _get_preview_subprocess_args(encoding_task_copy, time_position)

        if self.preview_generator.run_preview_subprocess(encoding_task_copy, [trim_preview_args]):
            encoding_task.temp_output_file.trim_preview_file_path = None

            raise Exception
        else:
            encoding_task.temp_output_file.trim_preview_file_path = encoding_task_copy.temp_output_file.file_path

    def add_trim_task(self, encoding_task: encoding.Task, time_position=None):
        """
        Adds the given encoding task to the trim preview queue.

        Parameters:
            encoding_task: Encoding task to add to the trim tasks queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._trim_tasks_queue.put((encoding_task, time_position))

    def add_stop_task(self):
        """
        Adds a False boolean to the trim preview queue to stop the queue loop.

        Returns:
            None
        """
        self._trim_tasks_queue.put((False, None))

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
                encoding_task, time_position = self._settings_tasks_queue.get()

                if encoding_task:
                    encoding_task_copy = encoding_task.get_copy()
                else:
                    logging.info('--- STOPPING SETTINGS PREVIEW QUEUE LOOP ---')

                    break

                try:
                    if time_position is None:
                        time_position = round(encoding_task_copy.input_file.duration / 4, 2)

                    self._setup_encoding_task(encoding_task_copy, time_position)
                    self._process_settings_preview_task(encoding_task, encoding_task_copy)
                except:
                    logging.exception(''.join(['--- SETTINGS PREVIEW TASK FAILED ---\n',
                                               encoding_task_copy.input_file.file_path]))
                finally:
                    encoding_task.temp_output_file.settings_preview_threading_event.set()
        except:
            logging.exception('--- SETTINGS PREVIEW QUEUE LOOP FAILED ---')

    def _setup_encoding_task(self, encoding_task: encoding.Task, time_position: float | int):
        # Sets the encoding task's settings for generating a settings preview file.
        encoding_task.temp_output_file.name = encoding_task.temp_output_file.name + '_preview'
        encoding_task.temp_output_file.extension = encoding_task.output_file.extension
        encoding_task.is_using_temp_output_file = True
        self._setup_encoding_task_trim_settings(encoding_task, time_position)

    def _setup_encoding_task_trim_settings(self, encoding_task: encoding.Task, time_position: float | int):
        # Sets the encoding task's trim settings for generating a settings preview file.
        if time_position > (encoding_task.input_file.duration - 1):
            time_position -= 1

        trim_settings = trim.TrimSettings()
        trim_settings.start_time = time_position
        trim_settings.trim_duration = self.ENCODE_DURATION
        encoding_task.trim = trim_settings

    def _process_settings_preview_task(self,
                                       encoding_task: encoding.Task,
                                       encoding_task_copy: encoding.Task):
        # Creates a preview file for the settings preview task.
        settings_preview_args = self._get_preview_subprocess_args(encoding_task_copy)

        if self.preview_generator.run_preview_subprocess(encoding_task_copy, settings_preview_args):
            encoding_task.temp_output_file.settings_preview_file_path = None

            raise Exception
        else:
            encoding_task.temp_output_file.settings_preview_file_path = encoding_task_copy.temp_output_file.file_path

    def _get_preview_subprocess_args(self, encoding_task: encoding.Task) -> list:
        # Returns a list that contains lists of subprocess args for the settings preview task.
        settings_preview_args = encoding.FFmpegArgs.get_args(encoding_task)
        settings_preview_args.append(self._get_single_image_preview_subprocess_args(encoding_task))

        return settings_preview_args

    @staticmethod
    def _get_single_image_preview_subprocess_args(encoding_task: encoding.Task) -> list:
        # Returns a list that contains the subprocess args for generating a single image of the settings preview file.
        single_image_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
        single_image_args.append('-i')
        single_image_args.append(encoding_task.temp_output_file.file_path)
        encoding_task.temp_output_file.extension = '.png'
        single_image_args.append('-f')
        single_image_args.append('image2')
        single_image_args.append('-an')
        single_image_args.append('-update')
        single_image_args.append('1')
        single_image_args.append(encoding_task.temp_output_file.file_path)

        return single_image_args

    def add_settings_task(self, encoding_task: encoding.Task, time_position=None):
        """
        Adds the given encoding task to the settings preview queue.

        Parameters:
            encoding_task: Encoding task to add to the settings tasks queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._settings_tasks_queue.put((encoding_task, time_position))

    def add_stop_task(self):
        """
        Adds a False boolean to the settings preview queue to stop the queue loop.

        Returns:
            None
        """
        self._settings_tasks_queue.put((False, None))

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
                encoding_task, time_position = self._video_preview_queue.get()

                if encoding_task:
                    encoding_task_copy = encoding_task.get_copy()
                else:
                    logging.info('--- STOPPING VIDEO PREVIEW QUEUE LOOP ---')

                    break

                try:
                    if time_position is None:
                        time_position = round(encoding_task_copy.input_file.duration / 4, 2)

                    self._setup_encoding_task(encoding_task_copy, time_position)
                    self._process_video_preview_task(encoding_task, encoding_task_copy)
                except:
                    logging.exception(''.join(['--- VIDEO PREVIEW TASK FAILED ---\n',
                                               encoding_task_copy.input_file.file_path]))
                finally:
                    encoding_task.video_preview_threading_event.set()
        except:
            logging.exception('--- VIDEO PREVIEW QUEUE LOOP FAILED ---')

    def _setup_encoding_task(self, encoding_task: encoding.Task, time_position: float | int):
        # Creates a preview file for the video preview task.
        encoding_task.temp_output_file.name = encoding_task.temp_output_file.name + '_preview'
        encoding_task.temp_output_file.extension = encoding_task.output_file.extension
        encoding_task.is_using_temp_output_file = True
        self._setup_encoding_task_trim_settings(encoding_task, time_position)

    @staticmethod
    def _setup_encoding_task_trim_settings(encoding_task: encoding.Task, time_position: float | int):
        # Sets the encoding task's settings for generating a video preview file.
        if time_position > (encoding_task.input_file.duration - encoding_task.video_preview_duration):
            time_position -= encoding_task.video_preview_duration

        trim_settings = trim.TrimSettings()
        trim_settings.start_time = time_position
        trim_settings.trim_duration = encoding_task.video_preview_duration
        encoding_task.trim = trim_settings

    def _process_video_preview_task(self, encoding_task: encoding.Task, encoding_task_copy: encoding.Task):
        # Creates a preview file for the video preview task.
        video_preview_args = encoding.FFmpegArgs.get_args(encoding_task_copy)

        if self.preview_generator.run_preview_subprocess(encoding_task_copy, video_preview_args):
            encoding_task.temp_output_file.video_preview_file_path = None

            raise Exception
        else:
            encoding_task.temp_output_file.video_preview_file_path = encoding_task_copy.temp_output_file.file_path

    def add_video_task(self, encoding_task: encoding.Task, time_position=None):
        """
        Adds the given encoding task to the video preview queue.

        Parameters:
            encoding_task: Encoding task to add to the video tasks queue.
            time_position: Time position in the video to create the preview.

        Returns:
            None
        """
        self._video_preview_queue.put((encoding_task, time_position))

    def add_stop_task(self):
        """
        Adds a False boolean to the video preview queue to stop the queue loop.

        Returns:
            None
        """
        self._video_preview_queue.put((False, None))

    def empty_queue(self):
        """
        Empties the video preview queue.

        Returns:
            None
        """
        while not self._video_preview_queue.empty():
            self._video_preview_queue.get()


def _get_preview_subprocess_args(encoding_task: encoding.Task, time_position: float | int) -> list:
    # Returns a list of subprocess args for generating a single image with crop for the preview task.
    subprocess_args = ffmpeg_helper.FFMPEG_INIT_ARGS.copy()
    subprocess_args.append('-ss')
    subprocess_args.append(str(time_position))
    subprocess_args.append('-i')
    subprocess_args.append(encoding_task.input_file.file_path)
    subprocess_args.append('-vframes')
    subprocess_args.append('1')

    if encoding_task.filter.ffmpeg_args['-filter_complex'] is not None:
        subprocess_args.append('-filter_complex')
        subprocess_args.append(encoding_task.filter.ffmpeg_args['-filter_complex'])

    subprocess_args.append('-an')
    subprocess_args.append(encoding_task.temp_output_file.file_path)

    return subprocess_args
