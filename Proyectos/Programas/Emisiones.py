# comprobar si las restricciones de tráfico establecidas 
# en Madrid Central han servido para reducir significativamente las emisiones de gases contaminantes.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

# Códigos de las magnitudes contaminantes medidas
magnitudes = {
    '01':'Dióxido de Azufre',
    '06':'Monóxido de Carbono',
    '07':'Monóxido de Nitrógeno',
    '08':'Dióxido de Nitrógeno',
    '09':'Partículas < 2.5 μm',
    '10':'Partículas < 10 μm',
    '12':'Óxidos de Nitrógeno',
    '14':'Ozono',
    '20':'Tolueno',
    '30':'Benceno',
    '35':'Etilbenceno',
    '37':'Metaxileno',
    '38':'Paraxileno',
    '39':'Ortoxileno',
    '42':'Hidrocarburos totales(hexano)',
    '43':'Metano',
    '44':'Hidrocarburosno metánicos (hexano)'
}

# Códigos de las estaciones de medición.
estaciones = {
    '001':'Pº. Recoletos',
    '002':'Glta. de Carlos V',
    '035':'Pza. del Carmen',
    '004':'Pza. de España',
    '039':'Barrio del Pilar',
    '006':'Pza. Dr. Marañón',
    '007':'Pza. M. de Salamanca',
    '008':'Escuelas Aguirre',
    '009':'Pza. Luca de Tena',
    '038':'Cuatro Caminos',
    '011':'Av. Ramón y Cajal',
    '012':'Pza. Manuel Becerra',
    '040':'Vallecas',
    '014':'Pza. Fdez. Ladreda',
    '015':'Pza. Castilla',
    '016':'Arturo Soria', 
    '017':'Villaverde Alto',
    '018':'Calle Farolillo',
    '019':'Huerta Castañeda',
    '036':'Moratalaz',
    '021':'Pza. Cristo Rey',
    '022':'Pº. Pontones',
    '023':'Final C/ Alcalá',
    '024':'Casa de Campo',
    '025':'Santa Eugenia',
    '026':'Urb. Embajada (Barajas)',
    '027':'Barajas',
    '047':'Méndez Álvaro',
    '048':'Pº. Castellana',
    '049':'Retiro',
    '050':'Pza. Castilla',
    '054':'Ensanche Vallecas',
    '055':'Urb. Embajada (Barajas)',
    '056':'Plaza Elíptica',
    '057':'Sanchinarro',
    '058':'El Pardo',
    '059':'Parque Juan Carlos I',
    '060':'Tres Olivos'
}

# Carga de datos
from urllib.error import HTTPError

try:
    df = pd.read_csv('http://aprendeconalf.es/python/trabajos/datos/emisiones-madrid.csv')
except HTTPError:
    print('La url no existe')
else:
    # Preprocesamiento de datos
    # Pasar los días de columnas a una nueva variable DIA
    df = df.melt(id_vars=['ESTACION', 'MAGNITUD', 'ANO', 'MES'], var_name='DIA', value_name='VALOR')
    # Eliminar la D del valor de los días
    df['DIA'] = df['DIA'].apply(lambda x: x[1:])
    # Convertir las columnas DIA, MES, ANO, ESTACION y MAGNITUD en cadenas
    df['ESTACION'] = df['ESTACION'].astype(str)
    df['MAGNITUD'] = df['MAGNITUD'].astype(str)
    df['MES'] = df['MES'].astype(str)
    df['ANO'] = df['ANO'].astype(str)
    # Añadir 00 a la estación cuando la estación solo tiene un dígito y 0 cuando tiene dos
    df['ESTACION'] = df['ESTACION'].apply(
        lambda x: '00' + x if len(x) < 2 else '0' + x)
    # Añadir 0 a la magnitud cuando solo tiene un dígito
    df['MAGNITUD'] = df['MAGNITUD'].apply(lambda x: '0' + x if len(x) < 2 else x)
    # Añadir 0 al mes cuando el mes solo tiene un dígito
    df['MES'] = df['MES'].apply(lambda x: '0' + x if len(x) < 2 else x)
    # Crear una nueva columna concatenando las columnas DIA, MES y AÑO en formato dd/mm/aaaa
    df['FECHA'] = df['DIA'] + '/' + df['MES'] + '/' + df['ANO']
    # Convertir la columna fecha al tipo datetime
    df['FECHA'] = pd.to_datetime(df['FECHA'], format='%d/%m/%Y', errors='coerce')
    # Eliminar las filas con fechas no válidas
    df = df.drop(df[np.isnat(df['FECHA'])].index)
    # Ordenar el dataframe por fechas, magnitudes y estaciones
    df = df.sort_values(['FECHA', 'MAGNITUD', 'ESTACION'])

    print(df)