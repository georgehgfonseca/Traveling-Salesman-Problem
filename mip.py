import math
import time
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import random
import local_search as ls

# Based on Gurobi code on Mixed-Integer Programming heuristics: https://github.com/Gurobi/pres-mipheur
def tspmip(n, dist, timelimit=60):
    m = gp.Model()
    # Objects to use inside callbacks
    m._n = n
    m._subtours = []
    m._tours = []
    m._dist = dict(dist)

    # Create variables
    vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')

    # Create opposite direction (i,j) -> (j,i)
    # This isn't a new variable - it's a pointer to the same variable
    for i, j in vars.keys():
        vars[j, i] = vars[i, j]
        m._dist[j, i] = dist[i, j]

    # Add degree-2 constraint
    m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))

    # Set parameter for lazy constraints
    m.Params.lazyConstraints = 1

    # Set the relative MIP gap to 0 and the time limit
    m.Params.TimeLimit = timelimit

    # vars object to use inside callbacks
    m._vars = vars

    return m


# ## Subtours function
# Finds all subtours from an integer solution, sorted from smallest subtour to largest.
def subtours(vals):
    # make a list of edges selected in the solution
    edges = gp.tuplelist((i, j) for i, j in vals.keys()
                         if vals[i, j] > 0.5)
    cycles = []
    while edges:
        # Trace edges until we find a loop
        i, j = edges[0]
        thiscycle = [i]
        while j != thiscycle[0]:
            thiscycle.append(j)
            i, j = next((i, j) for i, j in edges.select(j, '*')
                        if j != thiscycle[-2])
        cycles.append(thiscycle)
        for j in thiscycle:
            edges.remove((i, j))
            edges.remove((j, i))
            i = j
    return sorted(cycles, key=lambda x: len(x))


def tourcost(dist, tour):
    """"Compute the cost aof a tour"""
    return sum(dist[tour[k - 1], tour[k]] for k in range(len(tour)))


# ## Callback function
# There are several parts to the main callback function:
# 1. Checks on integer solutions: if an integer solution is found, it either stores the tour or subtours
# 2. A call to a heuristic function, which we specify later
# 3. If subtours were found, add subtour elimination constraints
# 4. If a tour was generated (like from a heuristic), set that as a candidate solution
def tspcb(heurcb=None):
    def basecb(model, where):

        # Check MIP solution
        if where == GRB.Callback.MIPSOL:

            vals = model.cbGetSolution(model._vars)
            tours = subtours(vals)
            if len(tours) > 1:
                # Save the subtours for future use
                model._subtours.append(tours)
            else:
                # Save the tour for future use
                model._tours.append(tours[0])

                # Record time when first tour is found
                try:
                    model._firstsoltime
                except AttributeError:
                    model._firstsoltime = model.cbGet(GRB.Callback.RUNTIME)

        # Call inner heuristic callback function, if specified
        try:
            heurcb(model, where)
        except TypeError:  # no heuristic callback specified
            pass

        # Add subtour constraints if there are any subtours
        if where == GRB.Callback.MIPSOL:
            for tours in model._subtours:
                # add a subtour elimination constraint for all but largest subtour
                for tour in tours[:-1]:
                    model.cbLazy(gp.quicksum(model._vars[i, j]
                                             for i, j in combinations(tour, 2) if (i, j) in model._vars)
                                 <= len(tour) - 1)
            # Reset the subtours
            model._subtours = []

        # Inject a heuristic solution, if there is a saved one
        if where == GRB.Callback.MIPNODE:
            try:
                # There may be multiple tours - find the best one
                tour, cost = min(((tour, tourcost(model._dist, tour))
                                  for tour in model._tours),
                                 key=lambda x: x[-1])
                # Only apply if the tour is an improvement
                if cost < model.cbGet(GRB.Callback.MIPNODE_OBJBST):
                    # Set all variables to 0.0 - optional but helpful to suppress some warnings
                    model.cbSetSolution(model._vars.values(), [0.0] * len(model._vars))
                    # Now set variables in tour to 1.0
                    model.cbSetSolution([model._vars[tour[k - 1], tour[k]] for k in range(len(tour))],
                                        [1.0] * len(tour))
                    # Use the solution - optional but a slight performance improvement
                    model.cbUseSolution()
                # Reset the tours
                model._tours = []
            except ValueError:  # tours list was already empty
                pass

    return basecb  # the generated function


def dist_from_coord(coord):
    points = []
    for (i, x, y) in coord:
        points.append((x, y))
    n = len(points)

    # Dictionary of Euclidean distance between each pair of points
    dist = {(i, j):
                math.sqrt(sum((points[i][k] - points[j][k]) ** 2 for k in range(2)))
            for i in range(n) for j in range(i)}
    return dist


def load_soln(s_ini, m):
    for idx in range(len(s_ini) - 1):
        i, j = s_ini[idx], s_ini[idx + 1]
        m._vars[i, j].start = 1.0


def convert_soln(m):
    vals = m.getAttr('x', m._vars)
    edges = gp.tuplelist((i, j) for i, j in vals.keys()
                         if vals[i, j] > 0.5)
    cycles = []
    while edges:
        # Trace edges until we find a loop
        i,j = edges[0]
        thiscycle = [i]
        while j != thiscycle[0]:
            thiscycle.append(j)
            i,j = next((i,j) for i,j in edges.select(j, '*')
                       if j != thiscycle[-2])
        cycles.append(thiscycle)
        for j in thiscycle:
            edges.remove((i,j))
            edges.remove((j,i))
            i = j
    return cycles[0]


def full_model(coord, d, s_ini, fs_ini, params):
    chart_data = [[0, fs_ini, fs_ini]]
    n = len(coord)
    dist = dist_from_coord(coord)
    m = tspmip(n, dist, params.timelimit)
    s_ini, fs_ini, t = ls.local_search(d, s_ini, fs_ini, params)
    load_soln(s_ini, m)
    # m.optimize(tspcb())
    m.optimize(tspcb(combops))
    s = convert_soln(m)
    chart_data = [[m.Runtime, m.objVal, m.objVal]]
    return s, m.objVal, m.Runtime, chart_data


def fix_opt(coord, d, s_ini, fs_ini, params):
    chart_data = [[0, fs_ini, fs_ini]]
    n = len(coord)
    dist = dist_from_coord(coord)
    m = tspmip(n, dist, params.fix_opt_it_tl)
    m.Params.LogToConsole = 0  # deactivate Gurobi logs
    s_ini, fs_ini, t = ls.local_search(d, s_ini, fs_ini, params)
    load_soln(s_ini, m)
    m.update()
    t_init = time.time()
    n_nodes = params.fix_opt_n
    it = 0
    while time.time() - t_init < params.timelimit:
        it += 1
        # fix all vars
        for i, j in m._vars.keys():
            if it == 1:
                if m._vars[i, j].start == 1.0:
                    m._vars[i, j].ub = m._vars[i, j].lb = 1.0
                else:
                    m._vars[i, j].ub = m._vars[i, j].lb = 0.0
            else:
                if m._vars[i, j].x >= 0.999:
                    m._vars[i, j].ub = m._vars[i, j].lb = 1.0
                else:
                    m._vars[i, j].ub = m._vars[i, j].lb = 0.0

        # choose variables to unfix
        fixed = list(range(0, n))
        unfixed = []
        if n_nodes >= n:
            unfixed = list(range(0, n))
        else:
            while len(unfixed) < n_nodes:
                v = random.choice(fixed)
                fixed.remove(v)
                unfixed.append(v)

        # unfix vars
        for i, j in m._vars.keys():
            if i in unfixed or j in unfixed:
                m._vars[i, j].lb = 0.0
                m._vars[i, j].ub = 1.0

        # m.optimize(tspcb())
        m.optimize(tspcb(combops))
        chart_data.append([time.time() - t_init, m.objVal, m.objVal])

        if params.verbose:
            print(f'| it: {it:6d}  |  n_nodes: {n_nodes:6d}  |  lb: {m.objBound:10.2f}  |  ub (s): {m.objVal:10.2f}  |  time: {time.time() - t_init:10.2f} |')

        # check for global optimality
        if m.Status == GRB.OPTIMAL and n_nodes >= n:
            print("=" * 18, "Solution is optimal (sub-problem size equals problem size) ", "=" * 18)
            break

        # adjust sub-problem size
        if m.Status == GRB.OPTIMAL:
            n_nodes = math.ceil(n_nodes * 1.20)
        else:
            n_nodes = math.ceil(n_nodes * 0.80)

    s = convert_soln(m)
    return s, m.objVal, time.time() - t_init, chart_data


# ====================================== unused code, use it at your own risk ==========================================
# ## Heuristic Code
# A Python class that computes some standard TSP heuristics:
#
# 1. Greedy node insertion
# 1. Subtour node patching
# 1. Solution improvement via swapping
#
# In both the greedy and patch heuristics, we use Python aggreate [min](https://docs.python.org/3/library/functions.html#min) functions with a key function so that we can obtain the argmin value. The key is specified as a [lambda function](https://docs.python.org/3/reference/expressions.html#lambda) so that we don't need to define a named function.
class pytsp:
    def __init__(self, n, dist, logging=False):
        self.n = n
        self.dist = dist
        self.logging = logging

    # Construct a heuristic tour via greedy insertion
    def greedy(self, dist=None, sense=1):
        if not dist:
            dist = self.dist
        unexplored = list(range(self.n))
        tour = []
        prev = 0
        while unexplored:
            best = min((i for i in unexplored if i != prev), key=lambda k: sense * dist[prev, k])
            tour.append(best)
            unexplored.remove(best)
            prev = best
        if self.logging:
            print("**** greedy heuristic tour=%f, obj=%f" % (tourcost(self.dist, tour), tourcost(dist, tour)))
        return tour

    # Construct a heuristic tour via Karp patching method from subtours
    def patch(self, subtours):
        if self.logging:
            print("**** patching %i subtours" % len(subtours))
        tours = list(subtours)  # copy object to avoid destroying it
        while len(tours) > 1:
            # t1,t2 are tours to merge
            # k1,k2 are positions to merge in the tours
            # d is the direction - forwards or backwards
            t2 = tours.pop()
            # Find best merge
            j1, k1, k2, d, obj = min(((j1, k1, k2, d,
                                       self.dist[tours[j1][k1 - 1], t2[k2 - d]] +
                                       self.dist[tours[j1][k1], t2[k2 - 1 + d]] -
                                       self.dist[tours[j1][k1 - 1], tours[j1][k1]] -
                                       self.dist[t2[k2 - 1], t2[k2]])
                                      for j1 in range(len(tours))
                                      for k1 in range(len(tours[j1]))
                                      for k2 in range(len(t2))
                                      for d in range(2)),  # d=0 is forward, d=1 is reverse
                                     key=lambda x: x[-1])
            t1 = tours[j1]
            k1 += 1  # include the position
            k2 += 1
            if d == 0:  # forward
                tour = t1[:k1] + t2[k2:] + t2[:k2] + t1[k1:]
            else:  # reverse
                tour = t1[:k1] + list(reversed(t2[:k2])) + list(reversed(t2[k2:])) + t1[k1:]
            tours[j1] = tour  # replace j1 with new merge
        if self.logging:
            print("**** patched tour=%f" % tourcost(self.dist, tour))
        return tours[0]

    # Improve a tour via swapping
    # This is simple - just do 2-opt
    def swap(self, tour):
        if self.logging:
            beforecost = tourcost(self.dist, tour)

        for j1 in range(len(tour)):
            for j2 in range(j1 + 1, len(tour)):
                if self.dist[tour[j1 - 1], tour[j1]] + self.dist[tour[j2 - 1], tour[j2]] > \
                        self.dist[tour[j1 - 1], tour[j2 - 1]] + self.dist[tour[j1], tour[j2]]:
                    # swap
                    tour = tour[:j1] + list(reversed(tour[j1:j2])) + tour[j2:]

        if self.logging:
            print("**** swapping: before=%f after=%f" % (beforecost, tourcost(self.dist, tour)))
        return tour

# def run_all(dataset):
#     # load problem data
#     d, coord = util.read_tsp(dataset)
#     dist = dist_from_coord(coord)
#     n = len(coord)
#
#     # ## Generate model and solve with basic callback
#     # Without any customization, the callback function `tspcb` simply finds subtours and adds constraints to prevent them.
#     print("=" * 100, "noheur")
#     m = tspmip(n, dist)
#     m.optimize(tspcb())
#
#     # ### Solve the TSP with the greedy heuristic
#     print("=" * 100, "greedy")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(greedycb))
#
#     # ### Solve the TSP with the swap heuristic
#     # By itself, this should be no faster at finding the first solution, but it may reduce the time to optimality.
#     print("=" * 100, "swap")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(swapcb))
#
#     # ### Solve the TSP with the patch heuristic
#     print("=" * 100, "patch")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(patchcb))
#
#
#     print("=" * 100, "greedy+swap")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(combogs))
#
#     print("=" * 100, "patch+swap")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(combops))
#
#     print("=" * 100, "patch+greedy+swap")
#     m = tspmip(n, dist)
#     m.optimize(tspcb(combopgs))


# def mip_fix_opt_seq(coord, s_ini, fs_ini, n_nodes, timelimit, timelimit_it):
#     chart_data = [[0, fs_ini, fs_ini]]
#     n = len(coord)
#     dist = dist_from_coord(coord)
#     m = tspmip(n, dist, timelimit_it)
#     load_soln(s_ini, m)
#     m.update()
#     t_init = time.time()
#     it = 0
#     while time.time() - t_init < timelimit:
#         it += 1
#         # fix all vars
#         for i, j in m._vars.keys():
#             if it == 1:
#                 if m._vars[i, j].start == 1.0:
#                     m._vars[i, j].ub = m._vars[i, j].lb = 1.0
#                 else:
#                     m._vars[i, j].ub = m._vars[i, j].lb = 0.0
#             else:
#                 if m._vars[i, j].x >= 0.999:
#                     m._vars[i, j].ub = m._vars[i, j].lb = 1.0
#                 else:
#                     m._vars[i, j].ub = m._vars[i, j].lb = 0.0
#
#         # choose variables to unfix
#         fixed = list(range(0, n))
#         unfixed = []
#         if it == 1:
#             s = s_ini
#         else:
#             s = convert_soln(m)
#         if n_nodes >= n:
#             unfixed = list(range(0, n))
#         while len(unfixed) < n_nodes:
#             v = random.choice(fixed)
#             # variables related to a sequence of 10 cities are unfixed together
#             idx = s.index(v)
#             for i in range(idx, idx+10):
#                 if i >= len(s) or len(unfixed) >= n_nodes:
#                     break
#                 if s[i] not in fixed:
#                     continue
#                 fixed.remove(s[i])
#                 unfixed.append(s[i])
#         print("=" * 50, "iter:", it, "n_nodes:", n_nodes, "=" * 50)
#
#         # unfix vars
#         for i, j in m._vars.keys():
#             if i in unfixed or j in unfixed:
#                 m._vars[i, j].lb = 0.0
#                 m._vars[i, j].ub = 1.0
#
#         m.optimize(tspcb())
#         chart_data.append([time.time() - t_init, m.objVal, m.objVal])
#
#         # check for global optimality
#         if m.Status == GRB.OPTIMAL and n_nodes >= n:
#             print("=" * 50, "iter:", it, "Optimal Solution Found", "=" * 50)
#             break
#
#         # adjust sub-problem size
#         if m.Status == GRB.OPTIMAL:
#             n_nodes = math.ceil(n_nodes * 1.10)
#         else:
#             n_nodes = math.ceil(n_nodes * 0.80)
#
#     s = convert_soln(m)
#     return s, m.objVal, time.time() - t_init, chart_data

# # ## Try swap heuristic
# # When a tour has been discovered in the MIP, call the swap heuristic to try and improve it.
#
# # ### Callback for swap heuristic
# # Since the base callback injects a tour at a MIP node, this should be called at a MIP node.
def swapcb(model, where):
    if where == GRB.Callback.MIPNODE:
        pt = pytsp(model._n, model._dist)
        for k in range(len(model._tours)):
            model._tours[k] = pt.swap(model._tours[k])
#
#
#
# # ## Try greedy heuristic
# # - While solving the MIP, call the greedy heuristic using the _fractional values from the LP relaxation_
# # - The motivation is that these fractional values should guide towards a good solution
# # - When values are all zero (like crossing between subtours), pick the edge with the shortest length.
#
# # %% [markdown] slideshow={"slide_type": "slide"}
# # ### Callback for greedy heuristic
# def greedycb(model, where):
#     if where == GRB.Callback.MIPNODE:
#         if model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.OPTIMAL:
#             x = model.cbGetNodeRel(model._vars)
#             for k in x:
#                 if x[k] < 0.001:
#                     x[k] = -model._dist[k]
#             pt = pytsp(model._n, model._dist)
#             model._tours.append(pt.greedy(dist=x, sense=-1))  # maximize using the x values
#
#
#
# # ## Try patch heuristic
# # When an integer solution contains subtours, call the patching heuristic to create a tour, and try that as a heuristic solution.
#
# ### Callback for patch heuristic
def patchcb(model, where):
    if where == GRB.Callback.MIPSOL:
        pt = pytsp(model._n, model._dist)
        for subtour in model._subtours:
            model._tours.append(pt.patch(subtour))

#
#
# # ## Multiple heuristics
# # Why not combine multiple heuristics together?
# # ### Combination: Greedy + Swap
# def combogs(model, where):
#     greedycb(model, where)
#     swapcb(model, where)
#
# ### Combination: Patch + Swap
def combops(model, where):
    patchcb(model, where)
    swapcb(model, where)
#
# # ### Combination: Patch + Greedy + Swap
# def combopgs(model, where):
#     patchcb(model, where)
#     greedycb(model, where)
#     swapcb(model, where)
