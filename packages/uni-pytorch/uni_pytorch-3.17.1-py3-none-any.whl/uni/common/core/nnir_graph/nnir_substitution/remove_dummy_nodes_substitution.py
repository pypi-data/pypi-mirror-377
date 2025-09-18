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
from typing import List

from uni.common.core.nnir_graph.nnir_nodes import NnirNode
from uni.common.core.nnir_graph.nnir_nodes.dummy_node import DummyNode, DummyOutput, DummyInput
from uni.common.core.nnir_graph.nnir_substitution import NnirSubstituteBase


class RemoveDummyNodeSubstitution(NnirSubstituteBase):
    """ Remove dummy nodes.
        Dummy nodes are service nodes that ensure consistency between op inputs/outputs and actual incoming/
        outgoing edges (as op inputs/outputs are represented by actual edges),
        so the removal should be performed after all processing is completed
    """

    def dev_post_validation(self):
        self.nnir_graph.validate_graph(allow_disconnected_outputs=True)
        self.nnir_graph.validate_nodes()

    def get_match_list(self) -> List[List[NnirNode]]:
        return self.nodes_linear_op_matcher([(DummyNode, None)])

    def single_match_substitute(self, match: List[NnirNode]):
        node = match[0]
        assert isinstance(node, DummyNode)
        assert len(match) == 1
        if isinstance(node, DummyOutput):
            self.nnir_graph.remove_node(node, reconnect=False, reindex_input_edges=False)
        elif isinstance(node, DummyInput):
            raise RuntimeError('NnirGraph is not expected to contain DummyInputs')
        else:
            raise RuntimeError(f'Unknown DummyNode type {node.op}')

    def short_name(self):
        return "remove_dummy_nodes"
