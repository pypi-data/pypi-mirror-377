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
Created on 1/31/24

@author: lotanw
"""

from uni.common.core.nnir_graph.nnir_nodes import TopKGather
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx


class OnnxGatherElementsToNnirNode(OnnxFactoryBase):
    """ https://github.com/onnx/onnx/blob/main/docs/Operators.md#GatherElements """

    @classmethod
    @validate_onnx(num_inputs=2, num_outputs=1, attrs=[], optional_attrs=["axis"])
    def from_onnx(cls, onnx_node, graph_ctx=None) -> TopKGather:
        axis = onnx_node.get_attr_with_default_from_schema("axis")
        return TopKGather(name=onnx_node.name, axis=axis)
