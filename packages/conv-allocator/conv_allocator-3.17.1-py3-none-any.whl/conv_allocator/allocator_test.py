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
import sys
import argparse
from ortools.linear_solver import pywraplp

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Allocation optimizer')
    parser.add_argument('--source', type=str, help='Source filename', default='')
    parser.add_argument('--target', type=str, help='Target filename', default='')
    parser.add_argument('--time', type=int, help='Allowed time in seconds', default=0)

    return parser.parse_args(args)

def hello_world(source_filename, target_filename, allowed_time):
    print(f"Hello from conv-allocator!")
    print(f"Source: {source_filename}")
    print(f"Target: {target_filename}")
    print(f"Allowed time: {allowed_time} seconds")

    solver = pywraplp.Solver.CreateSolver('GLOP')
    x = solver.NumVar(0, 10, 'x')
    y = solver.NumVar(0, 10, 'y')
    solver.Add(x + y <= 20)
    solver.Maximize(x + y)
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print(f"x = {x.solution_value()}, y = {y.solution_value()}")
    else:
        print("No solution found")

def main(args=None):
    if args is None:
        # Use sys.argv if no args provided
        args = sys.argv[1:]

    parsed_args = parse_args(args)
    hello_world(parsed_args.source, parsed_args.target, parsed_args.time)

if __name__ == "__main__":
    main()