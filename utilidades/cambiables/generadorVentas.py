import os
import gzip
import pickle
import random

from descuentos_optimizador.configuracion import Config

def cargar_pickle_gz(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontro: {path}")
    with gzip.open(path, 'rb') as f:
        return pickle.load(f)

def cargar_precios_netos(path):
    precios = {}
    with open(path, "r") as f:
        for line in f:
            partes = line.strip().split(" ", 1)
            if len(partes) != 2:
                continue
            hotel_id, resto = partes
            hotel_id = int(hotel_id)
            pares = [x.strip() for x in resto.split(",") if x.strip()]
            precios[hotel_id] = {}
            for par in pares:
                try:
                    mayorista, precio = par.split()
                    precios[hotel_id][int(mayorista)] = float(precio)
                except ValueError:
                    continue
    return precios

ruta = Config.RUTA_ANALISIS_COMISIONES
comisiones_agencia_hotel = {}
comisiones_por_hotel = {}

if os.path.exists(ruta):
    with open(ruta, 'r') as f:
        for linea in f:
            partes = linea.strip().split("|")
            if len(partes) < 6:
                continue
            agencia_id = partes[0]
            hotel_id = partes[2]
            try:
                comision = float(partes[5])
            except ValueError:
                continue

            clave = (agencia_id, hotel_id)
            comisiones_agencia_hotel[clave] = comision
            comisiones_por_hotel.setdefault(hotel_id, []).append(comision)

def obtener_comision_agencia_estimada(agencia, hotel):
    clave = (agencia, hotel)
    comision = comisiones_agencia_hotel.get(clave)
    if comision is not None:
        return comision
    lista = comisiones_por_hotel.get(hotel, [])
    return sum(lista) / len(lista) if lista else 0.0

info_hoteles = {}
with open(Config.RUTA_DISTANCIA_HOTELES, 'r') as f:
    for line in f:
        hotel_id, distancia, _ = line.strip().split(",")
        info_hoteles[int(hotel_id)] = float(distancia)

reserva_meses = [0.4, 0.45, 0.6, 0.85, 1, 0.9, 0.7, 0.6, 0.5, 0.45, 0.4, 0.5]

def probabilidad_venta(peso_hoy, peso_ayer, comision_agencia, peticiones_ayer=None, peticiones_hoy=None, dia_actual=1, distancia=None):
    probabilidad = 0.0 

    diferencia = comision_agencia - peso_hoy
    if diferencia > 5:
        probabilidad += 0.2
    elif diferencia > 2:
        probabilidad += 0.1
    elif diferencia > 0:
        probabilidad += 0.05

    if peso_ayer > peso_hoy:
        probabilidad += 0.05
    elif peso_ayer < peso_hoy:
        probabilidad -= 0.05

    if peticiones_ayer is not None and peticiones_hoy is not None:
        if peticiones_hoy > peticiones_ayer:
            probabilidad += 0.03
        elif peticiones_hoy < peticiones_ayer:
            probabilidad -= 0.02

    mes = ((dia_actual - 1) // 30) % 12
    mes_factor = reserva_meses[mes]
    ajuste_mes = (mes_factor - 0.5) * 0.1 
    probabilidad += ajuste_mes

    return max(0.01, min(1.0, probabilidad))

def generar_ventas_por_dia(dia):
    agencias = [f"Agencia{str(i).zfill(3)}" for i in range(1, Config.NUM_AGENCIAS + 1)]

    descuentos_hoy = cargar_pickle_gz(os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{dia - 1}.gz"))
    descuentos_ayer_path = os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{dia - 2}.gz")
    descuentos_ayer = cargar_pickle_gz(descuentos_ayer_path) if os.path.exists(descuentos_ayer_path) else {}

    precios_por_hotel = cargar_precios_netos(Config.RUTA_PRECIOS_PROVEEDOR)

    beneficio_ayer_data = {}
    beneficio_hoy_data = {}
    if dia >= 4:
        rendimiento_ayer = cargar_pickle_gz(os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{dia - 2}.gz")).get(dia - 2, {})
        rendimiento_hoy = cargar_pickle_gz(os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{dia - 1}.gz")).get(dia - 1, {})
        beneficio_ayer_data = rendimiento_ayer.get("peticiones_cliente_hotel", {})
        beneficio_hoy_data = rendimiento_hoy.get("peticiones_cliente_hotel", {})

    total_ventas_objetivo = random.randint(2500, 6000)
    ventas_realizadas = 0
    beneficio_total = 0.0
    intentos = 0
    max_intentos = total_ventas_objetivo * 10

    output_path = Config.RUTA_VENTAS
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        while ventas_realizadas < total_ventas_objetivo and intentos < max_intentos:
            intentos += 1
            agencia = random.choice(agencias)
            hotel = random.choice(list(precios_por_hotel.keys()))
            mayoristas_disponibles = list(precios_por_hotel[hotel].keys())
            if not mayoristas_disponibles:
                continue
            mayorista = random.choice(mayoristas_disponibles)
            neto = precios_por_hotel[hotel][mayorista]

            try:
                dto_hoy = descuentos_hoy[agencia][hotel]
            except KeyError:
                continue

            dto_ayer = descuentos_ayer.get(agencia, {}).get(hotel, dto_hoy)
            comision_media = obtener_comision_agencia_estimada(agencia, str(hotel))

            peticiones_ayer = peticiones_hoy = None
            if dia >= 4:
                peticiones_ayer = beneficio_ayer_data.get(agencia, {}).get(hotel, {}).get("P")
                peticiones_hoy = beneficio_hoy_data.get(agencia, {}).get(hotel, {}).get("P")

            distancia = info_hoteles.get(hotel, 10.0)

            prob = probabilidad_venta(
                dia_actual=dia,
                peso_hoy=dto_hoy,
                peso_ayer=dto_ayer,
                comision_agencia=comision_media,
                peticiones_ayer=peticiones_ayer,
                peticiones_hoy=peticiones_hoy,
                distancia=distancia
            )

            if random.random() > prob:
                continue

            precio = round(neto * (1 + dto_hoy / 100), 2)
            beneficio = round(precio - neto, 2)

            f.write(f"{hotel};{agencia};{int(agencia.replace('Agencia', ''))};{precio:.2f};{neto:.2f};{beneficio:.2f};{mayorista}\n")
            ventas_realizadas += 1
            beneficio_total += beneficio

    
    print(f"Dia {dia}: hotelesCredencialesmayorista.txt generado con {ventas_realizadas} ventas correctamente")
    
