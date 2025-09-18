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
Created on 12/15/22

@author: irenab
"""
import sys
from typing import Optional

from uni.common.main import Converter
from uni.pytorch.version import __version__

COMPONENT = 'uni-pytorch'
FRAMEWORK = 'onnx'


def main(cmd_args: Optional[list] = None, setup_logging=True):
    # delay fw imports until after args parsing
    def parser_cls_getter():
        from uni.pytorch.onnx_parser.onnx_parser import OnnxParser
        return OnnxParser

    converter = Converter(parser_cls_getter, __version__, COMPONENT, FRAMEWORK)
    return converter.execute(cmd_args, setup_logging)


if __name__ == '__main__':
    # same behaviour as entry point in wheel
    sys.exit(main())
