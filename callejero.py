"""
callejero.py

Discrete Mathematics - IMAT
ICAI, Universidad Pontificia Comillas

Group: GP09B
Members:
    - Javier Mochales López
    - Javier Martínez Berenguer

Description:
Library with the tools and helper classes needed to represent a street map as a graph:
loading and normalising the Madrid address directory, geocoding addresses (with fuzzy
matching) and downloading/cleaning the OpenStreetMap street graph with travel times.
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
    "Exception indicating that navigation is not available at the moment"
    pass


class AddressNotFoundError(Exception):
    "Exception indicating that a searched address does not exist in the database"
    pass



############## Part 2 ##############

def gmd_a_grados(data: pd.DataFrame) -> pd.Series:
    """
    Converts the DataFrame data to decimal degrees and adds the sign depending
    on the orientation of the location.
    Args:
        -data: DataFrame with the location information.
    Returns:
        -A Series with the position converted to decimal degrees.
    """
    lista_divisores = pd.array([1,60,3600])
    valores = data.iloc[:,:-1]
    valores = valores / lista_divisores
    direccion = data.iloc[:,-1]
    direccion = direccion.map({"N" : 1, "E" : 1, "S" : -1, "W" : -1})
    return valores.sum(axis=1)*direccion


def normaliza_texto(cadena: str) -> str:
    """
    Normalises the text to upper case, without accents
    and/or additional syntactic elements.

    Args:
        - cadena(str): string to normalise
    Returns:
        - clean normalised string
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


def carga_callejero() -> pd.DataFrame:
    """ Loads the Madrid street directory, processes it and returns
    a DataFrame with the processed data

    Args: None
    Returns:
        pd.DataFrame: processed street directory, with coordinates in decimal degrees
            and normalised street names.
    Raises:
        FileNotFoundError if the csv file with the addresses does not exist
    """
    if not os.path.exists("direcciones.csv"):
        raise FileNotFoundError("The file direcciones.csv does not exist")
    
    callejero = pd.read_csv("direcciones.csv", sep= ";", encoding= "latin1", usecols=["VIA_CLASE","VIA_PAR","VIA_NOMBRE","NUMERO","LATITUD","LONGITUD"])

    regex = re.compile(r"(\d+)[°º]\s*(\d+)\'(\d+\.?\d*)\'\'\s*([NSEW])")

    aux = pd.DataFrame()            #create an auxiliary dataframe to convert the longitude and latitude coordinates
    cols_la = ["la_grados", "la_minutos", "la_segundos", "la_dir"]
    cols_lo = ["lo_grados", "lo_minutos", "lo_segundos", "lo_dir"]

    aux[cols_la] = callejero["LATITUD"].str.extract(regex)      #extract each part of the coordinates with a regex
    aux[cols_lo] = callejero["LONGITUD"].str.extract(regex)

    aux[cols_la[:-1] + cols_lo[:-1]] = aux[cols_la[:-1] + cols_lo[:-1]].astype("float")     #convert every column except the direction to float
    callejero["LATITUD"] = gmd_a_grados(aux[cols_la])
    callejero["LONGITUD"] = gmd_a_grados(aux[cols_lo])


    for col in ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE"]:
        callejero[col] = callejero[col].fillna("").map(normaliza_texto)

    return callejero


def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Searches for an address, given in the format
        street, number
    in the Madrid street DataFrame and returns the (latitude, longitude) pair in degrees of the
    geographic location of that address

    Args:
        direccion (str): full street name with number, in the format "Street, num"
        callejero (DataFrame): DataFrame with the street information
    Returns:
        Tuple[float,float]: (latitude, longitude) float pair of the searched address, in degrees
    Raises:
        ValueError: If the address format does not contain a comma or a number
        AdressNotFoundError: If the address does not exist in the database
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    #1) DEFINE THE FORMAT WE ACCEPT 
    CLASES = r"AUTOVIA|AUTOPISTA|AVENIDA|CALLE|CAMINO|CARRETERA|GLORIETA|PASAJE|PASEO|PLAZA|RONDA|TRAVESIA"
    PARES = r"DE LAS|DE LOS|DE LA|DEL|DE"
    regex_via = re.compile(rf"^\s*({CLASES})?\s*({PARES})?\s*(.+)\s*")

    #2) NORMALISE THE USER INPUT
    direccion_clean = normaliza_texto(direccion)

    #3) SPLIT STREET AND NUMBER
    # Check that the comma is present
    if "," not in direccion_clean:
        raise ValueError("The address format must be 'street, number'. The separating comma is missing.")
    
    partes = direccion_clean.split(",", 1)
    if len(partes) < 2 or not partes[1].strip():
        raise ValueError("The address format must be 'street, number'. The street number is missing.")
    
    dir, num_raw = [p.strip() for p in partes]
    
    mnum = re.search(r"\d+", num_raw)
    if not mnum:
        raise AddressNotFoundError(f"Invalid number in: '{num_raw}' (an integer was expected)")
    numero = int(mnum.group())

    #4) MATCH THE PATTERN
    m = regex_via.match(dir)
    if not m:
        raise AddressNotFoundError(f"Unrecognised street structure: '{dir}'")
    
    clase = m.group(1) or ""
    par = m.group(2) or ""
    via = m.group(3)
    
    #5) FIND IT IN THE DF
    mask_exacta = (
        (callejero["VIA_CLASE"] == clase) &
        (callejero["VIA_PAR"] == par) &
        (callejero["VIA_NOMBRE"] == via) &
        (callejero["NUMERO"].astype("Int64") == numero)
        )
    
    candidatos = callejero.loc[mask_exacta, ["LATITUD","LONGITUD"]]

    #6) If there is no exact match -> apply fuzzy matching 
    if len(candidatos) == 0: 
        mask_base = (
            (callejero["NUMERO"].astype("Int64") == numero)
        )
        sub = callejero.loc[mask_base].copy()

        if len(sub) == 0:
            raise AddressNotFoundError("Address not found")

        # compute the similarity for each distinct name
        mejor_score = -1.0
        mejor_nombre = None
        for nombre_candidato in sub["VIA_NOMBRE"].unique():
            score = difflib.SequenceMatcher(None, via, nombre_candidato).ratio()
            if score > mejor_score:
                mejor_score = score
                mejor_nombre = nombre_candidato

        if mejor_score < 0.7:
            raise AddressNotFoundError("Address not found")

        candidatos = sub.loc[sub["VIA_NOMBRE"] == mejor_nombre, ["LATITUD", "LONGITUD"]]

    # 7) RETURN THE FIRST MATCH
    lat, lon = float(candidatos.iloc[0]["LATITUD"]), float(candidatos.iloc[0]["LONGITUD"])
    return (lat, lon)



############## Part 4 ##############

def comprobar_existencia(clave: str, data: dict):
    return clave in data

def carga_grafo() -> nx.MultiDiGraph:
    """ Retrieves the Madrid street quiver from OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: quiver of the Madrid streets.
    Raises:
        ServiceNotAvailableError: If the graph cannot be retrieved from OpenStreetMap.
    """
    ruta_grafo = "madrid.graphml"
    existencia = os.path.exists(ruta_grafo)

    if not existencia:  #Download the OpenStreetMap graph if it has not been downloaded before
        try:
            G = ox.graph_from_place("Madrid, Spain", network_type="drive")
        except Exception:
            raise ServiceNotAvailableError("The graph could not be retrieved from OpenStreetMap")
        ox.save_graphml(G, filepath="madrid.graphml")
    
    G = ox.load_graphml(filepath="madrid.graphml")
    
    return G 
    

def comprobar_lista(clave: str, posicion: int, data: dict):
    """
    Checks whether the value of the "data" dictionary under key "clave" is a list.
    If so, replaces it with the value at position "posicion" of the list. If the list is
    shorter than that position, it takes the last one.

    Args:
        -clave: dictionary key.
        -posicion: index of the list value we want.
        -data: dictionary with all the information.
    
    Returns: None

    Raises: None
    """
    if isinstance(data[clave], list):
        if len(data[clave]) <= posicion:
            data[clave] = data[clave][-1]
        else:
            data[clave] = data[clave][posicion]
    


def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Turns the Madrid street multidigraph into a simple directed graph with travel times.
    Args:
        multidigrafo: multidigraph of the Madrid streets obtained from OpenStreetMap.
    Returns:
        nx.DiGraph: loop-free directed graph associated with the given multidigraph.
    Raises: None
    """

    G = ox.convert.to_digraph(multidigrafo, weight="length") #removes repeated edges but not loops 

    loops = list(nx.selfloop_edges(G)) #loops
    G.remove_edges_from(loops)

    for _, _, data in G.edges(data=True):       #iterate over every edge of the graph
        if isinstance(data["highway"], list):
            a = -1
            b = "tipo"
            indice = 0
            for i in range(len(data["highway"])):
                val = MAX_SPEEDS[data["highway"][i]]
                if val > a:                                 #keep the road type with the highest speed limit
                    indice = i
                    a = val
                    b = data["highway"][i]

            data["highway"] = b

            if comprobar_existencia("name", data):
                comprobar_lista("name", indice, data)
        
        if  not comprobar_existencia("name", data):
            data["name"] = ""

        elif isinstance(data["name"], list):
            data["name"] = data["name"][0]
        

        if not comprobar_existencia("maxspeed", data):
            data["maxspeed"] = MAX_SPEEDS[data["highway"]]
            
        elif isinstance(data["maxspeed"], list):
            data["maxspeed"] = max(data["maxspeed"])
        
        try:
            data["maxspeed"] = int(data["maxspeed"])
        except (ValueError, TypeError):
            data["maxspeed"] = MAX_SPEEDS[data["highway"]]


        data["time"] = data["length"] / (data["maxspeed"] * 1_000)      #create a new key with the edge travel time
    
    return G
    




