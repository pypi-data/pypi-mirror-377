import numpy as np


def min_max_normalize(image, min_val, max_val):
    """
    Normalizes an image using min-max scaling to a specified range.

    Parameters:
    image (numpy.ndarray): The input image to normalize.
    min_val (float): The minimum value of the normalized range (default is 0).
    max_val (float): The maximum value of the normalized range (default is 1).

    Returns:
    numpy.ndarray: The normalized image.
    """
    img_min = np.min(image)
    img_max = np.max(image)

    if img_max - img_min == 0:
        return np.zeros_like(image) + min_val  # Avoid division by zero

    normalized_image = (image - img_min) / (img_max - img_min)
    return normalized_image * (max_val - min_val) + min_val


def min_max_normalize_images(X, min_val=0, max_val=1):
    """
    Normalizes a batch of images using min-max scaling to a specified range.

    Parameters:
    images (numpy.ndarray): The input image to normalize.
    min_val (float): The minimum value of the normalized range (default is 0).
    max_val (float): The maximum value of the normalized range (default is 1).

    Returns:
    numpy.ndarray: The normalized images.
    """

    images = [min_max_normalize(x, min_val, max_val) for x in X]
    return images


__all__ = [min_max_normalize_images]
