import os
import random
from descuentos_optimizador.configuracion import Config


def generar_precios_neto_por_mayorista():
 
    hoteles = list(range(1, Config.NUM_HOTELES + 1))  # 
    mayoristas = [str(i) for i in range(1, Config.NUM_MAYORISTAS + 1)]

 
    directorio_salida = os.path.dirname(Config.RUTA_PRECIOS_PROVEEDOR)
    os.makedirs(directorio_salida, exist_ok=True)
    ruta_salida = Config.RUTA_PRECIOS_PROVEEDOR

    with open(ruta_salida, "w") as f:
        for hotel in hoteles:
            n_mayoristas = random.randint(Config.MIN_MAYORISTAS_POR_HOTEL, Config.MAX_MAYORISTAS_POR_HOTEL)
            mayoristas_asignados = random.sample(mayoristas, n_mayoristas)

            precio_base = round(random.uniform(Config.MIN_PRECIO, Config.MAX_PRECIO - Config.MAX_DIFERENCIA_PRECIO), 2)

            precios = []
            for mayorista in mayoristas_asignados:
                precio = round(precio_base + random.uniform(0, Config.MAX_DIFERENCIA_PRECIO), 2)
                precios.append(f"{mayorista} {precio:.2f}")

            f.write(f"{hotel} {', '.join(precios)}\n")

    print(f"Precios netos generados correctamente en: {ruta_salida}")

if __name__ == "__main__":
    generar_precios_neto_por_mayorista()
