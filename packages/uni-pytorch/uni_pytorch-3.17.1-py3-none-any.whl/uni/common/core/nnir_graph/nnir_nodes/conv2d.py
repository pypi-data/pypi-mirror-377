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
Created on 8/25/22

@author: irenab
"""
from typing import List

from .weights_bias_node_base import WeightsAndBiasNodeBase
from .common import Padding2d, Param2d
from uni.common.core.nnir_graph.semantics import Semantics, SemanticsHelper, AxisSemantics
from uni.common.core.error.defs import ParamErrorInfo
from uni.common.core.error.util import raise_op_error, ErrorInfo


class Conv2dBias(WeightsAndBiasNodeBase):
    NUM_OUTPUTS = 1

    error_invalid_pad_size = 'Padding >= kernel size is not supported'
    error_stride_and_dilation = 'Stride > 1 with dilation > 1 are not supported'
    error_invalid_grouped_dm = 'Non-integer depth multiplier (filter group size / input group size) is not supported ' \
                               'with group > 1'

    max_kernel_size_for_depthwise = 12
    error_invalid_kernel_for_depthwise = 'Kernel size > 12 is not supported for depthwise conv'

    def __init__(self, name, kernel_size: Param2d, stride: Param2d, dilation: Param2d, group: int, pad2d: Padding2d,
                 input_group_size: int, out_group_size: int, **kwargs):
        super().__init__(name, **kwargs)
        self.kernel_size = kernel_size
        self.stride = stride
        self.dilation = dilation
        self.groups = group
        self.pad = pad2d
        self.input_group_size = input_group_size
        self.out_group_size = out_group_size

    def _validate(self):
        errors: List[ErrorInfo] = []
        # stride and dilation cannot be both > 1
        if self.dilation > Param2d(1, 1) and self.stride > Param2d(1, 1):
            errors.append(
                ParamErrorInfo(name='stride, dilation',
                               value=f'{self.stride}, {self.dilation}',
                               reason=self.error_stride_and_dilation))

        # pad should be < dilated kernel_size
        dilated_kernel = Param2d(*[(k - 1) * d + 1 for k, d in zip(self.kernel_size, self.dilation)])
        if any(v >= dilated_kernel.h for v in self.pad.h) or any(v >= dilated_kernel.w for v in self.pad.w):
            errors.append(ParamErrorInfo(name='padding', value=self.pad, reason=self.error_invalid_pad_size))

        if self.input_group_size == 1 and any(k > self.max_kernel_size_for_depthwise for k in self.kernel_size):
            errors.append(
                ParamErrorInfo(name='kernel size',
                               value=self.kernel_size,
                               reason=self.error_invalid_kernel_for_depthwise))

        if self.groups > 1:
            errors.extend(self._validate_grouped_conv2d())

        # validate Hin/Hout size limit
        err = self.validate_data_dim_size(axis=AxisSemantics.HEIGHT,
                                          upper_limit=self.max_2d_op_h_size,
                                          return_error=True)
        if err:
            errors.append(err)

        if errors:
            raise_op_error(self.op_info(), errors=errors, history=self.history)

    def get_input_semantics(self, semantic_helper: SemanticsHelper) -> Semantics:
        return Semantics(semantic_helper.data_tensor_semantics(), self.weight_semantics, self.bias_semantics)

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        self.output_semantics = semantics_helper.node_data_semantics()

    def _validate_grouped_conv2d(self) -> List[ParamErrorInfo]:
        errors: List[ParamErrorInfo] = []
        if self.input_group_size == 1:
            # no limitations for depthwise grouped conv
            return errors

        if self.out_group_size % self.input_group_size:
            err = ParamErrorInfo(name='depth multiplier',
                                 value=f'{self.out_group_size}/{self.input_group_size}',
                                 reason=self.error_invalid_grouped_dm)
            errors.append(err)

        return errors

    def export_uni_model(self):
        from uni_model import UniLayerConv2D
        from uni.common.exporters.uni_model.uni_model_exporter import UniModelExporter
        return UniLayerConv2D(self.name,
                              k_h=self.kernel_size.h,
                              k_w=self.kernel_size.w,
                              s_h=self.stride.h,
                              s_w=self.stride.w,
                              p_h_before=self.pad.h[0],
                              p_h_after=self.pad.h[1],
                              p_w_before=self.pad.w[0],
                              p_w_after=self.pad.w[1],
                              rate0=self.dilation.h,
                              rate1=self.dilation.w,
                              group=self.groups,
                              data_format=self.get_uni_model_input_data_layout(),
                              weights_layout=UniModelExporter.tensor_semantics_to_layout(self.weight_semantics),
                              out_dtypes=self.get_uni_model_out_dtypes())
