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
Created on 12/11/22

@author: irenab
"""
from pathlib import PosixPath
from typing import List, Union, Tuple, Set, Type, Any, Iterable
import abc
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.core.multigraph.edge import Edge
from uni.common.core.multigraph.node_graph_api import GraphRequest, NodePosition
from uni.common.core.multigraph.typing import NodeKey    # noqa: F401
from uni.common.core.nnir_graph.nnir_graph import NnirGraph
from uni.common.core.nnir_graph.nnir_edge import NnirEdge
from uni.common.core.nnir_graph.nnir_nodes import NnirNode, Variable
from uni.common.core.error.defs import InvalidOpError, InvalidOpsError
from uni.common.parsers.base_reader import BaseReader
from uni.common.util.vis import MultigraphVis    # type: ignore
from uni.common.util.dev import skip_compliance_check
from uni.common.logger import get_logger, MessageCodes

logger = get_logger(__name__)

MAX_TPC_MINOR_VERSION = 5
TPC_SUPPORTED_TYPS = ['imx500']


class BaseParser(abc.ABC):
    vis_converter = MultigraphVis

    def __init__(self, fw_model: Union[str, PosixPath, Any], reader: Type[BaseReader], vis_path=None):
        self.reader = reader(fw_model)
        self.model = self.reader.model
        self.vis_path = vis_path

    def get_metadata(self):
        return self.reader.get_metadata()

    def validate_metadata(self):
        metadata = self.get_metadata()
        logger.debug(f'reading metadata: {metadata}', message_code=MessageCodes.EXECUTION)
        if 'tpc_minor_version' in metadata and int(metadata['tpc_minor_version']) > MAX_TPC_MINOR_VERSION:
            raise RuntimeError(f"Unsupported TPC minor version: {metadata['tpc_minor_version']}. "
                               f"Supported versions are up to {MAX_TPC_MINOR_VERSION}.")

        if 'tpc_platform_type' in metadata and metadata['tpc_platform_type'] not in TPC_SUPPORTED_TYPS:
            raise RuntimeError(f"Unsupported TPC platform type: {metadata['tpc_platform_type']}. "
                               f"Supported types are {TPC_SUPPORTED_TYPS}.")

    @abc.abstractmethod
    def verify_supported_nodes(self, meta_graph: MultiDiGraph):
        """ Check that all nodes are supported
            Raises:
                UnsupportedOpsError containing all unsupported ops if any node is not supported
        """
        pass

    def parse(self) -> NnirGraph:
        meta_graph: MultiDiGraph = self.reader.build_meta_graph()
        if self.vis_path:
            self.vis_converter.dump_vis_json(meta_graph, self.vis_path / 'initial_meta_graph.json')
        meta_graph.validate_graph(allow_disconnected_outputs=False)

        self.verify_supported_nodes(meta_graph)

        nnir_graph = self._build_nnir_graph(meta_graph)

        # Second validation pass on full nnir_graph (first was at the level of nodes conversion during nnir_graph)
        if skip_compliance_check():
            logger.warning('SDSP compliance validation is disabled', message_code=MessageCodes.EXECUTION)
        else:
            logger.debug('Running SDSP compliance validation')
            nnir_graph.validate_nodes()
        return nnir_graph

    @staticmethod
    @abc.abstractmethod
    def _convert_meta_node(meta_graph, node) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        pass

    def _build_nnir_graph(self, meta_graph: MultiDiGraph) -> NnirGraph:
        """ Convert meta-graph to NnirGraph
            If any node fails conversion to NnirNode, errors for all failed nodes will be aggregated
            and InvalidOpsError will be raised """

        nnir_graph = NnirGraph(data_format=self.reader.get_data_format())
        invalid_nodes = []
        nodes_try_to_remove = set()
        reconnect_input: dict = {}

        for meta_node in meta_graph.topological_sort(data=True):
            try:
                ret = self._convert_meta_node(meta_graph, meta_node)
            except InvalidOpError as e:
                invalid_nodes.append(e.op_errors)
                continue

            # go over remaining nodes to identify additional issues,
            # but don't do anything else since graph construction is broken
            if invalid_nodes:
                continue

            nnir_node, requests = ret if isinstance(ret, tuple) else (ret, [])
            if not isinstance(requests, Iterable):
                requests = [requests] if requests else []

            nnir_graph.add_node(nnir_node, inject_ctx=True)

            # only add edges for inputs that were not discarded
            orig_in_edges: List[Edge] = meta_graph.get_ordered_in_edges(meta_node)
            edges_to_add, detached_input_nodes = self._filter_detached_edges(orig_in_edges, requests)
            nodes_try_to_remove.update(detached_input_nodes)

            for i, edge in enumerate(edges_to_add):
                # update src if needed
                src = reconnect_input.get(edge.src, edge.src)
                nnir_edge = NnirEdge(src=src, src_index=edge.src_index, dest=edge.dest, dest_index=i, shape=edge.shape)
                nnir_graph.add_edge(nnir_edge)

            for request in requests:
                # new inputs must be inserted after inputs_to_detach were removed (nnir edges were added)
                self._insert_input_variables_from_request(request, nnir_graph, nnir_node, meta_node=meta_node)
                # only needs nnir_node to be added
                self._add_adjacent_node_from_request(request, nnir_graph, nnir_node, reconnect_input)
                self._duplicate_dynamic_input(request, nnir_graph, nnir_node)

        if invalid_nodes:
            raise InvalidOpsError(invalid_nodes)
        # remove detached nnir_nodes
        for node in nodes_try_to_remove:    # type: NodeKey
            assert nnir_graph.is_source(node)
            nnir_graph.remove_node_if_detached(node)

        return nnir_graph

    @staticmethod
    def _filter_detached_edges(orig_in_edges: list, requests: Iterable[GraphRequest]) -> Tuple[List[Edge], Set]:
        edges_to_add = orig_in_edges
        nodes_to_remove = set()
        for request in requests:
            if request.inputs_to_detach:
                assert max(request.inputs_to_detach) < len(orig_in_edges)
                edges_to_add = [e for e in orig_in_edges if e.dest_index not in request.inputs_to_detach]
                nodes_to_remove.update({orig_in_edges[i].src for i in request.inputs_to_detach})
        return edges_to_add, nodes_to_remove

    def _insert_input_variables_from_request(self, request: GraphRequest, nnir_graph: NnirGraph, node: NnirNode,
                                             **kwargs):
        """
            Note: This function has overwritten in TensorflowParser

            Insert additional input variable as requested by the node factory
            Currently inputs can only be added at indices following existing inputs
            (e.g. if node has 2 inputs, new inputs can be added at indices 2, 3, ...) """
        new_inputs = request.const_inputs_to_insert
        if not new_inputs:
            return
        for i, n in new_inputs.items():
            var = Variable(n.name, data=n.data, quant_info=n.quant)
            nnir_graph.add_node(var, inject_ctx=True)
            needs_to_update_edge = nnir_graph.get_ordered_in_edges(node)[i:]
            if len(needs_to_update_edge) > 0 and request.validate_const_insert_at_the_end:
                raise NotImplementedError('new inputs can be added only at end ')
            for e in needs_to_update_edge:
                nnir_graph.remove_edge(src=e.src, dest=e.dest, src_index=e.src_index, dest_index=e.dest_index)
            nnir_graph.add_edge(NnirEdge(src=n.name, src_index=0, dest=node.name, dest_index=i, shape=n.data.shape))
            for e in needs_to_update_edge:
                nnir_graph.add_edge(e.clone(dest_index=e.dest_index + 1))

    @staticmethod
    def _add_adjacent_node_from_request(request: GraphRequest, nnir_graph: NnirGraph, node: NnirNode,
                                        reconnect_input: dict):
        if not request.adjacent_node_to_insert:
            return
        new_node: NnirNode = request.adjacent_node_to_insert.node
        cfg = request.adjacent_node_to_insert
        if cfg.node_position == NodePosition.NODE_AFTER:
            assert node.NUM_OUTPUTS is not None
            assert isinstance(node.NUM_OUTPUTS, int)
            if node.NUM_OUTPUTS > 1:
                raise NotImplementedError('Attempted to insert a node after a node with multiple outputs')
            nnir_graph.add_node(new_node, inject_ctx=True)
            new_edge = NnirEdge(src=node.name, src_index=0, dest=new_node.name, dest_index=0, shape=cfg.shape)
            nnir_graph.add_edge(new_edge)
            # Input connectivity for subsequent nodes looks at the original node, so need to map it to the new node
            reconnect_input[node.name] = new_node.name
        elif cfg.node_position == NodePosition.NODE_BEFORE:
            nnir_graph.insert_node_before(node.name, new_node, cfg.edge_index, cfg.shape)
        else:
            raise NotImplementedError(f'Node position {cfg.node_position} is not supported')

    @staticmethod
    def _duplicate_dynamic_input(request, nnir_graph, nnir_node):
        if not request.dynamic_input_to_duplicate:
            return
        in_edges = nnir_graph.get_ordered_in_edges(nnir_node)
        for edge_to_dup_index in request.dynamic_input_to_duplicate.keys():
            for new_dest in request.dynamic_input_to_duplicate[edge_to_dup_index]:
                nnir_graph.add_edge(in_edges[edge_to_dup_index].clone(dest_index=new_dest))
