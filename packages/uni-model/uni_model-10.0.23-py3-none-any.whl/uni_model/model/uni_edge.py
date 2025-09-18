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
'''
Created on 10/3/22

@author: zvikaa
'''
from uni_model.model.uni_layer import UniLayer
from dataclasses import dataclass

@dataclass(frozen=True)
class UniEdgeKey:
    from_node: str
    from_index: int
    to_node: str
    to_index: int

class UniEdge:
    def __init__(self, from_node: UniLayer, from_index: int, to_node: UniLayer, to_index: int):
        self.from_node = from_node
        self.from_index = from_index
        self.to_node = to_node
        self.to_index = to_index

    def to_key(self)-> UniEdgeKey:
        return UniEdgeKey(self.from_node.name, self.from_index, self.to_node.name, self.to_index)

    def desc(self)->str:
        return f"from {self.from_node.name}:{self.from_index} to {self.to_node.name}:{self.to_index}"

    def __eq__(self, other):
        if not isinstance(other, UniEdge):
            return False
        if self.from_node != other.from_node or self.from_index != other.from_index or \
                self.to_node != other.to_node or self.to_index != other.to_index:
            return False
        return True

    def __lt__(self, other):
        return self.desc() < other.desc()

    def __hash__(self):
        return hash(self.to_key())
