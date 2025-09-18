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
Created on 8/8/22

@author: irenab
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Sequence, Iterable, NamedTuple, Optional, List

from uni.common.core.common import OpInfo


class UnsupportedError(Exception):
    """ Base class for Unsupported exceptions """
    pass


class ErrorInfo:
    reason: str


@dataclass
class ParamErrorInfo(ErrorInfo):
    """ Info about an error for a single param of an op """
    name: str
    value: Any
    reason: str

    def __str__(self):
        return f'Param error - param: {self.name}, value: {self.value}, reason: {self.reason}'


@dataclass
class OpInputErrorInfo(ErrorInfo):
    """ Invalid input for op """
    input_index: int
    input_name: str
    reason: str

    def __str__(self):
        return f'Input error - input index: {self.input_index}, input node: {self.input_name}, reason: {self.reason}'


@dataclass
class OpOutputErrorInfo(ErrorInfo):
    """ Invalid output for op. Can refer to output tensor or to output op """
    output_index: int
    output_name: str
    reason: str

    def __str__(self):
        return f'Output error - output index: {self.output_index}, ' \
               f'output tensor/node: {self.output_name}, reason: {self.reason}'


@dataclass
class OpIncorrectNumberOfInputsErrorInfo(ErrorInfo):
    """ Missing inputs for op (in case onnx allow less o more inputs) """
    expected_num_inputs: List[int]
    actual_num_inputs: int
    reason: str

    def __str__(self):
        return f'Incorrect number of inputs error - expected: {self.expected_num_inputs},' \
               f' actual: {self.actual_num_inputs}, reason: {self.reason}'


class OpErrorsInfo(NamedTuple):
    """ Info about all error for a single op """
    op_info: OpInfo
    errors: Sequence[ErrorInfo]
    orig_op_info: Optional[OpInfo] = None

    @staticmethod
    def _format_op_info(op_info):
        s = ''
        if op_info.framework:
            s = f'[{op_info.framework}] '
        s += f'op: {op_info.op}, id: {op_info.node_id}'
        return s

    def __str__(self):
        msg = 'Node ' + self._format_op_info(self.op_info)
        if self.orig_op_info:
            orig_op = self.orig_op_info
            assert orig_op.node_id and orig_op.op and orig_op.framework
            if orig_op.node_id != self.op_info.node_id or orig_op.op != self.op_info.op:
                msg += ', ' + self._format_op_info(self.orig_op_info)
        msg += ', errors:\n\t'
        msg += '\n\t'.join(str(e) for e in self.errors)
        return msg


class InvalidOpError(UnsupportedError):
    """ Exception: errors for a single Op """

    def __init__(self, op_errors: OpErrorsInfo):
        self.op_errors = op_errors


class InvalidOpsError(UnsupportedError):
    """ Exception: All Ops with invalid params """

    def __init__(self, ops: Sequence[OpErrorsInfo]):
        self.ops = ops

    def __str__(self):
        return '\n'.join(str(op) for op in self.ops)


class UnsupportedOpsError(UnsupportedError):
    """ Exception: Unsupported ops """

    def __init__(self, ops: Iterable[str]):
        self.ops = sorted(ops)


class ModelErrorInputMessages(Enum):
    BATCH_SIZE_ERR = "Batch size > 1"
    DYNAMIC_INPUT_ERR = "Dynamic input tensor shape"

    def get_reason(self, input_idx: int) -> str:
        if self == ModelErrorInputMessages.BATCH_SIZE_ERR:
            return f"The provided model input: {input_idx} has batch-size > 1." \
                    " MCT currently supports batch-size of 1 only."
        if self == ModelErrorInputMessages.DYNAMIC_INPUT_ERR:
            return f"The provided model input: {input_idx} has a dynamic input tensor shape. " \
                   "MCT currently supports models with constant input tensor size."
        raise NotImplementedError(f"Unsupported error message: {self}")


class UnsupportedModelInputError(UnsupportedError):
    """ Exception: Unsupported model input """

    def __init__(self, input_idx: int, reason: ModelErrorInputMessages):
        self.reason = ModelErrorInputMessages.get_reason(reason, input_idx)
        super().__init__(self.reason)
