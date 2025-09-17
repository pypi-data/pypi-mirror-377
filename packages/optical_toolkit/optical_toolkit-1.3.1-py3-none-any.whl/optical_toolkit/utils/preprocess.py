import numpy as np

from .min_max_normalize import min_max_normalize_images
from .standardize import standardize_images


def preprocess(X, skip_steps=None, normalize_range=(0, 1)):
    """
    Preprocesses the input data by applying standardization and/or normalization.

    Parameters:
    X (numpy.ndarray): The input data to preprocess.
    skip_steps (list, optional): List of preprocessing steps to skip. Options:
        - "standardize" or "std" to skip standardization
        - "normalize" or "minmax" to skip normalization
    normalize_range (tuple, optional): The min-max range for normalization
                                       (default: (0, 1)).

    Returns:
    numpy.ndarray: The preprocessed data.
    """
    skip_steps = set(skip_steps or [])

    preprocessing_steps = [
        ("standardize", standardize_images),
        ("normalize", min_max_normalize_images),
    ]

    for name, func in preprocessing_steps:
        if name not in skip_steps and name[:3] not in skip_steps:
            X = func(X)

    return np.array(X)
