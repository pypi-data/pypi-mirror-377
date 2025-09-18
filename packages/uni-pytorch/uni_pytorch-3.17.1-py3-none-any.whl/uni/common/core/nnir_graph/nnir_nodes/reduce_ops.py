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
Created on 3/15/23

@author: irenab
"""
from typing import Sequence
import abc

from .nnir_node import NnirNode


class ReduceNodeBase(NnirNode, abc.ABC):
    NUM_INPUTS = 1
    NUM_OUTPUTS = 1

    def __init__(self, name, axes: Sequence[int], keepdims: bool, **kwargs):
        super().__init__(name, **kwargs)
        if isinstance(axes, int):
            axes = (axes, )
        self.axes = tuple(int(x) for x in axes)
        self.keepdims = keepdims

    def export_uni_model(self):
        return self._uni_model_kls(self.name,
                                   axes=list(self.axes),
                                   keep_dims=self.keepdims,
                                   out_dtypes=self.get_uni_model_out_dtypes())

    @property
    @abc.abstractmethod
    def _uni_model_kls(self):
        pass


class ReduceMean(ReduceNodeBase):

    @property
    def _uni_model_kls(self):
        from uni_model import UniLayerReduceMean
        return UniLayerReduceMean


class ReduceMax(ReduceNodeBase):

    @property
    def _uni_model_kls(self):
        from uni_model import UniLayerReduceMax
        return UniLayerReduceMax


class ReduceSum(ReduceNodeBase):

    @property
    def _uni_model_kls(self):
        from uni_model import UniLayerReduceSum
        return UniLayerReduceSum
