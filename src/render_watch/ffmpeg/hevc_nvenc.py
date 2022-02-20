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
    """
    Stores all settings for the HEVC NVENC codec.
    """

    PRESET = [
        'default', 'slow', 'medium', 'fast', 'hp', 'hq', 'bd', 'll', 'llhq', 'llhp', 'lossless', 'losslesshp', 'p1',
        'p2', 'p3', 'p4', 'p5', 'p6', 'p7'
    ]
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
        self.ffmpeg_args = {
            '-c:v': 'hevc_nvenc',
            '-qp': '20.0'
        }
        self.is_advanced_enabled = False
        self.is_qp_custom_enabled = False
        self.is_dual_pass_enabled = False
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self) -> str:
        return self.ffmpeg_args['-c:v']

    @property
    def qp(self) -> float:
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return 20.0

    @qp.setter
    def qp(self, qp_value: float | None):
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.bitrate = None

    @property
    def bitrate(self) -> int:
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']

            return int(bitrate_arg.split('k')[0])
        return 2500

    @bitrate.setter
    def bitrate(self, bitrate_value: int | None):
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.qp = None

    @property
    def profile(self) -> int:
        """
        Returns profile as an index.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']

            return self.PROFILE.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index: int | None):
        if profile_index and 0 < profile_index < HevcNvenc.PROFILE_LENGTH:
            self.ffmpeg_args['-profile:v'] = self.PROFILE[profile_index]
        else:
            self.ffmpeg_args.pop('-profile:v', 0)

    @property
    def preset(self) -> int:
        """
        Returns preset as an index.
        """
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        if preset_index and 0 < preset_index < HevcNvenc.PRESET_LENGTH:
            self.ffmpeg_args['-preset'] = self.PRESET[preset_index]
        else:
            self.ffmpeg_args.pop('-preset', 0)

    @property
    def level(self) -> int:
        """
        Returns level as an index.
        """
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']

            return self.LEVEL.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index: int | None):
        if level_index and 0 < level_index < HevcNvenc.LEVEL_LENGTH:
            self.ffmpeg_args['-level'] = self.LEVEL[level_index]
        else:
            self.ffmpeg_args.pop('-level', 0)

    @property
    def tune(self) -> int:
        """
        Returns tune as an index.
        """
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']

            return self.TUNE.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index: int | None):
        if tune_index and 0 < tune_index < HevcNvenc.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def multi_pass(self) -> int:
        """
        Returns multi pass as an index.
        """
        if '-multipass' in self.ffmpeg_args:
            multi_pass_arg = self.ffmpeg_args['-multipass']

            return self.MULTI_PASS.index(multi_pass_arg)
        return 0

    @multi_pass.setter
    def multi_pass(self, multi_pass_index: int | None):
        if multi_pass_index and 0 < multi_pass_index < HevcNvenc.MULTI_PASS_LENGTH:
            self.ffmpeg_args['-multipass'] = self.MULTI_PASS[multi_pass_index]
        else:
            self.ffmpeg_args.pop('-multipass', 0)

    @property
    def cbr(self) -> bool:
        if '-cbr' in self.ffmpeg_args:
            cbr_arg = self.ffmpeg_args['-cbr']

            return cbr_arg == '1'
        return False

    @cbr.setter
    def cbr(self, is_cbr_enabled: bool):
        if is_cbr_enabled:
            self.ffmpeg_args['-cbr'] = '1'
        else:
            self.ffmpeg_args.pop('-cbr', 0)

    @property
    def qp_i(self) -> float:
        if '-init_qpI' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpI'])
        return 20.0

    @qp_i.setter
    def qp_i(self, qp_i_value: float | None):
        if qp_i_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpI', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpI'] = str(qp_i_value)

    @property
    def qp_p(self) -> float:
        if '-init_qpP' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpP'])
        return 20.0

    @qp_p.setter
    def qp_p(self, qp_p_value: float | None):
        if qp_p_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpP', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpP'] = str(qp_p_value)

    @property
    def qp_b(self) -> float:
        if '-init_qpB' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpB'])
        return 20.0

    @qp_b.setter
    def qp_b(self, qp_b_value: float | None):
        if qp_b_value is None:
            self._ffmpeg_advanced_args.pop('-init_qpB', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpB'] = str(qp_b_value)

    @property
    def rc(self) -> int:
        """
        Returns rate control as an index.
        """
        if '-rc' in self._ffmpeg_advanced_args:
            rc_arg = self._ffmpeg_advanced_args['-rc']

            return self.RATE_CONTROL.index(rc_arg)
        return 0

    @rc.setter
    def rc(self, rc_index: int | None):
        if rc_index and 0 < rc_index < HevcNvenc.RATE_CONTROL_LENGTH:
            self._ffmpeg_advanced_args['-rc'] = self.RATE_CONTROL[rc_index]
        else:
            self._ffmpeg_advanced_args.pop('-rc', 0)

    @property
    def rc_lookahead(self) -> int:
        if '-rc-lookahead' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-rc-lookahead'])
        return 0

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value: int | None):
        if rc_lookahead_value is None:
            self._ffmpeg_advanced_args.pop('-rc-lookahead', 0)
        else:
            self._ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead_value)

    @property
    def surfaces(self) -> int:
        if '-surfaces' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-surfaces'])
        return 8

    @surfaces.setter
    def surfaces(self, surfaces_value: int | None):
        if surfaces_value is None:
            self._ffmpeg_advanced_args.pop('-surfaces', 0)
        else:
            self._ffmpeg_advanced_args['-surfaces'] = str(surfaces_value)

    @property
    def b_frames(self) -> int:
        if '-bf' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-bf'])
        return 0

    @b_frames.setter
    def b_frames(self, b_frames_value: int | None):
        if b_frames_value is None:
            self._ffmpeg_advanced_args.pop('-bf', 0)
        else:
            self._ffmpeg_advanced_args['-bf'] = str(b_frames_value)

    @property
    def refs(self) -> int:
        if '-refs' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-refs'])
        return 0

    @refs.setter
    def refs(self, refs_value: int | None):
        if refs_value is None:
            self._ffmpeg_advanced_args.pop('-refs', 0)
        else:
            self._ffmpeg_advanced_args['-refs'] = str(refs_value)

    @property
    def no_scenecut(self) -> bool:
        if '-no-scenecut' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['-no-scenecut']

            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, is_no_scenecut_enabled: bool):
        if is_no_scenecut_enabled:
            self._ffmpeg_advanced_args['-no-scenecut'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-no-scenecut', 0)

    @property
    def forced_idr(self) -> bool:
        if '-forced-idr' in self._ffmpeg_advanced_args:
            forced_idr_arg = self._ffmpeg_advanced_args['-forced-idr']

            return forced_idr_arg == '1'
        return False

    @forced_idr.setter
    def forced_idr(self, is_forced_idr_enabled: bool):
        if is_forced_idr_enabled:
            self._ffmpeg_advanced_args['-forced-idr'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-forced-idr', 0)

    @property
    def spatial_aq(self) -> bool:
        if '-spatial-aq' in self._ffmpeg_advanced_args:
            spatial_aq_arg = self._ffmpeg_advanced_args['-spatial-aq']

            return spatial_aq_arg == '1'
        return False

    @spatial_aq.setter
    def spatial_aq(self, is_spatial_aq_enabled: bool):
        if is_spatial_aq_enabled:
            self._ffmpeg_advanced_args['-spatial-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-spatial-aq', 0)

    @property
    def temporal_aq(self) -> bool:
        if '-temporal-aq' in self._ffmpeg_advanced_args:
            temporal_aq_arg = self._ffmpeg_advanced_args['-temporal-aq']

            return temporal_aq_arg == '1'
        return False

    @temporal_aq.setter
    def temporal_aq(self, is_temporal_aq_enabled: bool):
        if is_temporal_aq_enabled:
            self._ffmpeg_advanced_args['-temporal-aq'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-temporal-aq', 0)

    @property
    def non_ref_p(self) -> bool:
        if '-nonref_p' in self._ffmpeg_advanced_args:
            non_ref_p_arg = self._ffmpeg_advanced_args['-nonref_p']

            return non_ref_p_arg == '1'
        return False

    @non_ref_p.setter
    def non_ref_p(self, is_non_ref_p_enabled: bool):
        if is_non_ref_p_enabled:
            self._ffmpeg_advanced_args['-nonref_p'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-nonref_p', 0)

    @property
    def strict_gop(self) -> bool:
        if '-strict_gop' in self._ffmpeg_advanced_args:
            strict_gop_arg = self._ffmpeg_advanced_args['-strict_gop']

            return strict_gop_arg == '1'
        return False

    @strict_gop.setter
    def strict_gop(self, is_strict_gop_enabled):
        if is_strict_gop_enabled:
            self._ffmpeg_advanced_args['-strict_gop'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-strict_gop', 0)

    @property
    def aq_strength(self) -> int:
        if '-aq-strength' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-aq-strength'])
        return 8

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: int | None):
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('-aq-strength', 0)
        else:
            self._ffmpeg_advanced_args['-aq-strength'] = str(aq_strength_value)

    @property
    def bluray_compat(self) -> bool:
        if '-bluray-compat' in self._ffmpeg_advanced_args:
            bluray_compat_arg = self._ffmpeg_advanced_args['-bluray-compat']

            return bluray_compat_arg == '1'
        return False

    @bluray_compat.setter
    def bluray_compat(self, is_bluray_compat_enabled: bool):
        if is_bluray_compat_enabled:
            self._ffmpeg_advanced_args['-bluray-compat'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-bluray-compat', 0)

    @property
    def weighted_pred(self) -> bool:
        if '-weighted_pred' in self._ffmpeg_advanced_args:
            weighted_pred_arg = self._ffmpeg_advanced_args['-weighted_pred']

            return weighted_pred_arg == '1'
        return False

    @weighted_pred.setter
    def weighted_pred(self, is_weighted_pred_enabled: bool):
        if is_weighted_pred_enabled:
            self._ffmpeg_advanced_args['-weighted_pred'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-weighted_pred', 0)

    @property
    def b_ref_mode(self) -> int:
        """
        Returns bref mode as an index.
        """
        if '-b_ref_mode' in self._ffmpeg_advanced_args:
            b_ref_mode_arg = self._ffmpeg_advanced_args['-b_ref_mode']

            return self.BREF_MODE.index(b_ref_mode_arg)
        return 0

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index: int | None):
        if b_ref_mode_index and 0 < b_ref_mode_index < HevcNvenc.BREF_MODE_LENGTH:
            self._ffmpeg_advanced_args['-b_ref_mode'] = self.BREF_MODE[b_ref_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('-b_ref_mode', 0)

    @property
    def tier(self) -> bool:
        if '-tier' in self._ffmpeg_advanced_args:
            tier_value = self._ffmpeg_advanced_args['-tier']

            return tier_value == '1'
        return False

    @tier.setter
    def tier(self, is_tier_high_enabled: bool):
        if is_tier_high_enabled:
            self._ffmpeg_advanced_args['-tier'] = '1'
        else:
            self._ffmpeg_advanced_args.pop('-tier', 0)

    @property
    def encode_pass(self):
        return None  # Returns None for compatibility.

    def get_ffmpeg_advanced_args(self) -> dict:
        if self.is_advanced_enabled:
            return self._ffmpeg_advanced_args
        return {None: None}
