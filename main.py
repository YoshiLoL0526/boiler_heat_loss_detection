import os
import argparse

from utils import generate_pdf_report, measure_execution_time, load_image_file, load_config_file
from processor import ThermalImageProcessor


@measure_execution_time
def process(image_path, config_path, threshold_hot, output_folder):
    """
    Realizar procesamiento de una imagen térmica
    """

    # Crear carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Procesar la imagen térmica
    thermal_processor = ThermalImageProcessor()
    image = load_image_file(image_path)
    config = load_config_file(config_path)
    data, histogram = thermal_processor.process(threshold_hot)

    # Generar reporte PDF
    generate_pdf_report(data, histogram, output_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Procesamiento de imágenes térmicas')
    parser.add_argument('-i', '--image-file', help='Archivo de imagen térmica', required=True)
    parser.add_argument('-c', '--config-file', help='Archivo de configuración', required=True)
    parser.add_argument('-o', '--output-folder', help='Carpeta de salida', required=False, default='output')
    parser.add_argument('-th', '--threshold-hot', type=int, help='Threshold utilizado', required=False, default=200)
    args = parser.parse_args()

    process(args.image_file, args.config_file, args.threshold_hot, args.output_folder)
