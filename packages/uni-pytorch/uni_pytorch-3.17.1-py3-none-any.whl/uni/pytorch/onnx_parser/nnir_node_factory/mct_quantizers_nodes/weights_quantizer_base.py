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
import abc

from uni.common.core.error import OpOutputErrorInfo, raise_op_error
from . import OnnxMctFactoryBase


class WeightsQuantizerBase(OnnxMctFactoryBase, abc.ABC):

    @classmethod
    def validate_out_op_type(cls, graph_ctx, onnx_node):
        errors = []
        op_type_list = [
            'Add', 'Concat', 'Conv', 'ConvTranspose', 'Div', 'Expand', 'Gather', 'GatherElements', 'Gemm', 'MatMul',
            'Max', 'Min', 'Mul', 'Sub', 'Unsqueeze'
        ]
        out_nodes = graph_ctx.get_out_nodes()[0]
        for i, out_node in enumerate(out_nodes):
            out_node_op_type = out_node.op_type
            if out_node_op_type not in op_type_list:
                errors.append(
                    OpOutputErrorInfo(output_index=i,
                                      output_name='quantized data',
                                      reason=cls.get_out_type_err_msg(onnx_node.op_type, out_node_op_type)))
        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

    @staticmethod
    def get_out_type_err_msg(from_node_op_type: str, to_node_op_type: str):
        return f"{from_node_op_type} output can't be connected to {to_node_op_type}"
