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
from typing import List

from uni.common.core.multigraph.edge import Edge
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, MultiClassNonMaxSuppression, SSDPostProcess
from uni.common.core.nnir_graph.nnir_nodes.dummy_node import DummyOutput
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase


class NMSOutputsSubstitution(NnirSubstituteBase):
    """
    nms without indices to nms with indices
    """

    def single_match_substitute(self, match: List[NnirNode]):
        """
        when replacing nms without indices to nms with indices,
        1 moving output 3 edges to output 4
        2 add a dummy node to output 3
        """
        node = match[0]
        remove_edges: List[Edge] = self.nnir_graph.get_out_edges(node, by_output=True)[3]
        for edge in remove_edges:
            new_edge = edge.clone(src_index=edge.src_index + 1)
            self.nnir_graph.remove_edge_by_obj(edge)
            self.nnir_graph.add_edge(new_edge)
        new_node = DummyOutput(f"{node.name}_dummy_indices")
        self.nnir_graph.add_node(new_node)
        self.nnir_graph.add_edge(Edge(src=node.name, dest=new_node.name, src_index=3, dest_index=0))

    def get_match_list(self) -> List[List[NnirNode]]:

        def selector(node: NnirNode, graph: NnirGraph):
            return graph.node_out_degree(node) == 4

        return (self.nodes_linear_op_matcher([(MultiClassNonMaxSuppression, selector)]) +
                self.nodes_linear_op_matcher([(SSDPostProcess, selector)]))

    def short_name(self):
        return 'nms_outputs'
