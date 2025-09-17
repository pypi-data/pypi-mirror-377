import random
import re

import tensorflow as tf
from tensorflow.keras.applications import (VGG16, DenseNet121, EfficientNetB0,
                                           InceptionV3, MobileNet, ResNet50, Xception)


def instantiate_model(model_path, model_custom_objects):
    if model_custom_objects is None:
        model_custom_objects = {}

    # Check if model_path corresponds to a pretrained model name
    pretrained_models = {
        "xception": Xception,
        "resnet50": ResNet50,
        "inceptionv3": InceptionV3,
        "vgg16": VGG16,
        "densenet121": DenseNet121,
        "mobilenet": MobileNet,
        "efficientnetb0": EfficientNetB0,
    }

    if model_path.lower() in pretrained_models:
        # Load the corresponding pretrained model
        model = pretrained_models[model_path.lower()](
            weights="imagenet", include_top=False
        )
    else:
        # Load the model from the specified path
        try:
            model = tf.keras.models.load_model(
                model_path, custom_objects=model_custom_objects
            )
        except ValueError as e:
            raise ValueError(f"{e}: Model not found")

    return model


def get_conv_layer(model, layer_name):
    if layer_name is None:
        # Find all convolutional layers in the model
        conv_layers = [
            layer for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)
        ]

        if not conv_layers:
            raise ValueError("No convolutional layers found in the model.")

        layer = random.choice(conv_layers)
    else:
        layer = model.get_layer(name=layer_name)

    return layer


def get_conv_layers(model, custom_layer_prefix, layer_name_preference):
    conv_layers = []

    if layer_name_preference:
        pattern = re.compile(f".*{re.escape(layer_name_preference)}.*")
    else:
        pattern = None

    for layer in model.layers:
        if pattern and pattern.match(layer.name) and hasattr(layer, "filters"):
            conv_layers.append(layer)
        elif (
            custom_layer_prefix
            and layer.name.startswith(custom_layer_prefix)
            and hasattr(layer, "filters")
        ):
            conv_layers.append(layer)
        elif isinstance(layer, tf.keras.layers.Conv2D):
            conv_layers.append(layer)

    print(conv_layers)

    return conv_layers


def layer_distribution(
    num_layers,
    format="hierarchical",
    included_indices=None,
    select_topmost=True,
    select_bottommost=True,
):
    if format == "hierarchical":
        layer_indices = _hierarchical_layers(num_layers)
    elif format == "constant":
        layer_indices = _constantly_inc_layers(num_layers)
    elif format == "all":
        layer_indices = _all_layers(num_layers)
    else:
        ValueError(
            f"format={format} is not supported. Try 'hierarchical', 'constant', or 'all'"
        )

    if included_indices is not None:
        layer_indices = tf.concat(
            [layer_indices, tf.convert_to_tensor(included_indices, dtype=tf.int32)],
            axis=0,
        )
    if select_topmost:
        layer_indices = tf.concat([[0, 1], layer_indices], axis=0)
    if select_bottommost:
        layer_indices = tf.concat(
            [layer_indices, [num_layers - 2, num_layers - 1]], axis=0
        )

    layer_indices = tf.sort(tf.unique(layer_indices).y)

    if num_layers < len(layer_indices):
        layer_indices = layer_indices[:num_layers]

    return layer_indices


def _hierarchical_layers(num_layers):
    bot_percentiles = tf.linspace(0.0, 0.2, 3)
    mid_percentiles = tf.linspace(0.2, 0.5, 3)
    top_percentiles = tf.linspace(0.5, 0.7, 2)

    percentiles = tf.concat([bot_percentiles, mid_percentiles, top_percentiles], axis=0)

    layer_indices = tf.cast(percentiles * (num_layers - 1), tf.int32)

    return layer_indices


def _constantly_inc_layers(num_layers):
    percentiles = tf.linspace(0.0, 1.0, 10)

    layer_indices = tf.cast(percentiles * (num_layers - 1), tf.int32)

    return layer_indices


def _all_layers(num_layers):
    percentiles = tf.linspace(0.0, 1.0, num_layers)

    layer_indices = tf.cast(percentiles * (num_layers - 1), tf.int32)

    return layer_indices


def infer_input_size(model):
    size = model.inputs[0].shape[1]
    return size if size else 100
