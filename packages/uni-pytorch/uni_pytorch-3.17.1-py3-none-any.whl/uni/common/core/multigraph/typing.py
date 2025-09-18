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
from typing import Protocol, TypeVar, Union, runtime_checkable

from uni.common.core.multigraph.edge import Edge

NodeKey = Union[str, int]


# Any object can be MultiGraph node as long as it has 'key' attribute or property that can be used as unique id
# runtime_checkable makes it usable with isinstance
@runtime_checkable
class WithKeyProperty(Protocol):
    # unique id
    @property
    def key(self) -> NodeKey:
        return 1    # pragma: no cover


@runtime_checkable
class WithKeyAttr(Protocol):
    # unique id
    key: NodeKey


WithKey = Union[WithKeyAttr, WithKeyProperty]

# Any type that can be used as MultiGraph node
# This is the way to denote any node type that implements the protocol
# and so can be used in MultiGraph or its derived graphs (without static type checking getting furious)
NodeObj = TypeVar('NodeObj', bound=WithKey)
NodeObjOrKey = Union[NodeObj, NodeKey]

EdgeObj = TypeVar('EdgeObj', bound=Edge)


def is_node_obj(node):
    return isinstance(node, (WithKeyAttr, WithKeyProperty))
