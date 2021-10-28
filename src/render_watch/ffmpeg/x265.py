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
    """
    Stores all settings for the x265 codec.
    """

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
            '-c:v': 'libx265',
            '-crf': '20.0'
        }
        self.advanced_enabled = False
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self):
        """
        Returns crf as a float.
        """
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return None

    @crf.setter
    def crf(self, crf):
        """
        Stores crf as a string.
        """
        if crf is None or crf < 0 or crf > 51:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf)
            self.qp = None
            self.bitrate = None

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
        if qp is None or qp < 0 or qp > 51:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp)
            self.crf = None
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
        if bitrate is None or bitrate <= 0 or bitrate > 99999:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate) + 'k'
            self.crf = None
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
        if profile_index is None or not 0 < profile_index < X265.PROFILE_LIST_LENGTH:
            self.ffmpeg_args.pop('-profile:v', 0)
        else:
            self.ffmpeg_args['-profile:v'] = self.PROFILE_ARGS_LIST[profile_index]

    @property
    def preset(self):
        """
        Returns preset as an index.
        """
        if '-preset' in self.ffmpeg_args:
            preset_value = self.ffmpeg_args['-preset']
            return self.PRESET_ARGS_LIST.index(preset_value)
        return 0

    @preset.setter
    def preset(self, preset_index):
        """
        Stores preset index as a string.
        """
        if preset_index is None or not 0 < preset_index < X265.PRESET_LIST_LENGTH:
            self.ffmpeg_args.pop('-preset', 0)
        else:
            self.ffmpeg_args['-preset'] = self.PRESET_ARGS_LIST[preset_index]

    @property
    def level(self):
        """
        Returns level as an index.
        """
        if '-level' in self.ffmpeg_args:
            level_value = self.ffmpeg_args['-level']
            return self.LEVEL_ARGS_LIST.index(level_value)
        return 0

    @level.setter
    def level(self, level_index):
        """
        Stores level index as a string.
        """
        if level_index is None or not 0 < level_index < X265.LEVEL_LIST_LENGTH:
            self.ffmpeg_args.pop('-level', 0)
        else:
            self.ffmpeg_args['-level'] = self.LEVEL_ARGS_LIST[level_index]

    @property
    def tune(self):
        """
        Returns tune as an index.
        """
        if '-tune' in self.ffmpeg_args:
            tune_value = self.ffmpeg_args['-tune']
            return self.TUNE_ARGS_LIST.index(tune_value)
        return 0

    @tune.setter
    def tune(self, tune_index):
        """
        Stores tune index as a string.
        """
        if tune_index is None or not 0 < tune_index < X265.TUNE_LIST_LENGTH:
            self.ffmpeg_args.pop('-tune', 0)
        else:
            self.ffmpeg_args['-tune'] = self.TUNE_ARGS_LIST[tune_index]

    @property
    def vbv_maxrate(self):
        """
        Returns vbv maxrate as an int.
        """
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate):
        """
        Stores vbv maxrate as a string.
        """
        if vbv_maxrate is None or not 0 < vbv_maxrate <= 99999:
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate)

    @property
    def vbv_bufsize(self):
        """
        Returns vbv bufsize as an int.
        """
        if 'vbv-bufsize=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-bufsize='])
        return 2500

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize):
        """
        Stores vbv bufsize as a string.
        """
        if vbv_bufsize is None or not 0 < vbv_bufsize <= 99999:
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize)

    @property
    def aq_mode(self):
        """
        Returns aq mode as an index.
        """
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_arg = self._ffmpeg_advanced_args['aq-mode=']
            return self.AQ_MODE_ARGS_LIST.index(aq_mode_arg)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index):
        """
        Stores aq mode index as a string.
        """
        if aq_mode_index is None or not 0 < aq_mode_index < X265.AQ_MODE_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('aq-mode=', 0)
        else:
            self._ffmpeg_advanced_args['aq-mode='] = self.AQ_MODE_ARGS_LIST[aq_mode_index]

    @property
    def aq_strength(self):
        """
        Returns aq strength as a float.
        """
        if 'aq-strength=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['aq-strength='])
        return 1.0

    @aq_strength.setter
    def aq_strength(self, aq_strength):
        """
        Stores aq strength as a string.
        """
        if aq_strength is None or aq_strength < 0:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(aq_strength)

    @property
    def hevc_aq(self):
        """
        Returns hevc aq as a boolean.
        """
        if 'hevc-aq=' in self._ffmpeg_advanced_args:
            hevc_aq_arg = self._ffmpeg_advanced_args['hevc-aq=']
            return hevc_aq_arg == '1'
        return False

    @hevc_aq.setter
    def hevc_aq(self, hevc_aq_enabled):
        """
        Stores hevc aq as a string.
        """
        if hevc_aq_enabled is None or not hevc_aq_enabled:
            self._ffmpeg_advanced_args.pop('hevc-aq=', 0)
        else:
            self._ffmpeg_advanced_args['hevc-aq='] = '1'

    @property
    def keyint(self):
        """
        Returns keyint as an int.
        """
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint):
        """
        Stores keyint as a string.
        """
        if keyint is None or keyint < 0:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint)

    @property
    def min_keyint(self):
        """
        Returns min keyint as an int.
        """
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 0

    @min_keyint.setter
    def min_keyint(self, min_keyint):
        """
        Stores min keyint as a string.
        """
        if min_keyint is None or min_keyint < 0:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint)

    @property
    def ref(self):
        """
        Returns ref as an int.
        """
        if 'ref=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['ref='])
        return 3

    @ref.setter
    def ref(self, ref):
        """
        Stores ref as a string.
        """
        if ref is None or ref < 0:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref)

    @property
    def bframes(self):
        """
        Returns bframes as an int.
        """
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 4

    @bframes.setter
    def bframes(self, bframes):
        """
        Stores bframes as a string.
        """
        if bframes is None or bframes < 0:
            self._ffmpeg_advanced_args.pop('bframes=', 0)
        else:
            self._ffmpeg_advanced_args['bframes='] = str(bframes)

    @property
    def b_adapt(self):
        """
        Returns b adapt as an index.
        """
        if 'b-adapt=' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['b-adapt=']
            return self.B_ADAPT_ARGS_LIST.index(b_adapt_arg)
        return 0

    @b_adapt.setter
    def b_adapt(self, b_adapt_index):
        """
        Stores b adapt index as a string.
        """
        if b_adapt_index is None or not 0 < b_adapt_index < X265.B_ADAPT_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)
        else:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT_ARGS_LIST[b_adapt_index]

    @property
    def no_b_pyramid(self):
        """
        Returns no b pyramid as a boolean.
        """
        if 'no-b-pyramid=' in self._ffmpeg_advanced_args:
            no_b_pyramid_arg = self._ffmpeg_advanced_args['no-b-pyramid=']
            return no_b_pyramid_arg == '1'
        return False

    @no_b_pyramid.setter
    def no_b_pyramid(self, no_b_pyramid_enabled):
        """
        Stores no b pyramid as a string.
        """
        if no_b_pyramid_enabled is None or not no_b_pyramid_enabled:
            self._ffmpeg_advanced_args.pop('no-b-pyramid=', 0)
        else:
            self._ffmpeg_advanced_args['no-b-pyramid='] = '1'

    @property
    def b_intra(self):
        """
        Returns b intra as a boolean.
        """
        if 'b-intra=' in self._ffmpeg_advanced_args:
            b_intra_arg = self._ffmpeg_advanced_args['b-intra=']
            return b_intra_arg == '1'
        return False

    @b_intra.setter
    def b_intra(self, b_intra_enabled):
        """
        Stores b intra as a string.
        """
        if b_intra_enabled is None or not b_intra_enabled:
            self._ffmpeg_advanced_args.pop('b-intra=', 0)
        else:
            self._ffmpeg_advanced_args['b-intra='] = '1'

    @property
    def no_open_gop(self):
        """
        Returns no open gop as a boolean.
        """
        if 'no-open-gop=' in self._ffmpeg_advanced_args:
            no_open_gop_arg = self._ffmpeg_advanced_args['no-open-gop=']
            return no_open_gop_arg == '1'
        return False

    @no_open_gop.setter
    def no_open_gop(self, no_open_gop_enabled):
        """
        Stores no open gop as a string.
        """
        if no_open_gop_enabled is None or not no_open_gop_enabled:
            self._ffmpeg_advanced_args.pop('no-open-gop=', 0)
        else:
            self._ffmpeg_advanced_args['no-open-gop='] = '1'

    @property
    def rc_lookahead(self):
        """
        Returns rc lookahead as an int.
        """
        if 'rc-lookahead=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rc-lookahead='])
        return 20

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead):
        """
        Stores rc lookahead as a string.
        """
        if rc_lookahead is None or rc_lookahead < 0:
            self._ffmpeg_advanced_args.pop('rc-lookahead=', 0)
        else:
            self._ffmpeg_advanced_args['rc-lookahead='] = str(rc_lookahead)

    @property
    def no_scenecut(self):
        """
        Returns no scenecut as a boolean.
        """
        if 'no-scenecut=' in self._ffmpeg_advanced_args:
            no_scenecut_arg = self._ffmpeg_advanced_args['no-scenecut=']
            return no_scenecut_arg == '1'
        return False

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut_enabled):
        """
        Stores no scenecut as a string.
        """
        if no_scenecut_enabled is None or not no_scenecut_enabled:
            self._ffmpeg_advanced_args.pop('no-scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['no-scenecut='] = '1'

    @property
    def no_high_tier(self):
        """
        Returns no high tier as a boolean.
        """
        if 'no-high-tier=' in self._ffmpeg_advanced_args:
            no_high_tier_arg = self._ffmpeg_advanced_args['no-high-tier=']
            return no_high_tier_arg == '1'
        return False

    @no_high_tier.setter
    def no_high_tier(self, no_high_tier_enabled):
        """
        Stores no high tier as a string.
        """
        if no_high_tier_enabled is None or not no_high_tier_enabled:
            self._ffmpeg_advanced_args.pop('no-high-tier=', 0)
        else:
            self._ffmpeg_advanced_args['no-high-tier='] = '1'

    @property
    def psy_rd(self):
        """
        Returns psy rd as a float.
        """
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rd='])
        return 2.0

    @psy_rd.setter
    def psy_rd(self, psy_rd):
        """
        Stores psy rd as a string.
        """
        if psy_rd is None or psy_rd < 0:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rd='] = str(psy_rd)

    @property
    def psy_rdoq(self):
        """
        Returns psy rdoq as a float.
        """
        if 'psy-rdoq=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['psy-rdoq='])
        return 0.0

    @psy_rdoq.setter
    def psy_rdoq(self, psy_rdoq):
        """
        Stores psy rdoq as a string.
        """
        if psy_rdoq is None or psy_rdoq < 0:
            self._ffmpeg_advanced_args.pop('psy-rdoq=', 0)
        else:
            self._ffmpeg_advanced_args['psy-rdoq='] = str(psy_rdoq)

    @property
    def me(self):
        """
        Returns me as an index.
        """
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']
            return self.ME_ARGS_LIST.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index):
        """
        Stores me index as a string.
        """
        if me_index is None or not 0 < me_index < X265.ME_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('me=', 0)
        else:
            self._ffmpeg_advanced_args['me='] = self.ME_ARGS_LIST[me_index]

    @property
    def subme(self):
        """
        Returns subme as an int.
        """
        if 'subme=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['subme='])
        return 2

    @subme.setter
    def subme(self, subme):
        """
        Stores subme as a string.
        """
        if subme is None or subme < 0:
            self._ffmpeg_advanced_args.pop('subme=', 0)
        else:
            self._ffmpeg_advanced_args['subme='] = str(subme)

    @property
    def weightb(self):
        """
        Return weight b as a boolean.
        """
        if 'weightb=' in self._ffmpeg_advanced_args:
            weightb_arg = self._ffmpeg_advanced_args['weightb=']
            return weightb_arg == '1'
        return False

    @weightb.setter
    def weightb(self, weightb_enabled):
        """
        Stores weight b as a string.
        """
        if weightb_enabled is None or not weightb_enabled:
            self._ffmpeg_advanced_args.pop('weightb=', 0)
        else:
            self._ffmpeg_advanced_args['weightb='] = '1'

    @property
    def no_weightp(self):
        """
        Returns no weightp as a boolean.
        """
        if 'no-weightp=' in self._ffmpeg_advanced_args:
            no_weightp_arg = self._ffmpeg_advanced_args['no-weightp=']
            return no_weightp_arg == '1'
        return False

    @no_weightp.setter
    def no_weightp(self, no_weightp_enabled):
        """
        Stores no weightp as a string.
        """
        if no_weightp_enabled is None or not no_weightp_enabled:
            self._ffmpeg_advanced_args.pop('no-weightp=', 0)
        else:
            self._ffmpeg_advanced_args['no-weightp='] = '1'

    @property
    def deblock(self):
        """
        Returns deblock as a tuple of ints.
        """
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')
            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock):
        """
        Stores deblock tuple as a string.
        """
        if deblock is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def no_deblock(self):
        """
        Returns no deblock as a boolean.
        """
        if 'no-deblock=' in self._ffmpeg_advanced_args:
            no_deblock_arg = self._ffmpeg_advanced_args['no-deblock=']
            return no_deblock_arg == '1'
        return False

    @no_deblock.setter
    def no_deblock(self, no_deblock_enabled):
        """
        Stores no deblock as a string.
        """
        if no_deblock_enabled is None or not no_deblock_enabled:
            self._ffmpeg_advanced_args.pop('no-deblock=', 0)
        else:
            self._ffmpeg_advanced_args['no-deblock='] = '1'

    @property
    def no_sao(self):
        """
        Returns no sao as a boolean.
        """
        if 'no-sao=' in self._ffmpeg_advanced_args:
            no_sao_arg = self._ffmpeg_advanced_args['no-sao=']
            return no_sao_arg == '1'
        return False

    @no_sao.setter
    def no_sao(self, no_sao_enabled):
        """
        Stores no sao as a string.
        """
        if no_sao_enabled is None or not no_sao_enabled:
            self._ffmpeg_advanced_args.pop('no-sao=', 0)
        else:
            self._ffmpeg_advanced_args['no-sao='] = '1'

    @property
    def sao_non_deblock(self):
        """
        Returns sao non deblock as a boolean.
        """
        if 'sao-non-deblock=' in self._ffmpeg_advanced_args:
            sao_non_deblock_args = self._ffmpeg_advanced_args['sao-non-deblock=']
            return sao_non_deblock_args == '1'
        return False

    @sao_non_deblock.setter
    def sao_non_deblock(self, sao_non_deblock_enabled):
        """
        Stores sao non deblock as a string.
        """
        if sao_non_deblock_enabled is None or not sao_non_deblock_enabled:
            self._ffmpeg_advanced_args.pop('sao-non-deblock=', 0)
        else:
            self._ffmpeg_advanced_args['sao-non-deblock='] = '1'

    @property
    def limit_sao(self):
        """
        Returns limit sao as a boolean.
        """
        if 'limit-sao=' in self._ffmpeg_advanced_args:
            limit_sao_arg = self._ffmpeg_advanced_args['limit-sao=']
            return limit_sao_arg == '1'
        return False

    @limit_sao.setter
    def limit_sao(self, limit_sao_enabled):
        """
        Stores limit sao as a string.
        """
        if limit_sao_enabled is None or not limit_sao_enabled:
            self._ffmpeg_advanced_args.pop('limit-sao=', 0)
        else:
            self._ffmpeg_advanced_args['limit-sao='] = '1'

    @property
    def selective_sao(self):
        """
        Returns selective sao as an int.
        """
        if 'selective-sao=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['selective-sao='])
        return 0

    @selective_sao.setter
    def selective_sao(self, selective_sao):
        """
        Stores selective sao as a string.
        """
        if selective_sao is None or selective_sao < 0:
            self._ffmpeg_advanced_args.pop('selective-sao=', 0)
        else:
            self._ffmpeg_advanced_args['selective-sao='] = str(selective_sao)

    @property
    def rd(self):
        """
        Returns rd as an int.
        """
        if 'rd=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['rd='])
        return 3

    @rd.setter
    def rd(self, rd):
        """
        Stores rd as a string.
        """
        if rd is None or rd < 0:
            self._ffmpeg_advanced_args.pop('rd=', 0)
        else:
            self._ffmpeg_advanced_args['rd='] = str(rd)

    @property
    def rdoq_level(self):
        """
        Returns rdoq level as an intex.
        """
        if 'rdoq-level=' in self._ffmpeg_advanced_args:
            rdoq_level_arg = self._ffmpeg_advanced_args['rdoq-level=']
            return self.RDOQ_LEVEL_ARGS_LIST.index(rdoq_level_arg)
        return 0

    @rdoq_level.setter
    def rdoq_level(self, rdoq_level_index):
        """
        Stores rdoq level index as a string.
        """
        if rdoq_level_index is None or not 0 < rdoq_level_index < X265.RDOQ_LEVEL_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('rdoq-level=', 0)
        else:
            self._ffmpeg_advanced_args['rdoq-level='] = self.RDOQ_LEVEL_ARGS_LIST[rdoq_level_index]

    @property
    def rd_refine(self):
        """
        Returns rd refine as a boolean.
        """
        if 'rd-refine=' in self._ffmpeg_advanced_args:
            rd_refine_value = self._ffmpeg_advanced_args['rd-refine=']
            return rd_refine_value == '1'
        return False

    @rd_refine.setter
    def rd_refine(self, rd_refine_enabled):
        """
        Stores rd refine as a string.
        """
        if rd_refine_enabled is None or not rd_refine_enabled:
            self._ffmpeg_advanced_args.pop('rd-refine=', 0)
        else:
            self._ffmpeg_advanced_args['rd-refine='] = '1'

    @property
    def ctu(self):
        """
        Returns ctu as an index.
        """
        if 'ctu=' in self._ffmpeg_advanced_args:
            ctu_arg = self._ffmpeg_advanced_args['ctu=']
            return self.MAX_CU_SIZE_ARGS_LIST.index(ctu_arg)
        return 0

    @ctu.setter
    def ctu(self, ctu_index):
        """
        Stores ctu index as a string.
        """
        if ctu_index is None or not 0 < ctu_index < X265.MAX_CU_SIZE_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('ctu=', 0)
        else:
            self._ffmpeg_advanced_args['ctu='] = self.MAX_CU_SIZE_ARGS_LIST[ctu_index]

    @property
    def min_cu_size(self):
        """
        Returns min cu size as an index.
        """
        if 'min-cu-size=' in self._ffmpeg_advanced_args:
            min_cu_size_arg = self._ffmpeg_advanced_args['min-cu-size=']
            return self.MIN_CU_SIZE_ARGS_LIST.index(min_cu_size_arg)
        return 0

    @min_cu_size.setter
    def min_cu_size(self, min_cu_size_index):
        """
        Stores min cu size index as a string.
        """
        if min_cu_size_index is None or not 0 < min_cu_size_index < X265.MIN_CU_SIZE_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('min-cu-size=', 0)
        else:
            self._ffmpeg_advanced_args['min-cu-size='] = self.MIN_CU_SIZE_ARGS_LIST[min_cu_size_index]

    @property
    def rect(self):
        """
        Returns rect as a boolean.
        """
        if 'rect=' in self._ffmpeg_advanced_args:
            rect_arg = self._ffmpeg_advanced_args['rect=']
            return rect_arg == '1'
        return False

    @rect.setter
    def rect(self, rect_enabled):
        """
        Stores rect as a string.
        """
        if rect_enabled is None or not rect_enabled:
            self._ffmpeg_advanced_args.pop('rect=', 0)
        else:
            self._ffmpeg_advanced_args['rect='] = '1'

    @property
    def amp(self):
        """
        Returns amp as a boolean.
        """
        if 'amp=' in self._ffmpeg_advanced_args:
            amp_arg = self._ffmpeg_advanced_args['amp=']
            return amp_arg == '1'
        return False

    @amp.setter
    def amp(self, amp_enabled):
        """
        Stores amp as a string.
        """
        if amp_enabled is None or not amp_enabled:
            self._ffmpeg_advanced_args.pop('amp=', 0)
        else:
            self._ffmpeg_advanced_args['amp='] = '1'

    @property
    def wpp(self):
        """
        Returns wpp as a boolean.
        """
        if 'wpp=' in self._ffmpeg_advanced_args:
            wpp_arg = self._ffmpeg_advanced_args['wpp=']
            return wpp_arg == '1'
        return False

    @wpp.setter
    def wpp(self, wpp_enabled):
        """
        Stores wpp as a string.
        """
        if wpp_enabled is None or not wpp_enabled:
            self._ffmpeg_advanced_args.pop('wpp=', 0)
        else:
            self._ffmpeg_advanced_args['wpp='] = '1'

    @property
    def pmode(self):
        """
        Returns pmode as a boolean.
        """
        if 'pmode=' in self._ffmpeg_advanced_args:
            pmode_arg = self._ffmpeg_advanced_args['pmode=']
            return pmode_arg == '1'
        return False

    @pmode.setter
    def pmode(self, pmode_enabled):
        """
        Stores pmode as a string.
        """
        if pmode_enabled is None or not pmode_enabled:
            self._ffmpeg_advanced_args.pop('pmode=', 0)
        else:
            self._ffmpeg_advanced_args['pmode='] = '1'

    @property
    def pme(self):
        """
        Returns pme as a boolean.
        """
        if 'pme=' in self._ffmpeg_advanced_args:
            pme_arg = self._ffmpeg_advanced_args['pme=']
            return pme_arg == '1'
        return False

    @pme.setter
    def pme(self, pme_enabled):
        """
        Stores pme as a string.
        """
        if pme_enabled is None or not pme_enabled:
            self._ffmpeg_advanced_args.pop('pme=', 0)
        else:
            self._ffmpeg_advanced_args['pme='] = '1'

    @property
    def uhd_bd(self):
        """
        Returns uhd bd as a boolean.
        """
        if 'uhd-bd=' in self._ffmpeg_advanced_args:
            uhd_bd_value = self._ffmpeg_advanced_args['uhd-bd=']
            return uhd_bd_value == '1'
        return False

    @uhd_bd.setter
    def uhd_bd(self, uhd_bd_enabled):
        """
        Stores uhd bd as a string.
        """
        if uhd_bd_enabled is None or not uhd_bd_enabled:
            self._ffmpeg_advanced_args.pop('uhd-bd=', 0)
        else:
            self._ffmpeg_advanced_args['uhd-bd='] = '1'

    @property
    def encode_pass(self):
        """
        Returns encode pass as an int.
        """
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass):
        """
        Stores encode pass as a string.
        """
        if encode_pass is None or not 1 <= encode_pass <= 2:
            self._ffmpeg_advanced_args.pop('pass=', 0)
        else:
            self._ffmpeg_advanced_args['pass='] = str(encode_pass)

    @property
    def stats(self):
        """
        Returns stats as a file path.
        """
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return None

    @stats.setter
    def stats(self, stats_file_path):
        """
        Stores stats file path as a string.
        """
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    def get_ffmpeg_advanced_args(self):
        """
        Returns dictionary with advanced args.
        """
        advanced_args = {'-x265-params': None}

        args = ''
        if self.advanced_enabled:
            args = self._generate_advanced_args()
        else:
            if 'pass=' in self._ffmpeg_advanced_args:
                args = self._get_pass_args()
        if args:
            advanced_args['-x265-params'] = args
        return advanced_args

    def _get_pass_args(self):
        """
        Returns args string for encode pass.
        """
        pass_args = 'pass='
        pass_args += str(self.encode_pass)
        pass_args += ':'
        pass_args += 'stats='
        pass_args += self._ffmpeg_advanced_args['stats=']
        return pass_args

    def _generate_advanced_args(self):
        """
        Returns args string for all advanced settings.
        """
        x265_advanced_settings = ''
        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x265_advanced_settings += setting
                x265_advanced_settings += arg
                x265_advanced_settings += ':'
        return x265_advanced_settings
