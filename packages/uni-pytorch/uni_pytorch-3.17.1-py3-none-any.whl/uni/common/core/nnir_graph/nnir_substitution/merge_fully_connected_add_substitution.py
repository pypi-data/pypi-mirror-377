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
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Variable, FullyConnected, Add
from . import NnirSubstituteBase


class MergeFullyConnectedAndAddSubstitution(NnirSubstituteBase):
    """
    reason: torch -> onnx nn.Linear (with input len 4 and bias) have fc (no quant) + add (with quant)
    fully connected + add -> fully connected with new bias
    when fc bias is zero
    before:
        fc_input -> fc
        fc_weight --> fc
        fc_bias --> fc (all zero)
        fc --> add
        const --> add
    after:
        fc_input -> fc
        fc_weight --> fc
        new_bias --> fc (new_bias = fc_bias + const)
        fc quant is the same as add quant

    must be after absorb_quant
    """

    def short_name(self):
        return 'fc_add'

    def get_match_list(self):

        def fc_selector(node: NnirNode, graph: NnirGraph):
            if node.get_quant(0) is not None:
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                # limit the match only to the case to torch.onnx.export create
                return False
            bias: Variable = graph.get_ordered_in_nodes(node, data=True)[2]    # type: ignore[assignment]
            bias_out_nodes = graph.get_out_nodes(bias, data=False, by_output=False)
            if len(bias_out_nodes) != 1:
                # limit the match only to the case to torch.onnx.export create
                return False
            return bias.data.min() == 0 and bias.data.max() == 0

        def add_selector(node: NnirNode, graph: NnirGraph):
            const_list = [n for n in self.nnir_graph.get_ordered_in_nodes(node, data=True) if isinstance(n, Variable)]
            if len(const_list) != 1:
                return False
            const = const_list[0]
            const_out_nodes = graph.get_out_nodes(const, data=False, by_output=False)
            if len(const_out_nodes) != 1:
                # limit the match only to the case to torch.onnx.export create
                return False
            return True

        return self.nodes_linear_op_matcher([(FullyConnected, fc_selector), (Add, add_selector)])

    def single_match_substitute(self, match):
        fc, add = match
        const = [n for n in self.nnir_graph.get_ordered_in_nodes(add, data=True) if isinstance(n, Variable)][0]
        bias = self.nnir_graph.get_ordered_in_nodes(fc, data=True)[2]
        bias.data = const.data
        fc.set_quant(add.get_quant(0), 0)
        bias.set_quant(const.get_quant(0), 0, override=True)
        self.nnir_graph.remove_node(const, reconnect=False, reindex_input_edges=True)
        self.nnir_graph.remove_node(add, reconnect=True, reindex_input_edges=True)
