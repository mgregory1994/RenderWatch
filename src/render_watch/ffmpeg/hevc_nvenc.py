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


class HevcNvenc:
    preset_ffmpeg_args_list = ('auto', 'slow', 'medium', 'fast', 'hp', 'hq', 'bd', 'll', 'llhq', 'llhp', 'lossless',
                               'losslesshp')
    preset_human_readable_list = ('auto', 'slow', 'medium', 'fast', 'HP', 'HQ', 'low latency', 'low latency HQ',
                                  'low latency HP', 'lossless', 'lossless HP')
    profile_ffmpeg_args_list = ('auto', 'main', 'main10', 'rext')
    level_ffmpeg_args_list = ('auto', '1', '2', '2.1', '3', '3.1', '4', '4.1', '5', '5.1', '5.2', '6', '6.1', '6.2')
    rate_control_ffmpeg_args_list = ('auto', 'constqp', 'vbr', 'cbr', 'cbr_ld_hq', 'cbr_hq', 'vbr_hq')
    rate_control_human_readable_list = ('auto', 'constant qp', 'vbr', 'cbr', 'cbr low-delay', 'cbr HQ', 'vbr HQ')
    coder_ffmpeg_args_list = ('auto', 'cabac', 'cavlc', 'ac', 'vlc')
    bref_mode_ffmpeg_args_list = ('auto', 'disabled', 'each', 'middle')

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'hevc_nvenc',
            '-qp': '20',
            '-b:v': None,
            '-profile:v': None,
            '-preset': None,
            '-level': None,
            '-cbr': None,
            '-2pass': None
        }
        self.advanced_enabled = False
        self.qp_custom_enabled = False
        self.__ffmpeg_advanced_args = {
            '-init_qpP': None,
            '-init_qpB': None,
            '-init_qpI': None,
            '-rc': None,
            '-rc-lookahead': None,
            '-surfaces': None,
            '-no-scenecut': None,
            '-forced-idr': None,
            '-spatial-aq': None,
            '-temporal-aq': None,
            '-nonref_p': None,
            '-strict_gop': None,
            '-aq-strength': None,
            '-bluray-compat': None,
            '-weighted_pred': None,
            '-b_ref_mode': None,
            '-tier': None
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def qp(self):
        try:
            qp = self.ffmpeg_args['-qp']
            qp_value = float(qp)
        except TypeError:
            return None
        else:
            return qp_value

    @qp.setter
    def qp(self, qp_value):
        try:
            if qp_value is None or qp_value < 0 or qp_value > 51:
                raise ValueError

            self.ffmpeg_args['-qp'] = str(qp_value)
        except (ValueError, TypeError):
            self.ffmpeg_args['-qp'] = None
        else:
            self.bitrate = None

    @property
    def bitrate(self):
        try:
            bitrate = self.ffmpeg_args['-b:v']
            bitrate_value = int(bitrate.split('k')[0])
        except:
            return None
        else:
            return bitrate_value

    @bitrate.setter
    def bitrate(self, bitrate_value):
        try:
            if bitrate_value is None or bitrate_value < 0 or bitrate_value > 99999:
                raise ValueError

            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
        except (ValueError, TypeError):
            self.ffmpeg_args['-b:v'] = None
        else:
            self.qp = None

    @property
    def profile(self):
        try:
            profile_value = self.ffmpeg_args['-profile:v']

            if profile_value is None:
                profile_index = 0
            else:
                profile_index = self.profile_ffmpeg_args_list.index(profile_value)
        except ValueError:
            return 0
        else:
            return profile_index

    @profile.setter
    def profile(self, profile_index):
        try:
            if profile_index is None or profile_index < 1:
                self.ffmpeg_args['-profile:v'] = None
            else:
                self.ffmpeg_args['-profile:v'] = self.profile_ffmpeg_args_list[profile_index]
        except IndexError:
            self.ffmpeg_args['-profile:v'] = None

    @property
    def preset(self):
        try:
            preset_value = self.ffmpeg_args['-preset']

            if preset_value is None:
                preset_index = 0
            else:
                preset_index = self.preset_ffmpeg_args_list.index(preset_value)
        except ValueError:
            return 0
        else:
            return preset_index

    @preset.setter
    def preset(self, preset_index):
        try:
            if preset_index is None or preset_index < 1:
                self.ffmpeg_args['-preset'] = None
            else:
                self.ffmpeg_args['-preset'] = self.preset_ffmpeg_args_list[preset_index]
        except IndexError:
            self.ffmpeg_args['-preset'] = None

    @property
    def level(self):
        try:
            level_value = self.ffmpeg_args['-level']

            if level_value is None:
                level_index = 0
            else:
                level_index = self.level_ffmpeg_args_list.index(level_value)
        except ValueError:
            return 0
        else:
            return level_index

    @level.setter
    def level(self, level_index):
        try:
            if level_index is None or level_index < 1:
                self.ffmpeg_args['-level'] = None
            else:
                self.ffmpeg_args['-level'] = self.level_ffmpeg_args_list[level_index]
        except IndexError:
            self.ffmpeg_args['-level'] = None

    @property
    def dual_pass(self):
        dual_pass_value = self.ffmpeg_args['-2pass']

        if dual_pass_value is None or dual_pass_value != '1':
            return False

        return True

    @dual_pass.setter
    def dual_pass(self, dual_pass_enabled):
        if dual_pass_enabled is None or not dual_pass_enabled:
            self.ffmpeg_args['-2pass'] = None
        else:
            self.ffmpeg_args['-2pass'] = '1'

    @property
    def cbr(self):
        cbr_value = self.ffmpeg_args['-cbr']

        if cbr_value is None or cbr_value != '1':
            return False

        return True

    @cbr.setter
    def cbr(self, cbr_enabled):
        if cbr_enabled is None or not cbr_enabled:
            self.ffmpeg_args['-cbr'] = None
        else:
            self.ffmpeg_args['-cbr'] = '1'

    @property
    def qp_i(self):
        try:
            qp_i = self.__ffmpeg_advanced_args['-init_qpI']
            qp_i_value = float(qp_i)
        except TypeError:
            return 20.0
        else:
            return qp_i_value

    @qp_i.setter
    def qp_i(self, qp_i_value):
        try:
            if qp_i_value is None or qp_i_value < 0 or qp_i_value > 51:
                raise ValueError

            self.__ffmpeg_advanced_args['-init_qpI'] = str(qp_i_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-init_qpI'] = None

    @property
    def qp_p(self):
        try:
            qp_p = self.__ffmpeg_advanced_args['-init_qpP']
            qp_p_value = float(qp_p)
        except TypeError:
            return 20.0
        else:
            return qp_p_value

    @qp_p.setter
    def qp_p(self, qp_p_value):
        try:
            if qp_p_value is None or qp_p_value < 0 or qp_p_value > 51:
                raise ValueError

            self.__ffmpeg_advanced_args['-init_qpP'] = str(qp_p_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-init_qpP'] = None

    @property
    def qp_b(self):
        try:
            qp_b = self.__ffmpeg_advanced_args['-init_qpB']
            qp_b_value = float(qp_b)
        except TypeError:
            return 20.0
        else:
            return qp_b_value

    @qp_b.setter
    def qp_b(self, qp_b_value):
        try:
            if qp_b_value is None or qp_b_value < 0 or qp_b_value > 51:
                raise ValueError

            self.__ffmpeg_advanced_args['-init_qpB'] = str(qp_b_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-init_qpB'] = None

    @property
    def rc(self):
        try:
            rc_value = self.__ffmpeg_advanced_args['-rc']

            if rc_value is None:
                rc_index = 0
            else:
                rc_index = self.rate_control_ffmpeg_args_list.index(rc_value)
        except ValueError:
            return 0
        else:
            return rc_index

    @rc.setter
    def rc(self, rc_index):
        try:
            if rc_index is None or rc_index < 1:
                self.__ffmpeg_advanced_args['-rc'] = None
            else:
                self.__ffmpeg_advanced_args['-rc'] = self.rate_control_ffmpeg_args_list[rc_index]
        except IndexError:
            self.__ffmpeg_advanced_args['-rc'] = None

    @property
    def rc_lookahead(self):
        try:
            rc_lookahead = self.__ffmpeg_advanced_args['-rc-lookahead']
            rc_lookahead_value = int(rc_lookahead)
        except TypeError:
            return 0
        else:
            return rc_lookahead_value

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value):
        try:
            if rc_lookahead_value is None or rc_lookahead_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['-rc-lookahead'] = str(rc_lookahead_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-rc-lookahead'] = None

    @property
    def surfaces(self):
        try:
            surfaces = self.__ffmpeg_advanced_args['-surfaces']
            surfaces_value = int(surfaces)
        except TypeError:
            return 8
        else:
            return surfaces_value

    @surfaces.setter
    def surfaces(self, surfaces_value):
        try:
            if surfaces_value is None or surfaces_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['-surfaces'] = str(surfaces_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-surfaces'] = None

    @property
    def no_scenecut(self):
        no_scenecut_value = self.__ffmpeg_advanced_args['-no-scenecut']

        if no_scenecut_value is None or no_scenecut_value != '1':
            return False

        return True

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut_enabled):
        if no_scenecut_enabled is None or not no_scenecut_enabled:
            self.__ffmpeg_advanced_args['-no-scenecut'] = None
        else:
            self.__ffmpeg_advanced_args['-no-scenecut'] = '1'

    @property
    def forced_idr(self):
        forced_idr_value = self.__ffmpeg_advanced_args['-forced-idr']

        if forced_idr_value is None or forced_idr_value != '1':
            return False

        return True

    @forced_idr.setter
    def forced_idr(self, forced_idr_enabled):
        if forced_idr_enabled is None or not forced_idr_enabled:
            self.__ffmpeg_advanced_args['-forced-idr'] = None
        else:
            self.__ffmpeg_advanced_args['-forced-idr'] = '1'

    @property
    def spatial_aq(self):
        spatial_aq_value = self.__ffmpeg_advanced_args['-spatial-aq']

        if spatial_aq_value is None or spatial_aq_value != '1':
            return False

        return True

    @spatial_aq.setter
    def spatial_aq(self, spatial_aq_enabled):
        if spatial_aq_enabled is None or not spatial_aq_enabled:
            self.__ffmpeg_advanced_args['-spatial-aq'] = None
        else:
            self.__ffmpeg_advanced_args['-spatial-aq'] = '1'

    @property
    def temporal_aq(self):
        temporal_aq_value = self.__ffmpeg_advanced_args['-temporal-aq']

        if temporal_aq_value is None or temporal_aq_value != '1':
            return False

        return True

    @temporal_aq.setter
    def temporal_aq(self, temporal_aq_enabled):
        if temporal_aq_enabled is None or not temporal_aq_enabled:
            self.__ffmpeg_advanced_args['-temporal-aq'] = None
        else:
            self.__ffmpeg_advanced_args['-temproal-aq'] = '1'

    @property
    def non_ref_p(self):
        non_ref_p_value = self.__ffmpeg_advanced_args['-nonref_p']

        if non_ref_p_value is None or non_ref_p_value != '1':
            return False

        return True

    @non_ref_p.setter
    def non_ref_p(self, non_ref_p_enabled):
        if non_ref_p_enabled is None or not non_ref_p_enabled:
            self.__ffmpeg_advanced_args['-nonref_p'] = None
        else:
            self.__ffmpeg_advanced_args['-nonref_p'] = '1'

    @property
    def strict_gop(self):
        strict_gop_value = self.__ffmpeg_advanced_args['-strict_gop']

        if strict_gop_value is None or strict_gop_value != '1':
            return False

        return True

    @strict_gop.setter
    def strict_gop(self, strict_gop_enabled):
        if strict_gop_enabled is None or not strict_gop_enabled:
            self.__ffmpeg_advanced_args['-strict_gop'] = None
        else:
            self.__ffmpeg_advanced_args['-strict_gop'] = '1'

    @property
    def aq_strength(self):
        try:
            aq_strength = self.__ffmpeg_advanced_args['-aq-strength']
            aq_strength_value = int(aq_strength)
        except TypeError:
            return 8
        else:
            return aq_strength_value

    @aq_strength.setter
    def aq_strength(self, aq_strength_value):
        try:
            if aq_strength_value is None or aq_strength_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['-aq-strength'] = str(aq_strength_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['-aq-strength'] = None

    @property
    def bluray_compat(self):
        bluray_compat_value = self.__ffmpeg_advanced_args['-bluray-compat']

        if bluray_compat_value is None or bluray_compat_value != '1':
            return False

        return True

    @bluray_compat.setter
    def bluray_compat(self, bluray_compat_enabled):
        if bluray_compat_enabled is None or not bluray_compat_enabled:
            self.__ffmpeg_advanced_args['-bluray-compat'] = None
        else:
            self.__ffmpeg_advanced_args['-bluray-compat'] = '1'

    @property
    def weighted_pred(self):
        weighted_pred_value = self.__ffmpeg_advanced_args['-weighted_pred']

        if weighted_pred_value is None or weighted_pred_value != '1':
            return False

        return True

    @weighted_pred.setter
    def weighted_pred(self, weighted_pred_enabled):
        if weighted_pred_enabled is None or not weighted_pred_enabled:
            self.__ffmpeg_advanced_args['-weighted_pred'] = None
        else:
            self.__ffmpeg_advanced_args['-weighted_pred'] = '1'

    @property
    def b_ref_mode(self):
        try:
            b_ref_mode_value = self.__ffmpeg_advanced_args['-b_ref_mode']

            if b_ref_mode_value is None:
                b_ref_mode_index = 0
            else:
                b_ref_mode_index = self.bref_mode_ffmpeg_args_list.index(b_ref_mode_value)
        except ValueError:
            return 0
        else:
            return b_ref_mode_index

    @b_ref_mode.setter
    def b_ref_mode(self, b_ref_mode_index):
        try:
            if b_ref_mode_index is None or b_ref_mode_index < 1:
                self.__ffmpeg_advanced_args['-b_ref_mode'] = None
            else:
                self.__ffmpeg_advanced_args['-b_ref_mode'] = self.bref_mode_ffmpeg_args_list[b_ref_mode_index]
        except IndexError:
            self.__ffmpeg_advanced_args['-b_ref_mode'] = None

    @property
    def tier(self):
        tier_value = self.__ffmpeg_advanced_args['-tier']

        if tier_value is None or tier_value != 'high':
            return False

        return True

    @tier.setter
    def tier(self, tier_high_enabled):
        if tier_high_enabled is None or not tier_high_enabled:
            self.__ffmpeg_advanced_args['-tier'] = 'main'
        else:
            self.__ffmpeg_advanced_args['-tier'] = 'high'

    @property
    def encode_pass(self):
        return None

    def get_ffmpeg_advanced_args(self):
        if not self.advanced_enabled:
            return {None: None}

        return self.__ffmpeg_advanced_args
