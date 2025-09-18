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
Created on 8/31/22

@author: irenab
"""
from typing import NamedTuple, Tuple
from enum import Enum


class Param2d(NamedTuple):
    h: int
    w: int

    def __str__(self):
        return str(tuple(self))


class Padding2d(NamedTuple):
    h: Tuple[int, int] = (0, 0)
    w: Tuple[int, int] = (0, 0)

    def is_empty(self):
        return self.h == (0, 0) and self.w == (0, 0)


class PaddingStr(str, Enum):
    valid = 'valid'
    same = 'same'
