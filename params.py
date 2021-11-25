import sys

class Params:

    def __init__(self, args):
        # default parameter values
        self.instance = None
        self.timelimit = None
        self.seed = None
        self.verbose = 1
        self.lb = 0
        self.output = 0
        self.chart = 0

        self.constructive = "PARTGREEDY"
        self.alpha = 0.0

        self.algorithm = "ILS"
        self.localsearch = "RANDOM*"
        self.neigh_types = 2
        self.ls_max = 1000

        self.grasp_alpha = 0.10
        self.sa_alpha = 0.90
        self.sa_max = 100
        self.sa_t_0 = 100
        self.tabu_max = 100
        self.vns_k_max = 2
        self.ils_p_level = 3
        self.fix_opt_n = 200
        self.fix_opt_it_tl = 60

        if not self.read_args(args):
            self.print_usage()
            sys.exit(0)

    def read_args(self, args):
        print("Arguments: %s\n" % " ".join(args))
        if len(args) == 1:
            print("ERROR: No instance file provided!\n")
            return False
        self.instance = args[1]
        i = 2
        while i < len(args):
            if args[i] == "-timelimit":
                self.timelimit = int(args[i + 1])
                print("Time limit set to %d" % self.timelimit)
                i += 2
            elif args[i] == "-seed":
                self.seed = int(args[i+1])
                print("Random seed set to %d" % self.seed)
                i += 2
            elif args[i] == "-verbose":
                self.verbose = int(args[i+1])
                print("Verbose output set to %d" % self.verbose)
                i += 2
            elif args[i] == "-lb":
                self.lb = float(args[i+1])
                print("Lower bound set to %f" % self.lb)
                i += 2
            elif args[i] == "-output":
                self.output = int(args[i+1])
                print("Output solution will be written to file (0.no/1.yes) %d" % self.output)
                i += 2
            elif args[i] == "-chart":
                self.chart = int(args[i+1])
                print("Convergence chart will be written on file (0.no/1.yes) %d" % self.chart)
                i += 2
            elif args[i] == "-constructive":
                self.constructive = args[i + 1]
                print("Constructive method set to %s" % self.constructive)
                i += 2
            elif args[i] == "-alpha":
                self.alpha = float(args[i+1])
                print("Alpha (partially greedy constriction) set to %f" % self.alpha)
                i += 2
            elif args[i] == "-algorithm":
                self.algorithm = args[i + 1]
                print("Method value set to '%s'" % self.algorithm)
                i += 2
            elif args[i] == "-localsearch":
                self.localsearch = args[i + 1]
                print("Local search method set to %s" % self.localsearch)
                i += 2
            elif args[i] == "-ls_max":
                self.ls_max = int(args[i + 1])
                print("Max local search iters (* num cities) set to %d" % self.ls_max)
                i += 2
            elif args[i] == "-neigh_types":
                self.neigh_types = int(args[i + 1])
                print("Number of neighborhood types set to %d" % self.neigh_types)
                i += 2
            elif args[i] == "-grasp_alpha":
                self.grasp_alpha = float(args[i + 1])
                print("GRASP alpha set to %f" % self.grasp_alpha)
                i += 2
            elif args[i] == "-sa_alpha":
                self.sa_alpha = float(args[i + 1])
                print("SA alpha set to %f" % self.sa_alpha)
                i += 2
            elif args[i] == "-sa_max":
                self.sa_max = int(args[i + 1])
                print("SA max (* num cities) set to %d" % self.sa_max)
                i += 2
            elif args[i] == "-sa_t_0":
                self.sa_t_0 = int(args[i + 1])
                print("SA initial temperature set to %d" % self.sa_t_0)
                i += 2
            elif args[i] == "-tabu_max":
                self.tabu_max = int(args[i + 1])
                print("Tabu list size set to %d" % self.tabu_max)
                i += 2
            elif args[i] == "-vns_k_max":
                self.vns_k_max = int(args[i + 1])
                print("VNS max neighborhood size set to %d" % self.vns_k_max)
                i += 2
            elif args[i] == "-ils_p_level":
                self.ils_p_level = int(args[i + 1])
                print("ILS perturbation level set to %d" % self.ils_p_level)
                i += 2
            elif args[i] == "-fixopt_it_tl":
                self.fix_opt_it_tl = int(args[i + 1])
                print("Fix-Opt time limit for each iteration set to %d" % self.fix_opt_it_tl)
                i += 2
            elif args[i] == "-fixopt_n":
                self.fix_opt_n = int(args[i + 1])
                print("Fix-Opt initial number of cities set to %d" % self.fix_opt_n)
                i += 2
            else:
                print(f'\nWARNING: Unrecognized argument {args[i]}')
                # return False
        print()
        return True

    def print_usage(self):
        print(f"Usage: python main.py <instance> [params]")
        print(f"    <instance> : Path of the instance file in TSPLIB95 format.")
        print(f"")
        print(f"Parameters:")
        print(f"  -timelimit <time>     : runtime limit (secs) (default: = num cities).")
        print(f"  -seed <seed>          : random seed (default: {self.seed}).")
        print(f"  -verbose <0/1>        : print algorithm logs (0/1) (default: {self.verbose}).")
        print(f"  -lb <value>           : lower bound for this instance (default: {self.lb}).")
        print(f"  -output <0/1>         : plot the solution to /output folder (0/1) (default: {self.output}).")
        print(f"  -chart <0/1>          : write convergence chart to /output folder (0/1)  (default: {self.chart}).")
        print(f"  -constructive <value> : select the constructive method to build initial solutions; possible values are")
        print(f"                          {{GREEDY, PARTGREEDY}} (default: {self.constructive})")
        print(f"  -alpha <value>        : alpha value to the partially greedy constructive algorithm (default: {self.alpha}).")
        print(f"  -algorithm <value>    : select the optimization algorithm to execute; possible values are")
        print(f"                          {{GRASP, TS, SA, VNS, ILS, FIXOPT, MIP}} (default: {self.algorithm})")
        print(f"  -localsearch <value>  : local search method to use inside the main algorithm; possible values are")
        print(f"                          {{RANDOM*, RANDOM2, RANDOM3, DESCENT2, DESCENT3, FIRSTIMPROV2, FIRSTIMPROV3, VND*}}")
        print(f"                          (2 = 2-opt | 3 = 3-opt | * = both) (default: {self.localsearch})")
        print(f"  -neigh_types <n>      : number of neighborhood types to apply (1=2-opt / 2=2-opt and 3-opt) (default: {self.neigh_types}).")
        print(f"  -ls_max <n>           : maximum number of random local search iters (default: {self.ls_max}).")
        print(f"  -grasp_alpha <value>  : alpha value to GRASP algorithm (default: {self.grasp_alpha}).")
        print(f"  -sa_t_0 <value>       : initial temperature value to Simulated Annealing algorithm (default: {self.sa_t_0}).")
        print(f"  -sa_alpha <value>     : alpha value to Simulated Annealing algorithm (default: {self.sa_alpha}).")
        print(f"  -sa_max <value>       : SAmax value (* num cities) to Simulated Annealing algorithm (default: {self.sa_max}).")
        print(f"  -tabu_max <value>     : size of tabu list of Tabu Search algorithm (default: {self.tabu_max}).")
        print(f"  -vns_max_k <value>    : maximum neighborhood size to VNS algorithm (default: {self.vns_k_max}).")
        print(f"  -ils_p_level <value>  : perturbation level to ILS algorithm (default: {self.ils_p_level}).")
        print(f"  -fixopt_it_tl <time>  : runtime limit (secs) for each iteration of fixopt (default: {self.fix_opt_it_tl}).")
        print(f"  -fixopt_n <n>         : number of cities to be optimized at each iteration of fixopt (default: {self.fixopt_n}).")
        print(f"")
        print(f"Example:")
        print(f"  python main.py /datasets/att48.tsp -timelimit 60 -seed 1 -algorithm GRASP -localsearch DESCENT2 -grasp_alpha 0.1")
        print(f"")
