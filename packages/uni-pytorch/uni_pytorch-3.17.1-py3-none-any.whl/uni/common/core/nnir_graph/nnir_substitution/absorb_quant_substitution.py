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
from typing import List, Sequence

from uni.common.core.nnir_graph.nnir_edge import NnirEdge
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Quant, Identity
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase
from uni.common.core.node_history import NodeHistory
from uni.common.core.uid_generator import UIDGenerator
from uni.common.logger import get_logger, MessageCodes

logger = get_logger(__name__)


class AbsorbQuantSubstitution(NnirSubstituteBase):
    """ Quantization info from quantization node is absorbed into edges.
        A -> Quant -> B  => A -quant-> B
        A -> QuantA -> QuantB -> B => A -quant-> B if QuantA and QuantB contain the same quant info
                                   => A -quantA-> Identity -quantB-> B if QuantA and QuantB contain different info
    """

    def get_match_list(self) -> List[List[NnirNode]]:
        return self.nodes_linear_op_matcher([(Quant, None)])

    def single_match_substitute(self, match: List[NnirNode]):
        assert len(match) == 1
        node = match[0]
        assert isinstance(node, Quant)
        if not self.nnir_graph.node_exists(node.name):
            # in case is already removed
            return
        in_edges: Sequence[NnirEdge] = self.nnir_graph.get_ordered_in_edges(node)
        assert len(in_edges) == 1, f'Quant node {node.name} expected to have single input'
        in_edge = in_edges[0]
        node_quant = node.to_quant_info()
        prev_node: NnirNode = self.nnir_graph.get_node_data(in_edge.src)
        prev_src_index = in_edge.src_index
        self.nnir_graph.remove_edge(in_edge.src, in_edge.src_index, in_edge.dest, in_edge.dest_index)
        if prev_node.get_quant(prev_src_index) not in [node_quant, None]:
            logger.warning(f'Adding Identity between two different quantizations in a row ({node.name})',
                           message_code=MessageCodes.QUANTIZATION)
            # if quantization on input edge differs from quant node, add identity
            history = NodeHistory(node.op_info(), desc='Separate two subsequent quantizations')
            identity = Identity(name=f'Identity.uid{UIDGenerator.next()}', history=history)
            self.nnir_graph.add_node(identity)
            self.nnir_graph.add_edge(in_edge.clone(dest=identity.name))
            prev_node = self.nnir_graph.get_node_data(identity.name)
            prev_src_index = 0

        prev_node.set_quant(node_quant, prev_src_index)

        for out_edge in self.nnir_graph.get_out_edges(node, by_output=False):    # type: NnirEdge
            # can be multiple edges if shared, but all should come from same single output
            assert out_edge.src_index == 0, f'Quant node {node.name} expected to have single input'
            self.nnir_graph.remove_edge(out_edge.src, out_edge.src_index, out_edge.dest, out_edge.dest_index)
            self.nnir_graph.add_edge(out_edge.clone(src=prev_node.name, src_index=prev_src_index))

        self.nnir_graph.remove_node(node, reconnect=False, reindex_input_edges=False)

    def short_name(self):
        return "absorb_quant"
