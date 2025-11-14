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

from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


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

    for col in ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE"]:
        callejero[col + "_N"] = callejero[col].fillna("").map(normaliza_texto)

    return callejero


def gmd_a_grados(data) -> pd.Series:
    grados, minutos, segundos, direccion = data.iloc[:,0], data.iloc[:,1], data.iloc[:,2], data.iloc[:,3]
    grados_dec = grados + minutos/60 + segundos/3600
    direccion = direccion.map({"N" : 1, "E" : 1, "S" : -1, "W" : -1})
    return grados_dec * direccion


def normaliza_texto(cadena: str) -> str:
    """Mayúsculas, sin tildes ni eñes raras."""
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
    regex_via = re.compile(rf"^\s*({CLASES})\s+({PARES})?\s+(.+)\s*$")

    #2) NORMALIZAR LA ENTRADA DEL USUARIO
    direccion_clean = normaliza_texto(direccion)

    #3) SEPARAR VÍA Y NÚMERO
    dir, num_raw = [p.strip() for p in direccion_clean.split(",", 1)]
    mnum = re.search(r"\d+", num_raw)
    if not mnum:
        raise ValueError(f"Número inválido en: '{num_raw}' (se esperaba un entero)")
    numero = int(mnum.group())

    #4) CASAR PATRÓN
    m = regex_via.match(dir)
    if not m: 
        raise ValueError(f"No se reconoce la estructura de la vía: '{dir}'")
    
    clase = m.group(1)
    par = (m.group(2) or '').strip() or None
    via = m.group(3)
    
    #5) ENCONTRAR EN EL DF
    par_cmp = par or ""  # en el CSV, ausencia de partícula suele ir como cadena vacía
    mask_exacta = (
        (callejero["VIA_CLASE"]  == clase) &
        (callejero["VIA_PAR"].fillna("") == par_cmp) &
        (callejero["VIA_NOMBRE"] == via) &
        (callejero["NUMERO"].astype("Int64") == numero)
        )
    
    candidatos = callejero.loc[mask_exacta, ["LATITUD","LONGITUD"]]

    #6) Si el match no es exacto -> aplicamos fuzzy 
    if len(candidatos) == 0: 
        mask_base = (
            (callejero["VIA_CLASE"] == clase) &
            (callejero["VIA_PAR"]   == par) &
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


def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    pass


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

    return G

