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

import subprocess
import logging

from ffmpeg.trim_settings import TrimSettings
from ffmpeg.settings import Settings
from startup.app_requirements import AppRequirements


def get_chunks(ffmpeg, preferences):
    number_of_chunks = __get_number_of_chunks_from_ffmpeg(ffmpeg, preferences)

    if not is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
        return None

    return __generate_chunks_from_ffmpeg(ffmpeg, number_of_chunks, preferences)


def __get_number_of_chunks_from_ffmpeg(ffmpeg, preferences):
    if ffmpeg.is_video_settings_nvenc():
        return AppRequirements.nvenc_max_workers

    return preferences.parallel_tasks


def __generate_chunks_from_ffmpeg(ffmpeg, number_of_chunks, preferences):
    chunk_rows = []

    for current_chunk in range(1, (number_of_chunks + 1)):
        chunk_rows.append(__generate_chunk(ffmpeg, number_of_chunks, current_chunk, preferences))

    chunk_rows.append(__get_audio_chunk(ffmpeg, preferences))

    return chunk_rows


def __generate_chunk(ffmpeg, number_of_chunks, chunk, preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    trim_settings = __setup_chunk_trim_settings(ffmpeg, number_of_chunks, chunk)

    if ffmpeg.is_video_settings_2_pass():
        ffmpeg_copy.temp_file_name += ('_' + str(chunk))
        ffmpeg_copy.video_settings.stats = preferences.temp_directory + '/' + ffmpeg_copy.temp_file_name + '.log'

    ffmpeg_copy.audio_settings = None
    ffmpeg_copy.no_audio = True
    ffmpeg_copy.video_chunk = True
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name + '_' + str(chunk)
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'
    ffmpeg_copy.trim_settings = trim_settings

    if ffmpeg_copy.is_video_settings_vp9() or ffmpeg_copy.is_video_settings_vp8():
        ffmpeg_copy.output_container = '.webm'
    else:
        ffmpeg_copy.output_container = '.mp4'

    return ffmpeg_copy


def __setup_chunk_trim_settings(ffmpeg, number_of_chunks, chunk):
    trim_settings = TrimSettings()

    if ffmpeg.trim_settings is not None:
        trim_duration = ffmpeg.trim_settings.trim_duration
        trim_start_time = ffmpeg.trim_settings.start_time
        chunk_duration = (trim_duration / number_of_chunks)
        chunk_start_time = trim_start_time + (chunk_duration * (chunk - 1))

        if chunk == 1:
            trim_settings.start_time = trim_start_time
            trim_settings.trim_duration = chunk_duration
        elif chunk == number_of_chunks:
            chunk_offset_duration = (trim_duration + trim_start_time) - chunk_start_time
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_offset_duration
        else:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_duration
    else:
        duration = ffmpeg.duration_origin
        chunk_duration = (duration / number_of_chunks)
        chunk_start_time = chunk_duration * (chunk - 1)

        if chunk == 1:
            trim_settings.start_time = 0
            trim_settings.trim_duration = chunk_duration
        elif chunk == number_of_chunks:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = duration - chunk_start_time
        else:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_duration

    return trim_settings


def __get_audio_chunk(ffmpeg, preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    ffmpeg_copy.no_video = True
    ffmpeg_copy.video_settings = None
    ffmpeg_copy.output_container = '.mkv'
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name + '_audio'
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'

    return ffmpeg_copy


def is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
    if ffmpeg.video_settings is not None:

        if ffmpeg.trim_settings is not None:

            if ffmpeg.audio_settings is not None and (ffmpeg.trim_settings.trim_duration / number_of_chunks) >= 10:
                return True
        elif (ffmpeg.duration_origin / number_of_chunks) >= 10:
            return True

    return False


def run_video_chunks_concatination(video_chunks_row_list, ffmpeg, preferences):
    concatenation_output_file_path = preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_concat'
    concatenation_lines = __generate_video_chunk_concatenation_lines(video_chunks_row_list)
    ffmpeg_args = __generate_video_chunk_concatenation_ffmpeg_args(ffmpeg, concatenation_output_file_path, preferences)

    if not __generate_concatenation_output_file(ffmpeg, concatenation_output_file_path, concatenation_lines):
        return

    __run_video_chunks_concatenation_process(ffmpeg, ffmpeg_args)


def __generate_video_chunk_concatenation_lines(video_chunks_row_list):
    concatenation_lines = []

    for video_chunk_row in video_chunks_row_list:
        video_chunk_file_name = video_chunk_row.ffmpeg.filename
        video_chunk_output_container = video_chunk_row.ffmpeg.output_container

        concatenation_lines.append('file \'' + video_chunk_file_name + video_chunk_output_container + '\'\n')

    return concatenation_lines


def __generate_concatenation_output_file(ffmpeg, concatenation_output_file_path, concatenation_lines):
    with open(concatenation_output_file_path, 'w') as concatenation_file:
        try:
            concatenation_file.writelines(concatenation_lines)
        except:
            logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---')

            return False
        else:
            return True


def __generate_video_chunk_concatenation_ffmpeg_args(ffmpeg, concatenation_output_file, preferences):
    ffmpeg_args = ffmpeg.ffmpeg_concatenation_init_args.copy()

    ffmpeg_args.append(concatenation_output_file)
    ffmpeg_args.append('-c')
    ffmpeg_args.append('copy')
    ffmpeg_args.append(preferences.temp_directory + '/' + ffmpeg.temp_file_name + ffmpeg.output_container)

    return ffmpeg_args


def __run_video_chunks_concatenation_process(ffmpeg, ffmpeg_args):
    with subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        while True:
            output = process.stdout.readline().strip()

            if not output:
                break

        rc = process.wait()

    if rc != 0:
        logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---')


def run_video_chunks_muxing(audio_chunk_row, ffmpeg, preferences):
    ffmpeg_args = __generate_video_chunks_muxing_ffmpeg_args(ffmpeg, audio_chunk_row, preferences)

    __run_video_chunks_muxing_process(ffmpeg, ffmpeg_args)


def __generate_video_chunks_muxing_ffmpeg_args(ffmpeg, audio_chunk_row, preferences):
    ffmpeg_args = ffmpeg.ffmpeg_init_args.copy()
    video_input_file_name = ffmpeg.temp_file_name + ffmpeg.output_container
    video_input_file_path = preferences.temp_directory + '/' + video_input_file_name
    audio_input_file_name = audio_chunk_row.ffmpeg.filename + audio_chunk_row.ffmpeg.output_container
    audio_input_file_path = preferences.temp_directory + '/' + audio_input_file_name

    ffmpeg_args.append('-i')
    ffmpeg_args.append(video_input_file_path)
    ffmpeg_args.append('-i')
    ffmpeg_args.append(audio_input_file_path)
    ffmpeg_args.append('-c')
    ffmpeg_args.append('copy')
    ffmpeg_args.append(ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container)

    return ffmpeg_args


def __run_video_chunks_muxing_process(ffmpeg, ffmpeg_args):
    with subprocess.Popen(ffmpeg_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                          bufsize=1) as process:
        while True:
            output = process.stdout.readline().strip()

            if not output:
                break

        rc = process.wait()

    if rc != 0:
        logging.error('--- FAILED TO MUX VIDEO AND AUDIO: ' + ffmpeg.filename + ' ---')


def is_input_valid(input_file_path):
    container = input_file_path.split('.')[-1]

    return container in Settings.valid_input_containers
