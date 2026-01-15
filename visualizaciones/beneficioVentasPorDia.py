from descuentos_optimizador.configuracion import Config

    
def obtener_beneficio_y_ventas_dia():
    ruta = Config.RUTA_VENTAS

    total_beneficio = 0.0
    total_ventas = 0

    
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split(";")
            if len(partes) < 6:
                continue
            try:
                beneficio = float(partes[5])
                total_beneficio += beneficio
                total_ventas += 1
            except ValueError:
                continue
   

    return total_beneficio, total_ventas

