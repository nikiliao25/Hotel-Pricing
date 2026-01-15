import os

class Config:
    NUM_AGENCIAS = 300
    NUM_HOTELES = 10000

    NUM_MAYORISTAS = 200
    MIN_MAYORISTAS_POR_HOTEL = 1
    MAX_MAYORISTAS_POR_HOTEL = 3
    MIN_PRECIO = 50.00
    MAX_PRECIO = 400.00
    MAX_DIFERENCIA_PRECIO = 10.00
    MIN_PETICIONES = 1
    MAX_PETICIONES = 100

    RUTA_BASE = "/Users/nikiliao/Desktop/Projects/Hotel Pricing Normal/descuentos_optimizador"

    RUTA_DESCUENTOS = os.path.join(RUTA_BASE, "datos/gz/descuentos/")
    RUTA_RENDIMIENTO = os.path.join(RUTA_BASE, "datos/gz/rendimiento/")
    RUTA_SALIDA_RESUMEN = os.path.join(RUTA_BASE, "datos/csv/cambiables/estadisticasResumen.csv")
    RUTA_FECHA_ACTUALIZACION = os.path.join(RUTA_BASE, "datos/gz/fechaUltimaActualizacion.gz")
    RUTA_FICHERO_MEJOR_PROVEEDOR = os.path.join(RUTA_BASE, "datos/bruto/cambiables/ficheroMejorProveedor.txt")
    RUTA_BRUTO = os.path.join(RUTA_BASE, "datos/bruto/")


    RUTA_PRECIOS_PROVEEDOR = os.path.join(RUTA_BASE, "datos/bruto/fijos/preciosMayoristaHotel.txt")
    RUTA_DISTANCIA_HOTELES = os.path.join(RUTA_BASE, "datos/csv/fijos/infoHoteles.txt")
    RUTA_MEJOR_PROVEEDOR = os.path.join(RUTA_BASE, "datos/bruto/cambiables/ficheroMejorProveedor.txt")
    RUTA_VENTAS = os.path.join(RUTA_BASE, "datos/bruto/cambiables/hotelesCredencialesMayorista.txt")
    RUTA_PETICIONES_HOTEL = os.path.join(RUTA_BASE, "datos/bruto/cambiables/peticionesHotel.txt")
    RUTA_PETICIONES_PROVEEDOR = os.path.join(RUTA_BASE, "datos/bruto/cambiables/peticionesProveedor.txt")
    RUTA_PETICIONES_PROVEEDOR_MULTI = os.path.join(RUTA_BASE, "datos/bruto/cambiables/peticionesProveedorMulti.txt")

    RUTA_DATOS_HOTELES = os.path.join(RUTA_BASE, "datos/csv/fijos/datosDatasets.csv")
    RUTA_MODELO = os.path.join(RUTA_BASE, "datos/pkl/fijos/modeloFinal.pkl")

    RUTA_ANALISIS_COMISIONES = os.path.join(RUTA_BASE, "datos/csv/cambiables/analisisComisionesAgencias.csv")
    RUTA_COMISIONES_PKL = os.path.join(RUTA_BASE, "datos/pkl/cambiables/analisisComisiones.pkl")

    DESCUENTO_MIN = -5.0
    DESCUENTO_MAX = 3.0
