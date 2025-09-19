# coding=utf-8
from collections.abc import Callable
from typing import Any

TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyArr_Dic = TyArr | TyDic
TyDoC = dict[str, TyCallable]

TnStr = None | str
TnDoC = None | TyDoC
TnCallable = None | TyCallable


class DoC:
    """
    Dictionary of Callables
    """
    @classmethod
    def ex_cmd(cls, doc: TnDoC, kwargs: TyDic) -> Any:
        """
        Get the cmd from arguments and keyword argument list args_kwargs
        and call the ex function with the given cmd.
        """
        cmd: TnStr = kwargs.get('cmd')
        return cls.ex(doc, cmd, kwargs)

    @classmethod
    def ex(cls, doc: TnDoC, cmd: TnStr, args_kwargs: TyArr_Dic) -> Any:
        """
        Show and execute the function located as the value of the
        given cmd in the function dictionary.
        """
        fnc: TyCallable = cls.sh(doc, cmd)
        return fnc(args_kwargs)

    @staticmethod
    def sh(doc: TnDoC, key: TnStr) -> TyCallable:
        """
        Show(get) the function as the value of the
        function-dictionary for the given key.
        """
        if not doc:
            msg = f"function table: {doc} is not defined"
            raise Exception(msg)
        if not key:
            msg = f"key: {key} is not defined"
            raise Exception(msg)
        fnc: TnCallable = doc.get(key)
        if not fnc:
            msg = f"key: {key} is not defined in function table: {doc}"
            raise Exception(msg)
        return fnc
