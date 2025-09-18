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
from enum import IntEnum
import numpy as np
from .nnir_node import NnirNode


class BatchNorm(NnirNode):
    NUM_INPUTS = 3
    NUM_OUTPUTS = 1

    def __init__(self, name, axis):
        super().__init__(name)
        self.axis = axis

    class Inputs(IntEnum):
        Data = 0
        A = 1
        B = 2

    def export_uni_model(self):
        from uni_model import UniLayerBatchNorm
        return UniLayerBatchNorm(self.name, out_dtypes=self.get_uni_model_out_dtypes(), axis=self.axis)

    @staticmethod
    def get_a_b(gamma, beta, mean, variance, epsilon):
        """
        This function converts the parameters of batchnorm from the framework to a and b
        Batchnorm returns: gamma * (batch - moving_mean) / sqrt(moving_var+epsilon) + beta

        Parameters:
        gamma (vector): gamma or weight (TF\torch) from framework
        beta (vector): beta or bias (TF\torch) from framework
        mean (vector): moving_mean or running_mean (TF\torch)
        variance (vector): moving_var or running_var (TF\torch)
        epsilon: epsilon from fw

        Returns:
        a,b (vectors) such that a*x + b = gamma * (batch - moving_mean) / sqrt(moving_var+epsilon) + beta
        """
        a = gamma / np.sqrt(variance + epsilon)
        b = beta - mean * a

        return a, b
