from typing import List
import scipy as sp
from matplotlib import pyplot as plt
import networkx as nx

from DataSet import DataSet
from Definition import Definition
from Graphs import Graphs


def draw(graph: nx.Graph):
    nx.draw(
        graph,
        with_labels=True,
        font_weight='bold',
        node_size=1000,
        node_color='green',
    )
    plt.show()


# no tiene en cuenta conexiones entre nodos vecinos
def reduce_graph_1(graph: nx.Graph, subset: list) -> nx.Graph:
    sub_graph = nx.Graph()
    for node in subset:
        if node not in graph.nodes():
            continue
        for neighbor in graph.neighbors(node):
            weight = graph[node][neighbor]['weight']
            sub_graph.add_edge(node, neighbor, weight=weight)
    return sub_graph


def reduce_graph(graph: nx.Graph, subset: list) -> nx.Graph:
    return reduce_graph_1(graph, subset)


def bt_centrality(graph: nx.Graph, subset: List[str]) -> dict:
    sub_graph = reduce_graph(graph, subset)
    result = nx.betweenness_centrality(sub_graph, normalized=True, weight="weight")
    for w in subset:
        if w in result:
            result.pop(w)
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return result


def com_bt_centrality(graph: nx.Graph, subset: List[str]) -> dict:
    sub_graph = reduce_graph(graph, subset)
    result = nx.communicability_betweenness_centrality(sub_graph)
    for w in subset:
        if w in result:
            result.pop(w)
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return result


def precision(word_input: str, btc, k: int = 1) -> int:
    count = min(k, len(btc))
    for i in range(count):
        b = list(btc.keys())[i]
        if b == word_input:
            return 1
    return 0


def build_definitions_graph(graphs: Graphs, definitions: List[Definition], draw_graph: bool = False):
    total: int = 0
    p = {
        'frequency': [0, 0, 0],
        'time': [0, 0, 0],
        'association': [0, 0, 0],
        'communicability': [0, 0, 0],
    }
    for definition in definitions:
        print('\033[32m' + f'Input: {definition.word_input}' + '\033[0m')
        for word_output in definition.word_outputs:
            print('\033[33m' + f'Output: {word_output}' + '\033[0m')
            sub_graph = reduce_graph(graphs.graph_frequency, word_output)
            print('Frequency ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            p['frequency'][0] += precision(definition.word_input, btc, 1)
            p['frequency'][1] += precision(definition.word_input, btc, 3)
            p['frequency'][2] += precision(definition.word_input, btc, 5)
            print('\033[35m' + str(btc) + '\033[0m')
            if draw_graph:
                draw(sub_graph)
            sub_graph = reduce_graph(graphs.graph_time, word_output)
            print('Time ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            p['time'][0] += precision(definition.word_input, btc, 1)
            p['time'][1] += precision(definition.word_input, btc, 3)
            p['time'][2] += precision(definition.word_input, btc, 5)
            print('\033[35m' + str(btc) + '\033[0m')
            if draw_graph:
                draw(sub_graph)
            sub_graph = reduce_graph(graphs.graph_association, word_output)
            print('Association ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            p['association'][0] += precision(definition.word_input, btc, 1)
            p['association'][1] += precision(definition.word_input, btc, 3)
            p['association'][2] += precision(definition.word_input, btc, 5)
            print('\033[35m' + str(btc) + '\033[0m')
            if draw_graph:
                draw(sub_graph)
            print('Communicability ' + str(sub_graph))
            btc = com_bt_centrality(sub_graph, word_output)
            p['communicability'][0] += precision(definition.word_input, btc, 1)
            p['communicability'][1] += precision(definition.word_input, btc, 3)
            p['communicability'][2] += precision(definition.word_input, btc, 5)
            print('\033[35m' + str(btc) + '\033[0m')
            if draw_graph:
                draw(sub_graph)
            total += 1
    for k in p.keys():
        for i in range(3):
            p[k][i] /= total
    print(p)


if __name__ == '__main__':
    data_set = DataSet()
    # Import Graphs
    the_graphs = data_set.import_graphs()
    print('Frequency ' + str(the_graphs.graph_frequency))
    print('Time ' + str(the_graphs.graph_time))
    print('Association ' + str(the_graphs.graph_association))
    # Import Definitions
    the_definitions = data_set.import_definitions()
    print('Definitions ' + str(the_definitions))
    # Build Graphs
    build_definitions_graph(the_graphs, the_definitions)
