"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP09B
Integrantes:
    - Javier Mochales López
    - Javier Martínez Berenguer

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq #Librería para la creación de colas de prioridad
import excepciones as e

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """
    
    padres = {}
    d = {}
    visitados = set()
    contador = 0 #para caso de empate a la hora de hacer heappop
    

    for v in G.nodes():
        padres[v] = None
        d[v] = float('inf')
    
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
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """

    # Calculamos el árbol de caminos mínimos
    padres = dijkstra(G, peso, origen)
    
    camino = []
    actual = destino
    
    while actual is not None:
        camino.append(actual)
        actual = padres[actual]         #recorremos el camino en orden inverso (del destino al orgien)
    
    
    camino.reverse()
    return camino
 
def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3

    """
    padres = {}
    coste_min = {}
    visitados = set()  
    contador = 0 
    Q = []
    root = list(G.nodes())[0]
    
  
    for v in G.nodes():
        padres[v] = None
        coste_min[v] = float('inf')
    
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
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.

    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
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



if __name__ == "__main__":
    import callejero as ca
    G = ca.carga_grafo()
    aristas = kruskal(G, 1)
    print(aristas[0])