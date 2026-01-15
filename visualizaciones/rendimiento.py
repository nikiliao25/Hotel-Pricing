import gzip
import pickle
import os
from descuentos_optimizador.configuracion import Config

def revisar_rendimiento(dia):
    ruta = os.path.join(Config.RUTA_RENDIMIENTO, f"rendimiento-{dia}.gz")


    if not os.path.exists(ruta):
        print(f"El archivo para el dia {dia} no existe.")
        return

    with gzip.open(ruta, 'rb') as f:
        data = pickle.load(f)

    print(f"\nContenido del rendimiento del dia {dia}:")
    print("-" * 50)
    
    for key in data:
        valor = data[key]
        print(f"Clave: {key} — Tipo: {type(valor)}")
        if isinstance(valor, dict):
            print(f"Total claves: {len(valor)}")

    
    if dia in data:
        sub = data[dia]
        print(f"\nDetalles dentro de la clave '{dia}':")
        for key in sub:
            val = sub[key]
            n_claves = len(val) if isinstance(val, dict) else 'N/A'
            print(f"{key}: tipo {type(val)} - total claves: {n_claves}")

        if "peticiones_cliente_hotel" in sub:
            peticiones = sub["peticiones_cliente_hotel"]
            if peticiones:
                ejemplo_agencia = next(iter(peticiones))
                hoteles = peticiones[ejemplo_agencia]
                print(f"\nEjemplo de agencia: {ejemplo_agencia} — Total hoteles: {len(hoteles)}")
                for hotel_id, datos in hoteles.items():
                    print(f"   - Hotel {hotel_id}: {datos}")
                    break
    else:
        print(f"No se encontro la clave '{dia}' en el diccionario.")

if __name__ == "__main__":
    revisar_rendimiento(20)
