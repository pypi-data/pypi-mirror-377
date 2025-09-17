import numpy as np


def stitched_image(images, num_images, img_sz):
    margin = 5
    n = int(num_images ** (1 / 2))

    cropped_width = img_sz - 25 * 2
    cropped_height = img_sz - 25 * 2

    width = n * cropped_width + (n - 1) * margin
    height = n * cropped_height + (n - 1) * margin

    stitched_image = np.zeros((width, height, 3))

    for i in range(n):
        for j in range(n):
            image = images[i * n + j]
            stitched_image[
                (cropped_width + margin) * i : (cropped_width + margin) * i
                + cropped_width,
                (cropped_height + margin) * j : (cropped_height + margin) * j
                + cropped_height,
                :,
            ] = image

    return stitched_image


def concat_images(images, axis=1):
    margin = 5
    images = [np.asarray(img) for img in images]

    # Ensure all images have the same number of channels
    max_channels = max(img.shape[-1] if img.ndim == 3 else 1 for img in images)
    images = [
        (
            img
            if (img.ndim == 3 and img.shape[-1] == max_channels)
            else np.dstack([img] * max_channels)
        )
        for img in images
    ]

    # Find max height and width
    max_height = max(img.shape[0] for img in images)
    max_width = max(img.shape[1] for img in images)

    padded_images = []
    for img in images:
        h, w = img.shape[:2]

        # Calculate padding sizes
        pad_top = (max_height - h) // 2
        pad_bottom = max_height - h - pad_top
        pad_left = (max_width - w) // 2
        pad_right = max_width - w - pad_left

        # Pad the image to be centered
        padded_image = np.pad(
            img,
            ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
            mode="constant",
            constant_values=0,
        )
        padded_images.append(padded_image)

    # Add margin between images horizontally or vertically
    if axis == 1:  # Horizontal concatenation
        margin_pad = np.zeros((max_height, margin, max_channels), dtype=np.uint8)
        result = np.concatenate(
            [
                (
                    padded_images[i]
                    if i == len(padded_images) - 1
                    else np.concatenate([padded_images[i], margin_pad], axis=1)
                )
                for i in range(len(padded_images))
            ],
            axis=1,
        )

    elif axis == 0:  # Vertical concatenation
        margin_pad = np.zeros((margin, max_width, max_channels), dtype=np.uint8)
        result = np.concatenate(
            [
                (
                    padded_images[i]
                    if i == len(padded_images) - 1
                    else np.concatenate([padded_images[i], margin_pad], axis=0)
                )
                for i in range(len(padded_images))
            ],
            axis=0,
        )

    return result
