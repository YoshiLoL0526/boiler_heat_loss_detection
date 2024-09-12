from io import BytesIO

import cv2
import matplotlib.pyplot as plt
import numpy as np

from settings import PALETTE
from utils import interpolate_palette, nearest_color, celsius_to_kelvin


class ThermalImageProcessor:
    def __init__(self):
        self.palette = interpolate_palette(PALETTE)

    def apply_bilateral_filter(self, image):
        """
        Aplica un filtro bilateral a la imagen para mejorarla.
        """

        return cv2.bilateralFilter(image, 9, 75, 75)

    def calculate_grayscale_map(self, image):
        """
        Calcula el mapa en escala de grises a partir de una imagen RGB.
        """

        height, width, _ = image.shape
        grayscale_map = np.zeros((height, width), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                grayscale_map[i, j] = nearest_color(image[i, j], self.palette)
        return grayscale_map

    def calculate_temperature_map(self, grayscale_map, max_temp, min_temp):
        """
        Calcula el mapa de temperaturas de una imagen térmica.
        """

        temperature_map = grayscale_map / 255 * (max_temp - min_temp) + min_temp
        return temperature_map

    def find_hot_zones(self, grayscale_map, threshold_hot=200):
        """
        Busca zonas calientes en el mapa en escala de grises.
        """

        mask = cv2.threshold(grayscale_map, threshold_hot, 255, cv2.THRESH_BINARY)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours, hierarchy

    def calculate_histogram(self, temperature_map, min_temp, max_temp):
        """
        Calcula y guarda el histograma del mapa de temperaturas.
        """

        # Crear el histograma
        fig, ax = plt.subplots()
        ax.hist(temperature_map.ravel(), bins=50, range=(min_temp, max_temp),
                color='blue', alpha=0.7)
        ax.set_title('Histograma de la Imagen Térmica')
        ax.set_xlabel('Valor de temperatura (K)')
        ax.set_ylabel('Frecuencia')

        # Guardar la imagen en un objeto BytesIO en lugar de en el disco
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Obtener los bytes de la imagen
        image_bytes = buf.getvalue()

        # Convertir los bytes en un array de NumPy
        nparr = np.frombuffer(image_bytes, np.uint8)

        # Decodificar la imagen usando OpenCV
        image_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Cerrar el buffer y la figura
        buf.close()
        plt.close(fig)

        return image_cv2

    def calculate_heat_loss(self, image, grayscale, contours, hierarchy, b, ac, taf, co, d, bw, min_temp, max_temp):
        """
        Calcula la pérdida de calor en cada zona caliente.
        """

        px_per_meter = bw / d

        data = []
        # original_image = self.image.copy()
        for idx, contour in enumerate(contours):

            # Verificar si el contorno NO es un hueco
            if hierarchy[0][idx][3] != -1:
                continue

            temp_image = image.copy()
            cv2.drawContours(temp_image, [contour], 0, (0, 0, 0), 2)
            # cv2.drawContours(original_image, [contour], 0, (0, 0, 0), 2)
            mask = np.zeros(grayscale.shape, np.uint8)
            cv2.drawContours(mask, [contour], 0, 255, -1)

            zone = grayscale[mask == 255]
            area_px = cv2.contourArea(contour)

            # Comprobar si existen huecos en el contorno
            for edx, contour2 in enumerate(contours):
                if hierarchy[0][edx][3] == idx:
                    cv2.drawContours(temp_image, [contour2], 0, (0, 0, 0), 2)
                    # cv2.drawContours(original_image, [contour2], 0, (0, 0, 0), 2)
                    area_px -= cv2.contourArea(contour2)

            # Convertir a metros el área de la zona caliente
            area = area_px / px_per_meter ** 2

            # Calcular temperatura promedio de la zona caliente
            mean_temp_zone = np.mean(
                zone / 255 * (max_temp - min_temp) + min_temp)

            # Calcular pérdida de calor de la zona caliente
            heat_loss = (area / b) * (ac * (celsius_to_kelvin(mean_temp_zone) - taf) + co * (
                    ((celsius_to_kelvin(mean_temp_zone) / 100) ** 4) - ((taf / 100) ** 4)))

            data.append((temp_image, area, mean_temp_zone, heat_loss))

        return data

    def process(self, image, b, ac, taf, co, d, bw, min_temp, max_temp, threshold_hot=200):
        """
        Realizar el procesamiento completo de la imagen térmica
        """

        filtered_image = self.apply_bilateral_filter(image)
        grayscale_map = self.calculate_grayscale_map(filtered_image)
        contours, hierarchy = self.find_hot_zones(grayscale_map, threshold_hot)

        temperature_map = self.calculate_temperature_map(grayscale_map, min_temp, max_temp)
        histogram = self.calculate_histogram(temperature_map, min_temp, max_temp)

        data = self.calculate_heat_loss(image, grayscale_map, contours, hierarchy, b, ac, taf, co, d, bw, min_temp, max_temp)
        return data, histogram
