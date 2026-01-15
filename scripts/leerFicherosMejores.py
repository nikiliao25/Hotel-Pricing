from descuentos_optimizador.configuracion import Config
def leer_ficheros_mejores(ficheros_mejores):
    ruta = Config.RUTA_FICHERO_MEJOR_PROVEEDOR

    with open(ruta, 'r') as f:
        for linea in f:
            data = linea.strip().split()
            if len(data) > 4:
                try:
                    proveedor_id = int(data[2])
                    ficheros_mejores[proveedor_id] = [data[3], data[4]]
                except ValueError:
                    print(f"ID invalido en linea: {linea.strip()}")
            elif len(data) > 3:
                try:
                    proveedor_id = int(data[2])
                    ficheros_mejores[proveedor_id] = [data[3], "0"]
                except ValueError:
                    print(f"ID invalido en linea: {linea.strip()}")
    
    """
    print("\nficheros_mejores")
    for hotel_id, mayorista in ficheros_mejores.items():
        print(f"Hotel {hotel_id}: Mejor Proveedor = {mayorista[0]}, Segundo Mejor Proveedor = {mayorista[1]}")
    """

