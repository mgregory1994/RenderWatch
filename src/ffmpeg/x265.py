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


class X265:
    profile_ffmpeg_args_list = ("auto", "main", "main10", "main12")
    preset_ffmpeg_args_list = ("auto", "ultrafast", "superfast", "veryfast", "faster", "fast", "slow", "slower", "veryslow")
    level_ffmpeg_args_list = ("auto", "1", "2", "2.1", "3", "3.1", "4", "4.1", "5", "5.1", "5.2", "6", "6.1", "6.2", "8.5")
    tune_ffmpeg_args_list = ("auto", "grain", "animation", "zerolatency", "fastdecode", "psnr", "ssim")
    aq_mode_ffmpeg_args_list = ("auto", "0", "1", "2", "3", "4")
    aq_mode_human_readable_list = ('auto', 'disabled', 'enabled', 'auto variance', 'auto variance(dark)',
                                   'auto variance(dark + edge)')
    b_adapt_ffmpeg_args_list = ('auto', '0', '1', '2')
    b_adapt_human_readable_list = ('auto', 'none', 'fast', 'full(trellis)')
    me_ffmpeg_args_list = ('auto', 'dia', 'hex', 'umh', 'star', 'sea', 'full')
    rdoq_level_ffmpeg_args_list = ('auto', '0', '1', '2')
    rdoq_level_human_readable_list = ('auto', 'none', 'optimal rounding', 'decimate decisions')
    max_cu_size_ffmpeg_args_list = ('auto', '64', '32', '16')
    min_cu_size_ffmpeg_args_list = ('auto', '8', '16', '32')

    def __init__(self):
        self.ffmpeg_args = {
            "-c:v": "libx265",
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
            'vbv-maxrate=': None,
            'vbv-bufsize=': None,
            'aq-mode=': None,
            'aq-strength=': None,
            'hevc-aq=': None,
            'keyint=': None,
            'min-keyint=': None,
            'ref=': None,
            'bframes=': None,
            'b-adapt=': None,
            'no-b-pyramid=': None,
            'b-intra=': None,
            'no-open-gop=': None,
            'rc-lookahead=': None,
            'no-scenecut=': None,
            'no-high-tier=': None,
            'psy-rd=': None,
            'psy-rdoq=': None,
            'me=': None,
            'subme=': None,
            'weightb=': None,
            'no-weightp=': None,
            'deblock=': None,
            'no-deblock=': None,
            'no-sao=': None,
            'sao-non-deblock=': None,
            'limit-sao=': None,
            'selective-sao=': None,
            'rd=': None,
            'rdoq-level=': None,
            'rd-refine=': None,
            'ctu=': None,
            'min-cu-size=': None,
            'rect=': None,
            'amp=': None,
            'wpp=': None,
            'pmode=': None,
            'pme=': None,
            'uhd-bd=': None,
            'pass=': None,
            'stats=': None
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
    def vbv_maxrate(self):
        try:
            vbv_maxrate = self.__ffmpeg_advanced_args['vbv-maxrate=']
            vbv_maxrate_value = int(vbv_maxrate)
        except TypeError:
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
        except TypeError:
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
            if aq_mode_index is None or aq_mode_index == 0:
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
        except TypeError:
            return 1.0
        else:
            return aq_strength_value

    @aq_strength.setter
    def aq_strength(self, aq_strength_value):
        try:
            if aq_strength_value is None or aq_strength_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['aq-strength='] = str(aq_strength_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['aq-strength='] = None

    @property
    def hevc_aq(self):
        hevc_aq_value = self.__ffmpeg_advanced_args['hevc-aq=']

        if hevc_aq_value is None or hevc_aq_value != '1':
            return False

        return True

    @hevc_aq.setter
    def hevc_aq(self, hevc_aq_enabled):
        if hevc_aq_enabled is None or not hevc_aq_enabled:
            self.__ffmpeg_advanced_args['hevc-aq='] = None
        else:
            self.__ffmpeg_advanced_args['hevc-aq='] = '1'

    @property
    def keyint(self):
        try:
            keyint = self.__ffmpeg_advanced_args['keyint=']
            keyint_value = int(keyint)
        except TypeError:
            return 250
        else:
            return keyint_value

    @keyint.setter
    def keyint(self, keyint_value):
        try:
            if keyint_value is None or keyint_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['keyint='] = str(keyint_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['keyint='] = None

    @property
    def min_keyint(self):
        try:
            min_keyint = self.__ffmpeg_advanced_args['min-keyint=']
            min_keyint_value = int(min_keyint)
        except TypeError:
            return 0
        else:
            return min_keyint_value

    @min_keyint.setter
    def min_keyint(self, min_keyint_value):
        try:
            if min_keyint_value is None or min_keyint_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['min-keyint='] = str(min_keyint_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['min-keyint='] = None

    @property
    def ref(self):
        try:
            ref = self.__ffmpeg_advanced_args['ref=']
            ref_value = int(ref)
        except TypeError:
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
    def bframes(self):
        try:
            bframes = self.__ffmpeg_advanced_args['bframes=']
            bframes_value = int(bframes)
        except TypeError:
            return 4
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
    def no_b_pyramid(self):
        no_b_pyramid_value = self.__ffmpeg_advanced_args['no-b-pyramid=']

        if no_b_pyramid_value is None or no_b_pyramid_value != '1':
            return False

        return True

    @no_b_pyramid.setter
    def no_b_pyramid(self, no_b_pyramid_enabled):
        if no_b_pyramid_enabled is None or not no_b_pyramid_enabled:
            self.__ffmpeg_advanced_args['no-b-pyramid='] = None
        else:
            self.__ffmpeg_advanced_args['no-b-pyramid='] = '1'

    @property
    def b_intra(self):
        b_intra_value = self.__ffmpeg_advanced_args['b-intra=']

        if b_intra_value is None or b_intra_value != '1':
            return False

        return True

    @b_intra.setter
    def b_intra(self, b_intra_enabled):
        if b_intra_enabled is None or not b_intra_enabled:
            self.__ffmpeg_advanced_args['b-intra='] = None
        else:
            self.__ffmpeg_advanced_args['b-intra='] = '1'

    @property
    def no_open_gop(self):
        no_open_gop_value = self.__ffmpeg_advanced_args['no-open-gop=']

        if no_open_gop_value is None or no_open_gop_value != '1':
            return False

        return True

    @no_open_gop.setter
    def no_open_gop(self, no_open_gop_enabled):
        if no_open_gop_enabled is None or not no_open_gop_enabled:
            self.__ffmpeg_advanced_args['no-open-gop='] = None
        else:
            self.__ffmpeg_advanced_args['no-open-gop='] = '1'

    @property
    def rc_lookahead(self):
        try:
            rc_lookahead = self.__ffmpeg_advanced_args['rc-lookahead=']
            rc_lookahead_value = int(rc_lookahead)
        except TypeError:
            return 20
        else:
            return rc_lookahead_value

    @rc_lookahead.setter
    def rc_lookahead(self, rc_lookahead_value):
        try:
            if rc_lookahead_value is None or rc_lookahead_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['rc-lookahead='] = str(rc_lookahead_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['rc-lookahead='] = None

    @property
    def no_scenecut(self):
        no_scenecut_value = self.__ffmpeg_advanced_args['no-scenecut=']

        if no_scenecut_value is None or no_scenecut_value != '1':
            return False

        return True

    @no_scenecut.setter
    def no_scenecut(self, no_scenecut_enabled):
        if no_scenecut_enabled is None or not no_scenecut_enabled:
            self.__ffmpeg_advanced_args['no-scenecut='] = None
        else:
            self.__ffmpeg_advanced_args['no-scenecut='] = '1'

    @property
    def no_high_tier(self):
        no_high_tier_value = self.__ffmpeg_advanced_args['no-high-tier=']

        if no_high_tier_value is None or no_high_tier_value != '1':
            return False

        return True

    @no_high_tier.setter
    def no_high_tier(self, no_high_tier_enabled):
        if no_high_tier_enabled is None or not no_high_tier_enabled:
            self.__ffmpeg_advanced_args['no-high-tier='] = None
        else:
            self.__ffmpeg_advanced_args['no-high-tier='] = '1'

    @property
    def psy_rd(self):
        try:
            psy_rd = self.__ffmpeg_advanced_args['psy-rd=']
            psy_rd_value = float(psy_rd)
        except TypeError:
            return 2.0
        else:
            return psy_rd_value

    @psy_rd.setter
    def psy_rd(self, psy_rd_value):
        try:
            if psy_rd_value is None or psy_rd_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['psy-rd='] = str(psy_rd_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['psy-rd='] = None

    @property
    def psy_rdoq(self):
        try:
            psy_rdoq = self.__ffmpeg_advanced_args['psy-rdoq=']
            psy_rdoq_value = float(psy_rdoq)
        except TypeError:
            return 0.0
        else:
            return psy_rdoq_value

    @psy_rdoq.setter
    def psy_rdoq(self, psy_rdoq_value):
        try:
            if psy_rdoq_value is None or psy_rdoq_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['psy-rdoq='] = str(psy_rdoq_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['psy-rdoq='] = None

    @property
    def me(self):
        try:
            me_value = self.__ffmpeg_advanced_args['me=']

            if me_value is None:
                me_index = 0
            else:
                me_index = self.me_ffmpeg_args_list.index(me_value)
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
                self.__ffmpeg_advanced_args['me='] = self.me_ffmpeg_args_list[me_index]
        except IndexError:
            self.__ffmpeg_advanced_args['me='] = None

    @property
    def subme(self):
        try:
            subme = self.__ffmpeg_advanced_args['subme=']
            subme_value = int(subme)
        except TypeError:
            return 2
        else:
            return subme_value

    @subme.setter
    def subme(self, subme_value):
        try:
            if subme_value is None or subme_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['subme='] = str(subme_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['subme='] = None

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
    def no_weightp(self):
        no_weightp_value = self.__ffmpeg_advanced_args['no-weightp=']

        if no_weightp_value is None or no_weightp_value != '1':
            return False

        return True

    @no_weightp.setter
    def no_weightp(self, no_weightp_enabled):
        if no_weightp_enabled is None or not no_weightp_enabled:
            self.__ffmpeg_advanced_args['no-weightp='] = None
        else:
            self.__ffmpeg_advanced_args['no-weightp='] = '1'

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
    def no_sao(self):
        no_sao_value = self.__ffmpeg_advanced_args['no-sao=']

        if no_sao_value is None or no_sao_value != '1':
            return False

        return True

    @no_sao.setter
    def no_sao(self, no_sao_enabled):
        if no_sao_enabled is None or not no_sao_enabled:
            self.__ffmpeg_advanced_args['no-sao='] = None
        else:
            self.__ffmpeg_advanced_args['no-sao='] = '1'

    @property
    def sao_non_deblock(self):
        sao_non_deblock_value = self.__ffmpeg_advanced_args['sao-non-deblock=']

        if sao_non_deblock_value is None or sao_non_deblock_value != '1':
            return False

        return True

    @sao_non_deblock.setter
    def sao_non_deblock(self, sao_non_deblock_enabled):
        if sao_non_deblock_enabled is None or not sao_non_deblock_enabled:
            self.__ffmpeg_advanced_args['sao-non-deblock='] = None
        else:
            self.__ffmpeg_advanced_args['sao-non-deblock='] = '1'

    @property
    def limit_sao(self):
        limit_sao_value = self.__ffmpeg_advanced_args['limit-sao=']

        if limit_sao_value is None or limit_sao_value != '1':
            return False

        return True

    @limit_sao.setter
    def limit_sao(self, limit_sao_enabled):
        if limit_sao_enabled is None or not limit_sao_enabled:
            self.__ffmpeg_advanced_args['limit-sao='] = None
        else:
            self.__ffmpeg_advanced_args['limit-sao='] = '1'

    @property
    def selective_sao(self):
        try:
            selective_sao = self.__ffmpeg_advanced_args['selective-sao=']
            selective_sao_value = int(selective_sao)
        except TypeError:
            return 0
        else:
            return selective_sao_value

    @selective_sao.setter
    def selective_sao(self, selective_sao_value):
        try:
            if selective_sao_value is None or selective_sao_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['selective-sao='] = str(selective_sao_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['selective-sao='] = None

    @property
    def rd(self):
        try:
            rd = self.__ffmpeg_advanced_args['rd=']
            rd_value = int(rd)
        except TypeError:
            return 3
        else:
            return rd_value

    @rd.setter
    def rd(self, rd_value):
        try:
            if rd_value is None or rd_value < 0:
                raise ValueError

            self.__ffmpeg_advanced_args['rd='] = str(rd_value)
        except (ValueError, TypeError):
            self.__ffmpeg_advanced_args['rd='] = None

    @property
    def rdoq_level(self):
        try:
            rdoq_level_value = self.__ffmpeg_advanced_args['rdoq-level=']

            if rdoq_level_value is None:
                rdoq_level_index = 0
            else:
                rdoq_level_index = self.rdoq_level_ffmpeg_args_list.index(rdoq_level_value)
        except ValueError:
            return 0
        else:
            return rdoq_level_index

    @rdoq_level.setter
    def rdoq_level(self, rdoq_level_index):
        try:
            if rdoq_level_index is None or rdoq_level_index < 1:
                self.__ffmpeg_advanced_args['rdoq-level='] = None
            else:
                self.__ffmpeg_advanced_args['rdoq-level='] = self.rdoq_level_ffmpeg_args_list[rdoq_level_index]
        except IndexError:
            self.__ffmpeg_advanced_args['rdoq-level='] = None

    @property
    def rd_refine(self):
        rd_refine_value = self.__ffmpeg_advanced_args['rd-refine=']

        if rd_refine_value is None or rd_refine_value != '1':
            return False

        return True

    @rd_refine.setter
    def rd_refine(self, rd_refine_enabled):
        if rd_refine_enabled is None or not rd_refine_enabled:
            self.__ffmpeg_advanced_args['rd-refine='] = None
        else:
            self.__ffmpeg_advanced_args['rd-refine='] = '1'

    @property
    def ctu(self):
        try:
            ctu_value = self.__ffmpeg_advanced_args['ctu=']

            if ctu_value is None:
                ctu_index = 0
            else:
                ctu_index = self.max_cu_size_ffmpeg_args_list.index(ctu_value)
        except ValueError:
            return 0
        else:
            return ctu_index

    @ctu.setter
    def ctu(self, ctu_index):
        try:
            if ctu_index is None or ctu_index < 1:
                self.__ffmpeg_advanced_args['ctu='] = None
            else:
                self.__ffmpeg_advanced_args['ctu='] = self.max_cu_size_ffmpeg_args_list[ctu_index]
        except IndexError:
            self.__ffmpeg_advanced_args['ctu='] = None

    @property
    def min_cu_size(self):
        try:
            min_cu_size_value = self.__ffmpeg_advanced_args['min-cu-size=']

            if min_cu_size_value is None:
                min_cu_size_index = 0
            else:
                min_cu_size_index = self.min_cu_size_ffmpeg_args_list.index(min_cu_size_value)
        except ValueError:
            return 0
        else:
            return min_cu_size_index

    @min_cu_size.setter
    def min_cu_size(self, min_cu_size_index):
        try:
            if min_cu_size_index is None or min_cu_size_index < 1:
                self.__ffmpeg_advanced_args['min-cu-size='] = None
            else:
                self.__ffmpeg_advanced_args['min-cu-size='] = self.min_cu_size_ffmpeg_args_list[min_cu_size_index]
        except IndexError:
            self.__ffmpeg_advanced_args['min-cu-size='] = None

    @property
    def rect(self):
        rect_value = self.__ffmpeg_advanced_args['rect=']

        if rect_value is None or rect_value != '1':
            return False

        return True

    @rect.setter
    def rect(self, rect_enabled):
        if rect_enabled is None or not rect_enabled:
            self.__ffmpeg_advanced_args['rect='] = None
        else:
            self.__ffmpeg_advanced_args['rect='] = '1'

    @property
    def amp(self):
        amp_value = self.__ffmpeg_advanced_args['amp=']

        if amp_value is None or amp_value != '1':
            return False

        return True

    @amp.setter
    def amp(self, amp_enabled):
        if amp_enabled is None or not amp_enabled:
            self.__ffmpeg_advanced_args['amp='] = None
        else:
            self.__ffmpeg_advanced_args['amp='] = '1'

    @property
    def wpp(self):
        wpp_value = self.__ffmpeg_advanced_args['wpp=']

        if wpp_value is None or wpp_value != '1':
            return False

        return True

    @wpp.setter
    def wpp(self, wpp_enabled):
        if wpp_enabled is None or not wpp_enabled:
            self.__ffmpeg_advanced_args['wpp='] = None
        else:
            self.__ffmpeg_advanced_args['wpp='] = '1'

    @property
    def pmode(self):
        pmode_value = self.__ffmpeg_advanced_args['pmode=']

        if pmode_value is None or pmode_value != '1':
            return False

        return True

    @pmode.setter
    def pmode(self, pmode_enabled):
        if pmode_enabled is None or not pmode_enabled:
            self.__ffmpeg_advanced_args['pmode='] = None
        else:
            self.__ffmpeg_advanced_args['pmode='] = '1'

    @property
    def pme(self):
        pme_value = self.__ffmpeg_advanced_args['pme=']

        if pme_value is None or pme_value != '1':
            return False

        return True

    @pme.setter
    def pme(self, pme_enabled):
        if pme_enabled is None or not pme_enabled:
            self.__ffmpeg_advanced_args['pme='] = None
        else:
            self.__ffmpeg_advanced_args['pme='] = '1'

    @property
    def uhd_bd(self):
        uhd_bd_value = self.__ffmpeg_advanced_args['uhd-bd=']

        if uhd_bd_value is None or uhd_bd_value != '1':
            return False

        return True

    @uhd_bd.setter
    def uhd_bd(self, uhd_bd_enabled):
        if uhd_bd_enabled is None or not uhd_bd_enabled:
            self.__ffmpeg_advanced_args['uhd-bd='] = None
        else:
            self.__ffmpeg_advanced_args['uhd-bd='] = '1'

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
    def stats(self, file_path):
        self.__ffmpeg_advanced_args['stats='] = file_path

    def get_ffmpeg_advanced_args(self):
        advanced_args = {'-x265-params': None}
        args = ''

        if not self.advanced_enabled:
            if self.__ffmpeg_advanced_args['pass='] is not None:
                args = self.__get_pass_args()
        else:
            args = self.__generate_advanced_args()

        if args != '':
            advanced_args['-x265-params'] = args

        return advanced_args

    def __get_pass_args(self):
        pass_args = 'pass='
        pass_args += self.__ffmpeg_advanced_args['pass=']
        pass_args += ':'
        pass_args += 'stats='
        pass_args += self.__ffmpeg_advanced_args['stats=']

        return pass_args

    def __generate_advanced_args(self):
        x265_advanced_settings = ''

        for setting, value in self.__ffmpeg_advanced_args.items():
            if value is not None:
                x265_advanced_settings += setting
                x265_advanced_settings += value
                x265_advanced_settings += ':'

        return x265_advanced_settings
