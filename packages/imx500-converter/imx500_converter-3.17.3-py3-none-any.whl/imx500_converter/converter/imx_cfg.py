# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in accordance with the terms of written
#      license agreement between you and the Company (the "License").
#      Except as expressly stated in the License, the Company grants no
#      licenses by implication, estoppel, or otherwise. If you are not
#      aware of or do not agree to the License terms, you may not use,
#      copy or modify the Software. You may use the source code of the
#      Software only for your internal purposes and may not distribute the
#      source code of the Software, any part thereof, or any derivative work
#      thereof, to any third party, except pursuant to the Company's prior
#      written consent.
#      The Software is the confidential information of the Company.
# -------------------------------------------------------------------------------
"""
Created on 7/8/24

@author: irenab
"""
import dataclasses
import os
from dataclasses import dataclass, fields, field, MISSING, asdict
from enum import Enum
from typing import List, Optional, Union, Type, get_origin, get_args, Dict, Tuple, NamedTuple

from .util.keys_case import with_hyphenated_flat_keys, hyphenate
from .util.logger import LoggerFormat, SDSPLoggerLevel
from .util.error import ValidationErrors


class MemoryUnits(str, Enum):
    B = 'B'
    KB = 'K'
    MB = 'M'
    HUMAN = 'H'

    @classmethod
    def values(cls):
        return [v.value for v in cls]


class FieldsInfo(NamedTuple):
    mandatory: list
    optional: list
    defaults: dict


@dataclass
class CfgBase:

    @classmethod
    def get_fields_info(cls) -> 'FieldsInfo':
        """  Obtains fields info from dataclass definition """
        mandatory = []
        defaults = {}

        for f in fields(cls):
            if f.default is not MISSING:
                defaults[f.name] = f.default
            elif f.default_factory is not MISSING:
                defaults[f.name] = f.default_factory()
            else:
                mandatory.append(f.name)

        return FieldsInfo(mandatory=mandatory, optional=list(defaults.keys()), defaults=defaults)

    @classmethod
    def _get_types(cls) -> Dict[str, Union[Type, Tuple[Type, ...]]]:
        """ obtain fields' types """
        types = {}
        for f in fields(cls):
            origin = get_origin(f.type)
            args = get_args(f.type)
            if origin == Union:
                types[f.name] = tuple(args)
            elif origin is not None:
                # type hints like typing.List => origin=<class list>
                types[f.name] = (origin, )
            else:
                # regular python types
                types[f.name] = (f.type, )
        return types    # type: ignore[return-value]

    def validate_fields(self, hyphenate_err: bool, desc=None) -> List[str]:
        """
        Validate fields values type against their type hint.
        If field's metadata contains {'enum': EnumCls}, check the value is one of EnumCls values.

        Args:
            hyphenate_err: whether to change _ to - in field name in error
            desc: optional desc to add after error message.

        Returns:
            A list of errors
        """
        types = self._get_types()
        errors = []
        desc = (' ' + desc) if desc else ''
        for f in fields(self):
            val = getattr(self, f.name)
            _name = hyphenate(f.name) if hyphenate_err else f.name
            if not isinstance(val, types[f.name]):
                allowed_types = [t.__name__ for t in types[f.name]]
                errors.append(f'Invalid value type \'{type(val).__name__}\' for "{_name}"{desc}.'
                              f' Allowed types: {allowed_types}')
            if 'enum' in f.metadata:
                valid_values = [f.value for f in f.metadata['enum']]
                if val not in valid_values:
                    errors.append(f'Invalid value \'{val}\' for "{_name}"{desc}. Allowed values: {valid_values}')
        return errors

    def _to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ConverterCfg(CfgBase):
    """ IMX500 Converter configuration. This is not merely a container, but a (primitive)
        schema defining the converter's fields, types and default values.
        This class is agnostic to the source(s) of the configuration, but it provides 'updated' method for the sake
        of multiple sources.
        Validation is performed at instantiation and after each call to 'update'. It includes:
          - value type validation
          - str enum value validation
          - networks ordinals validation
    """
    # DO NOT MODIFY, INCLUDING TYPE HINTS (unless you kow what you are doing)
    networks: List['NetworkCfg']
    output_dir: str
    overwrite_output: bool = False
    report_size_unit: str = field(default=MemoryUnits.HUMAN.value, metadata={'enum': MemoryUnits})
    logger_level: str = field(default=SDSPLoggerLevel.INFO.value, metadata={'enum': SDSPLoggerLevel})
    logger_format: str = field(default=LoggerFormat.TEXT.value, metadata={'enum': LoggerFormat})
    logger_context: Optional[str] = None
    memory_report: bool = False
    model_insight: bool = False
    keep_temp: bool = False
    extra_sdspconv_args: str = ''

    def __post_init__(self):
        if self.logger_context is None:
            self.logger_context = str(os.getpid())
        self.validate()

    def updated(self, **kwargs) -> 'ConverterCfg':
        new = dataclasses.replace(self, **kwargs)
        new.validate()
        return new

    def validate(self, hyphenate_err=True):
        errors = self._validate_ordinals_with_default()
        errors.extend(self.validate_fields(hyphenate_err))
        for i, net in enumerate(self.networks):
            errors.extend(net.validate_fields(hyphenate_err, f'for network index {i}'))
        if errors:
            raise ValidationErrors(errors)

    def to_dict(self, hyphenated: bool):
        d = asdict(self)
        if hyphenated:
            d = with_hyphenated_flat_keys(d)
            for i, net in enumerate(d['networks']):
                d['networks'][i] = with_hyphenated_flat_keys(net)
        return d

    def to_cli_args(self, exclude_fields: List[str]) -> str:
        """ Build simple hyphenated cli args string
            Simple means "--key" for truthy bool and "--key val" otherwise. None values are ignored. """
        assert 'networks' in exclude_fields, 'cannot build cli for networks, pass it in exclude_fields'
        assert not (set(exclude_fields) - {f.name for f in fields(self)}), 'unknown field in exclude fields'
        cli = ''
        for f in fields(self):
            if f.name in exclude_fields:
                continue
            val = getattr(self, f.name)
            if val in [False, None]:
                continue
            arg = f' --{hyphenate(f.name)}'
            if val is True:
                cli += arg
            else:
                cli += f'{arg} {val}'
        return cli

    def _validate_ordinals_with_default(self) -> List:
        ordinals = [net.ordinal for net in self.networks if net.ordinal is not None]
        if not ordinals:
            for i, net in enumerate(self.networks):
                net.ordinal = i
            return []

        if len(ordinals) != len(self.networks):
            return ['Invalid ordinals: ordinals should be set for all networks, or none.']

        def is_valid(ordinal):
            return isinstance(ordinal, int) and 0 <= ordinal < 256

        if len(set(ordinals)) < len(self.networks) or not all(is_valid(o) for o in ordinals):
            return ['Invalid ordinals: expected unique integers between 0 and 255']
        return []


@dataclass
class NetworkCfg(CfgBase):
    input_path: str
    ordinal: Optional[int] = None
    input_persistency: bool = True
