<p align="center" width="75%">
  <img src="examples/logo.png" alt="opticaltoolkit_logo"/>
</p>

## A collection of deep learning -- computer vision utility functions

## Installation

``` bash
pip install optical_toolkit
```

## Visualize

- Visualize a dataset in a grid
```python
from sklearn.datasets import load_digits
from optical_toolkit.visualize import plot_images

X, y = load_digits()

plot_images(X, targets=y)
```
<p align="center" width="100%">
  <img src="examples/visualizations/test_sklearn_digits.png" alt="dataset"/>
</p>

- Summarize a dataset by classes
 ```python
from sklearn.datasets import load_digits
from optical_toolkit.visualize import plot_images

X, y = load_digits()

summarize_images(X, targets=y, num_images_per_class=10, num_classes=10)
```
<p align="center" width="100%">
    <img src="examples/visualizations/test_summarize_images.png" alt="dataset"/>
</p>


- Visualize the 2d and 3d embeddings of images
 ```python
from sklearn.datasets import load_digits
from optical_toolkit.visualize.embeddings import get_embeddings

X, y = load_digits()

2d_embeddings, fig_2d = get_embeddings(X, y, dims=2, embedding_type="tsne", return_plot=True)
3d_embeddings, fig_3d = get_embeddings(X, y, dims=3, embedding_type="tsne", return_plot=True)
```
<p align="center" width="100%">
  <img src="examples/embeddings/2d_TSNE_embedding.png" alt="embedding2d" width="47.5%"/>
  <img src="examples/embeddings/3d_TSNE_embedding.png" alt="embedding3d" width="47.5%"/>
</p>
<p align="center" width="100%">
  <img src="examples/2d_embedding_comparison.png" alt="embedding2d_comp" width="47.5%"/>
  <img src="examples/3d_embedding_comparison.png" alt="embedding3d_comp" width="47.5%"/>
</p>

## Insight
- Visualize the filters of a (trained) CNN model
 ```python
from optical_toolkit.cnn_filters import display_filters, display_model_filters

model_name = "xception"

layer_names = [
     "block2_sepconv1",
     "block5_sepconv1",
     "block9_sepconv1",
     "block14_sepconv1",
]

 for layer_name in layer_names:
     display_filters(
     model=model_name,
     layer_name=layer_name,
 )
```
<p align="center" width="100%">
    <img src="examples/insights/block2_sepconv1_layer_filters.png" alt="filters" width="47.5%"/>
    <img src="examples/insights/block5_sepconv1_layer_filters.png" alt="filters" width="47.5%"/>
    <img src="examples/insights/block9_sepconv1_layer_filters.png" alt="filters" width="47.5%"/>
    <img src="examples/insights/block14_sepconv1_layer_filters.png" alt="filters" width="47.5%"/>
</p>

```python
display_model_filters(model=model_name)
```
<p align="center" width="100%">
    <img src="examples/insights/xception_filters.png" alt="model_filters"/>
</p>

- Visualize the filters of your custom CNN with custom objects
```python
import keras

model_name = "examples/custom_models/svdnet.keras"
dir_name = "examples/insights"

@keras.saving.register_keras_serializable()
class ResidualConvBlock(keras.layers.Layer):
    ...

display_model_filters(
    model_name,
    custom_layer_prefix="residual",
)
```
<p align="center" width="100%">
    <img src="examples/insights/svdnet_filters.png" alt="model_filters"/>
</p>

## Analyze
- A high level function for image dataset analysis
```python
from sklearn.datasets import load_digits

from optical_toolkit.analyze.analyze import analyze_image_dataset

digits = load_digits()
X = digits.images
y = digits.target

analyze_image_dataset(X, y, output_path="examples/analyze/analysis.pdf")
```
[View full analysis (PDF)](examples/analyze/analysis.pdf)


