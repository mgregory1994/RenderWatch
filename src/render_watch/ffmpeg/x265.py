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


class X265:
    """Manages all settings for the x265 codec."""

    PROFILE_ARGS_LIST = ('auto', 'main', 'main10', 'main12')
    PROFILE_LIST_LENGTH = len(PROFILE_ARGS_LIST)
    PRESET_ARGS_LIST = ('auto', 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'slow', 'slower', 'veryslow')
    PRESET_LIST_LENGTH = len(PRESET_ARGS_LIST)
    LEVEL_ARGS_LIST = ('auto', '1', '2', '2.1', '3', '3.1', '4', '4.1', '5', '5.1', '5.2', '6', '6.1', '6.2', '8.5')
    LEVEL_LIST_LENGTH = len(LEVEL_ARGS_LIST)
    TUNE_ARGS_LIST = ('auto', 'grain', 'animation', 'zerolatency', 'fastdecode', 'psnr', 'ssim')
    TUNE_LIST_LENGTH = len(TUNE_ARGS_LIST)
    AQ_MODE_ARGS_LIST = ('auto', '0', '1', '2', '3', '4')
    AQ_MODE_UI_LIST = ('auto', 'disabled', 'enabled', 'variance', 'variance(dark)', 'variance(dark + edge)')
    AQ_MODE_LIST_LENGTH = len(AQ_MODE_ARGS_LIST)
    B_ADAPT_ARGS_LIST = ('auto', '0', '1', '2')
    B_ADAPT_UI_LIST = ('auto', 'none', 'fast', 'full(trellis)')
    B_ADAPT_LIST_LENGTH = len(B_ADAPT_ARGS_LIST)
    ME_ARGS_LIST = ('auto', 'dia', 'hex', 'umh', 'star', 'sea', 'full')
    ME_LIST_LENGTH = len(ME_ARGS_LIST)
    RDOQ_LEVEL_ARGS_LIST = ('auto', '0', '1', '2')
    RDOQ_LEVEL_UI_LIST = ('auto', 'none', 'optimal rounding', 'decimate decisions')
    RDOQ_LEVEL_LIST_LENGTH = len(RDOQ_LEVEL_ARGS_LIST)
    MAX_CU_SIZE_ARGS_LIST = ('auto', '64', '32', '16')
    MAX_CU_SIZE_LIST_LENGTH = len(MAX_CU_SIZE_ARGS_LIST)
    MIN_CU_SIZE_ARGS_LIST = ('auto', '8', '16', '32')
    MIN_CU_SIZE_LIST_LENGTH = len(MIN_CU_SIZE_ARGS_LIST)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libx265'
        }
        self.advanced_enabled = False
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self):
        """Returns crf argument as a float."""
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return None

    @crf.setter
    def crf(self, crf_value):
        """Stores crf value as a string argument."""
        if crf_value is None or crf_value < 0 or crf_value > 51:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)
            self.qp = None
            self.bitrate = None

    @property
    def qp(self):
        """Returns qp argument as a float."""
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return None

    @qp.setter
    def qp(self, qp_value):
        """Stores qp value as a string argument."""
        if qp_value is None or qp_value < 0 or qp_value > 51:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.crf = None
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
        if bitrate_value is None or bitrate_value < 0 or bitrate_value > 99999:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.crf = None
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
        if profile_index is None or profile_index < 1:
            self.ffmpeg_args.pop('-profile:v', 0)
        else:
            self.ffmpeg_args['-profile:v'] = self.PROFILE_ARGS_LIST[profile_index]

    @property
    def preset(self):
        """Returns preset argument as an index."""
        if '-preset' in self.ffmpeg_args:
            preset_value = self.ffmpeg_args['-preset']
            return self.PRESET_ARGS_LIST.index(preset_value)
        return 0

    @preset.setter
    def preset(self, preset_index):
        """Stores index as a preset argument."""
        if preset_index is None or preset_index < 1:
            self.ffmpeg_args.pop('-preset', 0)
        else:
            self.ffmpeg_args['-preset'] = self.PRESET_ARGS_LIST[preset_index]

    @property
    def level(self):
        """Returns level argument as an index."""
        if '-level' in self.ffmpeg_args:
            level_value = self.ffmpeg_args['-level']
            return self.LEVEL_ARGS_LIST.index(level_value)
        return 0

    @level.setter
    def level(self, level_index):
        """Stores index as a level argument."""
        if level_index is None or level_index < 1:
            self.ffmpeg_args.pop('-level', 0)
        else:
            self.ffmpeg_args['-level'] = self.LEVEL_ARGS_LIST[level_index]

    @property
    def tune(self):
        """Returns tune argument as an index."""
        if '-tune' in self.ffmpeg_args:
            tune_value = self.ffmpeg_args['-tune']
            return self.TUNE_ARGS_LIST.index(tune_value)
        return 0

    @tune.setter
    def tune(self, tune_index):
        """Stores index as a tune argument."""
        if tune_index is None or tune_index < 1:
            self.ffmpeg_args.pop('-tune', 0)
        else:
            self.ffmpeg_args['-tune'] = self.TUNE_ARGS_LIST[tune_index]

    @property
    def vbv_maxrate(self):
        """Returns vbv maxrate argument as an int."""
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value):
        """Stores vbv maxrate value as a string argument."""
        if vbv_maxrate_value is None or vbv_maxrate_value < 0 or vbv_maxrate_value > 99999:
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)

    @property
    def vbv_bufsize(self):
        """Returns vbv bufsize argument as an int."""
        if 'vbv-bufsize=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-bufsize='])
        return 2500

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize_value):
        """Stores vbv bufsize value as a string argument."""
        if vbv_bufsize_value is None or vbv_bufsize_value < 0 or vbv_bufsize_value > 99999:
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    @property
    def aq_mode(self):
        """Returns aq mode argument as an index."""
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_arg = self._ffmpeg_advanced_args['aq-mode=']
            return self.AQ_MODE_ARGS_LIST.index(aq_mode_arg)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index):
        """Stores index as a aq mode argument."""
        if aq_mode_index is None or aq_mode_index == 0:
            self._ffmpeg_advanced_args.pop('aq-mode=', 0)
        else:
            self._ffmpeg_advanced_args['aq-mode='] = self.AQ_MODE_ARGS_LIST[aq_mode_index]

    @property
    def aq_strength(self):
        """Returns aq strength argument as a float."""
        if 'aq-strength=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['aq-strength='])
        return 1.0

    @aq_strength.setter
    def aq_strength(self, aq_strength_value):
        """Stores aq strength value as a string argument."""
        if aq_strength_value is None or aq_strength_value < 0:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)

    @property
    def hevc_aq(self):
        """Returns hevc aq argument as a boolean."""
        if 'hevc-aq=' in self._ffmpeg_advanced_args:
            hevc_aq_arg = self._ffmpeg_advanced_args['hevc-aq=']
            return hevc_aq_arg == '1'
        return False

    @hevc_aq.setter
    def hevc_aq(self, hevc_aq_enabled):
        """Stores hevc aq boolean as a string argument."""
        if hevc_aq_enabled is None or not hevc_aq_enabled:
            self._ffmpeg_advanced_args.pop('hevc-aq=', 0)
        else:
            self._ffmpeg_advanced_args['hevc-aq='] = '1'

    @property
    def keyint(self):
        """Returns keyint argument as an int."""
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value):
        """Stores keyint value as a string argument."""
        if keyint_value is None or keyint_value < 0:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint_value)

    @property
    def min_keyint(self):
        """Returns min keyint argument as an int."""
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 0

    @min_keyint.setter
    def min_keyint(self, min_keyint_value):
        """Stores min keyint value as a string argument."""
        if min_keyint_value is None or min_keyint_value < 0:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def ref(self):
        """Returns ref argument as an int."""
        if 'ref=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['ref='])
        return 3

    @ref.setter
    def ref(self, ref_value):
        """Stores ref value as a string argument."""
        if ref_value is None or ref_value < 0:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref_value)

    @property
    def bframes(self):
        """Returns bframes argument as an int."""
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 4

    @bframes.setter
    def bframes(self, bframes_value):
        """Stores bframes value as a string argument."""
        if bframes_value is None or bframes_value < 0:
            self._ffmpeg_advanced_args.pop('bframes=', 0)
        else:
            self._ffmpeg_advanced_args['bframes='] = str(bframes_value)

    @property
    def b_adapt(self):
        """Returns b adapt argument as an index."""
        if 'b-adapt=' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['b-adapt=']
            return self.B_ADAPT_ARGS_LIST.index(b_adapt_arg)
        return 0

    @b_adapt.setter
    def b_adapt(self, b_adapt_index):
        """Stores index as a b adapt argument."""
        if b_adapt_index is None or b_adapt_index < 1:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)
        else:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT_ARGS_LIST[b_adapt_index]

    @property
    def no_b_pyramid(self):
        """Returns no b pyramid argument as a boolean."""
        if 'no-b-pyramid=' in self._ffmpeg_advanced_args:
            no_b_pyramid_arg = self._ffmpeg_advanced_args['no-b-pyramid=']
            return no_b_pyramid_arg == '1'
        return False

    @no_b_pyramid.setter
    def no_b_pyramid(self, no_b_pyramid_enabled):
        """Stores no b pyramid boolean as a string argument."""
        if no_b_pyramid_enabled is None or not no_b_pyramid_enabled:
            self._ffmpeg_advanced_args.pop('no-b-pyramid=', 0)
        else:
            self._ffmpeg_advanced_args['no-b-pyramid='] = '1'

    @property
    def b_intra(self):
        """Returns b intra argument as a boolean."""
        if 'b-intra=' in self._ffmpeg_advanced_args:
            b_intra_arg = self._ffmpeg_advanced_args['b-intra=']
            return b_intra_arg == '1'
        return False

    @b_intra.setter
    def b_intra(self, b_intra_enabled):
        """Stores b intra boolean as a string argument."""
        if b_intra_enabled is None or not b_intra_enabled:
            self._ffmpeg_advanced_args.pop('b-intra=', 0)
        else:
            self._ffmpeg_advanced_args['b-intra='] = '1'

    @property
    def no_open_gop(self):
        """Returns no open gop argument as a boolean."""
        if 'no-open-gop=' in self._ffmpeg_advanced_args:
            no_open_gop_arg = self._ffmpeg_advanced_args['no-open-gop=']
            return no_open_gop_arg == '1'
        return False

    @no_open_gop.setter
    def no_open_gop(self, no_open_gop_enabled):
        """Stores no open gop boolean as a string argument."""
        if no_open_gop_enabled is None or not no_open_gop_enabled:
            self._ffmpeg_advanced_args.pop('no-open-gop=', 0)
        else:
            self._ffmpeg_advanced_args['no-open-gop='] = '1'

    @property
    def rc_lookahead(self):
        """Returns rc lookahead argument as an int."""
        if 'rc-lookahead=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rc-lookahead='])
        return 20

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value):
        """Stores rc lookahead value as a string argument."""
        if rc_lookahead_value is None or rc_lookahead_value < 0:
            self._ffmpeg_advanced_args.pop('rc-lookahead=', 0)
        else:
            self._ffmpeg_advanced_args['rc-lookahead='] = str(rc_lookahead_value)

    @property
    def no_scenecut(self):
        """Returns no scenecut argument as a boolean."""
        if 'no-scenecut=' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['no-scenecut=']
            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut_enabled):
        """Stores no scenecut boolean as a string argument."""
        if no_scenecut_enabled is None or not no_scenecut_enabled:
            self._ffmpeg_advanced_args.pop('no-scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['no-scenecut='] = '1'

    @property
    def no_high_tier(self):
        """Returns no high tier argument as a boolean."""
        if 'no-high-tier=' in self._ffmpeg_advanced_args:
            no_high_tier_arg = self._ffmpeg_advanced_args['no-high-tier=']
            return no_high_tier_arg == '1'
        return False

    @no_high_tier.setter
    def no_high_tier(self, no_high_tier_enabled):
        """Stores no high tier boolean as a string argument."""
        if no_high_tier_enabled is None or not no_high_tier_enabled:
            self._ffmpeg_advanced_args.pop('no-high-tier=', 0)
        else:
            self._ffmpeg_advanced_args['no-high-tier='] = '1'

    @property
    def psy_rd(self):
        """Returns psy rd argument as a float."""
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rd='])
        return 2.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_value):
        """Stores psy rd value as a string argument."""
        if psy_rd_value is None or psy_rd_value < 0:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rd='] = str(psy_rd_value)

    @property
    def psy_rdoq(self):
        """Returns psy rdoq argument as a float."""
        if 'psy-rdoq=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rdoq='])
        return 0.0

    @psy_rdoq.setter
    def psy_rdoq(self, psy_rdoq_value):
        """Stores psy rdoq value as a string argument."""
        if psy_rdoq_value is None or psy_rdoq_value < 0:
            self._ffmpeg_advanced_args.pop('psy-rdoq=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rdoq='] = str(psy_rdoq_value)

    @property
    def me(self):
        """Returns me argument as an index."""
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']
            return self.ME_ARGS_LIST.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index):
        """Stores index as a me argument."""
        if me_index is None or me_index < 1:
            self._ffmpeg_advanced_args.pop('me=', 0)
        else:
            self._ffmpeg_advanced_args['me='] = self.ME_ARGS_LIST[me_index]

    @property
    def subme(self):
        """Returns subme argument as an int."""
        if 'subme=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['subme='])
        return 2

    @subme.setter
    def subme(self, subme_value):
        """Stores subme value as a string argument."""
        if subme_value is None or subme_value < 0:
            self._ffmpeg_advanced_args.pop('subme=', 0)
        else:
            self._ffmpeg_advanced_args['subme='] = str(subme_value)

    @property
    def weightb(self):
        """Return weight b argument as a boolean."""
        if 'weightb=' in self._ffmpeg_advanced_args:
            weightb_arg = self._ffmpeg_advanced_args['weightb=']
            return weightb_arg == '1'
        return False

    @weightb.setter
    def weightb(self, weightb_enabled):
        """Stores weight b boolean as a string argument."""
        if weightb_enabled is None or not weightb_enabled:
            self._ffmpeg_advanced_args.pop('weightb=', 0)
        else:
            self._ffmpeg_advanced_args['weightb='] = '1'

    @property
    def no_weightp(self):
        """Returns no weightp argument as a boolean."""
        if 'no-weightp=' in self._ffmpeg_advanced_args:
            no_weightp_arg = self._ffmpeg_advanced_args['no-weightp=']
            return no_weightp_arg == '1'
        return False

    @no_weightp.setter
    def no_weightp(self, no_weightp_enabled):
        """Stores no weightp boolean as a string argument."""
        if no_weightp_enabled is None or not no_weightp_enabled:
            self._ffmpeg_advanced_args.pop('no-weightp=', 0)
        else:
            self._ffmpeg_advanced_args['no-weightp='] = '1'

    @property
    def deblock(self):
        """Returns deblock argument as a tuple of ints."""
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')
            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock_values):
        """Stores deblock values tuple as a string argument."""
        if deblock_values is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock_values
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def no_deblock(self):
        """Returns no deblock argument as a boolean."""
        if 'no-deblock=' in self._ffmpeg_advanced_args:
            no_deblock_arg = self._ffmpeg_advanced_args['no-deblock=']
            return no_deblock_arg == '1'
        return False

    @no_deblock.setter
    def no_deblock(self, no_deblock_enabled):
        """Stores no deblock boolean as a string argument."""
        if no_deblock_enabled is None or not no_deblock_enabled:
            self._ffmpeg_advanced_args.pop('no-deblock=', 0)
        else:
            self._ffmpeg_advanced_args['no-deblock='] = '1'

    @property
    def no_sao(self):
        """Returns no sao argument as a boolean."""
        if 'no-sao=' in self._ffmpeg_advanced_args:
            no_sao_arg = self._ffmpeg_advanced_args['no-sao=']
            return no_sao_arg == '1'
        return False

    @no_sao.setter
    def no_sao(self, no_sao_enabled):
        """Stores no sao boolean as a string argument."""
        if no_sao_enabled is None or not no_sao_enabled:
            self._ffmpeg_advanced_args.pop('no-sao=', 0)
        else:
            self._ffmpeg_advanced_args['no-sao='] = '1'

    @property
    def sao_non_deblock(self):
        """Returns sao non deblock argument as a boolean."""
        if 'sao-non-deblock=' in self._ffmpeg_advanced_args:
            sao_non_deblock_args = self._ffmpeg_advanced_args['sao-non-deblock=']
            return sao_non_deblock_args == '1'
        return False

    @sao_non_deblock.setter
    def sao_non_deblock(self, sao_non_deblock_enabled):
        """Stores sao non deblock boolean as a string argument."""
        if sao_non_deblock_enabled is None or not sao_non_deblock_enabled:
            self._ffmpeg_advanced_args.pop('sao-non-deblock=', 0)
        else:
            self._ffmpeg_advanced_args['sao-non-deblock='] = '1'

    @property
    def limit_sao(self):
        """Returns limit sao argument as a boolean."""
        if 'limit-sao=' in self._ffmpeg_advanced_args:
            limit_sao_arg = self._ffmpeg_advanced_args['limit-sao=']
            return limit_sao_arg == '1'
        return False

    @limit_sao.setter
    def limit_sao(self, limit_sao_enabled):
        """Stores limit sao boolean as a string argument."""
        if limit_sao_enabled is None or not limit_sao_enabled:
            self._ffmpeg_advanced_args.pop('limit-sao=', 0)
        else:
            self._ffmpeg_advanced_args['limit-sao='] = '1'

    @property
    def selective_sao(self):
        """Returns selective sao argument as a boolean."""
        if 'selective-sao=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['selective-sao='])
        return 0

    @selective_sao.setter
    def selective_sao(self, selective_sao_value):
        """Stores selective sao boolean as a string argument."""
        if selective_sao_value is None or selective_sao_value < 0:
            self._ffmpeg_advanced_args.pop('selective-sao=', 0)
        else:
            self._ffmpeg_advanced_args['selective-sao='] = str(selective_sao_value)

    @property
    def rd(self):
        """Returns rd argument as an int."""
        if 'rd=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rd='])
        return 3

    @rd.setter
    def rd(self, rd_value):
        """Stores rd value as a string argument."""
        if rd_value is None or rd_value < 0:
            self._ffmpeg_advanced_args.pop('rd=', 0)
        else:
            self._ffmpeg_advanced_args['rd='] = str(rd_value)

    @property
    def rdoq_level(self):
        """Returns rdoq level argument as an intex."""
        if 'rdoq-level=' in self._ffmpeg_advanced_args:
            rdoq_level_arg = self._ffmpeg_advanced_args['rdoq-level=']
            return self.RDOQ_LEVEL_ARGS_LIST.index(rdoq_level_arg)
        return 0

    @rdoq_level.setter
    def rdoq_level(self, rdoq_level_index):
        """Stores index as a rdoq level argument."""
        if rdoq_level_index is None or rdoq_level_index < 1:
            self._ffmpeg_advanced_args.pop('rdoq-level=', 0)
        else:
            self._ffmpeg_advanced_args['rdoq-level='] = self.RDOQ_LEVEL_ARGS_LIST[rdoq_level_index]

    @property
    def rd_refine(self):
        """Returns rd refine argument as a boolean."""
        if 'rd-refine=' in self._ffmpeg_advanced_args:
            rd_refine_value = self._ffmpeg_advanced_args['rd-refine=']
            return rd_refine_value == '1'
        return False

    @rd_refine.setter
    def rd_refine(self, rd_refine_enabled):
        """Stores rd refine boolean as a string argument."""
        if rd_refine_enabled is None or not rd_refine_enabled:
            self._ffmpeg_advanced_args.pop('rd-refine=', 0)
        else:
            self._ffmpeg_advanced_args['rd-refine='] = '1'

    @property
    def ctu(self):
        """Returns ctu argument as an index."""
        if 'ctu=' in self._ffmpeg_advanced_args:
            ctu_arg = self._ffmpeg_advanced_args['ctu=']
            return self.MAX_CU_SIZE_ARGS_LIST.index(ctu_arg)
        return 0

    @ctu.setter
    def ctu(self, ctu_index):
        """Stores index as a ctu argument."""
        if ctu_index is None or ctu_index < 1:
            self._ffmpeg_advanced_args.pop('ctu=', 0)
        else:
            self._ffmpeg_advanced_args['ctu='] = self.MAX_CU_SIZE_ARGS_LIST[ctu_index]

    @property
    def min_cu_size(self):
        """Returns min cu size argument as an index."""
        if 'min-cu-size=' in self._ffmpeg_advanced_args:
            min_cu_size_arg = self._ffmpeg_advanced_args['min-cu-size=']
            return self.MIN_CU_SIZE_ARGS_LIST.index(min_cu_size_arg)
        return 0

    @min_cu_size.setter
    def min_cu_size(self, min_cu_size_index):
        """Stores index as a min cu size argument."""
        if min_cu_size_index is None or min_cu_size_index < 1:
            self._ffmpeg_advanced_args.pop('min-cu-size=', 0)
        else:
            self._ffmpeg_advanced_args['min-cu-size='] = self.MIN_CU_SIZE_ARGS_LIST[min_cu_size_index]

    @property
    def rect(self):
        """Returns rect argument as a boolean."""
        if 'rect=' in self._ffmpeg_advanced_args:
            rect_arg = self._ffmpeg_advanced_args['rect=']
            return rect_arg == '1'
        return False

    @rect.setter
    def rect(self, rect_enabled):
        """Stores rect boolean as a string argument."""
        if rect_enabled is None or not rect_enabled:
            self._ffmpeg_advanced_args.pop('rect=', 0)
        else:
            self._ffmpeg_advanced_args['rect='] = '1'

    @property
    def amp(self):
        """Returns amp argument as a boolean."""
        if 'amp=' in self._ffmpeg_advanced_args:
            amp_arg = self._ffmpeg_advanced_args['amp=']
            return amp_arg == '1'
        return False

    @amp.setter
    def amp(self, amp_enabled):
        """Stores amp boolean as a string argument."""
        if amp_enabled is None or not amp_enabled:
            self._ffmpeg_advanced_args.pop('amp=', 0)
        else:
            self._ffmpeg_advanced_args['amp='] = '1'

    @property
    def wpp(self):
        """Returns wpp argument as a boolean."""
        if 'wpp=' in self._ffmpeg_advanced_args:
            wpp_arg = self._ffmpeg_advanced_args['wpp=']
            return wpp_arg == '1'
        return False

    @wpp.setter
    def wpp(self, wpp_enabled):
        """Stores wpp boolean as a string argument."""
        if wpp_enabled is None or not wpp_enabled:
            self._ffmpeg_advanced_args.pop('wpp=', 0)
        else:
            self._ffmpeg_advanced_args['wpp='] = '1'

    @property
    def pmode(self):
        """Returns pmode argument as a boolean."""
        if 'pmode=' in self._ffmpeg_advanced_args:
            pmode_arg = self._ffmpeg_advanced_args['pmode=']
            return pmode_arg == '1'
        return False

    @pmode.setter
    def pmode(self, pmode_enabled):
        """Stores pmode boolean as a string argument."""
        if pmode_enabled is None or not pmode_enabled:
            self._ffmpeg_advanced_args.pop('pmode=', 0)
        else:
            self._ffmpeg_advanced_args['pmode='] = '1'

    @property
    def pme(self):
        """Returns pme argument as a boolean."""
        if 'pme=' in self._ffmpeg_advanced_args:
            pme_arg = self._ffmpeg_advanced_args['pme=']
            return pme_arg == '1'
        return False

    @pme.setter
    def pme(self, pme_enabled):
        """Stores pme boolean as a string argument."""
        if pme_enabled is None or not pme_enabled:
            self._ffmpeg_advanced_args.pop('pme=', 0)
        else:
            self._ffmpeg_advanced_args['pme='] = '1'

    @property
    def uhd_bd(self):
        """Returns uhd bd argument as a boolean."""
        if 'uhd-bd=' in self._ffmpeg_advanced_args:
            uhd_bd_value = self._ffmpeg_advanced_args['uhd-bd=']
            return uhd_bd_value == '1'
        return False

    @uhd_bd.setter
    def uhd_bd(self, uhd_bd_enabled):
        """Stores uhd bd boolean as a string argument."""
        if uhd_bd_enabled is None or not uhd_bd_enabled:
            self._ffmpeg_advanced_args.pop('uhd-bd=', 0)
        else:
            self._ffmpeg_advanced_args['uhd-bd='] = '1'

    @property
    def encode_pass(self):
        """Returns encode pass argument as an int."""
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        """Stores encode pass value as a string argument."""
        if encode_pass_value is None or encode_pass_value < 1 or encode_pass_value > 2:
            self._ffmpeg_advanced_args.pop('pass=', 0)
        else:
            self._ffmpeg_advanced_args['pass='] = str(encode_pass_value)

    @property
    def stats(self):
        """Returns stats argument as a file path string."""
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return None

    @stats.setter
    def stats(self, file_path):
        """Stores file path as a string argument."""
        if file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = file_path

    def get_ffmpeg_advanced_args(self):
        """Returns dictionary with advanced args string."""
        advanced_args = {'-x265-params': None}

        args = ''
        if self.advanced_enabled:
            args = self._generate_advanced_args()
        else:
            if self._ffmpeg_advanced_args['pass=']:
                args = self._get_pass_args()
        if args:
            advanced_args['-x265-params'] = args
        return advanced_args

    def _get_pass_args(self):
        """Returns string for encode pass arguments."""
        pass_args = 'pass='
        pass_args += str(self.encode_pass)
        pass_args += ':'
        pass_args += 'stats='
        pass_args += self._ffmpeg_advanced_args['stats=']
        return pass_args

    def _generate_advanced_args(self):
        """Returns string for all advanced settings."""
        x265_advanced_settings = ''
        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x265_advanced_settings += setting
                x265_advanced_settings += arg
                x265_advanced_settings += ':'
        return x265_advanced_settings
