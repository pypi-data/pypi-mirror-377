# -------------------------------------------------------------------------------
# (c) Copyright 2022 Sony Semiconductor Israel, Ltd. All rights reserved.
#
#      This software, in source or object form (the "Software"), is the
#      property of Sony Semiconductor Israel Ltd. (the "Company") and/or its
#      licensors, which have all right, title and interest therein, You
#      may use the Software only in  accordance with the terms of written
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
Created on 6/29/22

@author: irenab
"""
from typing import Union, Tuple, List

from uni.common.parsers.base_reader import MetaOpType
from uni.common.core.multigraph.node_graph_api import GraphRequest
from uni.common.core.nnir_graph.nnir_graph import NnirNode
from uni.common.core.error.defs import UnsupportedOpsError
from .onnx_reader import OnnxReader
from .onnx_reader_helper import OnnxReaderHelper, OnnxMetaNode
from uni.common.util.vis import OnnxMetaGraphVis    # type: ignore
from .onnx_schema_helper import OnnxSchemaHelper
from .onnx_simplifier import OnnxSimplifier
from uni.common.parsers.base_parser import BaseParser
from uni.common.util.dev import is_dev, disable_simplifier, is_save_simplifier
from uni.common.core.multigraph.graph import MultiDiGraph
from uni.common.logger import get_logger
from .onnx_op_to_factory import onnx_op_factory

logger = get_logger(__name__)


def is_dummy_input(node: OnnxMetaNode):
    return node.op_type == MetaOpType.DummyInput


def is_dummy_output(node: OnnxMetaNode):
    return node.op_type == MetaOpType.DummyOutput


schema_helper_dict = {}


class OnnxParser(BaseParser):
    vis_converter = OnnxMetaGraphVis

    def __init__(self, model_path, vis_path=None):
        if disable_simplifier():
            model = model_path
        else:
            model = self.run_simplifier(model_path)
        super().__init__(model, OnnxReader, vis_path)
        # Schema helper depends on opset version of the specific model, so we need to set it for OnnxMetaNode.
        # It's not used until the conversion of meta graph to nnir graph (though it could be used earlier at
        # OnnxMetaNode construction. It's delayed in order to separate attrs coming from the model and defaults)
        # making a dict in global scope to avoid creating a new instance for each model to prevent memory leak in pytest
        opset_version = OnnxReaderHelper.get_opset_version(self.model)
        if opset_version not in schema_helper_dict:
            schema_helper_dict[opset_version] = OnnxSchemaHelper(supported_ops=list(onnx_op_factory.keys()),
                                                                 opset_version=opset_version)

        OnnxMetaNode.set_onnx_schema_helper(schema_helper_dict[opset_version])

    @staticmethod
    def run_simplifier(model_path):
        onnx_sim = OnnxSimplifier(model_path)
        onnx_model = onnx_sim.simplify()
        if is_save_simplifier():
            sim_path = onnx_sim.save()
            logger.debug(f'Onnx model simplified saved to {sim_path}')
        deleted_nodes_count = onnx_sim.get_deleted_nodes_count()
        if deleted_nodes_count > 0 or is_dev():
            logger.debug(f'Simplifier delete {deleted_nodes_count} nodes from the model')
        return onnx_model

    def verify_supported_nodes(self, meta_graph: MultiDiGraph):
        nodes: List[OnnxMetaNode] = meta_graph.get_nodes(data=True)
        unsupported_nodes = set()
        for node in nodes:
            if node.op_type not in onnx_op_factory:
                unsupported_nodes.add(node.op_type)
        if unsupported_nodes:
            raise UnsupportedOpsError(unsupported_nodes)
        return nodes

    @staticmethod
    def _convert_meta_node(meta_graph, node) -> Union[NnirNode, Tuple[NnirNode, GraphRequest]]:
        factory = onnx_op_factory[node.op_type]
        assert factory is not None, node.op_type
        # check that factory method is decorated with validation config
        assert hasattr(factory.from_onnx, 'valid')
        return factory.from_onnx(node, graph_ctx=meta_graph.get_graph_context_for_node(node))
