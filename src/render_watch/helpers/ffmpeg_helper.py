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


import copy
import subprocess
import time

from itertools import repeat
from concurrent.futures import ThreadPoolExecutor

from render_watch.ffmpeg import task, video_codec, audio_codec
from render_watch import app_preferences, logger


# FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-loglevel', 'quiet', '-stats', '-y']
FFMPEG_INIT_ARGS = ['ffmpeg', '-hide_banner', '-stats', '-y']

FFMPEG_CONCATENATION_INIT_ARGS = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i']

VIDEO_COPY_ARGS = ('-c:v', 'copy')
AUDIO_COPY_ARGS = ('-c:a', 'copy')

AUDIO_NONE_ARG = '-an'
VIDEO_NONE_ARG = '-vn'

RAW_VIDEO_ARGS = ('-f', 'rawvideo')

VSYNC_ARGS = ('-vsync', '0')


def run_process_args(encode_task: task.Encode, process_args: list | tuple):
    """
    Runs a subprocess for the given encoding task using the given process args.

    Parameters:
        encode_task: Encode task that was used to create the process.
        process_args: List of process args.
    """
    with subprocess.Popen(process_args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True,
                          bufsize=1) as process:
        stdout_log = ''

        while True:
            stdout = process.stdout.readline().strip()

            if stdout == '' and process.poll() is not None:
                break

            stdout_log = ''.join([stdout_log, stdout, '\n'])

        process_return_code = process.wait()

    if process_return_code:
        logger.log_subprocess_error(encode_task.input_file.name, process_args, stdout_log)


class Args:
    """Class that contains functions to get a list of ffmpeg subprocess args for the given encoding task."""

    NVDEC_ARGS = ('-hwaccel', 'nvdec')
    NVDEC_OUT_FORMAT_ARGS = ('-hwaccel_output_format', 'cuda')

    @staticmethod
    def get_args(encode_task: task.Encode, cli_args=False) -> list:
        """
        Returns a list of ffmpeg subprocess args for the given encoding task.

        Parameters:
            encode_task: Encoding task to generate args from.
            cli_args: Boolean that represents whether to return arguments for the use of copy/paste into a terminal.

        Returns:
            A list of ffmpeg subprocess args using the given encoding task.
        """
        ffmpeg_args = FFMPEG_INIT_ARGS.copy()
        Args._add_trim_start_args(encode_task, ffmpeg_args)
        Args._add_nvdec_args(encode_task, ffmpeg_args)
        Args._add_input_file_args(encode_task, ffmpeg_args, cli_args)
        Args._add_stream_map_args(encode_task, ffmpeg_args)
        Args._add_video_codec_args(encode_task, ffmpeg_args)
        Args._add_audio_codec_args(encode_task, ffmpeg_args)
        Args._add_filter_args(encode_task, ffmpeg_args)
        Args._add_general_settings_args(encode_task, ffmpeg_args)
        Args._add_trim_duration_args(encode_task, ffmpeg_args)
        Args._add_vsync_args(encode_task, ffmpeg_args)
        Args._add_output_file_args(encode_task, ffmpeg_args, cli_args)

        return Args._add_2_pass_args(encode_task, ffmpeg_args)

    @staticmethod
    def _add_trim_start_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the trim setting's args to the list of ffmpeg args.
        if encode_task.trim_settings:
            ffmpeg_args.append('-ss')
            ffmpeg_args.append(encode_task.trim_settings.ffmpeg_args['-ss'])

    @staticmethod
    def _add_nvdec_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the nvdec args to the list of ffmpeg args.
        if video_codec.is_codec_nvenc(encode_task.get_video_codec()) and Compatibility.is_nvdec_supported():
            ffmpeg_args.extend(Args.NVDEC_ARGS)
            ffmpeg_args.extend(Args.NVDEC_OUT_FORMAT_ARGS)

    @staticmethod
    def _add_input_file_args(encode_task: task.Encode, ffmpeg_args: list, is_cli_args_enabled: bool):
        # Uses the given encoding task to add the input file args to the list of ffmpeg args.
        ffmpeg_args.append('-i')

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"', encode_task.input_file.file_path, '\"']))
        else:
            ffmpeg_args.append(encode_task.input_file.file_path)

    @staticmethod
    def _add_stream_map_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the stream mapping args to the list of ffmpeg args.
        Args._add_video_stream_args(encode_task, ffmpeg_args)
        Args._add_audio_stream_args(encode_task, ffmpeg_args)
        Args._add_subtitle_stream_args(encode_task, ffmpeg_args)

    @staticmethod
    def _add_video_stream_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the video stream mapping args to the list of ffmpeg args.
        if encode_task.get_video_stream() is not None:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(encode_task.get_video_stream().index)]))

    @staticmethod
    def _add_audio_stream_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the audio stream mapping args to the list of ffmpeg args.
        for audio_stream, audio_stream_codec in encode_task.audio_streams.items():
            ffmpeg_args.append('-map')
            ffmpeg_args.append(''.join(['0:', str(audio_stream.index)]))

    @staticmethod
    def _add_subtitle_stream_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the subtitle stream mapping args to the list of ffmpeg args.
        for stream in encode_task.filters.ffmpeg_args['-map']:
            ffmpeg_args.append('-map')
            ffmpeg_args.append(stream)

    @staticmethod
    def _add_video_codec_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the video codec settings args to the list of ffmpeg args.
        if encode_task.is_no_video:
            ffmpeg_args.append(VIDEO_NONE_ARG)
        elif encode_task.get_video_codec():
            ffmpeg_args.extend(Args.get_args_from_dict(encode_task.get_video_codec().ffmpeg_args))
            ffmpeg_args.extend(Args.get_args_from_dict(encode_task.get_video_codec().get_ffmpeg_advanced_args()))
        else:
            ffmpeg_args.extend(VIDEO_COPY_ARGS)

    @staticmethod
    def _add_audio_codec_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the audio codec settings args to the list of ffmpeg args.
        if encode_task.is_no_audio or video_codec.is_codec_2_pass(encode_task.get_video_codec()):
            ffmpeg_args.append(AUDIO_NONE_ARG)
        else:
            Args._add_audio_streams_codec_args(encode_task, ffmpeg_args)

    @staticmethod
    def _add_audio_streams_codec_args(encode_task: task.Encode, ffmpeg_args: list):
        # Adds the audio codec settings for each audio stream to the list of ffmpeg args.
        for audio_stream, audio_stream_codec in encode_task.audio_streams.items():
            if audio_stream_codec is None:
                ffmpeg_args.append(''.join(['-c:a:', str(encode_task.get_audio_stream_index(audio_stream))]))
                ffmpeg_args.append('copy')
            else:
                ffmpeg_args.extend(Args.get_args_from_dict(audio_stream_codec.ffmpeg_args))

    @staticmethod
    def _add_filter_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the filter args to the list of ffmpeg args.
        ffmpeg_args.extend(Args.get_args_from_dict(encode_task.filters.ffmpeg_args))

    @staticmethod
    def _add_general_settings_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the general settings args to the list of ffmpeg args.
        if encode_task.get_video_codec():
            ffmpeg_args.extend(Args.get_args_from_dict(encode_task.general_settings.ffmpeg_args))

    @staticmethod
    def _add_trim_duration_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the trim duration args to the list of ffmpeg args.
        if encode_task.trim_settings:
            ffmpeg_args.append('-to')
            ffmpeg_args.append(encode_task.trim_settings.ffmpeg_args['-to'])

    @staticmethod
    def _add_vsync_args(encode_task: task.Encode, ffmpeg_args: list):
        # Adds the vsync args to the list of ffmpeg args for an encoding task chunk.
        if isinstance(encode_task, task.VideoChunk):
            ffmpeg_args.extend(VSYNC_ARGS)

    @staticmethod
    def _add_output_file_args(encode_task: task.Encode, ffmpeg_args: list, is_cli_args_enabled: bool):
        # Uses the given encoding task to add the output file args to the list of ffmpeg args.
        if encode_task.is_using_temp_file:
            output_file = encode_task.temp_file
        else:
            output_file = encode_task.output_file

        if is_cli_args_enabled:
            ffmpeg_args.append(''.join(['\"', output_file.file_path, '\"']))
        else:
            ffmpeg_args.append(output_file.file_path)

    @staticmethod
    def _add_2_pass_args(encode_task: task.Encode, ffmpeg_args: list):
        # Uses the given encoding task to add the necessary settings for a 2-pass encode to the list of ffmpeg args.
        if video_codec.is_codec_2_pass(encode_task.get_video_codec()) \
                and encode_task.get_video_codec().encode_pass == 1:
            encode_task_copy = encode_task.get_copy()
            encode_task_copy.get_video_codec().encode_pass = 2

            return [ffmpeg_args, Args.get_args(encode_task_copy)[0]]
        return [ffmpeg_args]

    @staticmethod
    def get_args_from_dict(ffmpeg_args: dict):
        """
        Takes a dictionary containing ffmpeg args and returns a list containing those args.

        Returns:
            List of ffmpeg args based on the given dictionary of ffmpeg args.
        """
        args = []

        for setting, arg in ffmpeg_args.items():
            if arg is None or setting == '-map':
                continue

            args.append(setting)
            args.append(arg)

        return args


class Compatibility:
    """Class that checks for Nvenc and Nvdec compatibility with the system that's running the application."""
    _nvenc_supported = None
    _nvdec_supported = None
    _npp_supported = None

    @staticmethod
    def is_nvenc_supported() -> bool:
        """
        Returns whether Nvenc is supported on the system that's running the application.

        Returns:
            Boolean that represents whether Nvenc is supported.
        """
        if Compatibility._nvenc_supported is None:
            Compatibility._nvenc_supported = Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

            if Compatibility._nvenc_supported:
                video_codec.VIDEO_CODECS_MP4_UI.extend(['NVENC H264', 'NVENC H265'])
                video_codec.VIDEO_CODECS_MKV_UI.extend(['NVENC H264', 'NVENC H265'])
                video_codec.VIDEO_CODECS_TS_UI.extend(['NVENC H264', 'NVENC H265'])

        return Compatibility._nvenc_supported

    @staticmethod
    def run_test_process(test_process_args: list, counter=None) -> bool:  # Unused parameter necessary for this function
        """
        Runs subprocess.Popen using the given list of arguments. Used to test if the given arguments will result in a
        successful run of subprocess.Popen.

        Parameters:
            test_process_args: List of Strings that represent the args to pass into subprocess.Popen.
            counter: (Default: None) Variable passed in from ThreadPoolExecutor.

        Returns:
            Boolean that represents whether subprocess.Popen had a successful return code.
        """
        with subprocess.Popen(test_process_args,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT) as test_process:
            return test_process.wait() == 0

    @staticmethod
    def get_nvenc_test_args() -> list:
        """
        Returns a list of Strings that represent the arguments for running ffmpeg to test the H264 Nvenc codec.

        Returns:
            List of Strings that represent the arguments for running ffmpeg using the H264 Nvenc codec.
        """
        nvenc_test_args = FFMPEG_INIT_ARGS.copy()
        nvenc_test_args.append('-f')
        nvenc_test_args.append('lavfi')
        nvenc_test_args.append('-i')
        nvenc_test_args.append('nullsrc=s=256x256:d=5')
        nvenc_test_args.append('-c:v')
        nvenc_test_args.append('h264_nvenc')
        nvenc_test_args.append('-f')
        nvenc_test_args.append('null')
        nvenc_test_args.append('-')

        return nvenc_test_args

    @staticmethod
    def is_video_codec_compatible(nvenc_video_codec: video_codec.HevcNvenc | video_codec.HevcNvenc) -> bool:
        """
        Returns whether the given encoding task will run successfully with its current settings.

        Returns:
            Boolean that represents whether the given encoding task will run successfully.
        """
        nvenc_test_args = FFMPEG_INIT_ARGS.copy()
        nvenc_test_args.append('-f')
        nvenc_test_args.append('lavfi')
        nvenc_test_args.append('-i')
        nvenc_test_args.append('nullsrc=s=256x256:d=5')
        nvenc_test_args.extend(Args.get_args_from_dict(nvenc_video_codec.ffmpeg_args))
        nvenc_test_args.extend(Args.get_args_from_dict(nvenc_video_codec.get_ffmpeg_advanced_args()))
        nvenc_test_args.append('-f')
        nvenc_test_args.append('null')
        nvenc_test_args.append('-')

        return Compatibility.run_test_process(nvenc_test_args)

    @staticmethod
    def is_nvdec_supported() -> bool:
        """
        Returns whether Nvdec is supported on the system running the application.

        Returns:
            Boolean that represents whether Nvdec is supported.
        """
        if Compatibility._nvdec_supported is None:
            Compatibility._nvdec_supported = Compatibility._run_nvdec_test_process()

        return Compatibility._nvdec_supported

    @staticmethod
    def _run_nvdec_test_process() -> bool:
        # Returns whether cuvid was found in ffmpeg's list of decoders.
        is_nvdec_found = False

        with subprocess.Popen(Compatibility._get_list_decoders_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as nvdec_test_process:
            while True:
                stdout = nvdec_test_process.stdout.readline().strip()

                if stdout == '' and nvdec_test_process.poll() is not None:
                    break

                if 'cuvid' in stdout:
                    is_nvdec_found = True

                    break

        return is_nvdec_found

    @staticmethod
    def _get_list_decoders_args() -> list:
        # Returns a list of Strings that represent the args that will show ffmpeg's available decoders.
        list_decoders_process_args = FFMPEG_INIT_ARGS.copy()
        list_decoders_process_args.append('-decoders')

        return list_decoders_process_args

    @staticmethod
    def is_npp_supported() -> bool:
        """
        Returns whether NPP is supported on the system running this application.

        Returns:
            Boolean that represents whether NPP is supported.
        """
        if Compatibility._npp_supported is None:
            Compatibility._npp_supported = Compatibility._run_npp_test_process()

        return Compatibility._npp_supported

    @staticmethod
    def _run_npp_test_process() -> bool:
        # Returns whether NPP was found in ffmpeg's list of filters.
        is_npp_found = False

        with subprocess.Popen(Compatibility._get_npp_test_args(),
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              bufsize=1) as npp_test_process:
            while True:
                stdout = npp_test_process.stdout.readline().strip()

                if stdout == '' and npp_test_process.poll() is not None:
                    break

                if 'npp' in stdout:
                    is_npp_found = True

                    break

        return is_npp_found

    @staticmethod
    def _get_npp_test_args() -> list:
        # Returns a list of Strings that represent the args that will show ffmpeg's available filters.
        npp_test_args = FFMPEG_INIT_ARGS.copy()
        npp_test_args.append('-filters')

        return npp_test_args

    @staticmethod
    def is_nvenc_available() -> bool:
        """
        Returns whether the system running this application can run another process that's utilizing Nvenc.

        Returns:
            Boolean that represents whether the system that's running this application can run another process
            that's utilizing Nvenc.
        """
        return Compatibility.run_test_process(Compatibility.get_nvenc_test_args())

    @staticmethod
    def wait_until_nvenc_available():
        """
        Suspends the calling thread until the system that's running this application is able to run
        a process that's utilizing Nvenc.
        """
        while True:
            if Compatibility.is_nvenc_available():
                break
            else:
                time.sleep(3)


class Parallel:
    """Class that contains functions for setting up an encoding task for parallel encoding."""

    MIN_CHUNK_LENGTH_SECONDS = 10

    MAX_NVENC_WORKERS = 16
    nvenc_max_workers = 1

    @staticmethod
    def get_task_chunks(encode_task: task.Encode,
                        app_settings: app_preferences.Settings) -> tuple[task.VideoChunk | task.AudioChunk] | None:
        """
        Returns a tuple containing encoding tasks that are chunks of the given encoding task. Returns None if
        chunking is not possible for the given encoding task.

        Returns:
            Tuple containing encoding tasks that are chunks of the given encoding task. Or None if
            chunking is not possible.
        """
        number_of_chunks = Parallel._get_number_of_chunks(encode_task, app_settings)

        if Parallel._is_task_chunkable(encode_task, number_of_chunks):
            return Parallel._get_task_chunks(encode_task, number_of_chunks)
        return None

    @staticmethod
    def _get_number_of_chunks(encode_task: task.Encode, app_settings: app_preferences.Settings) -> int:
        # Returns the number of encoding task chunks to generate from the given encoding task.
        if video_codec.is_codec_nvenc(encode_task.get_video_codec()):
            return Parallel.nvenc_max_workers
        return Parallel._get_per_codec_number_of_chunks(encode_task, app_settings)

    @staticmethod
    def _get_per_codec_number_of_chunks(encode_task: task.Encode, app_settings: app_preferences.Settings) -> int:
        # Returns the number of encoding task chunks to generate depending on which video codec the task is using.
        if video_codec.is_codec_x264(encode_task.get_video_codec()):
            return app_settings.per_codec_x264

        if video_codec.is_codec_x265(encode_task.get_video_codec()):
            return app_settings.per_codec_x265

        if video_codec.is_codec_vp9(encode_task.get_video_codec()):
            return app_settings.per_codec_vp9
        return 1

    @staticmethod
    def _is_task_chunkable(encode_task: task.Encode, number_of_chunks: int) -> bool:
        # Returns a boolean representing whether it's possible to generate chunks from the given encoding task.
        if video_codec.is_codec_copy(encode_task.get_video_codec()) or encode_task.is_no_video:
            return False

        if encode_task.trim_settings and not audio_codec.is_copy_codec_in_audio_streams(encode_task.audio_streams):
            if (encode_task.trim_settings.trim_duration / number_of_chunks) >= Parallel.MIN_CHUNK_LENGTH_SECONDS:
                return True
        elif (encode_task.input_file.duration / number_of_chunks) >= Parallel.MIN_CHUNK_LENGTH_SECONDS:
            return True
        return False

    @staticmethod
    def _get_task_chunks(encode_task: task.Encode, number_of_chunks: int) -> tuple[task.VideoChunk | task.AudioChunk]:
        # Generates the given number of encoding task chunks from the given encoding task.
        task_chunks = []

        for index in range(1, (number_of_chunks + 1)):
            task_chunks.append(task.VideoChunk(encode_task, number_of_chunks, index))
        task_chunks.append(task.AudioChunk(encode_task))

        return tuple(task_chunks)

    @staticmethod
    def concatenate_video_task_chunks(chunk_tasks: tuple[task.VideoChunk | task.AudioChunk],
                                      encode_task: task.Encode):
        """
        Takes the given tuple of encoding task chunks and runs a subprocess to concatenate them into
        a single video file that has the same settings as the given encoding task.

        Parameters:
            chunk_tasks: Tuple that contains the encoding task chunks.
            encode_task: Original encoding task that the task chunks are based off of.

        Returns:
            None
        """
        chunk_list_file_path = ''.join([encode_task.temp_file.dir,
                                        '/',
                                        encode_task.temp_file.name,
                                        '_concat'])
        concatenation_args = Parallel._get_video_concatenation_args(chunk_tasks)

        if Parallel._write_concatenation_args(encode_task, chunk_list_file_path, concatenation_args):
            concatenation_process_args = Parallel._get_concatenation_process_args(encode_task, chunk_list_file_path)
            run_process_args(encode_task, concatenation_process_args)

    @staticmethod
    def _get_video_concatenation_args(chunk_tasks: tuple[task.VideoChunk | task.AudioChunk]) -> list:
        # Returns a list of strings that represent the concatenation args that ffmpeg will use.
        concatenation_args = []

        for chunk_task in chunk_tasks:
            if chunk_task.encode_task.is_no_video:
                continue

            concatenation_args.append(''.join(['file \'',
                                               chunk_task.encode_task.temp_file.name,
                                               chunk_task.encode_task.temp_file.extension,
                                               '\'\n']))

        return concatenation_args

    @staticmethod
    def _write_concatenation_args(encode_task: task.Encode,
                                  chunk_list_file_path: str,
                                  concatenation_args: list) -> bool:
        # Writes the given concatenation args to a file at the given chunk list file path.
        try:
            with open(chunk_list_file_path, 'w') as concatenation_file:
                concatenation_file.writelines(concatenation_args)

            return True
        except OSError:
            logger.log_video_chunk_concatenation_error(encode_task.input_file.name)

            return False

    @staticmethod
    def _get_concatenation_process_args(encode_task: task.Encode, chunk_list_file_path: str) -> list:
        # Returns a list of ffmpeg arguments that will concatenate the encoding task chunks.
        process_args = FFMPEG_CONCATENATION_INIT_ARGS.copy()
        process_args.append(chunk_list_file_path)
        process_args.append('-c')
        process_args.append('copy')
        process_args.append(''.join([encode_task.temp_file.dir,
                                     '/',
                                     encode_task.output_file.name,
                                     encode_task.output_file.extension]))

        return process_args

    @staticmethod
    def mux_chunks(chunk_tasks: tuple[task.VideoChunk | task.AudioChunk],
                   encode_task: task.Encode,
                   app_settings: app_preferences.Settings):
        """
        Runs a subprocess that uses ffmpeg to mux the concatenated encoding task chunks and the
        encoding task audio chunk into a single video file.

        Parameters:
            chunk_tasks: Tuple containing the encoding task chunks.
            encode_task: Original encoding task that the encoding task chunks are based off of.
            app_settings: Application settings.

        Returns:
            None
        """
        mux_chunks_process_args = Parallel._get_mux_chunks_process_args(chunk_tasks, encode_task, app_settings)
        run_process_args(encode_task, mux_chunks_process_args)

    @staticmethod
    def _get_mux_chunks_process_args(chunk_tasks: tuple[task.VideoChunk | task.AudioChunk],
                                     encode_task: task.Encode,
                                     app_settings: app_preferences.Settings) -> list:
        # Returns a list of subprocess arguments to mux the chunked files using ffmpeg.
        audio_chunk_task = chunk_tasks[-1]

        mux_chunks_process_args = FFMPEG_INIT_ARGS.copy()
        mux_chunks_process_args.append('-i')
        mux_chunks_process_args.append(''.join([app_settings.temp_directory,
                                                '/',
                                                encode_task.output_file.name,
                                                encode_task.output_file.extension]))
        mux_chunks_process_args.append('-i')
        mux_chunks_process_args.append(''.join([app_settings.temp_directory,
                                                '/',
                                                audio_chunk_task.output_file.name,
                                                audio_chunk_task.output_file.extension]))
        mux_chunks_process_args.append('-c')
        mux_chunks_process_args.append('copy')
        mux_chunks_process_args.append(encode_task.output_file.file_path)

        return mux_chunks_process_args

    @staticmethod
    def setup_nvenc_max_workers(app_settings: app_preferences.Settings):
        """
        Sets the maximum number of Nvenc workers that can run simultaneously when parallel encoding is enabled.

        Parameters:
            app_settings: Application's settings.
        """
        if app_settings.parallel_nvenc_workers:
            Parallel.nvenc_max_workers = app_settings.parallel_nvenc_workers

            logger.log_nvenc_max_workers_set(Parallel.nvenc_max_workers)
        else:
            Parallel._test_nvenc_max_workers()

    @staticmethod
    def _test_nvenc_max_workers():
        # Runs multiple Nvenc processes simultaneously until it fails or reaches the global max amount of workers.
        counter = 1

        while True:
            with ThreadPoolExecutor(max_workers=counter) as future_executor:
                results = future_executor.map(Compatibility.run_test_process,
                                              repeat(Compatibility.get_nvenc_test_args()),
                                              range(counter))

                if counter > Parallel.MAX_NVENC_WORKERS or Parallel._has_future_executor_results_failed(results):
                    Parallel.nvenc_max_workers = counter - 1

                    logger.log_nvenc_max_workers_set(Parallel.nvenc_max_workers)

                    break

            counter += 1

    @staticmethod
    def _has_future_executor_results_failed(results) -> bool:
        # Returns whether the ThreadPoolExecutor results have failed.
        for result in results:
            if not result:
                return True
        return False
