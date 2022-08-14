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
        return self._is_crf_enabled

    @property
    def is_qp_enabled(self) -> bool:
        return self._is_qp_enabled

    @property
    def is_bitrate_enabled(self) -> bool:
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
