from descuentos_optimizador.visualizaciones.graficarMetricas import graficar_metricas
from descuentos_optimizador.visualizaciones.beneficioVentasPorDia import obtener_beneficio_y_ventas_dia


from descuentos_optimizador.utilidades.fijos.generadorFicheroMejorProveedor import generar_mejor_proveedor
from descuentos_optimizador.utilidades.fijos.generadorDosPesos import generar_dos_descuentos_base
from descuentos_optimizador.utilidades.fijos.generadorFechaUltimaActualizacion import generar_fecha_ultima_actualizacion

from descuentos_optimizador.utilidades.cambiables.generadorVentas import generar_ventas_por_dia
from descuentos_optimizador.utilidades.cambiables.generadorPeticionesHotel import generar_peticiones_hotel_por_dia
from descuentos_optimizador.utilidades.cambiables.generadorPeticionesProveedor import generar_peticiones_proveedor
from descuentos_optimizador.utilidades.cambiables.actualizadorAnalisisComisiones import actualizar_analisis_comisiones_formato

from descuentos_optimizador.scripts.grabarHistorico import grabar_historico
from descuentos_optimizador.scripts.borrarArchivosIniciales import borrar_datos_previos
from descuentos_optimizador.main import ejecutar_algoritmo_descuentos

NUM_DIAS = 365

def preparar_dia_2():
    print("[Preparacion] Generando datos base para Dia 1 y Dia 2...")
    generar_mejor_proveedor()
    generar_dos_descuentos_base()
    generar_fecha_ultima_actualizacion()

    dia = 2
    generar_ventas_por_dia(dia)
    generar_peticiones_hotel_por_dia(dia)
    generar_peticiones_proveedor(dia)
    actualizar_analisis_comisiones_formato(dia)
    grabar_historico(dia) 


def simular():
    borrar_datos_previos()
    preparar_dia_2()

    beneficios_diarios = []
    ventas_diarias = []

    for dia in range(3, NUM_DIAS + 3):
        print(f"----------- Simulando Dia {dia} -----------")
        generar_ventas_por_dia(dia)
        generar_peticiones_hotel_por_dia(dia)
        generar_peticiones_proveedor(dia)
        actualizar_analisis_comisiones_formato(dia)

        beneficio, ventas = obtener_beneficio_y_ventas_dia()
        beneficios_diarios.append(beneficio)
        ventas_diarias.append(ventas)
    
        ejecutar_algoritmo_descuentos(dia)

    graficar_metricas(beneficios_diarios, ventas_diarias)

    ventas_total = sum(ventas_diarias)
    ventas_media = ventas_total / len(ventas_diarias)
    beneficio_total = sum(beneficios_diarios)
    beneficio_medio = beneficio_total / len(beneficios_diarios) 

    print(f"Ventas total acumulado: {ventas_total:,.2f}")
    print(f"Ventas media por dia: {ventas_media:,.2f}") 
    print(f"Beneficio total acumulado: {beneficio_total:,.2f}")
    print(f"Beneficio medio por dia: {beneficio_medio:,.2f}")


if __name__ == "__main__":
    simular()
