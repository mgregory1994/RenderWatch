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


class X264:
    """
    Stores all settings for the x264 codec.
    """

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

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libx264',
            '-crf': '20.0'
        }
        self.is_advanced_enabled = False
        self._ffmpeg_advanced_args = {}

    @property
    def codec_name(self) -> str:
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self) -> float:
        if '-crf' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-crf'])
        return 20.0

    @crf.setter
    def crf(self, crf_value: float | None):
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)
            self.qp = None
            self.bitrate = None

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
            self.crf = None
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
            self.crf = None
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
        """
        Stores profile index as a string.
        """
        if profile_index and 0 < profile_index < X264.PROFILE_LENGTH:
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
        if preset_index and 0 < preset_index < X264.PRESET_LENGTH:
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
        if level_index and 0 < level_index < X264.LEVEL_LENGTH:
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
        if tune_index and 0 < tune_index < X264.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def keyint(self) -> int:
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value: int | None):
        if keyint_value is None:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint_value)

    @property
    def min_keyint(self) -> int:
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 25

    @min_keyint.setter
    def min_keyint(self, min_keyint_value: int | None):
        if min_keyint_value is None:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def scenecut(self) -> int:
        if 'scenecut=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['scenecut='])
        return 0

    @scenecut.setter
    def scenecut(self, scenecut_value: int | None):
        if scenecut_value is None:
            self._ffmpeg_advanced_args.pop('scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['scenecut='] = str(scenecut_value)

    @property
    def bframes(self) -> int:
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 3

    @bframes.setter
    def bframes(self, bframes_value: int | None):
        if bframes_value is None:
            self._ffmpeg_advanced_args.pop('bframes=', 0)
        else:
            self._ffmpeg_advanced_args['bframes='] = str(bframes_value)

    @property
    def b_adapt(self) -> int:
        """
        Returns b adapt as an index.
        """
        if 'b-adapt=' in self._ffmpeg_advanced_args:
            b_adapt_arg = self._ffmpeg_advanced_args['b-adapt=']

            return self.B_ADAPT.index(b_adapt_arg)
        return 0

    @b_adapt.setter
    def b_adapt(self, b_adapt_index: int | None):
        if b_adapt_index and 0 < b_adapt_index < X264.B_ADAPT_LENGTH:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT[b_adapt_index]
        else:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)

    @property
    def b_pyramid(self) -> int:
        """
        Returns b pyramid as an index.
        """
        if 'b-pyramid=' in self._ffmpeg_advanced_args:
            b_pyramid_arg = self._ffmpeg_advanced_args['b-pyramid=']

            return self.B_PYRAMID.index(b_pyramid_arg)
        return 0

    @b_pyramid.setter
    def b_pyramid(self, b_pyramid_index: int | None):
        if b_pyramid_index and 0 < b_pyramid_index < X264.B_PYRAMID_LENGTH:
            self._ffmpeg_advanced_args['b-pyramid='] = self.B_PYRAMID[b_pyramid_index]
        else:
            self._ffmpeg_advanced_args.pop('b-pyramid=', 0)

    @property
    def no_cabac(self) -> bool:
        if 'no-cabac=' in self._ffmpeg_advanced_args:
            no_cabac_arg = self._ffmpeg_advanced_args['no-cabac=']

            return no_cabac_arg == '1'
        return False

    @no_cabac.setter
    def no_cabac(self, is_no_cabac_enabled: bool):
        if is_no_cabac_enabled:
            self._ffmpeg_advanced_args['no-cabac='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-cabac=', 0)

    @property
    def ref(self) -> int:
        if 'ref=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['ref='])
        return 3

    @ref.setter
    def ref(self, ref_value: int | None):
        if ref_value is None:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref_value)

    @property
    def no_deblock(self) -> bool:
        if 'no-deblock=' in self._ffmpeg_advanced_args:
            no_deblock_arg = self._ffmpeg_advanced_args['no-deblock=']

            return no_deblock_arg == '1'
        return False

    @no_deblock.setter
    def no_deblock(self, is_no_deblock_enabled: bool):
        if is_no_deblock_enabled:
            self._ffmpeg_advanced_args['no-deblock='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-deblock=', 0)

    @property
    def deblock(self) -> tuple:
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')

            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock_tuple: tuple | None):
        if deblock_tuple is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock_tuple
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def vbv_maxrate(self) -> int:
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value: int | None):
        if vbv_maxrate_value is None:
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)

    @property
    def vbv_bufsize(self) -> int:
        if 'vbv-bufsize=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-bufsize='])
        return 2500

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize_value: int | None):
        if vbv_bufsize_value is None:
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    @property
    def aq_mode(self) -> int:
        """
        Returns aq mode as an index.
        """
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_value = self._ffmpeg_advanced_args['aq-mode=']

            return self.AQ_MODE.index(aq_mode_value)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index: int | None):
        if aq_mode_index and 0 < aq_mode_index < X264.AQ_MODE_LENGTH:
            self._ffmpeg_advanced_args['aq-mode='] = self.AQ_MODE[aq_mode_index]
        else:
            self._ffmpeg_advanced_args.pop('aq-mode=', 0)

    @property
    def aq_strength(self) -> float:
        if 'aq-strength=' in self._ffmpeg_advanced_args:
            return float(self._ffmpeg_advanced_args['aq-strength='])
        return 1.0

    @aq_strength.setter
    def aq_strength(self, aq_strength_value: float | None):
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)

    @property
    def encode_pass(self) -> int:
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return 0

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        if encode_pass_value is None:
            self._ffmpeg_advanced_args.pop('pass=', 0)
        else:
            self._ffmpeg_advanced_args['pass='] = str(encode_pass_value)

    @property
    def stats(self) -> str:
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    @property
    def partitions(self) -> tuple:
        if 'partitions=' in self._ffmpeg_advanced_args:
            partitions_arg = self._ffmpeg_advanced_args['partitions=']

            if partitions_arg == 'all' or partitions_arg == 'none':
                return partitions_arg
            return partitions_arg.split(',')
        return ()

    @partitions.setter
    def partitions(self, partitions_tuple: tuple | str | None):
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
        Returns direct as an index.
        """
        if 'direct=' in self._ffmpeg_advanced_args:
            direct_arg = self._ffmpeg_advanced_args['direct=']

            return self.DIRECT.index(direct_arg)
        return 0

    @direct.setter
    def direct(self, direct_index: int | None):
        """
        Stores direct index as a string.
        """
        if direct_index and 0 < direct_index < X264.DIRECT_LENGTH:
            self._ffmpeg_advanced_args['direct='] = self.DIRECT[direct_index]
        else:
            self._ffmpeg_advanced_args.pop('direct=', 0)

    @property
    def weightb(self) -> bool:
        if 'weightb=' in self._ffmpeg_advanced_args:
            weightb_arg = self._ffmpeg_advanced_args['weightb=']

            return weightb_arg == '1'
        return False

    @weightb.setter
    def weightb(self, is_weightb_enabled: bool):
        if is_weightb_enabled:
            self._ffmpeg_advanced_args['weightb='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('weightb=', 0)

    @property
    def me(self) -> int:
        """
        Returns me as an index.
        """
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']

            return self.ME.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index: int | None):
        if me_index and 0 < me_index < X264.ME_LENGTH:
            self._ffmpeg_advanced_args['me='] = self.ME[me_index]
        else:
            self._ffmpeg_advanced_args.pop('me=', 0)

    @property
    def me_range(self) -> int:
        if 'merange=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['merange='])
        return 16

    @me_range.setter
    def me_range(self, me_range_value: int | None):
        if me_range_value is None:
            self._ffmpeg_advanced_args.pop('merange=', 0)
        else:
            self._ffmpeg_advanced_args['merange='] = str(me_range_value)

    @property
    def subme(self) -> int:
        """
        Returns subme as an index.
        """
        if 'subme=' in self._ffmpeg_advanced_args:
            subme_arg = self._ffmpeg_advanced_args['subme=']

            return self.SUB_ME.index(subme_arg)
        return 0

    @subme.setter
    def subme(self, subme_index: int | None):
        if subme_index and 0 < subme_index < X264.SUB_ME_LENGTH:
            self._ffmpeg_advanced_args['subme='] = self.SUB_ME[subme_index]
        else:
            self._ffmpeg_advanced_args.pop('subme=', 0)

    @property
    def psy_rd(self) -> tuple:
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            psy_rd_arg = self._ffmpeg_advanced_args['psy-rd=']
            psy_rd, psy_rd_trellis = psy_rd_arg.split(',')

            return float(psy_rd), float(psy_rd_trellis)
        return 1.0, 0.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_tuple: tuple | None):
        if psy_rd_tuple is None:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            psy_rd, psy_rd_trellis = psy_rd_tuple
            self._ffmpeg_advanced_args['psy-rd='] = str(psy_rd) + ',' + str(psy_rd_trellis)

    @property
    def mixed_refs(self) -> bool:
        if 'mixed-refs=' in self._ffmpeg_advanced_args:
            mixed_refs_arg = self._ffmpeg_advanced_args['mixed-refs=']

            return mixed_refs_arg == '1'
        return False

    @mixed_refs.setter
    def mixed_refs(self, is_mixed_refs_enabled: bool):
        if is_mixed_refs_enabled:
            self._ffmpeg_advanced_args['mixed-refs='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('mixed-refs=', 0)

    @property
    def dct8x8(self) -> bool:
        if '8x8dct=' in self._ffmpeg_advanced_args:
            dct_arg = self._ffmpeg_advanced_args['8x8dct=']

            return dct_arg == '1'
        return False

    @dct8x8.setter
    def dct8x8(self, is_dct8x8_enabled: bool):
        if is_dct8x8_enabled:
            self._ffmpeg_advanced_args['8x8dct='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('8x8dct=', 0)

    @property
    def trellis(self) -> int:
        """
        Returns trellis as an index.
        """
        if 'trellis=' in self._ffmpeg_advanced_args:
            trellis_arg = self._ffmpeg_advanced_args['trellis=']

            return self.TRELLIS.index(trellis_arg)
        return 0

    @trellis.setter
    def trellis(self, trellis_index: int | None):
        if trellis_index and 0 < trellis_index < X264.TRELLIST_LENGTH:
            self._ffmpeg_advanced_args['trellis='] = self.TRELLIS[trellis_index]
        else:
            self._ffmpeg_advanced_args.pop('trellis=', 0)

    @property
    def no_fast_pskip(self) -> bool:
        if 'no-fast-pskip=' in self._ffmpeg_advanced_args:
            no_fast_pskip_arg = self._ffmpeg_advanced_args['no-fast-pskip=']

            return no_fast_pskip_arg == '1'
        return False

    @no_fast_pskip.setter
    def no_fast_pskip(self, is_no_fast_pskip_enabled: bool):
        if is_no_fast_pskip_enabled:
            self._ffmpeg_advanced_args['no-fast-pskip='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-fast-pskip=', 0)

    @property
    def no_dct_decimate(self) -> bool:
        if 'no-dct-decimate=' in self._ffmpeg_advanced_args:
            no_dct_decimate_arg = self._ffmpeg_advanced_args['no-dct-decimate=']

            return no_dct_decimate_arg == '1'
        return False

    @no_dct_decimate.setter
    def no_dct_decimate(self, is_no_dct_decimate_enabled: bool):
        if is_no_dct_decimate_enabled:
            self._ffmpeg_advanced_args['no-dct-decimate='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-dct-decimate=', 0)

    @property
    def constant_bitrate(self) -> bool:
        if 'nal_hrd=' in self._ffmpeg_advanced_args:
            constant_bitrate_arg = self._ffmpeg_advanced_args['nal_hrd=']

            return constant_bitrate_arg == 'cbr'
        return False

    @constant_bitrate.setter
    def constant_bitrate(self, is_constant_bitrate_enabled: bool):
        if is_constant_bitrate_enabled:
            self._ffmpeg_advanced_args['nal_hrd='] = 'cbr'
        else:
            self._ffmpeg_advanced_args.pop('nal_hrd=', 0)

    @property
    def weightp(self) -> int:
        """
        Returns weightp as an index.
        """
        if 'weightp=' in self._ffmpeg_advanced_args:
            weightp_arg = self._ffmpeg_advanced_args['weightp=']

            return self.WEIGHT_P.index(weightp_arg)
        return 0

    @weightp.setter
    def weightp(self, weightp_index: int | None):
        if weightp_index and 0 < weightp_index < X264.WEIGHT_P_LENGTH:
            self._ffmpeg_advanced_args['weightp='] = self.WEIGHT_P[weightp_index]
        else:
            self._ffmpeg_advanced_args.pop('weightp=', 0)

    def get_ffmpeg_advanced_args(self) -> dict:
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
        return ''.join(['nal_hrd=', str(self.constant_bitrate).lower()])

    def _get_pass_args(self) -> str:
        return ''.join(['pass=',
                        str(self.encode_pass),
                        ':',
                        'stats=',
                        self.stats])

    def _generate_advanced_args(self) -> str:
        x264_advanced_args = ''

        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x264_advanced_args += ''.join([setting, arg, ':'])

        return x264_advanced_args
