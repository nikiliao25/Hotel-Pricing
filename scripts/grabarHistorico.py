import os
import gzip
import pickle
from collections import OrderedDict
from descuentos_optimizador.configuracion import Config


def grabar_historico(dia):
    ruta_peticiones_hotel = Config.RUTA_PETICIONES_HOTEL
    ruta_ventas = Config.RUTA_VENTAS
    ruta_peticiones_proveedor = Config.RUTA_PETICIONES_PROVEEDOR
    ruta_peticiones_proveedor_multi = Config.RUTA_PETICIONES_PROVEEDOR_MULTI
    ruta_rendimiento = os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{dia}.gz")

    peticiones_cliente_hotel = {}
    total_peticiones_cliente = {}
    total_peticiones = 0
    peticiones_total_hotel_cliente = {}

    with open(ruta_peticiones_hotel, 'r') as f:
        for numero_linea, linea in enumerate(f, 1):
            if not linea.strip():
                continue
            partes = linea.strip().split()
            agencia = partes[0]
            pares = " ".join(partes[1:]).split(',')

            if agencia not in peticiones_cliente_hotel:
                peticiones_cliente_hotel[agencia] = {}
            if agencia not in total_peticiones_cliente:
                total_peticiones_cliente[agencia] = 0

            for par in pares:
                par = par.strip()
                if not par:
                    continue
                try:
                    hotel_id_str, peticiones = par.split()
                    hotel_id = int(hotel_id_str)
                    peticiones = int(peticiones)

                    if hotel_id not in peticiones_cliente_hotel[agencia]:
                        peticiones_cliente_hotel[agencia][hotel_id] = {'P': 0}
                    peticiones_cliente_hotel[agencia][hotel_id]['P'] += peticiones
                    total_peticiones_cliente[agencia] += peticiones
                    total_peticiones += peticiones
                except ValueError as error_valor:
                    print(f"Linea {numero_linea} — Error: {error_valor} — Linea original: '{linea.strip()}'")

    for agencia in peticiones_cliente_hotel:
        peticiones_cliente_hotel[agencia] = OrderedDict(
            sorted(peticiones_cliente_hotel[agencia].items(), key=lambda item: item[1]['P'], reverse=True)
        )

    total_peticiones_cliente = OrderedDict(
        sorted(total_peticiones_cliente.items(), key=lambda item: item[1], reverse=True)
    )

    """
    print("Resultados de peticionesHotel.txt:")
    print("\npeticiones_cliente_hotel")
    for agencia, hoteles in peticiones_cliente_hotel.items():
        print(f"{agencia}:")
        for hotel, datos in hoteles.items():
            print(f"  Hotel {hotel}: {datos['P']} peticiones")

    print("\ntotal_peticiones_cliente")
    for agencia, total in total_peticiones_cliente.items():
        print(f"{agencia}: {total} peticiones")

    print(f"\ntotal_peticiones\nTotal general de peticiones: {total_peticiones}")
    """

    beneficio = {}
    beneficio_cliente_total = {}
    beneficio_cliente_proveedor = {}
    beneficio_proveedor = {}
    proveedor_reservas = {}
    cliente_proveedor_reservas = {}
    cliente_hotel_reservas = {}
    beneficio_global = 0.0
    reservas_vendidas = 0

    with open(ruta_ventas, "r") as file:
        for linea in file:
            campos = linea.strip().split(";")
            if len(campos) != 7:
                continue

            id_hotel, agencia, id_agencia, precio, neto, beneficio_valor, id_mayorista = campos
            id_hotel = int(id_hotel)
            id_agencia = int(id_agencia)
            beneficio_valor = float(beneficio_valor)

            peticiones_real = peticiones_cliente_hotel.get(agencia, {}).get(id_hotel, {}).get("P", 0)
            if peticiones_real == 0:
                print(f"Venta ignorada (sin peticiones) → Agencia: {agencia}, Hotel: {id_hotel}")
                continue

            beneficio.setdefault(agencia, {}).setdefault(id_hotel, {'B': 0.0, 'C': 0, 'P': 0, 'BP': 0.0})
            beneficio[agencia][id_hotel]['B'] += beneficio_valor
            beneficio[agencia][id_hotel]['C'] += 1

            beneficio_cliente_total.setdefault(agencia, {'B': 0.0, 'C': 0, 'P': 0, 'BP': 0.0})
            beneficio_cliente_total[agencia]['B'] += beneficio_valor
            beneficio_cliente_total[agencia]['C'] += 1

            beneficio_cliente_proveedor.setdefault(agencia, {})
            beneficio_cliente_proveedor[agencia].setdefault(id_mayorista, 0.0)
            beneficio_cliente_proveedor[agencia][id_mayorista] += beneficio_valor

            beneficio_proveedor.setdefault(id_mayorista, 0.0)
            beneficio_proveedor[id_mayorista] += beneficio_valor

            proveedor_reservas.setdefault(id_mayorista, 0)
            proveedor_reservas[id_mayorista] += 1

            cliente_proveedor_reservas.setdefault(agencia, {})
            cliente_proveedor_reservas[agencia].setdefault(id_mayorista, 0)
            cliente_proveedor_reservas[agencia][id_mayorista] += 1

            cliente_hotel_reservas.setdefault(agencia, {})
            cliente_hotel_reservas[agencia].setdefault(id_hotel, 0)
            cliente_hotel_reservas[agencia][id_hotel] += 1

            beneficio_global += beneficio_valor
            reservas_vendidas += 1


    for agencia in beneficio:
        for hotel in list(beneficio[agencia].keys()):
            hotel_id = int(hotel) if isinstance(hotel, str) and hotel.isdigit() else hotel
            if hotel_id != hotel:
                beneficio[agencia][hotel_id] = beneficio[agencia].pop(hotel)

            peticiones_reales = peticiones_cliente_hotel.get(agencia, {}).get(hotel_id, {}).get('P', 0)
            beneficio[agencia][hotel_id]['P'] = peticiones_reales
            if peticiones_reales > 0:
                beneficio[agencia][hotel_id]['BP'] = beneficio[agencia][hotel_id]['B'] / peticiones_reales

    for agencia in beneficio_cliente_total:
        peticiones_real_total = total_peticiones_cliente.get(agencia, 0)
        beneficio_cliente_total[agencia]['P'] = peticiones_real_total
        if peticiones_real_total > 0:
            beneficio_cliente_total[agencia]['BP'] = beneficio_cliente_total[agencia]['B'] / peticiones_real_total

    """
    print("\nbeneficio_cliente_hotel")
    for agencia in beneficio:
        print(f"Agencia: {agencia}")
        for hotel in sorted(beneficio[agencia].keys(), key=lambda x: int(x)):
            b = beneficio[agencia][hotel]
            print(f"  Hotel {hotel} → B: {b['B']:.2f}, C: {b['C']}, P: {b['P']}, BP: {b['BP']:.2f}")

    print("\nbeneficio_total_cliente")
    for agencia in beneficio_cliente_total:
        b = beneficio_cliente_total[agencia]
        print(f"Agencia: {agencia} → B: {b['B']:.2f}, R: {b['C']}, P: {b['P']}, BP: {b['BP']:.2f}")


    print("\nbeneficio_proveedor")
    for mayorista in beneficio_proveedor:
        print(f"Mayorista: {mayorista} → Beneficio total: {beneficio_proveedor[mayorista]:.2f}")

    print("\nbeneficio_agencia_proveedor")
    for agencia in beneficio_cliente_proveedor:
        for mayorista in beneficio_cliente_proveedor[agencia]:
            b = beneficio_cliente_proveedor[agencia][mayorista]
            print(f"{agencia} - Mayorista {mayorista} → Beneficio total: {b:.2f}")

    print("\nreservas_proveedor")
    for mayorista in proveedor_reservas:
        print(f"Mayorista {mayorista} → Total reservas: {proveedor_reservas[mayorista]}")

    print("\nreservas_cliente_proveedor")
    for agencia in cliente_proveedor_reservas:
        for mayorista in cliente_proveedor_reservas[agencia]:
            r = cliente_proveedor_reservas[agencia][mayorista]
            print(f"{agencia} - Mayorista {mayorista} → Reservas: {r}")

    print("\nreservas_cliente_hotel")
    for agencia in cliente_hotel_reservas:
        for hotel in sorted(cliente_hotel_reservas[agencia], key=lambda x: int(x)):
            r = cliente_hotel_reservas[agencia][hotel]
            print(f"{agencia} - Hotel {hotel} → Reservas: {r}")

    print(f"\nbeneficio_total\nTotal beneficio global: {beneficio_global:.2f}")
    """

    print(f"Dia {dia}: total reservas vendidas: {reservas_vendidas}")
    
    peticiones_cliente_proveedor = {}
    total_peticiones_proveedor = {}
    total_peticiones_cliente_proveedor = {}

    with open(ruta_peticiones_proveedor, 'r') as f:
        for numero_linea, linea in enumerate(f, 1):
            if not linea.strip():
                continue
            partes = linea.strip().split()
            agencia = partes[0]
            pares = " ".join(partes[1:]).split(',')

            peticiones_cliente_proveedor.setdefault(agencia, {})
            total_peticiones_cliente_proveedor.setdefault(agencia, 0)

            for par in pares:
                par = par.strip()
                if not par:
                    continue
                try:
                    mayorista_id_normal, peticiones = par.split()
                    mayorista_id = int(mayorista_id_normal)
                    peticiones = int(peticiones)

                    peticiones_cliente_proveedor[agencia].setdefault(mayorista_id, {'P': 0})
                    peticiones_cliente_proveedor[agencia][mayorista_id]['P'] += peticiones

                    total_peticiones_proveedor.setdefault(mayorista_id, {'P': 0, 'B': 0.0, 'R': 0, 'BP': 0.0})
                    total_peticiones_proveedor[mayorista_id]['P'] += peticiones

                    beneficio_valor = beneficio_proveedor.get(mayorista_id, 0.0)
                    reservas_val = proveedor_reservas.get(mayorista_id, 0)
                    total_peticiones_proveedor[mayorista_id]['B'] = beneficio_valor
                    total_peticiones_proveedor[mayorista_id]['R'] = reservas_val
                    total_peticiones_proveedor[mayorista_id]['BP'] = beneficio_valor / total_peticiones_proveedor[mayorista_id]['P'] if total_peticiones_proveedor[mayorista_id]['P'] > 0 else 0.0

                    total_peticiones_cliente_proveedor[agencia] += peticiones
                    total_peticiones += peticiones
                except ValueError as error_valor:
                    print(f"Línea {numero_linea} — Error: {error_valor} — Línea original: '{linea.strip()}'")

    beneficio_global_por_peticion = beneficio_global / total_peticiones if total_peticiones > 0 else 0.0

    """
    print("\npeticiones_cliente_proveedor")
    for agencia in peticiones_cliente_proveedor:
        print(f"\nAgencia: {agencia}")
        for mayorista, datos in peticiones_cliente_proveedor[agencia].items():
            p = datos.get("P", 0)
            print(f"  Mayorista {mayorista} → P: {p}")
   
    print("\ntotal_peticiones_proveedor (no ordenado)")
    for mayorista in total_peticiones_proveedor:
        print(f"Mayorista {mayorista} → P: {total_peticiones_proveedor[mayorista]['P']}, B: {total_peticiones_proveedor[mayorista]['B']:.2f}, R: {total_peticiones_proveedor[mayorista]['R']}, BP: {total_peticiones_proveedor[mayorista]['BP']:.2f}")

    print("\ntotal_peticiones_cliente_proveedor")
    for agencia in total_peticiones_cliente_proveedor:
        print(f"{agencia} → Total peticiones a mayoristas: {total_peticiones_cliente_proveedor[agencia]}")

    print(f"\ntotal_peticiones\n{total_peticiones}")
    """

    print(f"Dia {dia}: beneficio_global antes de la división: {beneficio_global:.2f}")
    print(f"Dia {dia}: total_peticiones antes de la división: {total_peticiones}")
    print(f"Dia {dia}: beneficio medio por petición: {beneficio_global_por_peticion:.6f}")


    total_peticiones_cliente_proveedor_multi = {}

    with open(ruta_peticiones_proveedor_multi, 'r') as f:
        for numero_linea, linea in enumerate(f, 1):
            if not linea.strip():
                continue
            partes = linea.strip().split()
            agencia = partes[0]
            pares = " ".join(partes[1:]).split(',')

            if agencia not in peticiones_cliente_proveedor:
                peticiones_cliente_proveedor[agencia] = {}
            if agencia not in total_peticiones_cliente_proveedor_multi:
                total_peticiones_cliente_proveedor_multi[agencia] = 0

            for par in pares:
                par = par.strip()
                if not par:
                    continue
                try:
                    mayorista_id_str, peticiones = par.split()
                    mayorista_id = int(mayorista_id_str)
                    peticiones = int(peticiones)

                    if mayorista_id not in peticiones_cliente_proveedor[agencia]:
                        peticiones_cliente_proveedor[agencia][mayorista_id] = {"P": 0, "M": 0, "B": 0.0, "BP": 0.0, "R": 0}
                    else:
                        if "M" not in peticiones_cliente_proveedor[agencia][mayorista_id]:
                            peticiones_cliente_proveedor[agencia][mayorista_id]["M"] = 0

                    peticiones_cliente_proveedor[agencia][mayorista_id]["M"] += peticiones
                    total_peticiones_cliente_proveedor_multi[agencia] += peticiones

                    reservas = cliente_proveedor_reservas.get(agencia, {}).get(mayorista_id, 0)
                    beneficio_valor = beneficio_cliente_proveedor.get(agencia, {}).get(mayorista_id, 0.0)

                    if reservas:
                        peticiones_cliente_proveedor[agencia][mayorista_id]['R'] = reservas
                        peticiones_cliente_proveedor[agencia][mayorista_id]['B'] = beneficio_valor
                    else:
                        peticiones_cliente_proveedor[agencia][mayorista_id]['R'] = 0
                        peticiones_cliente_proveedor[agencia][mayorista_id]['B'] = 0.0

                    p = peticiones_cliente_proveedor[agencia][mayorista_id].get("P", 0)
                    if p > 0:
                        peticiones_cliente_proveedor[agencia][mayorista_id]['BP'] = peticiones_cliente_proveedor[agencia][mayorista_id]['B'] / p
                    else:
                        peticiones_cliente_proveedor[agencia][mayorista_id]['BP'] = 0.0

                except ValueError as error_valor:
                    print(f"Linea {numero_linea} — Error: {error_valor} — Linea original: '{linea.strip()}'")


    for agencia in peticiones_cliente_hotel:
        for hotel_id_str in peticiones_cliente_hotel[agencia]:
            hotel_id = int(hotel_id_str)
            peticiones = peticiones_cliente_hotel[agencia][hotel_id_str]['P']
            reservas = beneficio.get(agencia, {}).get(hotel_id, {}).get('C', 0)
            beneficio_valor = beneficio.get(agencia, {}).get(hotel_id, {}).get('B', None)

            if hotel_id not in peticiones_total_hotel_cliente:
                peticiones_total_hotel_cliente[hotel_id] = {'P': 0, 'C': 0, 'B': 0.0}

            peticiones_total_hotel_cliente[hotel_id]['P'] += peticiones

            if reservas and beneficio_valor is not None:
                peticiones_total_hotel_cliente[hotel_id]['C'] += reservas
                peticiones_total_hotel_cliente[hotel_id]['B'] += beneficio_valor
            else:
                bp_agencia = beneficio_cliente_total.get(agencia, {}).get('BP')
                bp_global = beneficio_global / total_peticiones if total_peticiones else 0.0
                bp = bp_global if not bp_agencia or bp_agencia == 0.0 else bp_agencia
                peticiones_total_hotel_cliente[hotel_id]['B'] += -bp * peticiones

    peticiones_total_hotel_cliente = OrderedDict(
        sorted(peticiones_total_hotel_cliente.items(), key=lambda x: x[1]['P'], reverse=True)
    )

    total_peticiones_proveedor = OrderedDict(
        sorted(total_peticiones_proveedor.items(), key=lambda item: item[1]['BP'], reverse=True)
    )

    """
    print("\nDetalle de peticiones_cliente_proveedor\n")
    for agencia, proveedores in peticiones_cliente_proveedor.items():
        print(f"Agencia: {agencia}")
        for mayorista, datos in proveedores.items():
            print(f"  Mayorista: {mayorista} | P: {datos.get('P', 0)} | M: {datos.get('M', 0)} | R: {datos.get('R', 0)} | B: {datos.get('B', 0.0):.2f} | BP: {datos.get('BP', 0.0):.4f}")
        print()


    
    print("\n Total por hotel (peticiones, reservas, beneficio) ordenado por peticion")
    for hotel_id, datos in peticiones_total_hotel_cliente.items():
        print(f"Hotel {hotel_id} → P: {datos['P']}, C: {datos['C']}, B: {datos['B']:.2f}")
    """

    peso_peticiones = {}
    for mayorista_id in total_peticiones_proveedor:
        mayorista_id_int = int(mayorista_id)
        total_p = total_peticiones_proveedor[mayorista_id]['P']
        peso_peticiones[mayorista_id_int] = total_p / total_peticiones if total_peticiones else 0.0

    clientes_proveedor_categoria = {}

    for agencia in peticiones_cliente_proveedor:
        clientes_proveedor_categoria.setdefault(agencia, {'B': [], 'M': [], 'N': []})
        totalCliente = 0
        for mayorista_id in peticiones_cliente_proveedor[agencia]:
            mayorista_id_int = int(mayorista_id)
            datos = peticiones_cliente_proveedor[agencia][mayorista_id]
            totalCliente += datos.get('P', 0)

        if totalCliente == 0:
            continue

        for mayorista_id in peticiones_cliente_proveedor[agencia]:
            mayorista_id_int = int(mayorista_id)
            datos = peticiones_cliente_proveedor[agencia][mayorista_id]
            peticiones_proveedor_cliente = datos.get('P', 0)
            peso_relativo = peticiones_proveedor_cliente / totalCliente
            peso_global = peso_peticiones.get(mayorista_id_int, 0.0)

            """
            print(f"{agencia} - Mayorista {mayorista_id}: peso_relativo={peso_relativo:.4f}, peso_global={peso_global:.4f}")
            """

            if peso_relativo > 2 * peso_global:
                clientes_proveedor_categoria[agencia]['B'].append(mayorista_id_int)
            elif peso_relativo < peso_global:
                clientes_proveedor_categoria[agencia]['M'].append(mayorista_id_int)
            else:
                clientes_proveedor_categoria[agencia]['N'].append(mayorista_id_int)

    """
    print("\ntotal_peticiones_proveedor (ordenado por bp")
    for proveedor, datos in total_peticiones_proveedor.items():
        print(f"Mayorista {proveedor} → P: {datos['P']}, B: {datos['B']:.2f}, R: {datos['R']}, BP: {datos['BP']:.6f}")

    
    print("\nDetalle completo de peticiones_cliente_hotel")
    for agencia in peticiones_cliente_hotel:
        print(f"\nAgencia: {agencia}")
        for hotel_id in peticiones_cliente_hotel[agencia]:
            datos = peticiones_cliente_hotel[agencia][hotel_id]
            print(f"  Hotel {hotel_id} → P: {datos.get('P', 0)}, B: {datos.get('B', 0.0):.2f}, BP: {datos.get('BP', 0.0):.2f}, C: {datos.get('C', 0)}")


    print("\ntotal_peticiones_cliente_proveedor_multi)
    for agencia in total_peticiones_cliente_proveedor_multi:
        print(f"{agencia} → Total peticiones multi: {total_peticiones_cliente_proveedor_multi[agencia]}")
    
    
    
    print("\nclientes_proveedor_categoria")
    for cliente in clientes_proveedor_categoria:
        print(f"\nAgencia: {cliente}")
        for categoria in ['B', 'M', 'N']:
            proveedores = clientes_proveedor_categoria[cliente][categoria]
            if proveedores:
                print(f"  Categoria {categoria}: {', '.join(proveedores)}")
    """
    

    historico = {
        dia: {
            "total_peticiones_proveedor": total_peticiones_proveedor,
            "total_peticiones_cliente_proveedor": total_peticiones_cliente_proveedor,
            "total_peticiones_cliente_proveedor_multi": total_peticiones_cliente_proveedor_multi,
            "peticiones_cliente_proveedor": peticiones_cliente_proveedor,
            "peticiones_cliente_hotel": peticiones_cliente_hotel,
            "clientes_proveedor_categoria": clientes_proveedor_categoria,
            "beneficio_cliente_proveedor": beneficio_cliente_proveedor,
            "beneficio": beneficio,
            "beneficio_cliente_total": beneficio_cliente_total
        }
    }

    for agencia, total_hotel in total_peticiones_cliente_proveedor.items():
        if agencia in total_peticiones_cliente_proveedor_multi:
            total_multi = total_peticiones_cliente_proveedor_multi[agencia]
            if total_hotel == 0:
                continue
            ratio_multi_hotel = total_multi / total_hotel

            for n in range(200):  
                mayorista_id = n  
                datos_prov = peticiones_cliente_proveedor.get(agencia, {}).get(mayorista_id)
                if datos_prov:
                    p = datos_prov.get("P", 0)
                    m = datos_prov.get("M", 0)
                    if p > 0 and m > 0:
                        v = (m / p) / ratio_multi_hotel
                        peticiones_cliente_proveedor[agencia][mayorista_id]["V"] = v

    os.makedirs(os.path.dirname(ruta_rendimiento), exist_ok=True)
    with gzip.open(ruta_rendimiento, "wb") as f:
        pickle.dump(historico, f)

    print(f"Dia {dia}: rendimiento generado correctamente")

    return historico
