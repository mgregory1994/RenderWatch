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


VIDEO_CODECS_MP4_UI = ['copy', 'H264', 'H265']
VIDEO_CODECS_MKV_UI = ['copy', 'H264', 'H265', 'VP9']
VIDEO_CODECS_TS_UI = ['copy', 'H264']
VIDEO_CODECS_WEBM_UI = ('copy', 'VP9')


def is_codec_copy(video_codec) -> bool:
    """
    Returns whether the given video codec is a Copy codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is a Copy codec.
    """
    return isinstance(video_codec, Copy)


def is_codec_2_pass(video_codec) -> bool:
    """
    Returns whether the given video codec is set up for 2-pass encoding.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is set up for 2-pass encoding.
    """
    if not is_codec_copy(video_codec) and video_codec.encode_pass is not None:
        return 1 <= video_codec.encode_pass <= 2
    return False


def is_codec_x264(video_codec) -> bool:
    """
    Returns whether the given video codec is an X264 codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is an X264 codec.
    """
    return isinstance(video_codec, X264)


def is_codec_x265(video_codec) -> bool:
    """
    Returns whether the given video codec is an X265 codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is an X265 codec.
    """
    return isinstance(video_codec, X265)


def is_codec_h264_nvenc(video_codec) -> bool:
    """
    Returns whether the given video codec is a H264 Nvenc codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is a H264 Nvenc codec.
    """
    return isinstance(video_codec, H264Nvenc)


def is_codec_hevc_nvenc(video_codec) -> bool:
    """
    Returns whether the given video codec is a Hevc Nvenc codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is a Hevc Nvenc codec.
    """
    return isinstance(video_codec, HevcNvenc)


def is_codec_nvenc(video_codec) -> bool:
    """
    Returns whether the given video codec is a Nvenc codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is a Nvenc codec.
    """
    return is_codec_h264_nvenc(video_codec) or is_codec_hevc_nvenc(video_codec)


def is_codec_vp9(video_codec) -> bool:
    """
    Returns whether the given video codec is a VP9 codec.

    Parameters:
        video_codec: Video codec to check.

    Returns:
        Boolean that represents whether the given video codec is a VP9 codec.
    """
    return isinstance(video_codec, VP9)


class Copy:
    """Class that configures all Copy codec settings available for Render Watch."""

    def __init__(self):
        """Initializes the Copy class with all necessary variables for the codec's options."""
        self.ffmpeg_args = {
            '-c:v': 'copy',
        }
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self) -> str:
        return self.ffmpeg_args['-c:v']


class X264:
    """Class that configures all X264 codec settings available for Render Watch."""

    PROFILE = ('auto', 'baseline', 'main', 'high', 'high10')
    PROFILE_LENGTH = len(PROFILE)

    PRESET = ('auto', 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'slow', 'slower', 'veryslow')
    PRESET_LENGTH = len(PRESET)

    TUNE = ('auto', 'film', 'animation', 'grain', 'stillimage', 'psnr', 'ssim', 'fastdecode', 'zerolatency')
    TUNE_LENGTH = len(TUNE)

    LEVEL = (
        'auto', '1', '1.1', '1.2', '1.3', '2', '2.1', '2.2',
        '3', '3.1', '3.2', '4', '4.1', '4.2', '5', '5.1'
    )
    LEVEL_LENGTH = len(LEVEL)

    AQ_MODE = ('auto', '0', '1', '2', '3')
    AQ_MODE_UI = ('auto', 'none', 'across frames', 'auto varaince', 'auto variance (dark)')
    AQ_MODE_LENGTH = len(AQ_MODE)

    B_ADAPT = ('auto', '0', '1', '2')
    B_ADAPT_UI = ('auto', 'off', 'fast', 'optimal')
    B_ADAPT_LENGTH = len(B_ADAPT)

    B_PYRAMID = ('auto', '1', '2')
    B_PYRAMID_UI = ('auto', 'strict', 'normal')
    B_PYRAMID_LENGTH = len(B_PYRAMID)

    WEIGHT_P = ('auto', '0', '1', '2')
    WEIGHT_P_UI = ('auto', 'off', 'simple', 'smart')
    WEIGHT_P_LENGTH = len(WEIGHT_P)

    ME = ('auto', 'dia', 'hex', 'umh', 'esa', 'tesa')
    ME_LENGTH = len(ME)

    SUB_ME = ('auto', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
    SUB_ME_UI = (
        'auto', '1:QPel SAD', '2:QPel SATD', '3:HPel on MB', '4:Always QPel',
        '5:Multi QPel', '6:RD I/P Frames', '7:RD All Frames', '8:RD Refine I/P Frames',
        '9:RD Refine Frames', '10:QP-RD'
    )
    SUB_ME_LENGTH = len(SUB_ME)

    TRELLIS = ('auto', '0', '1', '2')
    TRELLIS_UI = ('auto', 'off', 'encode only', 'always')
    TRELLIST_LENGTH = len(TRELLIS)

    DIRECT = ('auto', '0', '1', '2')
    DIRECT_UI = ('auto', 'none', 'spatial', 'temporal')
    DIRECT_LENGTH = len(DIRECT)

    CRF_MIN = 0.0
    CRF_MAX = 51.0
    CRF_DEFAULT = 23.0

    QP_MIN = 0.0
    QP_MAX = 51.0

    BITRATE_MIN = 0
    BITRATE_MAX = 99999

    KEYINT_MIN = 10
    KEYINT_MAX = 990

    SCENECUT_MIN = 10
    SCENECUT_MAX = 990

    B_FRAMES_MIN = 0
    B_FRAMES_MAX = 16

    REF_MIN = 0
    REF_MAX = 16

    DEBLOCK_MIN = -9
    DEBLOCK_MAX = 9

    AQ_STRENGTH_MIN = 0.0
    AQ_STRENGTH_MAX = 2.0

    ME_RANGE_MIN = 4
    ME_RANGE_MAX = 64

    PSYRD_MIN = 0.0
    PSYRD_MAX = 2.0

    PSYRD_TRELLIS_MIN = 0.0
    PSYRD_TRELLIS_MAX = 1.0

    def __init__(self):
        """Initializes the X264 class with all necessary variables for the codec's options."""
        self.is_advanced_enabled = False
        self._is_crf_enabled = True
        self._is_qp_enabled = False
        self._is_bitrate_enabled = False
        self.ffmpeg_args = {
            '-c:v': 'libx264',
            '-crf': str(self.CRF_DEFAULT)
        }
        self._ffmpeg_advanced_args = {}

    @property
    def is_crf_enabled(self) -> bool:
        """
        Returns whether CRF is enabled for the rate type settings.

        Returns:
            Boolean that represents whether CRF is enabled for the rate type settings.
        """
        return self._is_crf_enabled

    @property
    def is_qp_enabled(self) -> bool:
        """
        Returns whether QP is enabled for the rate type settings.

        Returns:
            Boolean that represents whether QP is enabled for the rate type settings.
        """
        return self._is_qp_enabled

    @property
    def is_bitrate_enabled(self) -> bool:
        """
        Returns whether bitrate is enabled for the rate type settings.

        Returns:
            Boolean that represents whether bitrate is enabled for the rate type settings.
        """
        return self._is_bitrate_enabled

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self) -> float:
        """
        Returns the value of the CRF setting.

        Returns:
            CRF setting as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return self.CRF_DEFAULT

    @crf.setter
    def crf(self, crf_value: float | None):
        """
        Sets the CRF setting to the specified value.

        Parameters:
            crf_value: The value to use for the CRF setting.

        Returns:
            None
        """
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)
            self.qp = None
            self.bitrate = None
            self._is_crf_enabled = True
            self._is_qp_enabled = False
            self._is_bitrate_enabled = False

    @property
    def qp(self) -> float:
        """
        Returns the value of the QP setting.

        Returns:
            QP setting as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return self.CRF_DEFAULT

    @qp.setter
    def qp(self, qp_value: float | None):
        """
        Sets the QP setting to the specified value.

        Parameters:
            qp_value: The value to use for the QP setting.

        Returns:
            None
        """
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.crf = None
            self.bitrate = None
            self._is_crf_enabled = False
            self._is_qp_enabled = True
            self._is_bitrate_enabled = False

    @property
    def bitrate(self) -> int:
        """
        Returns the value of the bitrate setting.

        Returns:
            Bitrate setting as an integer.
        """
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']

            return int(bitrate_arg.split('k')[0])
        return 2500

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate setting to the specified value.

        Parameters:
            bitrate_value: The value to use for the bitrate setting.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.crf = None
            self.qp = None
            self._is_crf_enabled = False
            self._is_qp_enabled = False
            self._is_bitrate_enabled = True

    @property
    def profile(self) -> int:
        """
        Returns the index of the profile setting.

        Returns:
            Profile setting as an index using the PROFILE variable.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']

            return self.PROFILE.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            profile_index: Index from the PROFILE variable.

        Returns:
            None
        """
        if profile_index and 0 < profile_index < X264.PROFILE_LENGTH:
            self.ffmpeg_args['-profile:v'] = self.PROFILE[profile_index]
        else:
            self.ffmpeg_args.pop('-profile:v', 0)

    @property
    def preset(self) -> int:
        """
        Returns the index of the preset setting.

        Returns:
            Preset setting as an index using the PRESET variable.
        """
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            preset_index: Index from the PRESET variable.

        Returns:
            None
        """
        if preset_index and 0 < preset_index < X264.PRESET_LENGTH:
            self.ffmpeg_args['-preset'] = self.PRESET[preset_index]
        else:
            self.ffmpeg_args.pop('-preset', 0)

    @property
    def level(self) -> int:
        """
        Returns the index of the level setting.

        Returns:
            Level setting as an index using the LEVEL variable.
        """
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']

            return self.LEVEL.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index: int | None):
        """
        Sets the level setting to the specified index.

        Parameters:
            level_index: Index from the LEVEL variable.

        Returns:
            None
        """
        if level_index and 0 < level_index < X264.LEVEL_LENGTH:
            self.ffmpeg_args['-level'] = self.LEVEL[level_index]
        else:
            self.ffmpeg_args.pop('-level', 0)

    @property
    def tune(self) -> int:
        """
        Returns the index of the tune setting.

        Returns:
            Tune setting as an index using the TUNE variable.
        """
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']

            return self.TUNE.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index: int | None):
        """
        Sets the tune setting to the specified index.

        Parameters:
            tune_index: Index from the TUNE variable.

        Returns:
            None
        """
        if tune_index and 0 < tune_index < X264.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def keyint(self) -> int:
        """
        Returns the value of the keyframe interval setting.

        Returns:
            Keyframe Interval setting as an integer.
        """
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value: int | None):
        """
        Sets the keyframe interval setting to the specified value.

        Parameters:
            keyint_value: The value to use for the keyframe interval setting.

        Returns:
            None
        """
        if keyint_value is None:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint_value)

    @property
    def min_keyint(self) -> int:
        """
        Returns the value of the minimum keyframe interval setting.

        Returns:
            Minimum keyframe interval setting as an integer.
        """
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 25

    @min_keyint.setter
    def min_keyint(self, min_keyint_value: int | None):
        """
        Sets the minimum keyframe interval setting to the specified value.

        Parameters:
            min_keyint_value: The value to use for the minimum keyframe interval setting.

        Returns:
            None
        """
        if min_keyint_value is None:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def scenecut(self) -> int:
        """
        Returns the value of the scenecut setting.

        Returns:
            Scenecut setting as an integer.
        """
        if 'scenecut=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['scenecut='])
        return 40

    @scenecut.setter
    def scenecut(self, scenecut_value: int | None):
        """
        Sets the scenecut setting to the specified value.

        Parameters:
            scenecut_value: The value to use for the scenecut setting.

        Returns:
            None
        """
        if scenecut_value is None:
            self._ffmpeg_advanced_args.pop('scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['scenecut='] = str(scenecut_value)

    @property
    def bframes(self) -> int:
        """
        Returns the value of the B Frames setting.

        Returns:
            B Frames setting as an integer.
        """
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 3

    @bframes.setter
    def bframes(self, bframes_value: int | None):
        """
        Sets the B Frames setting to the specified value.

        Parameters:
            bframes_value: The value to use for the B Frames setting.

        Returns:
            None
        """
        if bframes_value is None:
            self._ffmpeg_advanced_args.pop('bframes=', 0)
        else:
            self._ffmpeg_advanced_args['bframes='] = str(bframes_value)

    @property
    def b_adapt(self) -> int:
        """
        Returns the index of the B Adapt setting.

        Returns:
            B Adapt setting as an index using the B_ADAPT variable.
        """
        if 'b-adapt=' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['b-adapt=']

            return self.B_ADAPT.index(b_adapt_arg)
        return 0

    @b_adapt.setter
    def b_adapt(self, b_adapt_index: int | None):
        """
        Sets the B adapt setting to the specified index.

        Parameters:
            b_adapt_index: Index from the B_ADAPT variable.

        Returns:
            None
        """
        if b_adapt_index and 0 < b_adapt_index < X264.B_ADAPT_LENGTH:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT[b_adapt_index]
        else:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)

    @property
    def b_pyramid(self) -> int:
        """
        Returns the index of the B Pyramid setting.

        Returns:
            B Pyramid setting as an index using the B_PYRAMID variable.
        """
        if 'b-pyramid=' in self._ffmpeg_advanced_args:
            b_pyramid_arg = self._ffmpeg_advanced_args['b-pyramid=']

            return self.B_PYRAMID.index(b_pyramid_arg)
        return 0

    @b_pyramid.setter
    def b_pyramid(self, b_pyramid_index: int | None):
        """
        Sets the B pyramid setting to the specified index.

        Parameters:
            b_pyramid_index: Index from the B_PYRAMID variable.

        Returns:
            None
        """
        if b_pyramid_index and 0 < b_pyramid_index < X264.B_PYRAMID_LENGTH:
            self._ffmpeg_advanced_args['b-pyramid='] = self.B_PYRAMID[b_pyramid_index]
        else:
            self._ffmpeg_advanced_args.pop('b-pyramid=', 0)

    @property
    def no_cabac(self) -> bool:
        """
        Returns whether the no CABAC setting is enabled.

        Returns:
            Boolean that represents whether the no CABAC setting is enabled.
        """
        if 'no-cabac=' in self._ffmpeg_advanced_args:
            no_cabac_arg = self._ffmpeg_advanced_args['no-cabac=']

            return no_cabac_arg == '1'
        return False

    @no_cabac.setter
    def no_cabac(self, is_no_cabac_enabled: bool):
        """
        Sets the no CABAC setting to the specified value.

        Parameters:
            is_no_cabac_enabled: Boolean that represents whether the no CABAC setting is enabled.

        Returns:
            None
        """
        if is_no_cabac_enabled:
            self._ffmpeg_advanced_args['no-cabac='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-cabac=', 0)

    @property
    def ref(self) -> int:
        """
        Returns the value of the reference frames setting.

        Returns:
            Reference frames setting as an integer.
        """
        if 'ref=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['ref='])
        return 3

    @ref.setter
    def ref(self, ref_value: int | None):
        """
        Sets the reference frames setting to the specified value.

        Parameters:
            ref_value: The value to use for the reference frames setting.

        Returns:
            None
        """
        if ref_value is None:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref_value)

    @property
    def no_deblock(self) -> bool:
        """
        Returns whether the no deblock setting is enabled.

        Returns:
            Boolean that represents whether the no deblock setting is enabled.
        """
        if 'no-deblock=' in self._ffmpeg_advanced_args:
            no_deblock_arg = self._ffmpeg_advanced_args['no-deblock=']

            return no_deblock_arg == '1'
        return False

    @no_deblock.setter
    def no_deblock(self, is_no_deblock_enabled: bool):
        """
        Sets the no deblock setting to the specified value.

        Parameters:
            is_no_deblock_enabled: Boolean that represents whether the no deblock setting is enabled.

        Returns:
            None
        """
        if is_no_deblock_enabled:
            self._ffmpeg_advanced_args['no-deblock='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-deblock=', 0)

    @property
    def deblock(self) -> tuple:
        """
        Returns the values for the deblock setting.

        Returns:
            Tuple that represents the Alpha and Beta values for the deblock setting.
        """
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')

            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock_tuple: tuple | None):
        """
        Sets the deblock setting to the specified values.

        Parameters:
            deblock_tuple: Tuple that contains the alpha and beta values for the deblock setting.

        Returns:
            None
        """
        if deblock_tuple is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock_tuple
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def vbv_maxrate(self) -> int:
        """
        Returns the value for the vbv maxrate setting.

        Returns:
            Vbv maxrate setting as an integer.
        """
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value: int | None):
        """
        Sets the vbv maxrate setting to the specified value.

        Parameters:
            vbv_maxrate_value: Value to use for the vbv maxrate setting.

        Returns:
            None
        """
        if vbv_maxrate_value is None or not self.is_vbv_valid():
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)

    @property
    def vbv_bufsize(self) -> int:
        """
        Returns the value for the vbv bufsize setting.

        Returns:
            Vbv bufsize setting as an integer.
        """
        if 'vbv-bufsize=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-bufsize='])
        return 2500

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize_value: int | None):
        """
        Sets the vbv bufsize setting to the specified value.

        Parameters:
            vbv_bufsize_value: Value to use for the vbv bufsize setting.

        Returns:
            None
        """
        if vbv_bufsize_value is None or not self.is_vbv_valid():
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    def is_vbv_valid(self) -> bool:
        """
        Returns whether VBV is able to be used and is enabled.

        Returns:
            Boolean that represents whether VBV is valid and enabled.
        """
        if self.is_advanced_enabled:
            return self.is_bitrate_enabled and not self.constant_bitrate
        return False

    @property
    def aq_mode(self) -> int:
        """
        Returns the index of the AQ mode setting.

        Returns:
            AQ mode setting as an index using the AQ_MODE variable.
        """
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_value = self._ffmpeg_advanced_args['aq-mode=']

            return self.AQ_MODE.index(aq_mode_value)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index: int | None):
        """
        Sets the AQ mode setting to the specified index.

        Parameters:
            aq_mode_index: Index from the AQ_MODE variable.

        Returns:
            None
        """
        if aq_mode_index and 0 < aq_mode_index < X264.AQ_MODE_LENGTH:
            self._ffmpeg_advanced_args['aq-mode='] = self.AQ_MODE[aq_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('aq-mode=', 0)

    @property
    def aq_strength(self) -> float:
        """
        Returns the value of the AQ strength setting.

        Returns:
            AQ strength setting as a float.
        """
        if 'aq-strength=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['aq-strength='])
        return 1.0

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: float | None):
        """
        Sets the AQ strength setting to the specified value.

        Parameters:
            aq_strength_value: The value to use for the AQ strength setting.

        Returns:
            None
        """
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(round(aq_strength_value, 1))

    @property
    def encode_pass(self) -> int | None:
        """
        Returns the value of the encode pass setting.

        Returns:
            Encode pass as an integer.
        """
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        """
        Sets the encode pass setting to the specified value.

        Parameters:
            encode_pass_value: Current encode pass to use.

        Returns:
            None
        """
        if encode_pass_value is None:
            self._ffmpeg_advanced_args.pop('pass=', 0)
        else:
            self._ffmpeg_advanced_args['pass='] = str(encode_pass_value)

    @property
    def stats(self) -> str:
        """
        Returns the value of the stats setting.

        Returns:
            Stats setting as a string that represents the file path to use for the stats file.
        """
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        """
        Sets the stats setting to the specified value.

        Parameters:
            stats_file_path: String that represents the file path to use for the stats file.

        Returns:
            None
        """
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    @property
    def partitions(self) -> tuple | str:
        """
        Returns the value(s) for the partitions setting.

        Returns:
            Tuple that contains strings that represent the partitions that are being used or a string that represents
            all or none.
        """
        if 'partitions=' in self._ffmpeg_advanced_args:
            partitions_arg = self._ffmpeg_advanced_args['partitions=']

            if partitions_arg == 'all' or partitions_arg == 'none':
                return partitions_arg

            return partitions_arg.split(',')
        return ()

    @partitions.setter
    def partitions(self, partitions_tuple: tuple | str | None):
        """
        Sets the partitions setting to the specified value(s).

        Parameters:
            partitions_tuple: Tuple that contains strings that represent the partitions that are being used or a
            string that represents all or none.

        Returns:
            None
        """
        if partitions_tuple is None:
            self._ffmpeg_advanced_args.pop('partitions=', 0)
        elif partitions_tuple == 'all' or partitions_tuple == 'none':
            self._ffmpeg_advanced_args['partitions='] = partitions_tuple
        else:
            partition_arg = ''

            for index, partition_value in enumerate(partitions_tuple):
                partition_arg += partition_value

                if index != (len(partitions_tuple) - 1):
                    partition_arg += ','

            self._ffmpeg_advanced_args['partitions='] = partition_arg

    @property
    def direct(self) -> int:
        """
        Returns the index of the direct setting.

        Returns:
            Direct setting as an index using the DIRECT variable.
        """
        if 'direct=' in self._ffmpeg_advanced_args:
            direct_arg = self._ffmpeg_advanced_args['direct=']

            return self.DIRECT.index(direct_arg)
        return 0

    @direct.setter
    def direct(self, direct_index: int | None):
        """
        Sets the direct setting to the specified index.

        Parameters:
            direct_index: Index from the DIRECT variable.

        Returns:
            None
        """
        if direct_index and 0 < direct_index < X264.DIRECT_LENGTH:
            self._ffmpeg_advanced_args['direct='] = self.DIRECT[direct_index]
        else:
            self._ffmpeg_advanced_args.pop('direct=', 0)

    @property
    def weightb(self) -> bool:
        """
        Returns whether the weight B setting is enabled.

        Returns:
            Boolean that represents whether the weight B setting is enabled.
        """
        if 'weightb=' in self._ffmpeg_advanced_args:
            weightb_arg = self._ffmpeg_advanced_args['weightb=']

            return weightb_arg == '1'
        return False

    @weightb.setter
    def weightb(self, is_weightb_enabled: bool):
        """
        Sets the weight B setting to the specified value.

        Parameters:
            is_weightb_enabled: Boolean that represents whether the weight B setting is enabled.

        Returns:
            None
        """
        if is_weightb_enabled:
            self._ffmpeg_advanced_args['weightb='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('weightb=', 0)

    @property
    def me(self) -> int:
        """
        Returns the index of the motion estimation setting.

        Returns:
            Motion estimation setting as an index using the ME variable.
        """
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']

            return self.ME.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index: int | None):
        """
        Sets the motion estimation setting to the specified index.

        Parameters:
            me_index: Index from the ME variable.

        Returns:
            None
        """
        if me_index and 0 < me_index < X264.ME_LENGTH:
            self._ffmpeg_advanced_args['me='] = self.ME[me_index]
        else:
            self._ffmpeg_advanced_args.pop('me=', 0)

    @property
    def me_range(self) -> int:
        """
        Returns the value of the motion estimation range setting.

        Returns:
            Motion estimation range setting as an integer.
        """
        if 'merange=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['merange='])
        return 16

    @me_range.setter
    def me_range(self, me_range_value: int | None):
        """
        Sets the motion estimation range setting to the specified value.

        Parameters:
            me_range_value: The value to use for the motion estimation range setting.

        Returns:
            None
        """
        if me_range_value is None:
            self._ffmpeg_advanced_args.pop('merange=', 0)
        else:
            self._ffmpeg_advanced_args['merange='] = str(me_range_value)

    @property
    def subme(self) -> int:
        """
        Returns the index of the sub-motion estimation setting.

        Returns:
            Sub-motion estimation setting as an index using the SUB_ME variable.
        """
        if 'subme=' in self._ffmpeg_advanced_args:
            subme_arg = self._ffmpeg_advanced_args['subme=']

            return self.SUB_ME.index(subme_arg)
        return 0

    @subme.setter
    def subme(self, subme_index: int | None):
        """
        Sets the sub-motion estimation setting to the specified index.

        Parameters:
            Index from the SUB_ME variable.

        Returns:
            None
        """
        if subme_index and 0 < subme_index < X264.SUB_ME_LENGTH:
            self._ffmpeg_advanced_args['subme='] = self.SUB_ME[subme_index]
        else:
            self._ffmpeg_advanced_args.pop('subme=', 0)

    @property
    def psy_rd(self) -> tuple:
        """
        Returns the value of the PsyRD setting.

        Returns:
            PsyRD setting as a tuple that contains the PsyRD and PsyRD Trellis values respectively.
        """
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            psy_rd_arg = self._ffmpeg_advanced_args['psy-rd=']
            psy_rd, psy_rd_trellis = psy_rd_arg.split(',')

            return float(psy_rd), float(psy_rd_trellis)
        return 1.0, 0.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_tuple: tuple | None):
        """
        Sets the PsyRD setting to the specified values.

        Parameters:
            psy_rd_tuple: Tuple that contains the PsyRD and PsyRD Trellis values respectively.

        Returns:
            None
        """
        if psy_rd_tuple is None:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            psy_rd, psy_rd_trellis = psy_rd_tuple
            self._ffmpeg_advanced_args['psy-rd='] = str(round(psy_rd, 1)) + ',' + str(round(psy_rd_trellis, 2))

    @property
    def mixed_refs(self) -> bool:
        """
        Returns whether the Mixed Reference Frames setting is enabled.

        Returns:
            Boolean that represents whether the Mixed Reference Frames setting is enabled.
        """
        if 'mixed-refs=' in self._ffmpeg_advanced_args:
            mixed_refs_arg = self._ffmpeg_advanced_args['mixed-refs=']

            return mixed_refs_arg == '1'
        return False

    @mixed_refs.setter
    def mixed_refs(self, is_mixed_refs_enabled: bool):
        """
        Sets the Mixed Reference Frames setting to the specified value.

        Parameters:
            is_mixed_refs_enabled: Boolean that represents whether the Mixed Reference Frames setting is enabled.

        Returns:
            None
        """
        if is_mixed_refs_enabled:
            self._ffmpeg_advanced_args['mixed-refs='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('mixed-refs=', 0)

    @property
    def dct8x8(self) -> bool:
        """
        Returns whether the dct8x8 setting is enabled.

        Returns:
            Boolean that represents whether the dct8x8 setting is enabled.
        """
        if '8x8dct=' in self._ffmpeg_advanced_args:
            dct_arg = self._ffmpeg_advanced_args['8x8dct=']

            return dct_arg == '1'
        return False

    @dct8x8.setter
    def dct8x8(self, is_dct8x8_enabled: bool):
        """
        Sets the dct8x8 setting to the specified value.

        Parameters:
            is_dct8x8_enabled: Boolean that represents whether the dct8x8 setting is enabled.

        Returns:
            None
        """
        if is_dct8x8_enabled:
            self._ffmpeg_advanced_args['8x8dct='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('8x8dct=', 0)

    @property
    def trellis(self) -> int:
        """
        Returns the index of the Trellis setting.

        Returns:
            Trellis setting as an index using the TRELLIS variable.
        """
        if 'trellis=' in self._ffmpeg_advanced_args:
            trellis_arg = self._ffmpeg_advanced_args['trellis=']

            return self.TRELLIS.index(trellis_arg)
        return 0

    @trellis.setter
    def trellis(self, trellis_index: int | None):
        """
        Sets the Trellis setting to the specified index.

        Parameters:
            trellis_index: Index from the TRELLIS variable.

        Returns:
            None
        """
        if trellis_index and 0 < trellis_index < X264.TRELLIST_LENGTH:
            self._ffmpeg_advanced_args['trellis='] = self.TRELLIS[trellis_index]
        else:
            self._ffmpeg_advanced_args.pop('trellis=', 0)

    @property
    def no_fast_pskip(self) -> bool:
        """
        Returns whether the No Fast P Skip setting is enabled.

        Returns:
            Boolean that represents whether the No Fast P Skip setting is enabled.
        """
        if 'no-fast-pskip=' in self._ffmpeg_advanced_args:
            no_fast_pskip_arg = self._ffmpeg_advanced_args['no-fast-pskip=']

            return no_fast_pskip_arg == '1'
        return False

    @no_fast_pskip.setter
    def no_fast_pskip(self, is_no_fast_pskip_enabled: bool):
        """
        Sets the No Fast P Skip setting to the specified value.

        Parameters:
            is_no_fast_pskip_enabled: Boolean that represents whether the No Fast P Skip setting is enabled.

        Returns:
            None
        """
        if is_no_fast_pskip_enabled:
            self._ffmpeg_advanced_args['no-fast-pskip='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-fast-pskip=', 0)

    @property
    def no_dct_decimate(self) -> bool:
        """
        Returns whether the No DCT Decimate setting is enabled.

        Returns:
            Boolean that represents whether the No DCT Decimate setting is enabled.
        """
        if 'no-dct-decimate=' in self._ffmpeg_advanced_args:
            no_dct_decimate_arg = self._ffmpeg_advanced_args['no-dct-decimate=']

            return no_dct_decimate_arg == '1'
        return False

    @no_dct_decimate.setter
    def no_dct_decimate(self, is_no_dct_decimate_enabled: bool):
        """
        Sets the No DCT Decimate setting to the specified value.

        Parameters:
            is_no_dct_decimate_enabled: Boolean that represents whether the No DCT Decimate setting is enabled.

        Returns:
            None
        """
        if is_no_dct_decimate_enabled:
            self._ffmpeg_advanced_args['no-dct-decimate='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-dct-decimate=', 0)

    @property
    def constant_bitrate(self) -> bool:
        """
        Returns whether the Constant Bitrate setting is enabled.

        Returns:
            Boolean that represents whether the Constant Bitrate setting is enabled.
        """
        if 'nal_hrd=' in self._ffmpeg_advanced_args:
            constant_bitrate_arg = self._ffmpeg_advanced_args['nal_hrd=']

            return constant_bitrate_arg == 'cbr'
        return False

    @constant_bitrate.setter
    def constant_bitrate(self, is_constant_bitrate_enabled: bool):
        """
        Sets the Constant Bitrate setting to the specified value.

        Parameters:
            is_constant_bitrate_enabled: Boolean that represents whether the Constant Bitrate setting is enabled.

        Returns:
            None
        """
        if is_constant_bitrate_enabled:
            self._ffmpeg_advanced_args['nal_hrd='] = 'cbr'
        else:
            self._ffmpeg_advanced_args.pop('nal_hrd=', 0)

    @property
    def weightp(self) -> int:
        """
        Returns the index of the Weight P setting.

        Returns:
            Weight P setting as an index using the WEIGHT_P variable.
        """
        if 'weightp=' in self._ffmpeg_advanced_args:
            weightp_arg = self._ffmpeg_advanced_args['weightp=']

            return self.WEIGHT_P.index(weightp_arg)
        return 0

    @weightp.setter
    def weightp(self, weightp_index: int | None):
        """
        Sets the Weight P setting to the specified index.

        Parameters:
            weightp_index: Index from the WEIGHT_P variable.

        Returns:
            None
        """
        if weightp_index and 0 < weightp_index < X264.WEIGHT_P_LENGTH:
            self._ffmpeg_advanced_args['weightp='] = self.WEIGHT_P[weightp_index]
        else:
            self._ffmpeg_advanced_args.pop('weightp=', 0)

    def get_ffmpeg_advanced_args(self) -> dict:
        """
        Returns the ffmpeg arguments for the x264 codec's settings.

        Returns:
            Dictionary that contains the arguments and their settings for the x264 codec.
        """
        advanced_args = {'-x264-params': None}
        args = ''

        if self.is_advanced_enabled:
            args = self._generate_advanced_args()
        else:
            if self.constant_bitrate:
                args = self._get_constant_bitrate_args()
            elif self.encode_pass:
                args = self._get_pass_args()

        if args:
            advanced_args['-x264-params'] = args

        return advanced_args

    def _get_constant_bitrate_args(self) -> str:
        # Returns the Constant Bitrate setting as a string that represents ffmpeg arguments.
        return ''.join(['nal_hrd=', str(self.constant_bitrate).lower()])

    def _get_pass_args(self) -> str:
        # Returns the Encode Pass and Stats settings as a string that represents ffmpeg arguments.
        return ''.join(['pass=', str(self.encode_pass), ':', 'stats=', self.stats])

    def _generate_advanced_args(self) -> str:
        # Returns the advanced settings for the x264 codec as a string that represents ffmpeg arguments.
        x264_advanced_args = ''

        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x264_advanced_args += ''.join([setting, arg, ':'])

        return x264_advanced_args


class X265:
    """Class that configures all X265 codec setting available for Render Watch."""

    PROFILE = ('auto', 'main', 'main10', 'main12')
    PROFILE_LENGTH = len(PROFILE)

    PRESET = ('auto', 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'slow', 'slower', 'veryslow')
    PRESET_LENGTH = len(PRESET)

    LEVEL = ('auto', '1', '2', '2.1', '3', '3.1', '4', '4.1', '5', '5.1', '5.2', '6', '6.1', '6.2', '8.5')
    LEVEL_LENGTH = len(LEVEL)

    TUNE = ('auto', 'grain', 'animation', 'zerolatency', 'fastdecode', 'psnr', 'ssim')
    TUNE_LENGTH = len(TUNE)

    AQ_MODE = ('auto', '0', '1', '2', '3', '4')
    AQ_MODE_UI = ('auto', 'disabled', 'enabled', 'variance', 'variance(dark)', 'variance(dark + edge)')
    AQ_MODE_LENGTH = len(AQ_MODE)

    B_ADAPT = ('auto', '0', '1', '2')
    B_ADAPT_UI = ('auto', 'none', 'fast', 'full(trellis)')
    B_ADAPT_LENGTH = len(B_ADAPT)

    ME = ('auto', 'dia', 'hex', 'umh', 'star', 'sea', 'full')
    ME_LENGTH = len(ME)

    RDOQ_LEVEL = ('auto', '0', '1', '2')
    RDOQ_LEVEL_UI = ('auto', 'none', 'optimal rounding', 'decimate decisions')
    RDOQ_LEVEL_LENGTH = len(RDOQ_LEVEL)

    MAX_CU_SIZE = ('auto', '64', '32', '16')
    MAX_CU_SIZE_LENGTH = len(MAX_CU_SIZE)

    MIN_CU_SIZE = ('auto', '8', '16', '32')
    MIN_CU_SIZE_LENGTH = len(MIN_CU_SIZE)

    CRF_MIN = 0.0
    CRF_MAX = 51.0

    QP_MIN = 0.0
    QP_MAX = 51.0

    BITRATE_MIN = 100
    BITRATE_MAX = 99999

    AQ_STRENGTH_MIN = 0.0
    AQ_STRENGTH_MAX = 3.0

    KEYINT_MIN = 0
    KEYINT_MAX = 990

    MIN_KEYINT_MIN = 0
    MIN_KEYINT_MAX = 990

    REFS_MIN = 1
    REFS_MAX = 16

    RC_LOOKAHEAD_MIN = 10
    RC_LOOKAHEAD_MAX = 990

    PSY_RD_MIN = 0.0
    PSY_RD_MAX = 5.0

    PSY_RDOQ_MIN = 0.0
    PSY_RDOQ_MAX = 50.0

    SUBME_MIN = 0
    SUBME_MAX = 7

    DEBLOCK_MIN = -6
    DEBLOCK_MAX = 6

    SELECTIVE_SAO_MIN = 0
    SELECTIVE_SAO_MAX = 4

    RD_MIN = 1
    RD_MAX = 6

    def __init__(self):
        """Initializes the X265 class with all necessary variables for the codec's settings."""
        self.is_advanced_enabled = False
        self._is_crf_enabled = True
        self._is_qp_enabled = False
        self._is_bitrate_enabled = False
        self.ffmpeg_args = {
            '-c:v': 'libx265',
            '-crf': '20'
        }
        self._ffmpeg_advanced_args = {}

    @property
    def is_crf_enabled(self) -> bool:
        """
        Returns whether CRF is enabled for the rate type settings.

        Returns:
            Boolean that represents whether CRF is enabled for the rate type settings.
        """
        return self._is_crf_enabled

    @property
    def is_qp_enabled(self) -> bool:
        """
        Returns whether QP is enabled for the rate type settings.

        Returns:
            Boolean that represents whether QP is enabled for the rate type settings.
        """
        return self._is_qp_enabled

    @property
    def is_bitrate_enabled(self) -> bool:
        """
        Returns whether bitrate is enabled for the rate type settings.

        Returns:
            Boolean that represents whether bitrate is enabled for the rate type settings.
        """
        return self._is_bitrate_enabled

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self) -> float:
        """
        Returns the value of the CRF setting.

        Returns:
            CRF setting as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return 20.0

    @crf.setter
    def crf(self, crf_value: float | None):
        """
        Sets the CRF setting to the specified value.

        Parameters:
            crf_value: Value to use for the CRF setting.

        Returns:
            None
        """
        if crf_value is None or crf_value < 0 or crf_value > 51:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)
            self.qp = None
            self.bitrate = None
            self._is_crf_enabled = True
            self._is_qp_enabled = False
            self._is_bitrate_enabled = False

    @property
    def qp(self) -> int:
        """
        Returns the value of the QP setting.

        Returns:
            QP setting as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-qp'])
        return 20

    @qp.setter
    def qp(self, qp_value: int | None):
        """
        Sets the QP setting to the specified value.

        Parameters:
            qp_value: Value to use for the QP setting.

        Returns:
            None
        """
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.crf = None
            self.bitrate = None
            self._is_crf_enabled = False
            self._is_qp_enabled = True
            self._is_bitrate_enabled = False

    @property
    def bitrate(self) -> int:
        """
        Returns the value of the bitrate setting.

        Returns:
            Bitrate setting as an integer.
        """
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']

            return int(bitrate_arg.split('k')[0])
        return 2500

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate setting to the specified value.

        Parameters:
            bitrate_value: Value to use for the bitrate setting.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.crf = None
            self.qp = None
            self._is_crf_enabled = False
            self._is_qp_enabled = False
            self._is_bitrate_enabled = True

    @property
    def profile(self) -> int:
        """
        Returns the index of the profile setting.

        Returns:
            Profile setting as an index using the PROFILE variable.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']

            return self.PROFILE.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            profile_index: Index from the PROFILE variable.

        Returns:
            None
        """
        if profile_index and 0 < profile_index < X265.PROFILE_LENGTH:
            self.ffmpeg_args['-profile:v'] = self.PROFILE[profile_index]
        else:
            self.ffmpeg_args.pop('-profile:v', 0)

    @property
    def preset(self) -> int:
        """
        Returns the index of the preset setting.

        Returns:
            Preset setting as an index using the PRESET variable.
        """
        if '-preset' in self.ffmpeg_args:
            preset_value = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_value)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        """
        Sets the preset setting to the specified index.

        Parameters:
            preset_index: Index from the PRESET variable.

        Returns:
            None
        """
        if preset_index and 0 < preset_index < X265.PRESET_LENGTH:
            self.ffmpeg_args['-preset'] = self.PRESET[preset_index]
        else:
            self.ffmpeg_args.pop('-preset', 0)

    @property
    def level(self) -> int:
        """
        Returns the index of the level setting.

        Returns:
            Level setting as an index using the LEVEL variable.
        """
        if '-level' in self.ffmpeg_args:
            level_value = self.ffmpeg_args['-level']

            return self.LEVEL.index(level_value)
        return 0

    @level.setter
    def level(self, level_index: int | None):
        """
        Sets the level setting to the specified index.

        Parameters:
            level_index: Index from the LEVEL variable.

        Returns:
            None
        """
        if level_index and 0 < level_index < X265.LEVEL_LENGTH:
            self.ffmpeg_args['-level'] = self.LEVEL[level_index]
        else:
            self.ffmpeg_args.pop('-level', 0)

    @property
    def tune(self) -> int:
        """
        Returns the index of the tune setting.

        Returns:
            Tune setting as an index using the TUNE variable.
        """
        if '-tune' in self.ffmpeg_args:
            tune_value = self.ffmpeg_args['-tune']

            return self.TUNE.index(tune_value)
        return 0

    @tune.setter
    def tune(self, tune_index: int | None):
        """
        Sets the tune setting to the specified index.

        Parameters:
            tune_index: Index from the TUNE variable.

        Returns:
            None
        """
        if tune_index and 0 < tune_index < X265.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def vbv_maxrate(self) -> int:
        """
        Returns the value of the vbv maxrate setting.

        Returns:
            Vbv maxrate setting as an integer.
        """
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value: int | None):
        """
        Sets the vbv maxrate setting to the specified value.

        Parameters:
            vbv_maxrate_value: Value to use for the vbv maxrate setting.

        Returns:
            None
        """
        if vbv_maxrate_value is None or not self.is_vbv_valid():
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)

    @property
    def vbv_bufsize(self) -> int:
        """
        Returns the value of the vbv bufsize setting.

        Returns:
            Vbv bufsize setting as an integer.
        """
        if 'vbv-bufsize=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-bufsize='])
        return 2500

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize_value: int | None):
        """
        Sets the vbv bufsize setting to the specified value.

        Parameters:
            vbv_bufsize_value: Value to use for the vbv bufsize setting.

        Returns:
            None
        """
        if vbv_bufsize_value is None or not self.is_vbv_valid():
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    def is_vbv_valid(self) -> bool:
        """
        Returns whether VBV is able to be used and is enabled.

        Returns:
            Boolean that represents whether VBV is valid and enabled.
        """
        return self.is_advanced_enabled and self.is_bitrate_enabled

    @property
    def aq_mode(self) -> int:
        """
        Returns the index of the AQ mode setting.

        Returns:
            AQ mode setting as an index using the AQ_MODE variable.
        """
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_arg = self._ffmpeg_advanced_args['aq-mode=']

            return self.AQ_MODE.index(aq_mode_arg)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index: int | None):
        """
        Sets the AQ mode setting to the specified index.

        Parameters:
            aq_mode_index: Index from the AQ_MODE variable.

        Returns:
            None
        """
        if aq_mode_index and 0 < aq_mode_index < X265.AQ_MODE_LENGTH:
            self._ffmpeg_advanced_args['aq-mode='] = self.AQ_MODE[aq_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('aq-mode=', 0)

    @property
    def aq_strength(self) -> float:
        """
        Returns the value of the AQ strength setting.

        Returns:
            AQ strength setting as a float.
        """
        if 'aq-strength=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['aq-strength='])
        return 1.0

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: float | None):
        """
        Sets the AQ strength setting to the specified value.

        Parameters:
            aq_strength_value: Value to use for the AQ strength setting.

        Returns:
            None
        """
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(round(aq_strength_value, 1))

    @property
    def hevc_aq(self) -> bool:
        """
        Returns whether the hevc AQ setting is enabled.

        Returns:
            Boolean that represents whether the hevc AQ setting is enabled.
        """
        if 'hevc-aq=' in self._ffmpeg_advanced_args:
            hevc_aq_arg = self._ffmpeg_advanced_args['hevc-aq=']

            return hevc_aq_arg == '1'
        return False

    @hevc_aq.setter
    def hevc_aq(self, is_hevc_aq_enabled: bool):
        """
        Sets the hevc AQ setting to the specified value.

        Parameters:
            is_hevc_aq_enabled: Boolean that represents whether the hevc AQ setting is enabled.

        Returns:
            None
        """
        if is_hevc_aq_enabled:
            self._ffmpeg_advanced_args['hevc-aq='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('hevc-aq=', 0)

    @property
    def keyint(self) -> int:
        """
        Returns the value of the keyframe interval setting.

        Returns:
            Keyframe interval setting as an integer.
        """
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value: int | None):
        """
        Sets the keyframe interval setting to the specified value.

        Parameters:
            keyint_value: Value to use for the keyframe interval setting.

        Returns:
            None
        """
        if keyint_value is None:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint_value)

    @property
    def min_keyint(self) -> int:
        """
        Returns the value of the minimum keyframe interval setting.

        Returns:
            Minimum keyframe interval setting as an integer.
        """
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 0

    @min_keyint.setter
    def min_keyint(self, min_keyint_value: int | None):
        """
        Sets the minimum keyframe interval setting to the specified value.

        Parameters:
            min_keyint_value: Value to use for the minimum keyframe interval setting.

        Returns:
            None
        """
        if min_keyint_value is None:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def ref(self) -> int:
        """
        Returns the value of the reference frames setting.

        Returns:
            Reference frames setting as an integer.
        """
        if 'ref=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['ref='])
        return 3

    @ref.setter
    def ref(self, ref_value: int | None):
        """
        Sets the reference frames setting to the specified value.

        Parameters:
            ref_value: Value to use for the reference frames setting.

        Returns:
            None
        """
        if ref_value is None:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref_value)

    @property
    def bframes(self) -> int:
        """
        Returns the value of the B frames setting.

        Returns:
            B frames setting as an integer.
        """
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 4

    @bframes.setter
    def bframes(self, bframes_value: int | None):
        """
        Sets the B frames setting to the specified value.

        Parameters:
            bframes_value: Value to use for the B frames setting.

        Returns:
            None
        """
        if bframes_value is None:
            self._ffmpeg_advanced_args.pop('bframes=', 0)
        else:
            self._ffmpeg_advanced_args['bframes='] = str(bframes_value)

    @property
    def b_adapt(self) -> int:
        """
        Returns the index of the B adapt setting.

        Returns:
            B adapt setting as an index using the B_ADAPT variable.
        """
        if 'b-adapt=' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['b-adapt=']

            return self.B_ADAPT.index(b_adapt_arg)
        return 0

    @b_adapt.setter
    def b_adapt(self, b_adapt_index: int | None):
        """
        Sets the B adapt setting to the specified index.

        Parameters:
            Index from the B_ADAPT variable.

        Returns:
            None
        """
        if b_adapt_index and 0 < b_adapt_index < X265.B_ADAPT_LENGTH:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT[b_adapt_index]
        else:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)

    @property
    def no_b_pyramid(self) -> bool:
        """
        Returns whether the no B pyramid setting is enabled.

        Returns:
            Boolean that represents whether the no B pyramid setting is enabled.
        """
        if 'no-b-pyramid=' in self._ffmpeg_advanced_args:
            no_b_pyramid_arg = self._ffmpeg_advanced_args['no-b-pyramid=']

            return no_b_pyramid_arg == '1'
        return False

    @no_b_pyramid.setter
    def no_b_pyramid(self, is_no_b_pyramid_enabled: bool):
        """
        Sets the no B pyramid setting to the specified value.

        Parameters:
            is_no_b_pyramid_enabled: Boolean that represents whether the no B pyramid setting is enabled.

        Returns:
            None
        """
        if is_no_b_pyramid_enabled:
            self._ffmpeg_advanced_args['no-b-pyramid='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-b-pyramid=', 0)

    @property
    def b_intra(self) -> bool:
        """
        Returns whether the B intra setting is enabled.

        Returns:
            Boolean that represents whether the B intra setting is enabled.
        """
        if 'b-intra=' in self._ffmpeg_advanced_args:
            b_intra_arg = self._ffmpeg_advanced_args['b-intra=']

            return b_intra_arg == '1'
        return False

    @b_intra.setter
    def b_intra(self, is_b_intra_enabled: bool):
        """
        Sets the B intra setting to the specified value.

        Parameters:
            is_b_intra_enabled: Boolean that represents whether the B intra setting is enabled.

        Returns:
            None
        """
        if is_b_intra_enabled:
            self._ffmpeg_advanced_args['b-intra='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('b-intra=', 0)

    @property
    def no_open_gop(self) -> bool:
        """
        Returns whether the no open GOP setting is enabled.

        Returns:
            Boolean that represents whether the no open GOP setting is enabled.
        """
        if 'no-open-gop=' in self._ffmpeg_advanced_args:
            no_open_gop_arg = self._ffmpeg_advanced_args['no-open-gop=']

            return no_open_gop_arg == '1'
        return False

    @no_open_gop.setter
    def no_open_gop(self, is_no_open_gop_enabled: bool):
        """
        Sets the no open GOP setting to the specified value.

        Parameters:
            is_no_open_gop_enabled: Boolean that represents whether the no open GOP setting is enabled.

        Returns:
            None
        """
        if is_no_open_gop_enabled:
            self._ffmpeg_advanced_args['no-open-gop='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-open-gop=', 0)

    @property
    def rc_lookahead(self) -> int:
        """
        Returns the value of the rate control lookahead setting.

        Returns:
            Rate control lookahead setting as an integer.
        """
        if 'rc-lookahead=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rc-lookahead='])
        return 20

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value: int | None):
        """
        Sets the rate control lookahead setting to the specified value.

        Parameters:
            rc_lookahead_value: Value to use for the rate control lookahead setting.

        Returns:
            None
        """
        if rc_lookahead_value is None:
            self._ffmpeg_advanced_args.pop('rc-lookahead=', 0)
        else:
            self._ffmpeg_advanced_args['rc-lookahead='] = str(rc_lookahead_value)

    @property
    def no_scenecut(self) -> bool:
        """
        Returns whether the no scenecut setting is enabled.

        Returns:
            Boolean that represents whether the no scenecut setting is enabled.
        """
        if 'no-scenecut=' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['no-scenecut=']

            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, is_no_scenecut_enabled: bool):
        """
        Sets the no scenecut setting to the specified value.

        Parameters:
            is_no_scenecut_enabled: Boolean that represents whether the no scenecut setting is enabled.

        Returns:
            None
        """
        if is_no_scenecut_enabled:
            self._ffmpeg_advanced_args['no-scenecut='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-scenecut=', 0)

    @property
    def no_high_tier(self) -> bool:
        """
        Returns whether the no high tier setting is enabled.

        Returns:
            Boolean that represents whether the no high tier setting is enabled.
        """
        if 'no-high-tier=' in self._ffmpeg_advanced_args:
            no_high_tier_arg = self._ffmpeg_advanced_args['no-high-tier=']

            return no_high_tier_arg == '1'
        return False

    @no_high_tier.setter
    def no_high_tier(self, is_no_high_tier_enabled: bool):
        """
        Sets the no high tier setting to the specified value.

        Parameters:
            is_no_high_tier_enabled: Boolean that represents whether the no high tier setting is enabled.

        Returns:
            None
        """
        if is_no_high_tier_enabled:
            self._ffmpeg_advanced_args['no-high-tier='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-high-tier=', 0)

    @property
    def psy_rd(self) -> float:
        """
        Returns the value of the psychovisual rate-distortion setting.

        Returns:
            Psychovisual rate-distortion setting as a float.
        """
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rd='])
        return 2.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_value: float | None):
        """
        Sets the psychovisual rate-distortion setting to the specified value.

        Parameters:
            psy_rd_value: Value to use for the psychovisual rate-distortion setting.

        Returns:
            None
        """
        if psy_rd_value is None:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rd='] = str(round(psy_rd_value, 1))

    @property
    def psy_rdoq(self) -> float:
        """
        Returns the value of the psychovisual rate-distortion RDOQ setting.

        Returns:
            Psychovisual rate-distortion RDOQ setting as a float.
        """
        if 'psy-rdoq=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rdoq='])
        return 0.0

    @psy_rdoq.setter
    def psy_rdoq(self, psy_rdoq_value: float | None):
        """
        Sets the psychovisual rate-distortion RDOQ setting to the specified value.

        Parameters:
            psy_rdoq_value: Value to use for the psychovisual rate-distortion RDOQ setting.

        Returns:
            None
        """
        if psy_rdoq_value is None:
            self._ffmpeg_advanced_args.pop('psy-rdoq=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rdoq='] = str(round(psy_rdoq_value, 1))

    @property
    def me(self) -> int:
        """
        Returns the index for the motion estimation setting.

        Returns:
            Motion estimation setting as an index using the ME variable.
        """
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']

            return self.ME.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index: int | None):
        """
        Sets the motion estimation setting to the specified index.

        Parameters:
            me_index: Index from the ME variable.

        Returns:
            None
        """
        if me_index and 0 < me_index < X265.ME_LENGTH:
            self._ffmpeg_advanced_args['me='] = self.ME[me_index]
        else:
            self._ffmpeg_advanced_args.pop('me=', 0)

    @property
    def subme(self) -> int:
        """
        Returns the value of the sub-motion estimation setting.

        Returns:
            Sub-motion estimation setting as an integer.
        """
        if 'subme=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['subme='])
        return 2

    @subme.setter
    def subme(self, subme_value: int | None):
        """
        Sets the sub-motion estimation setting to the specified value.

        Parameters:
            subme_value: Value to use for the sub-motion estimation setting.

        Returns:
            None
        """
        if subme_value is None:
            self._ffmpeg_advanced_args.pop('subme=', 0)
        else:
            self._ffmpeg_advanced_args['subme='] = str(subme_value)

    @property
    def weightb(self) -> bool:
        """
        Returns whether the weight B setting is enabled.

        Returns:
            Boolean that represents whether the weight B setting is enabled.
        """
        if 'weightb=' in self._ffmpeg_advanced_args:
            weightb_arg = self._ffmpeg_advanced_args['weightb=']

            return weightb_arg == '1'
        return False

    @weightb.setter
    def weightb(self, is_weightb_enabled: bool):
        """
        Sets the weight B setting to the specified value.

        Parameters:
            is_weightb_enabled: Boolean that represents whether the weight B setting is enabled.

        Returns:
            None
        """
        if is_weightb_enabled:
            self._ffmpeg_advanced_args['weightb='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('weightb=', 0)

    @property
    def no_weightp(self) -> bool:
        """
        Returns whether the no weight P setting is enabled.

        Returns:
            Boolean that represents whether the no weight P setting is enabled.
        """
        if 'no-weightp=' in self._ffmpeg_advanced_args:
            no_weightp_arg = self._ffmpeg_advanced_args['no-weightp=']

            return no_weightp_arg == '1'
        return False

    @no_weightp.setter
    def no_weightp(self, is_no_weightp_enabled: bool):
        """
        Sets the no weight P setting to the specified value.

        Parameters:
            is_no_weightp_enabled: Boolean that represents whether the no weight P setting is enabled.

        Returns:
            None
        """
        if is_no_weightp_enabled:
            self._ffmpeg_advanced_args['no-weightp='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-weightp=', 0)

    @property
    def deblock(self) -> tuple:
        """
        Returns the alpha and beta values respectively for the deblock setting.

        Returns:
            Tuple that contains the alpha and beta values respectively for the deblock setting.
        """
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')

            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock_tuple: tuple | None):
        """
        Sets the alpha and beta values respectively for the deblock setting.

        Parameters:
            deblock_tuple: Tuple that contains the alpha and beta values respectively for the deblock setting.

        Returns:
            None
        """
        if deblock_tuple is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock_tuple
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def no_deblock(self) -> bool:
        """
        Returns whether the no deblock setting is enabled.

        Returns:
            Boolean that represents whether the no deblock setting is enabled.
        """
        if 'no-deblock=' in self._ffmpeg_advanced_args:
            no_deblock_arg = self._ffmpeg_advanced_args['no-deblock=']

            return no_deblock_arg == '1'
        return False

    @no_deblock.setter
    def no_deblock(self, is_no_deblock_enabled: bool):
        """
        Sets the no deblock setting to the specified value.

        Parameters:
            is_no_deblock_enabled: Boolean that represents whether the no deblock setting is enabled.

        Returns:
            None
        """
        if is_no_deblock_enabled:
            self._ffmpeg_advanced_args['no-deblock='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-deblock=', 0)

    @property
    def no_sao(self) -> bool:
        """
        Returns whether the no SAO setting is enabled.

        Returns:
            Boolean that represents whether the no SAO setting is enabled.
        """
        if 'no-sao=' in self._ffmpeg_advanced_args:
            no_sao_arg = self._ffmpeg_advanced_args['no-sao=']

            return no_sao_arg == '1'
        return False

    @no_sao.setter
    def no_sao(self, is_no_sao_enabled: bool):
        """
        Sets the no SAO setting to the specified value.

        Parameters:
            is_no_sao_enabled: Boolean that represents whether the no SAO setting is enabled.

        Returns:
            None
        """
        if is_no_sao_enabled:
            self._ffmpeg_advanced_args['no-sao='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-sao=', 0)

    @property
    def sao_non_deblock(self) -> bool:
        """
        Returns whether the SAO non-deblock setting is enabled.

        Returns:
            Boolean that represents whether the SAO non-deblock setting is enabled.
        """
        if 'sao-non-deblock=' in self._ffmpeg_advanced_args:
            sao_non_deblock_args = self._ffmpeg_advanced_args['sao-non-deblock=']

            return sao_non_deblock_args == '1'
        return False

    @sao_non_deblock.setter
    def sao_non_deblock(self, is_sao_non_deblock_enabled: bool):
        """
        Sets the SAO non-deblock setting to the specified value.

        Parameters:
            is_sao_non_deblock_enabled: Boolean that represents whether the SAO non-deblock setting is enabled.

        Returns:
            None
        """
        if is_sao_non_deblock_enabled:
            self._ffmpeg_advanced_args['sao-non-deblock='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('sao-non-deblock=', 0)

    @property
    def limit_sao(self) -> bool:
        """
        Returns whether the limit SAO setting is enabled.

        Returns:
            Boolean that represents whether the limit SAO setting is enabled.
        """
        if 'limit-sao=' in self._ffmpeg_advanced_args:
            limit_sao_arg = self._ffmpeg_advanced_args['limit-sao=']

            return limit_sao_arg == '1'
        return False

    @limit_sao.setter
    def limit_sao(self, is_limit_sao_enabled: bool):
        """
        Sets the limit SAO setting to the specified value.

        Parameters:
            is_limit_sao_enabled: Boolean that represents whether the limit SAO setting is enabled.

        Returns:
            None
        """
        if is_limit_sao_enabled:
            self._ffmpeg_advanced_args['limit-sao='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('limit-sao=', 0)

    @property
    def selective_sao(self) -> int:
        """
        Returns the value of the selective SAO setting.

        Returns:
            Selective SAO setting as an integer.
        """
        if 'selective-sao=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['selective-sao='])
        return 0

    @selective_sao.setter
    def selective_sao(self, selective_sao_value: int | None):
        """
        Sets the selective SAO setting to the specified value.

        Parameters:
            selective_sao_value: Value to use for the selective SAO setting.

        Returns:
            None
        """
        if selective_sao_value is None:
            self._ffmpeg_advanced_args.pop('selective-sao=', 0)
        else:
            self._ffmpeg_advanced_args['selective-sao='] = str(selective_sao_value)

    @property
    def rd(self) -> int:
        """
        Returns the value of the rate distortion setting.

        Returns:
            Rate distortion as an integer.
        """
        if 'rd=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rd='])
        return 3

    @rd.setter
    def rd(self, rd_value: int | None):
        """
        Sets the rate distortion setting to the specified value.

        Parameters:
            rd_value: Value to use for the rate distortion setting.

        Returns:
            None
        """
        if rd_value is None:
            self._ffmpeg_advanced_args.pop('rd=', 0)
        else:
            self._ffmpeg_advanced_args['rd='] = str(rd_value)

    @property
    def rdoq_level(self) -> int:
        """
        Returns the index of the RDOQ level setting.

        Returns:
            RDOQ level setting as an index using the RDOQ_LEVEL variable.
        """
        if 'rdoq-level=' in self._ffmpeg_advanced_args:
            rdoq_level_arg = self._ffmpeg_advanced_args['rdoq-level=']

            return self.RDOQ_LEVEL.index(rdoq_level_arg)
        return 0

    @rdoq_level.setter
    def rdoq_level(self, rdoq_level_index: int | None):
        """
        Sets the RDOQ level setting to the specified index.

        Parameters:
            rdoq_level_index: Index from the RDOQ_LEVEL variable.
        """
        if rdoq_level_index and 0 < rdoq_level_index < X265.RDOQ_LEVEL_LENGTH:
            self._ffmpeg_advanced_args['rdoq-level='] = self.RDOQ_LEVEL[rdoq_level_index]
        else:
            self._ffmpeg_advanced_args.pop('rdoq-level=', 0)

    @property
    def rd_refine(self) -> bool:
        """
        Returns whether the rate-distortion refine setting is enabled.

        Returns:
            Boolean that represents whether the rate-distortion refine setting is enabled.
        """
        if 'rd-refine=' in self._ffmpeg_advanced_args:
            rd_refine_value = self._ffmpeg_advanced_args['rd-refine=']

            return rd_refine_value == '1'
        return False

    @rd_refine.setter
    def rd_refine(self, is_rd_refine_enabled: bool):
        """
        Sets the rate-distortion refine setting to the specified value.

        Parameters:
            is_rd_refine_enabled: Boolean that represents whether the rate-distortion refine setting is enabled.

        Returns:
            None
        """
        if is_rd_refine_enabled:
            self._ffmpeg_advanced_args['rd-refine='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('rd-refine=', 0)

    @property
    def ctu(self) -> int:
        """
        Returns the index of the CTU setting.

        Returns:
            CTU setting as an index using the MAX_CU_SIZE variable.
        """
        if 'ctu=' in self._ffmpeg_advanced_args:
            ctu_arg = self._ffmpeg_advanced_args['ctu=']

            return self.MAX_CU_SIZE.index(ctu_arg)
        return 0

    @ctu.setter
    def ctu(self, ctu_index: int | None):
        """
        Sets the CTU setting to the specified index.

        Parameters:
            ctu_index: Index from the MAX_CU_SIZE variable.

        Returns:
            None
        """
        if ctu_index and 0 < ctu_index < X265.MAX_CU_SIZE_LENGTH:
            self._ffmpeg_advanced_args['ctu='] = self.MAX_CU_SIZE[ctu_index]
        else:
            self._ffmpeg_advanced_args.pop('ctu=', 0)

    @property
    def min_cu_size(self) -> int:
        """
        Returns the index of the min CU size setting.

        Returns:
            Min CU size setting as an index using the MIN_CU_SIZE variable.
        """
        if 'min-cu-size=' in self._ffmpeg_advanced_args:
            min_cu_size_arg = self._ffmpeg_advanced_args['min-cu-size=']

            return self.MIN_CU_SIZE.index(min_cu_size_arg)
        return 0

    @min_cu_size.setter
    def min_cu_size(self, min_cu_size_index: int | None):
        """
        Sets the min CU size setting to the specified index.

        Parameters:
            min_cu_size_index: Index from the MIN_CU_SIZE variable.

        Returns:
            None
        """
        if min_cu_size_index and 0 < min_cu_size_index < X265.MIN_CU_SIZE_LENGTH:
            self._ffmpeg_advanced_args['min-cu-size='] = self.MIN_CU_SIZE[min_cu_size_index]
        else:
            self._ffmpeg_advanced_args.pop('min-cu-size=', 0)

    @property
    def rect(self) -> bool:
        """
        Returns whether the rect setting is enabled.

        Returns:
            Boolean that represents whether the rect setting is enabled.
        """
        if 'rect=' in self._ffmpeg_advanced_args:
            rect_arg = self._ffmpeg_advanced_args['rect=']

            return rect_arg == '1'
        return False

    @rect.setter
    def rect(self, is_rect_enabled: bool):
        """
        Sets the rect setting to the specified value.

        Parameters:
            is_rect_enabled: Boolean that represents whether the rect setting is enabled.

        Returns:
            None
        """
        if is_rect_enabled:
            self._ffmpeg_advanced_args['rect='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('rect=', 0)

    @property
    def amp(self) -> bool:
        """
        Returns whether the amp setting is enabled.

        Returns:
            Boolean that represents whether the amp setting is enabled.
        """
        if 'amp=' in self._ffmpeg_advanced_args:
            amp_arg = self._ffmpeg_advanced_args['amp=']

            return amp_arg == '1'
        return False

    @amp.setter
    def amp(self, is_amp_enabled: bool):
        """
        Sets the amp setting to the specified value.

        Parameters:
            is_amp_enabled: Boolean that represents whether the amp setting is enabled.

        Returns:
            None
        """
        if is_amp_enabled:
            self._ffmpeg_advanced_args['amp='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('amp=', 0)

    @property
    def wpp(self) -> bool:
        """
        Returns whether the WPP setting is enabled.

        Returns:
            Boolean that represents whether the WPP setting is enabled.
        """
        if 'wpp=' in self._ffmpeg_advanced_args:
            wpp_arg = self._ffmpeg_advanced_args['wpp=']

            return wpp_arg == '1'
        return False

    @wpp.setter
    def wpp(self, is_wpp_enabled: bool):
        """
        Sets the WPP setting to the specified value.

        Parameters:
            is_wpp_enabled: Boolean that represents whether the WPP setting is enabled.

        Returns:
            None
        """
        if is_wpp_enabled:
            self._ffmpeg_advanced_args['wpp='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('wpp=', 0)

    @property
    def pmode(self) -> bool:
        """
        Returns whether the P mode setting is enabled.

        Returns:
            Boolean that represents whether the P mode setting is enabled.
        """
        if 'pmode=' in self._ffmpeg_advanced_args:
            pmode_arg = self._ffmpeg_advanced_args['pmode=']

            return pmode_arg == '1'
        return False

    @pmode.setter
    def pmode(self, is_pmode_enabled: bool):
        """
        Sets the P mode setting to the specified value.

        Parameters:
            is_pmode_enabled: Boolean that represents whether the P mode setting is enabled.

        Returns:
            None
        """
        if is_pmode_enabled:
            self._ffmpeg_advanced_args['pmode='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('pmode=', 0)

    @property
    def pme(self) -> bool:
        """
        Returns whether the PME setting is enabled.

        Returns:
            Boolean that represents whether the PME setting is enabled.
        """
        if 'pme=' in self._ffmpeg_advanced_args:
            pme_arg = self._ffmpeg_advanced_args['pme=']

            return pme_arg == '1'
        return False

    @pme.setter
    def pme(self, is_pme_enabled: bool):
        """
        Sets the PME setting to the specified value.

        Parameters:
            is_pme_enabled: Boolean that represents whether the PME setting is enabled.

        Returns:
            None
        """
        if is_pme_enabled:
            self._ffmpeg_advanced_args['pme='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('pme=', 0)

    @property
    def uhd_bd(self) -> bool:
        """
        Returns whether the UHD BD setting is enabled.

        Returns:
            Boolean that represents whether the UHD BD setting is enabled.
        """
        if 'uhd-bd=' in self._ffmpeg_advanced_args:
            uhd_bd_value = self._ffmpeg_advanced_args['uhd-bd=']

            return uhd_bd_value == '1'
        return False

    @uhd_bd.setter
    def uhd_bd(self, is_uhd_bd_enabled: bool):
        """
        Sets the UHD BD setting to the specified value.

        Parameters:
            is_uhd_bd_enabled: Boolean that represents whether the UHD BD setting is enabled.

        Returns:
            None
        """
        if is_uhd_bd_enabled:
            self._ffmpeg_advanced_args['uhd-bd='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('uhd-bd=', 0)

    @property
    def encode_pass(self) -> int:
        """
        Returns that value of the encode pass setting.

        Returns:
            Encode pass setting as an integer.
        """
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return 0

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        """
        Sets the encode pass setting to the specified value.

        Parameters:
            encode_pass_value: Value to use for the encode pass setting.

        Returns:
            None
        """
        if encode_pass_value is None:
            self._ffmpeg_advanced_args.pop('pass=', 0)
        else:
            self._ffmpeg_advanced_args['pass='] = str(encode_pass_value)

    @property
    def stats(self) -> str:
        """
        Returns the full file path of the stats file.

        Returns:
            String that represents the full file path of the stats file.
        """
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        """
        Sets the full file path for the stats file.

        Parameters:
            stats_file_path: Full file path to use for the stats file.

        Returns:
            None
        """
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    def get_ffmpeg_advanced_args(self) -> dict:
        """
        Returns the ffmpeg arguments for the x265 codec's settings.

        Returns:
            Dictionary that contains the arguments and their settings for the x265 codec.
        """
        advanced_args = {'-x265-params': None}
        args = ''

        if self.is_advanced_enabled:
            args = self._generate_advanced_args()
        else:
            if self.encode_pass:
                args = self._get_pass_args()

        if args:
            advanced_args['-x265-params'] = args

        return advanced_args

    def _get_pass_args(self) -> str:
        # Returns the Encode Pass and Stats settings as a string that represents ffmpeg arguments.
        return ''.join(['pass=', str(self.encode_pass), ':', 'stats=', self.stats])

    def _generate_advanced_args(self) -> str:
        # Returns the advanced settings for the x265 codec as a string that represents ffmpeg arguments.
        x265_advanced_settings = ''

        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x265_advanced_settings += ''.join([setting, arg, ':'])

        return x265_advanced_settings


class H264Nvenc:
    """Class that configures all H264 Nvenc codec settings available for Render Watch."""

    PRESET = [
        'default', 'slow', 'medium', 'fast', 'lossless', 'losslesshp', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
    PRESET_LENGTH = len(PRESET)

    PROFILE = ['auto', 'baseline', 'main', 'high', 'high444p']
    PROFILE_LENGTH = len(PROFILE)

    LEVEL = [
        'auto', '1.0', '1.0b', '1.1', '1.2', '1.3', '2.0', '2.1', '2.2', '3.0', '3.1', '3.2', '4.0', '4.1', '4.2',
        '5.0', '5.1', '5.2', '6.0', '6.1', '6.2'
    ]
    LEVEL_LENGTH = len(LEVEL)

    TUNE = ['auto', 'hq', 'll', 'ull', 'lossless']
    TUNE_LENGTH = len(TUNE)

    RATE_CONTROL = ['auto', 'constqp', 'vbr', 'cbr', 'cbr_ld_hq', 'cbr_hq', 'vbr_hq']
    RATE_CONTROL_LENGTH = len(RATE_CONTROL)

    MULTI_PASS = ['auto', 'disabled', 'qres', 'fullres']
    MULTI_PASS_LENGTH = len(MULTI_PASS)

    CODER = ['auto', 'cabac', 'cavlc', 'ac', 'vlc']
    CODER_LENGTH = len(CODER)

    BREF_MODE = ['auto', 'disabled', 'each', 'middle']
    BREF_MODE_LENGTH = len(BREF_MODE)

    QP_MIN = 0.0
    QP_MAX = 51.0

    BITRATE_MIN = 100
    BITRATE_MAX = 99999

    RC_LOOKAHEAD_MIN = 0
    RC_LOOKAHEAD_MAX = 990

    SURFACES_MIN = 0
    SURFACES_MAX = 64

    B_FRAMES_MIN = 0
    B_FRAMES_MAX = 16

    REFS_MIN = 0
    REFS_MAX = 16

    AQ_STRENGTH_MIN = 1
    AQ_STRENGTH_MAX = 15

    def __init__(self):
        """Initializes the H264Nvenc class with all necessary variables for the codec's options."""
        self.is_advanced_enabled = False
        self.is_qp_custom_enabled = False
        self.is_dual_pass_enabled = False
        self._is_qp_enabled = True
        self._is_bitrate_enabled = False
        self._ffmpeg_advanced_args = {}
        self.ffmpeg_args = {
            '-c:v': 'h264_nvenc',
            '-qp': '20'
        }

    @property
    def is_qp_enabled(self) -> bool:
        """
        Returns whether QP is enabled for the rate type settings.

        Returns:
            Boolean that represents whether QP is enabled for the rate type settings.
        """
        return self._is_qp_enabled

    @property
    def is_bitrate_enabled(self) -> bool:
        """
        Returns whether bitrate is enabled for the rate type settings.

        Returns:
            Boolean that represents whether bitrate is enabled for the rate type settings.
        """
        return self._is_bitrate_enabled

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def qp(self) -> int:
        """
        Returns the value of the QP setting.

        Returns:
            QP setting as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-qp'])
        return 20

    @qp.setter
    def qp(self, qp_value: int | None):
        """
        Sets the QP setting to the specified value.

        Parameters:
            qp_value: Value to use for the QP setting.

        Returns:
            None
        """
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.bitrate = None
            self._is_qp_enabled = True
            self._is_bitrate_enabled = False

    @property
    def bitrate(self) -> int:
        """
        Returns the value of the bitrate setting.

        Returns:
            Bitrate setting as an integer.
        """
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']

            return int(bitrate_arg.split('k')[0])
        return 2500

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate setting to the specified value.

        Parameters:
            bitrate_value: Value to use for the bitrate setting.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.qp = None
            self._is_qp_enabled = False
            self._is_bitrate_enabled = True

    @property
    def profile(self) -> int:
        """
        Returns the index of the profile setting.

        Returns:
            Profile setting as an index using the PROFILE variable.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']

            return self.PROFILE.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            profile_index: Index from the PROFILE variable.

        Returns:
            None
        """
        if profile_index and 0 < profile_index < H264Nvenc.PROFILE_LENGTH:
            self.ffmpeg_args['-profile:v'] = self.PROFILE[profile_index]
        else:
            self.ffmpeg_args.pop('-profile:v', 0)

    @property
    def preset(self) -> int:
        """
        Returns the index of the preset setting.

        Returns:
            Preset setting as an index using the PRESET variable.
        """
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        """
        Sets the preset setting to the specified index.

        Parameters:
            preset_index: Index from the PRESET variable.

        Returns:
            None
        """
        if preset_index and 0 < preset_index < H264Nvenc.PRESET_LENGTH:
            self.ffmpeg_args['-preset'] = self.PRESET[preset_index]
        else:
            self.ffmpeg_args.pop('-preset', 0)

    @property
    def level(self) -> int:
        """
        Returns the index of the level setting.

        Returns:
            Level setting as an index using the LEVEL variable.
        """
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']

            return self.LEVEL.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index: int | None):
        """
        Sets the level setting to the specified index.

        Parameters:
            level_index: Index from the LEVEL variable.

        Returns:
            None
        """
        if level_index and 0 < level_index < H264Nvenc.LEVEL_LENGTH:
            self.ffmpeg_args['-level'] = self.LEVEL[level_index]
        else:
            self.ffmpeg_args.pop('-level', 0)

    @property
    def tune(self) -> int:
        """
        Returns the index of the tune setting.

        Returns:
            Tune setting as an index using the TUNE variable.
        """
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']

            return self.TUNE.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index: int | None):
        """
        Sets the tune setting to the specified index.

        Parameters:
            tune_index: Index from the TUNE variable.

        Returns:
            None
        """
        if tune_index and 0 < tune_index < H264Nvenc.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def multi_pass(self) -> int:
        """
        Returns the index of the multi-pass setting.

        Returns:
            Multi-pass setting as an index using the MULTI_PASS variable.
        """
        if '-multipass' in self.ffmpeg_args:
            multi_pass_arg = self.ffmpeg_args['-multipass']

            return self.MULTI_PASS.index(multi_pass_arg)
        return 0

    @multi_pass.setter
    def multi_pass(self, multi_pass_index: int | None):
        """
        Sets the multi-pass setting to the specified index.

        Parameters:
            multi_pass_index: Index from the MULTI_PASS variable.

        Returns:
            None
        """
        if multi_pass_index and 0 < multi_pass_index < H264Nvenc.MULTI_PASS_LENGTH:
            self.ffmpeg_args['-multipass'] = self.MULTI_PASS[multi_pass_index]
        else:
            self.ffmpeg_args.pop('-multipass', 0)

    @property
    def cbr(self) -> bool:
        """
        Returns whether the constant bitrate setting is enabled.

        Returns:
            Boolean that represents whether the constant bitrate setting is enabled.
        """
        if '-cbr' in self.ffmpeg_args:
            cbr_value = self.ffmpeg_args['-cbr']

            return cbr_value == '1'
        return False

    @cbr.setter
    def cbr(self, cbr_enabled: bool):
        """
        Sets the constant bitrate setting to the specified value.

        Parameters:
            cbr_enabled: Boolean that represents whether the constant bitrate setting is enabled.

        Returns:
            None
        """
        if cbr_enabled:
            self.ffmpeg_args['-cbr'] = '1'
        else:
            self.ffmpeg_args.pop('-cbr', 0)

    @property
    def qp_i(self) -> int:
        """
        Returns the value of the QP I setting.

        Returns:
            QP I setting as a float.
        """
        if '-init_qpI' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpI'])
        return 20

    @qp_i.setter
    def qp_i(self, qp_i_value: int | None):
        """
        Sets the QP I setting to the specified value.

        Parameters:
            qp_i_value: Value to use for the QP I setting.

        Returns:
            None
        """
        if qp_i_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpI', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpI'] = str(qp_i_value)

    @property
    def qp_p(self) -> int:
        """
        Returns the value of the QP P setting.

        Returns:
            QP P setting as a float.
        """
        if '-init_qpP' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpP'])
        return 20

    @qp_p.setter
    def qp_p(self, qp_p_value: int | None):
        """
        Sets the QP P setting to the specified value.

        Parameters:
            qp_p_value: Value to use for the QP P setting.

        Returns:
            None
        """
        if qp_p_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpP', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpP'] = str(qp_p_value)

    @property
    def qp_b(self) -> int:
        """
        Returns the value of the QP B setting.

        Returns:
            QP B setting as a float.
        """
        if '-init_qpB' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpB'])
        return 20

    @qp_b.setter
    def qp_b(self, qp_b_value: int | None):
        """
        Sets the QP B setting to the specified value.

        Parameters:
            qp_b_value: Value to use for the QP B setting.

        Returns:
            None
        """
        if qp_b_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpB', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpB'] = str(qp_b_value)

    @property
    def rc(self) -> int:
        """
        Returns the index of the rate control setting.

        Returns:
            Rate control setting as an index using the RATE_CONTROL variable.
        """
        if '-rc' in self._ffmpeg_advanced_args:
            rc_arg = self._ffmpeg_advanced_args['-rc']

            return self.RATE_CONTROL.index(rc_arg)
        return 0

    @rc.setter
    def rc(self, rc_index: int | None):
        """
        Sets the rate control setting to the specified value.

        Parameters:
            rc_index: Index from the RATE_CONTROL variable.

        Returns:
            None
        """
        if rc_index and 0 < rc_index < H264Nvenc.RATE_CONTROL_LENGTH:
            self._ffmpeg_advanced_args['-rc'] = self.RATE_CONTROL[rc_index]
        else:
            self._ffmpeg_advanced_args.pop('-rc', 0)

    @property
    def rc_lookahead(self) -> int:
        """
        Returns the value of the rate control lookahead setting.

        Returns:
            Rate control lookahead setting as an integer.
        """
        if '-rc-lookahead' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-rc-lookahead'])
        return 0

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value: int | None):
        """
        Sets the rate control lookahead setting to the specified value.

        Parameters:
            rc_lookahead_value: Value to use for the rate control lookahead setting.

        Returns:
            None
        """
        if rc_lookahead_value is None:
            self._ffmpeg_advanced_args.pop('-rc-lookahead', 0)
        else:
            self._ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead_value)

    @property
    def surfaces(self) -> int:
        """
        Returns the value of the surfaces setting.

        Returns:
            Surfaces setting as an integer.
        """
        if '-surfaces' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-surfaces'])
        return 0

    @surfaces.setter
    def surfaces(self, surfaces_value: int | None):
        """
        Sets the surfaces setting to the specified value.

        Parameters:
            surfaces_value: Value to use for the surfaces setting.

        Returns:
            None
        """
        if surfaces_value is None:
            self._ffmpeg_advanced_args.pop('-surfaces', 0)
        else:
            self._ffmpeg_advanced_args['-surfaces'] = str(surfaces_value)

    @property
    def b_frames(self) -> int:
        """
        Returns the value of the B Frames setting.

        Returns:
            B Frames setting as an integer.
        """
        if '-bf' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-bf'])
        return 0

    @b_frames.setter
    def b_frames(self, b_frames_value: int | None):
        """
        Sets the B Frames setting to the specified value.

        Parameters:
            b_frames_value: Value to use for the B Frames setting.

        Returns:
            None
        """
        if b_frames_value is None:
            self._ffmpeg_advanced_args.pop('-bf', 0)
        else:
            self._ffmpeg_advanced_args['-bf'] = str(b_frames_value)

    @property
    def refs(self) -> int:
        """
        Returns the value of the reference frames setting.

        Returns:
            Reference frames setting as an integer.
        """
        if '-refs' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-refs'])
        return 0

    @refs.setter
    def refs(self, refs_value: int | None):
        """
        Sets the reference frames setting to the specified value.

        Parameters:
            refs_value: Value to use for the reference frames setting.

        Returns:
            None
        """
        if refs_value is None:
            self._ffmpeg_advanced_args.pop('-refs', 0)
        else:
            self._ffmpeg_advanced_args['-refs'] = str(refs_value)

    @property
    def no_scenecut(self) -> bool:
        """
        Returns whether the no scenecut setting is enabled.

        Returns:
            Boolean that represents whether the no scenecut setting is enabled.
        """
        if '-no-scenecut' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['-no-scenecut']

            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, is_no_scenecut_enabled: bool):
        """
        Sets the no scenecut setting to the specified value.

        Parameters:
            is_no_scenecut_enabled: Boolean that represents whether the no scenecut setting is enabled.

        Returns:
            None
        """
        if is_no_scenecut_enabled:
            self._ffmpeg_advanced_args['-no-scenecut'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-no-scenecut', 0)

    @property
    def forced_idr(self) -> bool:
        """
        Returns whether the forced idr setting is enabled.

        Returns:
            Boolean that represents whether the forced idr setting is enabled.
        """
        if '-forced-idr' in self._ffmpeg_advanced_args:
            forced_idr_arg = self._ffmpeg_advanced_args['-forced-idr']

            return forced_idr_arg == '1'
        return False

    @forced_idr.setter
    def forced_idr(self, is_forced_idr_enabled: bool):
        """
        Sets the forced idr setting to the specified value.

        Parameters:
            is_forced_idr_enabled: Boolean that represents whether the forced idr setting is enabled.

        Returns:
            None
        """
        if is_forced_idr_enabled:
            self._ffmpeg_advanced_args['-forced-idr'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-forced-idr', 0)

    @property
    def b_adapt(self) -> bool:
        """
        Returns whether the B adapt setting is enabled.

        Returns:
            Boolean that represents whether the B adapt setting is enabled.
        """
        if '-b_adapt' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['-b_adapt']

            return b_adapt_arg == '1'
        return False

    @b_adapt.setter
    def b_adapt(self, is_b_adapt_enabled: bool):
        """
        Sets the B adapt setting to the specified value.

        Parameters:
            is_b_adapt_enabled: Boolean that represents whether the B adapt setting is enabled.

        Returns:
            None
        """
        if is_b_adapt_enabled:
            self._ffmpeg_advanced_args['-b_adapt'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-b_adapt', 0)

    @property
    def spatial_aq(self) -> bool:
        """
        Returns whether the spatial AQ setting is enabled.

        Returns:
            Boolean that represents whether the spatial AQ setting is enabled.
        """
        if '-spatial-aq' in self._ffmpeg_advanced_args:
            spatial_aq_arg = self._ffmpeg_advanced_args['-spatial-aq']

            return spatial_aq_arg == '1'
        return False

    @spatial_aq.setter
    def spatial_aq(self, is_spatial_aq_enabled: bool):
        """
        Sets the spatial AQ setting to the specified value.

        Parameters:
            is_spatial_aq_enabled: Boolean that represents whether the spatial AQ setting is enabled.

        Returns:
            None
        """
        if is_spatial_aq_enabled:
            self._ffmpeg_advanced_args['-spatial-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-spatial-aq', 0)

    @property
    def temporal_aq(self) -> bool:
        """
        Returns whether the temporal AQ setting is enabled.

        Returns:
            Boolean that represents whether the temporal AQ setting is enabled.
        """
        if '-temporal-aq' in self._ffmpeg_advanced_args:
            temporal_aq_arg = self._ffmpeg_advanced_args['-temporal-aq']

            return temporal_aq_arg == '1'
        return False

    @temporal_aq.setter
    def temporal_aq(self, is_temporal_aq_enabled: bool):
        """
        Sets the temporal AQ setting to the specified value.

        Parameters:
            is_temporal_aq_enabled: Boolean that represents whether the temporal AQ setting is enabled.

        Returns:
            None
        """
        if is_temporal_aq_enabled:
            self._ffmpeg_advanced_args['-temporal-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-temporal-aq', 0)

    @property
    def non_ref_p(self) -> bool:
        """
        Returns whether the non-reference P frames setting is enabled.

        Returns:
            Boolean that represents whether the non-reference P frames setting is enabled.
        """
        if '-nonref_p' in self._ffmpeg_advanced_args:
            non_ref_p_arg = self._ffmpeg_advanced_args['-nonref_p']

            return non_ref_p_arg == '1'
        return False

    @non_ref_p.setter
    def non_ref_p(self, is_non_ref_p_enabled: bool):
        """
        Sets the non-references P frames setting to the specified value.

        Parameters:
            is_non_ref_p_enabled: Boolean that represents whether the non-reference P frames setting is enabled.

        Returns:
            None
        """
        if is_non_ref_p_enabled:
            self._ffmpeg_advanced_args['-nonref_p'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-nonref_p', 0)

    @property
    def strict_gop(self) -> bool:
        """
        Returns whether the strict GOP setting is enabled.

        Returns:
            Boolean that represents whether the strict GOP setting is enabled.
        """
        if '-strict_gop' in self._ffmpeg_advanced_args:
            strict_gop_arg = self._ffmpeg_advanced_args['-strict_gop']

            return strict_gop_arg == '1'
        return False

    @strict_gop.setter
    def strict_gop(self, is_strict_gop_enabled: bool):
        """
        Sets the strict GOP setting to the specified value.

        Parameters:
            is_strict_gop_enabled: Boolean that represents whether the strict GOP setting is enabled.

        Returns:
            None
        """
        if is_strict_gop_enabled:
            self._ffmpeg_advanced_args['-strict_gop'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-strict_gop', 0)

    @property
    def aq_strength(self) -> int:
        """
        Returns the value of the AQ strength setting.

        Returns:
            AQ strength setting as an integer.
        """
        if '-aq-strength' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-aq-strength'])
        return 8

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: int | None):
        """
        Sets the AQ strength setting to the specified value.

        Parameters:
            aq_strength_value: Value to use for the AQ strength setting.

        Returns:
            None
        """
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('-aq-strength', 0)
        else:
            self._ffmpeg_advanced_args['-aq-strength'] = str(aq_strength_value)

    @property
    def bluray_compat(self) -> bool:
        """
        Returns whether the bluray compatibility setting is enabled.

        Returns:
            Boolean that represents whether the bluray compatibility setting is enabled.
        """
        if '-bluray-compat' in self._ffmpeg_advanced_args:
            bluray_compat_arg = self._ffmpeg_advanced_args['-bluray-compat']

            return bluray_compat_arg == '1'
        return False

    @bluray_compat.setter
    def bluray_compat(self, is_bluray_compat_enabled: bool):
        """
        Sets the bluray compatibility setting to the specified value.

        Parameters:
            is_bluray_compat_enabled: Boolean that represents whether the bluray compatibility setting is enabled.

        Returns:
            None
        """
        if is_bluray_compat_enabled:
            self._ffmpeg_advanced_args['-bluray-compat'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-bluray-compat', 0)

    @property
    def weighted_pred(self) -> bool:
        """
        Returns whether the weighted prediction setting is enabled.

        Returns:
            Boolean that represents whether the weighted prediction setting is enabled.
        """
        if '-weighted_pred' in self._ffmpeg_advanced_args:
            weighted_pred_arg = self._ffmpeg_advanced_args['-weighted_pred']

            return weighted_pred_arg == '1'
        return False

    @weighted_pred.setter
    def weighted_pred(self, is_weighted_pred_enabled: bool):
        """
        Sets the weighted prediction setting to the specified value.

        Parameters:
            is_weighted_pred_enabled: Boolean that represents whether the weighted prediction setting is enabled.

        Returns:
            None
        """
        if is_weighted_pred_enabled:
            self._ffmpeg_advanced_args['-weighted_pred'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-weighted_pred', 0)

    @property
    def coder(self) -> int:
        """
        Returns the index of the coder setting.

        Returns:
            Coder setting as an index using the CODER variable.
        """
        if '-coder' in self._ffmpeg_advanced_args:
            coder_arg = self._ffmpeg_advanced_args['-coder']

            return self.CODER.index(coder_arg)
        return 0

    @coder.setter
    def coder(self, coder_index: int | None):
        """
        Sets the coder setting to the specified index.

        Parameters:
            coder_index: Index from the CODER variable.

        Returns:
            None
        """
        if coder_index and 0 < coder_index < H264Nvenc.CODER_LENGTH:
            self._ffmpeg_advanced_args['-coder'] = self.CODER[coder_index]
        else:
            self._ffmpeg_advanced_args.pop('-coder', 0)

    @property
    def b_ref_mode(self) -> int:
        """
        Returns the index of the B reference mode setting.

        Returns:
            B reference mode setting as an index using the BREF_MODE variable.
        """
        if '-b_ref_mode' in self._ffmpeg_advanced_args:
            b_ref_mode_arg = self._ffmpeg_advanced_args['-b_ref_mode']

            return self.BREF_MODE.index(b_ref_mode_arg)
        return 0

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index: int | None):
        """
        Sets the B reference mode setting to the specified value.

        Parameters:
            b_ref_mode_index: Index from the BREF_MODE variable.

        Returns:
            None
        """
        if b_ref_mode_index and 0 < b_ref_mode_index < H264Nvenc.BREF_MODE_LENGTH:
            self._ffmpeg_advanced_args['-b_ref_mode'] = self.BREF_MODE[b_ref_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('-b_ref_mode', 0)

    @property
    def encode_pass(self) -> None:
        """
        Returns the value of the encode pass setting.

        Returns:
            None for compatibility with the FFmpegArgs class in the encoding module.
        """
        return None  # Returns None for compatibility.

    def get_ffmpeg_advanced_args(self) -> dict:
        """
        Returns the advanced ffmpeg args of the codec.

        Returns:
            Dictionary that contains the advanced ffmpeg args of the codec if advanced args are enabled.
        """
        if self.is_advanced_enabled:
            return self._ffmpeg_advanced_args
        return {}


class HevcNvenc:
    """Class that configures all HEVC Nvenc codec settings available for Render Watch. """

    PRESET = [
        'default', 'slow', 'medium', 'fast', 'lossless', 'losslesshp', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
    PRESET_LENGTH = len(PRESET)

    PROFILE = ['auto', 'main', 'main10', 'rext']
    PROFILE_LENGTH = len(PROFILE)

    LEVEL = [
        'auto', '1.0', '2.0', '2.1', '3.0', '3.1', '4.0', '4.1', '5.0', '5.1', '5.2', '6.0', '6.1', '6.2'
    ]
    LEVEL_LENGTH = len(LEVEL)

    TUNE = ['auto', 'hq', 'll', 'ull', 'lossless']
    TUNE_LENGTH = len(TUNE)

    RATE_CONTROL = ['auto', 'constqp', 'vbr', 'cbr', 'cbr_ld_hq', 'cbr_hq', 'vbr_hq']
    RATE_CONTROL_LENGTH = len(RATE_CONTROL)

    MULTI_PASS = ['auto', 'disabled', 'qres', 'fullres']
    MULTI_PASS_LENGTH = len(MULTI_PASS)

    BREF_MODE = ['auto', 'disabled', 'each', 'middle']
    BREF_MODE_LENGTH = len(BREF_MODE)

    def __init__(self):
        """Initializes the HevcNvenc class with all necessary variables for the codec's settings."""
        self.is_advanced_enabled = False
        self.is_qp_custom_enabled = False
        self.is_dual_pass_enabled = False
        self._is_qp_enabled = True
        self._is_bitrate_enabled = False
        self._ffmpeg_advanced_args = {}
        self.ffmpeg_args = {
            '-c:v': 'hevc_nvenc',
            '-qp': '20'
        }

    @property
    def is_qp_enabled(self) -> bool:
        """
        Returns whether QP is enabled for the rate type settings.

        Returns:
            Boolean that represents whether QP is enabled for the rate type settings.
        """
        return self._is_qp_enabled


    @property
    def is_bitrate_enabled(self) -> bool:
        """
        Returns whether bitrate is enabled for the rate type settings.

        Returns:
            Boolean that represents whether bitrate is enabled for the rate type settings.
        """
        return self._is_bitrate_enabled

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def qp(self) -> int:
        """
        Returns the value of the QP setting.

        Returns:
            QP setting as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-qp'])
        return 20

    @qp.setter
    def qp(self, qp_value: int | None):
        """
        Sets the QP setting to the specified value.

        Parameters:
            qp_value: Value to use for the QP setting.

        Returns:
            None
        """
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.bitrate = None
            self._is_qp_enabled = True
            self._is_bitrate_enabled = False

    @property
    def bitrate(self) -> int:
        """
        Returns the value of the bitrate setting.

        Returns:
            Bitrate setting as an integer.
        """
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']

            return int(bitrate_arg.split('k')[0])
        return 2500

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate setting to the specified value.

        Parameters:
            bitrate_value: Value to use for the bitrate setting.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.qp = None
            self._is_qp_enabled = False
            self._is_bitrate_enabled = True

    @property
    def profile(self) -> int:
        """
        Returns the index of the profile setting.

        Returns:
            Profile setting as an index using the PROFILE variable.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']

            return self.PROFILE.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            profile_index: Index from the PROFILE variable.

        Returns:
            None
        """
        if profile_index and 0 < profile_index < HevcNvenc.PROFILE_LENGTH:
            self.ffmpeg_args['-profile:v'] = self.PROFILE[profile_index]
        else:
            self.ffmpeg_args.pop('-profile:v', 0)

    @property
    def preset(self) -> int:
        """
        Returns the index of the preset setting.

        Returns:
            Profile setting as an index using the PRESET variable.
        """
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        """
        Sets the preset setting to the specified index.

        Parameters:
            preset_index: Index from the PRESET variable.

        Returns:
            None
        """
        if preset_index and 0 < preset_index < HevcNvenc.PRESET_LENGTH:
            self.ffmpeg_args['-preset'] = self.PRESET[preset_index]
        else:
            self.ffmpeg_args.pop('-preset', 0)

    @property
    def level(self) -> int:
        """
        Returns the index of the level setting.

        Returns:
            Level setting as an index using the LEVEL variable.
        """
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']

            return self.LEVEL.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index: int | None):
        """
        Sets the level setting to the specified index.

        Parameters:
            level_index: Index from the LEVEL variable.

        Returns:
            None
        """
        if level_index and 0 < level_index < HevcNvenc.LEVEL_LENGTH:
            self.ffmpeg_args['-level'] = self.LEVEL[level_index]
        else:
            self.ffmpeg_args.pop('-level', 0)

    @property
    def tune(self) -> int:
        """
        Returns the index of the tune setting.

        Returns:
            Tune setting as an index using the TUNE variable.
        """
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']

            return self.TUNE.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index: int | None):
        """
        Sets the tune setting to the specified index.

        Parameters:
            tune_index: Index from the TUNE variable.

        Returns:
            None
        """
        if tune_index and 0 < tune_index < HevcNvenc.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def multi_pass(self) -> int:
        """
        Returns the index of the multi-pass setting.

        Returns:
            Multi-pass setting as an index using the MULTI_PASS variable.
        """
        if '-multipass' in self.ffmpeg_args:
            multi_pass_arg = self.ffmpeg_args['-multipass']

            return self.MULTI_PASS.index(multi_pass_arg)
        return 0

    @multi_pass.setter
    def multi_pass(self, multi_pass_index: int | None):
        """
        Sets the multi-pass setting to the specified index.

        Parameters:
            multi_pass_index: Index from the MULTI_PASS variable.

        Returns:
            None
        """
        if multi_pass_index and 0 < multi_pass_index < HevcNvenc.MULTI_PASS_LENGTH:
            self.ffmpeg_args['-multipass'] = self.MULTI_PASS[multi_pass_index]
        else:
            self.ffmpeg_args.pop('-multipass', 0)

    @property
    def cbr(self) -> bool:
        """
        Returns whether the constant bitrate setting is enabled.

        Returns:
            Boolean that represents whether the bitrate setting is enabled.
        """
        if '-cbr' in self.ffmpeg_args:
            cbr_arg = self.ffmpeg_args['-cbr']

            return cbr_arg == '1'
        return False

    @cbr.setter
    def cbr(self, is_cbr_enabled: bool):
        """
        Sets the constant bitrate setting to the specified value.

        Parameters:
            is_cbr_enabled: Boolean that represents whether the constant bitrate setting is enabled.

        Returns:
            None
        """
        if is_cbr_enabled:
            self.ffmpeg_args['-cbr'] = '1'
        else:
            self.ffmpeg_args.pop('-cbr', 0)

    @property
    def qp_i(self) -> int:
        """
        Returns the value of the QP I setting.

        Returns:
            QP I setting as a float.
        """
        if '-init_qpI' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpI'])
        return 20

    @qp_i.setter
    def qp_i(self, qp_i_value: int | None):
        """
        Sets the QP I setting to the specified value.

        Parameters:
            qp_i_value: Value to use for the QP I setting.

        Returns:
            None
        """
        if qp_i_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpI', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpI'] = str(qp_i_value)

    @property
    def qp_p(self) -> int:
        """
        Returns the value of the QP P setting.

        Returns:
            QP P setting as a float.
        """
        if '-init_qpP' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpP'])
        return 20

    @qp_p.setter
    def qp_p(self, qp_p_value: int | None):
        """
        Sets the QP P setting to the specified value.

        Parameters:
            qp_p_value: Value to use for the QP P setting.

        Returns:
            None
        """
        if qp_p_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpP', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpP'] = str(qp_p_value)

    @property
    def qp_b(self) -> int:
        """
        Returns the value of the QP B setting.

        Returns:
            QP B setting as a float.
        """
        if '-init_qpB' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-init_qpB'])
        return 20

    @qp_b.setter
    def qp_b(self, qp_b_value: int | None):
        """
        Sets the QP B setting to the specified value.

        Parameters:
            qp_b_value: Value to use for the QP B setting.

        Returns:
            None
        """
        if qp_b_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpB', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpB'] = str(qp_b_value)

    @property
    def rc(self) -> int:
        """
        Returns the index of the rate control setting.

        Returns:
            Rate control setting as an index using the RATE_CONTROL variable.
        """
        if '-rc' in self._ffmpeg_advanced_args:
            rc_arg = self._ffmpeg_advanced_args['-rc']

            return self.RATE_CONTROL.index(rc_arg)
        return 0

    @rc.setter
    def rc(self, rc_index: int | None):
        """
        Sets the rate control setting to the specified index.

        Parameters:
            rc_index: Index from the RATE_CONTROL variable.

        Returns:
            None
        """
        if rc_index and 0 < rc_index < HevcNvenc.RATE_CONTROL_LENGTH:
            self._ffmpeg_advanced_args['-rc'] = self.RATE_CONTROL[rc_index]
        else:
            self._ffmpeg_advanced_args.pop('-rc', 0)

    @property
    def rc_lookahead(self) -> int:
        """
        Returns the value of the rate control lookahead setting.

        Returns:
            Rate control lookahead setting as an integer.
        """
        if '-rc-lookahead' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-rc-lookahead'])
        return 0

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value: int | None):
        """
        Sets the rate control lookahead setting to the specified value.

        Parameters:
            rc_lookahead_value: Value to use for the rate control lookahead setting.

        Returns:
            None
        """
        if rc_lookahead_value is None:
            self._ffmpeg_advanced_args.pop('-rc-lookahead', 0)
        else:
            self._ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead_value)

    @property
    def surfaces(self) -> int:
        """
        Returns the value of the surfaces setting.

        Returns:
            Surfaces setting as an integer.
        """
        if '-surfaces' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-surfaces'])
        return 8

    @surfaces.setter
    def surfaces(self, surfaces_value: int | None):
        """
        Sets the surfaces setting to the specified value.

        Parameters:
            surfaces_value: Value to use for the surfaces setting.

        Returns:
            None
        """
        if surfaces_value is None:
            self._ffmpeg_advanced_args.pop('-surfaces', 0)
        else:
            self._ffmpeg_advanced_args['-surfaces'] = str(surfaces_value)

    @property
    def b_frames(self) -> int:
        """
        Returns the value of the B frames setting.

        Returns:
            B frames setting as an integer.
        """
        if '-bf' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-bf'])
        return 0

    @b_frames.setter
    def b_frames(self, b_frames_value: int | None):
        """
        Sets the B frames setting to the specified value.

        Parameters:
            b_frames_value: Value to use for the B frames setting.

        Returns:
            None
        """
        if b_frames_value is None:
            self._ffmpeg_advanced_args.pop('-bf', 0)
        else:
            self._ffmpeg_advanced_args['-bf'] = str(b_frames_value)

    @property
    def refs(self) -> int:
        """
        Returns the value of the reference frames setting.

        Returns:
            Reference frames setting as an integer.
        """
        if '-refs' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-refs'])
        return 0

    @refs.setter
    def refs(self, refs_value: int | None):
        """
        Sets the reference frames setting to the specified value.

        Parameters:
            refs_value: Value to use for the reference frames setting.

        Returns:
            None
        """
        if refs_value is None:
            self._ffmpeg_advanced_args.pop('-refs', 0)
        else:
            self._ffmpeg_advanced_args['-refs'] = str(refs_value)

    @property
    def no_scenecut(self) -> bool:
        """
        Returns whether the no scenecut setting is enabled.

        Returns:
            Boolean that represents whether the no scenecut setting is enabled.
        """
        if '-no-scenecut' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['-no-scenecut']

            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, is_no_scenecut_enabled: bool):
        """
        Sets the no scenecut setting to the specified value.

        Parameters:
            is_no_scenecut_enabled: Boolean that represents whether the no scenecut setting is enabled.

        Returns:
            None
        """
        if is_no_scenecut_enabled:
            self._ffmpeg_advanced_args['-no-scenecut'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-no-scenecut', 0)

    @property
    def forced_idr(self) -> bool:
        """
        Returns whether the forced idr setting is enabled.

        Returns:
            Boolean that represents whether the forced idr setting is enabled.
        """
        if '-forced-idr' in self._ffmpeg_advanced_args:
            forced_idr_arg = self._ffmpeg_advanced_args['-forced-idr']

            return forced_idr_arg == '1'
        return False

    @forced_idr.setter
    def forced_idr(self, is_forced_idr_enabled: bool):
        """
        Sets the forced idr setting to the specified value.

        Parameters:
            is_forced_idr_enabled: Boolean that represents whether the forced idr setting is enabled.

        Returns:
            None
        """
        if is_forced_idr_enabled:
            self._ffmpeg_advanced_args['-forced-idr'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-forced-idr', 0)

    @property
    def spatial_aq(self) -> bool:
        """
        Returns whether the spatial AQ setting is enabled.

        Returns:
            Boolean that represents whether the spatial AQ setting is enabled.
        """
        if '-spatial-aq' in self._ffmpeg_advanced_args:
            spatial_aq_arg = self._ffmpeg_advanced_args['-spatial-aq']

            return spatial_aq_arg == '1'
        return False

    @spatial_aq.setter
    def spatial_aq(self, is_spatial_aq_enabled: bool):
        """
        Sets the spatial AQ setting to the specified value.

        Parameters:
            is_spatial_aq_enabled: Boolean that represents whether the spatial AQ setting is enabled.

        Returns:
            None
        """
        if is_spatial_aq_enabled:
            self._ffmpeg_advanced_args['-spatial-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-spatial-aq', 0)

    @property
    def temporal_aq(self) -> bool:
        """
        Returns whether the temporal AQ setting is enabled.

        Returns:
            Boolean that represents whether the temporal AQ setting is enabled.
        """
        if '-temporal-aq' in self._ffmpeg_advanced_args:
            temporal_aq_arg = self._ffmpeg_advanced_args['-temporal-aq']

            return temporal_aq_arg == '1'
        return False

    @temporal_aq.setter
    def temporal_aq(self, is_temporal_aq_enabled: bool):
        """
        Sets the temporal AQ setting to the specified value.

        Parameters:
            is_temporal_aq_enabled: Boolean that represents whether the temporal AQ setting is enabled.

        Returns:
            None
        """
        if is_temporal_aq_enabled:
            self._ffmpeg_advanced_args['-temporal-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-temporal-aq', 0)

    @property
    def non_ref_p(self) -> bool:
        """
        Returns whether the non-reference P frames setting is enabled.

        Returns:
            Boolean that represents whether the non-reference P frames setting is enabled.
        """
        if '-nonref_p' in self._ffmpeg_advanced_args:
            non_ref_p_arg = self._ffmpeg_advanced_args['-nonref_p']

            return non_ref_p_arg == '1'
        return False

    @non_ref_p.setter
    def non_ref_p(self, is_non_ref_p_enabled: bool):
        """
        Sets the non-reference P frames setting to the specified value.

        Parameters:
            is_non_ref_p_enabled: Boolean that represents whether the non-reference P frames setting is enabled.

        Returns:
            None
        """
        if is_non_ref_p_enabled:
            self._ffmpeg_advanced_args['-nonref_p'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-nonref_p', 0)

    @property
    def strict_gop(self) -> bool:
        """
        Returns whether the strict GOP setting is enabled.

        Returns:
            Boolean that represents whether the strict GOP setting is enabled.
        """
        if '-strict_gop' in self._ffmpeg_advanced_args:
            strict_gop_arg = self._ffmpeg_advanced_args['-strict_gop']

            return strict_gop_arg == '1'
        return False

    @strict_gop.setter
    def strict_gop(self, is_strict_gop_enabled: bool):
        """
        Sets the strict GOP setting to the specified value.

        Parameters:
            is_strict_gop_enabled: Boolean that represents whether the strict GOP setting is enabled.

        Returns:
            None
        """
        if is_strict_gop_enabled:
            self._ffmpeg_advanced_args['-strict_gop'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-strict_gop', 0)

    @property
    def aq_strength(self) -> int:
        """
        Returns the value of the AQ strength setting.

        Returns:
            AQ strength setting as an integer.
        """
        if '-aq-strength' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-aq-strength'])
        return 8

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: int | None):
        """
        Sets the AQ strength setting to the specified value.

        Parameters:
            aq_strength_value: Value to use for the AQ strength setting.

        Returns:
            None
        """
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('-aq-strength', 0)
        else:
            self._ffmpeg_advanced_args['-aq-strength'] = str(aq_strength_value)

    @property
    def bluray_compat(self) -> bool:
        """
        Returns whether the bluray compatibility setting is enabled.

        Returns:
            Boolean that represents whether the bluray compatibility setting is enabled.
        """
        if '-bluray-compat' in self._ffmpeg_advanced_args:
            bluray_compat_arg = self._ffmpeg_advanced_args['-bluray-compat']

            return bluray_compat_arg == '1'
        return False

    @bluray_compat.setter
    def bluray_compat(self, is_bluray_compat_enabled: bool):
        """
        Sets the bluray compatibility setting to the specified value.

        Parameters:
            is_bluray_compat_enabled: Boolean that represents whether the bluray compatibility setting is enabled.

        Returns:
            None
        """
        if is_bluray_compat_enabled:
            self._ffmpeg_advanced_args['-bluray-compat'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-bluray-compat', 0)

    @property
    def weighted_pred(self) -> bool:
        """
        Returns whether the weighed prediction setting is enabled.

        Returns:
            Boolean that represents whether the weighted prediction setting is enabled.
        """
        if '-weighted_pred' in self._ffmpeg_advanced_args:
            weighted_pred_arg = self._ffmpeg_advanced_args['-weighted_pred']

            return weighted_pred_arg == '1'
        return False

    @weighted_pred.setter
    def weighted_pred(self, is_weighted_pred_enabled: bool):
        """
        Sets the weighted prediction setting to the specified value.

        Parameters:
            is_weighted_pred_enabled: Boolean that represents whether the weighted prediction setting is enabled.

        Returns:
            None
        """
        if is_weighted_pred_enabled:
            self._ffmpeg_advanced_args['-weighted_pred'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-weighted_pred', 0)

    @property
    def b_ref_mode(self) -> int:
        """
        Returns the index of the B reference mode setting.

        Returns:
            B reference mode setting as an index using the BREF_MODE variable.
        """
        if '-b_ref_mode' in self._ffmpeg_advanced_args:
            b_ref_mode_arg = self._ffmpeg_advanced_args['-b_ref_mode']

            return self.BREF_MODE.index(b_ref_mode_arg)
        return 0

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index: int | None):
        """
        Sets the B reference mode setting to the specified index.

        Parameters:
            b_ref_mode_index: Index from the BREF_MODE variable.

        Returns:
            None
        """
        if b_ref_mode_index and 0 < b_ref_mode_index < HevcNvenc.BREF_MODE_LENGTH:
            self._ffmpeg_advanced_args['-b_ref_mode'] = self.BREF_MODE[b_ref_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('-b_ref_mode', 0)

    @property
    def tier(self) -> bool:
        """
        Returns whether the high-tier setting is enabled.

        Returns:
            Boolean that represents whether the high-tier setting is enabled.
        """
        if '-tier' in self._ffmpeg_advanced_args:
            tier_value = self._ffmpeg_advanced_args['-tier']

            return tier_value == '1'
        return False

    @tier.setter
    def tier(self, is_tier_high_enabled: bool):
        """
        Sets the high-tier setting to the specified value.

        Parameters:
            is_tier_high_enabled: Boolean that represents whether the high-tier setting is enabled.

        Returns:
            None
        """
        if is_tier_high_enabled:
            self._ffmpeg_advanced_args['-tier'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-tier', 0)

    @property
    def encode_pass(self) -> None:
        """
        Returns the value of the encode pass setting.

        Returns:
            None for compatibility with the FFmpegArgs class in the encoding module.
        """
        return None

    def get_ffmpeg_advanced_args(self) -> dict:
        """
        Returns the advanced ffmpeg args of the codec.

        Returns:
            Dictionary that contains the advanced ffmpeg args of the codec if advanced args are enabled.
        """
        if self.is_advanced_enabled:
            return self._ffmpeg_advanced_args
        return {}


class VP9:
    """Class that configures all VP9 codec settings available for Render Watch."""

    QUALITY = ('auto', 'good', 'best', 'realtime')
    QUALITY_LENGTH = len(QUALITY)

    SPEED = ('auto', '0', '1', '2', '3', '4', '5')
    SPEED_LENGTH = len(SPEED)

    CRF_MIN = 0.0
    CRF_MAX = 63.0

    BITRATE_MIN = 0
    BITRATE_MAX = 99999

    def __init__(self):
        """Initializes the VP9 class with all necessary variables for the codec's options."""
        self._is_crf_enabled = True
        self._is_bitrate_enabled = False
        self._is_constrained_enabled = False
        self._is_average_bitrate_enabled = True
        self._is_vbr_bitrate_enabled = False
        self._is_constant_bitrate_enabled = False
        self.ffmpeg_args = {
            '-c:v': 'libvpx-vp9',
            '-b:v': '0k'
        }

    @property
    def is_crf_enabled(self) -> bool:
        """
        Returns whether CRF is enabled for the rate type settings.

        Returns:
            Boolean that represents whether CRF is enabled for the rate type settings.
        """
        return self._is_crf_enabled

    @is_crf_enabled.setter
    def is_crf_enabled(self, is_enabled: bool):
        """
        Sets whether CRF is enabled for the rate type settings.

        Returns:
            None
        """
        self._is_crf_enabled = is_enabled

        if is_enabled:
            self.is_bitrate_enabled = False
            self.is_constrained_enabled = False

    @property
    def is_bitrate_enabled(self) -> bool:
        """
        Returns whether bitrate is enabled for the rate type settings.

        Returns:
            Boolean that represents whether bitrate is enabled for the rate type settings.
        """
        return self._is_bitrate_enabled

    @is_bitrate_enabled.setter
    def is_bitrate_enabled(self, is_enabled: bool):
        """
        Sets whether bitrate is enabled for the rate type settings.

        Returns:
            None
        """
        self._is_bitrate_enabled = is_enabled

        if is_enabled:
            self.is_crf_enabled = False
            self.is_constrained_enabled = False

    @property
    def is_constrained_enabled(self) -> bool:
        """
        Returns whether constrained is enabled for the rate type settings.

        Returns:
            Boolean that represents whether constrained is enabled for the rate type settings.
        """
        return self._is_constrained_enabled

    @is_constrained_enabled.setter
    def is_constrained_enabled(self, is_enabled: bool):
        """
        Sets whether constrained is enabled for the rate type settings.

        Returns:
            None
        """
        self._is_constrained_enabled = is_enabled

        if is_enabled:
            self.is_crf_enabled = False
            self.is_bitrate_enabled = False

    @property
    def is_average_bitrate_enabled(self) -> bool:
        """
        Returns whether average bitrate is enabled for the bitrate type settings.

        Returns:
            Boolean that represents whether average bitrate is enabled for the bitrate type settings.
        """
        return self._is_average_bitrate_enabled

    @is_average_bitrate_enabled.setter
    def is_average_bitrate_enabled(self, is_enabled: bool):
        """
        Sets whether average bitrate is enabled for the bitrate type settings.

        Returns:
            None
        """
        self._is_average_bitrate_enabled = is_enabled

        if is_enabled:
            self._is_vbr_bitrate_enabled = False
            self._is_constant_bitrate_enabled = False

    @property
    def is_vbr_bitrate_enabled(self) -> bool:
        """
        Returns whether vbr bitrate is enabled for the bitrate type settings.

        Returns:
            Boolean that represents whether vbr bitrate is enabled for the bitrate type settings.
        """
        return self._is_vbr_bitrate_enabled

    @is_vbr_bitrate_enabled.setter
    def is_vbr_bitrate_enabled(self, is_enabled: bool):
        """
        Sets whether vbr bitrate is enabled for the bitrate type settings.

        Returns:
            None
        """
        self._is_vbr_bitrate_enabled = is_enabled

        if is_enabled:
            self._is_average_bitrate_enabled = False
            self._is_constant_bitrate_enabled = False

    @property
    def is_constant_bitrate_enabled(self) -> bool:
        """
        Returns whether constant bitrate is enabled for the bitrate type settings.

        Returns:
            Boolean that represents whether constant bitrate is enabled for the bitrate type settings.
        """
        return self._is_constant_bitrate_enabled

    @is_constant_bitrate_enabled.setter
    def is_constant_bitrate_enabled(self, is_enabled: bool):
        """
        Sets whether constant bitrate is enabled for the bitrate type settings.

        Returns:
            None
        """
        self._is_constant_bitrate_enabled = is_enabled

        if is_enabled:
            self.is_average_bitrate_enabled = False
            self.is_vbr_bitrate_enabled = False

    @property
    def codec_name(self) -> str:
        """
        Returns the name of the codec.

        Returns:
            Codec's name as a string.
        """
        return self.ffmpeg_args['-c:v']

    @property
    def quality(self) -> int:
        """
        Returns what the quality option is set to.

        Returns:
            Quality option as an index using the QUALITY variable.
        """
        if '-deadline' in self.ffmpeg_args:
            quality_arg = self.ffmpeg_args['-deadline']

            return self.QUALITY.index(quality_arg)
        return 0

    @quality.setter
    def quality(self, quality_index: int | None):
        """
        Sets the quality option.

        Parameters:
            quality_index: Index from the QUALITY variable.

        Returns:
            None
        """
        if quality_index and 0 < quality_index < VP9.QUALITY_LENGTH:
            self.ffmpeg_args['-deadline'] = self.QUALITY[quality_index]
        else:
            self.ffmpeg_args.pop('-deadline', 0)

    @property
    def speed(self) -> int:
        """
        Returns what the speed option is set to.

        Returns:
            Speed option as an index using the SPEED variable.
        """
        if '-cpu-used' in self.ffmpeg_args:
            speed_arg = self.ffmpeg_args['-cpu-used']

            return self.SPEED.index(speed_arg)
        return 0

    @speed.setter
    def speed(self, speed_index: int | None):
        """
        Sets the speed option.

        Parameters:
            speed_index: Index from the SPEED variable.

        Returns:
            None
        """
        if speed_index and 0 < speed_index < VP9.SPEED_LENGTH:
            self.ffmpeg_args['-cpu-used'] = self.SPEED[speed_index]
        else:
            self.ffmpeg_args.pop('-cpu-used', 0)

    @property
    def bitrate(self) -> int:
        """
        Returns what the bitrate option is set to.

        Returns:
            Bitrate as an int.
        """
        bitrate_arg = self.ffmpeg_args['-b:v']

        return int(bitrate_arg.split('k')[0])

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        """
        Sets the bitrate option to the specified value.

        Parameters:
            bitrate_value: The value to set the bitrate to.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args['-b:v'] = '2500k'
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'

    @property
    def crf(self) -> int:
        """
        Returns what the CRF option is set to.

        Returns:
            CRF as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-crf'])
        return 30

    @crf.setter
    def crf(self, crf_value: int | None):
        """
        Sets the CRF option to the specified value.

        Parameters:
            crf_value: The value to set the CRF option to.

        Returns:
            None
        """
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)

    @property
    def maxrate(self) -> int:
        """
        Returns what the maxrate option is set to.

        Returns:
            Maxrate as an int.
        """
        if '-maxrate' in self.ffmpeg_args:
            maxrate_arg = self.ffmpeg_args['-maxrate']

            return int(maxrate_arg.split('k')[0])
        return 2500

    @maxrate.setter
    def maxrate(self, maxrate_value: int | None):
        """
        Sets the maxrate option to the specified value.

        Parameters:
            maxrate_value: The value to set the maxrate option to.

        Returns:
            None
        """
        if maxrate_value is None:
            self.ffmpeg_args.pop('-maxrate', 0)
        else:
            self.ffmpeg_args['-maxrate'] = str(maxrate_value) + 'k'

    @property
    def minrate(self) -> int:
        """
        Returns what the minrate option is set to.

        Returns:
            Minrate as an int.
        """
        if '-minrate' in self.ffmpeg_args:
            minrate_arg = self.ffmpeg_args['-minrate']

            return int(minrate_arg.split('k')[0])
        return 2500

    @minrate.setter
    def minrate(self, minrate_value: int | None):
        """
        Sets the minrate option to the specified value.

        Parameters:
            minrate_value: The value to set the minrate option to.

        Returns:
            None
        """
        if minrate_value is None:
            self.ffmpeg_args.pop('-minrate', 0)
        else:
            self.ffmpeg_args['-minrate'] = str(minrate_value) + 'k'

    @property
    def encode_pass(self) -> int:
        """
        Returns what the encode pass option is set to.

        Returns:
            Encode pass as an int.
        """
        if '-pass' in self.ffmpeg_args:
            return int(self.ffmpeg_args['-pass'])
        return 2500

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        """
        Sets the encode pass option to the specified value.

        Parameters:
            encode_pass_value: The value to set the encode pass option to.

        Returns:
            None
        """
        if encode_pass_value:
            self.ffmpeg_args['-pass'] = str(encode_pass_value)
        else:
            self.ffmpeg_args.pop('-pass', 0)

    @property
    def stats(self) -> str:
        """
        Returns what the stats option is set to.

        Returns:
            Stats as a string representing the file path to use.
        """
        if '-passlogfile' in self.ffmpeg_args:
            return self.ffmpeg_args['-passlogfile']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        """
        Sets the stats option to the specified value.

        Parameters:
            stats_file_path: File path string to set the stats option to.

        Returns:
            None
        """
        if stats_file_path:
            self.ffmpeg_args['-passlogfile'] = stats_file_path
        else:
            self.ffmpeg_args.pop('-passlogfile', 0)

    @property
    def row_multithreading(self) -> bool:
        """
        Returns what the row multithreading option is set to.

        Returns:
            Row multithreading as a boolean.
        """
        if '-row-mt' in self.ffmpeg_args:
            row_multithreading_arg = self.ffmpeg_args['-row-mt']

            return row_multithreading_arg == '1'
        return False

    @row_multithreading.setter
    def row_multithreading(self, is_row_multithreading_enabled: bool):
        """
        Sets the row multithreading option.

        Parameters:
            is_row_multithreading_enabled: Boolean value to set the row multithreading option to.

        Returns:
            None
        """
        if is_row_multithreading_enabled:
            self.ffmpeg_args['-row-mt'] = '1'
        else:
            self.ffmpeg_args.pop('-row-mt', 0)

    @staticmethod
    def get_ffmpeg_advanced_args() -> dict:
        """Null dictionary for compatibility with the encoding module for the FFmpegArgs class."""
        return {'': None}
