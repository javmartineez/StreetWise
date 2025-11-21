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
    while True:
        inicio = input("Ubicación actual: ")
        if inicio == "":
            return
        la1, lon1 = ca.busca_direccion(inicio, df)

        final = input("Ubicación del destino: ")
        if final == "":
            return
        la2, lon2 = ca.busca_direccion(final, df)

        ruta = input(""" Modo de cálculo de ruta(1,2,3):
        1: Ruta más corta entre las direcciones: Se considera la longitud total.
        2. Ruta más rápida entre las direcciones: Se considera el tiempo del viaje.
        3. Ruta más rápida optimizando semáforos: Se considera el tiempo del viaje.
            """)
        if ruta == 1:
            

    def metros():
        pass

    def tiempo():
        pass

    def tiempo_optimizado():
        pass

if __name__ == "__main__":
    main()