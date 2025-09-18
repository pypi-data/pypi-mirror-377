# -------------------------------------------------------------------------------
# (c) Copyright 2025 Sony Semiconductor Israel, Ltd. All rights reserved.
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
import json
from dataclasses import dataclass, field
from json import JSONEncoder, dumps
from typing import Optional, List
from uni_model import UniModel, UniGraph, UniLayer

ALLOCATIONS = 'allocations'
HAS_SCRATCH = 'hasScratch'
OUTPUT_SIZES = 'outputSizes'


def has_scratch(layer: UniLayer):
    return layer.extended_attr.get(HAS_SCRATCH, False)


def has_allocation(layer: UniLayer):
    return layer.extended_attr.get(ALLOCATIONS, False)


def get_allocation(layer: UniLayer):
    return AllocationDataPerLayer.decode_from_json(layer.extended_attr.get(ALLOCATIONS))




def get_schedule(node: UniLayer):
    if has_allocation(node):
        return get_allocation(node).schedule
    else:
        raise ValueError(f"Node {node.name} missing 'allocation'")


def get_scratch_cut(node: UniLayer):
    if has_allocation(node):
        return get_allocation(node).scratchCutTensorIds
    else:
        raise ValueError(f"Node {node.name} missing 'allocation'")


def get_cut(node: UniLayer):
    if has_allocation(node):
        return get_allocation(node).cutTensorIds
    else:
        raise ValueError(f"Node {node.name} missing 'allocation'")


@dataclass
class OutputAllocation:
    tensorId: str
    layerName: str
    outputIndex: int
    dynamicMemory: int
    staticMemory: int
    offset: Optional[int] = None


@dataclass
class AllocationDataPerLayer:
    schedule: int
    dynamicMemory: int
    cutTensorIds: list[str] = field(default_factory=list)
    scratchCutTensorIds: list[str] = field(default_factory=list)
    outputSizes: list[OutputAllocation] = field(default_factory=list)

    def encode_to_json(self) -> str:
        d = self.__dict__.copy()
        d[OUTPUT_SIZES] = [o.__dict__ for o in d[OUTPUT_SIZES]]
        return json.dumps(d)

    @staticmethod
    def decode_from_json(j: str) -> 'AllocationDataPerLayer':
        d = json.loads(j)
        d[OUTPUT_SIZES] = [OutputAllocation(**o) for o in d[OUTPUT_SIZES]]
        return AllocationDataPerLayer(**d)


def set_allocation(layer: UniLayer, alloc_data: AllocationDataPerLayer):
    layer.extended_attr[ALLOCATIONS] = alloc_data.encode_to_json()


if __name__ == "__main__":
    a = AllocationDataPerLayer(
        schedule=4,
        dynamicMemory=9,
        cutTensorIds=["t1", "t2"],
        scratchCutTensorIds=["t2"],
        outputSizes=[
            OutputAllocation(tensorId="t1", layerName="layerX", outputIndex=0, dynamicMemory=10, staticMemory=5)
        ]
    )
    encoded = a.encode_to_json()
    print("Serialized:", encoded)

    decoded = AllocationDataPerLayer.decode_from_json(encoded)
    print("Deserialized:", decoded)
