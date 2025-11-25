from typing import List,Tuple,Dict,Callable,Union
import re
import os

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

import callejero as ca
from grafo_pesado import camino_minimo


def metros(G: Union[nx.Graph, nx.DiGraph], node1: object, node2: object):
    """
    Función de peso en base a la distancia recorrida.

    Args:
        -G: grafo que se estudia.
        -node1: Nodo origen del grafo G.
        -node2: Nodo destino del grafo G.

    Return: Peso de la arista (nodo1, nodo2)
    """
    return G[node1][node2]["length"]

def tiempo(G: Union[nx.Graph, nx.DiGraph], node1: object, node2: object):
    """
    Función de peso en base al tiempo circulando.

    Args:
        -G: grafo que se estudia.
        -node1: Nodo origen del grafo G.
        -node2: Nodo destino del grafo G.

    Return: Peso de la arista (nodo1, nodo2)
    """
    return G[node1][node2]["time"]

def tiempo_optimizado(G: Union[nx.Graph, nx.DiGraph], node1: object, node2: object):
    """
    Función de peso en base al tiempo circulando optimizando semáforos y señales
    con una probabilidad de pararse 30s del 80%.

    Args:
        -G: grafo que se estudia.
        -node1: Nodo origen del grafo G.
        -node2: Nodo destino del grafo G.

    Return: Peso de la arista (nodo1, nodo2)
    """
    return G[node1][node2]["time"] + 0.8*30

def usuario_nodo(tipo_nodo: str):
    """
    Pregunta al usuario que el nodo a buscar.
    """
    palabra = input(f"Ubicación del {tipo_nodo}: ")
    if palabra == "":
        return
    return palabra


def calcular_camino(G: Union[nx.Graph, nx.DiGraph], origen: object, destino: object):
    ruta = input(""" Modo de cálculo de ruta(1,2,3):
    1: Ruta más corta entre las direcciones: Se considera la longitud total.
    2. Ruta más rápida entre las direcciones: Se considera el tiempo del viaje.
    3. Ruta más rápida optimizando semáforos: Se considera el tiempo del viaje.
    """)
    if ruta == "1":
        return camino_minimo(G, metros, origen, destino)
    elif ruta == "2":
        return camino_minimo(G, tiempo, origen, destino)
    elif ruta == "3":
        return camino_minimo(G, tiempo_optimizado, origen, destino)
    else:
        print("Elige un método de ruta existente.")
        return

def sacar_vector(G, u, v):
    if not G[u][v]["geometry"]:
        x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
        vector = (x1-x0, y1 -y0)
    
    else:
        geometria = list(G[u][v]["geometry"].coords)




def lista_instrucciones(G: Union[nx.Graph, nx.DiGraph], camino: list[object]):
    edges = list(zip(camino[:-1], camino[1:]))


        

def mostrar_ruta_sobre_grafo():
    pass

def main():
    df = ca.carga_callejero()
    G = ca.carga_grafo()
    G = ca.procesa_grafo(G)
    while True:
        inicio = usuario_nodo("origen")
        if inicio:
            lat1, lon1 = ca.busca_direccion(inicio, df)
        else: return

        final = usuario_nodo("destino")
        if final:
            lat2, lon2 = ca.busca_direccion(final, df)
        else: return

        origen = ox.distance.nearest_nodes(G, X=lon1, Y=lat1)
        destino = ox.distance.nearest_nodes(G, X=lon2, Y=lat2)

        camino = calcular_camino(G, origen, destino)
        print(camino)
        #direcciones = lista_instrucciones(G, camino)

        #mostrar_ruta_sobre_grafo()


if __name__ == "__main__":
    main()