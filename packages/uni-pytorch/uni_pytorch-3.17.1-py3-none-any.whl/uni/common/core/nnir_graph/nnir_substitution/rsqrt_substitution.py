# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
from typing import List, Sequence

from uni.common.core.nnir_graph.nnir_edge import NnirEdge
from uni.common.core.node_history import NodeHistory
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Div, Sqrt, Variable, RSqrt
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase


class RsqrtSubstitution(NnirSubstituteBase):
    """
    this substitution is for torch rsqrt is converted is onnx to 1 / sqrt
    input:  1  / sqrt
    output: rsqrt
    """

    def get_match_list(self) -> List[List[NnirNode]]:

        def sqrt_selector(node: NnirNode, graph: NnirGraph):
            if node.get_quant(0) is not None:
                return False
            out_nodes = graph.get_out_nodes(node, data=False, by_output=False)
            if len(out_nodes) != 1:
                # limit the match only to the case to torch.onnx.export create
                return False
            return True

        def div_selector(node: NnirNode, graph: NnirGraph):
            in_nodes: List[NnirNode] = graph.get_ordered_in_nodes(node, data=True)
            if not isinstance(in_nodes[0], Variable):
                return False
            const: Variable = in_nodes[0]
            return const.data.min() == 1 and const.data.max() == 1

        return self.nodes_linear_op_matcher([(Sqrt, sqrt_selector), (Div, div_selector)])

    def single_match_substitute(self, match: List[NnirNode]):
        sqrt, div = match
        const = [n for n in self.nnir_graph.get_ordered_in_nodes(div, data=True) if isinstance(n, Variable)][0]
        history = NodeHistory(div.op_info(), desc='1/sqrt -> rsqrt')
        new_node = RSqrt(name=f"{div.name}_rsqrt", history=history)
        new_node.set_quant(div.get_quant(0), 0)
        self.nnir_graph.add_node(new_node)
        in_edges: Sequence[NnirEdge] = self.nnir_graph.get_ordered_in_edges(sqrt)
        out_edges: Sequence[NnirEdge] = self.nnir_graph.get_out_edges(div, by_output=False)

        self.nnir_graph.remove_node(const, reconnect=False, reindex_input_edges=False)
        self.nnir_graph.remove_node(sqrt, reconnect=False, reindex_input_edges=False)
        self.nnir_graph.remove_node(div, reconnect=False, reindex_input_edges=False)

        assert len(in_edges) == 1
        in_edge = in_edges[0]
        self.nnir_graph.add_edge(in_edge.clone(dest=new_node.name))

        for out_edge in out_edges:
            self.nnir_graph.add_edge(out_edge.clone(src=new_node.name))

    def short_name(self):
        return "rsqrt_substitution"
