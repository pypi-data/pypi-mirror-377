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
Created on 7/20/22

@author: irenab
"""
from typing import Tuple, List, Dict, Optional, ClassVar, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

import onnx.numpy_helper
import numpy as np

from uni.common.core.node_history import NodeHistory
from uni.common.util.dev import is_dev
from .onnx_mct_reader_helper import MCT_QUANTIZERS_DOMAIN, OnnxMctQWeightsQuantizer

if TYPE_CHECKING:    # prevents circular dependency issue
    from .onnx_schema_helper import OnnxSchemaHelper    # pragma: no cover

KNOWN_DOMAINS = [onnx.defs.ONNX_DOMAIN, MCT_QUANTIZERS_DOMAIN, 'Sony', 'EdgeMDT']


class OnnxOpType(str, Enum):
    """
        can't use same value as MetaOpType because it is conflict in OnnxMetaNode.op_type
    """
    Identity = 'Identity'
    Constant = 'Constant'
    Shape = 'Shape'
    Range = 'Range'
    Add = 'Add'
    Mul = 'Mul'
    Pad = 'Pad'
    Dropout = 'Dropout'
    QuantizeLinear = 'QuantizeLinear'
    DequantizeLinear = 'DequantizeLinear'


@dataclass
class OnnxMetaNode:
    """ Is intended primarily as output from automatic conversion of Onnx node objects.
        Contains onnx-specific ops and attrs, but no Onnx internal implementation.
    """
    name: str
    op_type: str
    # [] = > 0 inputs / outputs
    input: List[str]
    output: List[str]
    attr: Dict = field(default_factory=dict)

    # capture node's history if node didn't originate from Onnx node obj or underwent modifications
    history: Optional[NodeHistory] = None

    # attribute must exist for Constant op in order to use get_const_data()
    # (defines class variable, it won't appear in dataclass fields)
    const_val_attr: ClassVar[str] = 'value'
    domain: str = field(default_factory=str)

    _schema_helper: ClassVar[Optional['OnnxSchemaHelper']] = None

    @property
    def original_name(self):
        return self.history.op_info.node_id if self.history else self.name

    @classmethod
    def set_onnx_schema_helper(cls, schema_helper: 'OnnxSchemaHelper'):
        """ Set onnx schema helper
            Must be set prior to calling get_attr_with_default_from_schema """
        cls._schema_helper = schema_helper

    @property
    def key(self):
        return self.name

    def has_attr(self, attr):
        return attr in self.attr

    def get_attr(self, attr: str):
        return self.attr[attr]

    def get_attr_with_default(self, attr: str, default: Any):
        if self.has_attr(attr):
            return self.get_attr(attr)
        assert attr not in self._schema_helper.get_default_attrs(self.op_type)    # type: ignore
        return default

    def get_attr_with_default_from_schema(self, attr: str, min_opset: Optional[int] = None, min_opset_def_val=None):
        """
        Retrieve the attribute value from the object if it exists; otherwise, retrieve the default value
        from the schema if applicable.

        Args:
            attr (str): The name of the attribute to retrieve.
            min_opset (Optional[int]): The minimum opset version required to consider the schema's default.
                                                 If None, defaults are always considered. Defaults to None.
            min_opset_def_val (optional): The default value to return if the attribute is not present
                                        and the opset version is below min_opset.
                                        If min_opset is None, min_opset_def_val should also be None.

        Returns:
            The attribute value if it exists, otherwise the default value from the schema or def_val.

        Raises:
            RuntimeError: If the schema helper is not set.
        """
        assert min_opset is not None or min_opset_def_val is None, \
            'min_opset_def_val should be None if min_opset is None'

        if self.has_attr(attr):
            return self.get_attr(attr)

        # only read defaults from schema if really needed
        # get_default_attrs is cached per op, so we don't read schemas for each attr
        if not self._schema_helper:
            raise RuntimeError(f'{self.__class__.__name__}.schema_helper attribute was not set')    # pragma: no cover

        if min_opset is not None and self._schema_helper.opset_version < min_opset:
            return min_opset_def_val

        return self._schema_helper.get_default_attrs(self.op_type)[attr]

    def is_const(self, check_quant):
        if check_quant:
            return self.op_type == OnnxOpType.Constant or self.op_type in set(OnnxMctQWeightsQuantizer)
        return self.op_type == OnnxOpType.Constant

    def get_const_data(self) -> Any:
        """ Convenience method to get data from const node"""
        if not self.is_const(check_quant=False):
            raise RuntimeError(f'method can only be called on node with op_type {OnnxOpType.Constant}')
        return self.get_attr(self.const_val_attr)

    def is_dummy_input(self):
        from uni.pytorch.onnx_parser.onnx_parser import is_dummy_input
        return is_dummy_input(self)

    def is_dummy_output(self):
        from uni.pytorch.onnx_parser.onnx_parser import is_dummy_output
        return is_dummy_output(self)

    def get_opset(self) -> int:
        """ Returns op's opset version (from model's opset) """
        if not self._schema_helper:
            raise RuntimeError('{self.__class__.__name__}.schema_helper attribute was not set')    # pragma: no cover
        return self._schema_helper.opset_version

    def is_dup_of(self, other_node):
        # checking if "self node" and "other node" has same functionality
        # not checking self attributes in [key, name, original_name, output]
        if (self.op_type != other_node.op_type or self.input != other_node.input or self.attr != other_node.attr
                or self.const_val_attr != other_node.const_val_attr or self.domain != other_node.domain
                or self.history != other_node.history):
            return False
        return True


class OnnxReaderHelper:
    """ Parses Onnx protobuf """

    @classmethod
    def parse_node(cls, onnx_node) -> OnnxMetaNode:
        node = OnnxMetaNode(onnx_node.name,
                            onnx_node.op_type,
                            list(onnx_node.input),
                            list(onnx_node.output),
                            domain=onnx_node.domain)
        try:
            if onnx_node.attribute:
                node.attr = {a.name: cls.read_attribute(a) for a in onnx_node.attribute}
        except NotImplementedError as e:
            raise NotImplementedError(
                f'Failed to parse node {onnx_node.name} of type {onnx_node.op_type} with error {e}')
        # ONNX Constant has multiple possible attributes (exactly one of which is full)
        # https://github.com/onnx/onnx/blob/main/docs/Operators.md#Constant
        # Set OnnxMetaNode.const_val_attr for easier future reading
        # Note: Variable.from_onnx skips attrs validation due to the handling here
        if onnx_node.op_type == OnnxOpType.Constant and OnnxMetaNode.const_val_attr not in node.attr:
            vals = list(node.attr.values())
            if len(vals) != 1:    # pragma: no cover
                raise ValueError(f'Could not retrieve the value for {onnx_node.op_type} node {onnx_node.name}'
                                 f'Expected a single attribute, actual{list(node.attr.keys())}')
            if is_dev():
                assert list(node.attr.keys())[0] in [
                    'value', 'value_float', 'value_floats', 'value_int', 'value_ints', 'value_string', 'value_strings'
                ]
            node.attr[OnnxMetaNode.const_val_attr] = vals[0]

        return node

    @classmethod
    def parse_initializer(cls, tensor: onnx.TensorProto) -> Tuple[str, np.ndarray]:
        # learnable params, represented by a regular tensor
        return cls.parse_tensor(tensor)

    @classmethod
    def parse_tensor(cls, tensor: onnx.TensorProto) -> Tuple[str, np.ndarray]:
        data = cls._get_tensor_data(tensor)
        return tensor.name, data

    @classmethod
    def parse_tensor_type(cls, tensor_type: onnx.ValueInfoProto) -> Tuple[str, tuple, np.dtype]:
        # tensor_typy corresponds to network inputs/outputs
        # TODO return type?
        def get_dim(dim):
            # when exporting onnx dynamic axes can be specified (axis with non-fixed size, e.g. batch)
            # for those axes dim_param will contain a string that was specified during export
            if dim.dim_param:
                return None
            return dim.dim_value

        shape = tuple([get_dim(dim) for dim in tensor_type.type.tensor_type.shape.dim])
        onnx_dtype_enum = tensor_type.type.tensor_type.elem_type
        np_dtype = onnx.mapping.TENSOR_TYPE_MAP[onnx_dtype_enum].np_dtype
        return tensor_type.name, shape, np_dtype

    @classmethod
    def read_attribute(cls, a: onnx.AttributeProto):
        # there are more weird types, that might have to be readed in special way,
        # so we'll add them one by one once encountered
        if a.type in [a.FLOAT, a.FLOATS, a.INT, a.INTS, a.STRING, a.STRINGS]:
            val = onnx.helper.get_attribute_value(a)
        elif a.type == a.TENSOR:
            val = cls._get_tensor_data(a.t)
        else:    # pragma: no cover
            raise NotImplementedError(f'Read onnx attribute (onnx.AttributeProto) of type {a.type}')

        if a.type == a.STRING:
            val = val.decode('UTF-8')
        elif a.type == a.STRINGS:
            val = [v.decode('UTF-8') for v in val]
        return val

    @staticmethod
    def get_opset_version(model: onnx.ModelProto) -> int:
        opset = [o for o in model.opset_import if o.domain == onnx.defs.ONNX_DOMAIN]
        assert len(opset) == 1
        return opset[0].version

    @staticmethod
    def get_unknown_domains(model: onnx.ModelProto) -> List[str]:
        unknown_domains = [o.domain for o in model.opset_import if o.domain not in KNOWN_DOMAINS]
        return [str(d) for d in unknown_domains]

    @staticmethod
    def get_inputs_initializers_intersection(model):
        input_names = [i.name for i in model.graph.input]
        initializer_names = [i.name for i in model.graph.initializer]
        return list(set(input_names) & set(initializer_names))

    @staticmethod
    def _get_tensor_data(tensor: onnx.TensorProto) -> np.ndarray:
        return onnx.numpy_helper.to_array(tensor)
