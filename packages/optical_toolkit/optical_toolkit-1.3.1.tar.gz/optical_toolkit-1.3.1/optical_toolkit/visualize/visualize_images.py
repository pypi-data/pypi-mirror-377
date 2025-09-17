import random
from collections import defaultdict
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from .decorators.validate_plot_images import validate_plot_images_args
from .decorators.validate_summarize_images import validate_summarize_images_args
from .functions.visualize_utils import (_convert_images_to_numpy, _plot_and_save,
                                        _resize_images_to_largest,
                                        _sort_images_by_targets, _stratified_sample)


@validate_plot_images_args
def plot_images(
    images: List[np.ndarray],
    num_samples: int | None = None,
    num_cols: int | None = None,
    targets: list | None = None,
    ordered_plot: bool = True,
    output_path: str = "images.png",
) -> plt.Figure:
    """
    Plot a grid of images and optionally their corresponding target labels.

    Args:
        images (List[np.ndarray]): A list of images as NumPy arrays.
        num_samples (int | None, optional): Number of images to display. If None, displays all.
        num_cols (int | None, optional): Number of columns in the image grid. If None, it will be inferred to make the grid square-ish.
        targets (list | None, optional): Labels corresponding to the images.
        ordered_plot (bool, optional): Whether to sort images based on targets. Defaults to True.
        output_path (str, optional): File path to save the image plot. Defaults to "images.png".

    Returns:
        plt.Figure: The matplotlib figure object containing the image grid.
    """

    images = _convert_images_to_numpy(images)

    if targets is not None and ordered_plot:
        images, targets = _sort_images_by_targets(images, targets)

    if num_samples is not None:
        if targets is not None:
            images, targets = _stratified_sample(images, targets, num_samples)
        else:
            indices = random.sample(range(len(images)), min(num_samples, len(images)))
            images = [images[i] for i in indices]

    images_resized = _resize_images_to_largest(images)

    # Automatically determine number of columns if not provided
    if num_cols is None:
        num_cols = int(np.ceil(np.sqrt(len(images_resized))))

    fig = _plot_and_save(images_resized, targets, num_cols, output_path)

    return fig


@validate_summarize_images_args
def summarize_images(
    images: List[np.ndarray],
    targets: List[int],
    num_images_per_class: int = 10,
    num_classes: int | None = None,
    output_path: str = "dataset_summary.png",
    colormap: str = "viridis",
) -> plt.Figure:
    """
    Create a summary grid of image examples per class.

    Args:
        images (List[np.ndarray]): The list of all images.
        targets (List[int]): Corresponding class labels.
        num_images_per_class (int): Number of images to show per class.
        num_classes (int, optional): Limit to the first N classes.
        output_path (str): File path to save the plot.
        colormap (str): The colormap to use for displaying images.

    Returns:
        plt.Figure: The matplotlib figure object for the summary grid.
    """
    class_images: Dict[int, List[np.ndarray]] = defaultdict(list)
    for img, label in zip(images, targets):
        class_images[label].append(img)

    sorted_class_items = sorted(class_images.items())
    if num_classes is not None:
        sorted_class_items = sorted_class_items[:num_classes]

    n_rows = len(sorted_class_items)
    n_cols = num_images_per_class + 1  # first column for class label

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 2, n_rows * 2))
    axes = np.atleast_2d(axes)

    for row_idx, (label, class_images_list) in enumerate(sorted_class_items):
        ax_label = axes[row_idx, 0]
        ax_label.axis("off")
        ax_label.text(
            0.5,
            0.5,
            f"Class {label}",
            fontsize=14,
            ha="center",
            va="center",
            transform=ax_label.transAxes,
        )

        for col_idx, img in enumerate(class_images_list[:num_images_per_class]):
            ax = axes[row_idx, col_idx + 1]
            ax.imshow(img, cmap=colormap)
            ax.axis("off")

        for col_idx in range(len(class_images_list), num_images_per_class):
            axes[row_idx, col_idx + 1].set_visible(False)

    plt.subplots_adjust(wspace=0.2, hspace=0.2)
    plt.savefig(output_path, bbox_inches="tight")
    print(f"Summary plot saved to {output_path}")
    plt.show()

    return fig
