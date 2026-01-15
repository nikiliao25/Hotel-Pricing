def saltar_agencia(historico_hoy, historico_ayer, agencia):
    hoy_tiene_peticiones = agencia in historico_hoy.get("peticiones_cliente_hotel", {})
    ayer_tiene_peticiones = agencia in historico_ayer.get("peticiones_cliente_hotel", {})

    return not (hoy_tiene_peticiones or ayer_tiene_peticiones)
