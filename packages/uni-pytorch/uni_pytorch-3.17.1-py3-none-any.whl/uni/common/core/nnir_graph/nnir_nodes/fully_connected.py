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
Created on 11/16/22

@author: irenab
"""
from typing import List

from uni.common.core.nnir_graph.nnir_nodes.weights_bias_node_base import WeightsAndBiasNodeBase
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.error import raise_op_input_error, exceeds_limit_msg, OpInputErrorInfo, ParamErrorInfo, \
    raise_op_error, ErrorInfo


class FullyConnected(WeightsAndBiasNodeBase):
    NUM_INPUTS = 3
    NUM_OUTPUTS = 1

    invalid_input_shape_error = 'Only 2d input (N,D) or 4d (N, D0, D1, D2) input is supported'
    max_input_size = 32700
    max_num_output_features = 2**13
    invalid_input_size_error = exceeds_limit_msg('Input size', max_input_size)
    invalid_num_output_features_error = exceeds_limit_msg('Output size', max_num_output_features)

    def _validate(self):
        data_shape = self.graph_ctx.get_in_shapes()[0]
        in_node: NnirNode = self.graph_ctx.get_in_nodes()[0]
        if len(data_shape) not in [2, 4] or data_shape[0] not in self.valid_batch:
            # if input shape is wrong, the is no point to continue to other checks
            raise_op_input_error(self.op_info(),
                                 input_index=0,
                                 input_name=in_node.name,
                                 reason=self.invalid_input_shape_error,
                                 history=self.history)

        errors: List[ErrorInfo] = []
        if len(data_shape) == 2 and data_shape[-1] > self.max_input_size:
            errors.append(OpInputErrorInfo(input_index=0, input_name=in_node.name,
                                           reason=self.invalid_input_size_error))

        output_shape = self.graph_ctx.get_out_shapes()[0]
        if len(output_shape) == 2 and output_shape[-1] > self.max_num_output_features:
            errors.append(
                ParamErrorInfo(name='output features',
                               value=output_shape[-1],
                               reason=self.invalid_num_output_features_error))

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def export_uni_model(self):
        from uni_model import UniLayerFullyConnected
        from uni.common.exporters.uni_model.uni_model_exporter import UniModelExporter
        return UniLayerFullyConnected(self.name,
                                      weight_layout=UniModelExporter.tensor_semantics_to_layout(self.weight_semantics),
                                      out_dtypes=self.get_uni_model_out_dtypes())
