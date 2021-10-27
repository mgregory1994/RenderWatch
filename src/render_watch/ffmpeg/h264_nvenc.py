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


class H264Nvenc:
    """
    Stores all settings for the H264 NVENC codec.
    """

    PRESET_ARGS_LIST = [
        'default', 'slow', 'medium', 'fast', 'hp', 'hq', 'bd', 'll', 'llhq', 'llhp', 'lossless', 'losslesshp', 'p1',
        'p2', 'p3', 'p4', 'p5', 'p6', 'p7'
    ]
    PRESET_LIST_LENGTH = len(PRESET_ARGS_LIST)

    PROFILE_ARGS_LIST = ['auto', 'baseline', 'main', 'high', 'high444p']
    PROFILE_LIST_LENGTH = len(PROFILE_ARGS_LIST)

    LEVEL_ARGS_LIST = [
        'auto', '1.0', '1.0b', '1.1', '1.2', '1.3', '2.0', '2.1', '2.2', '3.0', '3.1', '3.2', '4.0', '4.1', '4.2',
        '5.0', '5.1', '5.2', '6.0', '6.1', '6.2'
    ]
    LEVEL_LIST_LENGTH = len(LEVEL_ARGS_LIST)

    TUNE_ARGS_LIST = ['auto', 'hq', 'll', 'ull', 'lossless']
    TUNE_LIST_LENGTH = len(TUNE_ARGS_LIST)

    RATE_CONTROL_ARGS_LIST = ['auto', 'constqp', 'vbr', 'cbr', 'cbr_ld_hq', 'cbr_hq', 'vbr_hq']
    RATE_CONTROL_LIST_LENGTH = len(RATE_CONTROL_ARGS_LIST)

    MULTI_PASS_ARGS_LIST = ['auto', 'disabled', 'qres', 'fullres']
    MULTI_PASS_LIST_LENGTH = len(MULTI_PASS_ARGS_LIST)

    CODER_ARGS_LIST = ['auto', 'cabac', 'cavlc', 'ac', 'vlc']
    CODER_LIST_LENGTH = len(CODER_ARGS_LIST)

    BREF_MODE_ARGS_LIST = ['auto', 'disabled', 'each', 'middle']
    BREF_MODE_LIST_LENGTH = len(BREF_MODE_ARGS_LIST)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'h264_nvenc',
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
        """
        Returns qp as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return None

    @qp.setter
    def qp(self, qp):
        """
        Stores qp as a string.
        """
        if qp is None or not 0 <= qp <= 51:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp)
            self.bitrate = None

    @property
    def bitrate(self):
        """
        Returns bitrate as an int.
        """
        if '-b:v' in self.ffmpeg_args:
            bitrate_arg = self.ffmpeg_args['-b:v']
            return int(bitrate_arg.split('k')[0])
        return None

    @bitrate.setter
    def bitrate(self, bitrate):
        """
        Stores bitrate as a string.
        """
        if bitrate is None or not 0 < bitrate <= 99999:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate) + 'k'
            self.qp = None

    @property
    def profile(self):
        """
        Returns profile as an index.
        """
        if '-profile:v' in self.ffmpeg_args:
            profile_arg = self.ffmpeg_args['-profile:v']
            return self.PROFILE_ARGS_LIST.index(profile_arg)
        return 0

    @profile.setter
    def profile(self, profile_index):
        """
        Stores profile index as a string.
        """
        if profile_index is None or not 0 < profile_index < H264Nvenc.PROFILE_LIST_LENGTH:
            self.ffmpeg_args.pop('-profile:v', 0)
        else:
            self.ffmpeg_args['-profile:v'] = self.PROFILE_ARGS_LIST[profile_index]

    @property
    def preset(self):
        """
        Returns preset as an index.
        """
        if '-preset' in self.ffmpeg_args:
            preset_arg = self.ffmpeg_args['-preset']
            return self.PRESET_ARGS_LIST.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index):
        """
        Stores preset index as a string.
        """
        if preset_index is None or not 0 < preset_index < H264Nvenc.PRESET_LIST_LENGTH:
            self.ffmpeg_args.pop('-preset', 0)
        else:
            self.ffmpeg_args['-preset'] = self.PRESET_ARGS_LIST[preset_index]

    @property
    def level(self):
        """
        Returns level as an index.
        """
        if '-level' in self.ffmpeg_args:
            level_arg = self.ffmpeg_args['-level']
            return self.LEVEL_ARGS_LIST.index(level_arg)
        return 0

    @level.setter
    def level(self, level_index):
        """
        Stores level index as a string.
        """
        if level_index is None or not 0 < level_index < H264Nvenc.LEVEL_LIST_LENGTH:
            self.ffmpeg_args.pop('-level', 0)
        else:
            self.ffmpeg_args['-level'] = self.LEVEL_ARGS_LIST[level_index]

    @property
    def tune(self):
        """
        Returns tune as an index.
        """
        if '-tune' in self.ffmpeg_args:
            tune_arg = self.ffmpeg_args['-tune']
            return self.TUNE_ARGS_LIST.index(tune_arg)
        return 0

    @tune.setter
    def tune(self, tune_index):
        """
        Stores tune index as a string.
        """
        if tune_index is None or not 0 < tune_index < H264Nvenc.TUNE_LIST_LENGTH:
            self.ffmpeg_args.pop('-tune', 0)
        else:
            self.ffmpeg_args['-tune'] = self.TUNE_ARGS_LIST[tune_index]

    @property
    def multi_pass(self):
        """
        Returns multi pass as an index.
        """
        if '-multipass' in self.ffmpeg_args:
            multi_pass_arg = self.ffmpeg_args['-multipass']
            return self.MULTI_PASS_ARGS_LIST.index(multi_pass_arg)
        return 0

    @multi_pass.setter
    def multi_pass(self, multi_pass_index):
        """
        Stores multi-pass index as a string.
        """
        if multi_pass_index is None or not 0 < multi_pass_index < H264Nvenc.MULTI_PASS_LIST_LENGTH:
            self.ffmpeg_args.pop('-multipass', 0)
        else:
            self.ffmpeg_args['-multipass'] = self.MULTI_PASS_ARGS_LIST[multi_pass_index]

    @property
    def cbr(self):
        """
        Returns cbr as a boolean.
        """
        if '-cbr' in self.ffmpeg_args:
            cbr_value = self.ffmpeg_args['-cbr']
            return cbr_value == '1'
        return False

    @cbr.setter
    def cbr(self, cbr_enabled):
        """
        Stores cbr as a string.
        """
        if cbr_enabled is None or not cbr_enabled:
            self.ffmpeg_args.pop('-cbr', 0)
        else:
            self.ffmpeg_args['-cbr'] = '1'

    @property
    def qp_i(self):
        """
        Returns init qp i as a float.
        """
        if '-init_qpI' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpI'])
        return 20.0

    @qp_i.setter
    def qp_i(self, qp_i):
        """
        Stores init qp i as a string.
        """
        if qp_i is None or not 0 <= qp_i <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpI', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpI'] = str(qp_i)

    @property
    def qp_p(self):
        """
        Returns init qp p as a float.
        """
        if '-init_qpP' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpP'])
        return 20.0

    @qp_p.setter
    def qp_p(self, qp_p):
        """
        Stores init qp p as a string argument.
        """
        if qp_p is None or not 0 <= qp_p <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpP', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpP'] = str(qp_p)

    @property
    def qp_b(self):
        """
        Returns init qp b as a float.
        """
        if '-init_qpB' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['-init_qpB'])
        return 20.0

    @qp_b.setter
    def qp_b(self, qp_b):
        """
        Stores qp b as a string.
        """
        if qp_b is None or not 0 <= qp_b <= 51:
            self._ffmpeg_advanced_args.pop('-init_qpB', 0)
        else:
            self._ffmpeg_advanced_args['-init_qpB'] = str(qp_b)

    @property
    def rc(self):
        """
        Returns rate control as an index.
        """
        if '-rc' in self._ffmpeg_advanced_args:
            rc_arg = self._ffmpeg_advanced_args['-rc']
            return self.RATE_CONTROL_ARGS_LIST.index(rc_arg)
        return 0

    @rc.setter
    def rc(self, rc_index):
        """
        Stores rc index as a string.
        """
        if rc_index is None or not 0 < rc_index < H264Nvenc.RATE_CONTROL_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('-rc', 0)
        else:
            self._ffmpeg_advanced_args['-rc'] = self.RATE_CONTROL_ARGS_LIST[rc_index]

    @property
    def rc_lookahead(self):
        """
        Returns rate control lookahead as an int.
        """
        if '-rc-lookahead' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-rc-lookahead'])
        return 0

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead):
        """
        Stores rc lookahead as a string.
        """
        if rc_lookahead is None or rc_lookahead < 0:
            self._ffmpeg_advanced_args.pop('-rc-lookahead', 0)
        else:
            self._ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead)

    @property
    def surfaces(self):
        """
        Returns surfaces as an int.
        """
        if '-surfaces' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-surfaces'])
        return 8

    @surfaces.setter
    def surfaces(self, surfaces):
        """
        Stores surfaces as a string.
        """
        if surfaces is None or surfaces < 0:
            self._ffmpeg_advanced_args.pop('-surfaces', 0)
        else:
            self._ffmpeg_advanced_args['-surfaces'] = str(surfaces)

    @property
    def no_scenecut(self):
        """
        Returns no scenecut as a boolean.
        """
        if '-no-scenecut' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['-no-scenecut']
            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut):
        """
        Stores no scenecut as a string.
        """
        if no_scenecut is None or not no_scenecut:
            self._ffmpeg_advanced_args.pop('-no-scenecut', 0)
        else:
            self._ffmpeg_advanced_args['-no-scenecut'] = '1'

    @property
    def forced_idr(self):
        """
        Returns forced idr as a boolean.
        """
        if '-forced-idr' in self._ffmpeg_advanced_args:
            forced_idr_arg = self._ffmpeg_advanced_args['-forced-idr']
            return forced_idr_arg == '1'
        return False

    @forced_idr.setter
    def forced_idr(self, forced_idr_enabled):
        """
        Stores forced idr as a string.
        """
        if forced_idr_enabled is None or not forced_idr_enabled:
            self._ffmpeg_advanced_args.pop('-forced-idr', 0)
        else:
            self._ffmpeg_advanced_args['-forced-idr'] = '1'

    @property
    def b_adapt(self):
        """
        Returns b adapt as a boolean.
        """
        if '-b_adapt' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['-b_adapt']
            return b_adapt_arg == '1'
        return False

    @b_adapt.setter
    def b_adapt(self, b_adapt_enabled):
        """
        Stores b adapt as a string.
        """
        if b_adapt_enabled is None or not b_adapt_enabled:
            self._ffmpeg_advanced_args.pop('-b_adapt', 0)
        else:
            self._ffmpeg_advanced_args['-b_adapt'] = '1'

    @property
    def spatial_aq(self):
        """
        Returns spatial aq as a boolean.
        """
        if '-spatial-aq' in self._ffmpeg_advanced_args:
            spatial_aq_arg = self._ffmpeg_advanced_args['-spatial-aq']
            return spatial_aq_arg == '1'
        return False

    @spatial_aq.setter
    def spatial_aq(self, spatial_aq_enabled):
        """
        Stores spatial aq as a string.
        """
        if spatial_aq_enabled is None or not spatial_aq_enabled:
            self._ffmpeg_advanced_args.pop('-spatial-aq', 0)
        else:
            self._ffmpeg_advanced_args['-spatial-aq'] = '1'

    @property
    def temporal_aq(self):
        """
        Returns temporal aq as a boolean.
        """
        if '-temporal-aq' in self._ffmpeg_advanced_args:
            temporal_aq_arg = self._ffmpeg_advanced_args['-temporal-aq']
            return temporal_aq_arg == '1'
        return False

    @temporal_aq.setter
    def temporal_aq(self, temporal_aq_enabled):
        """
        Stores temporal aq as a string.
        """
        if temporal_aq_enabled is None or not temporal_aq_enabled:
            self._ffmpeg_advanced_args.pop('-temporal-aq', 0)
        else:
            self._ffmpeg_advanced_args['-temporal-aq'] = '1'

    @property
    def non_ref_p(self):
        """
        Returns non-ref p as a boolean.
        """
        if '-nonref_p' in self._ffmpeg_advanced_args:
            non_ref_p_arg = self._ffmpeg_advanced_args['-nonref_p']
            return non_ref_p_arg == '1'
        return False

    @non_ref_p.setter
    def non_ref_p(self, non_ref_p_enabled):
        """
        Stores non-ref p as a string.
        """
        if non_ref_p_enabled is None or not non_ref_p_enabled:
            self._ffmpeg_advanced_args.pop('-nonref_p', 0)
        else:
            self._ffmpeg_advanced_args['-nonref_p'] = '1'

    @property
    def strict_gop(self):
        """
        Returns strict gop as a boolean.
        """
        if '-strict_gop' in self._ffmpeg_advanced_args:
            strict_gop_arg = self._ffmpeg_advanced_args['-strict_gop']
            return strict_gop_arg == '1'
        return False

    @strict_gop.setter
    def strict_gop(self, strict_gop_enabled):
        """
        Stores strict gop as a string.
        """
        if strict_gop_enabled is None or not strict_gop_enabled:
            self._ffmpeg_advanced_args.pop('-strict_gop', 0)
        else:
            self._ffmpeg_advanced_args['-strict_gop'] = '1'

    @property
    def aq_strength(self):
        """
        Returns aq strength as an int.
        """
        if '-aq-strength' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['-aq-strength'])
        return 8

    @aq_strength.setter
    def aq_strength(self, aq_strength):
        """
        Stores aq strength as a string.
        """
        if aq_strength is None or aq_strength < 0:
            self._ffmpeg_advanced_args.pop('-aq-strength', 0)
        else:
            self._ffmpeg_advanced_args['-aq-strength'] = str(aq_strength)

    @property
    def bluray_compat(self):
        """
        Returns bluray compatibility as a boolean.
        """
        if '-bluray-compat' in self._ffmpeg_advanced_args:
            bluray_compat_arg = self._ffmpeg_advanced_args['-bluray-compat']
            return bluray_compat_arg == '1'
        return False

    @bluray_compat.setter
    def bluray_compat(self, bluray_compat_enabled):
        """
        Stores bluray compatibility as a string.
        """
        if bluray_compat_enabled is None or not bluray_compat_enabled:
            self._ffmpeg_advanced_args.pop('-bluray-compat', 0)
        else:
            self._ffmpeg_advanced_args['-bluray-compat'] = '1'

    @property
    def weighted_pred(self):
        """
        Returns weighted prediction as a boolean.
        """
        if '-weighted_pred' in self._ffmpeg_advanced_args:
            weighted_pred_arg = self._ffmpeg_advanced_args['-weighted_pred']
            return weighted_pred_arg == '1'
        return False

    @weighted_pred.setter
    def weighted_pred(self, weighted_pred_enabled):
        """
        Stores weighted prediction as a string.
        """
        if weighted_pred_enabled is None or not weighted_pred_enabled:
            self._ffmpeg_advanced_args.pop('-weighted_pred', 0)
        else:
            self._ffmpeg_advanced_args['-weighted_pred'] = '1'

    @property
    def coder(self):
        """
        Returns coder as an index.
        """
        if '-coder' in self._ffmpeg_advanced_args:
            coder_arg = self._ffmpeg_advanced_args['-coder']
            return self.CODER_ARGS_LIST.index(coder_arg)
        return 0

    @coder.setter
    def coder(self, coder_index):
        """
        Stores coder index as a string.
        """
        if coder_index is None or not 0 < coder_index < H264Nvenc.CODER_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('-coder', 0)
        else:
            self._ffmpeg_advanced_args['-coder'] = self.CODER_ARGS_LIST[coder_index]

    @property
    def b_ref_mode(self):
        """
        Returns bref mode as an index.
        """
        if '-b_ref_mode' in self._ffmpeg_advanced_args:
            b_ref_mode_arg = self._ffmpeg_advanced_args['-b_ref_mode']
            return self.BREF_MODE_ARGS_LIST.index(b_ref_mode_arg)
        return 0

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index):
        """
        Stores bref mode index as a string.
        """
        if b_ref_mode_index is None or not 0 < b_ref_mode_index < H264Nvenc.BREF_MODE_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('-b_ref_mode', 0)
        else:
            self._ffmpeg_advanced_args['-b_ref_mode'] = self.BREF_MODE_ARGS_LIST[b_ref_mode_index]

    @property
    def encode_pass(self):
        """
        Returns None for compatibility.
        """
        return None

    def get_ffmpeg_advanced_args(self):
        """
        Returns dictionary with advanced args.
        """
        if self.advanced_enabled:
            return self._ffmpeg_advanced_args
        return {None: None}
