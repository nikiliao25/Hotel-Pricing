import os
import glob
from descuentos_optimizador.configuracion import Config

def borrar_datos_previos():
    patrones_relativos = [
        "datos/gz/descuentos/pesos-*.gz",
        "datos/gz/rendimiento/rendimiento-*.gz",
        "datos/gz/fechaUltimaActualizacion.gz",
        "datos/bruto/cambiables/*.txt",
        "datos/csv/cambiables/*.csv", 
        "datos/pkl/cambiables/*.pkl"
    ]

    archivos_eliminados = 0

    for patron_relativo in patrones_relativos:
        ruta_completa = os.path.join(Config.RUTA_BASE, patron_relativo)
        for archivo in glob.glob(ruta_completa):
            try:
                os.remove(archivo)
                print(f"Archivo eliminado: {archivo}")
                archivos_eliminados += 1
            except Exception as e:
                print(f"Error eliminando {archivo}: {e}")

    if archivos_eliminados == 0:
        print("No se encontraron archivos previos para eliminar.")
    else:
        print(f"Total archivos eliminados: {archivos_eliminados}")

if __name__ == "__main__":
    borrar_datos_previos()
