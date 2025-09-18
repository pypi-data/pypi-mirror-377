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
Created on 9/22/22

@author: irenab
"""
from enum import IntEnum
from typing import Tuple, Optional, Sequence

import numpy as np

from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.multigraph.node_graph_api import GraphRequest, ConstNodeCfg
from uni.common.core.nnir_graph.semantics import AxisSemantics, TensorSemantics
from .common import Param2d


class WeightsAndBiasNodeBase(NnirNode):
    """ Base node for nodes with [data, weight, bias] inputs """
    NUM_INPUTS = 3
    NUM_OUTPUTS = 1

    bias_semantics = TensorSemantics(AxisSemantics.OUT_CHANNELS)

    class InputsIndex(IntEnum):
        """ Inputs order for applicable Nnir nodes """
        DATA = 0
        WEIGHT = 1
        BIAS = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._weight_semantics: Optional[TensorSemantics] = None
        self._data_semantics: Optional[TensorSemantics] = None

    @property
    def weight_semantics(self):
        """ must be set by framework factory upon NnirNode creation """
        if self._weight_semantics is None:
            raise RuntimeError('weight_semantics was not set')
        return self._weight_semantics

    @weight_semantics.setter
    def weight_semantics(self, sem):
        self._weight_semantics = sem

    @staticmethod
    def zero_bias(out_channels: Optional[int] = None):
        """ By default, 0 bias is created as scalar. If out_channels is passed, a vector is created """
        size = 1 if out_channels is None else out_channels
        return np.zeros((size, ), dtype=np.float32)

    @classmethod
    def request_add_zero_bias(cls, node_name, out_channels) -> GraphRequest:
        """ convenience method for framework factories """
        const = ConstNodeCfg(node_name + '_bias', cls.zero_bias(out_channels))
        cfg = {int(cls.InputsIndex.BIAS): const}
        return GraphRequest(const_inputs_to_insert=cfg)

    @classmethod
    def validate_and_query_weights(cls,
                                   inputs_shapes: Sequence[tuple],
                                   weight_semantics: TensorSemantics,
                                   kernel_size: Optional[Param2d] = None,
                                   infer_kernel_size: bool = True) -> Tuple[bool, Tuple[int, int], Optional[Param2d]]:
        """ Validate that weights/bias shapes are consistent and match semantics
            Args:
                inputs_shapes: shapes of op's input tensors
                weight_semantics: semantics for weights tensors. See params below for supported AxisSemantics values
                kernel_size: if passed, weights' KERNEL_H, KERNEL_W is validated against it
                infer_kernel_size: if True and kernel_size is None, will try to infer from weights KERNEL_H, KERNEL_W

            Returns: boolean flag whether inputs contain bias,
                    a tuple of weights #out_channels, weights #in_channels
                    kernel_size - inferred kernel_size if infer_kernel_size is True, or just kernel_size arg value
        """
        assert len(inputs_shapes) in [2, 3]
        has_bias = len(inputs_shapes) == 3

        weight_shape = inputs_shapes[cls.InputsIndex.WEIGHT]

        def weight_axis_size(axis_sem) -> int:
            return weight_shape[weight_semantics.axis_by_semantics(axis_sem)]

        if kernel_size:
            assert weight_axis_size(AxisSemantics.KERNEL_H) == kernel_size.h
            assert weight_axis_size(AxisSemantics.KERNEL_W) == kernel_size.w
        elif infer_kernel_size:
            kernel_size = Param2d(weight_axis_size(AxisSemantics.KERNEL_H), weight_axis_size(AxisSemantics.KERNEL_W))

        w_out_channels = weight_axis_size(AxisSemantics.OUT_CHANNELS)
        w_in_channels = weight_axis_size(AxisSemantics.IN_CHANNELS)
        return has_bias, (w_out_channels, w_in_channels), kernel_size
