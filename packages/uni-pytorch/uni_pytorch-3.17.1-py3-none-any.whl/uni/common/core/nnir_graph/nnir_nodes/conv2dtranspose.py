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
Created on 5/10/23

@author: irenab
"""
from typing import List

from uni.common.core.nnir_graph.semantics import Semantics, SemanticsHelper, AxisSemantics
from uni.common.core.error import ParamErrorInfo, raise_op_error, ErrorInfo
from .common import Padding2d, Param2d
from .weights_bias_node_base import WeightsAndBiasNodeBase


class Conv2dTransposeBias(WeightsAndBiasNodeBase):
    invalid_dilation_error = 'Dilation > 1 is not supported'
    invalid_kernel_stride_error = 'Stride > kernel size is not supported'
    invalid_padding_error = 'Input padding is not supported'
    invalid_groups_error = 'Groups > 1 is not supported'

    def __init__(self, name, kernel_size: Param2d, stride: Param2d, dilation: Param2d, groups: int, pad: Padding2d,
                 out_pad: Param2d, **kwargs):
        super().__init__(name, **kwargs)
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.groups = groups
        self.pad = pad
        self.out_pad = out_pad

    def _validate(self):
        errors: List[ErrorInfo] = []
        if self.dilation != Param2d(1, 1):
            errors.append(ParamErrorInfo('dilation', self.dilation, self.invalid_dilation_error))

        if any(s > k for s, k in zip(self.stride, self.kernel_size)):
            errors.append(
                ParamErrorInfo('stride, kernel size', f'{self.stride}, {self.kernel_size}',
                               self.invalid_kernel_stride_error))

        if any(p for p in self.pad.h + self.pad.w):
            errors.append(ParamErrorInfo('padding', self.pad, self.invalid_padding_error))

        if self.groups > 1:
            errors.append(ParamErrorInfo('groups', self.groups, self.invalid_groups_error))

        ret = self.validate_data_dim_size(AxisSemantics.HEIGHT, upper_limit=self.max_2d_op_h_size, return_error=True)
        if ret:
            errors.append(ret)

        if errors:
            raise_op_error(self.op_info(), errors, self.history)

    def export_uni_model(self):
        from uni_model import UniLayerConv2DTranspose
        from uni.common.exporters.uni_model.uni_model_exporter import UniModelExporter
        weight_layout = UniModelExporter.tensor_semantics_to_layout(self.weight_semantics)
        layer = UniLayerConv2DTranspose(self.name,
                                        k_h=self.kernel_size[0],
                                        k_w=self.kernel_size[1],
                                        s_h=self.stride[0],
                                        s_w=self.stride[1],
                                        p_h_before=self.pad.h[0],
                                        p_h_after=self.pad.h[1],
                                        p_w_before=self.pad.w[0],
                                        p_w_after=self.pad.w[1],
                                        output_p_h_after=int(self.out_pad[0]),
                                        output_p_w_after=int(self.out_pad[1]),
                                        data_format=self.get_uni_model_input_data_layout(),
                                        weights_layout=weight_layout,
                                        out_dtypes=self.get_uni_model_out_dtypes())
        return layer

    def get_input_semantics(self, semantic_helper: SemanticsHelper) -> Semantics:
        return Semantics(semantic_helper.data_tensor_semantics(), self.weight_semantics, self.bias_semantics)

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        self.output_semantics = semantics_helper.node_data_semantics()
