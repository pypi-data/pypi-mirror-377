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
Created on 6/24/24

@author: lotanw
"""
import json
import logging
import os
from pathlib import Path

from sdspconv_wrapper.main import main as sdspconv_main

from imx500_converter.converter.imx_cfg import ConverterCfg
from imx500_converter.converter.util.cli import split_cli_args


class SDSPConvRunner:
    # remap keys from ConvertCfg to sdspconv config
    REMAP_HYPHENATED_KEYS = {'output-dir': 'output', 'input-path': 'path'}
    IGNORE_HYPHENATED_KEYS_FOR_CFG = ['extra-sdspconv-args']

    UM_SUFFIX = '.um.pb'

    def run(self, cfg: ConverterCfg, uni_models_dir: str) -> int:
        cfg_path = os.path.join(uni_models_dir, 'sdspconv.cfg')
        self._build_dump_cfg(cfg, uni_models_dir, cfg_path)

        cli_args = f'--config {cfg_path} {cfg.extra_sdspconv_args}'

        logging.debug(f"running {sdspconv_main.__module__} {cli_args}")
        return sdspconv_main(split_cli_args(cli_args))

    def print_version(self, logger_level):
        sdspconv_main(split_cli_args(f'--version --logger-level {logger_level}'))

    def _build_dump_cfg(self, cfg: ConverterCfg, uni_models_dir: str, target_cfg_path: str) -> dict:
        cfg_dict = cfg.to_dict(hyphenated=True)
        for k in self.IGNORE_HYPHENATED_KEYS_FOR_CFG:
            del cfg_dict[k]

        cfg_dict = self._remapped_keys(cfg_dict)
        for i, net in enumerate(cfg_dict['networks']):
            net_name = Path(net['input-path']).stem
            net['path'] = self._find_uni_model(uni_models_dir, net_name)
            cfg_dict['networks'][i] = self._remapped_keys(net)

        with open(target_cfg_path, 'w') as f:
            json.dump(cfg_dict, f, indent=4)

        return cfg_dict

    @classmethod
    def _remapped_keys(cls, d: dict) -> dict:
        return {cls.REMAP_HYPHENATED_KEYS.get(k, k): v for k, v in d.items()}

    def _find_uni_model(self, uni_dir, net_name) -> str:
        uni_models = list(Path(uni_dir).glob(net_name + '*' + self.UM_SUFFIX))
        if len(uni_models) != 1:
            raise ConnectionError(f'Found {len(uni_models)} uni model files for network {net_name}, expected 1.')
        return str(uni_models[0])
