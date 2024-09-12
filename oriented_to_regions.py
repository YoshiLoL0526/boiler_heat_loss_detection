import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color
from skimage.segmentation import flood, flood_fill

# Cargar la imagen térmica RGB
image_path = 'caldera/1.jpg'
image = io.imread(image_path)

# Convertir la imagen a escala de grises
gray_image = color.rgb2gray(image)

# Seleccionar un punto de inicio para el crecimiento de la región (semilla)
seed_point = (145, 35)  # Cambia esto según tu imagen

# Aplicar la segmentación orientada a regiones usando crecimiento de regiones
# El valor de tolerancia define el rango de valores de intensidad que se incluirán en la región
tolerance = 0.05
segmented_image = flood(gray_image, seed_point, tolerance=tolerance)

# Visualizar la imagen original y la imagen segmentada
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(image)
ax[0].set_title('Imagen Térmica RGB Original')
ax[0].axis('off')

ax[1].imshow(segmented_image, cmap='gray')
ax[1].set_title('Imagen Segmentada')
ax[1].axis('off')

plt.show()
