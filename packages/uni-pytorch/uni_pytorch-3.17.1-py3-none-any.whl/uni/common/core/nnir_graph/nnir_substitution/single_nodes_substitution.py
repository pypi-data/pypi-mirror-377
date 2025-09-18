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
from pathlib import Path
from typing import List, Optional

from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase


class SingleNodesSubstitution(NnirSubstituteBase):
    """ Run node-to-subgraph substitutions
        For now we assume there are no conflicts between substitutions and the order doesn't matter """

    def __init__(self, nnir_graph: NnirGraph, vis_dir: Optional[Path]):
        super().__init__(nnir_graph, vis_dir)

    def get_match_list(self) -> List[List[NnirNode]]:

        def selector(node: NnirNode, graph: NnirGraph):
            return node.has_substitution()

        return self.nodes_linear_op_matcher([(None, selector)])

    def single_match_substitute(self, match: List[NnirNode]):
        node = match[0]
        ret = node.substitute()
        if ret is None:
            return

        new_nodes, new_edges = ret

        assert all(n.has_substitution() is False for n in new_nodes), 'conflicting substitutions'

        self._validate_edges(node, new_edges)

        # edges are removed automatically
        self.nnir_graph.remove_node(node, reconnect=False, reindex_input_edges=False)

        self.nnir_graph.add_nodes(new_nodes, inject_ctx=True)
        self.nnir_graph.add_edges(new_edges)

    def short_name(self):
        return "single_nodes_substitution"

    def _validate_edges(self, node, new_edges):
        # check that new edges were passed to replace all original inputs/outputs
        orig_srcs = [(e.src, e.src_index) for e in self.nnir_graph.get_ordered_in_edges(node)]
        orig_dests = [(e.dest, e.dest_index) for e in self.nnir_graph.get_out_edges(node, by_output=False)]
        for e in new_edges:
            if (e.src, e.src_index) in orig_srcs:
                orig_srcs.remove((e.src, e.src_index))
            elif (e.dest, e.dest_index) in orig_dests:
                orig_dests.remove((e.dest, e.dest_index))
        assert not (orig_srcs or orig_dests), f'Missing new edges for srcs {orig_srcs} or dests {orig_dests}'
