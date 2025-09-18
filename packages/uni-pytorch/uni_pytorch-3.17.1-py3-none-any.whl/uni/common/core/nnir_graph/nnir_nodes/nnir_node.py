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
Created on 6/15/22

@author: irenab
"""
from typing import Optional, final, Union, List, Tuple, TYPE_CHECKING, Dict
import abc

from uni.common.core.nnir_graph.quant_info import QuantInfoBase
from uni.common.core.node_history import NodeHistory
from uni.common.core.nnir_graph.semantics import SemanticsHelper, Semantics, AxisSemantics, DataFormat
from uni.common.core.multigraph.node_graph_api import NodeGraphContext
from uni.common.core.common import OpInfo, Framework
from uni.common.core import error
from uni.common.core.error import OpInputErrorInfo, OpOutputErrorInfo, ParamErrorInfo, raise_op_error, \
    supported_vals_msg, exceeds_limit_msg

if TYPE_CHECKING:
    from uni.common.core.nnir_graph.nnir_edge import NnirEdge


class NnirNode(abc.ABC):
    NUM_INPUTS: Union[Optional[int], List[int]]
    NUM_OUTPUTS: Union[Optional[int], List[int]]

    batch_size = 1
    valid_batch = [None, batch_size]
    max_2d_op_h_size = 2**15 - 1    # common limitation for 2d ops with kernel

    error_input_dim_size = lambda axis, limit: exceeds_limit_msg(f'{axis} size', limit)    # noqa: 471
    error_out_dim_size = lambda axis_name, limit: exceeds_limit_msg(f'Output {axis_name} size', limit)    # noqa: E731

    last_axis_error = "only last axis allowed"

    @classmethod
    def error_invalid_shape(cls, shape):
        return f'Invalid shape of {shape}. Shape must contain batch and at least one more dimension.'

    @classmethod
    def error_invalid_batch(cls, b):
        return f'Invalid batch dim {b}. {supported_vals_msg(cls.valid_batch)}'

    def error_op_along_batch_axis(self):
        return f'{self.op} along batch is invalid'

    def error_not_network_output(self, out_idx, is_last_node):
        msg = f'Output {out_idx} of {self.op} followed by non quantization layer is invalid.'
        if is_last_node:
            msg += f' {self.op} should be the last layer in the network, or followed by quantization.'
        return msg

    def get_uni_model_num_outputs(self):
        if self.NUM_OUTPUTS is None:
            return 1
        return self.NUM_OUTPUTS

    def __init__(self, name, history: Optional[NodeHistory] = None, **kwargs):
        self.name = name
        self.history = history
        self._graph_ctx: Optional[NodeGraphContext] = None
        self._data_format: Optional[DataFormat] = None
        out_size = self.get_uni_model_num_outputs()
        self._quant_list: List[Optional[QuantInfoBase]] = [None] * out_size
        self.output_semantics = Semantics(*[None] * out_size)

    @property
    def quant_list(self) -> List[Optional[QuantInfoBase]]:
        return self._quant_list

    def get_quant(self, idx: int):
        # for case that NUM_OUTPUTS is None
        if len(self._quant_list) == 1:
            idx = 0
        return self._quant_list[idx]

    def set_quant(self, quant, idx: int, override: bool = False):
        # for case that NUM_OUTPUTS is None
        if len(self._quant_list) == 1:
            idx = 0
        assert override or self._quant_list[idx] in [None, quant]
        self._quant_list[idx] = quant

    def set_semantics(self, tensor_semantics, idx: int):
        if len(self.output_semantics) == 1:
            idx = 0
        assert self.output_semantics[idx] in [None, tensor_semantics]
        self.output_semantics[idx] = tensor_semantics

    @property
    def key(self):
        return self.name

    @property
    def op(self):
        return self.__class__.__name__

    def op_info(self):
        return OpInfo(node_id=self.name, op=self.op, framework=Framework.nnir)

    def is_identity(self) -> bool:
        """ If True, the node instance will be removed from NnirGraph by remove_identity """
        return False

    def is_const(self) -> bool:
        """
            determines whether the node is instance of Variable (const)
        """
        return self.op == 'Variable'

    @property
    def graph_ctx(self) -> NodeGraphContext:
        if not self._graph_ctx:
            raise RuntimeError('graph_ctx property was not set')
        return self._graph_ctx

    @graph_ctx.setter
    def graph_ctx(self, ctx: NodeGraphContext):
        self._graph_ctx = ctx

    @property
    def data_format(self):
        if self._data_format is None:
            raise RuntimeError('data_format was not set')
        return self._data_format

    @data_format.setter
    def data_format(self, data_format):
        self._data_format = data_format

    @final
    def validate(self) -> None:
        """ Node validation (after nnir graph is complete) """
        if self.NUM_INPUTS is not None:
            if isinstance(self.NUM_INPUTS, int):
                assert self.graph_ctx.get_in_degree() == self.NUM_INPUTS, self
            else:
                assert self.graph_ctx.get_in_degree() in self.NUM_INPUTS, self
        if self.NUM_OUTPUTS is not None:
            if isinstance(self.NUM_OUTPUTS, int):
                assert self.graph_ctx.get_out_degree() == self.NUM_OUTPUTS, self
            else:
                assert self.graph_ctx.get_out_degree() in self.NUM_OUTPUTS, self
        self._validate()

    def _validate(self):
        """ Concrete node validation. graph_ctx is available at this point
            Note: all validation should be done here, even if graph_ctx is not required
            (any validation in c'tor will be reported together with framework errors) """
        pass

    def raise_op_param_error(self, name, value, reason):
        error.raise_op_param_error(self.op_info(), name, value, reason, self.history)

    def validate_batch(self,
                       input_index: Optional[int] = None,
                       return_error: bool = False) -> Optional[OpInputErrorInfo]:
        """ Validate batch value in shape is valid
            input_index: index of the input tensor to validate. Default can be left only if an op has 1 input.
            return_error: whether to return error object (so that it can be aggregated with other errors)
                          or raise an error. By default, raises an error.
        """
        assert input_index is not None or self.NUM_INPUTS == 1, 'pass input_index for op with more than one input '
        if input_index is None:
            input_index = 0

        input_shape = self.graph_ctx.get_in_shapes()[input_index]
        if len(input_shape) >= 2 and input_shape[0] in self.valid_batch:
            return None
        input_node: NnirNode = self.graph_ctx.get_in_nodes()[input_index]
        # not enough dimensions
        if len(input_shape) < 2:
            reason = self.error_invalid_shape(input_shape)
        # invalid batch values
        else:
            reason = self.error_invalid_batch(input_shape[0])
        err = OpInputErrorInfo(input_index=input_index, input_name=input_node.name, reason=reason)
        if return_error is False:
            raise_op_error(self.op_info(), errors=[err], history=self.history)

        return err

    def validate_last_index_axis(self, axis, shape, return_error: bool = False) -> Optional[ParamErrorInfo]:
        err = ParamErrorInfo("axis", 1, self.last_axis_error)
        last_axis = len(shape) - 1
        if axis in [-1, last_axis]:
            return None
        if return_error is False:
            raise_op_error(self.op_info(), errors=[err], history=self.history)
        return err

    def validate_input_dim_size(self, input_index, axis_index, upper_limit, return_error: bool = False):
        size_in = self.graph_ctx.get_in_shapes()[input_index][axis_index]
        if size_in > upper_limit:
            input_node: NnirNode = self.graph_ctx.get_in_nodes()[input_index]
            reason = self.__class__.error_input_dim_size(f'Axis {axis_index}', upper_limit)
            err = OpInputErrorInfo(input_index=input_index, input_name=input_node.name, reason=reason)
            if return_error is False:
                raise_op_error(self.op_info(), errors=[err], history=self.history)
            else:
                return err

    def validate_data_dim_size(self,
                               axis: AxisSemantics,
                               upper_limit: int,
                               input_index: int = 0,
                               output_index: int = 0,
                               return_error: bool = False) -> Union[OpInputErrorInfo, OpOutputErrorInfo, None]:
        """ Validate that dim input and output sizes does not exceed the upper limit (dim_size <= upper_limit)
            axis: axis to validate
            upper_limit: dim size upper limit
            input_index: index of the input data tensor to validate
            output_index: index of the output data tensor to validate
            return_error: whether to return error object (so that it can be aggregated with other errors)
                          or raise an error. By default, raises an error.
        """
        axis_index = SemanticsHelper(self.data_format).axis_by_semantics(axis)
        size_in = self.graph_ctx.get_in_shapes()[input_index][axis_index]
        size_out = self.graph_ctx.get_out_shapes()[output_index][axis_index]
        err = None    # type: Optional[Union[OpInputErrorInfo, OpOutputErrorInfo]]
        if size_in > upper_limit:
            input_node: NnirNode = self.graph_ctx.get_in_nodes()[0]
            reason = self.__class__.error_input_dim_size(axis.name.lower(), upper_limit)
            err = OpInputErrorInfo(input_index=input_index, input_name=input_node.name, reason=reason)
        elif size_out > upper_limit:
            reason = self.__class__.error_out_dim_size(axis.name.lower(), upper_limit)
            err = OpOutputErrorInfo(output_index=output_index, output_name='data tensor', reason=reason)

        if not err:
            return None

        if return_error is False:
            raise_op_error(self.op_info(), errors=[err], history=self.history)
        return err

    def validate_non_batch_op_axis(self, axis, input_index=None, return_error: bool = False):
        """ Checks that op axis is not batch """
        assert input_index is not None or self.NUM_INPUTS == 1, 'pass input_index for op with more than one input '
        if input_index is None:
            input_index = 0

        orig_axis = axis
        if axis < 0:
            rank = len(self.graph_ctx.get_in_shapes()[input_index])
            axis = rank + axis
        if axis == 0:
            error = ParamErrorInfo(name='axis', value=orig_axis, reason=self.error_op_along_batch_axis())
            if return_error:
                return error
            raise_op_error(self.op_info(), errors=[error], history=self.history)

    # this is checking recursively if all outputs leads to valid nodes
    def _check_leads_to_outputs(self, node):
        # python does not reimport in recursive functions
        from uni.common.core.nnir_graph.nnir_nodes import Output, DummyOutput, Identity, Quant
        if isinstance(node, (Output, DummyOutput)):
            return True
        if isinstance(node, (Identity, Quant)):
            # the Identity/Quant node have only 1 output
            return self._check_leads_to_outputs(list(node.graph_ctx.get_out_nodes().values())[0][0])
        return False

    def validate_node_output_is_network_output(self, idx_list: Optional[List[int]] = None, return_error: bool = False):
        """ If idx_list is passed, only those outputs are checked. If None, all outputs are checked. """
        errors: List[OpOutputErrorInfo] = []
        out_nodes: Dict[int, List[NnirNode]] = self.graph_ctx.get_out_nodes()
        idx_list = idx_list or list(range(len(out_nodes)))
        is_last_node = set(idx_list) == set(range(len(out_nodes)))
        for out_idx in idx_list:
            if any(not self._check_leads_to_outputs(n_leads_to_output) for n_leads_to_output in out_nodes[out_idx]):
                errors.append(
                    OpOutputErrorInfo(output_name="output",
                                      output_index=out_idx,
                                      reason=self.error_not_network_output(out_idx, is_last_node)))
        if return_error:
            return errors
        if errors:
            raise_op_error(self.op_info(), errors, self.history)

    def get_input_semantics(self, semantics_helper: SemanticsHelper) -> Optional[Semantics]:
        """ Retrieves semantics of the node inputs
            Should be implemented only for nodes with framework dependent semantics """
        return None

    def set_output_semantics(self, semantics_helper: SemanticsHelper):
        """ Set semantics of the node outputs
            Should be implemented only for nodes with framework dependent semantics """
        pass

    @abc.abstractmethod
    def export_uni_model(self):
        """ generate uni model node """
        raise NotImplementedError(self.__class__)

    def get_uni_model_out_dtypes(self):
        from uni.common.exporters.uni_model.util import UniModelUtils
        res = [UniModelUtils.get_float_type() for _ in enumerate(self.quant_list)]
        for idx, quant in enumerate(self.quant_list):
            if quant:
                res[idx] = quant.export_uni_model()
        return res

    def get_uni_model_input_data_layout(self):
        from uni_model import DataFormat as UniDataFormat
        if self.data_format == DataFormat.HWC:
            return UniDataFormat.HWC
        elif self.data_format == DataFormat.CHW:
            return UniDataFormat.CHW
        else:
            raise ValueError(f'Unsupported data format: {self.data_format}')

    def substitute(self) -> Optional[Tuple[List['NnirNode'], List['NnirEdge']]]:
        """
        Substitute the node with a subgraph. Must not directly modify the graph in any way.

        Returns:
            None if no substitution is needed
            A tuple of new nodes and new edges, including edges replacing all connections of the original node to the
            rest of the graph
        """
        return None

    @classmethod
    def has_substitution(cls) -> bool:
        return cls.substitute != NnirNode.substitute

    def __str__(self):
        return f'{self.__class__.__name__}:{self.name}'
