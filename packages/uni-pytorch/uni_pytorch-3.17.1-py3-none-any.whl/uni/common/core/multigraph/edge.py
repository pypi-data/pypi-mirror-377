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
Created on 8/4/22

@author: irenab
"""
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, replace

import numpy as np

if TYPE_CHECKING:
    from .typing import NodeKey


# eq + frozen make the class hashable
@dataclass(eq=True, frozen=True)
class Edge:
    """
    Base class for Edge object supported by MultiDiGraph
    Shape is optional - it's not strictly required by MultiDiGraph,
    but it can provide convenience services if it exists
    """
    src: 'NodeKey'    # source node key
    dest: 'NodeKey'    # dest node key
    src_index: int    # index of corresponding output of the source node
    dest_index: int    # index of corresponding input of the target node
    shape: Optional[tuple] = None    # tensor shape
    np_dtype: Optional[np.dtype] = None    # numpy dtype

    def clone(self, **kwargs):
        return replace(self, **kwargs)

    def __str__(self):
        return f'({self.src}:{self.src_index} -> {self.dest}:{self.dest_index})'

    def equal_by_connectivity(self, other):
        """ Equality between src, src_index, dest, dest_index """
        return self.src == other.src and self.dest == other.dest and \
            self.src_index == other.src_index and self.dest_index == other.dest_index
