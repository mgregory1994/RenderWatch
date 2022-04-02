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
    """Class that configures all X264 codec settings available for Render Watch."""

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
        """Initializes the X264 class with all necessary variables for the codec's options."""
        self.ffmpeg_args = {
            '-c:v': 'libx264',
            '-crf': '20.0'
        }
        self.is_advanced_enabled = False
        self._ffmpeg_advanced_args = {}

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
            crf_value: The value to use for the CRF setting.

        Returns:
            None
        """
        if crf_value is None:
            self.ffmpeg_args.pop('-crf', 0)
        else:
            self.ffmpeg_args['-crf'] = str(crf_value)
            self.qp = None
            self.bitrate = None

    @property
    def qp(self) -> float:
        """
        Returns the value of the QP setting.

        Returns:
            QP setting as a float.
        """
        if '-qp' in self.ffmpeg_args:
            return float(self.ffmpeg_args['-qp'])
        return 20.0

    @qp.setter
    def qp(self, qp_value: float | None):
        """
        Sets the QP setting to the specified value.

        Parameters:
            qp_value: The value to use for the QP setting.

        Returns:
            None
        """
        if qp_value is None:
            self.ffmpeg_args.pop('-qp', 0)
        else:
            self.ffmpeg_args['-qp'] = str(qp_value)
            self.crf = None
            self.bitrate = None

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
            bitrate_value: The value to use for the bitrate setting.

        Returns:
            None
        """
        if bitrate_value is None:
            self.ffmpeg_args.pop('-b:v', 0)
        else:
            self.ffmpeg_args['-b:v'] = str(bitrate_value) + 'k'
            self.crf = None
            self.qp = None

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
        if profile_index and 0 < profile_index < X264.PROFILE_LENGTH:
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
            preset_arg = self.ffmpeg_args['-preset']

            return self.PRESET.index(preset_arg)
        return 0

    @preset.setter
    def preset(self, preset_index: int | None):
        """
        Sets the profile setting to the specified index.

        Parameters:
            preset_index: Index from the PRESET variable.

        Returns:
            None
        """
        if preset_index and 0 < preset_index < X264.PRESET_LENGTH:
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
        if level_index and 0 < level_index < X264.LEVEL_LENGTH:
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
        if tune_index and 0 < tune_index < X264.TUNE_LENGTH:
            self.ffmpeg_args['-tune'] = self.TUNE[tune_index]
        else:
            self.ffmpeg_args.pop('-tune', 0)

    @property
    def keyint(self) -> int:
        """
        Returns the value of the keyframe interval setting.

        Returns:
            Keyframe Interval setting as an integer.
        """
        if 'keyint=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['keyint='])
        return 250

    @keyint.setter
    def keyint(self, keyint_value: int | None):
        """
        Sets the keyframe interval setting to the specified value.

        Parameters:
            keyint_value: The value to use for the keyframe interval setting.

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
        return 25

    @min_keyint.setter
    def min_keyint(self, min_keyint_value: int | None):
        """
        Sets the minimum keyframe interval setting to the specified value.

        Parameters:
            min_keyint_value: The value to use for the minimum keyframe interval setting.

        Returns:
            None
        """
        if min_keyint_value is None:
            self._ffmpeg_advanced_args.pop('min-keyint=', 0)
        else:
            self._ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)

    @property
    def scenecut(self) -> int:
        """
        Returns the value of the scenecut setting.

        Returns:
            Scenecut setting as an integer.
        """
        if 'scenecut=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['scenecut='])
        return 0

    @scenecut.setter
    def scenecut(self, scenecut_value: int | None):
        """
        Sets the scenecut setting to the specified value.

        Parameters:
            scenecut_value: The value to use for the scenecut setting.

        Returns:
            None
        """
        if scenecut_value is None:
            self._ffmpeg_advanced_args.pop('scenecut=', 0)
        else:
            self._ffmpeg_advanced_args['scenecut='] = str(scenecut_value)

    @property
    def bframes(self) -> int:
        """
        Returns the value of the B Frames setting.

        Returns:
            B Frames setting as an integer.
        """
        if 'bframes=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['bframes='])
        return 3

    @bframes.setter
    def bframes(self, bframes_value: int | None):
        """
        Sets the B Frames setting to the specified value.

        Parameters:
            bframes_value: The value to use for the B Frames setting.

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
        Returns the index of the B Adapt setting.

        Returns:
            B Adapt setting as an index using the B_ADAPT variable.
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
            b_adapt_index: Index from the B_ADAPT variable.

        Returns:
            None
        """
        if b_adapt_index and 0 < b_adapt_index < X264.B_ADAPT_LENGTH:
            self._ffmpeg_advanced_args['b-adapt='] = self.B_ADAPT[b_adapt_index]
        else:
            self._ffmpeg_advanced_args.pop('b-adapt=', 0)

    @property
    def b_pyramid(self) -> int:
        """
        Returns the index of the B Pyramid setting.

        Returns:
            B Pyramid setting as an index using the B_PYRAMID variable.
        """
        if 'b-pyramid=' in self._ffmpeg_advanced_args:
            b_pyramid_arg = self._ffmpeg_advanced_args['b-pyramid=']

            return self.B_PYRAMID.index(b_pyramid_arg)
        return 0

    @b_pyramid.setter
    def b_pyramid(self, b_pyramid_index: int | None):
        """
        Sets the B pyramid setting to the specified index.

        Parameters:
            b_pyramid_index: Index from the B_PYRAMID variable.

        Returns:
            None
        """
        if b_pyramid_index and 0 < b_pyramid_index < X264.B_PYRAMID_LENGTH:
            self._ffmpeg_advanced_args['b-pyramid='] = self.B_PYRAMID[b_pyramid_index]
        else:
            self._ffmpeg_advanced_args.pop('b-pyramid=', 0)

    @property
    def no_cabac(self) -> bool:
        """
        Returns whether the no CABAC setting is enabled.

        Returns:
            Boolean that represents whether the no CABAC setting is enabled.
        """
        if 'no-cabac=' in self._ffmpeg_advanced_args:
            no_cabac_arg = self._ffmpeg_advanced_args['no-cabac=']

            return no_cabac_arg == '1'
        return False

    @no_cabac.setter
    def no_cabac(self, is_no_cabac_enabled: bool):
        """
        Sets the no CABAC setting to the specified value.

        Parameters:
            is_no_cabac_enabled: Boolean that represents whether the no CABAC setting is enabled.

        Returns:
            None
        """
        if is_no_cabac_enabled:
            self._ffmpeg_advanced_args['no-cabac='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-cabac=', 0)

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
            ref_value: The value to use for the reference frames setting.

        Returns:
            None
        """
        if ref_value is None:
            self._ffmpeg_advanced_args.pop('ref=', 0)
        else:
            self._ffmpeg_advanced_args['ref='] = str(ref_value)

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
    def deblock(self) -> tuple:
        """
        Returns the values for the deblock setting.

        Returns:
            Tuple that represents the Alpha and Beta values for the deblock setting.
        """
        if 'deblock=' in self._ffmpeg_advanced_args:
            deblock_split_args = self._ffmpeg_advanced_args['deblock='].split(',')

            return int(deblock_split_args[0]), int(deblock_split_args[1])
        return 0, 0

    @deblock.setter
    def deblock(self, deblock_tuple: tuple | None):
        """
        Sets the deblock setting to the specified values.

        Parameters:
            deblock_tuple: Tuple that contains the alpha and beta values for the deblock setting.

        Returns:
            None
        """
        if deblock_tuple is None:
            self._ffmpeg_advanced_args.pop('deblock=', 0)
        else:
            alpha_strength, beta_strength = deblock_tuple
            self._ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)

    @property
    def vbv_maxrate(self) -> int:
        """
        Returns the value for the vbv maxrate setting.

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
        if vbv_maxrate_value is None:
            self._ffmpeg_advanced_args.pop('vbv-maxrate=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)

    @property
    def vbv_bufsize(self) -> int:
        """
        Returns the value for the vbv bufsize setting.

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
        if vbv_bufsize_value is None:
            self._ffmpeg_advanced_args.pop('vbv-bufsize=', 0)
        else:
            self._ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)

    @property
    def aq_mode(self) -> int:
        """
        Returns the index of the AQ mode setting.

        Returns:
            AQ mode setting as an index using the AQ_MODE variable.
        """
        if 'aq-mode=' in self._ffmpeg_advanced_args:
            aq_mode_value = self._ffmpeg_advanced_args['aq-mode=']

            return self.AQ_MODE.index(aq_mode_value)
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
        if aq_mode_index and 0 < aq_mode_index < X264.AQ_MODE_LENGTH:
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
            aq_strength_value: The value to use for the AQ strength setting.

        Returns:
            None
        """
        if aq_strength_value is None:
            self._ffmpeg_advanced_args.pop('aq-strength=', 0)
        else:
            self._ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)

    @property
    def encode_pass(self) -> int:
        """
        Returns the value of the encode pass setting.

        Returns:
            Encode pass as an integer.
        """
        if 'pass=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['pass='])
        return 0

    @encode_pass.setter
    def encode_pass(self, encode_pass_value: int | None):
        """
        Sets the encode pass setting to the specified value.

        Parameters:
            encode_pass_value: Current encode pass to use.

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
        Returns the value of the stats setting.

        Returns:
            Stats setting as a string that represents the file path to use for the stats file.
        """
        if 'stats=' in self._ffmpeg_advanced_args:
            return self._ffmpeg_advanced_args['stats=']
        return ''

    @stats.setter
    def stats(self, stats_file_path: str | None):
        """
        Sets the stats setting to the specified value.

        Parameters:
            stats_file_path: String that represents the file path to use for the stats file.

        Returns:
            None
        """
        if stats_file_path is None:
            self._ffmpeg_advanced_args.pop('stats=', 0)
        else:
            self._ffmpeg_advanced_args['stats='] = stats_file_path

    @property
    def partitions(self) -> tuple | str:
        """
        Returns the value(s) for the partitions setting.

        Returns:
            Tuple that contains strings that represent the partitions that are being used or a string that represents
            all or none.
        """
        if 'partitions=' in self._ffmpeg_advanced_args:
            partitions_arg = self._ffmpeg_advanced_args['partitions=']

            if partitions_arg == 'all' or partitions_arg == 'none':
                return partitions_arg
            return partitions_arg.split(',')
        return ()

    @partitions.setter
    def partitions(self, partitions_tuple: tuple | str | None):
        """
        Sets the partitions setting to the specified value(s).

        Parameters:
            partitions_tuple: Tuple that contains strings that represent the partitions that are being used or a
            string that represents all or none.

        Returns:
            None
        """
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
        Returns the index of the direct setting.

        Returns:
            Direct setting as an index using the DIRECT variable.
        """
        if 'direct=' in self._ffmpeg_advanced_args:
            direct_arg = self._ffmpeg_advanced_args['direct=']

            return self.DIRECT.index(direct_arg)
        return 0

    @direct.setter
    def direct(self, direct_index: int | None):
        """
        Sets the direct setting to the specified index.

        Parameters:
            direct_index: Index from the DIRECT variable.

        Returns:
            None
        """
        if direct_index and 0 < direct_index < X264.DIRECT_LENGTH:
            self._ffmpeg_advanced_args['direct='] = self.DIRECT[direct_index]
        else:
            self._ffmpeg_advanced_args.pop('direct=', 0)

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
    def me(self) -> int:
        """
        Returns the index of the motion estimation setting.

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
        if me_index and 0 < me_index < X264.ME_LENGTH:
            self._ffmpeg_advanced_args['me='] = self.ME[me_index]
        else:
            self._ffmpeg_advanced_args.pop('me=', 0)

    @property
    def me_range(self) -> int:
        """
        Returns the value of the motion estimation range setting.

        Returns:
            Motion estimation range setting as an integer.
        """
        if 'merange=' in self._ffmpeg_advanced_args:
            return int(self._ffmpeg_advanced_args['merange='])
        return 16

    @me_range.setter
    def me_range(self, me_range_value: int | None):
        """
        Sets the motion estimation range setting to the specified value.

        Parameters:
            me_range_value: The value to use for the motion estimation range setting.

        Returns:
            None
        """
        if me_range_value is None:
            self._ffmpeg_advanced_args.pop('merange=', 0)
        else:
            self._ffmpeg_advanced_args['merange='] = str(me_range_value)

    @property
    def subme(self) -> int:
        """
        Returns the index of the sub-motion estimation setting.

        Returns:
            Sub-motion estimation setting as an index using the SUB_ME variable.
        """
        if 'subme=' in self._ffmpeg_advanced_args:
            subme_arg = self._ffmpeg_advanced_args['subme=']

            return self.SUB_ME.index(subme_arg)
        return 0

    @subme.setter
    def subme(self, subme_index: int | None):
        """
        Sets the sub-motion estimation setting to the specified index.

        Parameters:
            Index from the SUB_ME variable.

        Returns:
            None
        """
        if subme_index and 0 < subme_index < X264.SUB_ME_LENGTH:
            self._ffmpeg_advanced_args['subme='] = self.SUB_ME[subme_index]
        else:
            self._ffmpeg_advanced_args.pop('subme=', 0)

    @property
    def psy_rd(self) -> tuple:
        """
        Returns the value of the PsyRD setting.

        Returns:
            PsyRD setting as a tuple that contains the PsyRD and PsyRD Trellis values respectively.
        """
        if 'psy-rd=' in self._ffmpeg_advanced_args:
            psy_rd_arg = self._ffmpeg_advanced_args['psy-rd=']
            psy_rd, psy_rd_trellis = psy_rd_arg.split(',')

            return float(psy_rd), float(psy_rd_trellis)
        return 1.0, 0.0

    @psy_rd.setter
    def psy_rd(self, psy_rd_tuple: tuple | None):
        """
        Sets the PsyRD setting to the specified values.

        Parameters:
            psy_rd_tuple: Tuple that contains the PsyRD and PsyRD Trellis values respectively.

        Returns:
            None
        """
        if psy_rd_tuple is None:
            self._ffmpeg_advanced_args.pop('psy-rd=', 0)
        else:
            psy_rd, psy_rd_trellis = psy_rd_tuple
            self._ffmpeg_advanced_args['psy-rd='] = str(psy_rd) + ',' + str(psy_rd_trellis)

    @property
    def mixed_refs(self) -> bool:
        """
        Returns whether the Mixed Reference Frames setting is enabled.

        Returns:
            Boolean that represents whether the Mixed Reference Frames setting is enabled.
        """
        if 'mixed-refs=' in self._ffmpeg_advanced_args:
            mixed_refs_arg = self._ffmpeg_advanced_args['mixed-refs=']

            return mixed_refs_arg == '1'
        return False

    @mixed_refs.setter
    def mixed_refs(self, is_mixed_refs_enabled: bool):
        """
        Sets the Mixed Reference Frames setting to the specified value.

        Parameters:
            is_mixed_refs_enabled: Boolean that represents whether the Mixed Reference Frames setting is enabled.

        Returns:
            None
        """
        if is_mixed_refs_enabled:
            self._ffmpeg_advanced_args['mixed-refs='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('mixed-refs=', 0)

    @property
    def dct8x8(self) -> bool:
        """
        Returns whether the dct8x8 setting is enabled.

        Returns:
            Boolean that represents whether the dct8x8 setting is enabled.
        """
        if '8x8dct=' in self._ffmpeg_advanced_args:
            dct_arg = self._ffmpeg_advanced_args['8x8dct=']

            return dct_arg == '1'
        return False

    @dct8x8.setter
    def dct8x8(self, is_dct8x8_enabled: bool):
        """
        Sets the dct8x8 setting to the specified value.

        Parameters:
            is_dct8x8_enabled: Boolean that represents whether the dct8x8 setting is enabled.

        Returns:
            None
        """
        if is_dct8x8_enabled:
            self._ffmpeg_advanced_args['8x8dct='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('8x8dct=', 0)

    @property
    def trellis(self) -> int:
        """
        Returns the index of the Trellis setting.

        Returns:
            Trellis setting as an index using the TRELLIS variable.
        """
        if 'trellis=' in self._ffmpeg_advanced_args:
            trellis_arg = self._ffmpeg_advanced_args['trellis=']

            return self.TRELLIS.index(trellis_arg)
        return 0

    @trellis.setter
    def trellis(self, trellis_index: int | None):
        """
        Sets the Trellis setting to the specified index.

        Parameters:
            trellis_index: Index from the TRELLIS variable.

        Returns:
            None
        """
        if trellis_index and 0 < trellis_index < X264.TRELLIST_LENGTH:
            self._ffmpeg_advanced_args['trellis='] = self.TRELLIS[trellis_index]
        else:
            self._ffmpeg_advanced_args.pop('trellis=', 0)

    @property
    def no_fast_pskip(self) -> bool:
        """
        Returns whether the No Fast P Skip setting is enabled.

        Returns:
            Boolean that represents whether the No Fast P Skip setting is enabled.
        """
        if 'no-fast-pskip=' in self._ffmpeg_advanced_args:
            no_fast_pskip_arg = self._ffmpeg_advanced_args['no-fast-pskip=']

            return no_fast_pskip_arg == '1'
        return False

    @no_fast_pskip.setter
    def no_fast_pskip(self, is_no_fast_pskip_enabled: bool):
        """
        Sets the No Fast P Skip setting to the specified value.

        Parameters:
            is_no_fast_pskip_enabled: Boolean that represents whether the No Fast P Skip setting is enabled.

        Returns:
            None
        """
        if is_no_fast_pskip_enabled:
            self._ffmpeg_advanced_args['no-fast-pskip='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-fast-pskip=', 0)

    @property
    def no_dct_decimate(self) -> bool:
        """
        Returns whether the No DCT Decimate setting is enabled.

        Returns:
            Boolean that represents whether the No DCT Decimate setting is enabled.
        """
        if 'no-dct-decimate=' in self._ffmpeg_advanced_args:
            no_dct_decimate_arg = self._ffmpeg_advanced_args['no-dct-decimate=']

            return no_dct_decimate_arg == '1'
        return False

    @no_dct_decimate.setter
    def no_dct_decimate(self, is_no_dct_decimate_enabled: bool):
        """
        Sets the No DCT Decimate setting to the specified value.

        Parameters:
            is_no_dct_decimate_enabled: Boolean that represents whether the No DCT Decimate setting is enabled.

        Returns:
            None
        """
        if is_no_dct_decimate_enabled:
            self._ffmpeg_advanced_args['no-dct-decimate='] = '1'
        else:
            self._ffmpeg_advanced_args.pop('no-dct-decimate=', 0)

    @property
    def constant_bitrate(self) -> bool:
        """
        Returns whether the Constant Bitrate setting is enabled.

        Returns:
            Boolean that represents whether the Constant Bitrate setting is enabled.
        """
        if 'nal_hrd=' in self._ffmpeg_advanced_args:
            constant_bitrate_arg = self._ffmpeg_advanced_args['nal_hrd=']

            return constant_bitrate_arg == 'cbr'
        return False

    @constant_bitrate.setter
    def constant_bitrate(self, is_constant_bitrate_enabled: bool):
        """
        Sets the Constant Bitrate setting to the specified value.

        Parameters:
            is_constant_bitrate_enabled: Boolean that represents whether the Constant Bitrate setting is enabled.

        Returns:
            None
        """
        if is_constant_bitrate_enabled:
            self._ffmpeg_advanced_args['nal_hrd='] = 'cbr'
        else:
            self._ffmpeg_advanced_args.pop('nal_hrd=', 0)

    @property
    def weightp(self) -> int:
        """
        Returns the index of the Weight P setting.

        Returns:
            Weight P setting as an index using the WEIGHT_P variable.
        """
        if 'weightp=' in self._ffmpeg_advanced_args:
            weightp_arg = self._ffmpeg_advanced_args['weightp=']

            return self.WEIGHT_P.index(weightp_arg)
        return 0

    @weightp.setter
    def weightp(self, weightp_index: int | None):
        """
        Sets the Weight P setting to the specified index.

        Parameters:
            weightp_index: Index from the WEIGHT_P variable.

        Returns:
            None
        """
        if weightp_index and 0 < weightp_index < X264.WEIGHT_P_LENGTH:
            self._ffmpeg_advanced_args['weightp='] = self.WEIGHT_P[weightp_index]
        else:
            self._ffmpeg_advanced_args.pop('weightp=', 0)

    def get_ffmpeg_advanced_args(self) -> dict:
        """
        Returns the ffmpeg arguments for the x264 codec's settings.

        Returns:
            Dictionary that contains the arguments and their settings for the x264 codec.
        """
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
        # Returns the Constant Bitrate setting as a string that represents ffmpeg arguments.
        return ''.join(['nal_hrd=', str(self.constant_bitrate).lower()])

    def _get_pass_args(self) -> str:
        # Returns the Encode Pass and Stats settings as a string that represents ffmpeg arguments.
        return ''.join(['pass=',
                        str(self.encode_pass),
                        ':',
                        'stats=',
                        self.stats])

    def _generate_advanced_args(self) -> str:
        # Returns the advanced settings for the x264 codec as a string that represents ffmpeg arguments.
        x264_advanced_args = ''

        for setting, arg in self._ffmpeg_advanced_args.items():
            if arg is not None:
                x264_advanced_args += ''.join([setting, arg, ':'])

        return x264_advanced_args
