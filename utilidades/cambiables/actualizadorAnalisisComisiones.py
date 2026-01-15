import os
import pickle
import pandas as pd
import random

from descuentos_optimizador.configuracion import Config

def actualizar_analisis_comisiones_formato(dia_actual):
    
    ruta_ventas = Config.RUTA_VENTAS
    ruta_pkl = Config.RUTA_COMISIONES_PKL
    ruta_comisiones = Config.RUTA_ANALISIS_COMISIONES

   
    if os.path.exists(ruta_pkl):
        with open(ruta_pkl, "rb") as f:
            historico = pickle.load(f)
    else:
        historico = []

  
    nuevas_filas = []
    if os.path.exists(ruta_ventas):
        with open(ruta_ventas, "r") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) == 7:
                    try:
                        hotel_id = int(parts[0])
                        nombre_agencia = parts[1].strip()
                        agencia_id = int(parts[2].strip())
                        neto = float(parts[4])
                        if neto == 0:
                            continue
                        margen_pct = min(30, max(5, random.betavariate(2, 10) * 35))
                        precio = neto * (1 + margen_pct / 100)
                        comision_pct = ((precio - neto) / neto) * 100
                        nuevas_filas.append({
                            "hotelid": hotel_id,
                            "agenciaid": agencia_id,
                            "nombre_agencia": nombre_agencia,
                            "comision": comision_pct,
                            "dia": dia_actual
                        })
                    except ValueError:
                        continue

    historico.extend(nuevas_filas)


    os.makedirs(os.path.dirname(ruta_pkl), exist_ok=True)
    with open(ruta_pkl, "wb") as f:
        pickle.dump(historico, f)
    print(f"Dia {dia_actual}: .pkl actualizado correctamente")

 
    if not historico:
        print("No hay datos suficientes para analisis.")
        return

    df = pd.DataFrame(historico)

    resumen = df.groupby(["agenciaid", "nombre_agencia", "hotelid"]).agg(
        comision_max=("comision", "max"),
        comision_min=("comision", "min"),
        comision_media=("comision", "mean"),
        comision_std=("comision", "std"),
        n_reservas=("comision", "count"),
        reserva_1=("dia", "min"),
        reserva_n=("dia", "max")
    ).reset_index()

    resumen["comision_std"] = resumen["comision_std"].fillna(0.0)

    columnas = [
        "agenciaid", "nombre_agencia", "hotelid",
        "comision_max", "comision_min", "comision_media", "comision_std",
        "reserva_1", "reserva_n", "n_reservas"
    ]
    resumen = resumen[columnas]

    os.makedirs(os.path.dirname(ruta_comisiones), exist_ok=True)
    resumen.to_csv(ruta_comisiones, sep="|", index=False, float_format="%.6f")
    print(f"Dia {dia_actual}: analisis actualizado y CSV generado correctamente")
