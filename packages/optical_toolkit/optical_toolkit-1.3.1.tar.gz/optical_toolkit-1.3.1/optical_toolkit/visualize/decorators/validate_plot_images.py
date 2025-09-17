from functools import wraps
from typing import List

import numpy as np


def validate_plot_images_args(func):
    @wraps(func)
    def wrapper(
        images: List[np.ndarray],
        num_samples: int | None = None,
        num_cols: int | None = None,
        targets: list | None = None,
        ordered_plot: bool = True,
        output_path: str = "images.png",
    ):
        # Check if images is a non-empty list or ndarray
        if isinstance(images, np.ndarray):
            if images.size == 0:
                raise ValueError("The images array cannot be empty.")
        elif len(images) == 0:
            raise ValueError("The images list cannot be empty.")

        # Validate num_cols
        if num_cols is not None and (not isinstance(num_cols, int) or num_cols <= 0):
            raise ValueError("num_cols must be a positive integer.")

        # Validate num_samples
        if num_samples is not None and (
            not isinstance(num_samples, int) or num_samples <= 0
        ):
            raise ValueError("num_samples must be a positive integer.")

        # Validate targets if they are provided
        if targets is not None and len(targets) != len(images):
            raise ValueError("The length of targets must match the number of images.")

        return func(images, num_samples, num_cols, targets, ordered_plot, output_path)

    return wrapper
