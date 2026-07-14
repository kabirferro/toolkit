from _core import run, require_pip, iter_src, no_files_warning, done, OUT_DIR

require_pip(PIL="Pillow", pillow_heif="pillow-heif")

from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener

register_heif_opener()

QUALITY = 85
SUPPORTED = {'.png', '.webp', '.heic', '.heif', '.bmp', '.gif', '.tiff', '.tif', '.jpg', '.jpeg'}


def convert_to_jpg(in_path, out_path):
    try:
        with Image.open(in_path) as im:
            # Flatten transparency to white background for JPEG
            if im.mode in ("RGBA", "LA"):
                background = Image.new("RGB", im.size, (255, 255, 255))
                background.paste(im, mask=im.split()[-1])
                im = background
            elif im.mode != "RGB":
                im = im.convert("RGB")
            im.save(out_path, format="JPEG", quality=QUALITY)
        print(f"✓ {in_path.name} -> {out_path.name}")
        return True
    except UnidentifiedImageError:
        print(f"✗ Not a valid image: {in_path.name}")
    except Exception as e:
        print(f"✗ Error processing {in_path.name}: {e}")
    return False


@run("IMAGES TO JPG")
def main():
    files = iter_src(SUPPORTED)
    if not files:
        no_files_warning("images", SUPPORTED)
        return
    processed = sum(convert_to_jpg(f, OUT_DIR / (f.stem + ".jpg")) for f in files)
    done(processed, len(files), "images")


main()
