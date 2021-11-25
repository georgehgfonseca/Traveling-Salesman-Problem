=========================================================================
   Brief description
=========================================================================
Source code of metaheuristics applied to the Traveling Salesman Problem
Developed by Prof. George Fonseca (george@ufop.edu.br)
PEP300 Metaheuristics applied to Combinatorial Optimization (PPGEP/UFOP)
Website: <http://professor.ufop.br/george/classes/pep300>
=========================================================================
   Licence:
=========================================================================
Metaheuristics applied to the Traveling Salesman Problem
Copyright (C) 2021  George Fonseca (george@ufop.edu.br)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=========================================================================
   Prerequisites:
=========================================================================
1. Requires python 3.X <https://www.python.org/downloads/>

2. Required packages:
bokeh==2.4.0
numpy==1.21.2
gurobipy==9.1.2
matplotlib==3.4.3

Simply install them by command line:
pip install -r requirements.txt

Or install one by one manually:
pip install bokeh
pip install numpy
pip install gurobipy
pip install matplotlib

To run MIP-based algorithms, a Gurobi (https://www.gurobi.com/) licence 
must be configured.
==========================================================================
   Running:
==========================================================================
Command line to run this software is:

python main.py <instance> [params]

Instance:
    <instance> : Path of the instance file in TSPLIB95 format.

Params:
  -timelimit <time>     : runtime limit (secs) (default: = num cities).
  -seed <seed>          : random seed (default: None).
  -verbose <0/1>        : print algorithm logs (0/1) (default: 1).
  -lb <value>           : lower bound for this instance (default: 0).
  -output <0/1>         : plot the solution to /output folder (0/1) (default: 1).
  -chart <0/1>          : write convergence chart to /output folder (0/1)  (default: 1).
  -constructive <value> : select the constructive method to build initial solutions; possible values are
                          {{GREEDY, PARTGREEDY}} (default: PARTGREEDY)
  -alpha <value>        : alpha value to the partially greedy constructive algorithm (default: 0.0).
  -algorithm <value>    : select the optimization algorithm to execute; possible values are
                          {{GRASP, TS, SA, VNS, ILS, FIXOPT, MIP}} (default: ILS)
  -localsearch <value>  : local search method to use inside the main algorithm; possible values are
                          {{RANDOM*, RANDOM2, RANDOM3, DESCENT2, DESCENT3, FIRSTIMPROV2, FIRSTIMPROV3, VND*}}
                          (2 = 2-opt | 3 = 3-opt | * = both) (default: RANDOM*)
  -neigh_types <n>      : number of neighborhood types to apply (1=2-opt / 2=2-opt and 3-opt) (default: 2).
  -ls_max <n>           : maximum number of random local search iters (default: 1000).
  -grasp_alpha <value>  : alpha value to GRASP algorithm (default: 0.10).
  -sa_t_0 <value>       : initial temperature value to Simulated Annealing algorithm (default: 100).
  -sa_alpha <value>     : alpha value to Simulated Annealing algorithm (default: 0.9).
  -sa_max <value>       : SAmax value (* num cities) to Simulated Annealing algorithm (default: 100).
  -tabu_max <value>     : size of tabu list of Tabu Search algorithm (default: 100).
  -vns_max_k <value>    : maximum neighborhood size to VNS algorithm (default: 2).
  -ils_p_level <value>  : perturbation level to ILS algorithm (default: 3).
  -fixopt_it_tl <time>  : runtime limit (secs) for each iteration of fixopt (default: 60).
  -fixopt_n <n>         : number of cities to be optimized at each iteration of fixopt (default: 200).

Example:
  python main.py /datasets/att48.tsp -timelimit 60 -seed 1 -algorithm GRASP -localsearch VND* -grasp_alpha 0.1

=============================================================================================
