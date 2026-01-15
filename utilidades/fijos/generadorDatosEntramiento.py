import pandas as pd
import numpy as np
import random
import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from descuentos_optimizador.configuracion import Config


num_hoteles = Config.NUM_HOTELES
num_datos = 100000
num_dias = 365
np.random.seed(42)
random.seed(42)


info_hoteles_path = os.path.join(Config.RUTA_DISTANCIA_HOTELES)
os.makedirs(os.path.dirname(info_hoteles_path), exist_ok=True)
with open(info_hoteles_path, "w") as f:
    for hotel_id in range(1, num_hoteles + 1):
        if random.random() < 0.9:
            distancia = round(np.random.normal(loc=3, scale=1.2), 2)
        else:
            distancia = round(np.random.uniform(10, 30), 2)
        distancia = max(0, distancia)  
        es_centrico = 1 if distancia <= 4 else 0
        f.write(f"{hotel_id},{distancia},{es_centrico}\n")


info_hoteles = {}
with open(info_hoteles_path, "r") as f:
    for line in f:
        hotel_id, distancia, es_centrico = line.strip().split(",")
        info_hoteles[int(hotel_id)] = {
            "distancia": float(distancia),
            "es_centrico": int(es_centrico)
        }


reserva_meses = [0.4, 0.45, 0.6, 0.85, 1, 0.9, 0.7, 0.6, 0.5, 0.45, 0.4, 0.5]

datos = []
for _ in range(num_datos):
    hotel_id = random.randint(1, num_hoteles)
    dia = random.randint(1, num_dias)
    mes = ((dia - 1) // 30) % 12
    impulso_calendario = reserva_meses[mes]

    distancia = info_hoteles[hotel_id]["distancia"]
    es_centrico = info_hoteles[hotel_id]["es_centrico"]

    penalizacion = max(0, min(1, distancia / 30)) 
    atractivo_base = 10 * (1 - penalizacion)
    ruido = np.random.normal(0, 1)

    target = atractivo_base * impulso_calendario + ruido
    target = max(0, min(10, round(target, 2)))

    datos.append({
        "hotel_id": hotel_id,
        "dia_del_ano": dia,
        "distancia": distancia,
        "es_centrico": es_centrico,
        "mes": mes + 1,
        "target": target
    })

df = pd.DataFrame(datos)
csv_path = os.path.join(Config.RUTA_DATOS_HOTELES)
df.to_csv(csv_path, index=False)