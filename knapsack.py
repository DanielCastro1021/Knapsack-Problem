import os
import time
from tabulate import tabulate
from ortools.algorithms import pywrapknapsack_solver


def dynamic_programming_solver(capacity, weights, values, time_limit):
    W, wt, val = capacity, weights, values
    n = len(val)
    K = [[0 for x in range(W + 1)] for x in range(n + 1)]

    start_time = time.perf_counter()
    time_limit = start_time+time_limit

    for i in range(n + 1):
        for w in range(W + 1):
            current_time = time.perf_counter()
            if(current_time >= time_limit):
                solution = K[i][w]
                time_to_solve = round(current_time - start_time, 3)
                return solution, time_to_solve

            if i == 0 or w == 0:
                K[i][w] = 0
            elif wt[i-1] <= w:
                K[i][w] = max(val[i-1] + K[i-1][w-wt[i-1]],  K[i-1][w])
            else:
                K[i][w] = K[i-1][w]

    solution = K[n][W]
    time_to_solve = round(time.perf_counter()-start_time, 3)
    return solution, time_to_solve


def ortools_solver(capacity, weights, values, time_limit):
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')
    solver.set_time_limit(time_limit)

    start_time = time.perf_counter()
    solver.Init(values, [weights], [capacity])
    solution = solver.Solve()
    time_to_solve = round(time.perf_counter()-start_time, 3)

    return solution, format(time_to_solve, '.3f')


def get_optimum_solution(file):
    with open(file, "r") as f:
        lines = f.readlines()
        return int(lines[0].strip().split()[0])


def get_solution(file, solver, time_limit):
    capacity, values, weights = 0, [], []
    with open(file, "r") as f:
        lines = f.readlines()
        capacity = float(lines[0].strip().split()[1])
        for line in lines[1:]:
            try:
                value, weight = line.strip().split()
                values.append(int(value))
                weights.append(int(weight))
            except:
                pass

    if solver == "ortools_solver":
        return ortools_solver(capacity, weights, values, time_limit)
    elif solver == "dynamic_programming_solver":
        return dynamic_programming_solver(capacity, weights, values, time_limit)
    else:
        raise Exception("Solver Not Found")


def main(folder, current_dataset, solver, time_limit):
    files = os.listdir(os.path.join(folder, current_dataset))
    results = []
    for file in files:
        optimum_solution = get_optimum_solution(os.path.join(
            folder, current_dataset+"-optimum", file))

        solution, time = get_solution(os.path.join(
            folder, current_dataset, file), solver, time_limit)

        gap = round(((optimum_solution-solution)/optimum_solution)*100, 2)

        results.append([file,
                       optimum_solution, solution, gap, time])

    print(tabulate(results, headers=[
          "File Name", "Z*", "Z", "Gap %", f"Time (s)"]))


if __name__ == "__main__":
    folder, datasets, solvers = "KP-instances", {
        1: "low-dimensional", 2: "large_scale"}, {1: "dynamic_programming_solver",  2: "ortools_solver"}

    current_dataset = datasets.get(1)
    solver = solvers.get(2)
    time_limit = 10.00

    main(folder, current_dataset, solver, time_limit)
