from typing import List,Tuple,Dict,Callable,Union
import os

import osmnx as ox
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx


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
    """
    Calcula el camino mínimo entre dos nodos en tres modos distintos. Por distancia mínima en metros,
    por tiempo mínimo o por tiempo mínimo optimizando la probabilidad de semáforos o señalización en
    los nodos.

    Args:
        -G: Grafo donde se encuentran todos los nodos/aristas del mapa.
        -origen: Nodo origen.
        -destino: Nodo destino.
    
    Returns:
        Camino de nodos mínimo entre origen y destino (en base al método seleccionado).

    Raises: None
    """
    opciones = {
        "1": metros,
        "2": tiempo,
        "3": tiempo_optimizado
    }
    while True:
        ruta = input(""" Modo de cálculo de ruta(1,2,3):
        1: Ruta más corta entre las direcciones: Se considera la longitud total.
        2. Ruta más rápida entre las direcciones: Se considera el tiempo del viaje.
        3. Ruta más rápida optimizando semáforos: Se considera el tiempo del viaje.
        """)
        if ruta in opciones:
            return camino_minimo(G, opciones[ruta], origen, destino)
        print("Elige un método de ruta existente.")

    

def sacar_direccion(v0: Tuple, v1: Tuple):
    """
    Calcula la dirección del segundo vector respecto al primero,, utilizando las propiedades del
    producto vectorial. Si da positivo esta a la izquierda, si es negativo a la derecha y en
    caso de ser nulo son paralelos.

    Args:
        -v0: vector de la primera arista.
        -v1: vector de la segunda arista.
    
    Returns:
        Dirección de v1 respecto de v0.
    
    Raises: None.
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
    
    
def sacar_vector(G: Union[nx.Graph, nx.DiGraph], u: object, v: object, final: bool = True):
    """
    Obtiene el vector dirección de una arista del Grafo a estudiar.

    Args:
        -G: Grafo donde se encuentran todos los nodos/aristas del mapa.
        -u: nodo del inicio de la arista.
        -v: nodo del final de la arista.
        -final: booleano para coger el vector de los últimos o primeros puntos.

    Returns:
        -vector: vector que representa la dirección de la arista en la intersección (puede ser
        del principio o del final de la arista).

    Raises: None 
    """
    #En caso de no tener la geometría de la arista utiliza los puntos de los nodos
    if "geometry" not in G[u][v]:
        x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
    
    else:
        geometria = list(G[u][v]["geometry"].coords)

        if len(geometria) < 2:      #comprobamos el caso en el que hay menos de dos puntos para que no explote el código
            x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
        else:
            if final:           #escogemos los dos últimos puntos si es la primera arista de la intersección
                x0, y0 = geometria[-2]
                x1, y1 = geometria[-1]
            else:               #escogemos los dos primeros puntos si es la segunda arista de la intersección
                x0, y0 = geometria[0]
                x1, y1 = geometria[1]
        
    vector = (x1-x0, y1 -y0)
    return vector


def instruccion(instrucciones: list, name: str, direccion: str, dist: int = None):
    """
    incluye una instrucción a la lista de instrucciones.

    Args:
        -instrucciones: lista con todas las instrucciones.
        -name: nombre de la calle.
        -direccion: tipo de intersección entre las calles.
        -dist: distancia recorrida durante la instrucción.
    
    Return: se incluye la instrucción a instrucciones

    Raises: None
    """
    if direccion == "recto":
        if name != "":
            instrucciones.append(f"Sigue recto {dist} metros por {name}")
        else:
            instrucciones.append(f"Sigue recto {dist} metros")
    else:
        if name != "":
            instrucciones.append(f"Gira a la {direccion} por {name}")
        else:
            instrucciones.append(f"Gira a la {direccion}")


def lista_instrucciones(G: Union[nx.Graph, nx.DiGraph], camino: list[object]):
    """
    Genera la lista de instrucciones a partir del Grafo y un camino de nodos.

    Args:
        -G: Grafo donde se encuentran todos los nodos/aristas del mapa.
        -camino: lista de nodos de la ruta establecida.
    
    Returns:
        instrucciones: lista con todas las instrucciones para el camino de nodos dado.
    
    Raises: None
    """
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

            if nombre1 == nombre2:      #Si seguimos
                length += dist1
            else:
                length += dist1
                instruccion(instrucciones, nombre1, "recto", length)

                v1 = sacar_vector(G, nodo11, nodo12, True)
                v2 = sacar_vector(G, nodo21, nodo22, False)
                direccion = sacar_direccion(v1,v2)
                            
                if direccion == "recto":
                    length = 0

                else:
                    instruccion(instrucciones, nombre2, direccion)
                    length = 0

        if nombre1 == nombre2:
            length += dist2
            instruccion(instrucciones, nombre1, "recto", length)
        else:
            instruccion(instrucciones, nombre2, "recto", dist2)
        instrucciones.append("Has llegado a tu destino!")

    elif len(edges) == 1:
        nodo1 = edges[0][0]
        nodo2 = edges[0][1]
        nombre = G[nodo1][nodo2]["name"]
        dist = round(G[nodo1][nodo2]["length"], 0)

        instruccion(instrucciones, nombre, "recto", dist)
        instrucciones.append("Has llegado a tu destino!")

    else:
        instrucciones.append("Estás ya en tu destino!")

    return instrucciones


def mostrar_camino_sobre_grafo(G, camino):
    """
    Muestra el mapa del grafo con la ruta establecida en el camino de nodos.

    Args:
        -G: Grafo donde se encuentran todos los nodos/aristas del mapa.
        -camino: lista de nodos de la ruta establecida.
    
    Returns: None

    Raises: None
    """
    # Extraer coordenadas de la ruta
    xs = [G.nodes[n]["x"] for n in camino]
    ys = [G.nodes[n]["y"] for n in camino]
 
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 10))
 
    # Dibujar mapa base (OSM) usando contextily
    ax.set_xlim(min(xs)-0.01, max(xs)+0.01)
    ax.set_ylim(min(ys)-0.01, max(ys)+0.01)
    ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)
 
    # Dibujar ruta encima
    ax.plot(xs, ys, color="red", linewidth=3)
 
    # Marcar inicio y final
    ax.scatter(xs[0], ys[0], c="green", s=50)
    ax.scatter(xs[-1], ys[-1], c="red", s=50)
 
    ax.set_axis_off()
    plt.show()


def main():
    """
    Función principal de ejecucion encargada de generar el DataFrame y el grafo de calles, preguntar al
    usuario el origen y destino deseado, calcular el camino mínimo entre estas y mostrar por pantalla el 
    mapa con la ruta.
    """
    try:
        df = ca.carga_callejero()
    except FileNotFoundError as e:
        print(e)
    try:
        G = ca.carga_grafo()
    except ca.ServiceNotAvailableError as e:
        print(e)
    G = ca.procesa_grafo(G)

    while True:
        try:
            print("\n____NUEVA RUTA____\n")
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

            mostrar_camino_sobre_grafo(G, camino)
        except (ca.AddressNotFoundError, ca.ServiceNotAvailableError) as e:
            print(e)



if __name__ == "__main__":
    main()