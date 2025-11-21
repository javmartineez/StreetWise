"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP09B
Integrantes:
    - Javier Mochales López
    - Javier Martínez Berenguer

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import re
import difflib
import os
import matplotlib.pyplot as plt
import numpy as np

from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': 20,
 'residential': 30,
 'primary_link': 40,
 'unclassified': 40,
 'secondary_link': 40,
 'trunk_link': 40,
 'secondary': 50,
 'tertiary': 50,
 'primary': 50,
 'trunk': 50,
 'tertiary_link':50,
 'busway': 50,
 'motorway_link': 70,
 'motorway': 100}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AddressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############


def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    callejero = pd.read_csv("direcciones.csv", sep= ";", encoding= "latin1")
    callejero = callejero[["VIA_CLASE","VIA_PAR","VIA_NOMBRE","NUMERO","LATITUD","LONGITUD"]]
    regex = re.compile(r"(\d+)[°º]\s*(\d+)\'(\d+\.?\d*)\'\'\s*([NSEW])")

    aux = pd.DataFrame()
    cols_la = ["la_grados", "la_minutos", "la_segundos", "la_dir"]
    cols_lo = ["lo_grados", "lo_minutos", "lo_segundos", "lo_dir"]

    aux[cols_la] = callejero["LATITUD"].str.extract(regex)
    aux[cols_lo] = callejero["LONGITUD"].str.extract(regex)
    aux[cols_la[:-1] + cols_lo[:-1]] = aux[cols_la[:-1] + cols_lo[:-1]].astype("float")
    callejero["LATITUD"] = gmd_a_grados(aux[cols_la])
    callejero["LONGITUD"] = gmd_a_grados(aux[cols_lo])

    #cols = ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE"]
    #callejero[cols] = callejero[cols].fillna("").apply(lambda col: col.map(normaliza_texto))
    for col in ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE"]:
        callejero[col] = callejero[col].fillna("").map(normaliza_texto)

    return callejero


def gmd_a_grados(data: pd.DataFrame) -> pd.Series:
    """
    Transforma los datos del DataFrame a grados decimales y añade signo dependiendo
    de la orinetación de la localización.
    Args:
        -data: DataFrame con la información de la localización.
    Returns:
        -Un Series con la posición transformada a grados decimales.
    """
    lista_divisores = pd.array([1,60,3600])
    valores = data.iloc[:,:-1]
    valores = valores / lista_divisores
    direccion = data.iloc[:,-1]
    direccion = direccion.map({"N" : 1, "E" : 1, "S" : -1, "W" : -1})
    return valores.sum(axis=1)*direccion



def normaliza_texto(cadena: str) -> str:
    """
    Función encargada de normalizar el texto a mayúsculas y sin tildes
    y/o elementos sintácticos adicionales. 

    Args: 
        - cadena(str): cadena a normalizar 
    Returns: 
        - cadena limpia normalizada
    """
    if cadena is None:
        return ""
    s = str(cadena).upper()
    reemplazos = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U",
        "À": "A", "È": "E", "Ì": "I", "Ò": "O", "Ù": "U",
        "Ñ": "N",
    }
    return "".join(reemplazos.get(c, c) for c in s)



def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    #1) DEFINIR EL FORMATO QUE VAMOS A ACEPTAR 
    CLASES = r"AUTOVIA|AUTOPISTA|AVENIDA|CALLE|CAMINO|CARRETERA|GLORIETA|PASAJE|PASEO|PLAZA|RONDA|TRAVESIA"
    PARES = r"DE LAS|DE LOS|DE LA|DEL|DE"
    regex_via = re.compile(rf"^\s*({CLASES})?\s*({PARES})?\s*(.+)\s*")

    #2) NORMALIZAR LA ENTRADA DEL USUARIO
    direccion_clean = normaliza_texto(direccion)

    #3) SEPARAR VÍA Y NÚMERO
    dir, num_raw = [p.strip() for p in direccion_clean.split(",", 1)]
    mnum = re.search(r"\d+", num_raw)
    if not mnum:
        raise AddressNotFoundError(f"Número inválido en: '{num_raw}' (se esperaba un entero)")
    numero = int(mnum.group())

    #4) CASAR PATRÓN
    m = regex_via.match(dir)
    if not m: 
        raise AddressNotFoundError(f"No se reconoce la estructura de la vía: '{dir}'")
    
    clase = m.group(1) or ""
    par = m.group(2) or ""
    via = m.group(3)
    
    #5) ENCONTRAR EN EL DF
    mask_exacta = (
        (callejero["VIA_CLASE"] == clase) &
        (callejero["VIA_PAR"] == par) &
        (callejero["VIA_NOMBRE"] == via) &
        (callejero["NUMERO"].astype("Int64") == numero)
        )
    
    candidatos = callejero.loc[mask_exacta, ["LATITUD","LONGITUD"]]

    #6) Si el match no es exacto -> aplicamos fuzzy 
    if len(candidatos) == 0: 
        mask_base = (
            (callejero["NUMERO"].astype("Int64") == numero)
        )
        sub = callejero.loc[mask_base].copy()

        if len(sub) == 0:
            raise AddressNotFoundError("Calle no encontrada ni siquiera de forma aproximada")

        # calculamos similitud para cada nombre distinto
        mejor_score = -1.0
        mejor_nombre = None
        for nombre_candidato in sub["VIA_NOMBRE"].unique():
            score = difflib.SequenceMatcher(None, via, nombre_candidato).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = nombre_candidato

        if mejor_score < 0.7:
            raise AddressNotFoundError("Calle no encontrada ni siquiera de forma aproximada")

        candidatos = sub.loc[sub["VIA_NOMBRE"] == mejor_nombre, ["LATITUD", "LONGITUD"]]

    # 7) DEVOLVER LA PRIMERA COINCIDENCIA
    lat, lon = float(candidatos.iloc[0]["LATITUD"]), float(candidatos.iloc[0]["LONGITUD"])
    return (lat, lon)



############## Parte 4 ##############


def arreglo_vias(serie):
    if isinstance(serie["highway"], list):
        a = -1
        b = "tipo"
        for i in serie["highway"]:
            val = MAX_SPEEDS[i]
            if val > a:
                a = val
                b = i
        serie["highway"] = b
        serie["maxspeed"] = a
    return serie 

def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    ruta_grafo = "madrid.graphml"
    existencia = os.path.exists(ruta_grafo)

    if not existencia:  #Cargamos el grafo de open street map si no se ha descargado previamente
        G = ox.graph_from_place("Madrid, Spain", network_type="drive")
        ox.save_graphml(G, filepath="madrid.graphml")
    
    G = ox.load_graphml(filepath="madrid.graphml")
    
    return G 

def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """

    G = ox.convert.to_digraph(multidigrafo, weight="length") #quita aristas repetidas pero no bucles 

    loops = list(nx.selfloop_edges(G)) #bucles
    G.remove_edges_from(loops)

    # df_grafo = nx.to_pandas_edgelist(G)
    # df_grafo = df_grafo.apply(func=arreglo_vias, axis=1)
    # #Hay que ver si podemos cambiar el diccionario MAX_SPEEDS para que sean numéricos y no tener que hacer tanta parafernalia
    # df_grafo["maxspeed"] = df_grafo["highway"].map(MAX_SPEEDS)
    # #df_grafo["maxspeed"] = df_grafo["maxspeed"].astype(np.int8)     NO se si merece la pena: cómo las velocidades no son superiores a 127 utilizamos int8 para ahorrar memoria
    # df_grafo["time"] = df_grafo["length"] / (df_grafo["maxspeed"] * 1_000)
    # G_rec = nx.from_pandas_edgelist(
    # df_grafo,
    # source="source",
    # target="target",
    # edge_attr=True,      # incluye todas las columnas restantes
    # create_using=nx.DiGraph()
    # )

    # return G_rec
    for u, v, data in G.edges(data=True):
        if isinstance(data["highway"], list):
            a = -1
            b = "tipo"
            for i in data["highway"]:
                val = MAX_SPEEDS[i]
                if val > a:
                    a = val
                    b = i
                data["highway"] = b
                data["maxspeed"] = a
        else:
            data["maxspeed"] = MAX_SPEEDS[data["highway"]]
        data["time"] = data["length"] / (data["maxspeed"] * 1_000)
    return G

if __name__ == "__main__":
    G = carga_grafo()
    Gd = procesa_grafo(G)


    




