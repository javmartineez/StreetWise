"""
test_grafo.py

Discrete Mathematics - IMAT
ICAI, Universidad Pontificia Comillas

Description:
Script for a basic check of the grafo_pesado.py library.

The "vertices" and "aristas" lists describe a graph (directed or undirected).
The script builds that graph with random edge weights
using the grafo.py library.

It then performs several basic operations on the graph and runs:
    - Dijkstra
    - Shortest path search with Dijkstra
    - Prim
    - Kruskal
"""
import networkx as nx
import grafo_pesado
import random

from typing import Union
MIN_PESO_ARISTA=1
MAX_PESO_ARISTA=12




############ Example weight functions ############

#Function returning a constant weight for every edge
def peso_constante(G:Union[nx.Graph, nx.DiGraph], origen:object, destino:object):
    return 1

#Function retrieving the random weight stored in the graph
def peso_aleatorio(G:Union[nx.Graph, nx.DiGraph], origen:object, destino:object):
    return G[origen][destino]["peso"]


#Lists of graph vertices and edges
dirigido=False
vertices=[1,2,3,'a',5,6]
aristas=[(1,2),(1,3),(1,'a'),(1,5),(2,'a'),(3,'a'),(3,5),(5,6)]

#Graph creation
if dirigido:
    G=nx.DiGraph()
else:
    G=nx.Graph()  

G.add_nodes_from(vertices)   

for a in aristas:
    #Store a random weight on each edge
    G.add_edge(a[0],a[1],peso=random.randrange(MIN_PESO_ARISTA,MAX_PESO_ARISTA))
    #Print the created edges to see the assigned weight
    print(a[0],a[1],":",G[a[0]][a[1]])


#Dijkstra and shortest path with constant weight
acm=grafo_pesado.dijkstra(G,peso_constante,1)
print(acm)

camino=grafo_pesado.camino_minimo(G,peso_constante,1,5)
print(camino)

#Dijkstra and shortest path with random weight
acm_rng=grafo_pesado.dijkstra(G,peso_aleatorio,1)
print(acm_rng)

camino_rng=grafo_pesado.camino_minimo(G,peso_aleatorio,1,5)
print(camino_rng)



if(not dirigido):
    #Minimum spanning tree
    aam=grafo_pesado.kruskal(G,peso_constante)
    print(aam)

    aam2=grafo_pesado.prim(G,peso_constante)
    print(aam2)


    aam_rng=grafo_pesado.kruskal(G,peso_aleatorio)
    print(aam_rng)

    aam2_rng=grafo_pesado.prim(G,peso_aleatorio)
    print(aam2_rng)