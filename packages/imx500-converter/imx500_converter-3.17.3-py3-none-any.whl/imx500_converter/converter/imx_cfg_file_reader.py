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
Created on 7/3/24

@author: lotanw
"""
import json
from typing import Type, List

from .imx_cfg import ConverterCfg, NetworkCfg, CfgBase
from .util.error import ValidationErrors, ConverterError
from .util.keys_case import with_dehyphenated_flat_keys


class CfgFileReader:
    SCHEMA_VERSION_FIELD = 'schema-version'
    DEFAULT_SCHEMA_VERSION = '1'
    SCHEMA_VERSIONS = [DEFAULT_SCHEMA_VERSION]

    def __init__(self, cfg_file):
        self.cfg_file = cfg_file

    def parse(self):
        config_data = self._load_config_file(self.cfg_file)

        # de-hypenate top-level keys
        config_data = with_dehyphenated_flat_keys(config_data)

        self._validate_schema(config_data)
        if self.SCHEMA_VERSION_FIELD in config_data:
            del config_data[self.SCHEMA_VERSION_FIELD]

        # Here we only validate the fields names so that we can build ConverterCfg. It validatess the rest
        # validate top-level keys
        errors = self._validate_fields(config_data, ConverterCfg)
        if 'networks' not in config_data:
            raise ValidationErrors(errors)
        # de-hypenate and validate networks' inner keys
        networks = config_data.pop('networks')
        networks = [with_dehyphenated_flat_keys(net) for net in networks]
        for i, net in enumerate(networks):
            errors.extend(self._validate_fields(net, NetworkCfg, desc=f'for network index {i}'))

        if errors:
            raise ValidationErrors(errors)

        network_cfgs = [NetworkCfg(**net) for net in networks]

        return ConverterCfg(networks=network_cfgs, **config_data)

    @staticmethod
    def _load_config_file(cfg_path):    # , gen_template_flag: str=None):
        try:
            with open(cfg_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConverterError(f'Failed to load the config file {cfg_path} with {type(e).__name__}: {str(e)}. ')

    @classmethod
    def _validate_schema(cls, cfg_file_content):
        schema_ver = cfg_file_content.get(cls.SCHEMA_VERSION_FIELD, cls.DEFAULT_SCHEMA_VERSION)

        if schema_ver not in cls.SCHEMA_VERSIONS:
            raise ValidationErrors([f'Unknown schema version {schema_ver}. Available versions {cls.SCHEMA_VERSIONS}'])

    @staticmethod
    def _validate_fields(cfg_file_content, cfg_cls: Type[CfgBase], desc='') -> List[str]:
        fields_info = cfg_cls.get_fields_info()
        missing_fields = [f for f in fields_info.mandatory if f not in cfg_file_content]
        unknown_fields = [k for k in cfg_file_content if k not in fields_info.mandatory + fields_info.optional]
        errors = []
        for f in missing_fields:
            errors.append(f'Missing mandatory field "{f}" {desc}')
        for f in unknown_fields:
            errors.append(f'Unknown field "{f}" {desc}')
        return errors
