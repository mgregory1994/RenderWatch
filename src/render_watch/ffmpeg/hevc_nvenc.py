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


from render_watch.helpers.nvidia_helper import NvidiaHelper


class HevcNvenc:
    """Manages all settings for the HEVC NVENC codec."""

    OPTIONS = NvidiaHelper.get_hevc_nvenc_options()
    PRESET_ARGS_LIST = ['auto']
    if '-preset' in OPTIONS:
        PRESET_ARGS_LIST = OPTIONS['-preset']
    PRESET_LIST_LENGTH = len(PRESET_ARGS_LIST)
    PROFILE_ARGS_LIST = ['auto']
    if '-profile' in OPTIONS:
        PROFILE_ARGS_LIST.extend(OPTIONS['-profile'])
    PROFILE_LIST_LENGTH = len(PROFILE_ARGS_LIST)
    LEVEL_ARGS_LIST = ['auto']
    if '-level' in OPTIONS:
        LEVEL_ARGS_LIST = OPTIONS['-level']
    LEVEL_LIST_LENGTH = len(LEVEL_ARGS_LIST)
    TUNE_ARGS_LIST = ['auto']
    if '-tune' in OPTIONS:
        TUNE_ARGS_LIST.extend(OPTIONS['-tune'])
    TUNE_LIST_LENGTH = len(TUNE_ARGS_LIST)
    RATE_CONTROL_ARGS_LIST = ['auto']
    if '-rc' in OPTIONS:
        RATE_CONTROL_ARGS_LIST.extend(OPTIONS['-rc'])
    RATE_CONTROL_LIST_LENGTH = len(RATE_CONTROL_ARGS_LIST)
    MULTI_PASS_ARGS_LIST = ['auto']
    if '-multipass' in OPTIONS:
        MULTI_PASS_ARGS_LIST.extend(OPTIONS['-multipass'])
    MULTI_PASS_LIST_LENGTH = len(MULTI_PASS_ARGS_LIST)
    BREF_MODE_ARGS_LIST = ['auto']
    if '-b_ref_mode' in OPTIONS:
        BREF_MODE_ARGS_LIST.extend(OPTIONS['-b_ref_mode'])
    BREF_MODE_LIST_LENGTH = len(BREF_MODE_ARGS_LIST)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'hevc_nvenc',
            '-qp': '20.0'
        }
        self.advanced_enabled = False
        self.qp_custom_enabled = False
        self.dual_pass_enabled = False
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def qp(self):
        """Returns qp argument as a float."""
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return None

    @qp.setter
    def qp(self, qp_value):
        """Stores qp value as a string argument."""
        if qp_value is None or not 0 <= qp_value <= 51:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.bitrate = None

    @property
    def bitrate(self):
        """Returns bitrate argument as an int."""
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']
            return int(bitrate_arg.split('k')[0])
        return None

    @bitrate.setter
    def bitrate(self, bitrate_value):
        """Stores bitrate value as a string argument."""
        if bitrate_value is None or not 0 < bitrate_value <= 99999:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.qp = None

    @property
    def profile(self):
        """Returns profile argument as an index."""
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']
            return self.PROFILE_ARGS_LIST.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index):
        """Stores index as a profile argument."""
        if profile_index is None or not 0 < profile_index < HevcNvenc.PROFILE_LIST_LENGTH:
            self.ffmpeg_args.pop('-profile:v', 0)
        else:
            self.ffmpeg_args['-profile:v'] = self.PROFILE_ARGS_LIST[profile_index]

    @property
    def preset(self):
        """Returns preset argument as an index."""
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']
            return self.PRESET_ARGS_LIST.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index):
        """Stores index as a preset argument."""
        if preset_index is None or not 0 < preset_index < HevcNvenc.PRESET_LIST_LENGTH:
            self.ffmpeg_args.pop('-preset', 0)
        else:
            self.ffmpeg_args['-preset'] = self.PRESET_ARGS_LIST[preset_index]

    @property
    def level(self):
        """Returns level argument as an index."""
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']
            return self.LEVEL_ARGS_LIST.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index):
        """Stores index as a level argument."""
        if level_index is None or not 0 < level_index < HevcNvenc.LEVEL_LIST_LENGTH:
            self.ffmpeg_args.pop('-level', 0)
        else:
            self.ffmpeg_args['-level'] = self.LEVEL_ARGS_LIST[level_index]

    @property
    def tune(self):
        """Returns tune argument as an index."""
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']
            return self.TUNE_ARGS_LIST.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index):
        """Stores index as a tune argument."""
        if tune_index is None or not 0 < tune_index < HevcNvenc.TUNE_LIST_LENGTH:
            self.ffmpeg_args.pop('-tune', 0)
        else:
            self.ffmpeg_args['-tune'] = self.TUNE_ARGS_LIST[tune_index]

    @property
    def multi_pass(self):
        """Returns multi pass argument as an index."""
        if '-multipass' in self.ffmpeg_args:
            multi_pass_arg = self.ffmpeg_args['-multipass']
            return self.MULTI_PASS_ARGS_LIST.index(multi_pass_arg)
        return 0

    @multi_pass.setter
    def multi_pass(self, multi_pass_index):
        """Stores index as a multi pass argument."""
        if multi_pass_index is None or not 0 < multi_pass_index < HevcNvenc.MULTI_PASS_LIST_LENGTH:
            self.ffmpeg_args.pop('-multipass', 0)
        else:
            self.ffmpeg_args['-multipass'] = self.MULTI_PASS_ARGS_LIST[multi_pass_index]

    @property
    def cbr(self):
        """Returns cbr argument as a boolean."""
        if '-cbr' in self.ffmpeg_args:
            cbr_arg = self.ffmpeg_args['-cbr']
            return cbr_arg == '1'
        return False

    @cbr.setter
    def cbr(self, cbr_enabled):
        """Stores cbr boolean as a string argument."""
        if cbr_enabled is None or not cbr_enabled:
            self.ffmpeg_args.pop('-cbr', 0)
        else:
            self.ffmpeg_args['-cbr'] = '1'

    @property
    def qp_i(self):
        """Returns init qpI argument as a float."""
        if '-init_qpI' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpI'])
        return 20.0

    @qp_i.setter
    def qp_i(self, qp_i_value):
        """Stores qpI value as a string argument."""
        if qp_i_value is None or not 0 <= qp_i_value <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpI', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpI'] = str(qp_i_value)

    @property
    def qp_p(self):
        """Returns init qpP argument as a float."""
        if '-init_qpP' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpP'])
        return 20.0

    @qp_p.setter
    def qp_p(self, qp_p_value):
        """Stores qpP value as a string argument."""
        if qp_p_value is None or not 0 <= qp_p_value <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpP', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpP'] = str(qp_p_value)

    @property
    def qp_b(self):
        """Returns init qpB argument as a float."""
        if '-init_qpB' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpB'])
        return 20.0

    @qp_b.setter
    def qp_b(self, qp_b_value):
        """Stores qpB value as a string argument."""
        if qp_b_value is None or not 0 <= qp_b_value <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpB', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpB'] = str(qp_b_value)

    @property
    def rc(self):
        """Returns rate control argument as an index."""
        if '-rc' in self._ffmpeg_advanced_args:
            rc_arg = self._ffmpeg_advanced_args['-rc']
            return self.RATE_CONTROL_ARGS_LIST.index(rc_arg)
        return 0

    @rc.setter
    def rc(self, rc_index):
        """Stores index as a rate control argument."""
        if rc_index is None or not 0 < rc_index < HevcNvenc.RATE_CONTROL_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('-rc', 0)
        else:
            self._ffmpeg_advanced_args['-rc'] = self.RATE_CONTROL_ARGS_LIST[rc_index]

    @property
    def rc_lookahead(self):
        """Returns rate control lookahead argument as an int."""
        if '-rc-lookahead' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-rc-lookahead'])
        return 0

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value):
        """Stores rate control lookahead value as a string argument."""
        if rc_lookahead_value is None or rc_lookahead_value < 0:
            self._ffmpeg_advanced_args.pop('-rc-lookahead', 0)
        else:
            self._ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead_value)

    @property
    def surfaces(self):
        """Returns surfaces argument as an int."""
        if '-surfaces' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-surfaces'])
        return 8

    @surfaces.setter
    def surfaces(self, surfaces_value):
        """Stores surfaces value as a string argument."""
        if surfaces_value is None or surfaces_value < 0:
            self._ffmpeg_advanced_args.pop('-surfaces', 0)
        else:
            self._ffmpeg_advanced_args['-surfaces'] = str(surfaces_value)

    @property
    def no_scenecut(self):
        """Returns no scenecut argument as a boolean."""
        if '-no-scenecut' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['-no-scenecut']
            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut_enabled):
        """Stores no scenecut boolean as a string argument."""
        if no_scenecut_enabled is None or not no_scenecut_enabled:
            self._ffmpeg_advanced_args.pop('-no-scenecut', 0)
        else:
            self._ffmpeg_advanced_args['-no-scenecut'] = '1'

    @property
    def forced_idr(self):
        """Returns forced idr argument as a boolean."""
        if '-forced-idr' in self._ffmpeg_advanced_args:
            forced_idr_arg = self._ffmpeg_advanced_args['-forced-idr']
            return forced_idr_arg == '1'
        return False

    @forced_idr.setter
    def forced_idr(self, forced_idr_enabled):
        """Stores forced idr boolean as a string argument."""
        if forced_idr_enabled is None or not forced_idr_enabled:
            self._ffmpeg_advanced_args.pop('-forced-idr', 0)
        else:
            self._ffmpeg_advanced_args['-forced-idr'] = '1'

    @property
    def spatial_aq(self):
        """Returns spatial aq argument as a boolean."""
        if '-spatial-aq' in self._ffmpeg_advanced_args:
            spatial_aq_arg = self._ffmpeg_advanced_args['-spatial-aq']
            return spatial_aq_arg == '1'
        return False

    @spatial_aq.setter
    def spatial_aq(self, spatial_aq_enabled):
        """Stores spatial aq boolean as a string argument."""
        if spatial_aq_enabled is None or not spatial_aq_enabled:
            self._ffmpeg_advanced_args.pop('-spatial-aq', 0)
        else:
            self._ffmpeg_advanced_args['-spatial-aq'] = '1'

    @property
    def temporal_aq(self):
        """Returns temporal aq argument as a boolean."""
        if '-temporal-aq' in self._ffmpeg_advanced_args:
            temporal_aq_arg = self._ffmpeg_advanced_args['-temporal-aq']
            return temporal_aq_arg == '1'
        return False

    @temporal_aq.setter
    def temporal_aq(self, temporal_aq_enabled):
        """Stores temporal aq boolean as a string argument."""
        if temporal_aq_enabled is None or not temporal_aq_enabled:
            self._ffmpeg_advanced_args.pop('-temporal-aq', 0)
        else:
            self._ffmpeg_advanced_args['-temporal-aq'] = '1'

    @property
    def non_ref_p(self):
        """Returns nonref p argument as a boolean."""
        if '-nonref_p' in self._ffmpeg_advanced_args:
            non_ref_p_arg = self._ffmpeg_advanced_args['-nonref_p']
            return non_ref_p_arg == '1'
        return False

    @non_ref_p.setter
    def non_ref_p(self, non_ref_p_enabled):
        """Stores nonref p boolean as a string argument."""
        if non_ref_p_enabled is None or not non_ref_p_enabled:
            self._ffmpeg_advanced_args.pop('-nonref_p', 0)
        else:
            self._ffmpeg_advanced_args['-nonref_p'] = '1'

    @property
    def strict_gop(self):
        """Returns strict gop argument as a boolean."""
        if '-strict_gop' in self._ffmpeg_advanced_args:
            strict_gop_arg = self._ffmpeg_advanced_args['-strict_gop']
            return strict_gop_arg == '1'
        return False

    @strict_gop.setter
    def strict_gop(self, strict_gop_enabled):
        """Stores strict gop boolean as a string argument."""
        if strict_gop_enabled is None or not strict_gop_enabled:
            self._ffmpeg_advanced_args.pop('-strict_gop', 0)
        else:
            self._ffmpeg_advanced_args['-strict_gop'] = '1'

    @property
    def aq_strength(self):
        """Returns aq strength argument as an int."""
        if '-aq-strength' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-aq-strength'])
        return 8

    @aq_strength.setter
    def aq_strength(self, aq_strength_value):
        """Stores aq strength value as a string argument."""
        if aq_strength_value is None or aq_strength_value < 0:
            self._ffmpeg_advanced_args.pop('-aq-strength', 0)
        else:
            self._ffmpeg_advanced_args['-aq-strength'] = str(aq_strength_value)

    @property
    def bluray_compat(self):
        """Returns bluray compatibility argument as a boolean."""
        if '-bluray-compat' in self._ffmpeg_advanced_args:
            bluray_compat_arg = self._ffmpeg_advanced_args['-bluray-compat']
            return bluray_compat_arg == '1'
        return False

    @bluray_compat.setter
    def bluray_compat(self, bluray_compat_enabled):
        """Stores bluray compatibility boolean as a string argument."""
        if bluray_compat_enabled is None or not bluray_compat_enabled:
            self._ffmpeg_advanced_args.pop('-bluray-compat', 0)
        else:
            self._ffmpeg_advanced_args['-bluray-compat'] = '1'

    @property
    def weighted_pred(self):
        """Returns weighted prediction argument as a boolean."""
        if '-weighted_pred' in self._ffmpeg_advanced_args:
            weighted_pred_arg = self._ffmpeg_advanced_args['-weighted_pred']
            return weighted_pred_arg == '1'
        return False

    @weighted_pred.setter
    def weighted_pred(self, weighted_pred_enabled):
        """Stores weighted prediction boolean as a string argument."""
        if weighted_pred_enabled is None or not weighted_pred_enabled:
            self._ffmpeg_advanced_args.pop('-weighted_pred', 0)
        else:
            self._ffmpeg_advanced_args['-weighted_pred'] = '1'

    @property
    def b_ref_mode(self):
        """Returns bref mode argument as an index."""
        if '-b_ref_mode' in self._ffmpeg_advanced_args:
            b_ref_mode_arg = self._ffmpeg_advanced_args['-b_ref_mode']
            return self.BREF_MODE_ARGS_LIST.index(b_ref_mode_arg)
        return 0

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index):
        """Stores index as a bref mode argument."""
        if b_ref_mode_index is None or not 0 < b_ref_mode_index < HevcNvenc.BREF_MODE_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('-b_ref_mode', 0)
        else:
            self._ffmpeg_advanced_args['-b_ref_mode'] = self.BREF_MODE_ARGS_LIST[b_ref_mode_index]

    @property
    def tier(self):
        """Returns tier argument as a boolean."""
        if '-tier' in self._ffmpeg_advanced_args:
            tier_value = self._ffmpeg_advanced_args['-tier']
            return tier_value == '1'
        return False

    @tier.setter
    def tier(self, tier_high_enabled):
        """Stores tier boolean as a string argument."""
        if tier_high_enabled is None or not tier_high_enabled:
            self._ffmpeg_advanced_args.pop('-tier', 0)
        else:
            self._ffmpeg_advanced_args['-tier'] = '1'

    @property
    def encode_pass(self):
        """Null function for ffmpeg.settings module compatibility."""
        return None

    def get_ffmpeg_advanced_args(self):
        """Returns advanced settings dictionary if advanced settings are enabled."""
        if self.advanced_enabled:
            return self._ffmpeg_advanced_args
        return {None: None}
