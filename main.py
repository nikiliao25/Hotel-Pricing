import pickle
import gzip
import os

from descuentos_optimizador.scripts.grabarHistorico import grabar_historico
from descuentos_optimizador.scripts.calcularValor import calcular_valor
from descuentos_optimizador.scripts.saltarAgencia import saltar_agencia
from descuentos_optimizador.scripts.leerFicherosMejores import leer_ficheros_mejores
from descuentos_optimizador.configuracion import Config

def ejecutar_algoritmo_descuentos(DIA_ACTUAL):
    DIA_AYER = DIA_ACTUAL - 1
    DIA_ANTEAYER = DIA_ACTUAL - 2

    def cargar_pickle_gz(path):
        with gzip.open(path, 'rb') as f:
            return pickle.load(f)

    fecha_ultima_actualizacion = cargar_pickle_gz(Config.RUTA_FECHA_ACTUALIZACION)
    historico_ayer = cargar_pickle_gz(os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{DIA_AYER}.gz"))
    descuentos_ayer = cargar_pickle_gz(os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{DIA_ANTEAYER}.gz"))
    descuentos_hoy = cargar_pickle_gz(os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{DIA_AYER}.gz"))


    historico_hoy = grabar_historico(DIA_ACTUAL)
    ficheros_mejores = {}
    leer_ficheros_mejores(ficheros_mejores)

    historico_hoy = historico_hoy.get(DIA_ACTUAL, {})
    historico_ayer = historico_ayer.get(DIA_AYER, {})
    

    peso_clientes_proveedores = {}
    for agencias, hoteles in descuentos_hoy.items():
        for hotel_id, dto in hoteles.items():
            if isinstance(hotel_id, str): 
                try:
                    IDHotel_int = int(hotel_id)
                    hoteles[IDHotel_int] = hoteles.pop(hotel_id)
                    hotel_id = IDHotel_int
                except ValueError:
                    continue
            if hotel_id in ficheros_mejores:
                prov1, prov2 = ficheros_mejores[hotel_id]

                if agencias not in peso_clientes_proveedores:
                    peso_clientes_proveedores[agencias] = {}
                if prov1 not in peso_clientes_proveedores[agencias]:
                    peso_clientes_proveedores[agencias][prov1] = {}
                if prov2 not in peso_clientes_proveedores[agencias][prov1]:
                    peso_clientes_proveedores[agencias][prov1][prov2] = {"dto": 0.0, "n": 0}

                peso_clientes_proveedores[agencias][prov1][prov2]["dto"] += dto
                peso_clientes_proveedores[agencias][prov1][prov2]["n"] += 1

    a = []
    media = {}
    ruta_txt = Config.RUTA_ANALISIS_COMISIONES
    with open(ruta_txt, 'r') as f:
        for linea in f:
            b = linea.strip().split("|")
            if len(b) < 10:
                continue
            a.append(b)
            if b[0].isdigit() and b[9].isdigit():
                agencia_id = b[0]
                comision_media = float(b[5])
                total_reservas = int(b[9])
                if agencia_id in media:
                    media[agencia_id]["m"] += comision_media * total_reservas
                    media[agencia_id]["t"] += total_reservas
                else:
                    media[agencia_id] = {"m": comision_media * total_reservas, "t": total_reservas}

    medias = {}
    for agencia_id, valores in media.items():
        total = valores["t"]
        medias[agencia_id] = {
            "m": valores["m"] / total if total else 0.0,
            "t": total
        }
 

    pesos = {}
    for i, dato in enumerate(a):
        if len(dato) > 2 and i > 0:
            agencia = dato[1]
            try:
                hotel = int(dato[2])  
            except ValueError:
                continue
            try:
                com_max = float(dato[3])
                com_media = float(dato[5])
            except (ValueError, IndexError):
                continue
            margen_agencia = medias.get(agencia, {}).get("m", 0)
            pesos.setdefault(agencia, {})[hotel] = margen_agencia - com_max if (margen_agencia - com_max) > 0 else margen_agencia - com_media

            if hotel not in fecha_ultima_actualizacion.get(agencia, {}):
                fecha_ultima_actualizacion.setdefault(agencia, {})[hotel] = DIA_ACTUAL

            if hotel not in descuentos_hoy.get(agencia, {}):
                mejores = ficheros_mejores.get(hotel)
                if mejores and mejores[0] in peso_clientes_proveedores.get(agencia, {}) and \
                mejores[1] in peso_clientes_proveedores[agencia][mejores[0]]:
                    peso = peso_clientes_proveedores[agencia][mejores[0]][mejores[1]]
                    descuento = peso["dto"] / peso["n"] if peso["n"] != 0 else 0
                    descuentos_hoy.setdefault(agencia, {})[hotel] = max(descuento, 0)
                else:
                    descuentos_hoy.setdefault(agencia, {})[hotel] = pesos[agencia][hotel]


    for agencias, data in historico_hoy.get("peticiones_cliente_hotel", {}).items():
        if saltar_agencia(historico_hoy, historico_ayer, agencias):
            continue
        for hotel_id, _ in data.items():
            try:
                hotel_id = int(hotel_id)
            except ValueError:
                continue  

            beneficio_hoy = historico_hoy["peticiones_cliente_hotel"][agencias][hotel_id].get("B", 0)

            if beneficio_hoy > 0:
                if agencias in descuentos_hoy and hotel_id in descuentos_hoy[agencias]:
                    if agencias in descuentos_ayer and hotel_id in descuentos_ayer[agencias]:
                        beneficio_ayer = historico_ayer.get("peticiones_cliente_hotel", {}).get(agencias, {}) \
                            .get(hotel_id, {}).get("B", 0)
                        dto_hoy = descuentos_hoy[agencias][hotel_id]
                        dto_ayer = descuentos_ayer[agencias][hotel_id]
                        dif = dto_hoy - dto_ayer
                        """
                        print(f"{agencias}-{hotel_id}: B_hoy={beneficio_hoy}, B_ayer={beneficio_ayer}, dto_hoy={dto_hoy:.3f}, dto_ayer={dto_ayer:.3f}, dif={dif:.3f}")
                        """
                        if beneficio_hoy > beneficio_ayer:
                            descuentos_hoy[agencias][hotel_id] += 0.1 if dif >= 0 else -0.1
                        else:
                            descuentos_hoy[agencias][hotel_id] -= dif
                        fecha_ultima_actualizacion.setdefault(agencias, {})[hotel_id] = DIA_ACTUAL
            else:
                if agencias in descuentos_hoy and hotel_id in descuentos_hoy[agencias]:
                    if agencias in descuentos_ayer and hotel_id in descuentos_ayer[agencias]:
                        dif = descuentos_hoy[agencias][hotel_id] - descuentos_ayer[agencias][hotel_id]
                        peticionesAyer = historico_ayer.get("peticiones_cliente_hotel", {}).get(agencias, {}) \
                            .get(hotel_id, {}).get("P", 0)
                        peticionesHoy = historico_hoy.get("peticiones_cliente_hotel", {}).get(agencias, {}) \
                            .get(hotel_id, {}).get("P", 0)
                        valor = calcular_valor(historico_hoy, agencias, hotel_id, peticionesAyer)
                        if peticionesHoy > peticionesAyer and dif >= 0:
                            descuentos_hoy[agencias][hotel_id] += valor
                        elif dif <= 0:
                            descuentos_hoy[agencias][hotel_id] += valor
                        fecha_ultima_actualizacion.setdefault(agencias, {})[hotel_id] = DIA_ACTUAL


    for agencias, data in historico_ayer.get("peticiones_cliente_hotel", {}).items():
        if saltar_agencia(historico_hoy, historico_ayer, agencias):
            continue
        for hotel_id in data:
            try:
                hotel_id = int(hotel_id)
            except ValueError:
                continue

            if agencias not in descuentos_hoy or hotel_id not in descuentos_hoy[agencias]:
                continue

            if agencias not in historico_hoy.get("peticiones_cliente_hotel", {}) or \
            hotel_id not in historico_hoy["peticiones_cliente_hotel"].get(agencias, {}):
                beneficio_ayer = historico_ayer["peticiones_cliente_hotel"][agencias][hotel_id].get("B", 0)
                valor = calcular_valor(historico_ayer, agencias, hotel_id, 0)
                dif = descuentos_hoy[agencias][hotel_id] - descuentos_ayer.get(agencias, {}).get(hotel_id, 0)
                if beneficio_ayer > 0:
                    descuentos_hoy[agencias][hotel_id] -= dif if dif > 0 else -valor
                else:
                    if agencias in descuentos_ayer and hotel_id in descuentos_ayer[agencias]:
                        dif = descuentos_hoy[agencias][hotel_id] - descuentos_ayer[agencias][hotel_id]
                        descuentos_hoy[agencias][hotel_id] -= dif if dif > 0 else -valor
                fecha_ultima_actualizacion.setdefault(agencias, {})[hotel_id] = DIA_ACTUAL

    
    for agencias, data in descuentos_hoy.items():
        for hotel_id in list(data):
            try:
                hotel_id = int(hotel_id)
            except ValueError:
                continue

            if descuentos_hoy[agencias][hotel_id] > Config.DESCUENTO_MAX:
                descuentos_hoy[agencias][hotel_id] = Config.DESCUENTO_MAX
            elif descuentos_hoy[agencias][hotel_id] < Config.DESCUENTO_MIN:
                descuentos_hoy[agencias][hotel_id] = Config.DESCUENTO_MIN

    with gzip.open(os.path.join(Config.RUTA_DESCUENTOS, f"pesos-{DIA_ACTUAL}.gz"), 'wb') as f:
        pickle.dump(descuentos_hoy, f)

    with gzip.open(Config.RUTA_FECHA_ACTUALIZACION, 'wb') as f:
        pickle.dump(fecha_ultima_actualizacion, f)

