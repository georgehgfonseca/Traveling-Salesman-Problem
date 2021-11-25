import matplotlib.pyplot as plt
import numpy as np
from bokeh.plotting import figure, show, save, output_file


def read_tsp(file_path):
    """"Read a TSP instance in TSPLIB95 format
    http://elib.zib.de/pub/mp-testdata/tsp/tsplib/tsp/index.html"""
    file = open(file_path, "r")
    coord = []
    # find coordinates section
    for line in file:
        if line.find("NODE_COORD_SECTION") != -1:
            break
    # read coordinates until EOF
    for line in file:
        if line.find("EOF") != -1:
            break
        line = line.strip().split(" ")
        i = int(line[0])
        x = float(line[1])
        y = float(line[2])
        coord.append((i, x, y))
    n = len(coord)
    # calculate Euclidean Distances
    d = [[0 for _ in range(n)] for _ in range(n)]
    for (i, xi, yi) in coord:
        for (j, xj, yj) in coord:
            if i != j:
                d[i - 1][j - 1] = ((xi - xj) ** 2 + (yi - yj) ** 2) ** (1 / 2)
    return d, coord


def plot_chart(chart_data, file, title, ub=None):
    fig, ax = plt.subplots()
    chart_data = np.array(chart_data)
    plt.plot(chart_data[:, 0], chart_data[:, 1], 'b--', chart_data[:, 0], chart_data[:, 2], 'r-')
    if ub:  # print optimal solution cost base line
        plt.axhline(y=ub, color='k', linestyle='--')
    plt.legend(('Current', 'Best', 'BKS'),
               loc='upper right', shadow=True)
    ax.set(xlabel='time (s)', ylabel='f(s)',
           title=title)
    ax.grid()
    fig.savefig(file)
    # plt.show()


def plot_overall_chart(chart_data, methods, file, title, ub=None):
    fig, ax = plt.subplots()
    styles = ['o-b', '^--g', ',-.r', 'v:c', 's-m', 'vk:', 'v-g', 'o-r', '^--y', ',-.b']
    for i in range(len(chart_data)):
        preprocess_data(chart_data[i])
        data = np.array(chart_data[i])
        plt.plot(data[:, 0], data[:, 2], styles[i])
    if ub is not None:  # print optimal solution cost base line
        plt.axhline(y=ub, color='k', linestyle='--')
        methods.append('BKS')
    plt.legend(methods,
               loc='upper right', shadow=True)
    ax.set(xlabel='time (s)', ylabel='f(s)',
           title=title)
    ax.grid()
    fig.savefig(file)
    # plt.show()


def preprocess_data(data):
    """"Remove duplicated best solution records"""
    i  = 0
    while i + 1 < len(data):
        if data[i][2] == data[i+1][2]:
            data.pop(i+1)
        else:
            i += 1


def plot_sol(s, coord, file_name, title="", path=False):
    """"Print a TSP solution"""
    fig = figure(title=title)
    i, x, y = zip(*coord)
    fig.circle(x, y, size=8)
    ptseq = [coord[k] for k in s]
    if not path:
        ptseq.append(ptseq[0])
    i, x, y = zip(*ptseq)
    fig.line(x, y)

    #show(fig)
    output_file(file_name)
    save(fig)
    #export_png(fig, filename=file_name)
    # fig.outpsavefig(file_name)