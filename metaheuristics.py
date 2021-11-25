import tsp
import local_search as ls
import time
import random
import math


def simulated_annealing(d, s, fs, params):
    """Simulated Annealing https://www.science.org/doi/10.1126/science.220.4598.671"""
    t_init = time.time()
    chart_data = []
    s_star = s[:]
    fs_star = fs  # best solution found so far
    # t_0 = set_initial_temperature_sampling(d, s, fs)
    # t_0 = set_initial_temperature_simulation(d, s, fs, sa_max)
    while time.time() - t_init < params.timelimit:
        iter_t = 0    # iterations at temperature t
        t = params.sa_t_0       # current temperature
        while t > 0.001:
            if params.verbose:
                print(f'| temp: {t:10.3f}  |  s: {fs:10.3f}  |  s*: {fs_star:10.3f}  |  time: {time.time() - t_init:10.2f} |')
            while iter_t < params.sa_max * len(d):
                iter_t += 1
                N = ls.get_random_neighbor(d, fs, s)
                delta = N[0][0] - fs
                if delta < 0:
                    s, fs = tsp.move_to_neighbor(N, d, fs, s)
                    if fs < fs_star:
                        s_star = s[:]
                        fs_star = fs
                else:
                    x = random.random()  # generates a random float number between 0 and 1
                    if x < math.exp(-delta/t):  # move to a worsening neighbor
                        s, fs = tsp.move_to_neighbor(N, d, fs, s)
            chart_data.append([time.time() - t_init, fs, fs_star])
            t = params.sa_alpha * t
            iter_t = 0
    return s_star, fs_star, time.time() - t_init, chart_data


def set_initial_temperature_simulation(d, s, fs, sa_max, t_0=100, beta=1.15, gama=0.90):
    """Defines initial temperature by simulation"""
    t = t_0       # current temperature
    flag = True
    while flag:
        accepted = 0
        for iter_t in range(sa_max):
            N = ls.get_random_neighbor(d, fs, s)
            delta = N[0][0] - fs
            if delta < 0:
                accepted += 1
            else:
                x = random.random()
                if x < math.exp(-delta/t):
                    accepted += 1
        if accepted >= gama * sa_max:
            flag = False
        else:
            t = beta * t
    return t


def set_initial_temperature_sampling(d, s, fs, n_neighbors=100):
    """Defines initial temperature by sampling"""
    t = 0
    for i in range(n_neighbors):
        N = ls.get_random_neighbor(d, fs, s)
        delta = fs - N[0][0]
        if math.fabs(delta) > t:
            t = math.fabs(delta)
    return t


def ils(d, s, fs, params):
    """Iterated Local Search https://doi.org/10.1007/BF01096763"""
    t_init = time.time()
    chart_data = []
    chart_data.append([time.time() - t_init, fs, fs])
    s, fs, t = ls.local_search(d, s, fs, params)
    chart_data.append([time.time() - t_init, fs, fs])
    it = 0
    while time.time() - t_init < params.timelimit:
        it += 1
        s_ = s[:]
        fs_ = fs
        # perturbation
        for _ in range(params.ils_p_level):  # perturbation: apply p_level 2-opt random moves to s_
            N = ls.get_two_opt_random_neighbor(d, s_, fs_)
            s_, fs_ = tsp.two_opt_move(d, s_, fs_, N[0][1], N[0][2])
        chart_data.append([time.time() - t_init, fs_, fs])
        # local search
        s__, fs__, t = ls.local_search(d, s_, fs_, params)
        # acceptance condition
        if fs__ < fs:
            s = s__[:]
            fs = fs__
        if params.verbose:
            print(f'| it: {it:6d}  |  s_: {fs_:10.2f}  |  s__: {fs__:10.2f}  |  s*: {fs:10.2f}  |  time: {time.time() - t_init:10.2f} |')
        chart_data.append([time.time() - t_init, fs__, fs])
    return s, fs, time.time() - t_init, chart_data


def vns(d, s_ini, fs_ini, params):
    """Variable Neighborhood Search (uses 1st improvement VND local search) https://doi.org/10.1007/BF01096763"""
    t_init = time.time()
    chart_data = []
    s = s_ini[:]
    fs = fs_ini
    it = 0
    while time.time() - t_init < params.timelimit:
        it += 1
        k = 1
        while k <= params.vns_k_max:
            if k == 1:  # move to random 2-opt neighbor
                N = ls.get_two_opt_random_neighbor(d, s, fs)
                s_, fs_ = tsp.two_opt_move(d, s[:], fs, N[0][1], N[0][2])
            elif k == 2:  # move to random 3-opt neighbor
                N = ls.get_three_opt_random_neighbor(d, s, fs)
                s_, fs_ = tsp.three_opt_move(d, s[:], fs, N[0][1], N[0][2], N[0][3])
            chart_data.append([time.time() - t_init, fs_, fs])
            # local search
            s__, fs__, t = ls.local_search(d, s_, fs_, params)
            if fs__ + ls.EPS < fs:
                s = s__[:]
                fs = fs__
                k = 1
            else:
                k = k + 1
            if params.verbose:
                print(f'| it: {it:6d}  |  k: {k:3d}  |  s_: {fs_:10.2f}  |  s__: {fs__:10.2f}  |  s*: {fs:10.2f}  |  time: {time.time() - t_init:10.2f} |')
            chart_data.append([time.time() - t_init, fs__, fs])
    return s, fs, time.time() - t_init, chart_data


def tabu_search(d, s, fs, params):
    """Tabu Search https://link.springer.com/chapter/10.1007/978-1-4613-0303-9_33"""
    t_init = time.time()
    chart_data = []
    s_star = s[:]
    fs_star = fs
    T = []  # tabu list
    it = 0
    while time.time() - t_init < params.timelimit:
        it += 1
        s, fs, m = tabu_neighbor(d, s, fs, fs_star, T)
        # s, fs, m = tabu_soln(d, s, fs, fs_star, T)
        T.append(m)
        # T.append(s)
        if len(T) > params.tabu_max:
            T.pop(0)
        if fs < fs_star:
            s_star = s[:]
            fs_star = fs
        if params.verbose:
            print(f'| it: {it:6d}  |  s: {fs:10.2f}  |  s*: {fs_star:10.2f}  |  time: {time.time() - t_init:10.2f} |')
        chart_data.append([time.time() - t_init, fs, fs_star])
    return s_star, fs_star, time.time() - t_init, chart_data


def tabu_soln(d, s, fs, fs_star, T):
    """Move to the best non Tabu neighbor"""
    V = []
    best_fs = float("inf")
    # 2-opt neighbors
    for i in range(1, len(s) - 1):
        for j in range(i + 1, len(s) - 1):
            if not (i == 1 and j == len(d) - 1):  # to avoid needless iterations
                m = (i, j)
                fs_ = tsp.two_opt(d, s, fs, i, j)
                if fs_ < best_fs:
                    s_, fs_ = tsp.two_opt_move(d, s[:], fs, i, j)
                    if s_ not in T:
                        best_fs = fs_
                        V.append([fs_, i, j])
    # 3-opt neighbors
    for i in range(1, len(s) - 1):
        for j in range(i + 1, len(s) - 1):
            for k in range(j + 1, len(s) - 1):
                m = (i, j, k)
                fs_ = tsp.three_opt(d, s, fs, i, j, k)
                if fs_ < best_fs:
                    s_, fs_ = tsp.three_opt_move(d, s[:], fs, i, j, k)
                    if s_ not in T:
                        best_fs = fs_
                        V.append([fs_, i, j, k])
    if V:
        if len(V[-1]) == 3:  # move to 2-opt best neighbor
            i, j = V[-1][1], V[-1][2]
            m = (i, j)
            s, fs = tsp.two_opt_move(d, s, fs, i, j)
        elif len(V[-1]) == 4:  # move to 3-opt best neighbor
            i, j, k = V[-1][1], V[-1][2], V[-1][3]
            m = (i, j, k)
            s, fs = tsp.three_opt_move(d, s, fs, i, j, k)
    return s, fs, m


def tabu_neighbor(d, s, fs, fs_star, T):
    """Move to the best non Tabu neighbor"""
    V = []
    best_fs = float("inf")
    # 2-opt neighbors
    for i in range(1, len(s) - 1):
        for j in range(i + 1, len(s) - 1):
            if not (i == 1 and j == len(d) - 1):  # to avoid needless iterations
                m = (i, j)
                fs_ = tsp.two_opt(d, s, fs, i, j)
                if fs_ < best_fs and (m not in T or fs_ < fs_star):
                    best_fs = fs_
                    V.append([fs_, i, j])
    # 3-opt neighbors
    for i in range(1, len(s) - 1):
        for j in range(i + 1, len(s) - 1):
            for k in range(j + 1, len(s) - 1):
                m = (i, j, k)
                fs_ = tsp.three_opt(d, s, fs, i, j, k)
                if fs_ < best_fs and (not three_opt_is_tabu(m, T) or fs_ < fs_star):
                    best_fs = fs_
                    V.append([fs_, i, j, k])
    if V:
        if len(V[-1]) == 3:  # move to 2-opt best neighbor
            i, j = V[-1][1], V[-1][2]
            m = (i, j)
            s, fs = tsp.two_opt_move(d, s, fs, i, j)
        elif len(V[-1]) == 4:  # move to 3-opt best neighbor
            i, j, k = V[-1][1], V[-1][2], V[-1][3]
            m = (i, j, k)
            s, fs = tsp.three_opt_move(d, s, fs, i, j, k)
    return s, fs, m


def three_opt_is_tabu(m, T):
    """Determinate whether a 3-opt move is tabu
    It cannot have 2 or more indexes in common with any tabu move"""
    for t in T:
        if len(t) == 3:
            count = 0
            if m[0] in t:
                count += 1
            if m[1] in t:
                count += 1
            if m[2] in t:
                count += 1
            if count >= 2:
                return True
    return False


def grasp(d, params):
    """Greedy Randomized Adaptive Search Procedure https://doi.org/10.1007/BF01096763"""
    t_init = time.time()
    fs_star = float("inf")
    it = 0
    chart_data = []
    while time.time() - t_init < params.timelimit:
        it += 1
        s_ini, fs_ini, t = tsp.part_greedy_build(d, params.grasp_alpha)
        if fs_ini < fs_star:
            fs_star = fs_ini
        chart_data.append([time.time() - t_init, fs_ini, fs_star])
        s, fs, t = ls.vnd_first_improvement(d, s_ini[:], fs_ini, ls.MAX_K)
        if params.verbose:
            print(f'| it: {it:6d}  |  s_ini: {fs_ini:10.2f}  |  s: {fs:10.2f}  |  s*: {fs_star:10.2f}  |  time: {time.time() - t_init:10.2f} |')
        if fs < fs_star:
            fs_star = fs
            s_star = s[:]
        chart_data.append([time.time() - t_init, fs, fs_star])

    return s_star, fs_star, time.time() - t_init, chart_data
