from typing import List

from matplotlib import pyplot as plt
import networkx as nx

from DataSet import DataSet
from Definition import Definition


def draw(graph: nx.Graph):
    nx.draw(
        graph,
        with_labels=True,
        font_weight='bold',
        node_size=1000,
        node_color='green',
    )
    plt.show()


def bt_centrality(graph: nx.Graph, subset: List[str]) -> dict:
    sub_graph = reduce_graph(graph, subset)
    result = nx.betweenness_centrality(sub_graph, normalized=True, weight="weight")
    for w in subset:
        if w in result:
            result.pop(w)
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return result


def reduce_graph(graph: nx.Graph, subset: list) -> nx.Graph:
    sub_graph = nx.Graph()
    for node in subset:
        if node not in graph.nodes():
            continue
        for neighbor in graph.neighbors(node):
            weight = graph[node][neighbor]['weight']
            sub_graph.add_edge(node, neighbor, weight=weight)
    return sub_graph


def build_definitions_graph(definitions: List[Definition]):
    for definition in definitions:
        print('\033[32m' + f'Input: {definition.word_input}' + '\033[0m')
        for word_output in definition.word_outputs:
            print('\033[33m' + f'Output: {word_output}' + '\033[0m')
            sub_graph = reduce_graph(graphs.graph_frequency, word_output)
            print('Frequency ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            print('\033[35m' + str(btc) + '\033[0m')
            draw(sub_graph)
            sub_graph = reduce_graph(graphs.graph_time, word_output)
            print('Time ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            print('\033[35m' + str(btc) + '\033[0m')
            draw(sub_graph)
            sub_graph = reduce_graph(graphs.graph_association, word_output)
            print('Association ' + str(sub_graph))
            btc = bt_centrality(sub_graph, word_output)
            print('\033[35m' + str(btc) + '\033[0m')
            draw(sub_graph)


if __name__ == '__main__':
    data_set = DataSet()
    # Import Graphs
    graphs = data_set.import_graphs()
    print('Frequency ' + str(graphs.graph_frequency))
    print('Time ' + str(graphs.graph_time))
    print('Association ' + str(graphs.graph_association))
    # Import Definitions
    the_definitions = data_set.import_definitions()
    print('Definitions ' + str(the_definitions))
    # Build Graphs
    build_definitions_graph(the_definitions)
