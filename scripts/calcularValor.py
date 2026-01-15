def calcular_valor(historico, agencia, hotel_id, peticiones_otro_dia):
    hoteles_comprados = len(historico.get("beneficio", {}).get(agencia, {}))
    

    hoteles_pedidos = len(historico.get("peticiones_cliente_hotel", {}).get(agencia, {}))

    if hoteles_comprados > 0:
        multiplicador = hoteles_pedidos / (hoteles_comprados * 200)
    else:
        multiplicador = hoteles_pedidos

    if multiplicador == 0:
        multiplicador = 1

    if "BP" in historico.get("beneficio_cliente_total", {}).get(agencia, {}):
        BP = historico["beneficio_cliente_total"][agencia]["BP"]
    else:
        total_peticiones = historico.get("total_peticiones_cliente_proveedor", {}).get(agencia, 0)
        BP = 1 / total_peticiones if total_peticiones != 0 else 0

    peticiones_hoy = historico.get("peticiones_cliente_hotel", {}).get(agencia, {}).get(hotel_id, {}).get("P", 0)

    valor = abs((peticiones_hoy - peticiones_otro_dia) * BP * multiplicador)
    """
    print(valor)
    """


    if valor > 0.25:
        valor = 0.25
    if valor == 0:
        valor = 0.01

    return valor
