from typing import List

import networkx as nx
import nltk
from operator import itemgetter
import xlrd
import spacy
import string
import os
import matplotlib.pyplot as plt
from networkx import Graph

nltk.download('stopwords')
nlp = spacy.load('es_core_news_sm')


def build_graphs():
    lista_grafos = []
    nombre_archivo = "NAP.xls"
    libro = xlrd.open_workbook(nombre_archivo)
    hoja = libro.sheet_by_index(0)
    num_filas = hoja.nrows
    GrafoFrec: Graph = nx.Graph()
    GrafoTiempo = nx.Graph()
    GrafoAsoc = nx.Graph()
    estimulo = ""
    for fila in range(0, num_filas - 1):
        celda = hoja.cell(fila, 0)
        cadena = celda.value
        if cadena == "--PALABRAS--" or cadena == "" or cadena == "=" \
                or hoja.cell(fila, 2).value == "":
            continue
        elif cadena == "======":
            estimulo = hoja.cell(fila + 1, 4).value
        else:
            frecuencia = hoja.cell(fila, 1).value
            tiempo = hoja.cell(fila, 2).value
            asociacion = hoja.cell(fila, 3).value
            palabra = hoja.cell(fila, 4).value
            estimulo = estimulo.strip()
            lema = str(palabra)
            lema = lema.strip()
            GrafoFrec.add_edge(estimulo, lema, weight=1 / float(frecuencia))
            GrafoTiempo.add_edge(estimulo, lema, weight=float(tiempo))
            GrafoAsoc.add_edge(estimulo, lema, weight=100 - float(asociacion))
    lista_grafos.append(GrafoFrec)
    lista_grafos.append(GrafoTiempo)
    lista_grafos.append(GrafoAsoc)
    return lista_grafos


build_graphs()


def clean_lematize(cadena):
    result = ''
    stopwords = nltk.corpus.stopwords.words('spanish')
    for c in string.punctuation:
        cadena = cadena.replace(c, '')
    cadena = cadena.strip()
    for word in cadena.split():
        if word not in stopwords:
            doc = nlp(word)
            result += doc[0].lemma_ + ' '
    return result.strip()


clear = clean_lematize('insecto de rayas que produce miel')
print(clear)


def concepts(the_list: List[dict[str, float]], subset: List[str]):
    data = []
    limit = len(the_list)
    if 100 < limit:
        limit = 100
    for i in range(0, limit):
        if 0. < float(the_list[i][1]) and the_list[i][0] in subset:
            data.append(the_list[i])
    return data


def dictionary_nap(definition: str) -> None:
    grafos = build_graphs()
    graph_frequency = grafos[0]
    graph_time = grafos[1]
    graph_association = grafos[2]
    texto = clean_lematize(definition)
    texto = texto.lower()
    tokens = texto.split()
    subconjunto_lemas = []
    for palabra in tokens:
        if palabra in graph_association.nodes():
            subconjunto_lemas.append(palabra)
    if len(subconjunto_lemas) > 0:
        print(subconjunto_lemas)
        resultados_asoc = nx.betweenness_centrality_subset(
            graph_association,
            subconjunto_lemas,
            subconjunto_lemas,
            normalized=True,
            weight="weight"
        )
        encontrados = sorted(
            resultados_asoc.items(),
            key=itemgetter(1),
            reverse=True
        )[0:99]
        print(encontrados)
        print("Resultados usando grafo asociación")
        print(concepts(encontrados, subconjunto_lemas))


dictionary_nap("Animal conocido como el rey de la selva")
