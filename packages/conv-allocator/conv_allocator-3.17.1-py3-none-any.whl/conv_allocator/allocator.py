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
import argparse
import math
import os
import csv
import json
import time
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import FIXED_SEARCH
from uni_model import GraphDefToUniModelConverter
from uni_model import UniModelToGraphDefConverter
from collections import defaultdict
from typing import List, Dict, Set
import json
from uni_model import UniModelPath

from conv_allocator.um_accessors import has_scratch, has_allocation, get_allocation, get_schedule, get_scratch_cut, get_cut, \
    set_allocation


@dataclass(eq=False)
class Block:
    layer_name: str
    output_index: int
    dynamic_memory: int
    static_memory: int
    offset: int
    tensor_id: str

    def __repr__(self):
        return (f"Block({self.layer_name}, {self.output_index}, "
                f"tensorId={self.tensor_id}, dynMem={self.dynamic_memory}, offset={self.offset})")

    def __eq__(self, other):
        return isinstance(other, Block) and (self.tensor_id == other.tensor_id)

    def __hash__(self):
        return hash((self.layer_name, self.output_index))


# Filter out layers without output and allocations
def filter_relevant_nodes(nodes):
    excluded_classes = {'UniLayerConst'}

    def is_relevant(node):
        class_name = node.__class__.__name__
        if class_name in excluded_classes:
            return False
        return True

    return [node for node in nodes if is_relevant(node)]


def validate_allocation_data(nodes):
    for node in nodes:
        name = getattr(node, 'name', '<unknown>')

        if not has_allocation(node):
            raise ValueError(f"Node {name} missing 'allocations'")

        try:
            loaded_allocation = get_allocation(node)
        except Exception:
            raise ValueError(f"Node {name} has invalid 'allocations'")

        if loaded_allocation.schedule is None:
            raise ValueError(f"Node {name} missing 'schedule'")

        if loaded_allocation.outputSizes is None:
            raise ValueError(f"Node {name} missing 'outputSizes'")


def down_scale(out, scale):
    return math.ceil(out.dynamicMemory/scale)

def parse_blocks_from_node(node, scale):
    allocations_data = get_allocation(node)
    blocks = [
        Block(
            out.layerName,
            out.outputIndex,
            down_scale(out, scale),
            out.staticMemory,
            out.offset,
            out.tensorId
        )
        for out in allocations_data.outputSizes
    ]
    return blocks


def create_fake_scratch_node(real_node):
    class FakeScratchNode:
        def __init__(self, source_node):
            self.source_real_node = source_node
            self.name = f"{source_node.name}_scratch"

    return FakeScratchNode(real_node)


def build_graph_cuts(unimodel, scale):
    graph = unimodel.uni_graphs[0]
    filtered_nodes = filter_relevant_nodes(graph.layer_nodes)
    validate_allocation_data(filtered_nodes)

    # Step 1: Sort by schedule
    sorted_nodes = sorted(filtered_nodes, key=get_schedule)

    # Step 2: Parse blocks from sorted nodes
    all_blocks_by_node = {}
    blocks_map = {}
    for node in sorted_nodes:
        blocks = parse_blocks_from_node(node, scale)
        all_blocks_by_node[node] = blocks
        for block in blocks:
            blocks_map[block] = node

    # Step 3: Handle scratch layers, preserving order
    scratch_fake_nodes = []
    ordered_nodes_with_scratch = []

    for node in sorted_nodes:
        ordered_nodes_with_scratch.append(node)
        if has_scratch(node):
            scratch_node = create_fake_scratch_node(node)
            scratch_fake_nodes.append(scratch_node)
            ordered_nodes_with_scratch.append(scratch_node)

    # Step 4: Use precomputed graph cuts from node metadata
    tensor_id_to_block = {block.tensor_id: block for block in blocks_map}
    graph_cuts = []

    for node in ordered_nodes_with_scratch:
        if hasattr(node, 'source_real_node'):  # Scratch fake node
            real_node = node.source_real_node
            scratch_ids = get_scratch_cut(real_node)
            block_set = {tensor_id_to_block[tid] for tid in scratch_ids}
        else:
            cut_ids = get_cut(node)
            block_set = {tensor_id_to_block[tid] for tid in cut_ids}

        graph_cuts.append(block_set)

    return graph_cuts, blocks_map


def solve_allocation(graph_cuts, blocks, time_limit):
    """
    Solve the memory allocation problem using CP-SAT solver.

    Args:
        graph_cuts: List of sets, each set contains block IDs that need to be in memory simultaneously
        blocks: Dictionary mapping block ID to its size

    Returns:
        Dictionary mapping block ID to (start_time, end_time)
    """

    start_time = time.time()

    # Estimate horizon (safe upper bound on end time)
    horizon = int(sum(block.dynamic_memory for block in blocks) * 2)

    model = cp_model.CpModel()

    # Create variables for each block
    block_dict = {}
    for block in blocks.keys():
        block_id = block.tensor_id
        block_size = block.dynamic_memory

        start_var = model.NewIntVar(0, horizon, f"start_{block_id}")
        end_var = model.NewIntVar(0, horizon, f"end_{block_id}")
        interval_var = model.NewIntervalVar(start_var, block_size, end_var, f"interval_{block_id}")

        block_dict[block] = (start_var, end_var, interval_var)

    # Solver setup
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 17
    solver.parameters.randomize_search = False
    solver.parameters.use_absl_random = False
    solver.parameters.num_workers = 1

    # fixed strategy - works with fixed_search
    # activation_vars = [start for start, _, _ in block_dict.values()]
    # model.AddDecisionStrategy(
    #     activation_vars,
    #     cp_model.CHOOSE_LOWEST_MIN,
    #     cp_model.SELECT_MIN_VALUE
    # )
    # solver.parameters.search_branching = cp_model.FIXED_SEARCH


    # Use AddNoOverlap per graph cut
    for cut in graph_cuts:
        cut_intervals = [block_dict[block][2] for block in cut]
        model.AddNoOverlap(cut_intervals)

    # Objective: minimize makespan (max end address)
    obj_var = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(obj_var, [end for _, end, _ in block_dict.values()])
    model.Minimize(obj_var)

    # Solution callback
    class SolutionCallback(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self._solution_count = 0
            self.latest_solution = None

        def on_solution_callback(self):
            self._solution_count += 1
            self.latest_solution = {
                block_id: (self.Value(start), self.Value(end))
                for block_id, (start, end, _) in block_dict.items()
            }

    callback = SolutionCallback()

    status = solver.Solve(model, callback)
    solve_time = time.time() - start_time

    results = callback.latest_solution if callback.latest_solution else {
        block_id: (solver.Value(start), solver.Value(end))
        for block_id, (start, end, _) in block_dict.items()
    } if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else {}

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        peak_memory = max(end for _, end in results.values())
        print(f"Status: {solver.StatusName(status)}")
        # print(f"Objective value: {solver.ObjectiveValue()}")
        # print(f"Peak memory usage: {peak_memory}")
        return results, solver, peak_memory, solve_time, True
    else:
        print(f"No solution found. Status: {solver.StatusName(status)}")
        return results, solver, 0, solve_time, False

def main():
    parser = argparse.ArgumentParser(description="Memory allocation solver.")
    parser.add_argument("--input_path", required=True, help="Path to input file")
    parser.add_argument("--output_path", required=True, help="Path to output file")
    parser.add_argument("--time_limit", type=int, required=True, help="Time limit in seconds")
    parser.add_argument("--scale", type=int, required=True, help="block size scale factor for address alignment.")
    args = parser.parse_args()

    scale = args.scale
    uni_model_loaded = GraphDefToUniModelConverter.convert(args.input_path)
    graph_cuts, blocks_map = build_graph_cuts(uni_model_loaded, scale)
    results_scaled, allocation, max_address_scaled, solve_time, solved = solve_allocation(graph_cuts, blocks_map, args.time_limit)
    max_address = max_address_scaled * scale

    if solved:
        layer_to_block_map = defaultdict(list)
        for k, v in blocks_map.items():
            layer_to_block_map[v].append(k)

        block_id_to_offset = defaultdict(list)
        for block in results_scaled:
            offset = results_scaled[block][0] * scale
            block_id_to_offset[block.tensor_id] = offset

        for node in uni_model_loaded.uni_graphs[0].layer_nodes:
            if has_allocation(node):
                # Load allocation object from accessor
                alloc_data = get_allocation(node)

                # Update the outputSizes offsets inside AllocationDataPerLayer
                for output_alloc in alloc_data.outputSizes:
                    output_alloc.offset = block_id_to_offset[output_alloc.tensorId]

                # Write updated allocation object back to node
                set_allocation(node, alloc_data)

        # debug print addresses
        # for node in uni_model_loaded.uni_graphs[0].layer_nodes:
        #     if has_allocation(node):
        #         alloc_data = get_allocation(node)
        #         for output_alloc in alloc_data.outputSizes:
        #             output_alloc.offset = block_id_to_offset[output_alloc.tensorId]
        #             print(f"tid: {output_alloc.tensorId}, offset: {output_alloc.offset}")

        print("Solution found")
        print(f"max_address: {max_address}")
        print(f"solve_time: {solve_time}")
    else:
        print("No solution found")

    path = Path(args.output_path)

    directory = str(path.parent)
    ext = ".um.pb"
    filename_wo_ext = os.path.basename(path)
    if filename_wo_ext.endswith(ext):
        filename_wo_ext = filename_wo_ext[:-len(ext)]

    uniPath = UniModelPath(directory, filename_wo_ext)
    UniModelToGraphDefConverter.convert(uni_model_loaded, uniPath)

if __name__ == "__main__":
    main()
