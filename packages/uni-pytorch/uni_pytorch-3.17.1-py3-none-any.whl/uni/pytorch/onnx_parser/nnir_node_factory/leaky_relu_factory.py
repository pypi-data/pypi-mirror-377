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
from typing import Tuple, Optional

from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes import PRelu
from uni.common.core.multigraph.node_graph_api import GraphRequest


class OnnxLeakyReluToNnirNode(OnnxFactoryBase):

    @classmethod
    @validate_onnx(num_inputs=1, num_outputs=1, attrs=["alpha"])
    def from_onnx(cls, onnx_node, graph_ctx=None) -> Tuple[PRelu, Optional[GraphRequest]]:
        alpha = onnx_node.get_attr("alpha")
        request = PRelu.request_add_slope_const(onnx_node.name, alpha)
        node = PRelu(name=onnx_node.name)
        return node, request
