import numpy as np


def standardize_images(X):
    """
    Standardizes a batch of images by subtracting the mean
     and dividing by the standard deviation.

    Parameters:
    X (numpy.ndarray): A batch of images with shape (N, H, W, C) where
                       N = number of images,
                       H = height,
                       W = width,
                       C = number of channels.

    Returns:
    numpy.ndarray: The standardized images.
    """
    means = np.mean(X, axis=(1, 2), keepdims=True)
    stds = np.std(X, axis=(1, 2), keepdims=True)
    stds[stds == 0] = 1e-3

    return (X - means) / stds
