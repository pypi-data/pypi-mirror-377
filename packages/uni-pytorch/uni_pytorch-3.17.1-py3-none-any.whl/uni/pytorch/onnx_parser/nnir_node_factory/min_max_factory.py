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
"""
Created on 9/21/23

@author: lotanw
"""
from abc import ABC
from typing import Sequence

from uni.common.core.error import raise_incorrect_number_of_inputs
from uni.pytorch.onnx_parser import OnnxMetaNode
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase


class MinMaxFactory(OnnxFactoryBase, ABC):
    incorrect_number_of_inputs_error_msg = 'Only binary op is supported'

    @classmethod
    def validate_num_inputs(cls, graph_ctx, onnx_node):
        in_nodes: Sequence[OnnxMetaNode] = graph_ctx.get_in_nodes()
        if len(in_nodes) != 2:
            raise_incorrect_number_of_inputs(cls.onnx_op_info(onnx_node),
                                             expected_num_inputs=[2],
                                             actual_num_inputs=len(in_nodes),
                                             reason=cls.incorrect_number_of_inputs_error_msg,
                                             history=None)
