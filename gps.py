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

# def direccion_calle(calle: str, df: pd.DataFrame):
#     regex = r"([A-Za-z]+)\s"
#     nombre, numero = calle.split(sep = ",")
#     nombre, numero  = nombre.strip(), numero.strip()
#     resultado = df.loc[df["VIA_NOMBRE"] == calle, ["LATITUD","LONGITUD"]]

#     if resultado.empty:
#         raise e.AdressNotFoundError("La calle solicitada no se encuentra en la base de datos")
    
#     latitud, longitud = resultado.loc[0,"LATITUD"], resultado.loc[0,"LONGITUD"]
#     return latitud, longitud

    
def direccion_a_coordenadas(direccion:str, df:pd.DataFrame) -> tuple:
    #1) DEFINIR EL FORMATO QUE VAMOS A ACEPTAR 
    CLASES = r"AUTOVIA|AVENIDA|CALLE|CAMINO|CARRETERA|GLORIETA|PASAJE|PASEO|PLAZA|RONDA|TRAVESIA"
    PARES = r"DE LAS|DE LOS|DE LA|DEL|DE"
    regex_via = re.compile(rf"^\s*({CLASES})\s+({PARES})?\s+(.+)\s*$")

    #2) NORMALIZAR LA ENTRADA DEL USUARIO
    #pasar todo a mayusculas
    direccion = direccion.upper()
    #quitar tildes
    replacements = {"Á":"A", "É":"E", "Ó":"O", "Ú":"U"}
    direccion_clean = ''.join([replacements.get(caracter, caracter) for caracter in direccion])

    #3) SEPARAR VIA Y NUMERO
    dir, num_raw = [p.strip() for p in direccion_clean.split(",", 1)]
    mnum = re.search(r"\d+", num_raw)
    if not mnum:
        raise ValueError(f"Número inválido en: '{num_raw}' (se esperaba un entero)")
    numero = int(mnum.group())

    #4) CASAR PATRON
    m = regex_via.match(dir)
    if not m: 
        raise ValueError(f"No se reconoce la estructura de la vía: '{dir}'")
    
    clase = m.group(1)
    par = (m.group(2) or '').strip() or None
    via = m.group(3)
    
    #5) ENCONTRAR EN EL DF
    par_cmp = par or ""  # en el CSV, ausencia de partícula suele ir como cadena vacía
    mask = (
        (df["VIA_CLASE"]  == clase) &
        (df["VIA_PAR"].fillna("") == par_cmp) &
        (df["VIA_NOMBRE"] == via) &
        (df["NUMERO"].astype("Int64") == numero)
        )
    
    candidatos = df.loc[mask, ["LATITUD","LONGITUD"]]

    #6) GESTION DE ERRORES
    if len(candidatos) == 0: 
        raise e.AddressNotFoundError("Calle no encontrada en la base de datos")

    lat, lon = float(candidatos.iloc[0]["LATITUD"]), float(candidatos.iloc[0]["LONGITUD"])
    return (lat, lon)



if __name__ == "__main__":
    df  = limpieza_fichero()
    print(df.isna().any())
    # lat, lon = direccion_a_coordenadas("Calle de Alberto Aguilera, 1", df)
    # print(lat, lon)