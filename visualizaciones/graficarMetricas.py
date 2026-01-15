import matplotlib.pyplot as plt  

def graficar_metricas(beneficios, ventas):
    dias = list(range(1, len(beneficios) + 1))

    plt.figure(figsize=(12, 5))
    plt.plot(dias, beneficios, marker='o', label="Beneficio total (€)")
    plt.title("Beneficio total por dia")
    plt.xlabel("Dia")
    plt.ylabel("Beneficio (€)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 5))
    plt.plot(dias, ventas, marker='x', color="green", label="Reservas")
    plt.title("Reservas por dia")
    plt.xlabel("Dia")
    plt.ylabel("Numero de reservas")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
