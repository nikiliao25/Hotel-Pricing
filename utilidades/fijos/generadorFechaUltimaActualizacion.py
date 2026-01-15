import pickle
import gzip
import os
import random
from descuentos_optimizador.configuracion import Config


def generar_fecha_ultima_actualizacion():
    dia_inicial = 1
    ruta_salida = Config.RUTA_FECHA_ACTUALIZACION

    fecha_ultima_actualizacion = {}
    for agencia_id in range(1, Config.NUM_AGENCIAS + 1):
        if random.random() > 0.7:  
            continue
        agencia = f"Agencia{str(agencia_id).zfill(3)}"
        fecha_ultima_actualizacion[agencia] = {}
        for hotel_id in range(1, Config.NUM_HOTELES + 1):
            if random.random() > 0.3: 
                continue
            fecha_ultima_actualizacion[agencia][hotel_id] = dia_inicial

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    with gzip.open(ruta_salida, 'wb') as f:
        pickle.dump(fecha_ultima_actualizacion, f)

    print(f"fecha_ultima_actualizacion.gz generado correctamente en: {ruta_salida}")