import random
import time


def greedy_build(d):
    """"Greedy initial solution build by nearest neighbor heuristic"""
    t_init = time.time()
    s = [0]
    fs = 0
    C = [i for i in range(1, len(d))]
    while len(C) != 0:
        # select c_min
        min_dist = float("inf")
        c_min = -1
        for c in C:
            if d[s[-1]][c] < min_dist:
                min_dist = d[s[-1]][c]
                c_min = c
        # insert c_min in solution s
        s.append(c_min)
        fs += min_dist
        C.remove(c_min)
    # add first node to close the cycle
    fs += d[s[-1]][s[0]]
    s.append(s[0])
    return s, fs, time.time() - t_init


def greedy_build_cheapest_insertion(d):
    """"Greedy initial solution build by cheapest insertion heuristic"""
    t_init = time.time()
    s = [0, 2, 5, 0]  # 0, 2 and 5 can be random
    fs = d[s[0]][s[1]] + d[s[1]][s[2]] + d[s[2]][s[3]]
    C = [x for x in range(0, len(d)) if x not in s]
    while C:
        # select c_min
        min_dist = float("inf")
        c_min = -1
        idx_min = -1
        for idx in range(len(s) - 1):
            i = s[idx]
            j = s[idx + 1]
            for k in C:
                if d[i][k] + d[k][j] - d[i][j] < min_dist:
                    min_dist = d[i][k] + d[k][j] - d[i][j]
                    c_min = k
                    idx_min = idx
        # insert c_min in s after position idx_min
        s.insert(idx_min + 1, c_min)
        fs += min_dist
        C.remove(c_min)
    return s, fs, time.time() - t_init


def part_greedy_build(d, alpha):
    """"Partially greedy initial solution build by nearest neighbor heuristic"""
    t_init = time.time()
    s = [0]
    fs = 0
    C = [i for i in range(1, len(d))]
    while len(C) != 0:
        # calculates best (g_min) and worst (g_max) candidates
        g_max = float("-inf")
        g_min = float("inf")
        for c in C:
            if d[s[-1]][c] > g_max:
                g_max = d[s[-1]][c]
            if d[s[-1]][c] < g_min:
                g_min = d[s[-1]][c]
        # create LCR
        LCR = []
        for c in C:
            if d[s[-1]][c] <= g_min + alpha * (g_max - g_min):
                LCR.append(c)
        # randomly select c and inserts in solution s
        c = random.choice(LCR)
        fs += d[s[-1]][c]
        s.append(c)
        C.remove(c)
    # add first node to close the cycle
    fs += d[s[-1]][s[0]]
    s.append(s[0])
    return s, fs, time.time() - t_init


def swap(d, s, fs, i, j):
    """"Eval swap of nodes at indexes i and j"""
    if i > j:
        i, j = j, i
    if j == i + 1:
        fs += - d[s[i - 1]][s[i]] - d[s[j]][s[j + 1]] + d[s[i - 1]][s[j]] + d[s[i]][s[j + 1]]
    else:
        fs += - d[s[i - 1]][s[i]] - d[s[i]][s[i + 1]] - d[s[j - 1]][s[j]] - d[s[j]][s[j + 1]] \
              + d[s[i - 1]][s[j]] + d[s[j]][s[i + 1]] + d[s[j - 1]][s[i]] + d[s[i]][s[j + 1]]
    return s, fs


def swap_move(d, s, fs, i, j):
    """"Do swap nodes at indexes i and j"""
    if i > j:
        i, j = j, i
    if j == i + 1:
        fs += - d[s[i - 1]][s[i]] - d[s[j]][s[j + 1]] + d[s[i - 1]][s[j]] + d[s[i]][s[j + 1]]
    else:
        fs += - d[s[i - 1]][s[i]] - d[s[i]][s[i + 1]] - d[s[j - 1]][s[j]] - d[s[j]][s[j + 1]] \
              + d[s[i - 1]][s[j]] + d[s[j]][s[i + 1]] + d[s[j - 1]][s[i]] + d[s[i]][s[j + 1]]
    s[i], s[j] = s[j], s[i]
    return s, fs


def swap_move_naive(d, s, fs, i, j):
    """"Naive (slow) swap nodes at indexes i and j"""
    if i > j:
        i, j = j, i
    s[i], s[j] = s[j], s[i]
    return s, full_eval(d, s)


def two_opt(d, s, fs, i, j):
    """"Eval 2-opt at indexes i and j (reversion of route segment [i...j])"""
    fs += d[s[i - 1]][s[j]] + d[s[i]][s[j + 1]] - d[s[i - 1]][s[i]] - d[s[j]][s[j + 1]]
    return fs


def two_opt_move(d, s, fs, i, j):
    """"Do 2-opt move at indexes i and j (reverse route segment [i...j])"""
    fs += d[s[i - 1]][s[j]] + d[s[i]][s[j + 1]] - d[s[i - 1]][s[i]] - d[s[j]][s[j + 1]]
    s = s[0:i] + list(reversed(s[i:j+1])) + s[j+1:]
    return s, fs


def two_opt_move_naive(d, s, fs, i, j):
    """"Naive (slow) 2-opt move at indexes i and j (reverse route segment [i...j])"""
    s = s[0:i] + list(reversed(s[i:j+1])) + s[j+1:]
    return s, full_eval(d, s)


def three_opt(d, s, fs, i, j, k):
    """"Eval 3-opt at indexes i, j and k (combinations of reversed route segments [i...j] and/or [j...k])"""
    c2_fs = c3_fs = c4_fs = float("inf")
    if i != j - 1:  # otherwise no new solution is generated!
        c2_fs = fs + d[s[i]][s[j]] + d[s[i + 1]][s[j + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]]
    if j != k - 1:  # otherwise no new solution is generated!
        c3_fs = fs + d[s[j]][s[k]] + d[s[j + 1]][s[k + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    if i != j - 1 and j != k - 1:  # otherwise no new solution is generated!
        c4_fs = fs + d[s[i]][s[j]] + d[s[i + 1]][s[k]] + d[s[j + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c5_fs = fs + d[s[i]][s[j + 1]] + d[s[k]][s[i + 1]] + d[s[j]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c6_fs = fs + d[s[i]][s[j + 1]] + d[s[k]][s[j]] + d[s[i + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c7_fs = fs + d[s[i]][s[k]] + d[s[j + 1]][s[i + 1]] + d[s[j]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c8_fs = fs + d[s[i]][s[k]] + d[s[j + 1]][s[j]] + d[s[i + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c_best_fs = min(c2_fs, c3_fs, c4_fs, c5_fs, c6_fs, c7_fs, c8_fs)
    return c_best_fs


def three_opt_move(d, s, fs, i, j, k):
    """"Do 3-opt move at indexes i, j and k (best combination of reversed route segments [i...j] and/or [j...k])"""
    # evaluate candidates
    c2_fs = c3_fs = c4_fs = float("inf")
    if i != j - 1:  # otherwise no new solution is generated!
        c2_fs = fs + d[s[i]][s[j]] + d[s[i + 1]][s[j + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]]
    if j != k - 1:  # otherwise no new solution is generated!
        c3_fs = fs + d[s[j]][s[k]] + d[s[j + 1]][s[k + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    if i != j - 1 and j != k - 1:  # otherwise no new solution is generated!
        c4_fs = fs + d[s[i]][s[j]] + d[s[i + 1]][s[k]] + d[s[j + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c5_fs = fs + d[s[i]][s[j + 1]] + d[s[k]][s[i + 1]] + d[s[j]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c6_fs = fs + d[s[i]][s[j + 1]] + d[s[k]][s[j]] + d[s[i + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c7_fs = fs + d[s[i]][s[k]] + d[s[j + 1]][s[i + 1]] + d[s[j]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    c8_fs = fs + d[s[i]][s[k]] + d[s[j + 1]][s[j]] + d[s[i + 1]][s[k + 1]] - d[s[i]][s[i + 1]] - d[s[j]][s[j + 1]] - d[s[k]][s[k + 1]]
    # move to the best candidate
    c_fs = min(c2_fs, c3_fs, c4_fs, c5_fs, c6_fs, c7_fs, c8_fs)
    if c2_fs == c_fs:
        s = s[0:i+1] + list(reversed(s[i+1:j+1])) + s[j+1:]
    elif c3_fs == c_fs:
        s = s[0:j+1] + list(reversed(s[j+1:k+1])) + s[k+1:]
    elif c4_fs == c_fs:
        s = s[0:i+1] + list(reversed(s[i+1:j+1])) + list(reversed(s[j+1:k+1])) + s[k+1:]
    elif c5_fs == c_fs:
        s = s[0:i+1] + s[j+1:k+1] + s[i+1:j+1] + s[k+1:]
    elif c6_fs == c_fs:
        s = s[0:i+1] + s[j+1:k+1] + list(reversed(s[i+1:j+1])) + s[k+1:]
    elif c7_fs == c_fs:
        s = s[0:i+1] + list(reversed(s[j+1:k+1])) + s[i+1:j+1] + s[k+1:]
    elif c8_fs == c_fs:
        s = s[0:i+1] + list(reversed(s[j+1:k+1])) + list(reversed(s[i+1:j+1])) + s[k+1:]
    return s, c_fs


def three_opt_move_naive(d, s, fs, i, j, k):
    """"Naive (slow) 3-opt move at indexes i, j and k
        (best combination of reversed route segments [i...j] and/or [j...k])"""
    # generate candidates
    c2 = s[0:i+1] + list(reversed(s[i+1:j+1])) + s[j+1:]
    c3 = s[0:j+1] + list(reversed(s[j+1:k+1])) + s[k+1:]
    c4 = s[0:i+1] + list(reversed(s[i+1:j+1])) + list(reversed(s[j+1:k+1])) + s[k+1:]
    c5 = s[0:i+1] + s[j+1:k+1] + s[i+1:j+1] + s[k+1:]
    c6 = s[0:i+1] + s[j+1:k+1] + list(reversed(s[i+1:j+1])) + s[k+1:]
    c7 = s[0:i+1] + list(reversed(s[j+1:k+1])) + s[i+1:j+1] + s[k+1:]
    c8 = s[0:i+1] + list(reversed(s[j+1:k+1])) + list(reversed(s[i+1:j+1])) + s[k+1:]
    # evaluate candidates
    c2_fs = c3_fs = c4_fs = float("inf")
    if i != j - 1:  # otherwise no new solution is generated!
        c2_fs = full_eval(d, c2)
    if j != k - 1:  # otherwise no new solution is generated!
        c3_fs = full_eval(d, c3)
    if i != j - 1 and j != k - 1:  # otherwise no new solution is generated!
        c4_fs = full_eval(d, c4)
    c5_fs = full_eval(d, c5)
    c6_fs = full_eval(d, c6)
    c7_fs = full_eval(d, c7)
    c8_fs = full_eval(d, c8)
    c_fs = min(c2_fs, c3_fs, c4_fs, c5_fs, c6_fs, c7_fs, c8_fs)
    if c2_fs == c_fs:
        s = c2_fs
    elif c3_fs == c_fs:
        s = c3_fs
    elif c4_fs == c_fs:
        s = c4_fs
    elif c5_fs == c_fs:
        s = c5_fs
    elif c6_fs == c_fs:
        s = c6_fs
    elif c7_fs == c_fs:
        s = c7_fs
    elif c8_fs == c_fs:
        s = c8_fs
    return s, c_fs


def move_to_neighbor(N, d, fs, s):
    """"Do either a 2-opt or a 3-opt move depending on the given neighbor N"""
    if len(N[0]) == 3:  # 2-opt neighbor
        s, fs = two_opt_move(d, s, fs, N[0][1], N[0][2])
    elif len(N[0]) == 4:  # 3-opt neighbor
        s, fs = three_opt_move(d, s, fs, N[0][1], N[0][2], N[0][3])
    return s, fs


def full_eval(d, s):
    """Full objective function evaluation (please avoid it!)"""
    fs = 0
    for i in range(len(s) - 1):
        fs += d[s[i]][s[i + 1]]
    return fs
