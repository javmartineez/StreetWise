import osmnx as ox
import networkx as nx
import pandas as pd
import re
import difflib
import os
import matplotlib.pyplot as plt
import callejero as ca

def main():
    df = ca.carga_callejero()
    # G = ca.carga_grafo()
    # G = ca.procesa_grafo(G)
    inicio = input("Ubicación actual: ")
    print(ca.busca_direccion(inicio, df))

if __name__ == "__main__":
    main()