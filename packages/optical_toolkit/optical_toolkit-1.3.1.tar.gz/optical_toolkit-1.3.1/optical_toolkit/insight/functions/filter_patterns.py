import tensorflow as tf
from tqdm import tqdm

from optical_toolkit.utils.deprocess_image import deprocess_image


def compute_loss(image, filter_index, feature_extractor):
    activation = feature_extractor(image)
    filter_activation = activation[..., filter_index]
    return tf.reduce_mean(filter_activation)


@tf.function
def gradient_ascent_step(image, filter_index, learning_rate, feature_extractor):
    with tf.GradientTape() as tape:
        tape.watch(image)
        loss = compute_loss(image, filter_index, feature_extractor)

    grads = tape.gradient(loss, image)
    grads = tf.math.l2_normalize(grads)

    image += learning_rate * grads

    return image


def generate_filter_pattern(filter_index, img_sz, feature_extractor):
    iterations = 30
    learning_rate = 10.0

    image = tf.random.uniform(minval=0.4, maxval=0.6, shape=(1, img_sz, img_sz, 3))

    for i in range(iterations):
        image = gradient_ascent_step(
            image, filter_index, learning_rate, feature_extractor
        )

    return image[0].numpy()


def generate_filter_patterns(layer, num_filters, img_sz, feature_extractor):
    all_images = []

    LINE_LENGTH = 100
    border = "=" * LINE_LENGTH
    sub_border = "-" * LINE_LENGTH
    desc = "Gradient Ascent on Layer"

    print()

    with tqdm(
        total=num_filters, desc=desc, unit="step", ncols=75, mininterval=0.1
    ) as pbar:
        tqdm.write(f"{border}\n{desc}: {layer.name}\n{sub_border}\n")
        for filter_index in range(num_filters):
            pbar.set_description(f"Processing filter {filter_index}")

            filter_index = tf.convert_to_tensor(filter_index, dtype=tf.int32)
            img_sz = tf.convert_to_tensor(img_sz, dtype=tf.int32)

            image = deprocess_image(
                generate_filter_pattern(filter_index, img_sz, feature_extractor)
            )
            all_images.append(image)

            pbar.update(1)

    print(f"\n{sub_border}\n")

    return all_images


#######################################################################
# @tf.function
# def gradient_ascent_step(image, filter_index, feature_extractor):
#     with tf.GradientTape() as tape:
#         tape.watch(image)  # Watch the image tensor
#         loss = compute_loss(image, filter_index, feature_extractor)

#     grads = tape.gradient(loss, image)
#     grads = tf.math.l2_normalize(grads)

#     return grads


# def generate_filter_pattern(filter_index, img_sz, feature_extractor):
#     iterations = 15
#     learning_rate = 0.02

#     optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

#     image = tf.random.uniform(minval=0.4, maxval=0.6, shape=(1, img_sz, img_sz, 3))

#     image = tf.Variable(image)

#     for i in range(iterations):
#         grads = gradient_ascent_step(image, filter_index, feature_extractor)
#         optimizer.apply_gradients([(grads, image)])

#     return image[0].numpy()
#######################################################################

__all__ = [generate_filter_patterns]
