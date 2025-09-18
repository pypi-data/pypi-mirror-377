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
Created on 7/10/24

@author: irenab
"""
import logging
import sys
from pathlib import Path
from typing import Callable
import subprocess as sp

from imx500_converter.converter.imx_cfg import ConverterCfg
from imx500_converter.converter.util.cli import split_cli_args
from imx500_converter.converter.util.logger import pause_logging


class UniConverterRunner:
    # tiresome black list so that we don't silently ignore new keys
    IGNORE_KEYS_FOR_CLI = [
        'networks', 'output_dir', 'overwrite_output', 'report_size_unit', 'memory_report', 'model_insight', 'keep_temp',
        'extra_sdspconv_args'
    ]

    def __init__(self, uni_main: Callable, uni_entry_point: str):
        self.uni_main = uni_main
        self.uni_entry_point = uni_entry_point

    def run(self, cfg: ConverterCfg, uni_out_dir: str) -> int:
        for network_cfg in cfg.networks:
            # make sure the input path has wrapper quotes in case it contains spaces
            # note that is " not ' since single quotes are not supported by the windows command line
            cli_args = f'--input-path "{network_cfg.input_path}" --output-dir "{uni_out_dir}" '
            cli_args += cfg.to_cli_args(exclude_fields=self.IGNORE_KEYS_FOR_CLI)
            logging.debug(f'running {self.uni_main.__module__} {cli_args}')
            with pause_logging():
                ret_code = self.uni_main(split_cli_args(cli_args))
            # even if one conversion fails, the flow stops
            if ret_code:
                return ret_code
        return 0

    def print_version(self):
        # run via entry point to get the correct name of the executable
        try:
            sp.run([self.uni_entry_point, '--version'], check=True)
        except FileNotFoundError:
            # if uni entry point is not found, it may not be in PATH. Try the full path in the python environment
            # bin directory. This can happen when running inside PyCharm, but should never happen from shell.
            sp.run([str(Path(sys.executable).parent / self.uni_entry_point), '--version'])
