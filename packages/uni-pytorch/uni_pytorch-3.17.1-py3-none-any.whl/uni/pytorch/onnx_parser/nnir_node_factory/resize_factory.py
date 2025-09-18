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
from typing import Tuple, List, Any

from uni.common.core.error import ParamErrorInfo, OpIncorrectNumberOfInputsErrorInfo, ErrorInfo
from uni.common.core.multigraph.node_graph_api import GraphRequest
from ._op2d_mixin import OnnxOp2dMixin
from uni.pytorch.onnx_parser.nnir_node_factory.base_factory import OnnxFactoryBase, validate_onnx
from uni.common.core.nnir_graph.nnir_nodes.resize import Resize, ResizeMode

from uni.common.core.error.util import supported_vals_msg, raise_op_error

opset_13_optional_attrs = [
    'coordinate_transformation_mode', 'cubic_coeff_a', 'exclude_outside', 'extrapolation_value', 'mode', 'nearest_mode'
]
opset_18_optional_attrs = ['antialias', 'axes', 'keep_aspect_ratio_policy']


class OnnxResizeToNnirNode(OnnxFactoryBase, OnnxOp2dMixin):
    """
    https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Resize-13
    https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Resize-18
    https://github.com/onnx/onnx/blob/main/docs/Changelog.md#Resize-19
    opset 18:
        new attributes 'antialias', 'axes', 'keep_aspect_ratio_policy'

    cubic_coeff_a is only relevant to cubic mode that is not supported
    extrapolation_value is only relevant to tf_crop_and_resize that is not supported

    onnx docs is a confusing about 1-2 inputs (x and roi  without scale and sizes)
    onnx 12 is working but onnx 13 is fail in validation,
    so we're allowing only 3-4 inputs (x, roi, scale and sizes)
    """
    exclude_outside_vals = [0]
    antialias_vals = [0]
    keep_aspect_ratio_policy_vals = ['stretch']
    # mode and coordinate_transformation_mode
    mode_ctm_vals = {'linear': ['half_pixel', 'pytorch_half_pixel'], 'nearest': ['asymmetric']}
    nearest_mode_vals = ['floor']

    invalid_inputs_msg = "One of 'scales' or 'sizes' inputs must be present"
    invalid_axes_msg = ("Axes must be a list of integers in the range [0, rank-1]."
                        " Negative values are allowed, but the axes must be in order.")

    @classmethod
    @validate_onnx(num_inputs=[1, 2, 3, 4],
                   num_outputs=1,
                   attrs=[],
                   optional_attrs=opset_13_optional_attrs + opset_18_optional_attrs,
                   opset_limits=(13, 20))
    def from_onnx(cls, onnx_node, graph_ctx=None) -> Tuple[Resize, GraphRequest]:
        """ Creates node instance from OnnxMetaNode """

        errors: List[ErrorInfo] = []

        def check_error(attr, supported_vals: List[Any], min_opset=None, def_val=None):
            val = onnx_node.get_attr_with_default_from_schema(attr, min_opset, def_val)
            if val not in supported_vals:
                msg = supported_vals_msg(supported_vals)
                err = ParamErrorInfo(name=attr, value=val, reason=msg)
                errors.append(err)
                return err
            return None

        # verify inputs have scales' or 'sizes
        in_nodes = graph_ctx.get_in_nodes()
        actual_inputs = {i: node for i, node in enumerate(in_nodes) if not node.is_dummy_input()}
        actual_num_inputs = max(actual_inputs.keys()) + 1    # keys in zero base
        if actual_num_inputs < 3:
            err = OpIncorrectNumberOfInputsErrorInfo(expected_num_inputs=[3, 4],
                                                     actual_num_inputs=len(in_nodes),
                                                     reason=cls.invalid_inputs_msg)
            errors.append(err)

        cls.validate_2d_op_data_shape(onnx_node, graph_ctx)
        check_error("exclude_outside", cls.exclude_outside_vals)
        mode = onnx_node.get_attr_with_default_from_schema("mode")
        mode_vals = list(cls.mode_ctm_vals.keys())
        if check_error("mode", mode_vals) is None:
            check_error("coordinate_transformation_mode", cls.mode_ctm_vals[mode])
        if mode == 'nearest':
            check_error("nearest_mode", cls.nearest_mode_vals)

        check_error("antialias", cls.antialias_vals, min_opset=18, def_val=0)
        check_error("keep_aspect_ratio_policy", cls.keep_aspect_ratio_policy_vals, min_opset=18, def_val='stretch')
        axes = onnx_node.get_attr_with_default("axes", None)
        in_rank = len(graph_ctx.get_in_shapes()[0])
        if not cls.validate_full_axes(axes, in_rank):
            errors.append(ParamErrorInfo(name="axes", value=axes, reason=cls.invalid_axes_msg))

        if errors:
            raise_op_error(cls.onnx_op_info(onnx_node), errors=errors, history=None)

        mode_dict = {'nearest': ResizeMode.NEAREST, 'linear': ResizeMode.BILINEAR}
        if mode not in mode_dict:
            RuntimeError(f"Resize mode {mode} is not supported")
        resize_mode = mode_dict[mode]

        req = GraphRequest(inputs_to_detach=list(range(len(graph_ctx.get_in_nodes())))[1:])

        hout, wout = cls._get_hout_wout(graph_ctx)
        node = Resize(name=onnx_node.name, target_height=hout, target_width=wout, mode=resize_mode)
        node.data_format = cls.data_format
        return node, req

    @classmethod
    def _get_hout_wout(cls, graph_ctx):
        # roi,scales and sizes are ignored because we get hout, wout from get_out_shapes
        h_index, w_index = cls.data_format.get_hw_axes()
        out_shape = graph_ctx.get_out_shapes()[0]
        hout, wout = out_shape[h_index], out_shape[w_index]
        return hout, wout

    @staticmethod
    def validate_full_axes(axes, in_rank):
        if axes is None:
            return True
        if len(axes) != in_rank:
            return False
        axes = [a if a >= 0 else a + in_rank for a in axes]
        return list(axes) == list(range(in_rank))
