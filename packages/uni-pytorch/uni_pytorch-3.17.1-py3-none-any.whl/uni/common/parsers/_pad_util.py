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
"""
Created on 12/19/23

@author: lotanw
"""

from typing import Tuple

from uni.common.core.nnir_graph.nnir_nodes.common import Padding2d, Param2d

from enum import Enum


class ExcessPaddingLocation(Enum):
    UPPER = 1
    LOWER = 2


def calc_same_padding(input_h: int, input_w: int, kernel_size: Param2d, stride: Param2d, dilation: Param2d,
                      padding_location: ExcessPaddingLocation) -> Padding2d:
    """ Calculate explicit padding for 'same' padding """
    total_pad_h = _calc_total_axis_pad(input_h, kernel_size.h, stride.h, dilation.h)
    total_pad_w = _calc_total_axis_pad(input_w, kernel_size.w, stride.w, dilation.w)
    h_padding = _split_total_axis_pad(total_pad_h, padding_location)
    w_padding = _split_total_axis_pad(total_pad_w, padding_location)
    return Padding2d(h=h_padding, w=w_padding)


def _calc_total_axis_pad(input_size: int, kernel: int, stride: int, dilation: int) -> int:
    """ Calculate total padding along one axis. Arguments are values for that single axis """
    dilated_kernel = (kernel - 1) * dilation + 1
    mod = input_size % stride
    if mod:
        total_pad = max(dilated_kernel - mod, 0)
    else:
        total_pad = max(dilated_kernel - stride, 0)
    return total_pad


def _split_total_axis_pad(total_pad: int, padding_location: ExcessPaddingLocation) -> Tuple[int, int]:
    """ Split total axis pad to pad before and pad after
        (if total_pad is not even, bigger part will be determined by the padding_location) """
    if padding_location is None or not isinstance(padding_location, ExcessPaddingLocation):
        raise ValueError(
            f"Invalid parameter: padding_location must be of type ExcessPaddingLocation, got {padding_location}")
    smaller_part = total_pad // 2
    bigger_part = total_pad - smaller_part
    if padding_location == ExcessPaddingLocation.UPPER:
        return smaller_part, bigger_part
    return bigger_part, smaller_part
