import os
import cv2
import time
import numpy as np
from pdf import PDF
import configparser as cp
from datetime import datetime


def interpolate_color(color1, color2, ratio):
    """
    Interpola dos colores RGB y devuelve el color resultante.

    Args:
    color1 (tuple): El primer color en formato RGB (r, g, b).
    color2 (tuple): El segundo color en formato RGB (r, g, b).
    ratio (float): La proporción de interpolación entre los dos colores, debe estar en el rango [0, 1].

    Returns:
    tuple: El color resultante de la interpolación.
    """

    return tuple(int(c1 + (c2 - c1) * ratio) for c1, c2 in zip(color1, color2))


def interpolate_palette(palette):
    """
    Interpola todos los colores intermedios en una paleta dada para completar los 256 valores de escala de grises.

    Args:
    palette (dict): Un diccionario que mapea colores RGB a valores de escala de grises.

    Returns:
    dict: La paleta interpolada que incluye todos los valores intermedios de escala de grises.
    """
    interpolated_palette = {k: v for k, v in palette.items()}
    keys = list(palette.keys())
    keys.sort(key=lambda x: palette[x])

    for i in range(len(keys) - 1):
        color1 = keys[i]
        color2 = keys[i + 1]
        value1 = palette[color1]
        value2 = palette[color2]
        for j in range(value1 + 1, value2):
            ratio = (j - value1) / (value2 - value1)
            interpolated_color = interpolate_color(color1, color2, ratio)
            interpolated_palette[interpolated_color] = j

    return dict(sorted(interpolated_palette.items(), key=lambda item: item[1]))


def celsius_to_kelvin(t):
    """Convert from Celsius to Kelvin"""

    return t + 273.15


def kelvin_to_celsius(k):
    """
    Convierte una temperatura de Kelvin a grados Celsius.

    :param k: Temperatura en Kelvin
    :return: Temperatura en grados Celsius
    """

    return k - 273.15


def calculate_distance(color1, color2):
    """Calcula la distancia euclidiana entre dos colores RGB"""

    return ((color1[2] - color2[2]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[0] - color2[0]) ** 2) ** 0.5


def nearest_color(color, palette):
    """
    Buscar el color más cercano en la paleta de colores

    :param color: tuple
    :param palette: dict
    :return: tuple
    """

    min_color = (255, 255, 255)
    min_distance = float("inf")
    for c in palette:
        distance = calculate_distance(color, c)
        if distance < min_distance:
            min_color = c
            min_distance = distance

    return palette[min_color]


def generate_pdf_report(data, histogram, output_folder):
    """Generar reporte PDF"""

    pdf = PDF()
    pdf.add_page()

    # Agregar la fecha del reporte
    current_date = datetime.now().strftime('%d-%m-%Y')
    pdf.set_font('helvetica', 'I', 10)
    pdf.cell(0, 10, f'Fecha: {current_date}', 0, 1, 'R')

    # Crear un encabezado para la tabla de zonas calientes
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(50, 10, 'Zona Caliente', 1, 0, 'C')
    pdf.cell(50, 10, 'Temperatura Promedio', 1, 0, 'C')
    pdf.cell(40, 10, 'Área', 1, 0, 'C')
    pdf.cell(50, 10, 'Pérdida de Calor', 1, 0, 'C')
    pdf.ln(10)

    for idx, (image, area, mean_temp, heat_loss) in enumerate(data):
        img_path = os.path.join(output_folder, f'zone{idx}.jpg')
        cv2.imwrite(img_path, image)

        # Agrega la información de la zona caliente a la tabla
        pdf.set_font('helvetica', '', 10)
        pdf.cell(50, 50, '', 1, 0, 'C')  # Celdas vacías para ajustar el formato
        pdf.image(img_path, x=pdf.get_x() - 50 + 5, y=pdf.get_y() + 5, w=40, h=40)
        pdf.cell(50, 50, f'{kelvin_to_celsius(mean_temp):.2f} °C', 1, 0, 'C')
        pdf.cell(40, 50, f'{area:.6f} m²', 1, 0, 'C')
        pdf.cell(50, 50, f'{heat_loss:.8f} W/m²', 1, 0, 'C')
        pdf.ln(50)

    # Agrega el histograma al PDF con bordes
    pdf.add_page()
    histogram_image_file = os.path.join(output_folder, 'histogram.jpg')
    cv2.imwrite(histogram_image_file, histogram)
    pdf.image(histogram_image_file, y=pdf.get_y(), w=190, keep_aspect_ratio=True)

    # Guarda el archivo PDF
    pdf.output(os.path.join(output_folder, 'reporte_zonas_calientes.pdf'))


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Almacenar el tiempo de inicio
        result = func(*args, **kwargs)  # Ejecutar la función
        end_time = time.time()  # Almacenar el tiempo de finalización
        execution_time = end_time - start_time  # Calcular el tiempo de ejecución

        # Calcular el tiempo de ejecución en horas, minutos y segundos
        hours, rem = divmod(execution_time, 3600)
        minutes, seconds = divmod(rem, 60)

        if execution_time >= 3600:
            print(
                f"Execution time of {func.__name__}: {int(hours)} hours, {int(minutes)} minutes, {seconds:.6f} seconds")
        elif execution_time >= 60:
            print(f"Execution time of {func.__name__}: {int(minutes)} minutes, {seconds:.6f} seconds")
        else:
            print(f"Execution time of {func.__name__}: {seconds:.6f} seconds")

        return result

    return wrapper


def create_palette_image(palette, width=256, height=50):
    palette_colors = list(palette.keys())
    print(palette_colors)
    n_colors = len(palette_colors)

    # Crear un array de imagen
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Llenar la imagen con los colores de la paleta
    for i, color in enumerate(palette_colors):
        start_x = i * width // n_colors
        end_x = (i + 1) * width // n_colors
        image[:, start_x:end_x, :] = tuple(reversed(color))

    return image


def load_config_file(config_file):
    """
    Carga los datos del archivo de configuración.
    """

    config = cp.ConfigParser()
    config.read(config_file)
    min_temp = float(config.get('parameters', 'min_temperature'))
    max_temp = float(config.get('parameters', 'max_temperature'))
    boiler_width_px = float(config.get('parameters', 'boiler_width_px'))
    boiler_width_m = float(config.get('parameters', 'boiler_width_m'))
    fuel_flow = float(config.get('parameters', 'fuel_flow'))
    heat_transfer_coeff = float(config.get('parameters', 'heat_transfer_coeff'))
    ambient_temp = float(config.get('parameters', 'ambient_temp'))

    return {
        "min_temp": min_temp,
        "max_temp": max_temp,
        "boiler_width_px": boiler_width_px,
        "boiler_width_m": boiler_width_m,
        "fuel_flow": fuel_flow,
        "heat_transfer_coeff": heat_transfer_coeff,
        "ambient_temp": ambient_temp,
    }


def load_image_file(image_file):
    """
    Carga un archivo de imagen.
    """

    return cv2.imread(image_file)
