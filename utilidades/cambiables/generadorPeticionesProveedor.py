import os
import random

from descuentos_optimizador.configuracion import Config

def generar_peticiones_proveedor(dia):
    agencias = [f"Agencia{str(i).zfill(3)}" for i in range(1, Config.NUM_AGENCIAS + 1)]

    ruta_bruto = os.path.dirname(Config.RUTA_VENTAS)
    ruta_ventas = Config.RUTA_VENTAS
    ruta_mejor_proveedor = Config.RUTA_MEJOR_PROVEEDOR
    ruta_peticiones_hotel = os.path.join(ruta_bruto, "peticionesHotel.txt")
    ruta_peticiones_proveedor = os.path.join(ruta_bruto, "peticionesProveedor.txt")
    ruta_peticiones_proveedor_multi = os.path.join(ruta_bruto, "peticionesProveedorMulti.txt")

    ventas_por_agencia = {}
    with open(ruta_ventas, "r") as f:
        for linea in f:
            partes = linea.strip().split(";")
            if len(partes) == 7:
                hotel, agencia, *_ , mayorista = partes
                hotel = int(hotel)
                if agencia not in ventas_por_agencia:
                    ventas_por_agencia[agencia] = {"hoteles": set(), "mayoristas": set()}
                ventas_por_agencia[agencia]["hoteles"].add(hotel)
                ventas_por_agencia[agencia]["mayoristas"].add(int(mayorista))

    peticiones_hotel = {}
    total_peticiones_por_hotel_agencia = {}
    with open(ruta_peticiones_hotel, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split(" ", 1)
            if len(partes) < 2:
                continue
            agencia = partes[0]
            hoteles_raw = partes[1].split(",")
            peticiones_hotel[agencia] = set()
            for par in hoteles_raw:
                par = par.strip()
                if not par:
                    continue
                try:
                    hotel_id, peticiones = par.split()
                    hotel_id = int(hotel_id)
                    peticiones_hotel[agencia].add(hotel_id)
                    total_peticiones_por_hotel_agencia[(agencia, hotel_id)] = int(peticiones)
                except ValueError:
                    print(f"Formato incorrecto en linea: {linea}")
                    continue

    mejor_proveedor_hotel = {}
    with open(ruta_mejor_proveedor, "r") as f:
        for linea in f:
            partes = linea.strip().split()
            if len(partes) >= 5:
                _, _, hotel_id, mejor, segundo = partes[:5]
                mejor_proveedor_hotel[int(hotel_id)] = (int(mejor), int(segundo))

    peticiones_proveedor = {}
    os.makedirs(os.path.dirname(ruta_peticiones_proveedor), exist_ok=True)
    with open(ruta_peticiones_proveedor, "w") as f:
        for agencia in agencias:
            mayoristas_usados = {}
            for hotel_id in peticiones_hotel.get(agencia, set()):
                total_pet = total_peticiones_por_hotel_agencia.get((agencia, hotel_id), 0)
                if total_pet == 0:
                    continue
                mejor, segundo = mejor_proveedor_hotel.get(hotel_id, (0, 0))
                if mejor != 0:
                    mayoristas_usados[mejor] = mayoristas_usados.get(mejor, 0) + total_pet
                if segundo != 0:
                    extra = max(1, int(total_pet * 0.25))
                    mayoristas_usados[segundo] = mayoristas_usados.get(segundo, 0) + extra

            for mayorista in ventas_por_agencia.get(agencia, {}).get("mayoristas", set()):
                if mayorista not in mayoristas_usados:
                    mayoristas_usados[mayorista] = random.randint(Config.MIN_PETICIONES, Config.MAX_PETICIONES)

            if mayoristas_usados:
                pares = [f"{mayorista} {pet}" for mayorista, pet in mayoristas_usados.items()]
                peticiones_proveedor[agencia] = mayoristas_usados
                f.write(f"{agencia} {', '.join(pares)}\n")

 
    with open(ruta_peticiones_proveedor_multi, "w") as f:
        for agencia, peticiones in peticiones_proveedor.items():
            total_pet = sum(peticiones.values())
            if total_pet < 5:
                continue
            max_multi = random.randint(int(total_pet * 0.4), int(total_pet * 0.6))
            total_asignado = 0
            pares = []
            proveedores = list(peticiones.items())
            random.shuffle(proveedores)
            for mayorista, pet in proveedores:
                if pet < 2:
                    continue
                max_este = min(pet // 2, max_multi - total_asignado)
                if max_este < 1:
                    continue
                pet_multi = random.randint(1, max_este)
                pares.append(f"{mayorista} {pet_multi}")
                total_asignado += pet_multi
                if total_asignado >= max_multi:
                    break
            if pares:
                f.write(f"{agencia} {', '.join(pares)}\n")

    print(f"Dia {dia}: peticionesProveedor.txt y peticionesProveedorMulti.txt generados correctamente")
