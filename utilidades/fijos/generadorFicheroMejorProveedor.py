import os
import datetime
from descuentos_optimizador.configuracion import Config

def generar_mejor_proveedor():
    ruta_precios_proveedor = Config.RUTA_PRECIOS_PROVEEDOR
    ruta_salida = Config.RUTA_MEJOR_PROVEEDOR

    hotel_proveedor_precios = {}

    with open(ruta_precios_proveedor, "r") as f:
        for n_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                partes = linea.split(" ", 1)
                hotel_id = int(partes[0])
                precios = partes[1].split(",")
                hotel_proveedor_precios[hotel_id] = {}
                for par in precios:
                    proveedor, precio = par.strip().split()
                    hotel_proveedor_precios[hotel_id][proveedor] = float(precio)
            except Exception as e:
                print(f"[Linea {n_linea}] Error: {e} → '{linea}'")

    hoy = datetime.date.today().isoformat()
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    with open(ruta_salida, "w") as f:
        for hotel_id, proveedores in hotel_proveedor_precios.items():
            mejores = sorted(proveedores.items(), key=lambda x: x[1])
            mejor = mejores[0][0] if len(mejores) > 0 else "0"
            segundo = mejores[1][0] if len(mejores) > 1 else "0"
            f.write(f"Sistema {hoy} {hotel_id} {mejor} {segundo}\n")

    print(f"ficheroMejorProveedor.txt generado correctamente")