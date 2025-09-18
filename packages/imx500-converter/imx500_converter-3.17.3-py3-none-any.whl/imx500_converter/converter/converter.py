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
import argparse
import logging
import os
import re
import shutil
import sys
import tempfile
from typing import Callable, List, Optional

from imx500_converter.converter.util.error import ValidationErrors, ConverterError
from imx500_converter.converter.util.logger import setup_uni_logging, SDSPLoggerLevel, LoggerFormat
from imx500_converter.converter.imx_cfg import MemoryUnits, ConverterCfg, NetworkCfg

from imx500_converter import __version__
from imx500_converter.converter.imx_cfg_file_reader import CfgFileReader
from imx500_converter.converter.sdspconv_runner import SDSPConvRunner
from imx500_converter.converter.uni_converter_runner import UniConverterRunner

LOGGER_COMPONENT = "IMX"
CONTEXT_LOGGER_NAME = 'IMX'


class Converter:

    def __init__(self, uni_main: Callable, uni_entry_point: str):
        self.uniconv_runner = UniConverterRunner(uni_main, uni_entry_point)
        self.sdspconv_runner = SDSPConvRunner()

    def __call__(self, cli_args: Optional[List]):
        try:
            config = self._process_args(cli_args)

            self._setup_logging(config)

            uni_fw_out_dir = self._get_uni_out_dir(config.output_dir, config.keep_temp)
            ret = self.uniconv_runner.run(config, uni_fw_out_dir)
            if ret:
                return ret

            ret = self.sdspconv_runner.run(config, uni_fw_out_dir)
            if ret:
                logging.error(f'sdspconv exited with error code: {ret}, uni files can be found in {uni_fw_out_dir}')
            elif not config.keep_temp:
                shutil.rmtree(uni_fw_out_dir)
            return ret

        except ValidationErrors as e:
            for err in e.errors:
                logging.error(err)
        except ConverterError as e:
            logging.error(f'Convertion failed with: {e}')
        except Exception as e:
            logging.exception(e)
        return 1

    @staticmethod
    def _get_uni_out_dir(output_dir: str, keep_temp: bool) -> str:
        if keep_temp:
            os.makedirs(output_dir, exist_ok=True)
            uni_out_dir = output_dir
        else:
            uni_out_dir = tempfile.TemporaryDirectory().name
        return uni_out_dir

    @staticmethod
    def _setup_logging(cfg: ConverterCfg):
        context = cfg.logger_context or str(os.getpid())
        setup_uni_logging(logger_name=CONTEXT_LOGGER_NAME,
                          logger_level=SDSPLoggerLevel(cfg.logger_level),
                          logger_format=LoggerFormat(cfg.logger_format),
                          context=context,
                          component=LOGGER_COMPONENT,
                          component_suffix=None)

    def _process_args(self, cli_args: Optional[List]) -> ConverterCfg:
        p = self._setup_parser()
        args = self._parse_args(p, cli_args)
        cfg = self._convert_args(args)
        return cfg

    # yapf: disable
    # flake8: noqa
    def _validate_extra_sdspconv_args(self, args_str):
        '''
            '^' -                                           matches from start
            '$' -                                           matches till end
            '|' -                                           matches two possible cases
            '[a-zA-Z]' -                                    matches English letters
            '[a-zA-Z0-9]' -                                 matches both English letters and numbers

            declaring next pattern as VALUE_PATTERN
            ([ ]([a-zA-Z0-9]+|['][a-zA-Z0-9 ]+[']|["][a-zA-Z0-9 ]+["]))? -
                                                            value pattern
                                                            allows space followed by 1 word or many wrapped in string
                                                            marks, for example:
                                                            info
                                                            "target"
                                                            'target A'

            --[a-zA-Z]+(-[a-zA-Z]+)*VALUE_PATTERN -
                                                            expecting 2 dashes cases
                                                            for example:
                                                            --vis
                                                            --overwrite-output
                                                            --log-level info
                                                            --target "target"
                                                            --target 'target A'

            -[a-zA-Z]VALUE_PATTERN -
                                                            expecting 1 dash cases
                                                            for example:
                                                            "-v"
                                                            "-n 1"
                                                            -t "target"
                                                            -t 'target A'

            In the doc rows below I used "<>" to symbolize obligatory values, and "[]" for optional values.
            I used "*" to symbolize 0-inf repeats.
        '''

        value_pattern = (
            "("
                "[ ]"                           # space to indicate start of value
                "("
                    "[a-zA-Z0-9]+"              # matches one word
                    "|"                         # or
                    "['][a-zA-Z0-9 ]+[']"       # matches (') string with one or more words separated by spaces
                    "|"                         # or
                    "[\"][a-zA-Z0-9 ]+[\"]"     # matches (") string with one or more words separated by spaces
                ")"
            ")?"                                # matches 0-1 value patterns
        )
        pattern = (
            f"^"                                                    # matches start of line
                f"("
                    f"("
                        f"--[a-zA-Z]+(-[a-zA-Z]+)*{value_pattern}"  # matches --<word>[-word]* [space word]
                        f"|"                                        # or
                        f"-[a-zA-Z]{value_pattern}"                 # matches -<char> [space word]
                    f")"
                    f"[ ]?"
                f")*"
            f"$"                                                    # matches till end of line
        )
        if os.name == 'nt':
            if args_str.startswith('"') and args_str.endswith('"'):
                # remove quotes from start and end
                args_str = args_str[1:-1]
        return re.fullmatch(pattern, args_str)
    # yapf: enable
    # flake8: enable

    @staticmethod
    def _setup_parser() -> argparse.ArgumentParser:
        """
        Note: all defaults are set to None so that we can identify args that were and were not passed in cli, in order
        to be able to handle cli precedence over config file correctly.
        Defaults shown in help should be the actual default.
        """
        defaults = ConverterCfg.get_fields_info().defaults
        defaults['input_persistency'] = NetworkCfg.get_fields_info().defaults['input_persistency']

        p = argparse.ArgumentParser()

        # defined as a regular arg so that it can be used with logger-level to show sub-tools versions
        p.add_argument('-v', '--version', default=None, action='store_true')

        # required (mutually exclusive)
        p.add_argument('-c', '--config', default=None, help='Configuration file path')
        # -----------------------------------------------------------------------------
        p.add_argument('-i', '--input-path', default=None, help='Input network file path')
        p.add_argument('-o', '--output-dir', default=None, help='Output directory path')

        # optional
        p.add_argument('--overwrite-output',
                       default=None,
                       action='store_true',
                       help='Allow overwriting of existing files in output-dir. By default, an error will be raised')

        p.add_argument('--report-size-unit',
                       default=None,
                       type=str,
                       choices=MemoryUnits.values(),
                       help=f'Units of memory size in memory report. Default: {defaults["report_size_unit"]}')
        p.add_argument('--memory-report',
                       default=None,
                       action='store_true',
                       help='Produce memory report and dnnParams.xml file without converting the network')
        p.add_argument('--model-insight',
                       default=None,
                       action='store_true',
                       help='Produce model insight files. Experimental feature')
        group_input_persistency = p.add_mutually_exclusive_group(required=False)
        group_input_persistency.add_argument('--input-persistency',
                                             dest='input_persistency',
                                             default=None,
                                             action='store_true',
                                             help=f'Enable input persistency during inference '
                                             f'{"(default)" if defaults["input_persistency"] else ""}')
        group_input_persistency.add_argument('--no-input-persistency',
                                             dest='input_persistency',
                                             default=None,
                                             action='store_false',
                                             help=f'Disable input persistency during inference '
                                             f'{"(default)" if not defaults["input_persistency"] else ""}')

        group_logger = p.add_argument_group(title='Logging options')
        group_logger.add_argument('--logger-format',
                                  default=None,
                                  type=str,
                                  choices=LoggerFormat.values(),
                                  help=f'The format of the logging output. Default: {defaults["logger_format"]}')
        group_logger.add_argument(
            '--logger-level',
            default=None,
            type=str,
            choices=SDSPLoggerLevel.values(),
            help=f'Set the verbosity level of the application. Default: {defaults["logger_level"]}')
        group_logger.add_argument('--logger-context', default=None, help=argparse.SUPPRESS)

        # suppressed
        p.add_argument('--keep-temp', default=None, action='store_true', help=argparse.SUPPRESS)
        p.add_argument('--extra-sdspconv-args', default=None, help=argparse.SUPPRESS)
        return p

    def _parse_args(self, parser: argparse.ArgumentParser, cli_args: Optional[List] = None) -> argparse.Namespace:
        """
        uni_exec: the name of uni-converter executable to use for obtaining its version
        """
        args = parser.parse_args(cli_args) if cli_args else parser.parse_args()

        if args.version:
            print(f"{parser.prog} {__version__}")
            sys.stdout.flush()

            if args.logger_level in [SDSPLoggerLevel.DEBUG, SDSPLoggerLevel.TRACE]:
                self.uniconv_runner.print_version()
                self.sdspconv_runner.print_version(logger_level=args.logger_level)
            parser.exit(0)

        if args.config:
            if args.input_path or args.output_dir:
                parser.error('Cannot use both configuration file and direct input/output.\n'
                             'Either use: -i/--input-path and -o/--output-dir for single conversion '
                             'or use: -c/--config to specify a configuration file.')
            # NOTE!!! if this changes or any cli flag needs to override network flags, need to update _convert_args
            if args.input_persistency is not None:
                parser.error('Cannot use --input-persistency / --no-input-persistency with a configuration file. '
                             'Please specify in the configuration file which network should run with this flag.')
        else:
            if args.input_path is None or args.output_dir is None:
                parser.error('Either use: -i/--input-path and -o/--output-dir for single conversion '
                             'or use: -c/--config to specify a configuration file.')

        if args.extra_sdspconv_args:
            # remove spaces from start and end
            args_str = args.extra_sdspconv_args.strip()
            # remove excess spaces in args
            args_str = re.sub(r'\s+', ' ', args_str)
            if not self._validate_extra_sdspconv_args(args_str):
                parser.error(f'Found invalid extra-sdspconv-args:\n {args.extra_sdspconv_args}')

        return args

    @staticmethod
    def _convert_args(args: argparse.Namespace) -> ConverterCfg:
        # filter args that were explicitly passed
        passed_cli_args = {k: v for k, v in vars(args).items() if v is not None and k not in ['version', 'config']}
        if args.config:
            cfg: ConverterCfg = CfgFileReader(args.config).parse()
            # override top level args (network args from cli is not currently allowed)
            cfg = cfg.updated(**passed_cli_args)
        else:
            net_kwargs = {}
            if args.input_persistency is not None:
                net_kwargs = {'input_persistency': args.input_persistency}
                del passed_cli_args['input_persistency']
            network = NetworkCfg(input_path=passed_cli_args.pop('input_path'), ordinal=0, **net_kwargs)
            cfg = ConverterCfg(networks=[network], **passed_cli_args)
        return cfg
