from functools import wraps
from typing import List

import numpy as np


def validate_summarize_images_args(func):
    @wraps(func)
    def wrapper(
        images: List[np.ndarray],
        targets: List[int],
        num_images_per_class: int = 10,
        num_classes: int | None = None,
        output_path: str = "dataset_summary.png",
        colormap: str = "viridis",
    ):
        # Check if images is a non-empty list or ndarray
        if isinstance(images, np.ndarray):
            if images.size == 0:
                raise ValueError("The images array cannot be empty.")
        elif len(images) == 0:
            raise ValueError("The images list cannot be empty.")

        # Check if targets is a non-empty list or ndarray
        if isinstance(targets, np.ndarray):
            if targets.size == 0:
                raise ValueError("The targets array cannot be empty.")
        elif len(targets) == 0:
            raise ValueError("The targets list cannot be empty.")

        # Check if num_images_per_class is a positive integer
        if not isinstance(num_images_per_class, int) or num_images_per_class <= 0:
            raise ValueError("num_images_per_class must be a positive integer.")

        # Check if num_classes is a positive integer, if provided
        if num_classes is not None and (
            not isinstance(num_classes, int) or num_classes <= 0
        ):
            raise ValueError("num_classes must be a positive integer.")

        # Check if colormap is a valid string
        if not isinstance(colormap, str):
            raise ValueError("colormap must be a string.")

        return func(
            images, targets, num_images_per_class, num_classes, output_path, colormap
        )

    return wrapper
