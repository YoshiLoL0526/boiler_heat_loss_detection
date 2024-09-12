import cv2


if __name__ == '__main__':
    image = cv2.imread('caldera/1.jpg')
    output_folder = 'tests'

    # Filtros de reducción de ruido
    # 1. Media
    blur_media = cv2.blur(image, (5, 5))
    cv2.imwrite(output_folder + '/blur_media.jpg', blur_media)

    # 2. Gaussiano
    blur_gaussiano = cv2.GaussianBlur(image, (5, 5), 0)
    cv2.imwrite(output_folder + '/blur_gaussiano.jpg', blur_gaussiano)

    # 3. Mediana
    blur_mediana = cv2.medianBlur(image, 5)
    cv2.imwrite(output_folder + '/blur_mediana.jpg', blur_mediana)

    # 4. Bilateral
    blur_bilateral = cv2.bilateralFilter(image, 9, 75, 75)
    cv2.imwrite(output_folder + '/blur_bilateral.jpg', blur_bilateral)
