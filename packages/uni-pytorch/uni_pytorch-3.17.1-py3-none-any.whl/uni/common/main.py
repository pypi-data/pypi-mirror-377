# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 8/6/22

@author: irenab
"""
from typing import Type, Optional, Callable
import argparse
from pathlib import Path
import sys
import os
import abc

from uni.common.core.nnir_graph.nnir_substitution import SubstitutionManager
from uni.common.exporters.uni_model.uni_model_exporter import UniModelExporter
from uni.common.logger import setup_uni_logging, SDSPLoggerLevel, LoggerFormat, MessageCodes
from uni.common.util.dev import is_dev
from uni.common.core.error.defs import UnsupportedOpsError, InvalidOpsError, UnsupportedModelInputError
from uni.common.exit_code import ExitCode
from uni.common.util.vis import MultigraphVis    # type: ignore
from uni.common.core.uid_generator import UIDGenerator
from uni.common.parsers.base_parser import BaseParser
from uni.common.logger import get_logger

logger = get_logger(__name__)

CONTEXT_LOGGER_NAME = 'uni-converter'


class VersionAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        print(f"{parser.prog} {parser.converter_version}")

        # Manually extract the logger_level value from sys.argv
        logger_level = self.get_argument_value("--logger-level")
        if logger_level in [SDSPLoggerLevel.DEBUG.value, SDSPLoggerLevel.TRACE.value]:
            from uni_model.version import __version__ as uni_version
            print(f"uni-model {uni_version}")

        exit(0)

    def get_argument_value(self, arg_name):
        """Extracts the value of an argument from sys.argv."""
        if arg_name in sys.argv:
            index = sys.argv.index(arg_name)
            if index + 1 < len(sys.argv):
                return sys.argv[index + 1]
        return None


class Converter(abc.ABC):

    def __init__(self, parser_cls_getter: Callable[[], Type[BaseParser]], version: str, component: str,
                 framework_name: str):
        self._parser_cls_getter = parser_cls_getter
        self.version = version
        self.component = component
        self.framework_name = framework_name

    def get_parser(self, model_path, vis_dir) -> BaseParser:
        return self._parser_cls_getter()(model_path, vis_dir)

    def convert_model(self, model_path, vis_dir=None):

        parser = self.get_parser(model_path, vis_dir)
        parser.validate_metadata()
        nnir_graph = parser.parse()
        self.validate_and_dump_vis(nnir_graph, vis_dir, 'initial_nnir_graph.json')

        substitution_manager = SubstitutionManager(nnir_graph, vis_dir)
        substitution_manager.substitute()

        nnir_graph.set_semantics_on_nodes()
        self.validate_and_dump_vis(nnir_graph, vis_dir, 'after_set_semantics.json', allow_disconnected_outputs=True)
        metadata = parser.get_metadata()
        return nnir_graph, metadata

    @staticmethod
    def validate_and_dump_vis(graph, vis_dir: Optional[Path], file_name, allow_disconnected_outputs=False):
        if vis_dir:    # pragma: no cover
            MultigraphVis.dump_vis_json(graph, vis_dir / file_name)
        graph.validate_graph(allow_disconnected_outputs=allow_disconnected_outputs)

    def parse_args(self, cmd_args=None):
        p = argparse.ArgumentParser()
        # set the version to pass to VersionAction
        p.converter_version = self.version    # type: ignore
        p.add_argument('-i', '--input-path', type=Path, required=True, help='Input network file')
        p.add_argument('-o', '--output-dir', type=Path, required=True, help='Output directory')
        p.add_argument('-v', '--version', action=VersionAction, nargs=0, help="Show program's version number and exit")
        p.add_argument('--vis', action='store_true', help=argparse.SUPPRESS)

        group = p.add_argument_group(title='Logging options')
        group.add_argument('--logger-format',
                           type=LoggerFormat,
                           choices=LoggerFormat.values(),
                           default=LoggerFormat.TEXT.value,
                           help='The format of the logging output. Default: %(default)s')
        group.add_argument('--logger-level',
                           type=SDSPLoggerLevel,
                           choices=SDSPLoggerLevel.values(),
                           default='info',
                           help='Set the verbosity level of the application. Default: %(default)s')
        group.add_argument('--logger-context', help='Context for the logger. Default: input file name + PID')
        group.add_argument('--logger-component-suffix', help='Suffix for the logger component name')

        if cmd_args:
            args = p.parse_args(cmd_args)
        else:
            args = p.parse_args()    # pragma: no cover
        args.input_path = Path(self.remove_quate(str(args.input_path)))
        args.output_dir = Path(self.remove_quate(str(args.output_dir)))
        return args

    @staticmethod
    def remove_quate(s: str) -> str:
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s

    def execute(self, cmd_args: Optional[list] = None, setup_logging=True):
        """ This function is used for entry point executable in wheel
            It expects to receive the exit code as return value from the function it wraps.
            Any error that we want to intercept should be handled here

            cmd_args: command line arguments as a list (not including the executable)
        """

        # TODO handle arg validation + dir creation/overriding
        try:
            args = self.parse_args(cmd_args)

            if setup_logging:
                self.setup_logging(args)

            # reset global uid generator (simplifies tests running from the same process)
            UIDGenerator.reset()

            vis_dir = args.output_dir / 'vis' if args.vis else None

            logger.info(f'Running version {self.version}')
            cmd_args = [__file__] + cmd_args if cmd_args else sys.argv
            logger.debug(f'cmd agrs: {" ".join(cmd_args)}')
            logger.info(f'Converting {args.input_path}')
            if not os.path.exists(args.input_path):
                raise RuntimeError(f'Input file {args.input_path} does not exist')
            if not os.path.isfile(args.input_path):
                raise RuntimeError(f'Input file {args.input_path} is not a file')
            g, metadata = self.convert_model(args.input_path, vis_dir)
            graph_id = os.path.splitext(os.path.basename(args.input_path))[0]
            metadata["framework_name"] = self.framework_name
            UniModelExporter.export(graph_id=graph_id,
                                    component_name=self.component,
                                    g=g,
                                    out_dir=args.output_dir,
                                    metadata=metadata)
        except UnsupportedModelInputError as e:
            logger.error(e.reason, message_code=MessageCodes.INVALID_MODEL)
            return ExitCode.INVALID_MODEL_INPUT
        except UnsupportedOpsError as e:
            logger.error(f'The network contains unsupported ops: {", ".join(e.ops)}',
                         message_code=MessageCodes.UNSUPPORTED_OPS)
            return ExitCode.UNSUPPORTED_OPS
        except InvalidOpsError as e:
            msg = "The network is not aligned with SDSP converter's restrictions. Errors are:\n"
            msg += f'\n{"-"*50}\n'.join(str(op) for op in e.ops)
            logger.error(msg, message_code=MessageCodes.INVALID_OPS)
            return ExitCode.INVALID_OPS
        except Exception as e:    # pragma: no cover
            logger.exception(e, message_code=MessageCodes.EXECUTION)
            logger.error(str(e), message_code=MessageCodes.EXECUTION)
            return ExitCode.EXECUTION_ERROR

        logger.info('Converted successfully')
        return ExitCode.SUCCESS

    def setup_logging(self, args):
        level = 'debug' if is_dev() else args.logger_level
        context = args.logger_context or f'{Path(args.input_path).name}-{os.getpid()}'
        setup_uni_logging(logger_name=CONTEXT_LOGGER_NAME,
                          logger_level=SDSPLoggerLevel(level),
                          logger_format=args.logger_format,
                          context=context,
                          component=self.component,
                          component_suffix=args.logger_component_suffix)
