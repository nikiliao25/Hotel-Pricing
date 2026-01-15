import os
import gzip
import pickle
import random
from descuentos_optimizador.configuracion import Config


def generar_peticiones_hotel_por_dia(dia):
    agencias = [f"Agencia{str(i).zfill(3)}" for i in range(1, Config.NUM_AGENCIAS + 1)]

    ruta_bruto_cambiables = os.path.dirname(Config.RUTA_VENTAS)
    ruta_ventas = Config.RUTA_VENTAS
    ruta_descuentos = Config.RUTA_DESCUENTOS
    ruta_salida = os.path.join(ruta_bruto_cambiables, "peticionesHotel.txt")

    os.makedirs(ruta_bruto_cambiables, exist_ok=True)

    usar_descuentos = True
    descuentos_ayer = {}
    descuentos_hoy = {}

    if dia - 3 == 0:
        usar_descuentos = False
        print(f"Aviso: Dia {dia}: No se usa descuentos porque pesos-0.gz no debería existir.")
    
        with gzip.open(os.path.join(ruta_descuentos, f"pesos-{dia - 2}.gz"), "rb") as f:
            descuentos_ayer = pickle.load(f)
        with gzip.open(os.path.join(ruta_descuentos, f"pesos-{dia - 1}.gz"), "rb") as f:
            descuentos_hoy = pickle.load(f)


    ventas_por_agencia = {}
    with open(ruta_ventas, "r") as f:
        for linea in f:
            partes = linea.strip().split(";")
            if len(partes) == 7:
                hotel_id, agencia, *_ = partes
                hotel_id = int(hotel_id)
                ventas_por_agencia.setdefault(agencia, set()).add(hotel_id)

 
    peticiones_hotel = {}
    with open(ruta_salida, "w") as f:
        for agencia in agencias:
            hoteles_agencia = descuentos_hoy.get(agencia, {}) if usar_descuentos else {}
            hoteles_venta = ventas_por_agencia.get(agencia, set())
            pares = []
            ya_peticionados = set()

            for hotel_id in hoteles_venta:
                pet = random.randint(Config.MIN_PETICIONES, Config.MAX_PETICIONES)
                pares.append(f"{hotel_id} {pet}")
                ya_peticionados.add(hotel_id)
                peticiones_hotel.setdefault(agencia, set()).add(hotel_id)

            if usar_descuentos:
                for hotel_id_str in hoteles_agencia:
                    hotel_id = int(hotel_id_str)
                    if hotel_id in ya_peticionados:
                        continue
                    dto_hoy = descuentos_hoy[agencia].get(hotel_id_str, 0)
                    dto_ayer = descuentos_ayer.get(agencia, {}).get(hotel_id_str, 0)
                    dif = dto_hoy - dto_ayer
                    prob = min(0.05 + dif * 0.1, 1.0) if dif > 0 else 0.05
                    if random.random() < prob:
                        pet = random.randint(Config.MIN_PETICIONES, Config.MAX_PETICIONES)
                        pares.append(f"{hotel_id} {pet}")
                        peticiones_hotel.setdefault(agencia, set()).add(hotel_id)

            if pares:
                f.write(f"{agencia} {', '.join(pares)}\n")

    print(f"Dia {dia}: peticionesHotel.txt generado correctamente")
