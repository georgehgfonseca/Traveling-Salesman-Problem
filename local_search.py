import tsp
import random
import time


EPS = 0.0001  # to avoid numerical issues when comparing float values
MAX_K = 2     # number of neighborhood structures


def get_two_opt_first_neighbor_sample(d, s, fs):
    """Get first neighbor regarding 2-opt neighborhood. A neighbor represented as: [fs, i, j]"""
    N = []
    lst = list(range(1, len(s) - 1)) # s = [0, 5, 2, 4, 7, 9, 1, 3, 6, 8, 0]
    random.shuffle(lst)
    for i in range(0, len(lst)):     # i_idx = 7, 1, 4, 9, 3, n-1, 8, ...
        for j in range(i + 1, len(lst)):
            i_idx = lst[i]
            j_idx = lst[j]
            if i_idx > j_idx:
                (i_idx, j_idx) = (j_idx, i_idx)
            s_new_dist = tsp.two_opt(d, s, fs, i_idx, j_idx)
            if s_new_dist + EPS < fs:
                # add neighbor
                N.append((s_new_dist, i_idx, j_idx))
                return N
    return N


def get_two_opt_first_neighbor(d, s, fs):
    """Get first neighbor regarding 2-opt neighborhood. A neighbor represented as: [fs, i, j]"""
    N = []                             # s = [0, 5, 2, 4, 7, 9, 1, 3, 6, 8, 0]
    for i_idx in range(1, len(s) - 1): # i_idx = 1, 2, 3, 4, 5, 6, 7, ... n - 1
        for j_idx in range(i_idx + 1, len(s) - 1):
            s_new_dist = tsp.two_opt(d, s, fs, i_idx, j_idx)
            if s_new_dist + EPS < fs:
                # add neighbor
                N.append((s_new_dist, i_idx, j_idx))
                return N
    return N


def get_two_opt_neighbors(d, s, fs):
    """Get all neighbors regarding 2-opt neighborhood. A neighbor represented as: [fs, i, j]"""
    N = []
    for i_idx in range(1, len(s) - 1):
        for j_idx in range(i_idx + 1, len(s) - 1):
            s_new_dist = tsp.two_opt(d, s, fs, i_idx, j_idx)
            if s_new_dist + EPS < fs:
                # add neighbor
                N.append((s_new_dist, i_idx, j_idx))
    return N


def get_two_opt_random_neighbor(d, s, fs):
    """Get a random 2-opt neighbor represented as: [fs, i, j]"""
    N = []
    i_idx = random.choice(range(1, len(s) - 1))
    j_idx = random.choice(range(1, len(s) - 1))
    while i_idx == j_idx:
        j_idx = random.choice(range(1, len(s) - 1))
    if i_idx > j_idx:
        i_idx, j_idx = j_idx, i_idx
    s_new_dist = tsp.two_opt(d, s, fs, i_idx, j_idx)
    N.append((s_new_dist, i_idx, j_idx))
    return N


def get_three_opt_first_neighbor(d, s, fs):
    """Get first neighbor regarding 3-opt neighborhood. A neighbor represented as: [fs, i, j, k]"""
    N = []
    for i_idx in range(1, len(s) - 1):
        for j_idx in range(i_idx + 1, len(s) - 1):
            for k_idx in range(j_idx + 1, len(s) - 1):
                s_new_dist = tsp.three_opt(d, s, fs, i_idx, j_idx, k_idx)
                if s_new_dist + EPS < fs:
                    # add neighbor
                    N.append((s_new_dist, i_idx, j_idx, k_idx))
                    return N
    return N


def get_three_opt_first_neighbor_sample(d, s, fs):
    """Get first neighbor regarding 3-opt neighborhood. A neighbor represented as: [fs, i, j, k]"""
    N = []
    l = range(1, len(s) - 1)
    l = random.sample(l, len(l))
    for i in range(len(l)):
        for j in range(i + 1, len(l)):
            for k in range(j + 1, len(l)):
                i_idx = l[i]
                j_idx = l[j]
                k_idx = l[k]
                # ensure i, j and k are ordered
                sum_val = i_idx + j_idx + k_idx
                max_val = max(i_idx, j_idx, k_idx)
                min_val = min(i_idx, j_idx, k_idx)
                i_idx = min_val
                j_idx = sum_val - max_val - min_val
                k_idx = max_val
                s_new_dist = tsp.three_opt(d, s, fs, i_idx, j_idx, k_idx)
                if s_new_dist + EPS < fs:
                    # add neighbor
                    N.append((s_new_dist, i_idx, j_idx, k_idx))
                    return N
    return N


def get_three_opt_neighbors(d, s, fs):
    """Get all neighbors regarding 3-opt neighborhood. A neighbor represented as: [fs, i, j, k]"""
    N = []
    for i_idx in range(1, len(s) - 1):
        for j_idx in range(i_idx + 1, len(s) - 1):
            for k_idx in range(j_idx + 1, len(s) - 1):
                fs_line = tsp.three_opt(d, s, fs, i_idx, j_idx, k_idx)
                if fs_line + EPS < fs:
                    # add neighbor
                    N.append((fs_line, i_idx, j_idx, k_idx))
    return N


def get_three_opt_random_neighbor(d, s, fs):
    """Get a random 3-opt neighbor represented as: [fs, i, j, k]"""
    N = []
    i = random.choice(range(1, len(s) - 1))
    j = random.choice(range(1, len(s) - 1))
    k = random.choice(range(1, len(s) - 1))
    while i == j or i == k or j == k:
        i = random.choice(range(1, len(s) - 1))
        j = random.choice(range(1, len(s) - 1))
        k = random.choice(range(1, len(s) - 1))
    # ensure i, j and k are ordered
    sum_val = i + j + k
    max_val = max(i, j, k)
    min_val = min(i, j, k)
    i = min_val
    j = sum_val - max_val - min_val
    k = max_val
    s_new_dist = tsp.three_opt(d, s, fs, i, j, k)
    N.append((s_new_dist, i, j, k))
    return N


def get_random_neighbor(d, fs, s):
    """Get either a 2-opt (50% odd) or a 3-opt neighbor (50% odd)"""
    r = random.random()
    if r < 0.5:
        return get_two_opt_random_neighbor(d, s, fs)
    else:
        return get_three_opt_random_neighbor(d, s, fs)


def descent_two_opt(d, s, fs):
    """Descent local search method (2-opt) for TSP"""
    t_init = time.time()
    N = get_two_opt_neighbors(d, s, fs)
    while N:
        # select best neighbor
        best_n = -1
        min = float("inf")
        for n in N:
            if n[0] < min:
                min = n[0]
                best_n = n
        # move to next neighbor
        s, fs = tsp.two_opt_move(d, s, fs, best_n[1], best_n[2])
        # print(round(s_dist, 2))
        N = get_two_opt_neighbors(d, s, fs)
    return s, fs, time.time() - t_init


def descent_three_opt(d, s, fs):
    """Descent local search method (3-opt) for TSP"""
    t_init = time.time()
    N = get_three_opt_neighbors(d, s, fs)
    while N:
        # select best neighbor
        best_n = -1
        min = float("inf")
        for n in N:
            if n[0] < min:
                min = n[0]
                best_n = n
        # move to next neighbor
        (s, fs) = tsp.three_opt_move(d, s, fs, best_n[1], best_n[2], best_n[3])
        N = get_three_opt_neighbors(d, s, fs)
    return s, fs, time.time() - t_init


def first_improvement_two_opt(d, s, fs):
    """First improvement local search method (2-opt) for TSP"""
    t_init = time.time()
    N = get_two_opt_first_neighbor_sample(d, s, fs)
    while N:
        # move to next neighbor
        s, fs = tsp.two_opt_move(d, s, fs, N[0][1], N[0][2])
        N = get_two_opt_first_neighbor_sample(d, s, fs)
    return s, fs, time.time() - t_init


def first_improvement_three_opt(d, s, fs):
    """First improvement local search method (3-opt) for TSP"""
    t_init = time.time()
    N = get_three_opt_first_neighbor_sample(d, s, fs)
    while N:
        # move to next neighbor
        s, fs = tsp.three_opt_move(d, s, fs, N[0][1], N[0][2], N[0][3])
        # print(round(s_dist, 2))
        N = get_three_opt_first_neighbor_sample(d, s, fs)
    return s, fs, time.time() - t_init


def random_descent_two_opt(d, s, fs, max_it):
    """Random descent local search method (2-opt) for TSP"""
    t_init = time.time()
    it = 0
    while it < max_it:
        it += 1
        N = get_two_opt_random_neighbor(d, s, fs)
        if N[0][0] + EPS < fs:
            it = 0
            # apply and accept move
            s, fs = tsp.two_opt_move(d, s, fs, N[0][1], N[0][2])
    return s, fs, time.time() - t_init


def random_descent_three_opt(d, s, fs, max_it):
    """Random descent local search method (3-opt) for TSP"""
    t_init = time.time()
    it = 0
    while it < max_it:
        it += 1
        N = get_three_opt_random_neighbor(d, s, fs)
        if N[0][0] + EPS < fs:
            it = 0
            # apply and accept move
            s, fs = tsp.three_opt_move(d, s, fs, N[0][1], N[0][2], N[0][3])
    return s, fs, time.time() - t_init


def random_descent(d, s, fs, max_it):
    """Random descent local search method (2 and 3-opt) for TSP"""
    t_init = time.time()
    it = 0
    while it < max_it:
        it += 1
        k = random.random()
        if k < 0.5:
            N = get_two_opt_random_neighbor(d, s, fs)
            if N[0][0] + EPS < fs:
                it = 0
                # apply and accept move
                s, fs = tsp.two_opt_move(d, s, fs, N[0][1], N[0][2])
        elif k < 1.0:
            N = get_three_opt_random_neighbor(d, s, fs)
            if N[0][0] + EPS < fs:
                it = 0
                # apply and accept move
                s, fs = tsp.three_opt_move(d, s, fs, N[0][1], N[0][2], N[0][3])
    return s, fs, time.time() - t_init


def vnd(d, s, fs, max_k):
    """Variable neighborhood descent method for TSP (k=1: 2-opt k=2: 3-opt)"""
    t_init = time.time()
    k = 1
    while k <= max_k:
        if k == 1:
            s_line, fs_line, t = descent_two_opt(d, s, fs)
        elif k == 2:
            s_line, fs_line, t = descent_three_opt(d, s, fs)
        if fs_line < fs:
            s = s_line[:]
            fs = fs_line
            k = 1
        else:
            k += 1
    return s, fs, time.time() - t_init


def vnd_first_improvement(d, s, fs, max_k):
    """Variable neighborhood descent method for TSP (k=1: 2-opt k=2: 3-opt)"""
    t_init = time.time()
    k = 1
    while k <= max_k:
        if k == 1:
            s_line, fs_line, t = first_improvement_two_opt(d, s, fs)
        elif k == 2:
            s_line, fs_line, t = first_improvement_three_opt(d, s, fs)
        if fs_line < fs:
            s = s_line[:]
            fs = fs_line
            k = 1
        else:
            k += 1
    return s, fs, time.time() - t_init


def local_search(d, s, fs, params):
    if params.localsearch == "DESCENT2":
        s_, fs_, t = descent_two_opt(d, s, fs)
    elif params.localsearch == "DESCENT3":
        s_, fs_, t = descent_three_opt(d, s, fs)
    elif params.localsearch == "FIRSTIMP2":
        s_, fs_, t = first_improvement_two_opt(d, s, fs)
    elif params.localsearch == "FIRSTIMP3":
        s_, fs_, t = first_improvement_three_opt(d, s, fs)
    elif params.localsearch == "RANDOM*":
        s_, fs_, t = random_descent(d, s, fs, params.ls_max * len(d))
    elif params.localsearch == "RANDOM2":
        s_, fs_, t = random_descent_two_opt(d, s, fs, params.ls_max * len(d))
    elif params.localsearch == "RANDOM3":
        s_, fs_, t = random_descent_three_opt(d, s, fs, params.ls_max * len(d))
    elif params.localsearch == "VND*":
        s_, fs_, t = vnd(d, s, fs, params.neigh_types)
    return s_, fs_, t
