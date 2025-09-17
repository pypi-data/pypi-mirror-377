# coding=utf-8

from ut_dic.dic import Dic
from ut_obj.str import Str
from ut_obj.strdate import StrDate

from typing import Any
from collections.abc import Callable

TyArr = list[Any]
TyDic = dict[Any, Any]
TyCallable = Any | Callable[..., Any]
TyDoEq = dict[str, Any]
TyStr = str

TnArr = None | TyArr
TnDic = None | TyDic
TnDoEq = None | TyDoEq
TnStr = None | TyStr


class DoEq:
    """ Manage Commandline Arguments
    """
    sh_value_msg1 = "Wrong parameter: {}; valid parameters are: {}"
    sh_value_msg2 = "Parameter={} value={} is invalid; valid values are={}"

    @staticmethod
    def _set_sh_prof(d_eq: TyDoEq, sh_prof: TyCallable) -> None:
        """ set current pacmod dictionary
        """
        if callable(sh_prof):
            d_eq['sh_prof'] = sh_prof()
        else:
            d_eq['sh_prof'] = sh_prof

    @classmethod
    def sh_value(cls, d_eq: TyDoEq, d_valid_parms: TnDic) -> TyDoEq:
        if not d_valid_parms:
            return d_eq
        d_eq_new = {}
        for _key, _value in d_eq.items():
            _type: TnStr = d_valid_parms.get(_key)
            if _type is None:
                raise Exception(cls.sh_value_msg1.format(_key, d_valid_parms))
            match _type:
                case 'int':
                    _value = int(_value)
                case 'bool':
                    _value = Str.sh_boolean(_value)
                case 'dict':
                    _value = Str.sh_dic(_value)
                case 'list':
                    _value = Str.sh_arr(_value)
                case '%Y-%m-%d':
                    _value = StrDate.sh(_value, _type)
                case '_':
                    match _type[0]:
                        case '{':
                            _obj = Str.sh_dic(_type)
                            if _value not in _obj:
                                raise Exception(cls.sh_value_msg2.format(_value, _obj))
                        case '[':
                            _obj = Str.sh_dic(_type)
                            if _value not in _obj:
                                raise Exception(cls.sh_value_msg2.format(_value, _obj))
            d_eq_new[_key] = _value
        return d_eq_new

    @classmethod
    def sh_d_valid_parms(cls, d_eq: TyDoEq, d_parms: TnDic) -> TnDoEq:
        if d_parms is None:
            return None
        if 'cmd' in d_eq:
            _a_cmd: TyArr = d_eq['cmd'].split()
            # _valid_commands = list(d_parms.keys())
            # if _cmd not in _valid_commands:
            #     msg = (f"Wrong command: {_cmd}; "
            #            f"valid commands are: {_valid_commands}")
            #     raise Exception(msg)
            _d_valid_parms: TnDoEq = Dic.loc(d_parms, *_a_cmd)
            return _d_valid_parms
        else:
            return d_parms

    @classmethod
    def verify(cls, d_eq: TyDoEq, d_parms: TnDic) -> TyDoEq:
        if d_parms is None:
            return d_eq
        _d_valid_parms: TnDic = cls.sh_d_valid_parms(d_eq, d_parms)
        if _d_valid_parms is None:
            return d_eq
        d_eq_new: TyDoEq = cls.sh_value(d_eq, _d_valid_parms)
        return d_eq_new

    @classmethod
    def sh_d_eq(cls, d_equ: TyDoEq, **kwargs) -> TyDic:
        """ show equates dictionary
        """
        _d_parms: TnDic = kwargs.get('d_parms')
        _prof = kwargs.get('sh_prof')
        _d_eq: TyDic = DoEq.verify(d_equ, _d_parms)
        cls._set_sh_prof(_d_eq, _prof)
        return _d_eq
