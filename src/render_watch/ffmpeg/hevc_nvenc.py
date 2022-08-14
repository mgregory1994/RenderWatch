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
