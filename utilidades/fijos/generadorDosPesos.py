import os
import gzip
import pickle
import random
from descuentos_optimizador.configuracion import Config


def generar_descuentos(indice_dia, probabilidad_aplicar=0.5):
    descuentos = {}
    for agencia_id in range(1, Config.NUM_AGENCIAS + 1):
        if random.random() < 0.8: 
            agencia = f"Agencia{str(agencia_id).zfill(3)}"
            descuentos[agencia] = {}
            for hotel_id in range(1, Config.NUM_HOTELES + 1):
                if random.random() < probabilidad_aplicar:
                    if random.random() < 0.8:
                        base = random.betavariate(2.5, 1.5)  
                        descuento = base * (Config.DESCUENTO_MAX - 0)  
                    else:
                        base = random.betavariate(2, 3) 
                        descuento = -base * abs(Config.DESCUENTO_MIN) \

                    descuento = max(min(descuento, Config.DESCUENTO_MAX), Config.DESCUENTO_MIN)
                    descuento = round(descuento, 2)
                    descuentos[agencia][hotel_id] = descuento

    ruta = os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{indice_dia}.gz")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with gzip.open(ruta, 'wb') as f:
        pickle.dump(descuentos, f)
    print(f"pesos-{indice_dia}.gz con descuentos aleatorios generado correctamente")

def generar_dos_descuentos_base():
    generar_descuentos(1)
    generar_descuentos(2)
