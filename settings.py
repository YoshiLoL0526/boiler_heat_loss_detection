# Definir la paleta de colores en escala de grises
PALETTE = {
    (255, 255, 255): 255,  # blanco
    (0, 0, 255): 204,  # rojo
    (0, 255, 255): 153,  # amarillo
    (0, 255, 0): 102,  # verde
    (255, 0, 0): 51,  # azul
    (0, 0, 0): 0  # negro
}

# Definir constantes
B = 330  # Flujo de combustible (kg/h)
# B = B / 3600  # Flujo de combustible (kg/s).
AC = 15  # Coeficiente de transferencia de calor por convección para gases (W/m^2K)
TAF = 306  # Temperatura ambiente (K)
CO = 5.97e-08  # Constante de Stefan Boltzmann (W/m2*k^4)
DIAMETER = 1.35  # Largo de la caldera en la imagen (m)
