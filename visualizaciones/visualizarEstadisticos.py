import os
import gzip
import pickle
import pandas as pd
from descuentos_optimizador.configuracion import Config

def cargar_rendimiento(dia):
    ruta_rendimiento = os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{dia}.gz")
    if not os.path.exists(ruta_rendimiento):
        return None
    with gzip.open(ruta_rendimiento, 'rb') as f:
        return pickle.load(f)

def procesar_dia(dia, data):
    beneficio_total = 0
    total_peticiones = 0
    total_reservas = 0
    total_bp = 0
    total_clientes = 0

    clientes = data.get("beneficio_cliente_total", {})
    for cliente, valores in clientes.items():
        b = valores.get("B", 0.0)
        p = valores.get("P", 0)
        c = valores.get("C", 0)
        bp = valores.get("BP", 0.0)

        beneficio_total += b
        total_peticiones += p
        total_reservas += c
        total_bp += bp
        total_clientes += 1

    beneficio_por_peticion = beneficio_total / total_peticiones if total_peticiones else 0
    beneficio_por_reserva = beneficio_total / total_reservas if total_reservas else 0
    conversion_rate = total_reservas / total_peticiones if total_peticiones else 0

    return {
        "dia": dia,
        "beneficio_total": round(beneficio_total, 2),
        "total_peticiones": total_peticiones,
        "total_reservas": total_reservas,
        "beneficio_medio_peticion": round(beneficio_por_peticion, 6),
        "beneficio_medio_reserva": round(beneficio_por_reserva, 6),
        "conversion_rate": round(conversion_rate, 4),
        "clientes_analizados": total_clientes
    }

def analizar_rendimiento():
    dias = []
    dia = 1

    while True:
        data = cargar_rendimiento(dia)
        if data is None:
            break
        resumen = procesar_dia(dia, data)
        dias.append(resumen)
        dia += 1

    df = pd.DataFrame(dias)
    os.makedirs(os.path.dirname(Config.RUTA_SALIDA_RESUMEN), exist_ok=True)
    df.to_csv(Config.RUTA_SALIDA_RESUMEN, index=False, sep="|", float_format="%.6f")
    print("Resumen generado correctamente en:", Config.RUTA_SALIDA_RESUMEN)
    print(df)

if __name__ == "__main__":
    analizar_rendimiento()
