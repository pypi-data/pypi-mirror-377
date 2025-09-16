"""
@lifetime >= 0.3.26rc3 \\
© 2024-Present Aveyzan // License: MIT

Core of `aveytense.types`; import this module instead
"""

from __future__ import annotations
import sys as _sys

from ._exceptions import _ErrorHandler as _E

from abc import (
    
    # 0.3.44
    ABC as ABC, 
    ABCMeta as ABCMeta,
    abstractmethod as abstractmethod
)

from array import (
    
    # 0.3.37
    array as array, 
    ArrayType as ArrayType
)

from ast import (
    
    # 0.3.44
    Expression as Expression, 
    Module as Module,
    Interactive as Interactive,
    
    # 0.3.54
    AST as AST
)

from collections import (
    
    # 0.3.37
    ChainMap as ChainMap, 
    Counter as Counter,
    defaultdict as defaultdict,
    deque as deque,
    OrderedDict as OrderedDict,
    
    # 0.3.44
    UserDict as UserDict,
    UserList as UserList,
    namedtuple as namedtuple,
    UserString as UserString
)

from collections.abc import (
    
    # < 0.3.50
    AsyncGenerator as AsyncGenerator,
    AsyncIterable as AsyncIterable,
    AsyncIterator as AsyncIterator,
    Awaitable as Awaitable,
    Callable as Callable,
    Collection as Collection,
    Container as Container,
    Coroutine as Coroutine,
    Generator as Generator,
    Hashable as Hashable,
    ItemsView as ItemsView,
    Iterable as Iterable,
    Iterator as Iterator,
    KeysView as KeysView,
    Mapping as Mapping,
    MappingView as MappingView,
    MutableMapping as MutableMapping,
    MutableSequence as MutableSequence,
    MutableSet as MutableUniqual, # pyright: ignore[reportUnusedImport]
    Reversible as Reversible,
    Sequence as Sequence,
    Set as Uniqual, # Naming to this to prevent ambiguity with typing.Set alias
    Sized as Sized,
    ValuesView as ValuesView
)

from contextlib import (
    
    # 0.3.53
    AbstractAsyncContextManager as AsyncContentManager, # pyright: ignore[reportUnusedImport]
    AbstractContextManager as ContextManager, # pyright: ignore[reportUnusedImport]
)

from dataclasses import dataclass as dataclass # 0.3.37
from enum import EnumMeta as EnumMeta # 0.3.26rc1

from functools import (
    
    # 0.3.26
    partial as partial,
    
    # 0.3.37
    cached_property as cachedproperty, 
    partialmethod as partialmethod,
    singledispatchmethod as singledispatchmethod,
    lru_cache as lru_cache,
    singledispatch as singledispatch,
    
    # 0.3.54
    lru_cache as lruCache, # pyright: ignore[reportUnusedImport]
    singledispatch as singleDispatch # pyright: ignore[reportUnusedImport]
)

from importlib import (
    
    # 0.3.44
    import_module as import_module,
    
    # 0.3.54
    import_module as importModule # pyright: ignore[reportUnusedImport]
)

from inspect import (
    
    # 0.3.26rc3
    ArgInfo as ArgInfo, 
    Arguments as Arguments,
    Attribute as Attribute,
    BlockFinder as BlockFinder,
    BoundArguments as BoundArguments,
    ClosureVars as ClosureVars,
    FrameInfo as FrameInfo,
    FullArgSpec as FullArgSpec,
    Parameter as Parameter,
    Signature as Signature,
    Traceback as Traceback,
)

from os import PathLike as PathLike # 0.3.52

from re import (
    
    # 0.3.26
    Match as Match, 
    Pattern as Pattern
)

# Imports from 0.3.51 are used for builtin function inspection via ~.util.ParamVar.

from types import (
    
    # 0.3.26rc1/0.3.34?
    coroutine as coroutine, # >=Py3.3
    new_class as new_class, # >=Py3.5
    
    # 0.3.26rc3
    new_class as newClass, # pyright: ignore[reportUnusedImport]
    ModuleType as ModuleType,
    TracebackType as TracebackType,
    CodeType as CodeType,
    
    # 0.3.37
    FunctionType as FunctionType,
    FrameType as FrameType,
    MethodType as MethodType,
    
    # 0.3.42
    MappingProxyType as MappingProxyType, # >=Py3.3
    
    # 0.3.43
    DynamicClassAttribute as DynamicClassAttribute,
    
    # 0.3.44
    AsyncGeneratorType as AsyncGeneratorType, # >=Py3.6
    CoroutineType as CoroutineType, # >=Py3.5
    
    # 0.3.51
    BuiltinFunctionType as BuiltinFunctionType, 
    ClassMethodDescriptorType as ClassMethodDescriptorType, # >=Py3.7
    MethodDescriptorType as MethodDescriptorType, # >=Py3.7
    MethodWrapperType as MethodWrapperType, # >=Py3.7
    WrapperDescriptorType as WrapperDescriptorType, # >=Py3.7
    
    # 0.3.53
    SimpleNamespace as SimpleNamespace, 
    
    # 0.3.54
    CellType as CellType, # >=Py3.8
    prepare_class as prepare_class, # >=Py3.3
    resolve_bases as resolve_bases, # >=Py3.7
    prepare_class as prepareClass # pyright: ignore[reportUnusedImport]
)

from typing import (
    
    # 0.3.26rc1
    no_type_check as noTypeCheck, # pyright: ignore[reportUnusedImport]
    
    # 0.3.37
    get_type_hints as get_type_hints, 
    no_type_check as no_type_check, 
    
    # 0.3.44
    cast as cast,
    
    # 0.3.54
    get_type_hints as getTypeHints # pyright: ignore[reportUnusedImport]
)

from unittest import (
    
    # 0.3.26rc3
    TestCase as TestCase, 
    TestLoader as TestLoader,
)

from uuid import UUID as UUID # 0.3.26rc3

__name__ = "aveytense.types"

# In this part of the code, we are retrieving currently used version of 'typing_extensions', and formalize the version
# like sys.version_info:
class TypingExtensionsVersionInfo:
    """
    @lifetime >= 0.3.54
    
    Version info for `typing_extensions`
    """
    
    def __init__(self):
        
        from importlib.metadata import version
        
        _typing_ext_string_ver_ = version("typing_extensions")
        
        # There I am believing devs won't use the epoch version component.
        # Every version since version 4.0.0 have 3 components, unlike before 4.0.0
        # some can have 4 (last being submicro)
        _split_components_ = _typing_ext_string_ver_.split(".")
        
        self.major = int(_split_components_[0])
        self.minor = int(_split_components_[1])
        
        _search_ = ("a", "b", "rc")
        _submicro_ = len(_split_components_) == 4
        
        if not _submicro_:
            self.submicro = 0
        else:
            self.micro = int(_split_components_[2])
            
        _search_found_ = False
        
        for search in _search_:
                
            if search in _split_components_[-1]:
                
                _search_found_ = True
                _split_id_ = _split_components_[-1].split(search)
                
                if not _submicro_:
                    self.micro = int(_split_id_[0])
                else:
                    self.submicro = int(_submicro_[0])
                
                if search == "a":
                    self.releaselevel = ("alpha", 1)
                    
                elif search == "b":
                    self.releaselevel = ("beta", 2)
                    
                else:
                    self.releaselevel = ("candidate", 3)
                    
                self.serial = int(_split_id_[1])
                
                break
                
        if not _search_found_:
            
            if not _submicro_:
                self.micro = int(_split_components_[-1])
            else:
                self.submicro = int(_split_components_[-1])
                
            self.releaselevel = ("final", 4)
            self.serial = 0

    def __gt__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        if len(other) == 1:
            return other < (self.major,)
        
        elif len(other) == 2:
            return other < (self.major, self.minor)
        
        elif len(other) == 3:
            return other < (self.major, self.minor, self.micro)
        
        elif len(other) == 4:
            
            if self.submicro == 0:
                return other < (self.major, self.minor, self.micro, self.releaselevel[1])
            else:
                return other < (self.major, self.minor, self.micro, self.submicro)
            
        return False
    
    def __lt__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        return not self.__gt__(other) and other != (self.major, self.minor, self.micro, self.releaselevel[1] if self.submicro == 0 else self.submicro)[:len(other)]
    
    def __ge__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        return not self.__lt__(other)
    
    def __le__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        return not self.__gt__(other)
    
    def __eq__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        return not self.__gt__(other) and not self.__lt__(other)
    
    def __ne__(self, other: tuple, /):
        
        if not isinstance(other, tuple):
            return False
        
        return not self.__eq__(other)
    
    def __str__(self):
        
        if self.releaselevel[1] == 1:
            _level_ = "a"
        elif self.releaselevel[1] == 2:
            _level_ = "b"
        elif self.releaselevel[1] == 3:
            _level_ = "rc"
        else:
            _level_ = None
        
        return "typing_extensions {}".format(".".join((
            str(self.major),
            str(self.minor),
            str(self.micro),
        )) + (
            "" if self.submicro == 0 else "." + str(self.submicro)
        ) + (
            _level_ + str(self.serial) if _level_ is not None else ""
        ))

TypingExtensionsVersionInfo = TypingExtensionsVersionInfo()        
    
### ENUMS & FLAGS ###
# 0.3.44: Additional checking to ensure these enumerator and flag classes exist already.

import enum as _enum

class Enum(_enum.Enum): # accessible for >=Py3.8
    """
    @lifetime >= 0.3.26rc1 [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)
    """
    
class Flag(_enum.Flag): # accessible for >=Py3.8
    """
    @lifetime >= 0.3.26rc1 [`enum.Flag`](https://docs.python.org/3/library/enum.html#enum.Flag)
    """
    
class ReprEnum(Enum): # >=Py3.11; practically subclass of enum.Enum and nothing in the body. Try to define for least than Py3.11
    """
    @lifetime >= 0.3.26rc1 [`enum.ReprEnum`](https://docs.python.org/3/library/enum.html#enum.ReprEnum)
    """

if _sys.version_info >= (3, 11):
    
    from enum import verify as verify, EnumCheck as EnumCheck, EnumType as EnumType
    
    # If not the same (as before 3.13 it can occur), we need to ensure they are the same by using type assignment
    if ReprEnum != _enum.ReprEnum:
        ReprEnum = _enum.ReprEnum
        
class EnumDict(Enum): # base class ignored after assignment below
    """
    @lifetime >= 0.3.26rc1 [`enum.EnumDict`](https://docs.python.org/3/library/enum.html#enum.EnumDict)
    
    Undocumented internal class `enum._EnumDict` before Python 3.13
    """
    
if _sys.version_info >= (3, 13):
    EnumDict = _enum.EnumDict
    
else:
    # questionable: since when enum._EnumDict was in enum.py file?
    EnumDict = _enum._EnumDict
    
class FlagBoundary(Enum): # >=Py3.11. Define for least than Py3.11
    """
    @lifetime >= 0.3.26rc1 [`enum.FlagBoundary`](https://docs.python.org/3/library/enum.html#enum.FlagBoundary)
    
    Control how out of range values are handled.
    
    `STRICT` -> error is raised             (default for `Flag`) \\
    `CONFORM` -> extra bits are discarded \\
    `EJECT` -> lose flag status \\
    `KEEP` -> keep flag status and all bits (default for `IntFlag`)
    """
    STRICT = _enum.auto() # 1; enum.auto accessible for >=Py3.8
    CONFORM = _enum.auto() # 2
    EJECT = _enum.auto() # 3
    KEEP = _enum.auto() # 4

class IntegerFlag(_enum.IntFlag): # accessible for >=Py3.8 (can be recreated via bases: >= Py3.11 (int, ReprEnum, Flag, boundary=FlagBoundary.KEEP), < Py3.11 (int, Flag))
    """
    @lifetime >= 0.3.26rc1. [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)
    """

if _sys.version_info >= (3, 11):
    
    class IntegerEnum(_enum.IntEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
        """
        
    class StringEnum(_enum.StrEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)
        """
        
else:
    
    class IntegerEnum(int, ReprEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
        """
        
    class StringEnum(str, ReprEnum):
        """
        @lifetime >= 0.3.26rc1. [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)
        """
        
        def __new__(cls, *values):
            "values must already be of type `str`"
            if len(values) > 3:
                raise TypeError('too many arguments for str(): %r' % (values, ))
            if len(values) == 1:
                # it must be a string
                if not isinstance(values[0], str):
                    raise TypeError('%r is not a string' % (values[0], ))
            if len(values) >= 2:
                # check that encoding argument is a string
                if not isinstance(values[1], str):
                    raise TypeError('encoding must be a string, not %r' % (values[1], ))
            if len(values) == 3:
                # check that errors argument is a string
                if not isinstance(values[2], str):
                    raise TypeError('errors must be a string, not %r' % (values[2]))
            value = str(*values)
            member = str.__new__(cls, value)
            member._value_ = value
            return member

        @staticmethod
        def _generate_next_value_(name, start, count, last_values):
            """
            Return the lower-cased version of the member name.
            """
            return name.lower()
        
### UTILITY TYPES ###

from typing import (
    
    # 0.3.26b3
    Generic as Generic, # >=Py3.5
    ClassVar as ClassVar, # >=Py3.5.3
    NoReturn as NoReturn, # >=Py3.6.2 (older doc can say 3.6.5)
    
    # 0.3.26rc1
    Optional as Optional, # >=Py3.5
    Union as Union, # >=Py3.5
    Final as Final, # >=Py3.8
    Protocol as Protocol, # >=Py3.8
    
    # 0.3.26rc3 
    ForwardRef as ForwardRef, # >=Py3.7.4
    
    # 0.3.37
    TYPE_CHECKING as TYPE_CHECKING # >=Py3.5.2
    
)

## >=3.7
from uuid import SafeUUID as SafeUUID

# ****************** Py3.9: 10/2020 ************************
# / 0.3.42 /: Inspect type subscription with abstract base
# classes from 'collections.abc'
# / 0.3.46 /: Inspect type substription with inbuilt classes
# from 'builtins' in submodule '~._subscript_builtins'
# / 0.3.52 /: Migrate inbuilt classes there; types with AVT_
# prefix only have purpose for typing, more specifically,
# subscripting. These change when going since or below Python 3.9.
# Some generic classes can throw errors when inspecting
# them in isinstance() or issubclass(), hence ordinarily classes
# without AVT_ prefix are exported.
if _sys.version_info >= (3, 9):
    
    # do not remove these unused imports!
    
    
    from builtins import (
        
        # 0.3.52
        dict as _AVT_Dict,
        frozenset as _AVT_FrozenSet,
        list as _AVT_List,
        set as _AVT_Set,
        tuple as AVT_Tuple,
        type as _AVT_Type
    )
    
    
    from collections import (
        
        # 0.3.52
        ChainMap as _AVT_ChainMap,
        Counter as _AVT_Counter,
        OrderedDict as _AVT_OrderedDict,
        defaultdict as _AVT_DefaultDict,
        deque as _AVT_Deque
    )
    
    
    from collections.abc import (
        
        # 0.3.52
        AsyncGenerator as _AVT_AsyncGenerator,
        AsyncIterable as _AVT_AsyncIterable,
        AsyncIterator as _AVT_AsyncIterator,
        Awaitable as _AVT_Awaitable,
        Callable as _AVT_Callable,
        Collection as _AVT_Collection,
        Container as _AVT_Container,
        Coroutine as _AVT_Coroutine,
        Generator as _AVT_Generator,
        ItemsView as _AVT_ItemsView,
        Iterable as _AVT_Iterable,
        Iterator as _AVT_Iterator,
        KeysView as _AVT_KeysView,
        Mapping as _AVT_Mapping,
        MappingView as _AVT_MappingView,
        MutableMapping as _AVT_MutableMapping,
        MutableSequence as _AVT_MutableSequence,
        MutableSet as _AVT_MutableUniqual,
        Reversible as _AVT_Reversible,
        Sequence as _AVT_Sequence,
        Set as _AVT_Uniqual,
        ValuesView as _AVT_ValuesView
    )
    
    
    from contextlib import (
        
        # 0.3.53
        AbstractAsyncContextManager as _AVT_AsyncContextManager,
        AbstractContextManager as _AVT_ContextManager
    )
    
    # 0.3.54
    from os import PathLike as _AVT_PathLike
    
    
    from re import (
        
        # 0.3.52
        Match as _AVT_Match,
        Pattern as _AVT_Pattern
    )
    
    from typing import (
        
        # ?
        IO as IO,
        
        # 0.3.26rc1
        Annotated as Annotated,
        
        # 0.3.26rc3
        BinaryIO as BinaryIO, 
        TextIO as TextIO
    )
    
    from types import GenericAlias as GenericAlias # 0.3.37
    
else:
    
    from typing import (
        
        # builtins, 0.3.52
        Dict as _AVT_Dict,
        FrozenSet as _AVT_FrozenSet,
        List as _AVT_List,
        Set as _AVT_Set,
        Tuple as AVT_Tuple,
        Type as _AVT_Type,
        
        # collections, 0.3.52
        ChainMap as _AVT_ChainMap,
        Counter as _AVT_Counter,
        OrderedDict as _AVT_OrderedDict,
        DefaultDict as _AVT_DefaultDict,
        Deque as _AVT_Deque,
        
        # collections.abc, 0.3.52
        AsyncGenerator as _AVT_AsyncGenerator,
        AsyncIterable as _AVT_AsyncIterable,
        AsyncIterator as _AVT_AsyncIterator,
        Awaitable as _AVT_Awaitable,
        Callable as _AVT_Callable,
        Collection as _AVT_Collection,
        Container as _AVT_Container,
        Coroutine as _AVT_Coroutine,
        Generator as _AVT_Generator,
        ItemsView as _AVT_ItemsView,
        Iterable as _AVT_Iterable,
        Iterator as _AVT_Iterator,
        KeysView as _AVT_KeysView,
        Mapping as _AVT_Mapping,
        MappingView as _AVT_MappingView,
        MutableMapping as _AVT_MutableMapping,
        MutableSequence as _AVT_MutableSequence,
        MutableSet as _AVT_MutableUniqual,
        Reversible as _AVT_Reversible,
        Sequence as _AVT_Sequence,
        Set as _AVT_Uniqual,
        ValuesView as _AVT_ValuesView,
        
        # contextlib, 0.3.53
        AsyncContextManager as _AVT_AsyncContextManager,
        ContextManager as _AVT_ContextManager,
        
        # re, 0.3.52
        Match as _AVT_Match,
        Pattern as _AVT_Pattern,
        
        # temporary internal imports for '_AVT_PathLike'
        TypeVar as _TypeVar,
        runtime_checkable as _runtime
    )
    
    from typing_extensions import Annotated as Annotated # 0.3.26rc1
    
    if TypingExtensionsVersionInfo >= (4, 7):
        from typing_extensions import (
            
            # ?
            IO as IO,
            # 0.3.26rc3
            BinaryIO as BinaryIO, # 0.3.26rc3
            TextIO as TextIO # 0.3.26rc3
        )
    
    _AnyStr_cov_pathLikeExclusive = _TypeVar("_AnyStr_cov_pathLikeExclusive", str, bytes, covariant = True)
    
    @_runtime
    class _AVT_PathLike(Protocol[_AnyStr_cov_pathLikeExclusive]):
        """@lifetime >= 0.3.54"""
        
        def __fspath__(self) -> _AnyStr_cov_pathLikeExclusive: ...
        
    del _TypeVar, _runtime

# ****************** Py3.10: 10/2021 ************************
if _sys.version_info >= (3, 10):
    
    from typing import (
        
        # 0.3.26rc1
        ParamSpec as ParamSpec, 
        ParamSpecArgs as ParamSpecArgs,
        ParamSpecKwargs as ParamSpecKwargs,
        TypeGuard as TypeGuard,
        TypeAlias as TypeAlias,
        Concatenate as Concatenate,
        get_args as get_args, # (renamed 0.3.34 from `getArgs`)
        
        # 0.3.37
        get_origin as get_origin,
        
        # 0.3.54
        get_args as getArgs, # pyright: ignore[reportUnusedImport]
        get_origin as getOrigin # pyright: ignore[reportUnusedImport]
    )
    
    from types import (
        
        # ?
        EllipsisType as EllipsisType,
        
        # 0.3.26
        NoneType as NoneType, # 0.3.26
        
        # 0.3.37
        UnionType as UnionType, 
        NotImplementedType as NotImplementedType
        
    )
    
    from inspect import get_annotations as get_annotations # 0.3.37
    
else:
    
    from typing_extensions import (
        # 0.3.26rc1
        ParamSpec as ParamSpec, 
        ParamSpecArgs as ParamSpecArgs, 
        ParamSpecKwargs as ParamSpecKwargs,
        TypeGuard as TypeGuard, 
        TypeAlias as TypeAlias,
        Concatenate as Concatenate,
        final as _final,
        get_args as get_args, # (renamed 0.3.34 from `getArgs`)
        
        # 0.3.37
        get_origin as get_origin,
        
        # 0.3.54
        get_origin as getOrigin, # pyright: ignore[reportUnusedImport]
        get_args as getArgs # pyright: ignore[reportUnusedImport]
    )
    
    NotImplementedType = type(NotImplemented) # >= 0.3.52
    
    # warrant usage for Py3.8 and Py3.9
    @_final
    class NoneType:
        "@lifetime >= 0.3.26"
        def __bool__(self) -> Literal[False]: ...
        
    @_final
    class EllipsisType: ...
        
    NoneType = cast(NoneType, type(None))
    EllipsisType = cast(EllipsisType, type(Ellipsis))
    
    del _final

# Literal (3.8+) bugfix (to 3.10.1)
if _sys.version_info >= (3, 10, 1):
    from typing import Literal as Literal # 0.3.26rc1
    
else:
    from typing_extensions import Literal as Literal # 0.3.26rc1

# ****************** Py3.11: 10/2022 ************************
# NewType (3.5.2+): the error message for subclassing instances
# of NewType was improved on 3.11
if _sys.version_info >= (3, 11):
    
    from typing import (
        
        # 0.3.26rc1
        LiteralString as LiteralString, 
        Never as Never,
        NewType as NewType,
        Self as Self,
        Any as Any,
        NotRequired as NotRequired,
        Required as Required,
        overload as overload,
        
        # 0.3.37
        assert_never as assert_never, 
        assert_type as assert_type,
        clear_overloads as clear_overloads,
        final as final,
        get_overloads as get_overloads,
        reveal_type as reveal_type,
        
        # 0.3.54
        assert_never as assertNever, # pyright: ignore[reportUnusedImport]
        assert_type as assertType, # pyright: ignore[reportUnusedImport]
        clear_overloads as clearOverloads, # pyright: ignore[reportUnusedImport]
        get_overloads as getOverloads, # pyright: ignore[reportUnusedImport]
        reveal_type as revealType, # pyright: ignore[reportUnusedImport]
    )
    
else:
    
    from typing_extensions import (
        
        # 0.3.26rc1
        NewType as NewType, 
        Any as Any,
        overload as overload,
        
        # 0.3.37
        final as final
    )
    
    if TypingExtensionsVersionInfo >= (4, 0):
        from typing_extensions import (
            
            # 0.3.26rc1
            Self as Self, 
            NotRequired as NotRequired,
            Required as Required
        )
    
    if TypingExtensionsVersionInfo >= (4, 1):
        from typing_extensions import (
            
            # 0.3.26rc1
            LiteralString as LiteralString, 
            Never as Never,
            
            # 0.3.37
            assert_never as assert_never,
            reveal_type as reveal_type,
            
            # 0.3.54
            assert_never as assertNever, # pyright: ignore[reportUnusedImport]
            reveal_type as revealType # pyright: ignore[reportUnusedImport]
        )
        
    if TypingExtensionsVersionInfo >= (4, 2):
        from typing_extensions import (
            
            # 0.3.37
            assert_type as assert_type, 
            clear_overloads as clear_overloads,
            get_overloads as get_overloads,
            
            # 0.3.54
            assert_type as assertType, # pyright: ignore[reportUnusedImport]
            clear_overloads as clearOverloads, # pyright: ignore[reportUnusedImport]
            get_overloads as getOverloads # pyright: ignore[reportUnusedImport]
        )

# ****************** Py3.12: 10/2023 ************************
# Unpack (3.11+): see PEP 692 (changed the repr of Unpack[])
# dataclass_transform (3.11+) was lacking frozen_default parameter
if _sys.version_info >= (3, 12):
    
    from typing import (
        
        # 0.3.26rc1
        Unpack as Unpack,
        
        # 0.3.37
        dataclass_transform as dataclass_transform, 
        override as override,
        
        # 0.3.54
        dataclass_transform as dataclassTransform # pyright: ignore[reportUnusedImport]
    )
    
    from types import (
        
        # 0.3.40
        get_original_bases as get_original_bases,
        
        # 0.3.54
        get_original_bases as getOriginalBases # pyright: ignore[reportUnusedImport]
    )
    
    from collections.abc import Buffer as _Buffer # 0.3.37
    from inspect import BufferFlags as BufferFlags # 0.3.26rc2
    
else:
    
    if TypingExtensionsVersionInfo >= (4, 1):
        from typing_extensions import (
            
            # 0.3.26rc1
            Unpack as Unpack,
            
            # 0.3.37
            dataclass_transform as dataclass_transform,
            
            # 0.3.54
            dataclass_transform as dataclassTransform # pyright: ignore[reportUnusedImport]
        )
        
    if TypingExtensionsVersionInfo >= (4, 4):
        from typing_extensions import override as override # 0.3.37
    
    if TypingExtensionsVersionInfo >= (4, 6):
        from typing_extensions import Buffer as _Buffer # 0.3.37
    
    class BufferFlags(IntegerFlag): # 0.3.26rc2
        SIMPLE = 0x0
        WRITABLE = 0x1
        FORMAT = 0x4
        ND = 0x8
        STRIDES = 0x10 | ND
        C_CONTIGUOUS = 0x20 | STRIDES
        F_CONTIGUOUS = 0x40 | STRIDES
        ANY_CONTIGUOUS = 0x80 | STRIDES
        INDIRECT = 0x100 | STRIDES
        CONTIG = ND | WRITABLE
        CONTIG_RO = ND
        STRIDED = STRIDES | WRITABLE
        STRIDED_RO = STRIDES
        RECORDS = STRIDES | WRITABLE | FORMAT
        RECORDS_RO = STRIDES | FORMAT
        FULL = INDIRECT | WRITABLE | FORMAT
        FULL_RO = INDIRECT | FORMAT
        READ = 0x100
        WRITE = 0x200

# ****************** Py3.13: 10/2024 ************************
# About TypeVar & TypeVarTuple see PEP 696 about 'default'
# parameter. NamedTuple is for backporting updates since its
# existence (3.5.2)
if _sys.version_info >= (3, 13):
    
    from typing import (
        
        # 0.3.26b3
        TypeVar as TypeVar, 
        
        # 0.3.26rc1
        NamedTuple as NamedTuple, 
        Protocol as Protocol,
        TypeIs as TypeIs,
        NoDefault as NoDefault,
        ReadOnly as ReadOnly,
        runtime_checkable as runtime,
        runtime_checkable as runtime_checkable,
        
        # 0.3.26rc3
        TypeVarTuple as TypeVarTuple,
        
        # 0.3.37
        get_protocol_members as get_protocol_members,
        is_protocol as is_protocol,
        
        # 0.3.54
        get_protocol_members as getProtocolMembers, # pyright: ignore[reportUnusedImport]
        is_protocol as isProtocol # pyright: ignore[reportUnusedImport]
        
    )
    
    from types import CapsuleType as CapsuleType # 0.3.54
    
else:
    
    from typing_extensions import (
        
        # 0.3.26b3
        TypeVar as TypeVar,
        
        # 0.3.26rc1
        NamedTuple as NamedTuple, 
        Protocol as Protocol,
        runtime_checkable as runtime,
        runtime_checkable as runtime_checkable,
        
        # 0.3.37
        is_protocol as is_protocol, 
        
        # 0.3.54
        is_protocol as isProtocol # pyright: ignore[reportUnusedImport]
    )
    
    if TypingExtensionsVersionInfo >= (4, 1):
        from typing_extensions import TypeVarTuple as TypeVarTuple # 0.3.26rc3
        
    if TypingExtensionsVersionInfo >= (4, 7):
        
        from typing_extensions import (
            # 0.3.37
            get_protocol_members as get_protocol_members,
            
            # 0.3.54
            get_protocol_members as getProtocolMembers # pyright: ignore[reportUnusedImport]
        )
        
    if TypingExtensionsVersionInfo >= (4, 9):
        from typing_extensions import ReadOnly as ReadOnly # 0.3.26rc1
    
    if TypingExtensionsVersionInfo >= (4, 10):
        from typing_extensions import TypeIs as TypeIs # 0.3.26rc1
    
    if TypingExtensionsVersionInfo >= (4, 12):
        from typing_extensions import (
            CapsuleType as CapsuleType, # 0.3.54
            NoDefault as NoDefault # 0.3.26rc1
        )                              
    
if _sys.version_info >= (3, 13, 3):
    from warnings import deprecated as deprecated # 0.3.37
else:
    
    if TypingExtensionsVersionInfo >= (4, 5):
        from typing_extensions import deprecated as deprecated # 0.3.37

# ****************** Py3.14: 10/2025 ************************
# Removal of 'collections.abc.ByteString', but we will still
# re-declare it
if _sys.version_info >= (3, 14):
    
    # 0.3.54
    import annotationlib # pyright: ignore[reportUnusedImport]
    
    from typing import TypeAliasType as TypeAliasType # 0.3.26rc1
    
    ByteString = Union[bytes, bytearray, memoryview] # 0.3.37
    
else:
    
    class annotationlib:
        """@lifetime >= 0.3.54"""
    
        if TypingExtensionsVersionInfo >= (4, 8):
            from typing_extensions import Doc as Doc
        
        if TypingExtensionsVersionInfo >= (4, 13):
            from typing_extensions import Format as Format
            
        else:
            class Format(IntegerEnum):
                VALUE = 1
                VALUE_WITH_FAKE_GLOBALS = 2
                FORWARDREF = 3
                STRING = 4
    
    if TypingExtensionsVersionInfo >= (4, 6):
        from typing_extensions import TypeAliasType as TypeAliasType # 0.3.26rc1
        
    if TypingExtensionsVersionInfo >= (4, 13):
        from typing_extensions import NoExtraItems as NoExtraItems # 0.3.54
        
    from collections.abc import ByteString as ByteString # 0.3.37   

### ****************** Py3.15: 10/2026 ************************
# If you are unfamiliar of PEP 728 about extra items in
# 'typing.TypedDict', PEP 728 was accepted and is planned for
# Python 3.15. 'typing_extensions' forgot one detail: set their
# internal value for PEP 728 check to 'False'. I will redo this
# statement in latest version, if anything changes with this PEP.
if _sys.version_info >= (3, 15):
    
    from typing import (
        
        # 0.3.37
        TypedDict as TypedDict, 
        is_typeddict as is_typeddict,
        
        # 0.3.54
        is_typeddict as isTypedDict # pyright: ignore[reportUnusedImport]
    ) 
    
else:
    
    from typing_extensions import TypedDict as TypedDict # 0.3.37
    
    if TypingExtensionsVersionInfo >= (4, 1):
        from typing_extensions import (
            
            # 0.3.37
            is_typeddict as is_typeddict, 
            # 0.3.54
            is_typeddict as isTypedDict # pyright: ignore[reportUnusedImport]
        )
    
    from typing import (
        
        # ?
        no_type_check_decorator as no_type_check_decorator,
        # 0.3.26rc1
        no_type_check_decorator as noTypeCheckDecorator # pyright: ignore[reportUnusedImport]
    )

### ****************** Py3.18: 10/2029 ************************
if _sys.version_info >= (3, 18):
    
    AnyStr = TypeVar("AnyStr", bytes, str)

else:
    
    from typing import AnyStr as AnyStr
    
def _restrict_args_count(origin, args, count):
    
    if not isinstance(args, tuple):
        _args_ = (args,)
    else:
        _args_ = args
    
    if len(_args_) > count:
        error = TypeError("expected {} type argument(s), got {}".format(str(count), str(len(_args_))))
        raise error
    
    if _sys.version_info >= (3, 9):
        return GenericAlias(origin, args)
    else:
        return TypingGenericType(origin, args)

import _collections_abc, _hashlib, hashlib, hmac as _hmac, typing as _typing, typing_extensions as _typing_ext 

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_T_con = TypeVar("_T_con", contravariant = True)
_T_cov = TypeVar("_T_cov", covariant = True)
_KT_con = TypeVar("_KT_con", contravariant = True)
_KT_cov = TypeVar("_KT_cov", covariant = True)
_VT_cov = TypeVar("_VT_cov", covariant = True)
_T_exit_cov = TypeVar("_T_exit_cov", covariant = True, bound = Optional[bool], default = Optional[bool])
_T_yield_cov = TypeVar("_T_yield_cov", covariant = True)
_T_send_con = TypeVar("_T_send_con", contravariant = True, default = None)
_T_return_cov = TypeVar("_T_return_cov", covariant = True, default = None)
_T_send_noDefault_con = TypeVar("_T_send_noDefault_con", contravariant = True)
_T_return_noDefault_cov = TypeVar("_T_return_noDefault_cov", covariant = True)
_P = ParamSpec("_P")

_A = TypeVar("_A", int, float, str) # for 'array.array'
_I = TypeVar("_I", default = int) # for 'memoryview'

# 0.3.52
# These both local variables below hold special names that Python uses in lambda and generator expressions.
# We use this way to ensure the change with this attribute's value will happen simultaneously with AveyTense.
_LambdaName = (lambda: None).__name__ # "<lambda>"
_GenExprName = (i for i in (1,)).__qualname__ # "<genexpr>"

class _GenExprTypeMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object):
        return isinstance(obj, Generator) and obj.__qualname__.endswith(_GenExprName)

class _LambdaTypeMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object):
        return isinstance(obj, FunctionType) and obj.__name__.endswith(_LambdaName)

class GenExprType(metaclass = _GenExprTypeMeta):
    """
    @lifetime >= 0.3.52
    
    Use this class to find, if a generator object is actually created from generator expression, with `isinstance()`.
    """
    __init__ = None
    
class LambdaType(metaclass = _LambdaTypeMeta):
    """
    @lifetime >= 0.3.44 \\
    @modified 0.3.52
    
    Use this class to find, if a callable is actually a lambda expression, with `isinstance()`.
    
    NOTE: this class isn't the same as Python's `types.LambdaType`, and it is reserved for `isinstance()` only
    """
    if False: # projected
        def __new__(
            cls,
            code: CodeType,
            globals: _AVT_Dict[str, Any],
            argdefs: Optional[AVT_Tuple[object, ...]] = None,
            closure: Optional[AVT_Tuple[CellType, ...]] = None,
            kwdefaults: Optional[_AVT_Dict[str, object]] = None
        ):
            # using assumption 'types.LambdaType' is type alias to 'types.FunctionType',
            # return 'types.FunctionType', just without the 'name' parameter required
            return FunctionType(code, globals, _LambdaName, argdefs, closure, kwdefaults)
    else:
        __init__ = None
    
class _SpecialFormMeta(type):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object): # 0.3.53: enhance type checking
        
        from typing import _SpecialForm
        from typing_extensions import _SpecialForm as _ExtSpecialForm
        
        # since 3.13 'typing.Annotated' is instance of 'typing._SpecialForm'
        if _sys.version_info >= (3, 13):
            return isinstance(obj, (_SpecialForm, _ExtSpecialForm))
        else:
            return isinstance(obj, (_SpecialForm, _ExtSpecialForm)) or obj is Annotated
        
        """elif _sys.version_info >= (3, 11):
            return isinstance(obj, _SpecialForm) or obj in (Annotated,)
        
        else:
            return isinstance(obj, _SpecialForm) or obj in (Annotated, Self, Never, LiteralString)"""
            
class AnnotationForm:
    """
    @lifetime >= 0.3.48
    
    Refer to `_typeshed.AnnotationForm` and return value as from this type alias (`typing.Any`)
    """
    
# Let's be honest, I was having trouble re-creating these classes with type annotations.
# In reality none of these are protocols, because these get appropriate values assigned later,
# these definitions are only for correct type hinting
class AnyMeta(Protocol):
    """@lifetime >= 0.3.52"""
    def __instancecheck__(self, obj: object) -> bool: ...
    def __repr__(self) -> str: ...
    
@final
class DictKeys(_AVT_KeysView[_KT_cov], Generic[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_keys` (generic only on stub files)
    """
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> _AVT_Iterator[_KT_cov]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if _sys.version_info >= (3, 13):
        def isdisjoint(self, other: _AVT_Iterable[_KT_cov], /) -> bool: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...

@final
class DictValues(_AVT_ValuesView[_VT_cov], Generic[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_values` (generic only on stub files)
    """
    def __reversed__(self) -> _AVT_Iterator[_VT_cov]: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...

@final
class DictItems(_AVT_ItemsView[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.53
    
    Generic version of class `_collections_abc.dict_items` (generic only on stub files)
    """
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> _AVT_Iterator[AVT_Tuple[_KT_cov, _VT_cov]]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if _sys.version_info >= (3, 13):
        def isdisjoint(self, other: _AVT_Iterable[AVT_Tuple[_KT_cov, _VT_cov]], /) -> bool: ...
    if _sys.version_info >= (3, 10):
        @property
        def mapping(self) -> MappingProxyType[_KT_cov, _VT_cov]: ...
    
class ProtocolMeta(Protocol):
    """@lifetime >= 0.3.52"""
    __protocol_attrs__: ClassVar[_AVT_Set[str]]
    def __init__(cls, *args: Any, **kwargs: Any) -> None: ...
    def __new__(
        mcls: _AVT_Type[Self],
        name: str,
        bases: AVT_Tuple[type, ...],
        namespace: _AVT_Dict[str, Any],
        /,
        **kwargs: Any
    ) -> Self: ...
    def __subclasscheck__(self, cls: type) -> bool: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    
class SpecialForm(metaclass = _SpecialFormMeta):
    """
    @lifetime >= 0.3.52
    
    Use this class to find, if a type is actually a special form from `typing`
    """
    
class TypedDictMeta(Protocol):
    """@lifetime >= 0.3.52"""
    def __new__(cls, typename: str, fields: _AVT_Dict[str, Any] = {}, /, *, total: bool = True) -> Self: ...

class TypingNoDefaultType:
    """@lifetime >= 0.3.53"""
    
class TypingTupleType(tuple):
    """
    @lifetime >= 0.3.53
    
    Get internal class for deprecated type alias `typing.Tuple` (inaccessible via mere `tuple`)
    """

class TypingGenericType(Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for generic aliases before `types.GenericAlias` (>=Py3.9)
    """
    _name: Optional[str] # ?
    _inst: bool # ?
    @property
    def __origin__(self) -> Union[type, TypeAliasType]: ...
    @property
    def __args__(self) -> AVT_Tuple[Any, ...]: ...
    @property
    def __parameters__(self) -> AVT_Tuple[Any, ...]: ...
    if _sys.version_info >= (3, 9):
        __slots__: None
        def __init__(self, origin: type, args: AVT_Tuple[Any, ...], *, inst: bool = True, name: Optional[str] = None) -> None: ...
    else:
        _special: bool # ?
        def __init__(self, origin: type, args: Any, *, inst: bool = True, special: bool = False, name: Optional[str] = None) -> None: ...
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    if _sys.version_info >= (3, 10):
        def __or__(self, other: type) -> UnionType: ...
        def __ror__(self, other: type) -> UnionType: ...
    else:
        def __or__(self, other: type) -> TypingUnionType: ...
        def __ror__(self, other: type) -> TypingUnionType: ...
    def __getitem__(self, args: Any) -> Self: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> _AVT_Generator[Any, Any, None]: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def copy_with(self, args: Any) -> Self: ...
    def _determine_new_args(self, args: Any) -> AVT_Tuple[Any, ...]: ...
    def _make_substitution(self, args: _AVT_Iterable[type], new_arg_by_param: Any) -> _AVT_List[Any]: ...
    ### inherited from typing._BaseGenericAlias ###
    def __dir__(self) -> _AVT_List[str]: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    def __subclasscheck__(self, cls: type) -> NoReturn: ...
    def __setattr__(self, attr: str, val: Any) -> None: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __mro_entries__(self, bases: _AVT_Iterable[object]) -> AVT_Tuple[type, ...]: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ... 

class TypingAnnotatedType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Annotated` class
    """
    __iter__: None
    @property
    def __origin__(self) -> Union[type, TypeAliasType]: ...
    @property
    def __metadata__(self) -> Any: ...
    def __init__(self, origin: type, metadata: Any) -> None: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    def __getattr__(self, attr: str) -> Any: ...
    def __mro_entries__(self, bases: _AVT_Iterable[object]) -> AVT_Tuple[type, ...]: ...
    def copy_with(self, args: Any) -> Self: ...
    
class TypingCallableType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `collections.abc.Callable` class
    """
    __iter__: None
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    
class TypingConcatenateType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Concatenate` class
    """
    def copy_with(self, args: Any) -> Self: ...
    
class TypingLiteralType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Literal` class
    """
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    
class TypingUnionType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Union` class
    """
    __iter__: None
    def __eq__(self, other: Self) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __reduce__(self) -> AVT_Tuple[Any, ...]: ...
    def __instancecheck__(self, obj: object) -> bool: ...
    def __subclasscheck__(self, cls: type) -> bool: ...
    def copy_with(self, args: Any) -> Self: ...
    
class TypingUnpackType(TypingGenericType, Protocol):
    """
    @lifetime >= 0.3.52
    
    Retrieves internal class for `typing.Unpack` class
    """
    def __repr__(self) -> str: ...
    def __getitem__(self, args: Any) -> Self: ...
    @property
    def __typing_unpacked_tuple_args__(self) -> Optional[AVT_Tuple[Any, ...]]: ...
    @property
    def __typing_is_unpacked_typevartuple__(self) -> bool: ...

# If you see many invocations of typing.cast(), I do it because I want all these to look like classes

cached_property = cachedproperty

AnnotationForm = cast(AnnotationForm, Any) # 0.3.48; _typeshed.AnnotationForm
AnyMeta = cast(AnyMeta, type(Any)) # >= 0.3.52

if False: # < 0.3.52
    Callback = Callable # 0.3.26b3
    Containable = Container # >= 0.3.26rc1
    Invocable = Callable # >= 0.3.26rc1
    SpecVar = ParamSpec
    SpecVarArgs = ParamSpecArgs
    SpecVarKwargs = ParamSpecKwargs
    TypeTupleVar = TypeVarTuple
    
async def _f(): pass
_coroutine = _f()

# this class as '_collections_abc.coroutine_wrapper' doesn't exist, neither does it exist in 'types'
CoroutineWrapperType = type(_coroutine.__await__()) # >= 0.3.53

_coroutine.close()
del _coroutine   

Hash = _hashlib.HASH # >= 0.3.44

# 0.3.53: '_hashlib.HASHXOF' undefined before Python 3.9
if _sys.version_info >= (3, 9): 
    Hashxof = _hashlib.HASHXOF # >= 0.3.44
else:
    Hashxof = type(hashlib.shake_128()) # >= 0.3.44

Hmac = _hmac.HMAC # >= 0.3.44
InComparable = _AVT_Container # >= 0.3.26rc1
Interface = Protocol # >= 0.3.44

# io >= Py3.14
if TypingExtensionsVersionInfo >= (4, 14):
    IOReader = _typing_ext.Reader # >= 0.3.54
    IOWriter = _typing_ext.Writer # >= 0.3.54

LenOperable = Sized # >= 0.3.26rc1
Pack = Concatenate
ProtocolMeta = cast(ProtocolMeta, type(Protocol)) # >= 0.3.52
ReadableBuffer = _Buffer # >= 0.3.44; refer to _typeshed.ReadableBuffer
ReadOnlyBuffer = _Buffer # >= 0.3.44; refer to _typeshed.ReadOnlyBuffer
Sizeable = Sized # >= 0.3.26rc3
TypedDictMeta = cast(TypedDictMeta, type(TypedDict("a", {}))) # >= 0.3.52

# typing >= Py3.14?
if TypingExtensionsVersionInfo >= (4, 13): 
    # >= 0.3.52
    TypeForm = _typing_ext.TypeForm # type: ignore

### Private classes from typing.py ###
# Use these with isinstance() to determine if these are desired special forms.

TypingAnnotatedType = cast(TypingAnnotatedType, type(Annotated[int, "$"])) # >= 0.3.52

if False: # remove this alias on 0.3.54
    TypingBaseGenericType = cast(TypingBaseGenericType, type(TypeGuard[int]).__base__) # >= 0.3.53; < 0.3.54

# Python 3.8 returns 'typing._GenericAlias', since Python 3.9 returned type is independent
TypingCallableType = cast(TypingCallableType, type(_AVT_Callable[..., Any])) # >= 0.3.52

# 0.3.53: Before Python 3.11, it is a TypeError for missing 'typing.ParamSpec' at the end of type parameters list
# 0.3.52 used ellipsis instead
TypingConcatenateType = cast(TypingConcatenateType, type(Concatenate[int, _P])) # >= 0.3.52

TypingGenericType = cast(TypingGenericType, type(TypeGuard[int])) # >= 0.3.52

if _sys.version_info >= (3, 9):
    
    class _TypingGenericType(TypingGenericType, _root=True):
        """
        @lifetime >= 0.3.54
        
        Same as `typing._GenericAlias`, just overrides the `__repr__` method to attempt returning valid module a generic \\
        type alias is defined in. Unlike for `typing._SpecialGenericAlias`, `__repr__` is defined with `typing` module preceding.
        
        This technique will not work once subscripting - it will hint `typing` as the module.
        """
        
        @_typing._tp_cache
        def __getitem__(self, args):
            
            # Parameterizes an already-parameterized object.
            #
            # For example, we arrive here doing something like:
            #   T1 = TypeVar('T1')
            #   T2 = TypeVar('T2')
            #   T3 = TypeVar('T3')
            #   class A(Generic[T1]): pass
            #   B = A[T2]  # B is a _GenericAlias
            #   C = B[T3]  # Invokes _GenericAlias.__getitem__
            #
            # We also arrive here when parameterizing a generic `Callable` alias:
            #   T = TypeVar('T')
            #   C = Callable[[T], None]
            #   C[int]  # Invokes _GenericAlias.__getitem__
            
            import typing
            
            if self.__origin__ in (Generic, Protocol):
                # Can't subscript Generic[...] or Protocol[...].
                raise TypeError(f"Cannot subscript already-subscripted {self}")
            if not self.__parameters__:
                raise TypeError(f"{self} is not a generic class")

            # Preprocess `args`.
            if not isinstance(args, tuple):
                args = (args,)
            args = typing._unpack_args(*(typing._type_convert(p) for p in args))
            return self.copy_with(self._determine_new_args(args))
        
        def __repr__(self):
            
            import typing
            
            if self._name:
                name = self.__module__ + "." + self._name
            else:
                name = typing._type_repr(self.__origin__)
            if self.__args__:
                args = ", ".join([typing._type_repr(a) for a in self.__args__])
            else:
                # To ensure the repr is evaluable.
                args = "()"
            
            return f'{name}[{args}]'
    
else:
    
    class _TypingGenericType(TypingGenericType, _root=True):
        """
        @lifetime >= 0.3.54
        
        Same as `typing._GenericAlias`, just overrides the `__repr__` method to return valid module a generic \\
        type alias is defined in. Unlike for `typing._SpecialGenericAlias`, `__repr__` is defined with `typing` \\
        module preceding.
        
        This technique will not work once subscripting - it will hint `typing` as the module.
        """

        def __repr__(self):
            
            import typing
            
            if (self._name != 'Callable' or
                    len(self.__args__) == 2 and self.__args__[0] is Ellipsis):
                if self._name:
                    name = self.__module__ + "." + self._name
                else:
                    name = typing._type_repr(self.__origin__)
                if not self._special:
                    args = f'[{", ".join([typing._type_repr(a) for a in self.__args__])}]'
                else:
                    args = ''
                return (f'{name}{args}')
            if self._special:
                return 'typing.Callable'
            return (f'typing.Callable'
                    f'[[{", ".join([typing._type_repr(a) for a in self.__args__[:-1]])}], '
                    f'{typing._type_repr(self.__args__[-1])}]')

TypingGenericType = cast(TypingGenericType, _TypingGenericType) # >= 0.3.52
TypingGenericType.__name__ = TypingGenericType.__qualname__ = "TypingGenericType"
del _TypingGenericType

TypingLiteralType = cast(TypingLiteralType, type(Literal[""])) # >= 0.3.52
TypingNoDefaultType = cast(TypingNoDefaultType, type(NoDefault)) # >= 0.3.53

# Even if 'typing.Tuple' is deprecated, it actually has an internal class that implements it. So I decided
# for version 0.3.54 to copy and paste this code scrap.
#
# 'type(tuple)' would return 'type' instead. 'type(AVT_Tuple[int])' is 'typing._GenericAlias' for Python 3.8
# and 'types.GenericAlias' since Python 3.9. There we are making sure 'typing.Tuple' is defined

if hasattr(_typing, "Tuple"):
    TypingTupleType = cast(TypingTupleType, type(_typing.Tuple)) # >= 0.3.53
    
# these statements below are from 0.3.54
elif _sys.version_info >= (3, 9):
    class TypingTupleType(type(_typing.Generator), _root=True):
        """
        @lifetime >= 0.3.54
        
        Re-declare internal class `typing._TupleType`
        """
        @_typing._tp_cache
        def __getitem__(self, params):
            
            import typing
            
            if not isinstance(params, tuple):
                params = (params,)
            if len(params) >= 2 and params[-1] is ...:
                msg = "Tuple[t, ...]: t must be a type."
                params = tuple(typing._type_check(p, msg) for p in params[:-1])
                return self.copy_with((*params, typing._TypingEllipsis))
            msg = "Tuple[t0, t1, ...]: each t must be a type."
            params = tuple(typing._type_check(p, msg) for p in params)
            return self.copy_with(params)
else:
    class TypingTupleType(TypingGenericType, _root=True):
        """
        @lifetime >= 0.3.54
        
        Re-declare internal class `typing._TupleType`
        """
        def __getitem__(self, params):
            if self._name != 'Callable' or not self._special:
                return self.__getitem_inner__(params)
            if not isinstance(params, tuple) or len(params) != 2:
                raise TypeError("Callable must be used as "
                                "Callable[[arg, ...], result].")
            args, result = params
            if args is Ellipsis:
                params = (Ellipsis, result)
            else:
                if not isinstance(args, list):
                    raise TypeError(f"Callable[args, result]: args must be a list."
                                    f" Got {args}")
                params = (tuple(args), result)
            return self.__getitem_inner__(params)

        @_typing._tp_cache
        def __getitem_inner__(self, params):
            
            import typing
            
            if self.__origin__ is tuple and self._special:
                if params == ():
                    return self.copy_with((typing._TypingEmpty,))
                if not isinstance(params, tuple):
                    params = (params,)
                if len(params) == 2 and params[1] is ...:
                    msg = "Tuple[t, ...]: t must be a type."
                    p = typing._type_check(params[0], msg)
                    return self.copy_with((p, typing._TypingEllipsis))
                msg = "Tuple[t0, t1, ...]: each t must be a type."
                params = tuple(typing._type_check(p, msg) for p in params)
                return self.copy_with(params)
            if self.__origin__ is Callable and self._special:
                args, result = params
                msg = "Callable[args, result]: result must be a type."
                result = typing._type_check(result, msg)
                if args is Ellipsis:
                    return self.copy_with((typing._TypingEllipsis, result))
                msg = "Callable[[arg, ...], result]: each arg must be a type."
                args = tuple(typing._type_check(arg, msg) for arg in args)
                params = args + (result,)
                return self.copy_with(params)
            return super().__getitem__(params)

# Python 3.8 returns 'typing._GenericAlias', since Python 3.9 returned class is 'typing._UnionGenericAlias',
# since Python 3.14 returned class will be different (right?)
TypingUnionType = cast(TypingUnionType, type(Union[int, str])) # >= 0.3.52

TypingUnpackType = cast(TypingUnpackType, type(Unpack[AVT_Tuple[int, str]])) # >= 0.3.52

Unused = object # >= 0.3.44; refer to _typeshed.Unused
Uuid = UUID # >= 0.3.54
WriteableBuffer = _Buffer # >= 0.3.44; refer to _typeshed.WriteableBuffer

### NON-STRICT GENERIC CLASSES ###

if _sys.version_info >= (3, 12):
    _AVT_Array = array
    
else:
    class _AVT_Array(array, Generic[_A]):
        __name__ = __qualname__ = "AVT_Array"
        
        if _sys.version_info >= (3, 9):
            __class_getitem__ = classmethod(GenericAlias)
            
AVT_Array = _AVT_Array[_A]
"""@lifetime >= 0.3.54"""

if _sys.version_info >= (3, 9):
    AVT_AsyncContextManager = _AVT_AsyncContextManager[_T_cov, _T_exit_cov]
    """@lifetime >= 0.3.53"""
    
else:
    AVT_AsyncContextManager = _AVT_AsyncContextManager[_T_cov]
    """@lifetime >= 0.3.53"""

AVT_AsyncGenerator = _AVT_AsyncGenerator[_T_yield_cov, _T_send_con]
"""@lifetime >= 0.3.52"""

AVT_AsyncIterable = _AVT_AsyncIterable[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_AsyncIterator = _AVT_AsyncIterator[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Awaitable = _AVT_Awaitable[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Callable = _AVT_Callable # not in 'strict' class
"""@lifetime >= 0.3.52"""

AVT_ChainMap = _AVT_ChainMap[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_Collection = _AVT_Collection[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Container = _AVT_Container[_T_cov]
"""@lifetime >= 0.3.52"""

if _sys.version_info >= (3, 9):
    AVT_ContextManager = _AVT_ContextManager[_T_cov, _T_exit_cov]
    """@lifetime >= 0.3.53"""
    
else:
    AVT_ContextManager = _AVT_ContextManager[_T_cov]
    """@lifetime >= 0.3.53"""

AVT_Coroutine = _AVT_Coroutine[_T_yield_cov, _T_send_noDefault_con, _T_return_noDefault_cov]
"""@lifetime >= 0.3.52"""

AVT_Counter = _AVT_Counter[_T]
"""@lifetime >= 0.3.52"""

AVT_DefaultDict = _AVT_DefaultDict[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_Deque = _AVT_Deque[_T]
"""@lifetime >= 0.3.52"""

AVT_Dict = _AVT_Dict[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_FrozenSet = _AVT_FrozenSet[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Generator = _AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]
"""@lifetime >= 0.3.52"""

if _sys.version_info >= (3, 9):
    _AVT_GenericAlias = GenericAlias # >= 0.3.55
else:
    _AVT_GenericAlias = TypingGenericType # >= 0.3.55
    
AVT_GenericAlias = _AVT_GenericAlias # not in 'strict' class
"""@lifetime >= 0.3.55"""

AVT_ItemsView = _AVT_ItemsView[_KT_cov, _VT_cov]
"""@lifetime >= 0.3.52"""

AVT_Iterable = _AVT_Iterable[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Iterator = _AVT_Iterator[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_KeysView = _AVT_KeysView[_KT_cov]
"""@lifetime >= 0.3.52"""

AVT_List = _AVT_List[_T]
"""@lifetime >= 0.3.52"""

AVT_Mapping = _AVT_Mapping[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_MappingView = _AVT_MappingView
"""@lifetime >= 0.3.52"""

AVT_Match = _AVT_Match[AnyStr]
"""@lifetime >= 0.3.52"""

if _sys.version_info >= (3, 14):
    _AVT_MemoryView = memoryview
else:
    
    class _AVT_MemoryView(_AVT_Sequence[_I]):
        __name__ = __qualname__ = "AVT_MemoryView"
        
        def __new__(cls, obj: ReadableBuffer):
            return memoryview(obj)
        
        if _sys.version_info >= (3, 9):
            __class_getitem__ = classmethod(GenericAlias)
            
AVT_MemoryView = _AVT_MemoryView[_I]
"""@lifetime >= 0.3.54"""
            
AVT_MutableMapping = _AVT_MutableMapping[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_MutableSequence = _AVT_MutableSequence[_T]
"""@lifetime >= 0.3.52"""

AVT_MutableUniqual = _AVT_MutableUniqual[_T]
"""@lifetime >= 0.3.52"""

AVT_OrderedDict = _AVT_OrderedDict[_KT, _VT]
"""@lifetime >= 0.3.52"""

AVT_PathLike = _AVT_PathLike
"""@lifetime >= 0.3.54"""

AVT_Pattern = _AVT_Pattern[AnyStr]
"""@lifetime >= 0.3.52"""

AVT_Reversible = _AVT_Reversible[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Sequence = _AVT_Sequence[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_Set = _AVT_Set[_T]
"""@lifetime >= 0.3.52"""

AVT_Type = _AVT_Type[_T]
"""@lifetime >= 0.3.52"""

if _sys.version_info >= (3, 10): 
    _AVT_UnionType = UnionType # >= 0.3.55
else:
    _AVT_UnionType = TypingUnionType # >= 0.3.55
    
AVT_UnionType = _AVT_UnionType
"""@lifetime >= 0.3.55"""
    
AVT_Uniqual = _AVT_Uniqual[_T_cov]
"""@lifetime >= 0.3.52"""

AVT_ValuesView = _AVT_ValuesView[_VT_cov]
"""@lifetime >= 0.3.52"""

# With these abstract base classes, type hinting may be incorrect, even if normally
# it should type hint correctly. Use these at your own risk, as 'aveytense.types.strict.<AVT_ prefixed class>'.

# 're.Match' and 're.Pattern' are neither mutable nor subclassable, so using tactic with 'type' in this case.
if hasattr(_AVT_Match, "__class_getitem__"):
    
    _match_dict = dict(
        [(k, _AVT_Match.__dict__[k]) for k in _AVT_Match.__dict__ if k != "__class_getitem__"] +
        [("__class_getitem__", lambda cls, args: _restrict_args_count(cls, args, 1)), ("__module__", __name__)]
    )

else:
    _match_dict = dict(
        [(k, _AVT_Match.__dict__[k]) for k in _AVT_Match.__dict__] +
        [("__module__", __name__)]
    )
    
if hasattr(_AVT_Pattern, "__class_getitem__"):
    
    _pattern_dict = dict(
        [(k, _AVT_Pattern.__dict__[k]) for k in _AVT_Pattern.__dict__ if k != "__class_getitem__"] +
        [("__class_getitem__", lambda cls, args: _restrict_args_count(cls, args, 1))]
    )

else:
    _pattern_dict = dict(
        [(k, _AVT_Pattern.__dict__[k]) for k in _AVT_Pattern.__dict__] +
        [("__module__", __name__)]
    )

class strict:
    """
    @lifetime >= 0.3.55
    
    Provides a little more strict generic type equivalents. \\
    Strictness is for deducing correct amount of type arguments
    """
    
    def __init__(self, *args, **kwds):
        error = TypeError("the '{}' class objects cannot be constructed".format(type(self).__name__))
        raise error
    
    def __init_subclass__(cls, *args, **kwds):
        error = TypeError("the '{}' class cannot be inherited")
        raise error
    
    if _sys.version_info >= (3, 12):
        class AVT_Array(array[_A]):
            """@lifetime >= 0.3.54"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 1)
        
    else:
        class AVT_Array(array, Generic[_A]):
            """@lifetime >= 0.3.54"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 1)

    if _sys.version_info >= (3, 9):

        class AVT_AsyncContextManager(_AVT_AsyncContextManager[_T_cov, _T_exit_cov]):
            """@lifetime >= 0.3.55"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 2)
                
    else:
        
        class AVT_AsyncContextManager(_AVT_AsyncContextManager[_T_cov]):
            """@lifetime >= 0.3.55"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 1)

    class AVT_AsyncGenerator(_AVT_AsyncGenerator[_T_yield_cov, _T_send_con]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
        
    class AVT_AsyncIterable(_AVT_AsyncIterable[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_AsyncIterator(_AVT_AsyncIterator[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Awaitable(_AVT_Awaitable[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_ChainMap(_AVT_ChainMap[_KT, _VT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
            
    class AVT_Collection(_AVT_Collection[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Container(_AVT_Container[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    if _sys.version_info >= (3, 9):

        class AVT_ContextManager(_AVT_ContextManager[_T, _T_exit_cov]):
            """@lifetime >= 0.3.55"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 2)
                
    else:
        
        class AVT_ContextManager(_AVT_ContextManager[_T]):
            """@lifetime >= 0.3.55"""
            
            if _sys.version_info >= (3, 9):
                def __class_getitem__(cls, args):
                    return _restrict_args_count(cls, args, 1)
            
    class AVT_Coroutine(_AVT_Coroutine[_T_yield_cov, _T_send_noDefault_con, _T_return_noDefault_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 3)
            
    class AVT_Counter(_AVT_Counter[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_DefaultDict(_AVT_DefaultDict[_KT, _VT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
            
    class AVT_Deque(_AVT_Deque[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Dict(_AVT_Dict[_KT, _VT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
            
    class AVT_FrozenSet(_AVT_FrozenSet[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Generator(_AVT_Generator[_T_yield_cov, _T_send_con, _T_return_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 3)
            
    class AVT_ItemsView(_AVT_ItemsView[_KT_cov, _VT_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)

    class AVT_Iterable(_AVT_Iterable[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Iterator(_AVT_Iterator[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    class AVT_KeysView(_AVT_KeysView[_KT_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_List(_AVT_List[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    class AVT_Mapping(_AVT_Mapping[_KT, _VT_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)

    # in 'typing.pyi', the type parameter assigned is not visible. prefer subscripting there anyway
    class AVT_MappingView(_AVT_MappingView[_KT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
        
    class AVT_Match(Generic[AnyStr]): # for type hinting
        """@lifetime >= 0.3.55"""
        
        __dict__ = _match_dict
        
    class AVT_MemoryView(_AVT_Sequence[_I]):
        """@lifetime >= 0.3.55"""
        
        def __new__(cls, obj: ReadableBuffer):
            return memoryview(obj)
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
                
    class AVT_MutableMapping(_AVT_MutableMapping[_KT, _VT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
            
    class AVT_MutableSequence(_AVT_MutableSequence[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    class AVT_MutableUniqual(_AVT_MutableUniqual[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_OrderedDict(_AVT_OrderedDict[_KT, _VT]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 2)
            
    class AVT_PathLike(_AVT_PathLike[AnyStr]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
        
    class AVT_Pattern(Generic[AnyStr]): # for type hinting
        """@lifetime >= 0.3.55"""
        
        __dict__ = _pattern_dict

    class AVT_Reversible(_AVT_Reversible[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    class AVT_Sequence(_AVT_Sequence[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Set(_AVT_Set[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

    AVT_Tuple = AVT_Tuple
    """@lifetime >= 0.3.52"""

    class AVT_Type(_AVT_Type[_T]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_Uniqual(_AVT_Uniqual[_T_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)
            
    class AVT_ValueView(_AVT_ValuesView[_VT_cov]):
        """@lifetime >= 0.3.55"""
        
        if _sys.version_info >= (3, 9):
            def __class_getitem__(cls, args):
                return _restrict_args_count(cls, args, 1)

del _collections_abc, _hashlib, hashlib, _hmac, _typing, _typing_ext # not for export!

# these type aliases are not official; not recommended to use them
StringUnion = Union[_T, str]
"@lifetime >= 0.3.26rc3"
IntegerUnion = Union[_T, int]
"@lifetime >= 0.3.26rc3"
FloatUnion = Union[_T, float]
"@lifetime >= 0.3.26rc3"
ComplexUnion = Union[_T, complex]
"@lifetime >= 0.3.26rc3"
IntegerFloatUnion = Union[_T, int, float]
"@lifetime >= 0.3.26rc3"
IntegerStringUnion = Union[_T, int, str]
"@lifetime >= 0.3.26rc3"
BooleanUnion = Union[_T, bool]
"@lifetime >= 0.3.26rc3"
TrueUnion = Union[_T, Literal[True]]
"@lifetime >= 0.3.26rc3"
FalseUnion = Union[_T, Literal[False]]
"@lifetime >= 0.3.26rc3"
OptionalUnion = Optional[Union[_T]]
"@lifetime >= 0.3.26rc3. `typing.Optional[typing.Union[T]]`"

# more warranted to stay
OptionalCallable = Optional[AVT_Callable[_P, _T]]
"@lifetime >= 0.3.26rc3. `typing.Optional[typing.Callable[**P, T]]` = `((**P) -> T) | None`"
AnyCallable = AVT_Callable[..., Any]
"@lifetime >= 0.3.26rc3. `typing.Callable[..., typing.Any]` = `(...) -> Any`"

TrueSequence = Union[_AVT_Sequence[_T], _AVT_Uniqual[_T]] # >= 0.3.54
"@lifetime >= 0.3.54. `typing.Union[Sequence[T], AbstractSet[T]]`"

### ABSTRACT BASE CLASSES ###
# These from _typeshed.pyi and not in collections.abc

@runtime
class ItemGetter(Protocol[_T_con, _T_cov]): # v = self[key] (type determined by _T_cov)
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__getitem__`. Type parameters:
    - first equals type for `key`
    - second equals returned type

    This method is invoked whether we want to get value \\
    via index notation `self[key]`, as instance of the class.
    """
    def __getitem__(self, key: _T_con, /) -> _T_cov: ...

if _sys.version_info >= (3, 9):
    
    @runtime
    class ClassItemGetter(Protocol): # v = self[key] (not instance)
        """
        @lifetime >= 0.3.26rc3

        An ABC with one method `__class_getitem__`. No type parameters.

        This method is invoked whether we want to get value \\
        via index notation `self[key]`, as reference to the class.
        """
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

class SizeableItemGetter(Sizeable, ItemGetter[int, _T_cov]):
    """
    @lifetime >= 0.3.27a3

    An ABC with methods `__len__` and `__getitem__`. Type parameters:
    - first equals returned type for `__getitem__`
    """
    ...

@runtime
class ItemSetter(Protocol[_T_con, _T_cov]): # self[key] = value
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__setitem__`. Type parameters:
    - first equals type for `key`
    - second equals type for `value`

    This method is invoked whether we want to set a new value for \\
    specific item accessed by `key`, as `self[key] = value`.
    """
    def __setitem__(self, key: _T_con, value: _T_cov, /) -> None: ...

@runtime
class ItemDeleter(Protocol[_T_con]): # del self[key]
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__delitem__`. Type parameters:
    - first equals type for `key`

    This method is invoked whether we want to delete specific item \\
    using `del` keyword as `del self[key]`.
    """
    def __delitem__(self, key: _T_con, /) -> None: ...

@runtime
class Getter(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__get__`. Type parameters:
    - first equals returned type
    """
    def __get__(self, instance: object, owner: Optional[type] = None, /) -> _T_cov: ...

@runtime
class Setter(Protocol[_T_con]):
    """
    @lifetime >= 0.3.27a3

    An ABC with one method `__set__`. Type parameters:
    - first equals type for `value`
    """
    def __set__(self, instance: object, value: _T_con, /) -> None: ...
    
@runtime
class Deleter(Protocol):
    """
    @lifetime >= 0.3.44
    
    An ABC with one method `__delete__`. No type parameters.
    """
    def __delete__(self, instance: object, /) -> None: ...
    
class Descriptor(
    Setter[_T_con],
    Getter[_T_cov],
    Deleter
):
    """
    @lifetime >= 0.3.44
    
    An ABC providing descriptor methods: `__get__`, `__set__` and `__delete__`
    """
    ...

@runtime
class FinalDescriptor(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.44
    
    An ABC providing descriptor methods, just `__set__` and `__delete__` throw an error. \\
    The same as `~.util.finalproperty` works.
    """
    def __get__(self, instance: Optional[object], owner: Optional[type] = None, /) -> _T_cov: ...
    def __set__(self, instance: Optional[object], value: Any, /) -> NoReturn: ...
    def __delete__(self, instance: Optional[object], /) -> NoReturn: ...
    

class KeysProvider(ItemGetter[_KT_con, Any]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `keys`. Type parameters:
    - first equals key
    - second equals value
    """
    def keys(self) -> Iterable[_KT_con]: ...

@runtime
class ItemsProvider(Protocol[_KT_cov, _VT_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `items`. Type parameters:
    - first equals key
    - second equals value
    """
    def items(self) -> Uniqual[tuple[_KT_cov, _VT_cov]]: ...
    
@runtime
class Buffer(Protocol):
    """
    @lifetime >= 0.3.44
    
    An ABC with one method `__buffer__`.
    """
    def __buffer__(self, flags: int, /) -> memoryview: ...
    
Buffer = _Buffer

@runtime
class BufferReleaser(Protocol):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__release_buffer__`.
    """
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...
    
# >= 0.3.44; < 0.3.54 as 'BufferManager'
@runtime
class BufferProtocol(Protocol):
    """
    @lifetime >= 0.3.54
    
    This ABC allows to implement buffer protocol to specific class
    """
    def __buffer__(self, flags: int, /) -> memoryview: ...
    def __release_buffer__(self, buffer: memoryview, /) -> None: ...

@runtime
class NewArgumentsGetter(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__getnewargs__`. Type parameters:
    - first equals type for returned tuple
    """
    def __getnewargs__(self) -> AVT_Tuple[_T_cov]: ...

class ItemManager(
    ItemGetter[_T_con, _T_cov],
    ItemSetter[_T_con, _T_cov],
    ItemDeleter[_T_con]
):
    """
    @lifetime >= 0.3.26rc3

    An ABC with following methods:
    - `__getitem__` - two type parameters (key type, return type)
    - `__setitem__` - two type parameters (key type, return type)
    - `__delitem__` - one type parameter (key type)
    """
    ...

@runtime
class SubclassHooker(Protocol):
    """
    @lifetime >= 0.3.26

    An ABC with one method `__subclasshook__`. No type parameters.

    Description: \\
    "Abstract classes can override this to customize `issubclass()`. \\
    This is invoked early on by `abc.ABCMeta.__subclasscheck__()`. \\
    It should return True, False or NotImplemented. If it returns \\
    NotImplemented, the normal algorithm is used. Otherwise, it \\
    overrides the normal algorithm (and the outcome is cached)."
    """
    def __subclasshook__(cls, subclass: type, /) -> bool: ...

@runtime
class LengthHintProvider(Protocol):
    """
    @lifetime >= 0.3.26rc3

    An ABC with one method `__length_hint__`. No type parameters.

    This method is invoked like in case of `list` built-in, just on behalf of specific class. \\
    It should equal invoking `len(self)`, as seen for `list`: "Private method returning \\
    an estimate of `len(list(it))`". Hard to explain this method, still, this class will be kept. 
    """
    def __length_hint__(self) -> int: ...

FSPathProvider = _AVT_PathLike
"""@lifetime >= 0.3.27a3"""

@runtime
class BytearrayConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__bytearray__`, which *has* to equal invoking `bytearray(self)`.
    """
    def __bytearray__(self) -> bytearray: ...

@runtime
class ListConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__tlist__` (before 0.3.27a3 - `__list__`), which *has* to equal invoking `list(self)`. \\
    Returned list type is addicted to covariant type parameter.
    """
    
    def __tlist__(self) -> _AVT_List[_T_cov]:
        "@lifetime >= 0.3.26rc3. Return `list(self)`"
        ...

@runtime
class TupleConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__ttuple__` (before 0.3.27a3 - `__tuple__`), which *has* to equal invoking `tuple(self)`. \\
    Returned tuple type is addicted to covariant type parameter.
    """
    
    def __ttuple__(self) -> AVT_Tuple[_T_cov, ...]:
        "@lifetime >= 0.3.26rc3. Return `tuple(self)`"
        ...

@runtime
class SetConvertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc3

    An unofficial ABC with one method `__tset__` (before 0.3.27a3 - `__set_init__`), which *has* to equal invoking `set(self)`. \\
    Returned set type is addicted to covariant type parameter.
    """
    
    def __tset__(self) -> _AVT_Set[_T_cov]:
        "@lifetime >= 0.3.26rc3. Return `set(self)`"
        ...

@runtime
class ReckonOperable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An unofficial ABC with one method `__reckon__`, which equals `aveytense.reckon(self)`. \\
    Returned type is always an integer.
    """
    def __reckon__(self) -> int:
        """
        @lifetime >= 0.3.26rc1

        Return `reckon(self)`.
        """
        ...

@runtime
class Absolute(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__abs__`, which equals invoking `abs(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __abs__(self) -> _T_cov: ...

@runtime
class Truncable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__trunc__`, which equals invoking `math.trunc(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __trunc__(self) -> _T_cov: ...

@runtime
class BooleanConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bool__` which equals invoking `bool(self)`.
    """
    def __bool__(self) -> bool: ...
    
    if _sys.version_info < (0, 3, 44): # __nonzero__ is only on Py2
        def __nonzero__(self) -> bool: ...

@runtime
class IntegerConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__int__`, which equals invoking `int(self)`
    """
    def __int__(self) -> int: ...

@runtime
class FloatConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__float__`, which equals invoking `float(self)`
    """
    def __float__(self) -> float: ...

@runtime
class ComplexConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__complex__`, which equals invoking `complex(self)`
    """
    def __complex__(self) -> complex: ...

@runtime
class BytesConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bytes__`, which equals invoking `bytes(self)`
    """
    def __bytes__(self) -> bytes: ...

if False: # < 0.3.48
    
    @runtime
    @deprecated("Deprecated since unicode() function doesn't exist. Deprecated since 0.3.41, and will be removed on 0.3.48")
    class UnicodeRepresentable(Protocol):
        """
        @lifetime >= 0.3.26rc3 \\
        @deprecated >= 0.3.41, up for removal on 0.3.48

        An ABC with one method `__unicode__`, which equals invoking `unicode(self)` (Py2)
        """
        def __unicode__(self) -> str: ...

@runtime
class BinaryRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__bin__`, which equals invoking `bin(self)`.

    In reality there is no such magic method as `__bin__`, but I encourage \\
    Python working team to think about it.
    """
    def __bin__(self) -> str: ...

@runtime
class OctalRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__oct__`, which equals invoking `oct(self)`
    """
    def __oct__(self) -> str: ...

@runtime
class HexadecimalRepresentable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__hex__`, which equals invoking `hex(self)`
    """
    def __hex__(self) -> str: ...

@runtime
class StringConvertible(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__str__`, which equals invoking `str(self)`
    """
    def __str__(self) -> str: ...

@runtime
class Representable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__repr__`, which equals invoking `repr(self)`
    """
    def __repr__(self) -> str: ...

@runtime
class Indexable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__index__`. This allows to use self inside slice expressions, \\
    those are: `slice(self, ..., ...)` and `iterable[self: ... : ...]` (`self` can be \\
    placed anywhere)
    """
    def __index__(self) -> int: ...

@runtime
class Positive(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__pos__`, which equals `+self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __pos__(self) -> _T_cov: ...

@runtime
class Negative(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__neg__`, which equals `-self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __neg__(self) -> _T_cov: ...

@runtime
class Invertible(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__invert__`, which equals `~self`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __invert__(self) -> _T_cov: ...

BufferOperable = Buffer
"@lifetime >= 0.3.26rc1. *aveytense.types.Buffer*"

@runtime
class LeastComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `<`
    """
    def __lt__(self, other: _T_con) -> bool: ...

@runtime
class GreaterComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `>`
    """
    def __gt__(self, other: _T_con) -> bool: ...

@runtime
class LeastEqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `<=`
    """
    def __le__(self, other: _T_con) -> bool: ...

@runtime
class GreaterEqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Can be compared with `>=`
    """
    def __ge__(self, other: _T_con) -> bool: ...

@runtime
class EqualComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26rc1

    Can be compared with `==`
    """
    def __eq__(self, other: _T_con) -> bool: ...

@runtime
class InequalComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26rc1

    Can be compared with `!=`
    """
    def __ne__(self, other: _T_con) -> bool: ...


class Comparable(
    LeastComparable[Any],
    GreaterComparable[Any],
    LeastEqualComparable[Any],
    GreaterEqualComparable[Any],
    EqualComparable[Any],
    InequalComparable[Any],
    InComparable[Any]
):
    """
    @lifetime >= 0.3.26b3

    An ABC supporting any form of comparison with operators \\
    `>`, `<`, `>=`, `<=`, `==`, `!=`, `in` (last 3 missing before 0.3.26rc1)
    """
    ...

class ComparableWithoutIn(
    LeastComparable[Any],
    GreaterComparable[Any],
    LeastEqualComparable[Any],
    GreaterEqualComparable[Any],
    EqualComparable[Any]
):
    """
    @lifetime >= 0.3.27a2

    An ABC same as `Comparable`, but without the `in` keyword support
    """
    ...

@runtime
class BitwiseAndOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__and__`, which equals `self & other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __and__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__or__`, which equals `self | other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __or__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__xor__`, which equals `self ^ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __xor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__lshift__`, which equals `self << other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__rshift__`, which equals `self >> other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __lshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseOperable(
    BitwiseAndOperable[Any, Any],
    BitwiseOrOperable[Any, Any],
    BitwiseXorOperable[Any, Any],
    BitwiseLeftOperable[Any, Any],
    BitwiseRightOperable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&`, `|`, `^`, `<<` and `>>` operators
    """
    ...

@runtime
class BitwiseAndReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__iand__`, which equals `self &= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iand__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseOrReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ior__`, which equals `self |= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ior__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseXorReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ixor__`, which equals `self ^= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ixor__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseLeftReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__ilshift__`, which equals `self <<= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ilshift__(self, other: _T_con) -> _T_cov: ...

@runtime
class BitwiseRightReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__irshift__`, which equals `self >>= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __irshift__(self, other: _T_con) -> _T_cov: ...

class BitwiseReassignable(
    BitwiseAndOperable[Any, Any],
    BitwiseOrOperable[Any, Any],
    BitwiseXorOperable[Any, Any],
    BitwiseLeftReassignable[Any, Any],
    BitwiseRightReassignable[Any, Any]):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&=`, `|=`, `^=`, `<<=` and `>>=` operators
    """
    ...

class BitwiseCollection(
    BitwiseReassignable,
    BitwiseOperable
):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `&`, `|` and `^` operators, including their \\
    augmented forms: `&=`, `|=` and `^=`, with `~` use following::

        class Example(BitwiseCollection, Invertible[_T]): ...
    """
    ...

class UnaryOperable(Positive[Any], Negative[Any], Invertible[Any]):
    """
    @lifetime >= 0.3.26rc1

    Can be used with `+`, `-` and `~` operators preceding the type
    """
    ...

class Indexed(ItemGetter[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc2
    
    An ABC with one method `__getitem__`, which equals `self[key]`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `key` parameter.
    """
    ...

@runtime
class AsyncNextOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__anext__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __anext__(self) -> Awaitable[_T_cov]: ...

@runtime
class AsyncExitOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__aexit__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aexit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[TracebackType] = None) -> Awaitable[_T_cov]: ...

@runtime
class AsyncEnterOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__aenter__`. Returned type must be an awaitable \\
    of type represented by covariant type parameter.
    """
    async def __aenter__(self) -> Awaitable[_T_cov]: ...

@runtime
class ExitOperable(Protocol):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__exit__`. Returned type is addicted to covariant type parameter.
    """
    def __exit__(self, exc_type: Optional[type[Exception]] = None, exc_value: Optional[Exception] = None, traceback: Optional[TracebackType] = None) -> bool: ...

@runtime
class EnterOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__enter__`. Returned type is addicted to covariant type parameter.
    """
    def __enter__(self) -> _T_cov: ...

@runtime
class Ceilable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__ceil__`, which equals `ceil(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __ceil__(self) -> _T_cov: ...

@runtime
class Floorable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__floor__`, which equals `floor(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __floor__(self) -> _T_cov: ...

@runtime
class Roundable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__round__`, which equals `round(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __round__(self, ndigits: Optional[int] = None) -> _T_cov: ...

@runtime
class NextOperable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.26b3

    An ABC with magic method `__next__`, which equals `next(self)`. \\
    Returned type is addicted to covariant type parameter.
    """
    def __next__(self) -> _T_cov: ...

CeilOperable = Ceilable
FloorOperable = Floorable
RoundOperable = Roundable

@runtime
class AdditionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__add__`, which equals `self + other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __add__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__sub__`, which equals `self - other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __sub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__mul__`, which equals `self * other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__matmul__`, which equals `self @ other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __matmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__truediv__`, which equals `self / other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __truediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__floordiv__`, which equals `self // other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __floordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class DivmodOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__divmod__`, which equals `divmod(self, other)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter \\
    first is type for `other` parameter.
    """
    def __divmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__mod__`, which equals `self % other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __mod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__pow__`, which equals `self ** other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __pow__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedAdditionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__radd__`, which equals `other + self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __radd__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedSubtractionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rsub__`, which equals `other - self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rsub__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmul__`, which equals `other * self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedMatrixMultiplicationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmatmul__`, which equals `other @ self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedTrueDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rtruediv__`, which equals `other / self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rtruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedFloorDivisionOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rfloordiv__`, which equals `other // self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rfloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedDivmodOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rdivmod__`, which equals `divmod(other, self)`. \\
    Returned type is addicted to covariant type parameter as the second type parameter; \\
    first is type for `other` parameter.
    """
    def __rdivmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedModuloOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rmod__`, which equals `other % self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rmod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ReflectedExponentiationOperable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__rpow__`, which equals `other ** self`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __rpow__(self, other: _T_con) -> _T_cov: ...

@runtime
class AdditionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__iadd__`, which equals `self += other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __iadd__(self, other: _T_con) -> _T_cov: ...

@runtime
class SubtractionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__isub__`, which equals `self -= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __isub__(self, other: _T_con) -> _T_cov: ...

@runtime
class MultiplicationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imul__`, which equals `self *= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imul__(self, other: _T_con) -> _T_cov: ...

@runtime
class MatrixMultiplicationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imatmul__`, which equals `self @= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imatmul__(self, other: _T_con) -> _T_cov: ...

@runtime
class TrueDivisionReassingable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__itruediv__`, which equals `self /= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __itruediv__(self, other: _T_con) -> _T_cov: ...

@runtime
class FloorDivisionReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__ifloordiv__`, which equals `self //= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ifloordiv__(self, other: _T_con) -> _T_cov: ...

@runtime
class ModuloReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__imod__`, which equals `self %= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __imod__(self, other: _T_con) -> _T_cov: ...

@runtime
class ExponentiationReassignable(Protocol[_T_con, _T_cov]):
    """
    @lifetime >= 0.3.26rc1
    
    An ABC with magic method `__ipow__`, which equals `self **= other`. \\
    Returned type is addicted to covariant type parameter as the second \\
    type parameter; first is type for `other` parameter.
    """
    def __ipow__(self, other: _T_con) -> _T_cov: ...

class ReflectedArithmeticOperable(
    ReflectedAdditionOperable[Any, Any],
    ReflectedSubtractionOperable[Any, Any],
    ReflectedMultiplicationOperable[Any, Any],
    ReflectedMatrixMultiplicationOperable[Any, Any],
    ReflectedTrueDivisionOperable[Any, Any],
    ReflectedFloorDivisionOperable[Any, Any],
    ReflectedDivmodOperable[Any, Any],
    ReflectedModuloOperable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of reflected arithmetic operations with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    where left operand is `other` and right is `self`
    """
    ...

class ArithmeticOperable(
    AdditionOperable[Any, Any],
    SubtractionOperable[Any, Any],
    MultiplicationOperable[Any, Any],
    MatrixMultiplicationOperable[Any, Any],
    TrueDivisionOperable[Any, Any],
    FloorDivisionOperable[Any, Any],
    DivmodOperable[Any, Any],
    ModuloOperable[Any, Any],
    ExponentiationOperable[Any, Any],
    ReflectedArithmeticOperable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of arithmetic operations, including their \\
    reflected equivalents, with following operators:
    ```
        + - * @ / // % ** divmod
    ```
    Both `self` and `other` can be either left or right operands.
    """
    ...

class ArithmeticReassignable(
    AdditionReassignable[Any, Any],
    SubtractionReassignable[Any, Any],
    MultiplicationReassignable[Any, Any],
    MatrixMultiplicationReassignable[Any, Any],
    TrueDivisionReassingable[Any, Any],
    FloorDivisionReassignable[Any, Any],
    ModuloReassignable[Any, Any],
    ExponentiationReassignable[Any, Any]
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned arithmetic operations \\
    with following operators:
    ```
        += -= *= @= /= //= %= **=
    ```
    """
    ...

class ArithmeticCollection(
    ArithmeticOperable,
    ArithmeticReassignable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind (except bitwise) of augmented/re-assigned and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod += -= *= @= /= //= %= **=
    ```
    """
    ...

class OperatorCollection(
    ArithmeticCollection,
    BitwiseCollection,
    UnaryOperable,
    Comparable
):
    """
    @lifetime >= 0.3.26rc1

    An ABC supporting every kind of augmented/re-assigned, reflected and normal arithmetic operations \\
    with following operators:
    ```
        + - * @ / // % ** divmod & | ^ += -= *= @= /= //= %= **= &= |= ^=
    ```
    unary assignment with `+`, `-` and `~`, and comparison with following operators:
    ```
        > < >= <= == != in
    ```
    """
    ...

class LenGetItemOperable(LenOperable, ItemGetter[int, _T_cov]): # _typeshed.SupportsLenAndGetItem
    """
    @lifetime >= 0.3.26rc2
    
    An ABC with `__getitem__` and `__len__` methods. Those are typical in sequences.
    """
    ...

@runtime
class Formattable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    An ABC with one method `__format__`, which equals invoking `format(self)`.
    """
    def __format__(self, format_spec: str = "") -> str: ...

@runtime
class Flushable(Protocol): # _typeshed.SupportsFlush
    """
    @lifetime >= 0.3.27b1

    An ABC with one method `flush()`.
    """
    def flush(self) -> object: ...

@runtime
class Writeable(Protocol[_T_con]): # _typeshed.SupportsWrite
    """
    @lifetime >= 0.3.27b1

    An ABC with one method `write()`.
    """
    def write(self, s: _T_con, /) -> object: ...

@runtime
class Copyable(Protocol):
    """
    @lifetime >= 0.3.34
    
    An ABC with one method `__copy__`.
    """
    if _sys.version_info >= (0, 3, 43):
        def __copy__(self) -> Self: ...
    
    else:
        def copy(self) -> Self: ... 

@runtime
class DeepCopyable(Protocol):
    """
    @lifetime >= 0.3.43
    
    An ABC with one method `__deepcopy__`.
    """
    def __deepcopy__(self, memo: Optional[_AVT_Dict[int, Any]] = None) -> Self: ...
    
### NEGATIONS ###
    
@runtime
class NotIterable(Protocol):
    """
    @lifetime >= 0.3.26b3

    Cannot be used with `for` loop
    """
    __iter__ = None

@runtime
class NotCallable(Protocol[_T_cov]):
    """
    @lifetime >= 0.3.45

    Cannot be called as a function (as `self()`)
    """
    if _sys.version_info >= (0, 3, 45):
        __call__ = None
    
    else:
        def __call__(self, *args, **kwds):
            _E(107)
            
# NotInvocable = NotCallable # >= 0.3.26rc1; < 0.3.54

@runtime
class NotUnaryOperable(Protocol):
    """
    @lifetime >= 0.3.26rc1

    Cannot be used with preceding operators `+`, `-` and `~`
    """
    def __pos__(self):
        _E(108, "")
        
    def __neg__(self):
        _E(108, "")
        
    def __invert__(self):
        _E(108, "")

@runtime
class NotReassignable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    This class does not support any form of re-assignment, those are augmented \\
    assignment operators: `+=`, `-=`, `*=`, `**=`, `/=`, `//=`, `%=`, `>>=`, `<<=`, \\
    `&=`, `|=`, `^=`. Setting new value also is prohibited.
    """
    __slots__ = ("__weakref__",)
    __op = (
        "; used operator '+='", # 0
        "; used operator '-='", # 1
        "; used operator '*='", # 2
        "; used operator '/='", # 3
        "; used operator '//='", # 4
        "; used operator '**='", # 5
        "; used operator '<<='", # 6
        "; used operator '>>='", # 7
        "; used operator '%='", # 8
        "; used operator '&='", # 9
        "; used operator '|='", # 10
        "; used operator '^='", # 11
    )
    
    def __set__(self, i: Self, v: _T_con):
        
        s = " variable that isn't assignable and re-assignable"
        _E(102, s)
            
    def __iadd__(self, o: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __isub__(self, o: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __imul__(self, o: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ifloordiv__(self, o: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __idiv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __itruediv__(self, o: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __imod__(self, o: _T_con):
        i = 8
        _E(102, self.__op[i])
        
    def __ipow__(self, o: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __ilshift__(self, o: _T_con):
        i = 6
        _E(102, self.__op[i])
        
    def __irshift__(self, o: _T_con):
        i = 7
        _E(102, self.__op[i])
        
    def __iand__(self, o: _T_con):
        i = 9
        _E(102, self.__op[i])
        
    def __ior__(self, o: _T_con):
        i = 10
        _E(102, self.__op[i])
        
    def __ixor__(self, o: _T_con):
        i = 11
        _E(102, self.__op[i])

@runtime
class NotComparable(Protocol[_T_con]):
    """
    @lifetime >= 0.3.26b3

    Cannot be compared with operators `==`, `!=`, `>`, `<`, `>=`, `<=`, `in`
    """
    __slots__ = ()
    __op = (
        "; used operator '<'", # 0
        "; used operator '>'", # 1
        "; used operator '<='", # 2
        "; used operator '>='", # 3
        "; used operator '=='", # 4
        "; used operator '!='", # 5
        "; used operator 'in'", # 6
    )
    def __lt__(self, other: _T_con):
        i = 0
        _E(102, self.__op[i])
        
    def __gt__(self, other: _T_con):
        i = 1
        _E(102, self.__op[i])
        
    def __le__(self, other: _T_con):
        i = 2
        _E(102, self.__op[i])
        
    def __ge__(self, other: _T_con):
        i = 3
        _E(102, self.__op[i])
        
    def __eq__(self, other: _T_con):
        i = 4
        _E(102, self.__op[i])
        
    def __ne__(self, other: _T_con):
        i = 5
        _E(102, self.__op[i])
        
    def __contains__(self, other: _T_con):
        i = 6
        _E(102, self.__op[i])
    
class Allocator:
    """
    @lifetime >= 0.3.27b3

    An allocator class. Classes extending this class have access to `__alloc__` magic method, \\
    but it is advisable to use it wisely.
    """
    __a = bytearray()

    def __init__(self, b: Union[bytearray, BytearrayConvertible], /):
        
        if isinstance(b, BytearrayConvertible):
            self.__a = b.__bytearray__()
            
        elif isinstance(b, bytearray):
            self.__a = b
            
        else:
            error = TypeError("Expected a bytearray object or object of class extending 'BytearrayConvertible' class")
            raise error
    
    def __alloc__(self):
        return self.__a.__alloc__()
    
RichComparable = Union[LeastComparable[Any], GreaterComparable[Any]]

__all__ = sorted([k for k in globals() if not k.startswith("_")])
__abc__ = sorted([k for k in globals() if is_protocol(globals()[k])])
__all_deprecated__ = sorted([k for k in globals() if hasattr(globals()[k], "__deprecated__")]) # 0.3.44

if __name__ == "__main__":
    error = RuntimeError("Import-only module")
    raise error