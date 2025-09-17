from enum import Enum


class ManifoldType(Enum):
    RANDOM_PROJECTION = "Random projection embedding"
    TRUNCATED_SVD = "Truncated SVD embedding"
    ISOMAP = "Isomap embedding"
    STANDARD_LLE = "Standard LLE embedding"
    MODIFIED_LLE = "Modified LLE embedding"
    HESSIAN_LLE = "Hessian LLE embedding"
    LTSA_LLE = "LTSA LLE embedding"
    MDS = "MDS embedding"
    RANDOM_TREES = "Random Trees embedding"
    SPECTRAL = "Spectral embedding"
    TSNE = "t-SNE embedding"
    NCA = "NCA embedding"
