# -------------------------------------------------------------------------------
# (c) Copyright 2024 Sony Semiconductor Israel, Ltd. All rights reserved.
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
Created on 3/25/24

@author: irenab
"""
import numpy as np
from onnxruntime_extensions import onnx_op, PyCustomOpDef

# Actual ort implementation from custom-layers requires all its torch dependencies, which increases the docker
# size ~x4 which we want to avoid as it's only needed for networks that contain the custom op, and we only need the
# op to be ort-inferrable for shape inference. So we just register a dummy implementation.

for cl in ["Sony", "EdgeMDT"]:

    @onnx_op(op_type=f"{cl}::FasterRCNNBoxDecode",
             inputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_float, PyCustomOpDef.dt_float, PyCustomOpDef.dt_float],
             outputs=[PyCustomOpDef.dt_float],
             attrs={})
    def dummy_box_decode(rel_codes, anchors, scale_factors, clip_window):
        return np.zeros(rel_codes.shape, dtype=np.float32)

    @onnx_op(op_type=f"{cl}::MultiClassNMS",
             inputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_float],
             outputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_float, PyCustomOpDef.dt_int32, PyCustomOpDef.dt_int32],
             attrs={
                 "score_threshold": PyCustomOpDef.dt_float,
                 "iou_threshold": PyCustomOpDef.dt_float,
                 "max_detections": PyCustomOpDef.dt_int64,
             })
    def dummy_nms_ort(boxes, scores, score_threshold, iou_threshold, max_detections):
        batch = boxes.shape[0]
        return (np.zeros((batch, max_detections, 4)), np.zeros(
            (batch, max_detections)), np.zeros((batch, max_detections),
                                               dtype=np.int32), np.zeros((batch, 1), dtype=np.int32))

    @onnx_op(op_type=f"{cl}::MultiClassNMSWithIndices",
             inputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_float],
             outputs=[
                 PyCustomOpDef.dt_float, PyCustomOpDef.dt_float, PyCustomOpDef.dt_int32, PyCustomOpDef.dt_int32,
                 PyCustomOpDef.dt_int32
             ],
             attrs={
                 "score_threshold": PyCustomOpDef.dt_float,
                 "iou_threshold": PyCustomOpDef.dt_float,
                 "max_detections": PyCustomOpDef.dt_int64,
             })
    def dummy_nms_with_indices_ort(boxes, scores, score_threshold, iou_threshold, max_detections):
        batch = boxes.shape[0]
        return (np.zeros((batch, max_detections, 4)), np.zeros(
            (batch, max_detections)), np.zeros(
                (batch, max_detections), dtype=np.int32), np.zeros(
                    (batch, max_detections), dtype=np.int32), np.zeros((batch, 1), dtype=np.int32))
