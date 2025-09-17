from pathlib import Path

from PIL import Image
from pypdf import PdfWriter

from optical_toolkit.visualize.visualize_images import summarize_images

from .functions.all_embeddings import plot_2d_embeddings, plot_3d_embeddings
from .functions.summary_statistics import summarize_image_statistics


def analyze_image_dataset(
    X, y, num_images_per_class=10, num_classes=None, output_path="summary.pdf"
):
    output_path = Path(output_path)

    if Path(output_path).suffix.lower() != ".pdf":
        raise ValueError("The file must have a '.pdf' extension.")

    if num_classes is None:
        num_classes = len(set(y))

    # Step 0: Summary Statistics
    temp_path_0 = f"{output_path.stem}_0.pdf"
    summarize_image_statistics(X=y, y=y, output_path=temp_path_0)

    # Step 1: Image Samples
    temp_path_1 = f"{output_path.stem}_1.pdf"
    summarize_images(
        images=X,
        targets=y,
        num_images_per_class=num_images_per_class,
        num_classes=num_classes,
        output_path=temp_path_1,
    )

    # Step 2: 2d Embeddings
    temp_path_2 = f"{output_path.stem}_2.pdf"
    plot_2d_embeddings(X, y, temp_path_2)

    # Step 3: 3d Embeddings
    temp_path_3 = f"{output_path.stem}_3.pdf"
    plot_3d_embeddings(X, y, temp_path_3)

    # Step 4: Merge outputs
    pdf_chunk_paths = [temp_path_0, temp_path_1, temp_path_2, temp_path_3]

    merger = PdfWriter()
    [merger.append(pdf) for pdf in pdf_chunk_paths]

    with open(output_path, "wb") as new_file:
        merger.write(new_file)

    # Step 5: Cleanup
    [Path.unlink(Path(path)) for path in pdf_chunk_paths]
