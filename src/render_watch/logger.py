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
import faulthandler
import sys
import os

from datetime import datetime


def setup_logging(application_config_directory: str):
    """
    Sets the file path and logging level for the logger.

    Parameters:
        application_config_directory: String that represents the application's configuration directory.
    """
    logging.basicConfig(filename=_get_logging_file_path(application_config_directory), level=_get_logging_type())


def _get_logging_file_path(application_config_directory: str) -> str:
    # Returns the logger's file path using the date and time.
    logging_file_name = datetime.now().strftime('%d-%m-%Y_%H:%M:%S') + '.log'
    logging_file_path = os.path.join(application_config_directory, logging_file_name)

    return logging_file_path


def _get_logging_type() -> int:
    # Returns the logging level type depending on whether the debug arg was passed into the application.
    logging_type = logging.ERROR

    for arg in sys.argv:
        if arg == '--debug':
            faulthandler.enable()

            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            logging_type = logging.DEBUG

            break

    return logging_type


def log_subprocess_error(input_file_name: str, subprocess_args: list | tuple, stdout_log: str):
    logging.error(''.join(['--- FAILED TO RUN PROCESS FOR: ',
                           input_file_name,
                           ' ---\n',
                           str(subprocess_args),
                           '\n',
                           stdout_log]))


def log_preview_subprocess_failed(temp_file_path: str, subprocess_args_list: list[str]):
    logging.exception(''.join(['--- PREVIEW SUBPROCESS FAILED: ', temp_file_path, ' ---\n', str(subprocess_args_list)]))


def log_nvenc_max_workers_set(max_workers: int):
    logging.info(' '.join(['--- NVENC MAX WORKERS SET TO:', str(max_workers), '---']))


def log_video_chunk_concatenation_error(input_file_name: str):
    logging.error(' '.join(['--- FAILED TO CONCAT VIDEO CHUNKS:', input_file_name, '---']))


def log_stopping_trim_preview_queue_loop():
    logging.info('--- STOPPING TRIM PREVIEW QUEUE LOOP ---')


def log_trim_preview_task_failed(input_file_path: str):
    logging.exception(''.join(['--- TRIM PREVIEW TASK FAILED ---\n', input_file_path]))


def log_trim_preview_queue_loop_failed():
    logging.exception('--- TRIM PREVIEW QUEUE LOOP FAILED ---')


def log_stopping_crop_preview_queue_loop():
    logging.info('--- STOPPING CROP PREVIEW QUEUE LOOP ---')


def log_crop_preview_task_failed(input_file_path: str):
    logging.exception(''.join(['--- CROP PREVIEW TASK FAILED ---\n', input_file_path]))


def log_crop_preview_queue_loop_failed():
    logging.exception('--- CROP PREVIEW QUEUE LOOP FAILED ---')


def log_stopping_settings_preview_queue_loop():
    logging.info('--- STOPPING SETTINGS PREVIEW QUEUE LOOP ---')


def log_settings_preview_task_failed(input_file_path: str):
    logging.exception(''.join(['--- SETTINGS PREVIEW TASK FAILED ---\n', input_file_path]))


def log_settings_preview_queue_loop_failed():
    logging.exception('--- SETTINGS PREVIEW QUEUE LOOP FAILED ---')


def log_stopping_video_preview_queue_loop():
    logging.info('--- STOPPING VIDEO PREVIEW QUEUE LOOP ---')


def log_video_preview_task_failed(input_file: str):
    logging.exception(''.join(['--- VIDEO PREVIEW TASK FAILED ---\n', input_file]))


def log_video_preview_queue_loop_failed():
    logging.exception('--- VIDEO PREVIEW QUEUE LOOP FAILED ---')


def log_video_preview_process_stopped(output_file_path: str):
    logging.info(' '.join(['--- VIDEO PREVIEW PROCESS STOPPED:', output_file_path, '---']))


def log_video_preview_process_failed(output_file_path: str, stdout_last_line: str):
    logging.error(''.join(['--- VIDEO PREVIEW PROCESS FAILED: ', output_file_path, ' ---\n', stdout_last_line]))


def log_stopping_benchmark_queue_loop():
    logging.info('--- STOPPING BENCHMARK QUEUE LOOP ---')


def log_benchmark_task_failed(input_file_path: str):
    logging.exception(''.join(['--- BENCHMARK TASK FAILED ---\n', input_file_path]))


def log_benchmark_process_stopped(input_file_path: str):
    logging.info(' '.join(['--- BENCHMARK PROCESS STOPPED:', input_file_path, '---']))


def log_benchmark_process_failed(input_file_path: str, stdout_last_line: str):
    logging.error(''.join(['--- BENCHMARK PROCESS FAILED: ', input_file_path, ' ---\n', stdout_last_line]))


def log_task_not_in_running_tasks_list(output_file_path: str):
    logging.exception('--- TASK NOT IN RUNNING TASKS LIST ---\n' + output_file_path)


def log_failed_to_run_standard_encoding_task(output_file_path: str):
    logging.exception(''.join(['--- FAILED TO RUN STANDARD ENCODING TASK ---\n', output_file_path]))


def log_standard_tasks_queue_loop_failed():
    logging.exception('--- STANDARD TASKS QUEUE LOOP FAILED ---')


def log_parallel_nvenc_queue_loop_disabled():
    logging.info('--- PARALLEL NVENC QUEUE LOOP DISABLED ---')


def log_failed_to_run_encoding_task(codec_name: str):
    logging.exception(''.join(['--- FAILED TO RUN ', codec_name, ' ENCODING TASK ---']))


def log_codec_queue_loop_instance_failed(codec_name: str):
    logging.exception(''.join(['--- ', codec_name, ' CODEC QUEUE LOOP INSTANCE FAILED ---']))


def log_watch_folder_queue_loop_failed():
    logging.exception('--- WATCH FOLDER QUEUE LOOP FAILED ---')


def log_watch_folder_next_encode_task_failed(output_file_path: str):
    logging.exception(''.join(['--- WATCH FOLDER CHILD ENCODING TASK FAILED ---\n', output_file_path]))


def log_watch_folder_encoding_task_loop_failed(output_file_path: str):
    logging.exception('--- WATCH FOLDER ENCODING TASK LOOP FAILED ---\n', output_file_path)


def log_encode_process_stopped(output_file_path: str):
    logging.info(' '.join(['--- ENCODE PROCESS STOPPED:', output_file_path, '---']))


def log_encode_process_failed(output_file_path: str, stdout_last_line: str):
    logging.error(''.join(['--- ENCODE PROCESS FAILED: ', output_file_path, ' ---\n', stdout_last_line]))
