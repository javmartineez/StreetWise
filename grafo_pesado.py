"""
grafo.py

Discrete Mathematics - IMAT
ICAI, Universidad Pontificia Comillas

Group: GP09B
Members:
    - Javier Martínez Berenguer
    - Javier Mochales López

Description:
Library for the analysis of weighted graphs.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq #Library for creating priority queues

INFTY=sys.float_info.max #"Infinite" distance between nodes of a graph

"""
In the following functions, weight functions are functions that receive a graph or digraph and two vertices and return a real number (their weight)
For example, if the graph edges store a field called 'valor' in their data, a possible weight function would be:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

and, in that case, to run Dijkstra with that parameter we would do

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Computes a Shortest-Path Tree for the weighted graph starting
    from the vertex "origen" using Dijkstra's algorithm. It only computes
    the tree of the connected component containing "origen".

    Args:
        origen (object): source vertex of the graph
    Returns:
        Dict[object,object]: dictionary that indicates, for each vertex reachable
            from "origen", which vertex is its parent in the shortest-path tree.
    Raises:
        TypeError: If origen is not "hashable".
    Example:
        If G.dijksra(1)={2:1, 3:2, 4:1} then 1 is the parent of 2 and 4, and 2 is the parent of 3.
        In particular, a shortest path from 1 to 3 would be 1->2->3.
    """
    # Check that the source is hashable
    try:
        hash(origen)
    except TypeError:
        raise TypeError(f"The source is not hashable: {type(origen).__name__}")
    
    padres = {}
    d = {}
    visitados = set()
    contador = 0 #tie-breaker for heappop
    

    for v in G.nodes():
        padres[v] = None
        d[v] = INFTY
    
    d[origen] = 0
    
    Q = []
    heapq.heappush(Q, (0, contador, origen)) 
    contador += 1
    
    while Q:
        dist_v, _, v = heapq.heappop(Q)
        
        if v in visitados:
            continue
        
        visitados.add(v)
        
        for x in G.neighbors(v):
            if x not in visitados:
                nueva_dist = d[v] + peso(G, v, x)
                
                if nueva_dist < d[x]:
                    d[x] = nueva_dist
                    padres[x] = v
                    heapq.heappush(Q, (d[x], contador, x))
                    contador += 1
    
    return padres

def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Computes the shortest path from the vertex origen to the vertex
    destino using Dijkstra's algorithm.

    Args:
        G (nx.Graph or nx.Digraph): graph or directed graph
        peso (function): function that receives a graph or directed graph and two of its vertices and returns the weight of the edge connecting them
        origen (object): source vertex of the graph
        destino (object): destination vertex of the graph
    Returns:
        List[object]: list with the graph vertices the shortest path between
            the source and the destination goes through. The first element of
            the list is origen and the last one is destino.
    Example:
        If dijksra(G,peso,1,4)=[1,5,2,4] then the shortest path in G between 1 and 4 is 1->5->2->4.
    Raises:
        TypeError: If origen or destino are not "hashable".
    """
    # Check that source and destination are hashable
    try:
        hash(origen)
    except TypeError:
        raise TypeError(f"The source is not hashable: {type(origen).__name__}")

    try:
        hash(destino)
    except TypeError:
        raise TypeError(f"The destination is not hashable: {type(destino).__name__}")


    # Compute the shortest-path tree
    padres = dijkstra(G, peso, origen)
    
    camino = []
    actual = destino
    
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]         #walk the path backwards (from the destination to the source)
    

    camino.reverse()
    return camino
 
def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Computes a Minimum Spanning Tree for the weighted graph
    using Prim's algorithm.

    Args:
        G (nx.Graph): graph
        peso (function): function that receives a graph and two of its vertices and returns the weight of the edge connecting them
    Returns:
        Dict[object,object]: dictionary that indicates, for each vertex of the
            graph, which vertex is its parent in the minimum spanning tree.
    Raises: None
    Example:
        If prim(G,peso)={1: None, 2:1, 3:2, 4:1} then in a minimum spanning tree:
            1 is a root (it has no parent)
            1 is the parent of 2 and 4
            2 is the parent of 3

    """
    padres = {}
    coste_min = {}
    visitados = set()  
    contador = 0 
    Q = []
    root = list(G.nodes())[0]
    
  
    for v in G.nodes():
        padres[v] = None
        coste_min[v] = INFTY
    
    coste_min[root] = 0
    heapq.heappush(Q, (0, contador, root))
    contador += 1
    
    while Q:
        coste_v, _, v = heapq.heappop(Q)
        
        if v in visitados:
            continue
        
        visitados.add(v)
        
        for x in G.neighbors(v):
            if x not in visitados:
                w_vx = peso(G, v, x)
                
                if w_vx < coste_min[x]:
                    coste_min[x] = w_vx
                    padres[x] = v
                    heapq.heappush(Q, (w_vx, contador, x))
                    contador += 1
    
    return padres


            

def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Computes a Minimum Spanning Tree for the graph
    using Kruskal's algorithm.

    Args:
        G (nx.Graph): graph
        peso (function): function that receives a graph and two of its vertices and returns the weight of the edge connecting them
    Returns:
        List[Tuple[object,object]]: list [(s1,t1),(s2,t2),...,(sn,tn)]
            of the pairs of graph vertices forming the edges
            of the minimum spanning tree.
    Raises: None
    Example:
        In the previous example where prim(G,peso)={1:None, 2:1, 3:2, 4:1} we could have, for instance,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    
    aristas = sorted(G.edges(), key=lambda e: peso(G, e[0], e[1]), reverse=True)
    
    C = {}
    aristas_aam = []
    
    for v in G.nodes():
        C[v] = {v}
    

    while aristas:
        arista = aristas.pop()
        u, v = arista[0], arista[1]
        
        if C[u] != C[v]:
            aristas_aam.append((u, v)) 
            
            componente_unida = C[u] | C[v]
            for w in componente_unida:
                C[w] = componente_unida
    
    return aristas_aam
