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

def sacar_vector(G, u, v, final=True):
    if "geometry" not in G[u][v]:
        x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
    
    else:
        geometria = list(G[u][v]["geometry"].coords)

        if len(geometria) < 2:
            x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
        else:
            if final:
                x0, y0 = geometria[-2]
                x1, y1 = geometria[-1]
            else:
                x0, y0 = geometria[0]
                x1, y1 = geometria[1]
        
    vector = (x1-x0, y1 -y0)
    return vector

def sacar_direccion(v0, v1):
    """
    Sabemos que en producto vectorial si haces u x v si v estaba a la izquierda de u el resultado queda positivo.
    Y si estaba a la derecha va a quedar negativo (se ve facil con la regla de la mano derecha).
    """
    x0, y0 = v0[0], v0[1]
    x1, y1 = v1[0], v1[1]
    z = x0*y1 - y0*x1

    if z > 0:
        return "izquierda"
    elif z < 0:
        return "derecha"
    else:
        return "recto"





def lista_instrucciones(G: Union[nx.Graph, nx.DiGraph], camino: list[object]):
    instrucciones = []
    edges = list(zip(camino[:-1], camino[1:]))
    if len(edges) > 1:
        length = 0
        for i in range(len(edges)-1):
            arista1 = edges[i]
            arista2 = edges[i+1]

            nodo11 = arista1[0]
            nodo12 = arista1[1]
            nodo21 = arista2[0]
            nodo22 = arista2[1]

            nombre1 = G[nodo11][nodo12]["name"]
            nombre2 = G[nodo21][nodo22]["name"]

            dist1 = round(G[nodo11][nodo12]["length"], 0)
            dist2 = round(G[nodo21][nodo22]["length"], 0)

            if nombre1 == nombre2:
                length += dist1
            else:
                length += dist1
                instruccion1 = instruccion(nombre1, "recto", length)
                instrucciones.append(instruccion1)

                v1 = sacar_vector(G, nodo11, nodo12, True)
                v2 = sacar_vector(G, nodo21, nodo22, False)
                direccion = sacar_direccion(v1,v2)
                
                
                if direccion == "recto":
                    length = dist2
                    instruccion2 = instruccion(nombre2, "recto", length)
                    instrucciones.append(instruccion2)
                    length = 0
                else:
                    instruccion2 = instruccion(nombre2, direccion)
                    instrucciones.append(instruccion2)
                    length = 0

        if nombre1 == nombre2:
            length += dist2
            instruccion1 = instruccion(nombre1, "recto", length)
            instrucciones.append(instruccion1)
        else:
            instruccion1 = instruccion(nombre2, "recto", dist2)
            instrucciones.append(instruccion1)
        instrucciones.append("Has llegado a tu destino!")
    elif len(edges) == 1:
        nodo1 = edges[0][0]
        nodo2 = edges[0][1]
        nombre = G[nodo1][nodo2]["name"]
        dist = round(G[nodo1][nodo2]["length"], 0)

        instruccion_f = instruccion(nombre, "recto", dist)
        instrucciones.append(instruccion_f)
        instrucciones.append("Has llegado a tu destino!")

    else:
        instrucciones.append("Estás ya en tu destino!")

    return instrucciones

        
def instruccion(name, direccion, dist=None):
    if direccion == "recto":
        return f"Sigue recto {dist} metros por {name}" if name != "" else f"Sigue recto {dist} metros"
    return f"Gira a la {direccion} por {name}" if name != "" else f"Gira a la {direccion}"

def mostrar_ruta_sobre_grafo(G, camino):
    plt.figure(figsize=(12, 12))

    # Dibujar grafo completo
    for u, v in G.edges():
        data = G[u][v]
        if "geometry" in data:
            xs, ys = data["geometry"].xy
        else:
            xs = [G.nodes[u]["x"], G.nodes[v]["x"]]
            ys = [G.nodes[u]["y"], G.nodes[v]["y"]]
        plt.plot(xs, ys, color="lightgray", linewidth=0.5)

    # Ruta
    for u, v in zip(camino[:-1], camino[1:]):
        data = G[u][v]
        if "geometry" in data:
            xs, ys = data["geometry"].xy
        else:
            xs = [G.nodes[u]["x"], G.nodes[v]["x"]]
            ys = [G.nodes[u]["y"], G.nodes[v]["y"]]
        plt.plot(xs, ys, color="red", linewidth=3)

    # marcar origen/destino
    xo, yo = G.nodes[camino[0]]["x"], G.nodes[camino[0]]["y"]
    xd, yd = G.nodes[camino[-1]]["x"], G.nodes[camino[-1]]["y"]
    plt.scatter([xo], [yo], color="green", s=50)
    plt.scatter([xd], [yd], color="blue", s=50)

    plt.axis("equal")
    plt.show()
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
        direcciones = lista_instrucciones(G, camino)
        for i in direcciones:
            print(i)

        mostrar_ruta_sobre_grafo(G, camino)


if __name__ == "__main__":
    main()