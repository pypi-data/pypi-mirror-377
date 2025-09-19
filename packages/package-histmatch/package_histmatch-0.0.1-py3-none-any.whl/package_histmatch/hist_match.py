import matplotlib.pyplot as plt
from skimage import io
from skimage.exposure import match_histograms


def match_images(source_path, reference_path, output_path):
    """
    Carrega duas imagens, faz a correspondência de histograma
    e salva a imagem resultante.
    """
    image = io.imread(source_path)
    reference = io.imread(reference_path)
    matched_image = match_histograms(image, reference, channel_axis=-1)

    io.imsave(output_path, matched_image)

    print(f"Imagem correspondida salva em {output_path}")

    # Opcional: para exibir as imagens no notebook ou script
    fig, (ax1, ax2, ax3) = plt.subplots(
        ncols=3, figsize=(16, 5), sharex=True, sharey=True
    )

    ax1.imshow(image)
    ax1.set_title("Imagem de Origem")

    ax2.imshow(reference)
    ax2.set_title("Imagem de Referência")

    ax3.imshow(matched_image)
    ax3.set_title("Imagem Correspondida")

    plt.tight_layout()
    plt.show()
