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
from typing import Union, Dict, Tuple

import numpy as np
from packaging.version import parse
import onnx
from onnx import shape_inference

from uni.common.core.common import Framework, OpInfo
from uni.common.core.connectivity_map import Tensor
from uni.common.core.error import UnsupportedModelInputError, ModelErrorInputMessages
from uni.common.core.nnir_graph.semantics import DataFormat
from uni.common.core.node_history import NodeHistory
from uni.common.core.uid_generator import UIDGenerator
from uni.common.parsers.base_reader import MetaOpType, BaseReader
from uni.pytorch.onnx_parser.onnx_reader_helper import OnnxReaderHelper, OnnxMetaNode, OnnxOpType
from uni.common.util.dev import is_dev, is_skip_validate_input
from uni.common.logger import get_logger, MessageCodes

logger = get_logger(__name__)
PYTORCH_MIN_SUPPORTED_VERSION = '2.0.0'
"""
https://github.com/pytorch/pytorch/blob/v<torch_version>/torch/onnx/_constants.py
torch 2.0.0 -> ONNX_MAX_OPSET = 18
torch 2.1.0 -> ONNX_MAX_OPSET = 19
torch 2.2.0 -> ONNX_MAX_OPSET = 19
torch 2.3.0 -> ONNX_MAX_OPSET = 19
torch 2.4.0 -> ONNX_MAX_OPSET = 20
"""
ONNX_OPSET_SUPPORTED_LIST = [15, 16, 17, 18, 19, 20]


class OnnxReader(BaseReader):

    def __init__(self, fw_model: Union[str, onnx.ModelProto]):
        UIDGenerator.reset()
        super().__init__(fw_model)
        # Run onnx shape inference. It adds value_info attr to onnx_model.graph
        self.model = shape_inference.infer_shapes(self.model, strict_mode=True, data_prop=True)
        self._tensor_shapes_type: Dict[str, Tuple[tuple, np.dtype]] = \
            {vi.name: OnnxReaderHelper.parse_tensor_type(vi)[1:] for vi in self.model.graph.value_info}

    def validate_model_input(self):
        if is_skip_validate_input():
            return
        for i, input_node in enumerate(self.model.graph.input):
            input_shape = self.tensors[input_node.name].shape
            if input_shape[0] not in [1, None]:
                raise UnsupportedModelInputError(i, ModelErrorInputMessages.BATCH_SIZE_ERR)
            if None in input_shape[1:]:
                raise UnsupportedModelInputError(i, ModelErrorInputMessages.DYNAMIC_INPUT_ERR)

    def get_metadata(self) -> Dict:
        from mct_quantizers.pytorch.metadata import get_onnx_metadata
        return get_onnx_metadata(self.model)

    @staticmethod
    def check_producer(model: onnx.ModelProto):
        """
        Check that model was produced is pytorch and version is supported
        """
        producer_name = model.producer_name
        producer_version = model.producer_version
        if producer_name != 'pytorch':
            raise RuntimeError(f'Unsupported producer: {producer_name}. Only pytorch is supported')
        if producer_version is None or parse(producer_version) < parse(PYTORCH_MIN_SUPPORTED_VERSION):
            raise RuntimeError(f'Unsupported producer version: {producer_version}. '
                               f'Only pytorch >= {PYTORCH_MIN_SUPPORTED_VERSION} is supported')

    @classmethod
    def _load_model(cls, path) -> onnx.ModelProto:
        try:
            model = onnx.load_model(path)
            onnx.checker.check_model(model, full_check=True)
        except (onnx.checker.ValidationError, shape_inference.InferenceError) as e:
            raise RuntimeError('Onnx model loaded but failed validation check') from e
        except Exception as e:
            raise RuntimeError(f'Failed to load {path}') from e
        cls.check_producer(model)
        opset_version = OnnxReaderHelper.get_opset_version(model)
        if opset_version not in ONNX_OPSET_SUPPORTED_LIST:
            raise RuntimeError(f'ONNX opset version {opset_version} is not supported.'
                               f' Supported ONNX opsets: {ONNX_OPSET_SUPPORTED_LIST}')

        unknown_domains = OnnxReaderHelper.get_unknown_domains(model)
        if unknown_domains:
            logger.warning(f'Unknown domains: {unknown_domains} in ONNX model', message_code=MessageCodes.INVALID_MODEL)
        intersection_names = OnnxReaderHelper.get_inputs_initializers_intersection(model)
        if intersection_names:
            raise RuntimeError(f'Model inputs contains initializers/constants: {intersection_names}')
        try:
            logger.debug(f'Loaded onnx model: {model.domain=}, {model.opset_import=}, {model.ir_version=}, '
                         f'{model.producer_name=}, {model.producer_version=}')
        except AttributeError:
            if is_dev():
                raise

        return model

    def get_data_format(self) -> DataFormat:
        return DataFormat.CHW

    def _build_nodes_and_connectivity(self):
        nodes = []

        # add placeholders
        for i, graph_input in enumerate(self.model.graph.input):
            ph_node = self._create_placeholder(graph_input, i)
            nodes.append(ph_node)

        # add consts from initializers (trainable)
        for initializer in self.model.graph.initializer:
            var_node = self._create_variable_from_initializer(initializer)
            nodes.append(var_node)

        # add regular onnx nodes
        for n in self.model.graph.node:
            if not n.name:
                raise NotImplementedError(f'ONNX nodes (type:{n.op_type}) with empty names are not currently supported')
            node: OnnxMetaNode = OnnxReaderHelper.parse_node(n)
            nodes.append(node)

            # for disconnected inputs/outputs we only add a tensor, dummy node will be added by the base class
            for i, tid in enumerate(node.output):
                if not tid:    # disconnected output, e.g. node.output=['x1', '', 'x3']
                    tid = f'{node.name}_dummy_output.{i}'
                shape, np_dtype = self._tensor_shapes_type.get(tid, (None, None))
                self.tensors.add_source(tensor_id=tid, node_name=node.name, index=i, shape=shape, dtype=np_dtype)

            for i, tid in enumerate(n.input):
                if not tid:    # missing optional input is empty, e.g. node.input=['x1', '', 'x3']
                    tid = f'{node.name}_dummy_input.{i}'
                self.tensors.add_dest(tensor_id=tid, node_name=node.name, index=i)

        # add outputs
        for i, graph_output in enumerate(self.model.graph.output):
            out_node = self._create_output(graph_output, i)
            nodes.append(out_node)

        return nodes

    def _build_dummy_node(self, name: str, op: MetaOpType, tensor: Tensor) -> OnnxMetaNode:
        if op == MetaOpType.DummyOutput:
            assert tensor.src
            return OnnxMetaNode(name, op_type=op, input=[tensor.src.name], output=[])
        if op == MetaOpType.DummyInput:
            assert len(tensor.dest) == 1
            return OnnxMetaNode(name, op_type=op, input=[], output=[tensor.dest[0].name])
        raise ValueError(f'Unexpected op {op}')

    def _create_variable_from_initializer(self, initializer: onnx.TensorProto) -> OnnxMetaNode:
        """ build 'fake' OnnxMetaNode imitating a node that came from real onnx constant node """
        tensor_name, data = OnnxReaderHelper.parse_initializer(initializer)
        var_name = self._rename_onnx_tensor(tensor_name, prefix='Variable', add_uid=True)
        history = NodeHistory(OpInfo(node_id=tensor_name, op='initializer', framework=Framework.onnx),
                              desc=f'Onnx Initializer -> {OnnxOpType.Constant}')
        var_node = OnnxMetaNode(name=var_name,
                                op_type=OnnxOpType.Constant,
                                input=[],
                                output=[tensor_name],
                                attr={OnnxMetaNode.const_val_attr: data},
                                history=history)
        self.tensors.add_source(tensor_id=tensor_name, node_name=var_node.name, index=0, shape=data.shape)
        return var_node

    def _create_placeholder(self, graph_input: onnx.ValueInfoProto, ordinal: int) -> OnnxMetaNode:
        """ Create 'fake' OnnxMetaNode for placeholder """
        tensor_name, shape, np_dtype = OnnxReaderHelper.parse_tensor_type(graph_input)
        name = self._rename_onnx_tensor(tensor_name, prefix=MetaOpType.Placeholder, add_uid=True)
        history = NodeHistory(OpInfo(node_id=tensor_name, op='tensor_type', framework=Framework.onnx),
                              desc=f'Model input -> {MetaOpType.Placeholder}')
        ph_node = OnnxMetaNode(name=name,
                               op_type=MetaOpType.Placeholder,
                               input=[],
                               output=[tensor_name],
                               attr={
                                   'shape': shape,
                                   'ordinal': ordinal
                               },
                               history=history)
        self.tensors.add_source(tensor_id=tensor_name, node_name=ph_node.name, index=0, shape=shape, dtype=np_dtype)
        return ph_node

    def _create_output(self, graph_output: onnx.ValueInfoProto, ordinal: int) -> OnnxMetaNode:
        """ create 'fake' OnnxMetaNode for Output """
        tensor_id, shape, np_dtype = OnnxReaderHelper.parse_tensor_type(graph_output)
        history = NodeHistory(OpInfo(node_id=tensor_id, op='tensor_type', framework=Framework.onnx),
                              desc=f'Model output -> {MetaOpType.Output}')
        name = self._rename_onnx_tensor(tensor_id, prefix=MetaOpType.Output, add_uid=True)
        out_node = OnnxMetaNode(name=name,
                                op_type=MetaOpType.Output,
                                input=[tensor_id],
                                output=[],
                                attr={
                                    'shape': shape,
                                    'ordinal': ordinal
                                },
                                history=history)
        self.tensors.add_dest(tensor_id=tensor_id, node_name=out_node.name, index=0, shape=shape, dtype=np_dtype)
        return out_node

    @staticmethod
    def _rename_onnx_tensor(tensor_uid: str, prefix: str = '', add_uid: bool = True) -> str:
        """ Create new (node) name based on tensor_id:
            removes tensor prefix onnx:: added by onnx to unnamed tensors
            prefix - optional prefix to add
            add_uid - add unique id, by default True.
                      Beware!!! If disabled, id modification might result in loss of uniqueness """
        new_id = tensor_uid.replace('onnx::', '')
        prefix = prefix + '.' if prefix else ''
        uid = f'.uid{UIDGenerator.next()}' if add_uid else ''
        new_id = prefix + new_id + uid
        return new_id
