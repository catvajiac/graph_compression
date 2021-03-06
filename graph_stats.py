#!/usr/bin/env python

import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy
import pickle
import sys
import os

STATS = ['number of edges', 'number of nodes', 'L1 norm of first eigenvector', 'L2 norm of first eigenvector', 'max. supernode size']

def make_all_dirs(dir_list):
    for d in dir_list:
        if not os.path.isdir('./' + d):
            os.mkdir('./' + d)


def usage(code):
    print('Usage: graph_stats.py [filename]')
    exit(code)

def L1norm(vector):
    total = 0
    for elem in vector:
        total += abs(elem)

    return float(total)


def log(lst):
    # dont want generator, b/c matplotlib can't handle it
    return list([math.log10(x) if x != 0 else 0 for x in lst])


def plot(g, stats, filename):
    for label, stat in stats.items():
        if label == 'timestamps':
            continue
        plt.plot(stats['timestamps'], stat, label=label)

    plt.legend()
    plt.title('Metrics over time on compressed graph')
    plt.xticks(rotation=70)
    plt.xlabel('Year')
    plt.ylabel('log10(Metric value)')
    plt.savefig('./plots/' + filename + '.png')
    plt.show()


def pad_vector(v, length):
    return numpy.pad(v, [[0, length], [0, 0]], 'constant')


def calc_stats(g, take_log=True):
    stats = {stat: [] for stat in STATS}
    #stats['timestamps'] = list([t for t in g])
    last_eig = numpy.zeros(shape=(2, 1))

    timestamps = list(map(int, [t for t in g]))
    stats['timestamps'] = list(map(str, range(min(timestamps), max(timestamps)+1)))
    #stats['timestamps'] = timestamps

    #for timestamp, graph in g.items():
    for timestamp in range(min(timestamps), max(timestamps)+1):
        if str(timestamp) not in g:
            for stat in stats:
                if stat == 'timestamps':
                    continue
                stats[stat].append(stats[stat][-1])
            continue

        graph = g[str(timestamp)]
        stats['number of nodes'].append(len(graph.nodes))
        stats['number of edges'].append(len(graph.edges))

        contains = nx.get_node_attributes(graph, 'contains')
        max_supernode_size = max(len(v) for _, v in contains.items())
        print(max_supernode_size)
        stats['max. supernode size'].append(max_supernode_size)

        # eigenvalues
        vals, vectors = numpy.linalg.eig(nx.convert_matrix.to_numpy_matrix(graph))
        vectors = sorted(zip(vals,vectors.T), key=lambda x: x[0].real, reverse=True)
        vector = vectors[0][1].T
        # pad eigenvectors with zeros, so we can compare
        new_len = vector.shape[0]
        curr_len = last_eig.shape[0]
        curr_eig = vector

        curr_eig = pad_vector(curr_eig, curr_len - new_len) if curr_len > new_len else curr_eig
        last_eig = pad_vector(last_eig, new_len - curr_len) if new_len > curr_len else last_eig


        change_vec = numpy.subtract(curr_eig, last_eig)
        if timestamp == '1945':
            print(timestamp, change_vec)
        stats['L1 norm of first eigenvector'].append(L1norm(change_vec))
        stats['L2 norm of first eigenvector'].append(numpy.linalg.norm(change_vec))
        last_eig = vector

    if take_log:
        stats['number of edges'] = log(stats['number of edges'])
        stats['number of nodes'] = log(stats['number of nodes'])
        stats['L1 norm of first eigenvector'] = log(stats['L1 norm of first eigenvector'])
        stats['L2 norm of first eigenvector'] = log(stats['L2 norm of first eigenvector'])
        stats['max. supernode size'] = log(stats['max. supernode size'])

    for k, v in stats.items():
        print(k, len(v))
    return stats



if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage(1)

    filename = sys.argv[1].strip()
    prefix = filename.split('/')[-1].split('.')[0]
    make_all_dirs(['plots'])
    if filename.endswith('.pkl'):
        with open(filename, 'rb') as f:
            g = pickle.load(f)
    else:
        read_graph(filename)

    stats = calc_stats(g)
    plot(g, stats, prefix)
