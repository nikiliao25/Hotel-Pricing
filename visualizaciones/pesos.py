import os
import sys
import gzip
import pickle
from descuentos_optimizador.configuracion import Config
DIRECTORIO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if DIRECTORIO_BASE not in sys.path:
    sys.path.append(DIRECTORIO_BASE)

def abrir_pesos_gz(dia):
    archivo = os.path.join(Config.RUTA_DESCUENTOS, f'pesos-{dia}.gz')

    with gzip.open(archivo, 'rb') as f:
        data = pickle.load(f)
    return data

pesos_dia = abrir_pesos_gz(3)
for k, v in list(pesos_dia.items())[:1]: 
    print(f"{k}: {v}")
