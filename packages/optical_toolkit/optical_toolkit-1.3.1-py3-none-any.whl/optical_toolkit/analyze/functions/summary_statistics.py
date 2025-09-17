import tempfile
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def create_statistics_table(X, y):
    """
    Create summary statistics for the dataset.
    """
    X = np.array(X)
    y = np.array(y)

    num_samples = len(X)
    class_counts = Counter(y)
    num_classes = len(class_counts)

    shapes = [img.shape for img in X]
    unique_shapes = list(set(shapes))
    uniform_shape = len(unique_shapes) == 1

    dtype_set = set(img.dtype for img in X)
    consistent_dtype = len(dtype_set) == 1

    image_means = [img.mean() for img in X]
    image_stds = [img.std() for img in X]

    summary = {
        "Number of samples": num_samples,
        "Number of classes": num_classes,
        "Uniform image shape": uniform_shape,
        "Image shapes": str(unique_shapes),
        "Consistent dtype": consistent_dtype,
        "Image dtype(s)": str(list(dtype_set)),
        "Mean pixel value (avg over images)": f"{np.mean(image_means):.4f}",
        "Std pixel value (avg over images)": f"{np.mean(image_stds):.4f}",
    }

    return summary, class_counts


def generate_statistics_table(summary, output_path):
    """
    Generate and save the general statistics table as an image.
    """
    fig, ax = plt.subplots(figsize=(10, len(summary) * 0.6))
    ax.axis("off")
    table_data = [[key, val] for key, val in summary.items()]
    table = ax.table(cellText=table_data, colLabels=["Property", "Value"], loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_text_props(ha="center", va="center")
        if row == 0:
            cell.set_facecolor("black")
            cell.set_text_props(color="white", weight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_class_distribution_table(class_counts, output_path):
    """
    Generate and save the class distribution table (with percentages and class weights).
    """
    total_samples = sum(class_counts.values())
    class_percentages = {k: (v / total_samples) * 100 for k, v in class_counts.items()}
    class_weights = {
        k: 1 / v for k, v in class_counts.items()
    }  # Inverse of frequency as weight

    # Create table data with Class, Count, Percentage, and Class Weight columns
    class_table_data = [
        [label, count, f"{percentage:.2f}%", f"{weight:.4f}"]
        for label, count, percentage, weight in zip(
            class_counts.keys(),
            class_counts.values(),
            class_percentages.values(),
            class_weights.values(),
        )
    ]

    fig, ax = plt.subplots(figsize=(10, len(class_counts) * 0.5 + 1))
    ax.axis("off")
    table = ax.table(
        cellText=class_table_data,
        colLabels=["Class", "Count", "Percentage", "Class Weight"],
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    for (row, col), cell in table.get_celld().items():
        cell.set_text_props(ha="center", va="center")
        if row == 0:
            cell.set_facecolor("black")
            cell.set_text_props(color="white", weight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_pie_chart(class_counts, output_path):
    """
    Generate and save the pie chart for class distribution, ensuring it is centered.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        class_counts.values(),
        labels=class_counts.keys(),
        autopct="%1.1f%%",
        startangle=90,
    )
    ax.axis("equal")
    plt.title("Class Distribution")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def combine_images(image_paths, output_path):
    """
    Combine multiple images vertically with spacing in between and save the combined image as a PDF.
    """
    images = [Image.open(img_path) for img_path in image_paths]
    images[0].save(output_path, save_all=True, append_images=images[1:], format="PDF")


def summarize_image_statistics(X, y, output_path):
    """
    Main function to summarize the image statistics and combine them into one final image (PDF).
    """
    # Step 1: Create summary statistics and class counts
    summary, class_counts = create_statistics_table(X, y)

    # Step 2: Generate the summary statistics
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        stats_path = tmpdir / "stats.png"
        class_path = tmpdir / "class.png"
        pie_path = tmpdir / "pie.png"

        generate_statistics_table(summary, stats_path)
        generate_class_distribution_table(class_counts, class_path)
        generate_pie_chart(class_counts, pie_path)

        all_paths = [stats_path, class_path, pie_path]

        # Step 3: Combine the images vertically and save as PDF
        combine_images(all_paths, output_path)

        # Step 4: Cleanup
        [Path.unlink(path) for path in all_paths]
