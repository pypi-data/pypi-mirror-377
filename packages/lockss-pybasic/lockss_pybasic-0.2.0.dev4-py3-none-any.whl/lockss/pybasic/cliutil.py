#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Command line utilities.
"""

from collections.abc import Callable
import sys
from typing import Any, ClassVar, Dict, Generic, Optional, TypeVar, TYPE_CHECKING

from pydantic.v1 import BaseModel, PrivateAttr, create_model
from pydantic.v1.fields import FieldInfo
from pydantic_argparse import ArgumentParser
from pydantic_argparse.argparse.actions import SubParsersAction
from rich_argparse import RichHelpFormatter

if TYPE_CHECKING:
    from _typeshed import SupportsWrite as SupportsWriteStr
else:
    SupportsWriteStr = Any


class StringCommand(BaseModel):

    def display(self, file: SupportsWriteStr=sys.stdout) -> None:
        print(getattr(self, 'display_string'), file=file)

    @staticmethod
    def make(model_name: str, option_name: str, description: str, display_string: str):
        return create_model(model_name,
                            __base__=StringCommand,
                            **{option_name: (Optional[bool], FieldInfo(False, description=description)),
                               display_string: PrivateAttr(display_string)})


class CopyrightCommand(StringCommand):

    @staticmethod
    def make(display_string: str):
        return StringCommand.make('CopyrightCommand', 'copyright', 'print the copyright and exit', display_string)


class LicenseCommand(StringCommand):

    @staticmethod
    def make(display_string: str):
        return StringCommand.make('LicenseCommand', 'license', 'print the software license and exit', display_string)


class VersionCommand(StringCommand):

    @staticmethod
    def make(display_string: str):
        return StringCommand.make('VersionCommand', 'version', 'print the version number and exit', display_string)


BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


class BaseCli(Generic[BaseModelT]):
    """
    Base class for general CLI functionality.

    ``BaseModelT`` represents a Pydantic-Argparse model type deriving from
    ``BaseModel``.

    For each command ``x-y-z`` induced by a Pydantic-Argparse field named
    ``x_y_z`` deriving from ``BaseModel`` , the ``dispatch()`` method expects a
    method named ``_x_y_z``.
    """

    def __init__(self, **kwargs):
        """
        Constructs a new ``BaseCli`` instance.

        :param kwargs: Keyword arguments. Must include ``model``, the
                       ``BaseModel`` type corresponding to ``BaseModelT``. Must
                       include ``prog``, the command-line name of the program.
                       Must include ``description``, the description string of
                       the program.
        :type kwargs: Dict[str, Any]
        """
        super().__init__()
        self._args: Optional[BaseModelT] = None
        self._parser: Optional[ArgumentParser] = None
        self.extra: Dict[str, Any] = dict(**kwargs)

    def run(self) -> None:
        """
        Runs the command line tool:

        *  Creates a Pydantic-Argparse ``ArgumentParser`` with ``model``,
           ``prog`` and ``description`` from the constructor keyword
           arguments in ``self.parser``.

        *  Stores the Pydantic-Argparse parsed arguments in ``self.args``.

        *  Calls ``dispatch()``.
        """
        self._parser: ArgumentParser = ArgumentParser(model=self.extra.get('model'),
                                                      prog=self.extra.get('prog'),
                                                      description=self.extra.get('description'))
        self._initialize_rich_argparse()
        self._args = self._parser.parse_typed_args()
        self.dispatch()

    def dispatch(self) -> None:
        """
        Dispatches from the first field ``x_y_z`` in ``self._args`` that is a
        command (i.e. whose value derives from ``BaseModel``) to a method
        called ``_x_y_z``.
        """
        self._dispatch_recursive(self._args, [])

    def _dispatch_recursive(self, base_model: BaseModel, subcommands: list[str]) -> None:
        field_names = base_model.__class__.__fields__.keys()
        for field_name in field_names:
            field_value = getattr(base_model, field_name)
            if issubclass(type(field_value), BaseModel):
                self._dispatch_recursive(field_value, [*subcommands, field_name])
                return
        func_name = ''.join(f'_{sub}' for sub in subcommands)
        func = getattr(self, func_name)
        if callable(func):
            func(base_model) # FIXME?
        else:
            self._parser.exit(1, f'internal error: no {func_name} callable for the {" ".join(sub for sub in subcommands)} command')

    def _initialize_rich_argparse(self) -> None:
        """
        Initializes `rich-argparse <https://pypi.org/project/rich-argparse/>`_
        for this instance.
        """
        self._initialize_rich_argparse_styles()
        def __add_formatter_class(container):
            container.formatter_class = RichHelpFormatter
            if hasattr(container, '_actions'):
                for action in container._actions:
                    if issubclass(type(action), SubParsersAction):
                        for subaction in action.choices.values():
                            __add_formatter_class(subaction)
        __add_formatter_class(self._parser)

    def _initialize_rich_argparse_styles(self) -> None:
        # See https://github.com/hamdanal/rich-argparse#customize-the-colors
        for cls in [RichHelpFormatter]:
            cls.styles.update({
                'argparse.args': 'bold cyan',  # for positional-arguments and --options (e.g "--help")
                'argparse.groups': 'underline dark_orange',  # for group names (e.g. "positional arguments")
                'argparse.help': 'default',  # for argument's help text (e.g. "show this help message and exit")
                'argparse.metavar': 'italic dark_cyan',  # for metavariables (e.g. "FILE" in "--file FILE")
                'argparse.prog': 'bold grey50',  # for %(prog)s in the usage (e.g. "foo" in "Usage: foo [options]")
                'argparse.syntax': 'bold',  # for highlights of back-tick quoted text (e.g. "`some text`")
                'argparse.text': 'default',  # for descriptions, epilog, and --version (e.g. "A program to foo")
                'argparse.default': 'italic',  # for %(default)s in the help (e.g. "Value" in "(default: Value)")
            })


def at_most_one_from_enum(model_cls: type[BaseModel], values: Dict[str, Any], enum_cls) -> Dict[str, Any]:
    """
    Among the fields of a Pydantic-Argparse model whose ``Field`` definition is
    tagged with the ``enum`` keyword set to the given ``Enum`` type, ensures
    that at most one of them has a true value in the given Pydantic-Argparse
    validator ``values``, or raises a ``ValueError`` otherwise.

    :param model_cls: A Pydantic-Argparse model class.
    :param values:    The Pydantic-Argparse validator ``values``.
    :param enum_cls:  The ``Enum`` class the fields of the Pydantic-Argparse
                      model are tagged with (using the ``enum`` keyword).
    :return: The ``values`` argument, if no ``ValueError`` has been raised.
    """
    enum_names = [field_name for field_name, model_field in model_cls.__fields__.items() if model_field.field_info.extra.get('enum') == enum_cls]
    ret = [field_name for field_name in enum_names if values.get(field_name)]
    if (length := len(ret)) > 1:
        raise ValueError(f'at most one of {', '.join([option_name(model_cls, enum_name) for enum_name in enum_names])} allowed; got {length} ({', '.join([option_name(enum_name) for enum_name in ret])})')
    return values


def get_from_enum(model_inst, enum_cls, default=None):
    """
    Among the fields of a Pydantic-Argparse model whose ``Field`` definition is
    tagged with the ``enum`` keyword set to the given ``Enum`` type, gets the
    corresponding enum value of the first with a true value in the model, or
    returns the given default value. Assumes the existence of a
    ``from_member()`` static method in the ``Enum`` class.

    :param model_inst:
    :param enum_cls:
    :param default:
    :return:
    """
    enum_names = [field_name for field_name, model_field in type(model_inst).__fields__.items() if model_field.field_info.extra.get('enum') == enum_cls]
    for field_name in enum_names:
        if getattr(model_inst, field_name):
            return enum_cls[field_name]
    return default


def at_most_one(model_cls: type[BaseModel], values: Dict[str, Any], *names: str):
    if (length := _matchy_length(values, *names)) > 1:
        raise ValueError(f'at most one of {', '.join([option_name(model_cls, name) for name in names])} allowed; got {length}')
    return values


def exactly_one(model_cls: type[BaseModel], values: Dict[str, Any], *names: str):
    if (length := _matchy_length(values, *names)) != 1:
        raise ValueError(f'exactly one of {', '.join([option_name(model_cls, name) for name in names])} required; got {length}')
    return values


def one_or_more(model_cls: type[BaseModel], values: Dict[str, Any], *names: str):
    if _matchy_length(values, *names) == 0:
        raise ValueError(f'one or more of {', '.join([option_name(model_cls, name) for name in names])} required')
    return values


def option_name(model_cls: type[BaseModel], name: str) -> str:
    if (info := model_cls.__fields__.get(name)) is None:
        raise RuntimeError(f'invalid name: {name}')
    if alias := info.alias:
        name = alias
    return f'{('-' if len(name) == 1 else '--')}{name.replace('_', '-')}'


def _matchy_length(values: Dict[str, Any], *names: str) -> int:
    return len([name for name in names if values.get(name)])
