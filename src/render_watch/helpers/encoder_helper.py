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


def get_chunks(ffmpeg, preferences):
    """Generates ffmpeg settings objects in chunks.

    Takes the ffmpeg settings object and generates chunks using the amount in preferences.
    These chunks will be homogeneous.

    :param ffmpeg:
        ffmpeg settings object.
    :param preferences:
        Application's preferences object.
    """
    number_of_chunks = __get_valid_number_of_chunks(ffmpeg, preferences)

    if not is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
        return None

    return __generate_chunk_list(ffmpeg, number_of_chunks, preferences)


def __get_valid_number_of_chunks(ffmpeg, preferences):
    # Checks if ffmpeg settings uses NVENC and returns the amount of chunks
    # depending on which codec is being used.
    if ffmpeg.is_video_settings_nvenc():
        return NvidiaHelper.nvenc_max_workers

    return preferences.parallel_tasks


def __generate_chunk_list(ffmpeg, number_of_chunks, preferences):
    # Returns a list of ffmpeg settings objects for all generated chunks.
    chunk_rows = []
    for current_chunk in range(1, (number_of_chunks + 1)):
        chunk_rows.append(__generate_chunk(ffmpeg, number_of_chunks, current_chunk, preferences))
    chunk_rows.append(__generate_audio_chunk(ffmpeg, preferences))
    return chunk_rows


def __generate_chunk(ffmpeg, number_of_chunks, chunk, preferences):
    # Creates a ffmpeg settings object chunk based on chunk/number_of_chunks.
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
    # Trims the ffmpeg settings object in correspondence with which chunk it is.
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


def __generate_audio_chunk(ffmpeg, preferences):
    # Returns an ffmpeg settings object based on outputting just the audio.
    ffmpeg_copy = ffmpeg.get_copy()

    ffmpeg_copy.no_video = True
    ffmpeg_copy.video_settings = None
    ffmpeg_copy.output_container = '.mkv'
    ffmpeg_copy.filename = ffmpeg_copy.temp_file_name + '_audio'
    ffmpeg_copy.output_directory = preferences.temp_directory + '/'

    return ffmpeg_copy


def is_ffmpeg_viable_for_chunking(ffmpeg, number_of_chunks):
    """Checks if ffmpeg settings object can be split into chunks.

    Under 10 seconds is currently considered too short to be a chunk.

    :param ffmpeg:
        ffmpeg settings object.
    :param number_of_chunks:
        Number of chunks to split ffmpeg into.
    """
    if ffmpeg.video_settings is not None:
        if ffmpeg.trim_settings is not None:
            if ffmpeg.audio_settings is not None and (ffmpeg.trim_settings.trim_duration / number_of_chunks) >= 10:
                return True
        elif (ffmpeg.duration_origin / number_of_chunks) >= 10:
            return True

    return False


def concatenate_video_chunks(video_chunks_list, ffmpeg, preferences):
    """Concatenates the completed chunk tasks into a single output.

    Creates a concatention file that contains a list of all chunk files.
    It then runs a process that uses ffmpeg to concatenate the chunk files.

    :param video_chunks_list:
        List of video chunk files.
    :param ffmpeg:
        ffmpeg settings object.
    :param preferences:
        Application's preferences object.
    """
    concat_option_file_path = preferences.temp_directory + '/' + ffmpeg.temp_file_name + '_concat'
    concat_option_text = __generate_video_concat_option_text(video_chunks_list)
    if not __write_concat_option_file(ffmpeg, concat_option_file_path, concat_option_text):
        return

    ffmpeg_args = __generate_video_concat_ffmpeg_args(ffmpeg, concat_option_file_path, preferences)
    __run_video_concat_process(ffmpeg, ffmpeg_args)


def __generate_video_concat_option_text(video_chunks_row_list):
    # Returns a list of chunk files to be concatenated.
    concatenation_lines = []
    for video_chunk_row in video_chunks_row_list:
        video_chunk_file_name = video_chunk_row.ffmpeg.filename
        video_chunk_output_container = video_chunk_row.ffmpeg.output_container
        concatenation_lines.append('file \'' + video_chunk_file_name + video_chunk_output_container + '\'\n')
    return concatenation_lines


def __write_concat_option_file(ffmpeg, concat_option_file_path, concat_options):
    # Writes the concatenation options into the concatenation file.
    with open(concat_option_file_path, 'w') as concatenation_file:
        try:
            concatenation_file.writelines(concat_options)
        except:
            logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---')
            return False
        else:
            return True


def __generate_video_concat_ffmpeg_args(ffmpeg, concatenation_output_file, preferences):
    # Returns ffmpeg arguments for concatenating chunk files.
    ffmpeg_args = ffmpeg.FFMPEG_CONCATENATION_INIT_ARGS.copy()
    ffmpeg_args.append(concatenation_output_file)
    ffmpeg_args.append('-c')
    ffmpeg_args.append('copy')
    ffmpeg_args.append(preferences.temp_directory + '/' + ffmpeg.temp_file_name + ffmpeg.output_container)
    return ffmpeg_args


def __run_video_concat_process(ffmpeg, ffmpeg_args):
    # Runs a process using the ffmpeg arguments to concatenate chunk files.
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

        rc = process.wait()

    if rc != 0:
        logging.error('--- FAILED TO CONCAT VIDEO CHUNKS: ' + ffmpeg.filename + ' ---\n' + stdout_log)


def mux_chunks(audio_chunk_row, ffmpeg, preferences):
    # Generates ffmpeg arguments and runs a process to mux the
    # video and audio streams after a chunk encode completes.
    ffmpeg_args = __generate_mux_video_chunks_ffmpeg_args(ffmpeg, audio_chunk_row, preferences)
    __run_mux_video_chunks_process(ffmpeg, ffmpeg_args)


def __generate_mux_video_chunks_ffmpeg_args(ffmpeg, audio_chunk_row, preferences):
    # Generates ffmpeg arguments for muxing video and audio files after a chunk encode completes.
    ffmpeg_args = ffmpeg.FFMPEG_INIT_ARGS.copy()

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


def __run_mux_video_chunks_process(ffmpeg, ffmpeg_args):
    # Runs a process using ffmoeg arguments to mux the video and audio files
    # after a chunk encode completes.
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

        rc = process.wait()

    if rc != 0:
        logging.error('--- FAILED TO MUX VIDEO AND AUDIO: ' + ffmpeg.filename + ' ---\n' + stdout_log)


def is_extension_valid(file_path):
    # Checks if file has an extension listed in valid_input_containers.
    container = file_path.split('.')[-1]
    return container in Settings.VALID_INPUT_CONTAINERS
