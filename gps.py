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
    Weight function based on the distance travelled.

    Args:
        -G: graph under study.
        -node1: source node of graph G.
        -node2: destination node of graph G.

    Return: weight of the edge (nodo1, nodo2)
    """
    return G[node1][node2]["length"]

def tiempo(G: Union[nx.Graph, nx.DiGraph], node1: object, node2: object):
    """
    Weight function based on driving time.

    Args:
        -G: graph under study.
        -node1: source node of graph G.
        -node2: destination node of graph G.

    Return: weight of the edge (nodo1, nodo2)
    """
    return G[node1][node2]["time"]

def tiempo_optimizado(G: Union[nx.Graph, nx.DiGraph], node1: object, node2: object):
    """
    Weight function based on driving time, accounting for traffic lights and signs
    with an 80% probability of stopping for 30 s.

    Args:
        -G: graph under study.
        -node1: source node of graph G.
        -node2: destination node of graph G.

    Return: weight of the edge (nodo1, nodo2)
    """
    return G[node1][node2]["time"] + 0.8*30


def usuario_nodo(tipo_nodo: str):
    """
    Asks the user for the node to search for.
    """
    palabra = input(f"Location of the {tipo_nodo}: ")
    if palabra == "":
        return
    return palabra


def calcular_camino(G: Union[nx.Graph, nx.DiGraph], origen: object, destino: object):
    """
    Computes the shortest path between two nodes in three different modes: minimum distance in metres,
    minimum time, or minimum time accounting for the probability of traffic lights or signs at
    the nodes.

    Args:
        -G: graph holding all the nodes/edges of the map.
        -origen: source node.
        -destino: destination node.

    Returns:
        Shortest path of nodes between origen and destino (according to the selected method).

    Raises: None
    """
    opciones = {
        "1": metros,
        "2": tiempo,
        "3": tiempo_optimizado
    }
    while True:
        ruta = input(""" Route calculation mode (1,2,3):
        1: Shortest route between the addresses: uses the total length.
        2. Fastest route between the addresses: uses the travel time.
        3. Fastest route accounting for traffic lights: uses the travel time.
        """)
        if ruta in opciones:
            return camino_minimo(G, opciones[ruta], origen, destino)
        else:
            print("Choose an existing route method.")

    

def sacar_direccion(v0: Tuple, v1: Tuple):
    """
    Computes the direction of the second vector with respect to the first one, using the properties of the
    cross product. If it is positive it is to the left, if it is negative to the right, and if it is
    zero they are parallel.

    Args:
        -v0: vector of the first edge.
        -v1: vector of the second edge.

    Returns:
        Direction of v1 with respect to v0.
    
    Raises: None.
    """
    x0, y0 = v0[0], v0[1]
    x1, y1 = v1[0], v1[1]

    z = x0*y1 - y0*x1
    if z > 0:
        return "left"
    elif z < 0:
        return "right"
    else:
        return "straight"
    
    
def sacar_vector(G: Union[nx.Graph, nx.DiGraph], u: object, v: object, final: bool = True):
    """
    Gets the direction vector of an edge of the graph under study.

    Args:
        -G: graph holding all the nodes/edges of the map.
        -u: start node of the edge.
        -v: end node of the edge.
        -final: whether to take the vector from the last or the first points.

    Returns:
        -vector: vector representing the direction of the edge at the intersection (it can be
        at the start or at the end of the edge).

    Raises: None 
    """
    #If the edge has no geometry, use the node coordinates
    if "geometry" not in G[u][v]:
        x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
    
    else:
        geometria = list(G[u][v]["geometry"].coords)

        if len(geometria) < 2:      #handle the case with fewer than two points so the code does not crash
            x0, y0, x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"], G.nodes[v]["x"], G.nodes[v]["y"] 
        else:
            if final:           #take the last two points if it is the first edge of the intersection
                x0, y0 = geometria[-2]
                x1, y1 = geometria[-1]
            else:               #take the first two points if it is the second edge of the intersection
                x0, y0 = geometria[0]
                x1, y1 = geometria[1]
        
    vector = (x1-x0, y1 -y0)
    return vector


def instruccion(instrucciones: list, name: str, direccion: str, dist: int = None):
    """
    Adds an instruction to the list of instructions.

    Args:
        -instrucciones: list with all the instructions.
        -name: street name.
        -direccion: type of turn between the streets.
        -dist: distance travelled during the instruction.

    Return: the instruction is appended to instrucciones

    Raises: None
    """
    if direccion == "straight":
        if name != "":
            instrucciones.append(f"Continue straight for {dist} metres on {name}")
        else:
            instrucciones.append(f"Continue straight for {dist} metres")
    else:
        if name != "":
            instrucciones.append(f"Turn {direccion} onto {name}")
        else:
            instrucciones.append(f"Turn {direccion}")


def lista_instrucciones(G: Union[nx.Graph, nx.DiGraph], camino: list[object]):
    """
    Generates the list of instructions from the graph and a path of nodes.

    Args:
        -G: graph holding all the nodes/edges of the map.
        -camino: list of nodes of the chosen route.

    Returns:
        instrucciones: list with all the instructions for the given path of nodes.
    
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

            if nombre1 == nombre2:      #If we stay on the same street
                length += dist1
            else:
                length += dist1
                instruccion(instrucciones, nombre1, "straight", length)

                v1 = sacar_vector(G, nodo11, nodo12, True)
                v2 = sacar_vector(G, nodo21, nodo22, False)
                direccion = sacar_direccion(v1,v2)
                            
                if direccion == "straight":
                    length = 0

                else:
                    instruccion(instrucciones, nombre2, direccion)
                    length = 0

        if nombre1 == nombre2:
            length += dist2
            instruccion(instrucciones, nombre1, "straight", length)
        else:
            instruccion(instrucciones, nombre2, "straight", dist2)
        instrucciones.append("You have arrived at your destination!")

    elif len(edges) == 1:
        nodo1 = edges[0][0]
        nodo2 = edges[0][1]
        nombre = G[nodo1][nodo2]["name"]
        dist = round(G[nodo1][nodo2]["length"], 0)

        instruccion(instrucciones, nombre, "straight", dist)
        instrucciones.append("You have arrived at your destination!")

    else:
        instrucciones.append("You are already at your destination!")

    return instrucciones


def mostrar_camino_sobre_grafo(G, camino):
    """
    Shows the graph map with the route given by the path of nodes.

    Args:
        -G: graph holding all the nodes/edges of the map.
        -camino: list of nodes of the chosen route.
    
    Returns: None

    Raises: None
    """
    # Extract the route coordinates
    xs = [G.nodes[n]["x"] for n in camino]
    ys = [G.nodes[n]["y"] for n in camino]
 
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 10))
 
    # Draw the base map (OSM) using contextily
    ax.set_xlim(min(xs)-0.01, max(xs)+0.01)
    ax.set_ylim(min(ys)-0.01, max(ys)+0.01)
    ctx.add_basemap(ax, crs="EPSG:4326", source=ctx.providers.OpenStreetMap.Mapnik)
 
    # Draw the route on top
    ax.plot(xs, ys, color="red", linewidth=3)
 
    # Mark start and end
    ax.scatter(xs[0], ys[0], c="green", s=50)
    ax.scatter(xs[-1], ys[-1], c="red", s=50)
 
    ax.set_axis_off()
    plt.show()


def main():
    """
    Main entry point: builds the DataFrame and the street graph, asks the
    user for the desired origin and destination, computes the shortest path between them and shows
    the map with the route.
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
            print("\n____NEW ROUTE____\n")
            inicio = usuario_nodo("origin")

            if inicio:
                lat1, lon1 = ca.busca_direccion(inicio, df)
            else: return

            final = usuario_nodo("destination")
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
        except (ca.AddressNotFoundError, ca.ServiceNotAvailableError, ValueError) as e:
            print(e)



if __name__ == "__main__":
    main()