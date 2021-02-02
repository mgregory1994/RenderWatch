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


class X264:
    profile_ffmpeg_args_list = ("auto", "baseline", "main", "high", "high10")
    preset_ffmpeg_args_list = ("auto", "ultrafast", "superfast", "veryfast", "faster", "fast", "slow", "slower",
                               "veryslow")
    tune_ffmpeg_args_list = ("auto", "film", "animation", "grain", "stillimage", "psnr", "ssim", "fastdecode",
                             "zerolatency")
    level_ffmpeg_args_list = ("auto", "1", "1.1", "1.2", "1.3", "2", "2.1", "2.2", "3", "3.1", "3.2", "4", "4.1", "4.2",
                              "5", "5.1")
    aq_mode_ffmpeg_args_list = ('auto', '0', '1', '2', '3')
    aq_mode_human_readable_list = ('auto', 'none', 'across frames', 'auto varaince', 'auto variance (dark)')
    b_adapt_ffmpeg_args_list = ('auto', '0', '1', '2')
    b_adapt_human_readable_list = ('auto', 'off', 'fast', 'optimal')
    b_pyramid_ffmpeg_args_list = ('auto', '1', '2')
    b_pyramid_human_readable_list = ('auto', 'strict', 'normal')
    weight_p_ffmpeg_args_list = ('auto', '0', '1', '2')
    weight_p_human_readable_list = ('auto', 'off', 'simple', 'smart')
    motion_estimation_ffmpeg_args_list = ('auto', 'dia', 'hex', 'umh', 'esa', 'tesa')
    sub_me_ffmpeg_args_list = ('auto', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')
    sub_me_human_readable_list = ('auto', '1:QPel SAD', '2:QPel SATD', '3:HPel on MB', '4:Always QPel',
                                  '5:Multi QPel', '6:RD I/P Frames', '7:RD All Frames',
                                  '8:RD Refine I/P Frames', '9:RD Refine Frames', '10:QP-RD')
    trellis_ffmpeg_args_list = ('auto', '0', '1', '2')
    trellis_human_readable_list = ('auto', 'off', 'encode only', 'always')
    direct_ffmpeg_args_list = ('auto', '0', '1', '2')
    direct_human_readable_list = ('auto', 'none', 'spatial', 'temporal')

    def __init__(self):
        self.ffmpeg_args = {
            "-c:v": "libx264",
            "-crf": "20",
            '-qp': None,
            "-b:v": None,
            "-profile:v": None,
            "-preset": None,
            "-level": None,
            "-tune": None
        }
        self.advanced_enabled = False
        self.__ffmpeg_advanced_args = {
            'keyint=': None,
            'min-keyint=': None,
            'scenecut=': None,
            'bframes=': None,
            'b-adapt=': None,
            'b-pyramid=': None,
            'no-cabac=': None,
            'ref=': None,
            'no-deblock=': None,
            'deblock=': None,
            'vbv-maxrate=': None,
            'vbv-bufsize=': None,
            'aq-mode=': None,
            'aq-strength=': None,
            'pass=': None,
            'stats=': None,
            'partitions=': None,
            'direct=': None,
            'weightb=': None,
            'weightp=': None,
            'me=': None,
            'merange=': None,
            'subme=': None,
            'psy-rd=': None,
            'mixed-refs=': None,
            '8x8dct=': None,
            'trellis=': None,
            'no-fast-pskip=': None,
            'no-dct-decimate=': None,
            'nal_hrd=': None
        }

    @property
    def codec_name(self):
        return self.ffmpeg_args['-c:v']

    @property
    def crf(self):
        try:
            crf = self.ffmpeg_args['-crf']
            crf_value = float(crf)
        except TypeError:
            return None
        else:
            return crf_value

    @crf.setter
    def crf(self, crf_value):
        try:
            if crf_value is None or crf_value < 0 or crf_value > 51:
                raise ValueError

            self.ffmpeg_args['-crf'] = str(crf_value)
        except (ValueError, TypeError):
            self.ffmpeg_args['-crf'] = None
        else:
            self.qp = None
            self.bitrate = None

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
            self.crf = None
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
            self.crf = None
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
    def tune(self):
        try:
            tune_value = self.ffmpeg_args['-tune']

            if tune_value is None:
                tune_index = 0
            else:
                tune_index = self.tune_ffmpeg_args_list.index(tune_value)
        except ValueError:
            return 0
        else:
            return tune_index

    @tune.setter
    def tune(self, tune_index):
        try:
            if tune_index is None or tune_index < 1:
                self.ffmpeg_args['-tune'] = None
            else:
                self.ffmpeg_args['-tune'] = self.tune_ffmpeg_args_list[tune_index]
        except IndexError:
            self.ffmpeg_args['-tune'] = None

    @property
    def keyint(self):
        try:
            keyint = self.__ffmpeg_advanced_args['keyint=']
            keyint_value = int(keyint)

            if keyint_value < 0 or keyint_value > 999:
                raise ValueError
        except (ValueError, TypeError):
            return 250
        else:
            return keyint_value

    @keyint.setter
    def keyint(self, keyint_value):
        try:
            if keyint_value is None or keyint_value < 0 or keyint_value > 999:
                raise ValueError

            self.__ffmpeg_advanced_args['keyint='] = str(keyint_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['keyint='] = None

    @property
    def min_keyint(self):
        try:
            min_keyint = self.__ffmpeg_advanced_args['min-keyint=']
            min_keyint_value = int(min_keyint)

            if min_keyint_value < 0 or min_keyint_value > 999:
                raise ValueError
        except (ValueError, TypeError):
            return 25
        else:
            return min_keyint_value

    @min_keyint.setter
    def min_keyint(self, min_keyint_value):
        try:
            if min_keyint_value is None or min_keyint_value < 0 or min_keyint_value > 999:
                raise ValueError

            self.__ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['min-keyint='] = None

    @property
    def scenecut(self):
        try:
            scenecut = self.__ffmpeg_advanced_args['scenecut=']
            scenecut_value = int(scenecut)

            if scenecut_value < 0:
                raise ValueError
        except (ValueError, TypeError):
            return None
        else:
            return scenecut_value

    @scenecut.setter
    def scenecut(self, scenecut_value):
        try:
            if scenecut_value is None or scenecut_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['scenecut='] = str(scenecut_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['scenecut='] = None

    @property
    def bframes(self):
        try:
            bframes = self.__ffmpeg_advanced_args['bframes=']
            bframes_value = int(bframes)

            if bframes_value < 0:
                raise ValueError
        except (ValueError, TypeError):
            return 3
        else:
            return bframes_value

    @bframes.setter
    def bframes(self, bframes_value):
        try:
            if bframes_value is None or bframes_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['bframes='] = str(bframes_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['bframes='] = None

    @property
    def b_adapt(self):
        try:
            b_adapt_value = self.__ffmpeg_advanced_args['b-adapt=']

            if b_adapt_value is None:
                b_adapt_index = 0
            else:
                b_adapt_index = self.b_adapt_ffmpeg_args_list.index(b_adapt_value)
        except ValueError:
            return 0
        else:
            return b_adapt_index

    @b_adapt.setter
    def b_adapt(self, b_adapt_index):
        try:
            if b_adapt_index is None or b_adapt_index < 1:
                self.__ffmpeg_advanced_args['b-adapt='] = None
            else:
                self.__ffmpeg_advanced_args['b-adapt='] = self.b_adapt_ffmpeg_args_list[b_adapt_index]
        except IndexError:
            self.__ffmpeg_advanced_args['b-adapt='] = None

    @property
    def b_pyramid(self):
        try:
            b_pyramid_value = self.__ffmpeg_advanced_args['b-pyramid=']

            if b_pyramid_value is None:
                b_pyramid_index = 0
            else:
                b_pyramid_index = self.b_pyramid_ffmpeg_args_list.index(b_pyramid_value)
        except ValueError:
            return 0
        else:
            return b_pyramid_index

    @b_pyramid.setter
    def b_pyramid(self, b_pyramid_index):
        try:
            if b_pyramid_index is None or b_pyramid_index < 1:
                self.__ffmpeg_advanced_args['b-pyramid='] = None
            else:
                self.__ffmpeg_advanced_args['b-pyramid='] = self.b_pyramid_ffmpeg_args_list[b_pyramid_index]
        except IndexError:
            self.__ffmpeg_advanced_args['b-pyramid='] = None

    @property
    def no_cabac(self):
        no_cabac_value = self.__ffmpeg_advanced_args['no-cabac=']

        if no_cabac_value is None or no_cabac_value != '1':
            return False

        return True

    @no_cabac.setter
    def no_cabac(self, no_cabac_enabled):
        if no_cabac_enabled is None or not no_cabac_enabled:
            self.__ffmpeg_advanced_args['no-cabac='] = None
        else:
            self.__ffmpeg_advanced_args['no-cabac='] = '1'

    @property
    def ref(self):
        try:
            ref = self.__ffmpeg_advanced_args['ref=']
            ref_value = int(ref)

            if ref_value < 0:
                raise ValueError
        except (ValueError, TypeError):
            return 3
        else:
            return ref_value

    @ref.setter
    def ref(self, ref_value):
        try:
            if ref_value is None or ref_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['ref='] = str(ref_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['ref='] = None

    @property
    def no_deblock(self):
        no_deblock_value = self.__ffmpeg_advanced_args['no-deblock=']

        if no_deblock_value is None or no_deblock_value != '1':
            return False

        return True

    @no_deblock.setter
    def no_deblock(self, no_deblock_enabled):
        if no_deblock_enabled is None or not no_deblock_enabled:
            self.__ffmpeg_advanced_args['no-deblock='] = None
        else:
            self.__ffmpeg_advanced_args['no-deblock='] = '1'

    @property
    def deblock(self):
        try:
            deblock = self.__ffmpeg_advanced_args['deblock=']
            deblock_split_values = deblock.split(',')
            deblock_values = int(deblock_split_values[0]), int(deblock_split_values[1])
        except:
            return 0, 0
        else:
            return deblock_values

    @deblock.setter
    def deblock(self, deblock_values):
        try:
            if deblock_values is None:
                self.__ffmpeg_advanced_args['deblock='] = None
            else:
                alpha_strength, beta_strength = deblock_values
                self.__ffmpeg_advanced_args['deblock='] = str(alpha_strength) + ',' + str(beta_strength)
        except TypeError:
            self.__ffmpeg_advanced_args['deblock='] = None

    @property
    def vbv_maxrate(self):
        try:
            vbv_maxrate = self.__ffmpeg_advanced_args['vbv-maxrate=']
            vbv_maxrate_value = int(vbv_maxrate)

            if vbv_maxrate_value < 0 or vbv_maxrate_value > 99999:
                raise ValueError
        except (ValueError, TypeError):
            return 2500
        else:
            return vbv_maxrate_value

    @vbv_maxrate.setter
    def vbv_maxrate(self, vbv_maxrate_value):
        try:
            if vbv_maxrate_value is None or vbv_maxrate_value < 0 or vbv_maxrate_value > 99999:
                raise ValueError

            self.__ffmpeg_advanced_args['vbv-maxrate='] = str(vbv_maxrate_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['vbv-maxrate='] = None

    @property
    def vbv_bufsize(self):
        try:
            vbv_bufsize = self.__ffmpeg_advanced_args['vbv-bufsize=']
            vbv_bufsize_value = int(vbv_bufsize)

            if vbv_bufsize_value < 0 or vbv_bufsize_value > 99999:
                raise ValueError
        except (ValueError, TypeError):
            return 2500
        else:
            return vbv_bufsize_value

    @vbv_bufsize.setter
    def vbv_bufsize(self, vbv_bufsize_value):
        try:
            if vbv_bufsize_value is None or vbv_bufsize_value < 0 or vbv_bufsize_value > 99999:
                raise ValueError

            self.__ffmpeg_advanced_args['vbv-bufsize='] = str(vbv_bufsize_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['vbv-bufsize='] = None

    @property
    def aq_mode(self):
        try:
            aq_mode_value = self.__ffmpeg_advanced_args['aq-mode=']

            if aq_mode_value is None:
                aq_mode_index = 0
            else:
                aq_mode_index = self.aq_mode_ffmpeg_args_list.index(aq_mode_value)
        except ValueError:
            return 0
        else:
            return aq_mode_index

    @aq_mode.setter
    def aq_mode(self, aq_mode_index):
        try:
            if aq_mode_index is None or aq_mode_index < 1:
                self.__ffmpeg_advanced_args['aq-mode='] = None
            else:
                self.__ffmpeg_advanced_args['aq-mode='] = self.aq_mode_ffmpeg_args_list[aq_mode_index]
        except IndexError:
            self.__ffmpeg_advanced_args['aq-mode='] = None

    @property
    def aq_strength(self):
        try:
            aq_strength = self.__ffmpeg_advanced_args['aq-strength=']
            aq_strength_value = float(aq_strength)

            if aq_strength_value < 0 or aq_strength_value > 2.0:
                raise ValueError
        except (ValueError, TypeError):
            return 1.0
        else:
            return aq_strength_value

    @aq_strength.setter
    def aq_strength(self, aq_strength_value):
        try:
            if aq_strength_value is None or aq_strength_value < 0 or aq_strength_value > 2.0:
                raise ValueError

            self.__ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['aq-strength='] = None

    @property
    def encode_pass(self):
        try:
            encode_pass = self.__ffmpeg_advanced_args['pass=']
            encode_pass_value = int(encode_pass)

            if encode_pass_value < 1 or encode_pass_value > 2:
                raise ValueError
        except (ValueError, TypeError):
            return None
        else:
            return encode_pass_value

    @encode_pass.setter
    def encode_pass(self, encode_pass_value):
        try:
            if encode_pass_value is None or encode_pass_value < 1 or encode_pass_value > 2:
                raise ValueError

            self.__ffmpeg_advanced_args['pass='] = str(encode_pass_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['pass='] = None

    @property
    def stats(self):
        return self.__ffmpeg_advanced_args['stats=']

    @stats.setter
    def stats(self, stats_file_path):
        self.__ffmpeg_advanced_args['stats='] = stats_file_path

    @property
    def partitions(self):
        try:
            partitions_value = self.__ffmpeg_advanced_args['partitions=']

            if partitions_value is None:
                return None

            if partitions_value == 'all' or partitions_value == 'none':
                return partitions_value

            return partitions_value.split(',')
        except:
            return None

    @partitions.setter
    def partitions(self, partitions_values):
        try:
            if partitions_values is None:
                self.__ffmpeg_advanced_args['partitions='] = None

                return
            elif partitions_values == 'all' or partitions_values == 'none':
                self.__ffmpeg_advanced_args['partitions='] = partitions_values

                return

            partition_arg = ''

            for index, partition_value in enumerate(partitions_values):
                partition_arg += partition_value

                if index != (len(partitions_values) - 1):
                    partition_arg += ','

            self.__ffmpeg_advanced_args['partitions='] = partition_arg
        except:
            self.__ffmpeg_advanced_args['partitions='] = None

    @property
    def direct(self):
        try:
            direct_value = self.__ffmpeg_advanced_args['direct=']

            if direct_value is None:
                direct_index = 0
            else:
                direct_index = self.direct_ffmpeg_args_list.index(direct_value)
        except ValueError:
            return 0
        else:
            return direct_index

    @direct.setter
    def direct(self, direct_index):
        try:
            if direct_index is None or direct_index < 1:
                self.__ffmpeg_advanced_args['direct='] = None
            else:
                self.__ffmpeg_advanced_args['direct='] = self.direct_ffmpeg_args_list[direct_index]
        except IndexError:
            self.__ffmpeg_advanced_args['direct='] = None

    @property
    def weightb(self):
        weightb_value = self.__ffmpeg_advanced_args['weightb=']

        if weightb_value is None or weightb_value != '1':
            return False

        return True

    @weightb.setter
    def weightb(self, weightb_enabled):
        if weightb_enabled is None or not weightb_enabled:
            self.__ffmpeg_advanced_args['weightb='] = None
        else:
            self.__ffmpeg_advanced_args['weightb='] = '1'

    @property
    def me(self):
        try:
            me_value = self.__ffmpeg_advanced_args['me=']

            if me_value is None:
                me_index = 0
            else:
                me_index = self.motion_estimation_ffmpeg_args_list.index(me_value)
        except ValueError:
            return 0
        else:
            return me_index

    @me.setter
    def me(self, me_index):
        try:
            if me_index is None or me_index < 1:
                self.__ffmpeg_advanced_args['me='] = None
            else:
                self.__ffmpeg_advanced_args['me='] = self.motion_estimation_ffmpeg_args_list[me_index]
        except IndexError:
            self.__ffmpeg_advanced_args['me='] = None

    @property
    def me_range(self):
        try:
            me_range = self.__ffmpeg_advanced_args['merange=']
            me_range_value = int(me_range)

            if me_range_value < 0:
                raise ValueError
        except (ValueError, TypeError):
            return 16
        else:
            return me_range_value

    @me_range.setter
    def me_range(self, me_range_value):
        try:
            if me_range_value is None or me_range_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['merange='] = str(me_range_value)
        except ValueError:
            self.__ffmpeg_advanced_args['merange='] = None

    @property
    def subme(self):
        try:
            subme_value = self.__ffmpeg_advanced_args['subme=']

            if subme_value is None:
                subme_index = 0
            else:
                subme_index = self.sub_me_ffmpeg_args_list.index(subme_value)
        except ValueError:
            return 0
        else:
            return subme_index

    @subme.setter
    def subme(self, subme_index):
        try:
            if subme_index is None or subme_index < 1:
                self.__ffmpeg_advanced_args['subme='] = None
            else:
                self.__ffmpeg_advanced_args['subme='] = self.sub_me_ffmpeg_args_list[subme_index]
        except IndexError:
            self.__ffmpeg_advanced_args['subme='] = None

    @property
    def psy_rd(self):
        try:
            psy_rd_setting = self.__ffmpeg_advanced_args['psy-rd=']
            psy_rd, psy_rd_trellis = psy_rd_setting.split(',')
            psy_rd_value = float(psy_rd)
            psy_rd_trellis_value = float(psy_rd_trellis)
        except:
            return 1.0, 0.0
        else:
            return psy_rd_value, psy_rd_trellis_value

    @psy_rd.setter
    def psy_rd(self, psy_rd_values):
        try:
            if psy_rd_values is None:
                raise ValueError

            psy_rd, psy_rd_trellis = psy_rd_values
            self.__ffmpeg_advanced_args['psy-rd='] = str(psy_rd) + ',' + str(psy_rd_trellis)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['psy-rd='] = None

    @property
    def mixed_refs(self):
        mixed_refs_value = self.__ffmpeg_advanced_args['mixed-refs=']

        if mixed_refs_value is None or mixed_refs_value != '1':
            return False

        return True

    @mixed_refs.setter
    def mixed_refs(self, mixed_refs_enabled):
        if mixed_refs_enabled is None or not mixed_refs_enabled:
            self.__ffmpeg_advanced_args['mixed-refs='] = None
        else:
            self.__ffmpeg_advanced_args['mixed-refs='] = '1'

    @property
    def dct8x8(self):
        dct_value = self.__ffmpeg_advanced_args['8x8dct=']

        if dct_value is None or dct_value != '1':
            return False

        return True

    @dct8x8.setter
    def dct8x8(self, dct8x8_enabled):
        if dct8x8_enabled is None or not dct8x8_enabled:
            self.__ffmpeg_advanced_args['8x8dct='] = None
        else:
            self.__ffmpeg_advanced_args['8x8dct='] = '1'

    @property
    def trellis(self):
        try:
            trellis_value = self.__ffmpeg_advanced_args['trellis=']

            if trellis_value is None:
                trellis_index = 0
            else:
                trellis_index = self.trellis_ffmpeg_args_list.index(trellis_value)
        except ValueError:
            return 0
        else:
            return trellis_index

    @trellis.setter
    def trellis(self, trellis_index):
        try:
            if trellis_index is None or trellis_index < 1:
                self.__ffmpeg_advanced_args['trellis='] = None
            else:
                self.__ffmpeg_advanced_args['trellis='] = self.trellis_ffmpeg_args_list[trellis_index]
        except IndexError:
            self.__ffmpeg_advanced_args['trellis='] = None

    @property
    def no_fast_pskip(self):
        no_fast_pskip_value = self.__ffmpeg_advanced_args['no-fast-pskip=']

        if no_fast_pskip_value is None or no_fast_pskip_value != '1':
            return False

        return True

    @no_fast_pskip.setter
    def no_fast_pskip(self, no_fast_pskip_enabled):
        if no_fast_pskip_enabled is None or not no_fast_pskip_enabled:
            self.__ffmpeg_advanced_args['no-fast-pskip='] = None
        else:
            self.__ffmpeg_advanced_args['no-fast-pskip='] = '1'

    @property
    def no_dct_decimate(self):
        no_dct_decimate_value = self.__ffmpeg_advanced_args['no-dct-decimate=']

        if no_dct_decimate_value is None or no_dct_decimate_value != '1':
            return False

        return True

    @no_dct_decimate.setter
    def no_dct_decimate(self, no_dct_decimate_enabled):
        if no_dct_decimate_enabled is None or not no_dct_decimate_enabled:
            self.__ffmpeg_advanced_args['no-dct-decimate='] = None
        else:
            self.__ffmpeg_advanced_args['no-dct-decimate='] = '1'

    @property
    def constant_bitrate(self):
        constant_bitrate_value = self.__ffmpeg_advanced_args['nal_hrd=']

        if constant_bitrate_value is None or constant_bitrate_value != 'cbr':
            return False

        return True

    @constant_bitrate.setter
    def constant_bitrate(self, constant_bitrate_enabled):
        if constant_bitrate_enabled is None or not constant_bitrate_enabled:
            self.__ffmpeg_advanced_args['nal_hrd='] = None
        else:
            self.__ffmpeg_advanced_args['nal_hrd='] = 'cbr'

    @property
    def weightp(self):
        try:
            weightp_value = self.__ffmpeg_advanced_args['weightp=']

            if weightp_value is None:
                weightp_index = 0
            else:
                weightp_index = self.weight_p_ffmpeg_args_list.index(weightp_value)
        except ValueError:
            return 0
        else:
            return weightp_index

    @weightp.setter
    def weightp(self, weightp_index):
        try:
            if weightp_index is None or weightp_index < 1:
                self.__ffmpeg_advanced_args['weightp='] = None
            else:
                self.__ffmpeg_advanced_args['weightp='] = self.weight_p_ffmpeg_args_list[weightp_index]
        except IndexError:
            self.__ffmpeg_advanced_args['weightp='] = None

    def get_ffmpeg_advanced_args(self):
        advanced_args = {'-x264-params': None}
        args = ''

        if not self.advanced_enabled:
            if self.__ffmpeg_advanced_args['nal_hrd='] is not None:
                args = self.__get_constant_bitrate_args()
            elif self.__ffmpeg_advanced_args['pass='] is not None:
                args = self.__get_pass_args()
        else:
            args = self.__generate_advanced_args()

        if args != '':
            advanced_args['-x264-params'] = args

        return advanced_args

    def __get_constant_bitrate_args(self):
        constant_bitrate_args = 'nal_hrd='
        constant_bitrate_args += self.__ffmpeg_advanced_args['nal_hrd=']

        return constant_bitrate_args

    def __get_pass_args(self):
        pass_args = 'pass='
        pass_args += self.__ffmpeg_advanced_args['pass=']
        pass_args += ':'
        pass_args += 'stats='
        pass_args += self.__ffmpeg_advanced_args['stats=']

        return pass_args

    def __generate_advanced_args(self):
        x264_advanced_args = ''

        for setting, value in self.__ffmpeg_advanced_args.items():
            if value is not None:
                x264_advanced_args += setting
                x264_advanced_args += value
                x264_advanced_args += ':'

        return x264_advanced_args
