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


import subprocess
import logging

from render_watch.ffmpeg.trim_settings import TrimSettings
from render_watch.ffmpeg.settings import Settings
from render_watch.helpers.nvidia_helper import NvidiaHelper


def get_chunks(ffmpeg, application_preferences):
    """
    Splits ffmpeg settings object into homogeneous chunks.

    :param ffmpeg: ffmpeg settings.
    :param application_preferences: Application preferences.
    """
    number_of_chunks = _get_number_of_chunks(ffmpeg, application_preferences)

    if is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
        return _get_chunks_list(ffmpeg, number_of_chunks, application_preferences)

    return None


def _get_number_of_chunks(ffmpeg, application_preferences):
    if ffmpeg.is_video_settings_nvenc():
        return NvidiaHelper.nvenc_max_workers

    if application_preferences.is_per_codec_parallel_tasks_enabled:
        return _get_per_codec_number_of_chunks(ffmpeg, application_preferences)

    return application_preferences.parallel_tasks


def _get_per_codec_number_of_chunks(ffmpeg, application_preferences):
    if ffmpeg.is_video_settings_x264():
        return application_preferences.per_codec_parallel_tasks['x264']
    elif ffmpeg.is_video_settings_x265():
        return application_preferences.per_codec_parallel_tasks['x265']
    elif ffmpeg.is_video_settings_vp9():
        return application_preferences.per_codec_parallel_tasks['vp9']
    else:
        return 1


def _get_chunks_list(ffmpeg, number_of_chunks, application_preferences):
    chunks = []

    for chunk_index in range(1, (number_of_chunks + 1)):
        chunks.append(_generate_video_chunk(ffmpeg, number_of_chunks, chunk_index, application_preferences))
    chunks.append(_generate_audio_chunk(ffmpeg, application_preferences))

    return chunks


def _generate_video_chunk(ffmpeg, number_of_chunks, chunk_index, application_preferences):
    trim_settings = _get_chunk_trim_settings(ffmpeg, number_of_chunks, chunk_index)

    ffmpeg_copy = _get_video_chunk_ffmpeg_settings(ffmpeg, chunk_index, application_preferences)
    ffmpeg_copy.trim_settings = trim_settings
    return ffmpeg_copy


def _get_chunk_trim_settings(ffmpeg, number_of_chunks, chunk_index):
    trim_settings = TrimSettings()

    if ffmpeg.trim_settings:
        trim_duration = ffmpeg.trim_settings.trim_duration
        trim_start_time = ffmpeg.trim_settings.start_time
        chunk_duration = (trim_duration / number_of_chunks)
        chunk_start_time = trim_start_time + (chunk_duration * (chunk_index - 1))
        if chunk_index == 1:
            trim_settings.start_time = trim_start_time
            trim_settings.trim_duration = chunk_duration
        elif chunk_index == number_of_chunks:
            chunk_offset_duration = (trim_duration + trim_start_time) - chunk_start_time
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_offset_duration
        else:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_duration
    else:
        duration = ffmpeg.duration_origin
        chunk_duration = (duration / number_of_chunks)
        chunk_start_time = chunk_duration * (chunk_index - 1)
        if chunk_index == 1:
            trim_settings.start_time = 0
            trim_settings.trim_duration = chunk_duration
        elif chunk_index == number_of_chunks:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = duration - chunk_start_time
        else:
            trim_settings.start_time = chunk_start_time
            trim_settings.trim_duration = chunk_duration

    return trim_settings


def _get_video_chunk_ffmpeg_settings(ffmpeg, chunk_index, application_preferences):
    ffmpeg_copy = ffmpeg.get_copy()

    if ffmpeg.is_video_settings_2_pass():
        ffmpeg_copy.temp_file_name += ('_' + str(chunk_index))
        ffmpeg_copy.video_settings.stats = application_preferences.temp_directory \
                                           + '/' \
                                           + ffmpeg_copy.temp_file_name \
                                           + '.log'

    ffmpeg_copy.audio_settings = None
    ffmpeg_copy.no_audio = True
    ffmpeg_copy.video_chunk = True
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name + '_' + str(chunk_index)
    ffmpeg_copy.output_directory = application_preferences.temp_directory + '/'

    if ffmpeg_copy.is_video_settings_vp9():
        ffmpeg_copy.output_container = '.webm'
    else:
        ffmpeg_copy.output_container = '.mp4'

    return ffmpeg_copy


def _generate_audio_chunk(ffmpeg, application_preferences):
    ffmpeg_copy = ffmpeg.get_copy()
    ffmpeg_copy.no_video = True
    ffmpeg_copy.video_settings = None
    ffmpeg_copy.output_container = '.mkv'
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name + '_audio'
    ffmpeg_copy.output_directory = application_preferences.temp_directory + '/'
    return ffmpeg_copy


def is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
    """
    Checks if ffmpeg settings object can be split into chunks.
    Under 10 seconds is considered too short to be a chunk.

    :param ffmpeg: ffmpeg settings.
    :param number_of_chunks: Number of chunks to split ffmpeg into.
    """
    if ffmpeg.video_settings:
        if ffmpeg.trim_settings:
            if ffmpeg.audio_settings and (ffmpeg.trim_settings.trim_duration / number_of_chunks) >= 10:
                return True
        elif (ffmpeg.duration_origin / number_of_chunks) >= 10:
            return True

    return False


def concatenate_video_chunks(video_chunks_list, ffmpeg, application_preferences):
    """
    Concatenates video chunks into a single output.

    :param video_chunks_list: List of video chunk files.
    :param ffmpeg: ffmpeg settings object.
    :param application_preferences: Application's preferences object.
    """
    concatenation_file_path = application_preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_concat'
    concatenation_args = _get_video_concatenation_args(video_chunks_list)
    if not _write_concatenation_args(ffmpeg, concatenation_file_path, concatenation_args):
        return

    ffmpeg_args = _get_ffmpeg_concatenation_args(ffmpeg, concatenation_file_path, application_preferences)
    _run_concatenation_process(ffmpeg, ffmpeg_args)


def _get_video_concatenation_args(video_chunks_list):
    concatenation_args = []

    for video_chunk in video_chunks_list:
        video_chunk_file_name = video_chunk.ffmpeg.filename
        video_chunk_output_container = video_chunk.ffmpeg.output_container
        concatenation_args.append('file \'' + video_chunk_file_name + video_chunk_output_container + '\'\n')

    return concatenation_args


def _write_concatenation_args(ffmpeg, concatenation_file_path, concatenation_args):
    try:
        with open(concatenation_file_path, 'w') as concatenation_file:
            concatenation_file.writelines(concatenation_args)

        return True
    except OSError:
        logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---')

        return False


def _get_ffmpeg_concatenation_args(ffmpeg, concatenation_file_path, application_preferences):
    ffmpeg_args = ffmpeg.FFMPEG_CONCATENATION_INIT_ARGS.copy()
    ffmpeg_args.append(concatenation_file_path)
    ffmpeg_args.append('-c')
    ffmpeg_args.append('copy')
    ffmpeg_args.append(application_preferences.temp_directory + '/' + ffmpeg.temp_file_name + ffmpeg.output_container)
    return ffmpeg_args


def _run_concatenation_process(ffmpeg, ffmpeg_args):
    with subprocess.Popen(ffmpeg_args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as process:
        stdout_log = ''

        while True:
            stdout = process.stdout.readline().strip()

            if stdout == '':
                break

            stdout_log += stdout + '\n'

    process_return_code = process.wait()

    if process_return_code:
        logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---\n' + stdout_log)


def mux_audio_chunk(audio_chunk, ffmpeg, application_preferences):
    ffmpeg_args = _get_mux_audio_chunk_ffmpeg_args(audio_chunk, ffmpeg, application_preferences)
    _run_mux_audio_chunk_process(ffmpeg, ffmpeg_args)


def _get_mux_audio_chunk_ffmpeg_args(audio_chunk, ffmpeg, application_preferences):
    video_file_name = ffmpeg.temp_file_name + ffmpeg.output_container
    video_file_path = application_preferences.temp_directory + '/' + video_file_name
    audio_file_name = audio_chunk.ffmpeg.filename + audio_chunk.ffmpeg.output_container
    audio_file_path = application_preferences.temp_directory + '/' + audio_file_name

    ffmpeg_args = ffmpeg.FFMPEG_INIT_ARGS.copy()
    ffmpeg_args.append('-i')
    ffmpeg_args.append(video_file_path)
    ffmpeg_args.append('-i')
    ffmpeg_args.append(audio_file_path)
    ffmpeg_args.append('-c')
    ffmpeg_args.append('copy')
    ffmpeg_args.append(ffmpeg.output_directory + ffmpeg.filename + ffmpeg.output_container)
    return ffmpeg_args


def _run_mux_audio_chunk_process(ffmpeg, ffmpeg_args):
    with subprocess.Popen(ffmpeg_args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as process:
        stdout_log = ''

        while True:
            stdout = process.stdout.readline().strip()

            if not stdout:
                break

            stdout_log += stdout

    process_return_code = process.wait()

    if process_return_code:
        logging.error('--- FAILED TO MUX VIDEO AND AUDIO: ' + ffmpeg.filename + ' ---\n' + stdout_log)


def is_file_extension_valid(file_path):
    container = file_path.split('.')[-1]
    return container in Settings.VALID_INPUT_CONTAINERS
