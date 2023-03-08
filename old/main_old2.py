import networkx as nx
import nltk
from operator import itemgetter
import xlrd
import spacy
import string
import os

from matplotlib import pyplot as plt

nlp = spacy.load('es_core_news_sm')


def ConstruyeGrafos():
    lista_grafos = []
    nombre_archivo = "corpus/NAP.xls"
    libro = xlrd.open_workbook(nombre_archivo)
    hoja = libro.sheet_by_index(0)
    GrafoFrec = nx.Graph()
    GrafoTiempo = nx.Graph()
    GrafoAsoc = nx.Graph()
    num_filas = hoja.nrows
    estimulo = ''
    lema = ''
    frecuencia = 0
    tiempo = 0
    asociacion = 0
    for fila in range(0, num_filas - 1):
        celda = hoja.cell(fila, 0)
        cadena = celda.value
        if cadena == '--PALABRAS--':
            continue
        elif cadena == '======':
            estimulo = hoja.cell(fila + 1, 4).value
        elif cadena == '' or cadena == '*':
            continue
        elif hoja.cell(fila, 2).value == '':
            continue
        else:
            frecuencia = hoja.cell(fila, 1).value
            tiempo = hoja.cell(fila, 2).value
            asociacion = hoja.cell(fila, 3).value
            palabra = hoja.cell(fila, 4).value
            estimulo = estimulo.strip()
            lema = str(palabra)
            lema = lema.strip()
            if estimulo != '' and lema != '':
                GrafoFrec.add_edge(estimulo, lema, weight=1 / float(frecuencia))
                GrafoTiempo.add_edge(estimulo, lema, weight=float(tiempo))
                GrafoAsoc.add_edge(estimulo, lema, weight=100 - float(asociacion))
    lista_grafos.append(GrafoFrec)
    lista_grafos.append(GrafoTiempo)
    lista_grafos.append(GrafoAsoc)
    # print(GrafoFrec.edges)
    return lista_grafos


print('Construye Grafos')
print(ConstruyeGrafos())


def limpia_lematiza(cadena):
    limpiado = ''
    palabras_funcionales = nltk.corpus.stopwords.words('spanish')
    for c in string.punctuation:
        cadena = cadena.replace(c, "")
    cadena = cadena.strip()
    for palabra in cadena.split(" "):
        if palabra not in palabras_funcionales:
            # doc = nlp(palabra)
            # limpiado += doc[0].lemma_+ " "
            limpiado += palabra + " "
    return limpiado


print('Limpia y lematiza')
print(limpia_lematiza("obreras pequeñitas"))


def conceptos(lista, subconjunto):
    datos = []
    if len(lista) <= 100:
        tope = len(lista)
    else:
        tope = 100
    for x in range(0, tope):
        if str(lista[x][0]) not in subconjunto and float(lista[x][1]) > 0:
            datos.append(str(lista[x][0]))
    return datos


def diccionario_nap(definicion):
    grafo = ConstruyeGrafos()
    grafo_frec = grafo[0]
    grafo_tiempo = grafo[1]
    grafo_asoc = grafo[2]
    texto = limpia_lematiza(definicion)
    texto = texto.lower()
    tokens = texto.split(" ")
    subconjunto_lemas = []
    for palabra in tokens:
        if palabra in grafo_asoc.nodes() and palabra != '':
            subconjunto_lemas.append(palabra)
    if len(subconjunto_lemas) > 0:
        resultados_asociacion = nx.betweenness_centrality_subset(grafo_asoc, subconjunto_lemas, subconjunto_lemas,
                                                                 normalized=True, weight="weight")
        encontrados = sorted(resultados_asociacion.items(), key=itemgetter(1), reverse=True)[0:99]
        print("Asociación")
        print(conceptos(encontrados, subconjunto_lemas))

        resultados_frecuencia = nx.betweenness_centrality_subset(grafo_frec, subconjunto_lemas, subconjunto_lemas,
                                                                 normalized=True, weight="weight")
        encontrados = sorted(resultados_frecuencia.items(), key=itemgetter(1), reverse=True)[0:99]
        print("Frecuencia")
        print(conceptos(encontrados, subconjunto_lemas))

        resultados_tiempo = nx.betweenness_centrality_subset(grafo_tiempo, subconjunto_lemas, subconjunto_lemas,
                                                             normalized=True, weight="weight")
        encontrados = sorted(resultados_tiempo.items(), key=itemgetter(1), reverse=True)[0:99]
        print("Tiempo")
        print(conceptos(encontrados, subconjunto_lemas))

    return


ConstruyeGrafos()

print('Diccionario NAP')
print(diccionario_nap("El aparato doméstico para lavar ropa"))


def precision(k, arreglo, concepto):
    tope = k
    encontrado = 0
    if k > len(arreglo):
        tope = len(arreglo)
    for i in range(0, tope):
        if arreglo[i] == concepto.strip():
            encontrado = 1
    return encontrado


def diccionario_btc(grafo, definicion):
    texto = limpia_lematiza(definicion)
    texto = texto.lower()
    tokens = texto.split(" ")
    subconjunto_lemas = []
    for palabra in tokens:
        if palabra in grafo.nodes() and palabra != '':
            subconjunto_lemas.append(palabra)
    if len(subconjunto_lemas) > 0:
        resultados = nx.betweenness_centrality_subset(grafo, subconjunto_lemas, subconjunto_lemas, normalized=True,
                                                      weight="weight")
        encontrados = sorted(resultados.items(), key=itemgetter(1), reverse=True)[0:99]
        return conceptos(encontrados, subconjunto_lemas)
    else:
        return []


def rendimiento_mdbl_btc():
    grafo = ConstruyeGrafos()
    grafo_frec = grafo[0]
    grafo_tiempo = grafo[1]
    grafo_asoc = grafo[2]

    p_1_t = p_1_f = p_1_a = 0
    p_3_t = p_3_f = p_3_a = 0
    p_5_t = p_5_f = p_5_a = 0
    total = 0

    directorio = "./corpus/definiciones_freeling/"
    for archivo in os.listdir(directorio):
        datos = open(directorio + archivo, encoding="utf8")
        lineas = datos.readlines()
        concepto = str(lineas[0]).lower()
        for linea in lineas[1:]:
            if linea.strip() != '':
                total += 1
                candidatos = diccionario_btc(grafo_asoc, linea)
                # print(candidatos,concepto)
                p_1_a += precision(1, candidatos, concepto)
                p_3_a += precision(3, candidatos, concepto)
                p_5_a += precision(5, candidatos, concepto)
                candidatos = diccionario_btc(grafo_frec, linea)
                # print(candidatos,concepto)
                p_1_f += precision(1, candidatos, concepto)
                p_3_f += precision(3, candidatos, concepto)
                p_5_f += precision(5, candidatos, concepto)
                candidatos = diccionario_btc(grafo_tiempo, linea)
                # print(candidatos,concepto)
                p_1_t += precision(1, candidatos, concepto)
                p_3_t += precision(3, candidatos, concepto)
                p_5_t += precision(5, candidatos, concepto)
                # input()
        datos.close()
    print("Asociacion")
    print("p@1:", p_1_a / total, "p@3:", p_3_a / total, "p@5", p_5_a / total)
    print("Frecuencia")
    print("p@1:", p_1_f / total, "p@3:", p_3_f / total, "p@5", p_5_f / total)
    print("Tiempo")
    print("p@1:", p_1_t / total, "p@3:", p_3_t / total, "p@5", p_5_t / total)
    return


# print('Rendimiento MBDL vs BTC')
# print(rendimiento_mdbl_btc())


def reduce_graph(graph: nx.Graph, subset: list) -> nx.Graph:
    sub_graph = nx.Graph()
    for node in subset:
        if node not in graph.nodes():
            continue
        for neighbor in graph.neighbors(node):
            weight = graph[node][neighbor]['weight']
            sub_graph.add_edge(node, neighbor, weight=weight)
    return sub_graph


def draw_graph(graph: nx.Graph):
    nx.draw(
        graph,
        with_labels=True,
        font_weight='bold',
        node_size=1000,
        node_color='green',
        # pos=nx.get_node_attributes(self._graph, 'pos'),
    )
    plt.show()


def test_reduce():
    grafo = ConstruyeGrafos()
    grafo_frec = grafo[0]
    grafo_tiempo = grafo[1]
    grafo_asoc = grafo[2]

    directorio = "./corpus/definiciones_freeling/"
    for archivo in os.listdir(directorio):
        datos = open(directorio + archivo, encoding="utf8")
        lineas = datos.readlines()
        concepto = str(lineas[0]).lower()
        for linea in lineas[1:]:
            linea = linea.strip()
            if linea != '':
                linea = limpia_lematiza(linea)
                my_subset: list = linea.split()

                grafo_frec_reducido = reduce_graph(grafo_frec, my_subset)

                draw_graph(grafo_frec_reducido)

                # btc
                result = nx.betweenness_centrality(grafo_frec_reducido, normalized=True, weight="weight")
                for w in my_subset:
                    if w in result:
                        result.pop(w)

                print()
                print('concepto')
                print(concepto.strip())
                print(linea)
                print(result)


test_reduce()

print('end')
