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


class X264:
    """Manages all settings for the x264 codec."""

    PROFILE_ARGS_LIST = ('auto', 'baseline', 'main', 'high', 'high10')
    PROFILE_LIST_LENGTH = len(PROFILE_ARGS_LIST)
    PRESET_ARGS_LIST = ('auto', 'ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'slow', 'slower', 'veryslow')
    PRESET_LIST_LENGTH = len(PRESET_ARGS_LIST)
    TUNE_ARGS_LIST = ('auto', 'film', 'animation', 'grain', 'stillimage', 'psnr', 'ssim', 'fastdecode', 'zerolatency')
    TUNE_LIST_LENGTH = len(TUNE_ARGS_LIST)
    LEVEL_ARGS_LIST = (
        'auto', '1', '1.1', '1.2', '1.3', '2', '2.1', '2.2',
        '3', '3.1', '3.2', '4', '4.1', '4.2', '5', '5.1'
    )
    LEVEL_LIST_LENGTH = len(LEVEL_ARGS_LIST)
    AQ_MODE_ARGS_LIST = ('auto', '0', '1', '2', '3')
    AQ_MODE_UI_LIST = ('auto', 'none', 'across frames', 'auto varaince', 'auto variance (dark)')
    AQ_MODE_LIST_LENGTH = len(AQ_MODE_ARGS_LIST)
    B_ADAPT_ARGS_LIST = ('auto', '0', '1', '2')
    B_ADAPT_UI_LIST = ('auto', 'off', 'fast', 'optimal')
    B_ADAPT_LIST_LENGTH = len(B_ADAPT_ARGS_LIST)
    B_PYRAMID_ARGS_LIST = ('auto', '1', '2')
    B_PYRAMID_UI_LIST = ('auto', 'strict', 'normal')
    B_PYRAMID_LIST_LENGTH = len(B_PYRAMID_ARGS_LIST)
    WEIGHT_P_ARGS_LIST = ('auto', '0', '1', '2')
    WEIGHT_P_UI_LIST = ('auto', 'off', 'simple', 'smart')
    WEIGHT_P_LIST_LENGTH = len(WEIGHT_P_ARGS_LIST)
    ME_ARGS_LIST = ('auto', 'dia', 'hex', 'umh', 'esa', 'tesa')
    ME_LIST_LENGTH = len(ME_ARGS_LIST)
    SUB_ME_ARGS_LIST = ('auto', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
    SUB_ME_UI_LIST = (
        'auto', '1:QPel SAD', '2:QPel SATD', '3:HPel on MB', '4:Always QPel',
        '5:Multi QPel', '6:RD I/P Frames', '7:RD All Frames', '8:RD Refine I/P Frames',
        '9:RD Refine Frames', '10:QP-RD'
    )
    SUB_ME_LIST_LENGTH = len(SUB_ME_ARGS_LIST)
    TRELLIS_ARGS_LIST = ('auto', '0', '1', '2')
    TRELLIS_UI_LIST = ('auto', 'off', 'encode only', 'always')
    TRELLIST_LIST_LENGTH = len(TRELLIS_ARGS_LIST)
    DIRECT_ARGS_LIST = ('auto', '0', '1', '2')
    DIRECT_UI_LIST = ('auto', 'none', 'spatial', 'temporal')
    DIRECT_LIST_LENGTH = len(DIRECT_ARGS_LIST)

    def __init__(self):
        self.ffmpeg_args = {
            '-c:v': 'libx264',
            '-crf': '20.0'
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
        if crf_value is None or not 0 <= crf_value <= 51:
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
        if qp_value is None or not 0 <= qp_value <= 51:
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
        if bitrate_value is None or not 0 < bitrate_value <= 99999:
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
        if profile_index is None or not 0 < profile_index < X264.PROFILE_LIST_LENGTH:
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
        if preset_index is None or not 0 < preset_index < X264.PRESET_LIST_LENGTH:
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
        if level_index is None or not 0 < level_index < X264.LEVEL_LIST_LENGTH:
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
        if tune_index is None or not 0 < tune_index < X264.TUNE_LIST_LENGTH:
            self.ffmpeg_args.pop('-tune', 0)
        else:
            self.ffmpeg_args['-tune'] = self.TUNE_ARGS_LIST[tune_index]

    @property
    def keyint(self):
        """Returns keyint argument as an int."""
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value):
        """Stores keyint value as a string argument."""
        if keyint_value is None or not 0 <= keyint_value <= 999:
            self._ffmpeg_advanced_args.pop('keyint=', 0)
        else:
            self._ffmpeg_advanced_args['keyint='] = str(keyint_value)

    @property
    def min_keyint(self):
        """Returns min keyint argument as an int."""
        if 'min-keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['min-keyint='])
        return 25

    @min_keyint.setter
    def min_keyint(self, min_keyint_value):
        """Stores min keyint value as a string argument."""
        if min_keyint_value is None or not 0 <= min_keyint_value <= 999:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def scenecut(self):
        """Returns scenecut argument as an int."""
        if 'scenecut=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['scenecut='])
        return None

    @scenecut.setter
    def scenecut(self, scenecut_value):
        """Stores scenecut value as a string argument."""
        if scenecut_value is None or scenecut_value < 0:
            self._ffmpeg_advanced_args.pop('scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['scenecut='] = str(scenecut_value)

    @property
    def bframes(self):
        """Returns bframes argument as an int."""
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 3

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
        if b_adapt_index is None or not 0 < b_adapt_index < X264.B_ADAPT_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)
        else:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT_ARGS_LIST[b_adapt_index]

    @property
    def b_pyramid(self):
        """Returns b pyramid argument as an index."""
        if 'b-pyramid=' in self._ffmpeg_advanced_args:
            b_pyramid_arg = self._ffmpeg_advanced_args['b-pyramid=']
            return self.B_PYRAMID_ARGS_LIST.index(b_pyramid_arg)
        return 0

    @b_pyramid.setter
    def b_pyramid(self, b_pyramid_index):
        """Stores index as a b pyramid argument."""
        if b_pyramid_index is None or not 0 < b_pyramid_index < X264.B_PYRAMID_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('b-pyramid=', 0)
        else:
            self._ffmpeg_advanced_args['b-pyramid='] = self.B_PYRAMID_ARGS_LIST[b_pyramid_index]

    @property
    def no_cabac(self):
        """Returns no cabac argument as a boolean."""
        if 'no-cabac=' in self._ffmpeg_advanced_args:
            no_cabac_arg = self._ffmpeg_advanced_args['no-cabac=']
            return no_cabac_arg == '1'
        return False

    @no_cabac.setter
    def no_cabac(self, no_cabac_enabled):
        """Stores no cabac boolean as a string argument."""
        if no_cabac_enabled is None or not no_cabac_enabled:
            self._ffmpeg_advanced_args.pop('no-cabac=', 0)
        else:
            self._ffmpeg_advanced_args['no-cabac='] = '1'

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
    def deblock(self):
        """Returns deblock argument as tuple of ints."""
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
    def vbv_maxrate(self):
        """Returns vbv maxrate argument as an int."""
        if 'vbv-maxrate=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['vbv-maxrate='])
        return 2500

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value):
        """Stores vbv maxrate value as a string argument."""
        if vbv_maxrate_value is None or not 0 <= vbv_maxrate_value <= 99999:
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
        if vbv_bufsize_value is None or not 0 <= vbv_bufsize_value <= 99999:
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    @property
    def aq_mode(self):
        """Returns aq mode argument as an index."""
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_value = self._ffmpeg_advanced_args['aq-mode=']
            return self.AQ_MODE_ARGS_LIST.index(aq_mode_value)
        return 0

    @aq_mode.setter
    def aq_mode(self, aq_mode_index):
        """Stores index as an aq mode argument."""
        if aq_mode_index is None or not 0 < aq_mode_index < X264.AQ_MODE_LIST_LENGTH:
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
        if aq_strength_value is None or not 0 <= aq_strength_value <= 2.0:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)

    @property
    def encode_pass(self):
        """Returns encode pass argument as an int."""
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return None

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        """Stores encode pass value as a string argument."""
        if encode_pass_value is None or not 1 <= encode_pass_value <= 2:
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
    def stats(self, stats_file_path):
        """Stores stats file path as a string argument."""
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    @property
    def partitions(self):
        """Returns partitions argument as a string or tuple of strings."""
        if 'partitions=' in self._ffmpeg_advanced_args:
            partitions_arg = self._ffmpeg_advanced_args['partitions=']
            if partitions_arg == 'all' or partitions_arg == 'none':
                return partitions_arg
            return partitions_arg.split(',')
        return None

    @partitions.setter
    def partitions(self, partitions_values):
        """Stores partitions values as a string argument."""
        if partitions_values is None:
            self._ffmpeg_advanced_args.pop('partitions=', 0)
        elif partitions_values == 'all' or partitions_values == 'none':
            self._ffmpeg_advanced_args['partitions='] = partitions_values
        else:
            partition_arg = ''
            for index, partition_value in enumerate(partitions_values):
                partition_arg += partition_value
                if index != (len(partitions_values) - 1):
                    partition_arg += ','

            self._ffmpeg_advanced_args['partitions='] = partition_arg

    @property
    def direct(self):
        """Returns direct argument as an index."""
        if 'direct=' in self._ffmpeg_advanced_args:
            direct_arg = self._ffmpeg_advanced_args['direct=']
            return self.DIRECT_ARGS_LIST.index(direct_arg)
        return 0

    @direct.setter
    def direct(self, direct_index):
        """Stores index as a string argument."""
        if direct_index is None or not 0 < direct_index < X264.DIRECT_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('direct=', 0)
        else:
            self._ffmpeg_advanced_args['direct='] = self.DIRECT_ARGS_LIST[direct_index]

    @property
    def weightb(self):
        """Returns weight b argument as a boolean."""
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
    def me(self):
        """Returns me argument as an index."""
        if 'me=' in self._ffmpeg_advanced_args:
            me_arg = self._ffmpeg_advanced_args['me=']
            return self.ME_ARGS_LIST.index(me_arg)
        return 0

    @me.setter
    def me(self, me_index):
        """Stores index as a me argument."""
        if me_index is None or not 0 < me_index < X264.ME_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('me=', 0)
        else:
            self._ffmpeg_advanced_args['me='] = self.ME_ARGS_LIST[me_index]

    @property
    def me_range(self):
        """Returns me range argument as an int."""
        if 'merange=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['merange='])
        return 16

    @me_range.setter
    def me_range(self, me_range_value):
        """Stores me range value as a string argument."""
        if me_range_value is None or me_range_value < 0:
            self._ffmpeg_advanced_args.pop('merange=', 0)
        else:
            self._ffmpeg_advanced_args['merange='] = str(me_range_value)

    @property
    def subme(self):
        """Returns subme argument as an index."""
        if 'subme=' in self._ffmpeg_advanced_args:
            subme_arg = self._ffmpeg_advanced_args['subme=']
            return self.SUB_ME_ARGS_LIST.index(subme_arg)
        return 0

    @subme.setter
    def subme(self, subme_index):
        """Stores index as a subme argument."""
        if subme_index is None or not 0 < subme_index < X264.SUB_ME_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('subme=', 0)
        else:
            self._ffmpeg_advanced_args['subme='] = self.SUB_ME_ARGS_LIST[subme_index]

    @property
    def psy_rd(self):
        """Returns psy rd argument as a tuple of floats."""
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            psy_rd_arg = self._ffmpeg_advanced_args['psy-rd=']
            psy_rd, psy_rd_trellis = psy_rd_arg.split(',')
            return float(psy_rd), float(psy_rd_trellis)
        return 1.0, 0.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_values):
        """Stores psy rd tuple values as a string argument."""
        if psy_rd_values is None:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            psy_rd, psy_rd_trellis = psy_rd_values
            if min(psy_rd, psy_rd_trellis, 0.0) != 0.0:
                self._ffmpeg_advanced_args.pop('psy-rd=', 0)
            else:
                self._ffmpeg_advanced_args['psy-rd='] = str(psy_rd) + ',' + str(psy_rd_trellis)

    @property
    def mixed_refs(self):
        """Returns mixed refs argument as a boolean."""
        if 'mixed-refs=' in self._ffmpeg_advanced_args:
            mixed_refs_arg = self._ffmpeg_advanced_args['mixed-refs=']
            return mixed_refs_arg == '1'
        return False

    @mixed_refs.setter
    def mixed_refs(self, mixed_refs_enabled):
        """Stores mixed refs boolean as a string argument."""
        if mixed_refs_enabled is None or not mixed_refs_enabled:
            self._ffmpeg_advanced_args.pop('mixed-refs=', 0)
        else:
            self._ffmpeg_advanced_args['mixed-refs='] = '1'

    @property
    def dct8x8(self):
        """Returns 8x8dct argument as a boolean."""
        if '8x8dct=' in self._ffmpeg_advanced_args:
            dct_arg = self._ffmpeg_advanced_args['8x8dct=']
            return dct_arg == '1'
        return False

    @dct8x8.setter
    def dct8x8(self, dct8x8_enabled):
        """Stores 8x8dct boolean as a string argument."""
        if dct8x8_enabled is None or not dct8x8_enabled:
            self._ffmpeg_advanced_args.pop('8x8dct=', 0)
        else:
            self._ffmpeg_advanced_args['8x8dct='] = '1'

    @property
    def trellis(self):
        """Returns trellis argument as an index."""
        if 'trellis=' in self._ffmpeg_advanced_args:
            trellis_arg = self._ffmpeg_advanced_args['trellis=']
            return self.TRELLIS_ARGS_LIST.index(trellis_arg)
        return 0

    @trellis.setter
    def trellis(self, trellis_index):
        if trellis_index is None or not 0 < trellis_index < X264.TRELLIST_LIST_LENGTH:
            """Stores index as a trellis argument."""
            self._ffmpeg_advanced_args.pop('trellis=', 0)
        else:
            self._ffmpeg_advanced_args['trellis='] = self.TRELLIS_ARGS_LIST[trellis_index]

    @property
    def no_fast_pskip(self):
        """Returns no fast pskip argument as a boolean."""
        if 'no-fast-pskip=' in self._ffmpeg_advanced_args:
            no_fast_pskip_arg = self._ffmpeg_advanced_args['no-fast-pskip=']
            return no_fast_pskip_arg == '1'
        return False

    @no_fast_pskip.setter
    def no_fast_pskip(self, no_fast_pskip_enabled):
        """Stores no fast pskip boolean as a string argument."""
        if no_fast_pskip_enabled is None or not no_fast_pskip_enabled:
            self._ffmpeg_advanced_args.pop('no-fast-pskip=', 0)
        else:
            self._ffmpeg_advanced_args['no-fast-pskip='] = '1'

    @property
    def no_dct_decimate(self):
        """Returns no dct decimate argument as a boolean."""
        if 'no-dct-decimate=' in self._ffmpeg_advanced_args:
            no_dct_decimate_arg = self._ffmpeg_advanced_args['no-dct-decimate=']
            return no_dct_decimate_arg == '1'
        return False

    @no_dct_decimate.setter
    def no_dct_decimate(self, no_dct_decimate_enabled):
        """Stores no dct decimate boolean as a string argument."""
        if no_dct_decimate_enabled is None or not no_dct_decimate_enabled:
            self._ffmpeg_advanced_args.pop('no-dct-decimate=', 0)
        else:
            self._ffmpeg_advanced_args['no-dct-decimate='] = '1'

    @property
    def constant_bitrate(self):
        """Returns constant bitrate argument as a boolean."""
        if 'nal_hrd=' in self._ffmpeg_advanced_args:
            constant_bitrate_arg = self._ffmpeg_advanced_args['nal_hrd=']
            return constant_bitrate_arg == 'cbr'
        return False

    @constant_bitrate.setter
    def constant_bitrate(self, constant_bitrate_enabled):
        """Stores constant bitrate boolean as a string argument."""
        if constant_bitrate_enabled is None or not constant_bitrate_enabled:
            self._ffmpeg_advanced_args.pop('nal_hrd=', 0)
        else:
            self._ffmpeg_advanced_args['nal_hrd='] = 'cbr'

    @property
    def weightp(self):
        """Returns weightp argument as an index."""
        if 'weightp=' in self._ffmpeg_advanced_args:
            weightp_arg = self._ffmpeg_advanced_args['weightp=']
            return self.WEIGHT_P_ARGS_LIST.index(weightp_arg)
        return 0

    @weightp.setter
    def weightp(self, weightp_index):
        """Stores index as a weightp argument."""
        if weightp_index is None or not 0 < weightp_index < X264.WEIGHT_P_LIST_LENGTH:
            self._ffmpeg_advanced_args.pop('weightp=', 0)
        else:
            self._ffmpeg_advanced_args['weightp='] = self.WEIGHT_P_ARGS_LIST[weightp_index]

    def get_ffmpeg_advanced_args(self):
        """Returns dictionary with advanced args string."""
        advanced_args = {'-x264-params': None}

        args = ''
        if self.advanced_enabled:
            args = self._generate_advanced_args()
        else:
            if 'nal_hrd=' in self._ffmpeg_advanced_args:
                args = self._get_constant_bitrate_args()
            elif 'pass=' in self._ffmpeg_advanced_args:
                args = self._get_pass_args()
        if args:
            advanced_args['-x264-params'] = args
        return advanced_args

    def _get_constant_bitrate_args(self):
        """Returns string for constant bitrate argument."""
        constant_bitrate_args = 'nal_hrd='
        constant_bitrate_args += str(self.constant_bitrate).lower()
        return constant_bitrate_args

    def _get_pass_args(self):
        """Returns string for encode pass arguments."""
        pass_args = 'pass='
        pass_args += str(self.encode_pass)
        pass_args += ':'
        pass_args += 'stats='
        pass_args += self.stats
        return pass_args

    def _generate_advanced_args(self):
        """Returns string for all advanced settings."""
        x264_advanced_args = ''
        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x264_advanced_args += setting
                x264_advanced_args += arg
                x264_advanced_args += ':'
        return x264_advanced_args
