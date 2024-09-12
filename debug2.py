import numpy as np
import matplotlib.pyplot as plt
from settings import PALETTE
from utils import interpolate_palette, create_palette_image

if __name__ == '__main__':
    palette = interpolate_palette(PALETTE)

    palette_image1 = create_palette_image(PALETTE)
    palette_image2 = create_palette_image(palette)

    # Crear la figura y los subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Primer subplot con la paleta de colores 'viridis'
    ax1.imshow(palette_image1)
    ax1.set_title('Paleta de colores original')
    ax1.set_axis_off()

    # Segundo subplot con la paleta de colores 'plasma'
    ax2.imshow(palette_image2)
    ax2.set_title('Paleta de colores interpolada')
    ax2.set_axis_off()

    # Mostrar la figura
    plt.tight_layout()
    plt.show()
