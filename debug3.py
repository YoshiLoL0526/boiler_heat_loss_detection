import cv2
import numpy as np
from processor import ThermalImageProcessor

if __name__ == '__main__':
    image = cv2.imread('caldera/1.jpg')
    thermal_processor = ThermalImageProcessor()
    grayscale = thermal_processor.calculate_grayscale_map(image)
    contours, hierarchy = thermal_processor.find_hot_zones(grayscale, 200)
    mask = cv2.threshold(grayscale, 200, 255, cv2.THRESH_BINARY)[1]
    # black_with_contours = np.zeros(grayscale.shape, np.uint8)
    # for idx, contour in enumerate(contours):
    #
    #     # Verificar si el contorno NO es un hueco
    #     if hierarchy[0][idx][3] != -1:
    #         continue
    #
    #     cv2.drawContours(black_with_contours, [contour], 0, 255, -1)

    # cv2.imwrite('tests/black_with_contours.jpg', black_with_contours)
    cv2.imwrite('tests/mask.jpg', mask)
