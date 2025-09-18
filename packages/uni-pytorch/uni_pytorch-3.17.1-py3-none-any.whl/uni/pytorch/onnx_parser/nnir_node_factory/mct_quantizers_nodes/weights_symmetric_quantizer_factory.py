# -------------------------------------------------------------------------------
# (c) Copyright 2023 Sony Semiconductor Israel, Ltd. All rights reserved.
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
from typing import Sequence, Tuple

from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_nodes import Variable
from uni.common.core.nnir_graph.quant_info import SymmetricPerChannelQuantInfo, SymmetricQuantInfo
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import validate_onnx
from .weights_quantizer_base import WeightsQuantizerBase


class WeightsSymmetricQuantizerToNnirNode(WeightsQuantizerBase):

    @classmethod
    @validate_onnx(num_inputs=2,
                   num_outputs=1,
                   attrs=['mctq_version', 'channel_axis', 'num_bits', 'per_channel', 'signed'])
    def from_onnx(cls, onnx_node: OnnxMetaNode, graph_ctx) -> Tuple[Variable, GraphRequest]:
        cls.validate_out_op_type(graph_ctx, onnx_node)
        channel_axis = onnx_node.get_attr('channel_axis')
        signed = bool(onnx_node.get_attr('signed'))
        num_bits = onnx_node.get_attr('num_bits')
        per_channel = bool(onnx_node.get_attr('per_channel'))
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        threshold_np_array = in_nodes[1].get_const_data()
        if per_channel:
            thresholds: Tuple[float] = tuple(threshold_np_array.tolist())
            quant_info = SymmetricPerChannelQuantInfo(axis=channel_axis,
                                                      thresholds=thresholds,
                                                      value_n_bits=num_bits,
                                                      signed=signed)
        else:
            assert len(threshold_np_array) == 1
            threshold: float = float(threshold_np_array[0])
            quant_info = SymmetricQuantInfo(threshold=threshold, value_n_bits=num_bits, signed=signed)    # type: ignore
        data = in_nodes[0].get_const_data()
        return Variable(name=onnx_node.name, data=data, quant_info=quant_info), GraphRequest(inputs_to_detach=[0, 1])
