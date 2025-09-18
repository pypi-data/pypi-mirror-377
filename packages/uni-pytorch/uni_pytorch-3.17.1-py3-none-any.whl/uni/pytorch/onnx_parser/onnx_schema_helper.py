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
Created on 9/7/22

@author: irenab
"""
from typing import Dict, List
from collections import defaultdict
from functools import lru_cache

import onnx
from onnx.defs import OpSchema

from .onnx_reader_helper import OnnxReaderHelper


class OnnxSchemaHelper:
    """ Used doc generation script for reference
        https://github.com/onnx/onnx/blob/main/onnx/defs/gen_doc.py """

    def __init__(self, supported_ops: list, opset_version: int):
        self.op_schemas: Dict[str, list] = self._get_ops_schemas(supported_ops)
        self.opset_version = opset_version

    @lru_cache(maxsize=None)
    def get_default_attrs(self, op, opset_version=None) -> Dict[str, OpSchema.Attribute]:
        if opset_version is None:
            assert self.opset_version
            opset_version = self.opset_version
        schema = self._get_op_schema_by_version(op, opset_version)
        default_values = {}
        for name, attr in schema.attributes.items():
            if attr.default_value and attr.default_value.name:
                default_values[name] = OnnxReaderHelper.read_attribute(attr.default_value)
        return default_values

    @staticmethod
    def _get_ops_schemas(supported_ops: list) -> Dict[str, List[OpSchema]]:
        """ get schemas (all revisions) for all ops that we support """
        ops: Dict[str, list] = defaultdict(list)
        for schema in onnx.defs.get_all_schemas_with_history():
            if schema.name in supported_ops:
                ops[schema.name].append(schema)
        return ops

    def _get_op_schema_by_version(self, op, opset_version=None) -> OpSchema:
        # return op schema with latest version <= opset_version
        if opset_version is None:
            assert self.opset_version
            opset_version = self.opset_version
        schemas = sorted(self.op_schemas[op], key=lambda s: s.since_version)
        schemas = [s for s in schemas if s.since_version <= opset_version]
        if not schemas:
            raise ValueError(f'Op {op} schema compatible with opset_version {opset_version} was not found')
        return schemas[-1]
