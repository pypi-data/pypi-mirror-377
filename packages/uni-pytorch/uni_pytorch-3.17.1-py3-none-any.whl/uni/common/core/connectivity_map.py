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
from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import List, NamedTuple, Optional, Tuple

import numpy as np

from uni.common.logger import trace_method


class ConnectivityMap:

    def __init__(self):
        """ build a map containing source and target nodes and ordinals of each tensor
         """
        self.tensors = defaultdict(Tensor)    # type: defaultdict

    def __getitem__(self, key):
        return self.tensors[key]

    def items(self):
        return self.tensors.items()

    def values(self):
        return self.tensors.values()

    @trace_method
    def add_source(self, tensor_id, node_name, index, shape=None, dtype=None):
        assert tensor_id and node_name
        t = self.tensors[tensor_id]
        if t.src:
            raise RuntimeError(f't.src for {tensor_id} already exists')
        t.src = Connection(node_name, index)
        self.add_shape(tensor_id, shape)
        self.add_dtype(tensor_id, dtype)

    @trace_method
    def add_dest(self, tensor_id, node_name, index, shape: Optional[Tuple] = None, dtype: Optional[np.dtype] = None):
        assert tensor_id and node_name
        t = self.tensors[tensor_id]
        if t.dest and [d for d in t.dest if d.name == node_name and d.index == index]:
            raise RuntimeError(f't.dest for {tensor_id} already exists')
        t.dest.append(Connection(node_name, index))
        self.add_shape(tensor_id, shape)
        self.add_dtype(tensor_id, dtype)

    def add_shape(self, tensor_id, shape: Optional[Tuple]):
        assert tensor_id
        if shape is None:
            return
        t = self.tensors[tensor_id]
        if t.shape not in [None, shape]:
            raise RuntimeError(f'Conflicting t.shape for {tensor_id}. Previously set {t.shape}, new {shape}.')
        t.shape = shape

    def add_dtype(self, tensor_id, dtype: Optional[np.dtype]):
        assert tensor_id
        if dtype is None:
            return
        t = self.tensors[tensor_id]
        if t.np_dtype not in [None, dtype]:
            raise RuntimeError(f'Conflicting t.dtype for {tensor_id}. Previously set {t.np_dtype}, new {dtype}.')
        t.np_dtype = dtype

    def update(self, other):
        # Assert that no keys in other.tensors are in self.tensors
        assert all(key not in self.tensors for key in other.tensors), "Some tensors are already present in self.tensors"
        self.tensors.update(other.tensors)

    def clone_with_new_names(self, new_tensor_names, suffix):
        new_map = ConnectivityMap()
        for tensor_id, tensor in self.tensors.items():
            kwargs = {}
            if tensor.src:
                kwargs['src'] = Connection(new_tensor_names[tensor.src.name], tensor.src.index)
            kwargs['dest'] = [Connection(new_tensor_names[d.name], d.index) for d in tensor.dest]    # type: ignore
            new_tensor = tensor.clone(**kwargs)
            new_map.tensors[tensor_id + suffix] = new_tensor
        return new_map


class Connection(NamedTuple):
    """ Represents edge connection to node, either outgoing or incoming
        for src -> (edge1, edge2) -> dest there are 4 connections: (src, 0), (src, 1), (dest, 0), (dest, 1) """
    name: str
    index: int    # type: ignore # Incompatible types in assignment


@dataclass
class Tensor:
    """ Tensor's connectivity info
        Can have a single source, but can be shared among several outputs """
    src: Optional[Connection] = None
    dest: List[Connection] = field(default_factory=list)
    shape: Optional[Tuple] = None
    np_dtype: Optional[np.dtype] = None

    def clone(self, **kwargs):
        return replace(self, **kwargs)
