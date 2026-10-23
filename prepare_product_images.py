"""Make white-background copies of the product photos for the website.

Many photos in data/products/ were transparent images flattened onto pure
black, so they show as black squares on a white page. This script flood-fills
the black background (only the black connected to the image's edges, so black
lettering and logos inside a garment stay untouched) with white, and saves the
result to data/products_web/ under the same filename.

The original photos are never changed. Run it again after adding photos:
    backend/.venv/bin/python prepare_product_images.py
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

DATA_DIR = Path(__file__).parent / "data"
SOURCE_DIR = DATA_DIR / "products"
OUTPUT_DIR = DATA_DIR / "products_web"

WHITE = (255, 255, 255)
MARKER = (255, 0, 255)  # temporary fill color, so filled pixels can be found afterward
NEAR_BLACK = 15  # max summed RGB value treated as background black
FILL_TOLERANCE = 15  # kept low: the darkest navy garments get within ~50 of black
EDGE_STEP = 4  # check every 4th pixel along the edges for black to start from
FRINGE_WIDTH = 5  # filter size: looks 2px into the garment from the background
FRINGE_DARKNESS = 45  # brightness (0-255) below which an edge pixel is leftover black


def edge_points(width: int, height: int):
    for x in range(0, width, EDGE_STEP):
        yield x, 0
        yield x, height - 1
    for y in range(0, height, EDGE_STEP):
        yield 0, y
        yield width - 1, y


def marker_mask(image: Image.Image) -> Image.Image:
    """White wherever the image is exactly the marker color."""
    channels = [
        band.point(lambda v, want=want: 255 if v == want else 0)
        for band, want in zip(image.split(), MARKER)
    ]
    return ImageChops.multiply(ImageChops.multiply(channels[0], channels[1]), channels[2])


def whiten_background(image: Image.Image) -> tuple[Image.Image, bool]:
    image = image.convert("RGB")
    pixels = image.load()
    changed = False
    for point in edge_points(*image.size):
        if sum(pixels[point]) <= NEAR_BLACK:
            ImageDraw.floodfill(image, point, MARKER, thresh=FILL_TOLERANCE)
            changed = True
    if not changed:
        return image, False

    background = marker_mask(image)
    # The flattening left a dark, jagged outline where garment met black;
    # whiten the darkest pixels right next to the filled background.
    near_background = background.filter(ImageFilter.MaxFilter(FRINGE_WIDTH))
    dark = image.convert("L").point(lambda v: 255 if v < FRINGE_DARKNESS else 0)
    image.paste(WHITE, mask=ImageChops.multiply(near_background, dark))
    image.paste(WHITE, mask=background)
    return image, True


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    whitened = 0
    sources = sorted(SOURCE_DIR.glob("*.jpg"))
    for source in sources:
        image, changed = whiten_background(Image.open(source))
        image.save(OUTPUT_DIR / source.name, quality=90)
        whitened += changed
    print(f"Saved {len(sources)} images to {OUTPUT_DIR}; {whitened} had a black background whitened.")


if __name__ == "__main__":
    main()
