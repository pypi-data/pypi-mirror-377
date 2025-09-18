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
import numpy as np

from . import NnirNode
from uni.common.core.multigraph.node_graph_api import GraphRequest


class PRelu(NnirNode):
    NUM_INPUTS = 2
    NUM_OUTPUTS = 1

    @staticmethod
    def request_add_slope_const(node_id, slope):
        """ Convenience function for fw factories that need to add slope input from attribute """
        return GraphRequest.request_insert_const_as_input(node_id + '_slope',
                                                          np.asarray(slope, dtype=np.float32),
                                                          input_index=1)

    def export_uni_model(self):
        from uni_model import UniLayerPRelu
        return UniLayerPRelu(self.name, out_dtypes=self.get_uni_model_out_dtypes())
