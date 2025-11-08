"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP09B
Integrantes:
    - Javier Mochales López
    - Javier Martínez Berenguer

Descripción:
XXXXXXXXXX

"""
import excepciones as e
import re
import pandas as pd

def limpieza_fichero() -> pd.DataFrame:
    df = pd.read_csv("direcciones.csv", sep= ";", encoding= "latin1")
    df = df[["VIA_CLASE","VIA_PAR","VIA_NOMBRE","NUMERO","LATITUD","LONGITUD"]]
    regex = r"(\d+)[°º]\s*(\d+)\'(\d+\.?\d*)\'\'\s*([NSEW])"
    aux = pd.DataFrame()
    cols_la = ["la_grados", "la_minutos", "la_segundos", "la_dir"]
    cols_lo = ["lo_grados", "lo_minutos", "lo_segundos", "lo_dir"]

    aux[cols_la] = df["LATITUD"].str.extract(regex)
    aux[cols_lo] = df["LONGITUD"].str.extract(regex)
    aux[cols_la[:-1] + cols_lo[:-1]] = aux[cols_la[:-1] + cols_lo[:-1]].astype("float")
    df["LATITUD"] = gmd_a_grados(aux[cols_la])
    df["LONGITUD"] = gmd_a_grados(aux[cols_lo])
    return df


def gmd_a_grados(data):
    grados, minutos, segundos, direccion = data.iloc[:,0], data.iloc[:,1], data.iloc[:,2], data.iloc[:,3]
    grados_dec = grados + minutos/60 + segundos/3600
    direccion = direccion.map({"N" : 1, "E" : 1, "S" : -1, "W" : -1})
    return grados_dec * direccion

def direccion_calle(calle: str, df: pd.DataFrame):
    regex = r"([A-Za-z]+)\s"
    nombre, numero = calle.split(sep = ",")
    nombre, numero  = nombre.strip(), numero.strip()
    resultado = df.loc[df["VIA_NOMBRE"] == calle, ["LATITUD","LONGITUD"]]

    if resultado.empty:
        raise e.StreetError("La calle solicitada no se encuentra en la base de datos")
    
    latitud, longitud = resultado.loc[0,"LATITUD"], resultado.loc[0,"LONGITUD"]
    return latitud, longitud
    



if __name__ == "__main__":
    df  = limpieza_fichero()
    lat, long = direccion_calle("Calle de Alberto Aguilera, 1", df)
    print(lat, long)