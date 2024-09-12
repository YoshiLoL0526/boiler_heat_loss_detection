import cv2
import numpy as np
from matplotlib import pyplot as plt


def region_growing(img, seed):
    # Initialize the segmented image as an array of zeros
    segmented_img = np.zeros_like(img)

    # Define the connectivity for 8-connected regions
    connectivity = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Initialize the list of seeds
    seeds = [seed]

    # Get the intensity value of the seed
    seed_value = img[seed[0], seed[1]]

    while len(seeds) > 0:
        current_seed = seeds.pop(0)

        for c in connectivity:
            neighbor = (current_seed[0] + c[0], current_seed[1] + c[1])

            # Check if the neighbor is within the bounds of the image
            if 0 <= neighbor[0] < img.shape[0] and 0 <= neighbor[1] < img.shape[1]:
                if segmented_img[neighbor[0], neighbor[1]] == 0 and np.linalg.norm(
                        img[neighbor[0], neighbor[1]] - seed_value) < 10:
                    segmented_img[neighbor[0], neighbor[1]] = 255
                    seeds.append(neighbor)

    return segmented_img


# Load the thermal image in RGB format
image_path = 'caldera/1.jpg'  # Reemplaza esto con la ruta a tu imagen térmica
img = cv2.imread(image_path)

# Convert the image to grayscale
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Define the seed point
seed_point = (128, 155)  # Reemplaza esto con el punto de semilla que desees

# Apply the region growing algorithm
segmented_img = region_growing(gray_img, seed_point)

# Display the original and segmented images
# plt.figure(figsize=(12, 6))
# plt.subplot(1, 2, 1)
# plt.title('Original Image')
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#
# plt.subplot(1, 2, 2)
# plt.title('Segmented Image')
# plt.imshow(segmented_img, cmap='gray')

fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
ax[0].set_title('Imagen original')
ax[0].axis('off')

ax[1].imshow(segmented_img, cmap='gray')
ax[1].set_title('Imagen Segmentada')
ax[1].axis('off')

plt.show()
