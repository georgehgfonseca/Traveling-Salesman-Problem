import tsp
import util
import random
import metaheuristics
import mip
import sys
from params import Params


def main(args):
    params = Params(args)         # read command line parameters
    d, coord = util.read_tsp(params.instance)
    if params.seed:
        random.seed(params.seed)  # change/remove to allow new random behavior (and solutions)
    if params.timelimit is None:
        params.timelimit = len(d)
        print("Unspecified run time limit set to (num cities)", params.timelimit, "\n")

    # build initial solution
    if params.constructive == "PARTGREEDY":
        s_ini, fs_ini, t = tsp.part_greedy_build(d, params.alpha)
    elif params.constructive == "GREEDY":
        s_ini, fs_ini, t = tsp.greedy_build(d)
    print("Initial solution of cost: ", round(fs_ini, 2))

    # run selected algorithm
    print("Running", params.algorithm)
    if params.algorithm == "GRASP":
        s, fs, t, data = metaheuristics.grasp(d, params)
    elif params.algorithm == "TS":
        s, fs, t, data = metaheuristics.tabu_search(d, s_ini, fs_ini, params)
    elif params.algorithm == "SA":
        s, fs, t, data = metaheuristics.simulated_annealing(d, s_ini, fs_ini, params)
    elif params.algorithm == "VNS":
        s, fs, t, data = metaheuristics.vns(d, s_ini, fs_ini, params)
    elif params.algorithm == "ILS":
        s, fs, t, data = metaheuristics.ils(d, s_ini, fs_ini, params)
    elif params.algorithm == "FIXOPT":
        s, fs, t, data = mip.fix_opt(coord, d, s_ini, fs_ini, params)
    elif params.algorithm == "MIP":
        s, fs, t, data = mip.full_model(coord, d, s_ini, fs_ini, params)

    # write outputs (if allowed)
    if params.chart:
        util.plot_chart(data, f'output/{params.instance} {params.algorithm} {params.seed}.png', f'{params.algorithm} convergence chart', params.lb)
    if params.output:
        util.plot_sol(s, coord, f'output/{params.instance} {params.algorithm} {params.seed}.html', title=f'{params.instance} {params.algorithm} {params.seed} Cost `{round(fs, 2)}')

    # needed to iRace
    print(round(fs, 2), end="")


if __name__ == "__main__":
    main(sys.argv)


# old code, just ignore it!
# ==================================== lecture test problem data and solution ==========================================
# dataset = "test_6_nodes"
# d = [[0, 9, 1, 4, 9, 1],
#      [9, 0, 5, 9, 7, 8],
#      [1, 5, 0, 3, 8, 6],
#      [4, 9, 3, 0, 2, 6],
#      [9, 7, 8, 2, 0, 2],
#      [1, 8, 6, 6, 2, 0]]
#
# s_ini = [0, 2, 3, 4, 5, 1, 0]
# fs_ini = 25
# t = 0.00

# ==================================== real problem data and greedy initial solution ===================================
# seed = 1
# random.seed(seed)  # change/remove to allow new random behavior (and solutions)
# datasets = ["Datasets/a280.tsp",
#             "Datasets/ali535.tsp",
#             "Datasets/att48.tsp",
#             "Datasets/burma14.tsp",
#             "Datasets/ch130.tsp",
#             "Datasets/fl1577.tsp",
#             "Datasets/fl3795.tsp",
#             "Datasets/kroA150.tsp",
#             "Datasets/pcb1173.tsp",
#             "Datasets/rat783.tsp"]
#
# # best known solution (upper bound) for each instance (in the same order of datasets)
# ubs = [2586.77,
#        202310.00,
#        33523.71,
#        30.88,
#        6110.72,
#        22249.00,
#        28772.00,
#        26524.86,
#        56931.51,
#        8842.99]
# dataset = datasets[-2]
# ub = ubs[-2]
# d, coord = util.read_tsp(dataset)
# alpha = 0.0
# s_ini, fs_ini, t = tsp.part_greedy_build(d, alpha)
#
# # =============================================== results table header =================================================
# print("=" * 13 + " " + f'{dataset:42}' + " " + "=" * 13)
# print(f'| Method               |                   s* |                 t(s) |')
# print(f'| Ini soln. alpha={round(alpha, 2):1.2f} | {round(fs_ini, 2):20.2f} | {round(t, 2):20.2f} |')
# print("=" * 70)
#
# # =============================================== local search methods =================================================
# s, fs, t = local_search.descent_two_opt(d, s_ini[:], fs_ini)
# print(f'| Descent 2-opt        | {round(fs, 2):20.2f} | {round(t, 2):20.2f} |')

# s, fs, t = local_search.first_improvement_two_opt(d, s_ini[:], fs_ini)
# print(f'| First Improv. 2-opt  | {round(fs, 2):20.2f} | {round(t, 2):20.2f} |')
#
# k = 1000
# max_it = len(d) * k
# s, fs, t = local_search.random_descent_two_opt(d, s_ini[:], fs_ini, max_it)
# print(f'| Random Descent 2-opt | {round(fs, 2):20.2f} | {round(t, 2):20.2f} |')
#
# s, fs, t = local_search.vnd(d, s_ini[:], fs_ini, 2)
# print(f'| VND 2-opt & 3-opt    | {round(fs, 2):20.2f} | {round(t, 2):20.2f} |')
# print("=" * 70)

# ============================================ local search meta-heuristics ============================================
# grasp_it_max = 20
# alpha = 0.05
# s_grasp, fs_grasp, t_grasp, data_grasp = metaheuristics.grasp(d, grasp_it_max, alpha)
# print(f'| GRASP {round(alpha, 2):1.2f} {grasp_it_max:3d}x      | {round(fs_grasp, 2):20.2f} | {round(t_grasp, 2):20.2f} |')
# util.plot_chart(data_grasp, f'{dataset} GRASP {seed}.png', f'GRASP convergence chart (alpha={alpha:1.2f})', ub)
# util.plot_sol(s_grasp, coord, f'{dataset} GRASP {seed}.html', title=f'{dataset} GRASP {seed} Cost `{round(fs_grasp, 2)}')
#
# tabu_it_max = 50
# tabu_max = 15
# s_ts, fs_ts, t_ts, data_ts = metaheuristics.tabu_search(d, s_ini, fs_ini, tabu_it_max, tabu_max)
# print(f'| Busca Tabu {tabu_max:3d} {tabu_it_max:4d}x | {round(fs_ts, 2):20.2f} | {round(t_ts, 2):20.2f} |')
# util.plot_chart(data_ts, f'{dataset} TS {seed}.png', f'Tabu Search convergence chart (tabu_max={tabu_max}, ir_max={tabu_it_max})', ub)
# util.plot_sol(s_ts, coord, f'{dataset} TS {seed}.html', title=f'{dataset} TS {seed} Cost `{round(fs_ts, 2)}')
#
# k = 300
# sa_max = len(d) * k
# alpha = 0.9
# s_sa, fs_sa, t_sa, data_sa = metaheuristics.simulated_annealing(d, s_ini, fs_ini, alpha, sa_max)
# print(f'| SA alpha={round(alpha, 2):1.2f} {sa_max:6d} | {round(fs_sa, 2):20.2f} | {round(t_sa, 2):20.2f} |')
# util.plot_chart(data_sa, f'{dataset} SA {seed}.png', f'SA convergence chart (alpha={alpha:1.2f}, SAmax={sa_max})', ub)
# util.plot_sol(s_sa, coord, f'{dataset} SA {seed}.html', title=f'{dataset} SA {seed} Cost `{round(fs_sa, 2)}')
#
# max_k = 2
# vns_it_max = 10
# k = 1000
# ls_max = len(d) * k
# s_vns, fs_vns, t_vns, data_vns = metaheuristics.vns(d, s_ini, fs_ini, vns_it_max, max_k, ls_max)
# print(f'| VNS k={max_k:2d} iters={vns_it_max:4d}x | {round(fs_vns, 2):20.2f} | {round(t_vns, 2):20.2f} |')
# util.plot_chart(data_vns, f'{dataset} VNS {seed}.png', f'VNS convergence chart (max_k={max_k})', ub)
# util.plot_sol(s_vns, coord, f'{dataset} VNS {seed}.html', title=f'{dataset} VNS {seed} Cost `{round(fs_vns, 2)}')
#
# ils_it_max = 25
# p_level = 2
# k = 1000
# ls_max = len(d) * k
# s_ils, fs_ils, t_ils, data_ils = metaheuristics.ils(d, s_ini, fs_ini, ils_it_max, p_level, ls_max)
# print(f'| ILS  p={p_level} iters={ils_it_max:4d}x | {round(fs_ils, 2):20.2f} | {round(t_ils, 2):20.2f} |')
# util.plot_chart(data_ils, f'{dataset} ILS {seed}.png', f'ILS convergence chart (p_level={p_level:2d})', ub)
# util.plot_sol(s_ils, coord, f'{dataset} ILS {seed}.html', title=f'{dataset} ILS {seed} Cost `{round(fs_ils, 2)}')
# print("=" * 70)

# # ================================================ mip-based algorithms ================================================
# timelimit = 600
# #mip.run_all(dataset)
# s_mip, fs_mip, t_mip = mip.full_model(coord, s, timelimit)
# print(f'| MIP    timelimit={timelimit} | {round(fs_mip, 2):20.2f} | {round(t_mip, 2):20.2f} |')
#
# timelimit_it = timelimit / 10
# n_nodes = int(len(d) / 5)
# s_fix_opt, fs_fix_opt, t_fix_opt, data_fixopt = mip.fix_opt(coord, s, fs, n_nodes, timelimit, timelimit_it)
# print(f'| Fix-Opt  tl={timelimit_it} n={n_nodes} | {round(fs_fix_opt, 2):20.2f} | {round(t_fix_opt, 2):20.2f} |')
# util.plot_chart(data_fixopt, f'{dataset} Fix-Opt {seed}.png', f'Fix-Opt convergence chart (n_nodes={timelimit_it:.2f})', ub)
# util.plot_sol(s_fix_opt, coord, f'{dataset} Fix-Opt {seed}.html', title=f'{dataset} Fix-Opt {seed} Cost `{round(fs_fix_opt, 2)}')
#
# timelimit_it = timelimit / 10
# n_nodes = int(len(d) / 5)
# s_fix_opt_seq, fs_fix_opt_seq, t_fix_opt_seq, data_fixopt_seq = mip.mip_fix_opt_seq(coord, s, fs, n_nodes, timelimit, timelimit_it)
# print(f'| Fix-OptS tl={timelimit_it} n={n_nodes} | {round(fs_fix_opt_seq, 2):20.2f} | {round(t_fix_opt_seq, 2):20.2f} |')
# util.plot_chart(data_fixopt_seq, f'{dataset} Fix-Opt Seq {seed}.png', f'Fix-Opt convergence chart (n_nodes={timelimit_it:.2f})', ub)
# util.plot_sol(s_fix_opt_seq, coord, f'{dataset} Fix-Opt Seq {seed}.html', title=f'{dataset} Fix-Opt {seed} Cost `{round(fs_fix_opt_seq, 2)}')

# ========================================== population-based meta-heuristics ==========================================

# ================================================ charting and plotting ===============================================
# overall_data = [data_grasp, data_ts, data_sa, data_vns, data_ils, data_fixopt, data_fixopt_seq]
# methods = ['GRASP', 'TS', 'SA', 'VNS', 'ILS', 'FixOpt', 'FixOptSeq']
# util.plot_overall_chart(overall_data, methods, f'{dataset} ALL {seed}.png', f'Comparison of {methods}', ub)
# ======================================================================================================================
